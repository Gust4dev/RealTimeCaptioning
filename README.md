# Sistema de Legendagem em Tempo Real para Acessibilidade Digital

## Visão Geral

Este projeto tem como objetivo desenvolver um sistema de _legendagem em tempo real_ que torna o conteúdo sonoro acessível para usuários com deficiência auditiva e para aqueles que necessitam de suporte visual em ambientes ruidosos. A solução proposta integra _captura de áudio_ diretamente do sistema operacional, processamento local utilizando modelos _ASR_ (como _Faster-Whisper_) e exibição de legendas por meio de um _overlay_ configurável.

## Objetivos

- **Transcrição em Tempo Real**: Capturar o áudio reproduzido no sistema (via _WASAPI_ em Windows) e transcrevê-lo de forma contínua com _latência_ inferior a 500ms.
- **Processamento Neural Otimizado**: Utilizar o _Faster-Whisper_ com _quantização int8_ e técnicas de _beam search_ para balancear _velocidade_ e _precisão_ na transcrição.
- **Interface de Exibição**: Desenvolver um _overlay_ não intrusivo e personalizável para a apresentação das legendas, permitindo ajustes em posição, tamanho, transparência e estilo.
- **Pipeline Modular**: Implementar um fluxo de processamento com módulos independentes para _captura_, _pré-processamento_, _transcrição_ e _exibição_, possibilitando futuras expansões e adaptações para outras plataformas.

## Especificações Técnicas

- **Captura de Áudio**:

  - **Plataforma**: Windows (utilizando _WASAPI_ em modo _loopback_)
  - **Parâmetros**: Taxa de amostragem de 16kHz, formato _PCM 16-bit mono_, _buffer_ dinâmico de 50–200ms
  - **Filtros DSP**: Implementação de supressão de ruído (ex.: _RNNoise_)

- **Processamento e Transcrição**:

  - **Modelo**: _Faster-Whisper_ (com suporte a _int8_ para quantização)
  - **Configurações**: Beam size = 3, janelas de 500ms com sobreposição, Voice Activity Detection (VAD) habilitado
  - **Técnicas Adicionais**: Decodificação incremental, uso de _DTW_ para alinhamento e correção ortográfica

- **Interface de Exibição**:
  - **Abordagem**: Overlay configurável, utilizando frameworks como _PyQt5_ ou _pyglet_ (com integração ao _DWM_ no Windows)
  - **Recursos**: Ajuste de posição, tamanho, transparência e contraste adaptativo

## Configuração do Ambiente

Para garantir a reprodutibilidade e isolamento das dependências, seguimos as práticas profissionais abaixo:

1. **Ambiente Virtual**:

   - Crie um ambiente virtual usando:
     ```bash
     python -m venv venv
     ```
   - Ative o ambiente:
     - No Windows:
       ```bash
       venv\Scripts\activate
       ```
     - No macOS/Linux:
       ```bash
       source venv/bin/activate
       ```

2. **Instalação de Dependências**:

   - Liste as dependências em `requirements.txt`:
     ```plaintext
     pyqt5
     sounddevice
     faster-whisper
     numpy
     ```
   - Instale-as com:
     ```bash
     pip install -r requirements.txt
     ```
   - Para congelar as versões, execute:
     ```bash
     pip freeze > requirements.txt
     ```

3. **Ferramentas de Linting e Formatação**:

   - Utilize o **Flake8** para análise estática:
     ```bash
     pip install flake8
     ```
   - Configure o `.flake8`:
     ```ini
     [flake8]
     max-line-length = 120
     exclude = venv,build,.vscode,__pycache__
     ```
   - Utilize o **Black** para formatação automática:
     ```bash
     pip install black
     ```
   - Instruções para formatação: `black src/`

4. **Controle de Versão e CI**:
   - O repositório inclui um arquivo `.gitignore` (veja abaixo) para ignorar arquivos e pastas indesejadas.
   - Planeje a configuração de uma pipeline CI (ex.: GitHub Actions) para rodar testes e validações de linting automaticamente.

## Roadmap e Futuras Extensões

- **Fase 1 – Protótipo**: Implementação básica dos módulos de captura de áudio e transcrição, juntamente com uma interface de exibição simples.
- **Fase 2 – Otimização**: Melhoria dos pipelines de processamento com técnicas de segmentação, threading e quantização, visando reduzir a latência e aprimorar a precisão.
- **Fase 3 – Expansão**: Integração de suporte para múltiplos idiomas, personalizações avançadas na interface e adaptações para plataformas adicionais (Linux/macOS).

## Considerações Finais

Este repositório reúne as ideias e os objetivos iniciais para o desenvolvimento de uma solução robusta e escalável de legendagem em tempo real. A proposta visa não somente atender a demandas de acessibilidade, mas também estabelecer um framework modular que permita futuras expansões e adaptações conforme novas necessidades surgirem.

_Nota_: Este projeto encontra-se em estágio conceitual e de planejamento. Instruções de execução e documentação detalhada serão atualizadas conforme o desenvolvimento dos módulos.
