from setuptools import setup, find_packages

setup(
    name="real-time-captioning",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pyqt5==5.15.9",
        "sounddevice==0.4.6",
        "faster-whisper==0.9.0",
        "numpy>=1.24.0",
        "scipy>=1.10.0",
        "pytest==7.2.0",
        "pyaudiowpatch==0.2.12.7",
        "soxr==0.3.5",
        "torch>=2.0.0",
        "torchaudio>=2.0.0",
    ],
    python_requires=">=3.8",
) 