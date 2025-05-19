import numpy as np
import tempfile
from scipy.io.wavfile import write
from faster_whisper import WhisperModel

class TranscricaoEmTempoReal:
    """
    Classe para transcrição contínua de áudio em tempo real usando Faster Whisper.
    """

    def __init__(self, modelo='tiny', idioma='pt', device='cpu', compute_type='int8'):
        print(f"Carregando modelo Faster Whisper '{modelo}'...")
        self.model = WhisperModel(modelo, device=device, compute_type=compute_type)
        self.idioma = idioma
        self.fs = 16000  # taxa alvo da captura/reamostragem
        # Buffer circular: guarda áudio até atingirmos segment_seconds
        self.buffer = np.empty((0,), dtype=np.float32)
        self.segment_seconds = 2.0   # tamanho do segmento para transcrever (segundos)
        self.step_seconds = 1.5      # contexto mantido após cada transcrição (segundos)
        print("Transcritor pronto.")

    def alimentar(self, chunk: np.ndarray):
        """
        Alimente o transcritor com um bloco de áudio reamostrado.
        Quando acumular >= segment_seconds, dispara a transcrição.
        """
        self.buffer = np.concatenate([self.buffer, chunk])
        if len(self.buffer) >= int(self.segment_seconds * self.fs):
            self._transcrever_buffer()

    def _transcrever_buffer(self):
        n_samples = int(self.segment_seconds * self.fs)
        to_transcribe = self.buffer[:n_samples]

        # Salva em arquivo temporário para o Whisper ler
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            write(f.name, self.fs, to_transcribe)
            segments, _ = self.model.transcribe(
                f.name,
                beam_size=5,
                language=self.idioma,
                condition_on_previous_text=True
            )

        texto = " ".join([seg.text for seg in segments])
        print(f"[Transcrição] {texto}")

        # Mantém apenas o contexto (step_seconds) para próxima iteração
        keep = int(self.step_seconds * self.fs)
        self.buffer = self.buffer[n_samples - keep:]
