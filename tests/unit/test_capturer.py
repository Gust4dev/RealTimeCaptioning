import numpy as np
import time
from src.audio.capturer import AudioCapturer


def mock_recorder_factory(samplerate: int, frames_per_chunk: int):
    """
    Yields synthetic audio chunks in int16 to simulate a real recorder.
    We'll produce a simple sine wave chunks and a few noisy frames.
    """
    t = 0
    dt = 1.0 / samplerate
    freq = 440.0
    # produce 10 chunks quickly
    for i in range(10):
        times = np.arange(frames_per_chunk) * dt + t
        tone = 0.25 * np.sin(2.0 * np.pi * freq * times)
        # scale to int16
        int16 = (tone * np.iinfo(np.int16).max).astype(np.int16)
        # stereo: duplicate channel dimension
        stereo = np.stack([int16, int16], axis=1)
        yield stereo
        t += frames_per_chunk * dt
        # little sleep to emulate real capture
        time.sleep(0.01)


def test_capturer_normalization_and_mono():
    capt = AudioCapturer(
        samplerate=16000, block_ms=100, queue_maxsize=5, recorder_factory=mock_recorder_factory
    )
    capt.start()
    # allow some chunks to be produced
    time.sleep(0.2)
    chunk = capt.read_chunk(timeout=1.0)
    capt.stop()
    assert chunk is not None
    assert chunk.dtype == np.float32
    # values should be within [-1, 1]
    assert float(np.max(np.abs(chunk))) <= 1.0 + 1e-6


def test_capturer_queue_drop_oldest():
    def fast_generator(sr, frames):
        # produce many chunks quickly (no sleep)
        for _ in range(20):
            arr = np.ones((frames, 2), dtype=np.int16) * 1000
            yield arr

    capt = AudioCapturer(
        samplerate=8000, block_ms=50, queue_maxsize=3, recorder_factory=fast_generator
    )
    capt.start()
    # let it fill
    time.sleep(0.1)
    size = capt.queue_size()
    capt.stop()
    # queue should not exceed maxsize
    assert size <= 3
