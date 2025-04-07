from src import captura_audio, transcricao, utils

def main():
    # Capturar áudio e salvar no diretório raw
    captura_audio.capturar_audio(duracao=5, fs=16000, canais=1, arquivo='data/raw/audio.wav')
    
    # Transcrever o áudio capturado
    texto = transcricao.transcrever_audio('data/raw/audio.wav', modelo='tiny', idioma='pt')
    
    # Salvar a transcrição no diretório processed
    utils.salvar_transcricao(texto, arquivo='data/processed/transcricao.txt')

if __name__ == '__main__':
    main()
