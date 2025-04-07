from faster_whisper import WhisperModel

def transcrever_audio(arquivo, modelo='tiny', idioma='pt'):
    print("Carregando modelo Faster Whisper...")
    model = WhisperModel(modelo, device="cpu", compute_type="int8")
    print("Transcrevendo áudio...")
    segments, _ = model.transcribe(arquivo, beam_size=3, language=idioma)
    texto = "\n".join([seg.text for seg in segments])
    print("Transcrição completa.")
    return texto
