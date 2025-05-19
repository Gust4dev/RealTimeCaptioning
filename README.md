# Sistema de Transcrição em Tempo Real

Sistema para captura de áudio e transcrição em tempo real usando faster-whisper e WASAPI.

## Visão Geral

Este projeto implementa um sistema de legendagem automática em tempo real. Ele usa o PyAudioWPatch para capturar áudio de dispositivos utilizando WASAPI no Windows, e o modelo faster-whisper para transcrição de fala para texto.

## Requisitos

- Python 3.8+
- PyAudioWPatch para captura de áudio
- faster-whisper para transcrição
- Pacotes adicionais listados em `requirements.txt`

## Instalação

```bash
# Clonar o repositório
git clone https://github.com/seu-usuario/RealTimeCaptioning.git
cd RealTimeCaptioning

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt
```

## Estrutura do Projeto

```
RealTimeCaptioning/
├── audio/                  # Módulos de captura de áudio
│   ├── __init__.py
│   └── capturer.py         # Implementação principal com WASAPI
├── transcription/          # Módulos de transcrição
│   ├── __init__.py
│   └── transcriber.py      # Implementação do transcritor
├── ui/                     # Componentes da interface (futura expansão)
│   └── __init__.py
├── models/                 # Diretório para modelos baixados
├── config.py               # Configurações globais do sistema
├── main.py                 # Ponto de entrada da aplicação
└── requirements.txt        # Dependências do projeto
```

## Configuração

O arquivo `config.py` contém todas as configurações necessárias para o sistema, incluindo:

- **AUDIO**: Configurações de captura de áudio (taxa de amostragem, tamanho do buffer, etc.)
- **TRANSCRIPTION**: Configurações do modelo Whisper (tamanho, dispositivo, parâmetros)
- **UI**: Configurações da interface do usuário

## Uso

O sistema oferece dois modos de operação:

### 1. Interface Completa

```bash
python main.py
```

Inicia a aplicação com interface gráfica completa, permitindo:

- Escolher dispositivo de entrada
- Visualizar estatísticas em tempo real
- Iniciar/parar a transcrição

### 2. Modo Overlay (Legendagem)

```bash
python main.py --overlay
```

Inicia apenas com o overlay de legendas no fundo da tela, ideal para uso durante apresentações ou streaming.

## Características Principais

- **Captura de Áudio com WASAPI**: Suporte a diferentes dispositivos e modos (inclusive loopback)
- **Buffer Circular**: Gestão eficiente de memória com buffer circular para processamento contínuo
- **Detecção de Silêncio**: Filtragem de áudio para processar apenas segmentos com voz
- **Normalização**: Processamento automático para melhorar qualidade da entrada
- **Transcrição Assíncrona**: Processamento em threads separadas para não bloquear a interface

## Solução de Problemas

### Erros de Dispositivo de Áudio

- Verifique se o dispositivo selecionado está disponível e ativo
- Em caso de erro WASAPI, a aplicação deve fazer fallback para o modo padrão

### Problemas de Desempenho

- Para melhor desempenho da CPU, use o modelo "tiny" ou "base"
- Para qualidade superior (requer GPU), use "medium" ou "large"
- Defina `compute_type` como "int8" para melhor desempenho em CPU

## Colaboradores

- Equipe de Desenvolvimento de Software
- Engenheiros de Áudio
- Especialistas em Processamento de Linguagem Natural
