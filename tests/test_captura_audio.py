import os
import pytest
from src import captura_audio

def test_captura_audio(tmp_path):
    # Define o caminho temporário para salvar o arquivo de áudio
    arquivo = tmp_path / "audio.wav"
    # Captura 1 segundo de áudio
    captura_audio.capturar_audio(duracao=1, fs=16000, canais=1, arquivo=str(arquivo))
    # Verifica se o arquivo foi criado e possui conteúdo
    assert os.path.exists(arquivo)
    assert os.path.getsize(arquivo) > 0
