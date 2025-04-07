import os
import pytest
from src import transcricao

def test_transcricao():
    # Define o caminho para um arquivo de áudio de teste (deve existir em data/raw)
    arquivo = os.path.join("data", "raw", "audio.wav")
    if not os.path.exists(arquivo):
        pytest.skip("Arquivo de áudio de teste não encontrado.")
    texto = transcricao.transcrever_audio(arquivo, modelo='tiny', idioma='pt')
    assert isinstance(texto, str)
    assert len(texto) > 0
