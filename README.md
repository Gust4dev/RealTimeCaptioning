
<p align="center">
  <img src="docs/logo.png" alt="Logo do Projeto" width="200"/>
</p>

<h1 align="center">RealTimeCaptioning</h1>
<p align="center">Sistema de legendagem automática em tempo real para acessibilidade digital</p>

---

## 📖 Sobre o Projeto
O **RealTimeCaptioning** é um sistema integrado de legendagem automática em tempo real, desenvolvido para promover **acessibilidade digital**.  
Utilizando tecnologias avançadas de **Reconhecimento Automático de Fala (ASR)**, o sistema converte áudio em texto instantaneamente, eliminando barreiras de comunicação para pessoas com deficiência auditiva e qualquer usuário que necessite de suporte textual.

Diferenciais:
- Independente de plataformas específicas
- Capacidade de operação em diferentes cenários e dispositivos
- Suporte a múltiplos idiomas (planejado)
- Interface gráfica amigável

---

## 📂 Estrutura do Projeto
```

src/
├── asr/               # Módulo de transcrição de áudio
├── audio/             # Captura e processamento de áudio
├── config/            # Arquivos de configuração
├── core/              # Aplicação principal
├── ui/                # Interfaces gráficas (Qt)
├── utils/             # Utilidades e logging
tests/                  # Testes unitários
docs/                   # Logo e documentação

````

---

## 🚀 Instalação

### Via Python
1. **Clone o repositório**
```bash
git clone https://github.com/seuusuario/RealTimeCaptioning.git
cd RealTimeCaptioning
````

2. **Instale as dependências**

```bash
pip install -r requirements.txt
```

Ou usando o **poetry** (recomendado):

```bash
poetry install
```

### Via Docker

```bash
docker build -t realtime-captioning .
docker run --rm -it realtime-captioning
```

---

## 💻 Uso Básico

```bash
python -m src.core.app
```

O sistema iniciará a captura de áudio e exibirá as legendas em tempo real na interface.

---

## ⚙️ Configuração

Todas as configurações podem ser ajustadas no arquivo:

```
src/config/config.toml
```

Exemplos:

* Taxa de amostragem do áudio
* Idioma de reconhecimento
* Estilo das legendas

---

## 📦 Dependências Principais

* **Python 3.10+**
* PyAudio / sounddevice
* SpeechRecognition / ASR backend
* PyQt5 / PySide6
* NumPy / SciPy

---

## 🤝 Contribuidores

* **Gustavo Gomes dos Santos** — *Universidade Evangélica de Goiás - UniEVANGÉLICA*

---

## 📜 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para mais detalhes.

```
