import sys
import logging
from captura_audio import CapturaDeAudio
from transcricao import TranscricaoEmTempoReal

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    try:
        # Inicializar o sistema de transcrição
        transcricao = TranscricaoEmTempoReal(
            modelo='tiny',
            idioma='pt',
            dispositivo="cpu",
            tipo_computacao="int8"
        )
        
        # Função de callback para processar o áudio
        def processar_audio(audio_chunk):
            texto = transcricao.processar_audio(audio_chunk)
            if texto:
                logger.info(f"Transcrição: {texto}")
        
        # Inicializar a captura de áudio
        captura = CapturaDeAudio(
            callback_processamento=processar_audio,
            fs=16000,
            canais=1
        )
        
        logger.info("Iniciando sistema de transcrição em tempo real...")
        captura.iniciar_captura(salvar_audio=False)
        
        # Manter o programa rodando
        try:
            while True:
                pass
        except KeyboardInterrupt:
            logger.info("Encerrando o programa...")
        finally:
            captura.parar_captura()
            
    except Exception as e:
        logger.error(f"Erro no sistema: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 