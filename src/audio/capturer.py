"""
AudioCapturer with optional WASAPI loopback support (Windows).

- Supports recorder_factory (for tests/mocks).
- Normalizes int16 -> float32 and mixes stereo->mono.
- Attempts stereo then mono automatically.
- When loopback=True on Windows, uses WASAPI loopback capturing from the default output device.
"""
from __future__ import annotations
import threading
import queue
import time
import logging
import sys
from typing import Callable, Optional, Iterator
import numpy as np

RecorderFactory = Callable[[int, int], Iterator[np.ndarray]]

LOG = logging.getLogger("realtime_captioning.audio")
if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class AudioCapturer:
    def __init__(
        self,
        samplerate: int = 48000,
        block_ms: int = 500,
        device: Optional[object] = None,
        queue_maxsize: int = 50,
        recorder_factory: Optional[RecorderFactory] = None,
        loopback: bool = False,
    ) -> None:
        """
        :param samplerate: sample rate in Hz
        :param block_ms: chunk size in ms
        :param device: explicit device index or name (None uses system default)
        :param queue_maxsize: internal queue size
        :param recorder_factory: optional generator factory for testing
        :param loopback: If True on Windows, attempt WASAPI loopback capture from output device (system audio)
        """
        self.sr = int(samplerate)
        self.block_ms = int(block_ms)
        self.blocksize = int(self.sr * self.block_ms / 1000)
        self.device = device
        self.loopback = bool(loopback)
        self._q: queue.Queue = queue.Queue(maxsize=queue_maxsize)
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self.recorder_factory = recorder_factory

    def _normalize(self, data: np.ndarray) -> np.ndarray:
        if np.issubdtype(data.dtype, np.integer):
            info = np.iinfo(data.dtype)
            denom = max(1, info.max)
            data_f = data.astype(np.float32) / denom
        else:
            data_f = data.astype(np.float32)

        if data_f.ndim > 1 and data_f.shape[1] > 1:
            data_f = data_f.mean(axis=1)

        return data_f.astype(np.float32)

    def _put_chunk(self, chunk: np.ndarray) -> None:
        try:
            self._q.put_nowait(chunk)
        except queue.Full:
            try:
                _ = self._q.get_nowait()
            except queue.Empty:
                pass
            try:
                self._q.put_nowait(chunk)
            except queue.Full:
                LOG.debug("[AudioCapturer] queue full after drop-oldest; discarding chunk")

    def _record_loop_with_factory(self, factory: RecorderFactory) -> None:
        it = factory(self.sr, self.blocksize)
        for raw in it:
            if self._stop_event.is_set():
                break
            if raw is None:
                continue
            try:
                chunk = self._normalize(raw)
                self._put_chunk(chunk)
            except Exception:
                LOG.exception("[AudioCapturer] error normalizing/putting chunk (factory)")

    def _record_loop_sounddevice(self) -> None:
        try:
            import sounddevice as sd  # type: ignore
        except Exception as e:
            LOG.exception("sounddevice import failed; install portaudio and python-sounddevice")
            raise RuntimeError("sounddevice is required for real capture. Install python-sounddevice.") from e

        # determine device index
        device_index = self.device
        try:
            if device_index is None:
                # sd.default.device may be tuple (in, out) or int
                try:
                    default_dev = sd.default.device
                    if isinstance(default_dev, (list, tuple)):
                        # default_dev[0] is input, default_dev[1] is output
                        in_idx, out_idx = (default_dev[0], default_dev[1] if len(default_dev) > 1 else None)
                    else:
                        in_idx = default_dev
                        out_idx = None
                except Exception:
                    in_idx = None
                    out_idx = None

                if self.loopback and sys.platform == "win32":
                    # Prefer default output device for WASAPI loopback
                    device_index = out_idx if out_idx is not None else None
                else:
                    device_index = in_idx if in_idx is not None else None
        except Exception:
            device_index = None

        # probe device info (when possible)
        max_in = 0
        max_out = 0
        try:
            probe_idx = device_index if device_index is not None else sd.default.device
            # if probe_idx is a tuple, pick input index for query
            if isinstance(probe_idx, (list, tuple)):
                probe_idx = probe_idx[0]
            if probe_idx is not None:
                info = sd.query_devices(probe_idx)
                max_in = int(info.get("max_input_channels", 0) or 0)
                max_out = int(info.get("max_output_channels", 0) or 0)
                LOG.debug("[AudioCapturer] probed device %s -> in:%d out:%d", probe_idx, max_in, max_out)
        except Exception:
            LOG.debug("[AudioCapturer] device probe failed; continuing with channel probing")

        if self.loopback and sys.platform == "win32":
            LOG.info("[AudioCapturer] loopback requested (WASAPI). Attempting to capture system audio.")
            # Prepare WASAPI extra settings if available
            extra = None
            try:
                # Only WASAPI supports loopback in PortAudio on Windows via sounddevice.WasapiSettings
                if hasattr(sd, "WasapiSettings"):
                    extra = sd.WasapiSettings(loopback=True)
                else:
                    extra = None
            except Exception:
                extra = None
        else:
            extra = None

        # If loopback requested and no output device index found, try to find first output-capable device
        if self.loopback and sys.platform == "win32" and device_index is None:
            try:
                devs = sd.query_devices()
                for i, d in enumerate(devs):
                    if d.get("max_output_channels", 0) > 0:
                        device_index = i
                        LOG.debug("[AudioCapturer] picked output device index %d for loopback: %s", i, d.get("name"))
                        break
            except Exception:
                LOG.debug("[AudioCapturer] could not enumerate devices to pick loopback target")

        # If no input channels on the probe, log a warning (but we'll still try fallback)
        if max_in == 0:
            LOG.warning("[AudioCapturer] device has no input channels (max_input_channels=%s); may require loopback or manual device selection", max_in)

        # Preferred channels order: stereo then mono (but ensure <= device capability)
        for channels_try in (2, 1):
            # If loopback and we probed output channels, ensure channels_try <= max_out (not max_in)
            if self.loopback and max_out:
                if channels_try > max_out:
                    LOG.debug("[AudioCapturer] skipping channels=%d (output device supports %d)", channels_try, max_out)
                    continue
            else:
                if max_in and channels_try > max_in:
                    LOG.debug("[AudioCapturer] skipping channels=%d (device supports %d)", channels_try, max_in)
                    continue

            try:
                LOG.info("[AudioCapturer] attempting InputStream device=%s channels=%d samplerate=%d blocksize=%d loopback=%s", device_index, channels_try, self.sr, self.blocksize, self.loopback)
                # use extra_settings for WASAPI loopback when available
                if extra is not None:
                    stream_kwargs = dict(device=device_index, samplerate=self.sr, channels=channels_try, dtype="int16", blocksize=self.blocksize, extra_settings=extra)
                else:
                    stream_kwargs = dict(device=device_index, samplerate=self.sr, channels=channels_try, dtype="int16", blocksize=self.blocksize)

                with sd.InputStream(**stream_kwargs) as stream:
                    LOG.info("[AudioCapturer] InputStream opened (channels=%d)", channels_try)
                    while not self._stop_event.is_set():
                        try:
                            data, overflowed = stream.read(self.blocksize)
                        except Exception as read_err:
                            LOG.exception("[AudioCapturer] error reading from stream: %s", read_err)
                            break
                        if overflowed:
                            LOG.warning("[AudioCapturer] overflow detected")
                        try:
                            chunk = self._normalize(data.copy())
                            self._put_chunk(chunk)
                        except Exception:
                            LOG.exception("[AudioCapturer] error normalizing/putting chunk")
                LOG.info("[AudioCapturer] InputStream closed for channels=%d", channels_try)
                return
            except Exception as e:
                LOG.warning("[AudioCapturer] InputStream failed for channels=%d: %s", channels_try, e)

        # If none succeeded, provide diagnostic
        try:
            devs = sd.query_devices()
            dev_info = []
            for i, d in enumerate(devs):
                dev_info.append(f"{i}:{d.get('name')} (in:{d.get('max_input_channels')}, out:{d.get('max_output_channels')})")
            devs_str = "; ".join(dev_info[:10])
        except Exception:
            devs_str = "unable to query devices"

        error_msg = (
            "AudioCapturer could not open any InputStream. "
            "Tried stereo and mono (with loopback=%s). Review your audio devices and ensure an input or WASAPI loopback-capable output device is present. "
            "Device probe: %s" % (self.loopback, devs_str)
        )
        LOG.error("[AudioCapturer] %s", error_msg)
        raise RuntimeError(error_msg)

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            LOG.debug("[AudioCapturer] start() called but thread is already running")
            return
        self._stop_event.clear()
        if self.recorder_factory is not None:
            target = lambda: self._record_loop_with_factory(self.recorder_factory)
        else:
            target = self._record_loop_sounddevice
        self._thread = threading.Thread(target=target, daemon=True)
        self._thread.start()
        LOG.debug("[AudioCapturer] thread started")

    def stop(self, wait: float = 2.0) -> None:
        LOG.debug("[AudioCapturer] stop() requested")
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=wait)
            self._thread = None

    def read_chunk(self, timeout: float = 0.5) -> Optional[np.ndarray]:
        try:
            return self._q.get(timeout=timeout)
        except queue.Empty:
            return None

    def queue_size(self) -> int:
        return self._q.qsize()
