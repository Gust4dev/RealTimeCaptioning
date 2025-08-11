"""
AudioCapturer

Responsibilities:
- Capture audio from system (via sounddevice) OR use an injected recorder (for tests/mocks).
- Normalize audio (int16 -> float32 in [-1, 1]).
- Convert stereo -> mono (by averaging channels) by default.
- Expose fixed-size chunks through a bounded queue with drop-oldest policy.

API:
- AudioCapturer(samplerate=48000, block_ms=500, device=None, queue_maxsize=50, recorder_factory=None)
- start()
- stop()
- read_chunk(timeout=0.5) -> np.ndarray | None
"""

from __future__ import annotations
import threading
import queue
import time
from typing import Callable, Optional, Iterator
import numpy as np


RecorderFactory = Callable[[int, int], Iterator[np.ndarray]]
# RecorderFactory(samplerate, frames_per_chunk) -> yields numpy arrays per chunk


class AudioCapturer:
    def __init__(
        self,
        samplerate: int = 48000,
        block_ms: int = 500,
        device: Optional[str] = None,
        queue_maxsize: int = 50,
        recorder_factory: Optional[RecorderFactory] = None,
    ) -> None:
        self.sr = int(samplerate)
        self.block_ms = int(block_ms)
        self.blocksize = int(self.sr * self.block_ms / 1000)
        self.device = device
        self._q: queue.Queue = queue.Queue(maxsize=queue_maxsize)
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self.recorder_factory = recorder_factory

    def _normalize(self, data: np.ndarray) -> np.ndarray:
        # Convert integer PCM to float32 in [-1, 1]
        if np.issubdtype(data.dtype, np.integer):
            # int16 or int32
            info = np.iinfo(data.dtype)
            data_f = data.astype(np.float32) / max(1, info.max)
        else:
            data_f = data.astype(np.float32)

        # Stereo to mono
        if data_f.ndim > 1 and data_f.shape[1] > 1:
            data_f = data_f.mean(axis=1)

        # Ensure dtype
        return data_f.astype(np.float32)

    def _put_chunk(self, chunk: np.ndarray) -> None:
        try:
            self._q.put_nowait(chunk)
        except queue.Full:
            # drop oldest then push (drop-oldest policy)
            try:
                _ = self._q.get_nowait()
            except queue.Empty:
                pass
            try:
                self._q.put_nowait(chunk)
            except queue.Full:
                # if still full, give up this chunk (should be rare)
                pass

    def _record_loop_with_factory(self, factory: RecorderFactory) -> None:
        # factory yields raw chunks (numpy arrays)
        it = factory(self.sr, self.blocksize)
        for raw in it:
            if self._stop_event.is_set():
                break
            if raw is None:
                continue
            chunk = self._normalize(raw)
            self._put_chunk(chunk)

    def _record_loop_sounddevice(self) -> None:
        # Lazy import to avoid failing environments that don't have sounddevice
        try:
            import sounddevice as sd  # type: ignore
        except Exception as e:
            # Reraise informative error
            raise RuntimeError(
                "sounddevice is required for real capture. Install libportaudio and the sounddevice package."
            ) from e

        # We'll use blocking read pattern
        try:
            with sd.InputStream(
                samplerate=self.sr,
                channels=2,
                dtype="int16",
                blocksize=self.blocksize,
                device=self.device,
            ) as stream:
                while not self._stop_event.is_set():
                    data, overflowed = stream.read(self.blocksize)
                    # data is numpy array shape (frames, channels)
                    if overflowed:
                        # still accept data but log it via print for now
                        print("[AudioCapturer] overflow detected")
                    chunk = self._normalize(data.copy())
                    self._put_chunk(chunk)
        except Exception as e:
            # Bubble up errors to be handled by orchestrator
            print(f"[AudioCapturer] error in capture: {e}")
            raise

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        if self.recorder_factory is not None:
            target = lambda: self._record_loop_with_factory(self.recorder_factory)
        else:
            target = self._record_loop_sounddevice
        self._thread = threading.Thread(target=target, daemon=True)
        self._thread.start()

    def stop(self, wait: float = 2.0) -> None:
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
