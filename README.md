Segue abaixo a versão atualizada do README em Markdown, organizada e com formatação para ser intuitiva e funcional:

```markdown
# Sistema de Legendagem em Tempo Real para Acessibilidade Digital

![Banner do Projeto](docs/images/banner.png)  
*Legenda: Solução integrada para tornar o conteúdo sonoro acessível por meio de transcrição em tempo real.*

## Visão Geral

O objetivo deste projeto é desenvolver um sistema de **legendagem em tempo real** que capture o áudio reproduzido pelo sistema operacional (via WASAPI em loopback), processe esse áudio localmente utilizando modelos **ASR** (como o *Faster-Whisper*) e exiba as legendas em um **overlay configurável**.  
Para garantir alta qualidade na conversão de taxas de amostragem, o sistema utiliza a biblioteca **soxr** para reamostrar o áudio capturado (a 48000 Hz) para a taxa exigida pelo modelo (16000 Hz).

## Objetivos

- **Transcrição em Tempo Real:**  
  Capturar o áudio do sistema e transcrevê-lo com latência inferior a 500ms, preservando a sincronização com a transmissão.

- **Processamento Neural Otimizado:**  
  Utilizar o *Faster-Whisper* com quantização *int8* e técnicas de beam search para equilibrar velocidade e precisão na transcrição.

- **Resampling de Alta Qualidade:**  
  Empregar a biblioteca *soxr* para converter a taxa nativa (ex.: 48000 Hz) para 16000 Hz, garantindo que o áudio processado possua a velocidade correta.

- **Interface de Exibição Modular:**  
  Desenvolver um overlay intuitivo (através de *PyQt5* ou *pyglet*) para exibir as legendas de forma não intrusiva, com suporte à personalização de posição, tamanho, transparência e contraste.

- **Pipeline Modular:**  
  Organizar os módulos de captura, pré-processamento, transcrição e exibição de forma que o sistema seja facilmente escalável e adaptável a futuras melhorias (como suporte a múltiplos idiomas e integração com outras plataformas).

## Estrutura do Projeto

```
RealTimeCaptioning/
├── data/
│   ├── raw/                # Áudio capturado (em taxa nativa, ex.: 48000 Hz)
│   └── processed/          # Transcrições e áudio processado (reamostrado para 16000 Hz)
├── docs/                   # Documentação e imagens do projeto
├── notebooks/              # Notebooks para experimentação e testes
├── src/
│   ├── __init__.py         # Inicializa o pacote
│   ├── captura_audio.py    # Módulo de captura de áudio via WASAPI
│   ├── transcricao.py      # Módulo de transcrição utilizando Faster-Whisper e soxr
│   └── utils.py            # Funções auxiliares (ex.: salvar transcrições)
├── tests/                  # Testes unitários para os módulos
│   ├── __init__.py
│   ├── test_captura_audio.py
│   └── test_transcricao.py
├── .gitignore              # Arquivos e pastas a serem ignorados pelo Git
├── README.md               # Este arquivo de documentação
└── requirements.txt        # Lista de dependências do projeto
```

## Configuração do Ambiente

1. **Criação do Ambiente Virtual:**

   ```bash
   python -m venv venv
   ```

   Ative o ambiente:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

2. **Instalação das Dependências:**

   As dependências estão listadas em `requirements.txt`. Utilize o seguinte comando:

   ```bash
   pip install -r requirements.txt
   ```

   *Exemplo de `requirements.txt`:*

   ```plaintext
   pyqt5==5.15.9
   sounddevice==0.4.6
   faster-whisper==1.0.3
   numpy==1.23.5
   scipy==1.9.3
   pytest==7.2.0
   pyaudiowpatch==0.2.12.7
   soxr==0.2.0
   ```

3. **Ferramentas de Linting e Formatação (Opcional):**

   - **Flake8:**  
     ```bash
     pip install flake8
     ```
     Configure um arquivo `.flake8` com:
     ```ini
     [flake8]
     max-line-length = 120
     exclude = venv,build,.vscode,__pycache__
     ```
   - **Black:**  
     ```bash
     pip install black
     ```
     Execute: `black src/` para formatar o código.

## Iniciando o Projeto

- **Executando o projeto:**  
  A partir da raiz do projeto, use:
  ```bash
  python -m src.main
  ```
  Isso iniciará o sistema de captura e transcrição em tempo real, processando o áudio do dispositivo de loopback e salvando a transcrição em `data/processed/transcricao_atual.txt`.

## Roadmap (Futuras Extensões)

- **Fase 1 – Protótipo:**  
  Implementação básica dos módulos de captura de áudio e transcrição com integração do soxr para resampling.

- **Fase 2 – Otimização:**  
  Refinamento do pipeline de processamento (ajustes de thresholds, sincronização de timestamps, etc.) e melhorias na interface.

- **Fase 3 – Expansão:**  
  Suporte a múltiplos idiomas, customização avançada do overlay e adaptação para outras plataformas (Linux/macOS).

## Considerações Finais

Este repositório reúne a base para um sistema robusto de legendagem em tempo real. Nosso foco atual é garantir a sincronização correta e evitar o efeito de *slow motion* no áudio, utilizando resampling de alta qualidade via *soxr*. Novas funcionalidades, como a interface visual e suporte a múltiplos idiomas, serão integradas em fases futuras.

---

*Nota:* Este projeto encontra-se em estágio conceitual e de prototipagem. Instruções detalhadas e documentação complementar serão atualizadas conforme o desenvolvimento dos módulos.

---

Esperamos que esta documentação facilite o início do desenvolvimento e a integração de novos recursos. Sinta-se à vontade para contribuir e sugerir melhorias.
```

Este README está formatado para fornecer uma visão clara, objetiva e atrativa do projeto, explicando desde a ideia central até as instruções de início e o roadmap. Ajuste imagens e detalhes conforme necessário para alinhar totalmente com sua identidade visual.