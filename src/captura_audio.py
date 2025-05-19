import soundcard as sc
import numpy as np
import soxr
import queue

# Fila global para os blocos reamostrados
AUDIO_QUEUE = queue.Queue()

# Taxas de amostragem
INPUT_SAMPLE_RATE = 48000
TARGET_SAMPLE_RATE = 16000
CHANNELS = 1
BLOCK_SIZE = 1024  # frames por bloco antes da reamostragem

def iniciar_captura_loopback_soundcard():
    """
    Captura áudio em loopback do alto-falante padrão usando soundcard.
    Empilha blocos reamostrados em AUDIO_QUEUE.
    """
    # Obtém o alto-falante padrão e o dispositivo de loopback associado
    speaker = sc.default_speaker()
    try:
        mic = sc.get_microphone(speaker.name + " (Loopback)")
    except Exception:
        # fallback a um dispositivo com loopback ativo
        mics = sc.all_microphones(include_loopback=True)
        if not mics:
            raise RuntimeError("Nenhum dispositivo de loopback encontrado via soundcard.")
        mic = mics[0]

    print(f"Usando loopback: {mic.name}")
    recorder = mic.recorder(samplerate=INPUT_SAMPLE_RATE, channels=CHANNELS)

    # Loop de captura
    try:
        with recorder:
            while True:
                block = recorder.record(numframes=BLOCK_SIZE)
                # block: shape (BLOCK_SIZE, CHANNELS)
                mono = np.mean(block, axis=1)
                resampled = soxr.resample(mono, INPUT_SAMPLE_RATE, TARGET_SAMPLE_RATE)
                AUDIO_QUEUE.put(resampled)
    except GeneratorExit:
        pass
    except KeyboardInterrupt:
        pass

    print("Loopback parado.")
