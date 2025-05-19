import threading
import time
import sys
import os
import numpy as np
import soundfile as sf

# Ajusta sys.path para importar módulos de src/
PROJECT_ROOT = os.path.dirname(__file__)
SRC_ROOT = os.path.join(PROJECT_ROOT, "src")
if SRC_ROOT not in sys.path:
    sys.path.insert(0, SRC_ROOT)

from captura_audio import iniciar_captura_loopback_soundcard, AUDIO_QUEUE, TARGET_SAMPLE_RATE
from transcricao import TranscricaoEmTempoReal

def thread_transcricao():
    """
    Lê blocos de AUDIO_QUEUE e alimenta o transcritor.
    """
    transcritor = TranscricaoEmTempoReal(modelo='tiny', idioma='pt')
    while True:
        chunk = AUDIO_QUEUE.get()  # bloqueia até ter um bloco
        transcritor.alimentar(chunk)

def main():
    # Inicia thread de captura (daemon)
    t_cap = threading.Thread(target=iniciar_captura_loopback_soundcard, daemon=True)
    t_cap.start()

    # Inicia thread de transcrição (daemon)
    t_tr = threading.Thread(target=thread_transcricao, daemon=True)
    t_tr.start()

    try:
        print("Sistema de legendagem em tempo real iniciado. Ctrl+C para encerrar.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nInterrompido pelo usuário. Encerrando...")
    finally:
        # Opcional: salvar buffer completo em arquivo para debug
        # Se desejar
        pass

if __name__ == "__main__":
    main()
