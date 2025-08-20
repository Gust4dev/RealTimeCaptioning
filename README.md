<p align="center">
  <img src="docs/logo.png" alt="Logo do Projeto" width="160"/>
</p>

# RealTimeCaptioning
**Sistema de legendagem automática em tempo real (desktop).**

O RealTimeCaptioning é um projeto open-source que captura áudio do sistema, transcreve em tempo real e exibe legendas como overlay.  
Inicialmente focado em **desktop (Windows / macOS)** e em **pt-BR**, com arquitetura modular para suportar múltiplos backends de ASR no futuro.

---

## ✨ Principais características
- Captura de áudio via loopback do sistema (ex.: WASAPI / CoreAudio)
- Pipeline em streaming com baixa latência
- Backend ASR configurável (ex.: faster-whisper / whisper.cpp / mock)
- Overlay em Qt (PySide6) com opções de estilo
- Estrutura modular, testes automatizados e CI

---

## 📂 Estrutura do repositório

```

docs/                   # logo e documentação
src/
├─ audio/             # captura e resampling (AudioCapturer)
├─ asr/               # transcriber e adapters
├─ ui/                # overlay (PySide6) e config UI
├─ core/              # orchestrator / entrypoint
└─ config/            # config.toml
tests/
Makefile
pyproject.toml

````

---

## 🔧 Requisitos (desenvolvimento)
- Python 3.10+ (recomendado)
- Conda / Miniconda (recomendado) ou Poetry
- Drivers de áudio do SO (PortAudio para sounddevice)
- (opcional) GPU para aceleração de ASR

---

## 🚀 Instalação

### Usando conda (recomendado)
```bash
# criar e ativar ambiente
conda create -n rtc python=3.10 -y
conda activate rtc

# adicionar canal conda-forge
conda config --add channels conda-forge
conda config --set channel_priority strict

# instalar dependências principais
conda install numpy pyside6 python-sounddevice resampy pytest -y
````

### Usando Poetry (alternativa)

```bash
poetry install
poetry shell
```

> Observação: o projeto usa `pyproject.toml`. Caso prefira pip, você pode exportar dependências com:
>
> ```bash
> poetry export -f requirements.txt --output requirements.txt
> ```

---

## ▶️ Execução (modo de desenvolvimento)

Para testar sem carregar modelo ASR pesado, use o backend `mock`:

```bash
python -m src.core.app --backend mock          # direto
poetry run python -m src.core.app --backend mock   # se estiver no ambiente poetry
```

---

## 🧪 Testes e lint

```bash
# rodar testes
pytest -q

# lint/format (pré-requisito: black/flake8 instalados)
make lint
```

---

## ⚙️ Configuração

Configurações principais ficam no arquivo:

```
src/config/config.toml
```

Exemplos de parâmetros:

* `samplerate`
* `perfil` (`low_latency`, `balanced`, `high_accuracy`)
* `device` (dispositivo de áudio)

---

## 👤 Contribuidores

* **Gustavo Gomes dos Santos** — *Universidade Evangélica de Goiás - UniEVANGÉLICA*

> Contribuições são bem-vindas via issues/PRs.

---

## 📜 Licença

MIT — veja `LICENSE`.
