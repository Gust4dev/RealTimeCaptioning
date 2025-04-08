import os
import numpy as np
import pyaudiowpatch as pyaudio
import soxr
import wave
import time
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def encontrar_stereo_mix(p):
    device_count = p.get_device_count()
    for i in range(device_count):
        info = p.get_device_info_by_index(i)
        if "stereo mix" in info["name"].lower():
            return i, info
    return None, None

class CapturaDeAudio:
    def __init__(self, callback_processamento=None, fs=16000, canais=1):
        self.callback_processamento = callback_processamento
        self.fs = fs
        self.canais = canais
        self.chunk_size = 4096  # Reduzido para menor latência
        self.formato = pyaudio.paInt16
        self.p = None
        self.stream = None
        self.gravando = False
        self.frames = []
        self.last_silence_log = 0
        self.device_rate = None
        self.buffer_audio = np.array([], dtype=np.int16)
        self.buffer_max_segundos = 5  # Buffer menor para menor latência

    def iniciar_captura(self, salvar_audio=False, arquivo_saida='data/raw/audio.wav'):
        self.salvar_audio = salvar_audio
        self.arquivo_saida = arquivo_saida
        self.frames = []
        if self.salvar_audio:
            diretorio = os.path.dirname(self.arquivo_saida)
            if not os.path.exists(diretorio):
                os.makedirs(diretorio)

        self.p = pyaudio.PyAudio()
        indice, info_stereo = encontrar_stereo_mix(self.p)
        if indice is None:
            logger.error("Erro: Dispositivo 'Stereo Mix' não encontrado. Habilite-o nas configurações de som.")
            exit(1)

        self.device_rate = int(info_stereo["defaultSampleRate"])
        logger.info(f"Usando dispositivo: {info_stereo['name']}")
        logger.info(f"Taxa de amostragem do dispositivo: {self.device_rate} Hz")

        def callback(in_data, frame_count, time_info, status):
            try:
                raw_data = np.frombuffer(in_data, dtype=np.int16)
                amp_max = np.max(np.abs(raw_data))
                
                if amp_max > 5:  # Threshold de silêncio
                    # Processamento em tempo real
                    if self.callback_processamento:
                        # Resample imediatamente para reduzir latência
                        resampled_float = soxr.resample(raw_data.astype(np.float32), self.device_rate, self.fs)
                        resampled_audio = np.clip(np.rint(resampled_float), -32768, 32767).astype(np.int16)
                        self.callback_processamento(resampled_audio)
                    
                    if self.salvar_audio:
                        self.frames.append(raw_data.tobytes())
                else:
                    now = time.time()
                    if now - self.last_silence_log > 5:
                        logger.debug("Silêncio detectado, ignorando...")
                        self.last_silence_log = now
                
                return (in_data, pyaudio.paContinue)
            except Exception as e:
                logger.error(f"Erro no callback: {e}")
                return (in_data, pyaudio.paContinue)

        self.stream = self.p.open(
            format=self.formato,
            channels=info_stereo["maxInputChannels"],
            rate=self.device_rate,
            frames_per_buffer=self.chunk_size,
            input=True,
            input_device_index=indice,
            stream_callback=callback,
            start=False
        )
        
        self.stream.start_stream()
        self.gravando = True
        logger.info("Captura de áudio iniciada com Stereo Mix. Pressione Ctrl+C para parar.")

    def parar_captura(self):
        if not self.gravando:
            return
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        self.gravando = False
        if self.salvar_audio and self.frames:
            self._salvar_arquivo_audio()
        logger.info("Captura de áudio finalizada.")

    def _salvar_arquivo_audio(self):
        if not self.frames:
            return
            
        audio_list = [np.frombuffer(frame, dtype=np.int16) for frame in self.frames]
        raw_audio = np.concatenate(audio_list)
        raw_float = raw_audio.astype(np.float32)
        resampled_float = soxr.resample(raw_float, self.device_rate, self.fs)
        resampled_audio = np.clip(np.rint(resampled_float), -32768, 32767).astype(np.int16)
        
        with wave.open(self.arquivo_saida, 'wb') as wf:
            wf.setnchannels(self.canais)
            wf.setsampwidth(self.p.get_sample_size(self.formato))
            wf.setframerate(self.fs)
            wf.writeframes(resampled_audio.tobytes())
        
        logger.info(f"Áudio salvo em {self.arquivo_saida}")
