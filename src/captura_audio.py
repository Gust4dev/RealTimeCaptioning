import os
import numpy as np
import pyaudiowpatch as pyaudio
from scipy.io.wavfile import write
import wave
import time

class CapturaDeAudio:
    def __init__(self, callback_processamento=None, fs=16000, canais=1):
        """
        Inicializa o módulo de captura de áudio usando PyAudioWPatch para WASAPI.
        - fs: taxa de amostragem desejada para processamento (ex: 16000 Hz)
        """
        self.callback_processamento = callback_processamento
        self.fs = fs  # Taxa desejada para processamento (não aplicada no callback)
        self.canais = canais
        self.chunk_size = 4096
        self.formato = pyaudio.paInt16
        self.p = None
        self.stream = None
        self.gravando = False
        self.frames = []
        self.last_silence_log = 0
        self.device_rate = None  # Taxa nativa do dispositivo

    def iniciar_captura(self, dispositivo_loopback=True, salvar_audio=False, arquivo_saida='data/raw/audio.wav'):
        self.salvar_audio = salvar_audio
        self.arquivo_saida = arquivo_saida
        self.frames = []
        if salvar_audio:
            diretorio = os.path.dirname(arquivo_saida)
            if not os.path.exists(diretorio):
                os.makedirs(diretorio)
                
        self.p = pyaudio.PyAudio()
        try:
            wasapi_info = self.p.get_host_api_info_by_type(pyaudio.paWASAPI)
        except OSError:
            print("WASAPI não disponível. Voltando para dispositivo padrão.")
            self._iniciar_com_dispositivo_padrao()
            return

        dispositivo_padrao = self.p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
        if dispositivo_loopback and not dispositivo_padrao.get("isLoopbackDevice", False):
            dispositivo_encontrado = False
            for loopback in self._get_dispositivos_loopback():
                if dispositivo_padrao["name"] in loopback["name"]:
                    dispositivo_padrao = loopback
                    dispositivo_encontrado = True
                    break
            if not dispositivo_encontrado:
                print("Dispositivo de loopback não encontrado. Usando dispositivo padrão.")
                self._iniciar_com_dispositivo_padrao()
                return

        print(f"Usando dispositivo: {dispositivo_padrao['name']}")
        self.device_rate = int(dispositivo_padrao["defaultSampleRate"])
        print(f"Taxa de amostragem do dispositivo: {self.device_rate} Hz")
        
        def callback(in_data, frame_count, time_info, status):
            try:
                raw_data = np.frombuffer(in_data, dtype=np.int16)
                amp_max = np.max(np.abs(raw_data))
                amp_mean = np.mean(np.abs(raw_data))
                print(f"[Debug] Raw data: shape={raw_data.shape}, Amplitude máxima: {amp_max}, Amplitude média: {amp_mean}")
                if amp_max > 5:
                    if self.salvar_audio:
                        self.frames.append(raw_data.tobytes())
                    if self.callback_processamento:
                        self.callback_processamento(raw_data)
                else:
                    now = time.time()
                    if now - self.last_silence_log > 5:
                        print("Silêncio detectado, ignorando...")
                        self.last_silence_log = now
                return (in_data, pyaudio.paContinue)
            except Exception as e:
                print(f"Erro no callback: {e}")
                return (in_data, pyaudio.paContinue)
        
        self.stream = self.p.open(
            format=self.formato,
            channels=dispositivo_padrao["maxInputChannels"],
            rate=self.device_rate,  # Usando a taxa nativa
            frames_per_buffer=self.chunk_size,
            input=True,
            input_device_index=dispositivo_padrao["index"],
            stream_callback=callback
        )
        self.gravando = True
        print("Captura de áudio iniciada com WASAPI. Pressione Ctrl+C para parar.")
        
    def _get_dispositivos_loopback(self):
        return self.p.get_loopback_device_info_generator()
    
    def _iniciar_com_dispositivo_padrao(self):
        def callback(in_data, frame_count, time_info, status):
            if self.salvar_audio:
                self.frames.append(in_data)
            audio_data = np.frombuffer(in_data, dtype=np.int16)
            if self.callback_processamento:
                self.callback_processamento(audio_data)
            return (in_data, pyaudio.paContinue)
        
        self.stream = self.p.open(
            format=self.formato,
            channels=self.canais,
            rate=self.fs,
            frames_per_buffer=self.chunk_size,
            input=True,
            stream_callback=callback
        )
        self.gravando = True
        print("Captura de áudio iniciada com dispositivo padrão. Pressione Ctrl+C para parar.")
    
    def parar_captura(self):
        if not self.gravando:
            return
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        self.gravando = False
        if self.salvar_audio and self.frames:
            self._salvar_arquivo_audio()
        print("Captura de áudio finalizada.")
    
    def _salvar_arquivo_audio(self):
        # Reconstrói o áudio a partir dos frames gravados
        audio_list = [np.frombuffer(frame, dtype=np.int16) for frame in self.frames]
        if audio_list:
            raw_audio = np.concatenate(audio_list)
        else:
            raw_audio = np.array([], dtype=np.int16)
        # Reamostrar o áudio de 48000 Hz para 16000 Hz usando soxr
        import soxr
        raw_float = raw_audio.astype(np.float32)
        resampled_float = soxr.resample(raw_float, self.device_rate, self.fs)
        resampled_audio = np.clip(np.rint(resampled_float), -32768, 32767).astype(np.int16)
        wf = wave.open(self.arquivo_saida, 'wb')
        wf.setnchannels(self.canais)
        wf.setsampwidth(self.p.get_sample_size(self.formato))
        wf.setframerate(self.fs)  # Define a taxa de saída como 16000 Hz
        wf.writeframes(resampled_audio.tobytes())
        wf.close()
        print(f"Áudio salvo em {self.arquivo_saida}")
    
    def listar_dispositivos(self):
        try:
            wasapi_info = self.p.get_host_api_info_by_type(pyaudio.paWASAPI)
        except Exception as e:
            print(f"Erro ao obter informações do WASAPI: {e}")
            return None
        print("\nDispositivos WASAPI disponíveis:")
        dispositivos = []
        for i in range(self.p.get_device_count()):
            info = self.p.get_device_info_by_index(i)
            if info["hostApi"] == wasapi_info["index"]:
                dispositivos.append((i, info["name"], info.get("isLoopbackDevice", False)))
        for idx, (dev_idx, nome, loopback) in enumerate(dispositivos):
            tipo = "Loopback" if loopback else "Normal"
            print(f"{idx+1}. {nome} ({tipo}) - Índice: {dev_idx}")
        escolha = int(input("\nEscolha o número do dispositivo: ")) - 1
        return dispositivos[escolha][0]
