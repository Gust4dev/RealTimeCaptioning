"""
Minimal orchestrator / entrypoint for RealTimeCaptioning.

Usage:
  # run with mock transcriber (fast, no models)
  python -m src.core.app --backend mock

  # placeholder for real backend:
  python -m src.core.app --backend real
"""
from __future__ import annotations
import argparse
import logging
import signal
import sys
import threading
import time
from typing import Optional

import numpy as np

# local imports
try:
    from src.audio.capturer import AudioCapturer
except Exception:
    # friendly fallback if module path not found when running from IDE
    from audio.capturer import AudioCapturer  # type: ignore

LOG = logging.getLogger("realtime_captioning")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class MockTranscriber:
    """
    Mock transcriber that simulates a streaming ASR backend.
    It receives audio chunks (numpy arrays) and returns a fake transcription.
    """

    def __init__(self):
        self._counter = 0

    def transcribe_chunk(self, chunk: np.ndarray) -> str:
        # Simple heuristic: compute RMS and return a synthetic text
        if chunk is None or chunk.size == 0:
            return ""
        rms = float(np.sqrt(np.mean(np.square(chunk.astype(np.float32)))))
        self._counter += 1
        # produce a plausible short text
        return f"[MOCK] chunk#{self._counter} rms={rms:.3f}"


class App:
    def __init__(self, backend: str = "mock") -> None:
        self.backend = backend
        self._stop = threading.Event()

        # AudioCapturer default params: 16k/50-500ms etc. adjust as needed
        self.capturer = AudioCapturer(samplerate=16000, block_ms=300, queue_maxsize=20, loopback=True)
        # Choose transcriber backend
        if backend == "mock":
            self.transcriber = MockTranscriber()
        else:
            # placeholder for real implementation
            LOG.warning("Real backend requested but not implemented. Falling back to mock.")
            self.transcriber = MockTranscriber()

        self._worker_thread: Optional[threading.Thread] = None

    def start(self) -> None:
        LOG.info("Starting AudioCapturer...")
        try:
            self.capturer.start()
        except Exception as e:
            LOG.exception("Failed to start AudioCapturer: %s", e)
            raise

        self._stop.clear()
        self._worker_thread = threading.Thread(target=self._run_loop, daemon=True)
        self._worker_thread.start()
        LOG.info("App started. Press Ctrl+C to stop.")

    def stop(self) -> None:
        LOG.info("Stopping app...")
        self._stop.set()
        try:
            self.capturer.stop()
        except Exception:
            LOG.exception("Error stopping capturer (ignored).")
        if self._worker_thread:
            self._worker_thread.join(timeout=2.0)
        LOG.info("Stopped.")

    def _run_loop(self) -> None:
        """
        Main loop: read chunks from capturer, run transcriber, print results.
        """
        while not self._stop.is_set():
            chunk = self.capturer.read_chunk(timeout=0.5)
            if chunk is None:
                # no audio available; continue
                continue
            try:
                text = self.transcriber.transcribe_chunk(chunk)
                if text:
                    LOG.info("TRANSCRIBED: %s", text)
            except Exception:
                LOG.exception("Transcription error (continuing).")

        LOG.debug("Worker loop exiting.")


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="realtime-captioning")
    parser.add_argument("--backend", choices=("mock", "real"), default="mock", help="ASR backend to use")
    args = parser.parse_args(argv)

    app = App(backend=args.backend)

    # handle SIGINT/SIGTERM cleanly
    def _sig_handler(signum, frame):
        LOG.info("Signal received, shutting down...")
        app.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, _sig_handler)
    signal.signal(signal.SIGTERM, _sig_handler)

    try:
        app.start()
        # main thread just waits while worker runs
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        LOG.info("KeyboardInterrupt received.")
        app.stop()
    except Exception:
        LOG.exception("Fatal error in main loop.")
        app.stop()
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
