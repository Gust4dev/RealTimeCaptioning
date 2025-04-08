from faster_whisper import WhisperModel
import numpy as np
import os
from scipy.io.wavfile import write
import soxr  # Biblioteca para reamostragem de alta qualidade

class TranscricaoEmTempoReal:
    def __init__(self, modelo='tiny', idioma='pt', dispositivo="cpu", tipo_computacao="int8", device_rate=48000):
        print(f"Carregando modelo Faster Whisper '{modelo}'...")
        self.model = WhisperModel(modelo, device=dispositivo, compute_type=tipo_computacao)
        self.idioma = idioma
        self.buffer_audio = np.array([], dtype=np.int16)
        self.fs = 16000  # Taxa de amostragem desejada para transcrição
        self.device_rate = device_rate  # Taxa nativa do dispositivo (ex.: 48000 Hz)
        self.ultima_transcricao = ""
        self.buffer_max_segundos = 30  # Máximo de segundos a acumular no buffer
        self.segmentos_atuais = []
        self.arquivo_temp = os.path.join("data", "raw", "temp_audio.wav")
        print("Modelo carregado e pronto para transcrição.")
    
    def processar_audio(self, audio_chunk):
        # Acumula a amostra raw (capturada a 48000 Hz) no buffer
        self.buffer_audio = np.append(self.buffer_audio, audio_chunk)
        max_samples = int(self.buffer_max_segundos * self.device_rate)
        if len(self.buffer_audio) > max_samples:
            self.buffer_audio = self.buffer_audio[-max_samples:]
        
        # Dispara a transcrição quando acumular pelo menos 2 segundos de áudio raw
        if len(self.buffer_audio) >= (2 * self.device_rate):
            # Reamostrar o buffer de 48000 Hz para 16000 Hz usando soxr
            resampled_float = soxr.resample(self.buffer_audio.astype(np.float32), self.device_rate, self.fs)
            resampled_audio = np.clip(np.rint(resampled_float), -32768, 32767).astype(np.int16)
            duracao = len(resampled_audio) / self.fs
            print(f"Transcrevendo {duracao:.2f} segundos de áudio reamostrado...")
            # Salva o áudio reamostrado em um arquivo temporário para transcrição
            write(self.arquivo_temp, self.fs, resampled_audio)
            segments, info = self.model.transcribe(
                self.arquivo_temp, 
                beam_size=5, 
                language=self.idioma,
                condition_on_previous_text=True
            )
            print(f"Info da transcrição: {info}")
            self.segmentos_atuais = list(segments)
            if self.segmentos_atuais:
                novo_texto = " ".join([seg.text for seg in self.segmentos_atuais])
                if novo_texto != self.ultima_transcricao:
                    self.ultima_transcricao = novo_texto
                    # Mantém um overlap de 1 segundo raw para continuidade
                    self.buffer_audio = self.buffer_audio[-self.device_rate:]
                    return self.ultima_transcricao
        return None

def transcrever_audio(arquivo, modelo='tiny', idioma='pt'):
    print("Carregando modelo Faster Whisper...")
    model = WhisperModel(modelo, device="cpu", compute_type="int8")
    print("Transcrevendo áudio...")
    segments, _ = model.transcribe(arquivo, beam_size=3, language=idioma)
    texto = " ".join([seg.text for seg in segments])
    print("Transcrição completa.")
    return texto
