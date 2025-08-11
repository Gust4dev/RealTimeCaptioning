# RealTimeCaptioning

![Logo](docs/logo.png)

**Legendagem automática em tempo real para desktop** — captura local do áudio do sistema, transcrição em streaming e overlay de legendas. Projeto modular, orientado a qualidade, testes e facilidade de contribuição.

---

### Links rápidos

- Repositório: [https://github.com/Gust4dev/RealTimeCaptioning](https://github.com/Gust4dev/RealTimeCaptioning)
- Documentação: `docs/` (MkDocs / LaTeX)
- Issues & Contribuição: abra uma issue no GitHub

---

### Destaques

- Foco em baixíssima latência e precisão para PT‑BR
- Arquitetura modular (captura, ASR, UI) — fácil de extender
- Perfis configuráveis: `low_latency`, `balanced`, `high_accuracy`
- Testes automatizados e CI (lint + pytest)

---

### Começando rápido

```bash
git clone https://github.com/Gust4dev/RealTimeCaptioning.git
cd RealTimeCaptioning
poetry install
poetry shell
make install-dev
poetry run python -m src.core.app --backend mock
```

---

### Estrutura (resumida)

```
src/
├─ audio/   # captura e resampling
├─ asr/     # transcriber / adapters
├─ ui/      # overlay (PySide6)
├─ core/    # orquestrador
└─ config/  # presets e perfis
```

---

### Contribuindo

1. Abra uma issue descrevendo o objetivo
2. Crie branch `feature/<nome>` a partir de `main`
3. Faça PR com testes e descreva as mudanças

---

### Referências e recursos

- Whisper / Faster‑Whisper — [https://github.com/openai/whisper](https://github.com/openai/whisper) / [https://github.com/guillaumekln/faster-whisper](https://github.com/guillaumekln/faster-whisper)
- whisper.cpp — [https://github.com/ggerganov/whisper.cpp](https://github.com/ggerganov/whisper.cpp)
- sounddevice / soundcard — bibliotecas para captura de áudio em Python
- PySide6 / Qt — toolkit recomendado para overlay

---

### Licença

MIT

---

_Arquivo simples e direto. Substitua `docs/logo.png` pela arte do projeto quando disponível._
