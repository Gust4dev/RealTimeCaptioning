def salvar_transcricao(texto, arquivo='data/processed/transcricao.txt'):
    with open(arquivo, 'w', encoding='utf-8') as f:
        f.write(texto)
    print(f"Transcrição salva em {arquivo}")
