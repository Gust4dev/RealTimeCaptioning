import time
import os
import signal
import sys
from src.captura_audio import CapturaDeAudio
from src.transcricao import TranscricaoEmTempoReal, transcrever_audio
from src.utils import salvar_transcricao

def main():
    print("Iniciando sistema de legendagem em tempo real...")
    print("Pressione Ctrl+C para encerrar.")
    
    # Cria os diretórios necessários caso não existam
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    
    # Inicializa o módulo de transcrição
    transcricao = TranscricaoEmTempoReal(modelo='tiny', idioma='pt')
    ultima_transcricao = ""
    
    # Função callback para processar cada chunk de áudio
    def processar_audio(audio_chunk):
        nonlocal ultima_transcricao
        texto = transcricao.processar_audio(audio_chunk)
        if texto and texto != ultima_transcricao:
            ultima_transcricao = texto
            print("\n----- Transcrição Atual -----")
            print(texto)
            print("-------------------------------\n")
            salvar_transcricao(texto, arquivo='data/processed/transcricao_atual.txt')
    
    # Inicializa o módulo de captura de áudio com callback
    captura = CapturaDeAudio(callback_processamento=processar_audio)
    captura.iniciar_captura(dispositivo_loopback=True, salvar_audio=True, arquivo_saida='data/raw/audio.wav')
    
    # Configura o manipulador de sinal para encerramento limpo
    def manipulador_sinal(sig, frame):
        print("\nEncerrando a captura e transcrição...")
        captura.parar_captura()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, manipulador_sinal)
    
    # Loop principal para manter o programa rodando
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nPrograma encerrado pelo usuário.")
    finally:
        captura.parar_captura()

def modo_legado():
    """
    Executa o modo legado (captura e transcrição não em tempo real).
    """
    from src import captura_audio, transcricao, utils
    captura_audio.capturar_audio(duracao=5, fs=16000, canais=1, arquivo='data/raw/audio.wav')
    texto = transcricao.transcrever_audio('data/raw/audio.wav', modelo='tiny', idioma='pt')
    utils.salvar_transcricao(texto, arquivo='data/processed/transcricao.txt')

if __name__ == '__main__':
    # Descomente a linha abaixo para usar o modo legado
    # modo_legado()
    
    # Modo em tempo real
    main()
