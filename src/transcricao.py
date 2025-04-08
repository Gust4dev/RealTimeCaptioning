from faster_whisper import WhisperModel
import numpy as np
import os
import logging
import io
import wave

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class TranscricaoEmTempoReal:
    def __init__(self, modelo='tiny', idioma='pt', dispositivo="cpu", tipo_computacao="int8", device_rate=48000):
        logger.info(f"Carregando modelo Faster Whisper '{modelo}'...")
        self.model = WhisperModel(modelo, device=dispositivo, compute_type=tipo_computacao)
        self.idioma = idioma
        self.buffer_audio = np.array([], dtype=np.int16)
        self.fs = 16000
        self.device_rate = device_rate
        self.ultima_transcricao = ""
        self.buffer_max_segundos = 5  # Buffer menor para menor latência
        self.segmentos_atuais = []
        logger.info("Modelo carregado e pronto para transcrição.")
    
    def processar_audio(self, audio_chunk):
        try:
            # Adiciona o novo chunk ao buffer
            self.buffer_audio = np.append(self.buffer_audio, audio_chunk)
            
            # Mantém apenas os últimos segundos no buffer
            max_samples = int(self.buffer_max_segundos * self.fs)
            if len(self.buffer_audio) > max_samples:
                self.buffer_audio = self.buffer_audio[-max_samples:]
            
            # Processa quando temos pelo menos 2 segundos de áudio
            if len(self.buffer_audio) >= (2 * self.fs):
                # Cria um buffer de áudio em memória
                audio_buffer = io.BytesIO()
                with wave.open(audio_buffer, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)  # 16-bit
                    wf.setframerate(self.fs)
                    wf.writeframes(self.buffer_audio.tobytes())
                
                # Transcreve diretamente do buffer
                segments, info = self.model.transcribe(
                    audio_buffer.getvalue(),
                    beam_size=5,
                    language=self.idioma,
                    condition_on_previous_text=True
                )
                
                self.segmentos_atuais = list(segments)
                if self.segmentos_atuais:
                    novo_texto = " ".join([seg.text for seg in self.segmentos_atuais])
                    if novo_texto != self.ultima_transcricao:
                        self.ultima_transcricao = novo_texto
                        logger.info(f"Transcrição: {novo_texto}")
                        # Mantém apenas o último segundo no buffer para continuidade
                        self.buffer_audio = self.buffer_audio[-self.fs:]
                        return novo_texto
        except Exception as e:
            logger.error(f"Erro no processamento de áudio: {e}")
        return None

def transcrever_audio(arquivo, modelo='tiny', idioma='pt'):
    logger.info("Carregando modelo Faster Whisper...")
    model = WhisperModel(modelo, device="cpu", compute_type="int8")
    logger.info("Transcrevendo áudio...")
    segments, _ = model.transcribe(arquivo, beam_size=3, language=idioma)
    texto = " ".join([seg.text for seg in segments])
    logger.info("Transcrição completa.")
    return texto
