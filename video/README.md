# Vídeo: "E se tu acordasse amanhã com memória perfeita?" (Parte 1)

Animação gerada por código a partir do roteiro em `../roteiro/analise-e-roteiro.md`.

| Arquivo | O que é |
|---|---|
| `memoria-perfeita-parte1.mp4` | Vídeo final 1080x1920, 30 fps, 89 s, com trilha e efeitos |
| `narracao.srt` | Texto da narração com o tempo de cada bloco, para gravar a voz em cima |
| `anim.html` | Toda a animação: personagem, cenários, câmera, legendas, callouts e pós-efeitos |
| `render.js` | Renderiza quadro a quadro com o Chromium (Playwright) e codifica com ffmpeg |
| `audio.py` | Gera a trilha lo-fi e os efeitos sonoros sincronizados com os cortes |

## Personalizar
- **@ do canal:** `CHANNEL` no topo de `anim.html`.
- **Cor das palavras-chave:** `KEY` no topo de `anim.html`.
- **Texto e tempo das legendas:** lista `CAPS` em `anim.html`. Palavras entre `*asteriscos*` saem coloridas.

## Gerar de novo
```bash
npm install                                   # fonte Roboto Condensed
node render.js preview prev 3.2 47 75         # prévia de quadros específicos
node render.js video mudo.mp4 30              # vídeo sem som (~9 min)
python3 audio.py trilha.wav                   # trilha + efeitos
ffmpeg -i mudo.mp4 -i trilha.wav -c:v copy -c:a aac -b:a 192k -shortest memoria-perfeita-parte1.mp4
```

## Gravar a narração
Grave seguindo `narracao.srt` (~140 palavras/min, tom de conversa). Na edição, coloque a voz em cima
do vídeo e abaixe a trilha uns 8–10 dB enquanto houver fala.
