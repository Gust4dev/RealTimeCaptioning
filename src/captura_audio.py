import os
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write

def capturar_audio(duracao=5, fs=16000, canais=1, arquivo='data/raw/audio.wav'):
    """
    Captura áudio do sistema utilizando a biblioteca sounddevice e salva em formato WAV.

    Parâmetros:
      - duracao: duração da gravação em segundos (padrão: 5 segundos)
      - fs: taxa de amostragem (padrão: 16000 Hz)
      - canais: número de canais de áudio (padrão: 1, mono)
      - arquivo: caminho onde o arquivo de áudio será salvo
    """
    # Cria o diretório de destino se não existir
    diretorio = os.path.dirname(arquivo)
    if not os.path.exists(diretorio):
        os.makedirs(diretorio)
    
    print("Iniciando a captura de áudio...")
    
    # Inicia a gravação do áudio
    recording = sd.rec(int(duracao * fs), samplerate=fs, channels=canais, dtype='int16')
    sd.wait()  # Aguarda o término da gravação
    
    # Salva a gravação em um arquivo WAV
    write(arquivo, fs, recording)
    
    print(f"Áudio capturado e salvo em {arquivo}")
