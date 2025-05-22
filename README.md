# 📝 Projeto de Transcrição em Tempo Real com Overlay

> **Status**: 🚧 Em desenvolvimento | 🧪 Fase de testes

Este projeto tem como objetivo criar uma aplicação de *transcrição em tempo real* que capta o áudio do sistema, converte em texto utilizando modelos de IA e exibe esse conteúdo em tempo real como uma sobreposição flutuante na tela (overlay).

---

## 🚀 Tecnologias Utilizadas

* **Python 3.11+**
* **Faster Whisper** (modelo de transcrição leve e eficiente)
* **WASAPI** (captura de áudio do loopback do sistema)
* **soxr** / **sox** (reamostragem de áudio de alta qualidade)
* **Tkinter** / **PyQt** (interface overlay flutuante)
* **Threading / AsyncIO** (paralelismo leve)

---

## 🎯 Objetivos do Projeto

* Capturar todo o áudio reproduzido pelo computador (ex: vídeos, músicas, reuniões, chamadas).
* Processar esse áudio em tempo real com alta fidelidade e precisão.
* Transcrever o áudio para texto usando IA (Faster Whisper).
* Exibir o texto em um overlay transparente, leve, que não interfira no uso da máquina.

---

## 🧩 Estrutura do Projeto

```bash
.
├── src/
│   ├── audio/
│   │   ├── capture.py         # Captura de áudio usando WASAPI
│   │   └── resample.py        # Reamostragem do áudio para 16kHz
│   ├── model/
│   │   └── transcriber.py     # Implementação do modelo Faster Whisper
│   ├── ui/
│   │   └── overlay.py         # Interface gráfica flutuante
│   ├── main.py                # Script principal que conecta os módulos
│   └── config.py              # Parâmetros de configuração
├── assets/
│   └── overlay-example.gif    # GIFs e imagens para documentação
├── requirements.txt           # Dependências do projeto
└── README.md
```

---

## 🛠️ Instalação e Uso

### 1. Clone o repositório

```bash
git clone https://github.com/Gust4dev/RealTimeCaptioning
cd RealTimeCaptioning
```

### 2. Crie um ambiente virtual

```bash
python -m venv venv
source venv/bin/activate  # no Windows: venv\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Execute a aplicação

```bash
python src/main.py
```

---

## ⚙️ Configurações

No arquivo `config.py`, você pode alterar:

```python
MODEL_SIZE = "base"
DEVICE = "cuda"  # ou "cpu"
SAMPLING_RATE = 16000
OVERLAY_POSITION = "top-right"
FONT_SIZE = 18
```

---

## 📌 Funcionalidades Previstas

*

---

## 🧠 Em Desenvolvimento

Atualmente, estamos testando os seguintes pontos:

* 🎧 Compatibilidade com diferentes dispositivos de áudio
* 🔄 Performance da transcrição em tempo real
* 🪞 Comportamento do overlay em diferentes monitores / resoluções
* 🧪 Testes com diferentes modelos do Whisper para encontrar o melhor custo/benefício

---

## 📷 Preview (Mockup)

---

## 🤝 Contribuindo

Sinta-se à vontade para contribuir! Aqui estão algumas formas:

* Criar issues com bugs ou sugestões 💡
* Enviar PRs com melhorias 🧩
* Testar o app em diferentes cenários 🔍

---

## 💬 Contato

📧 [gustavogomes034@outlook.com](mailto:gustavogomes034@outlook.com)
🔗 [linkedin.com/in/gustadev](https://linkedin.com/in/gustadev)

---

> Projeto pessoal com fins educacionais e de pesquisa. Feedbacks são bem-vindos! 💬
