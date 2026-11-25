# Contexto do projeto (passagem de sessão)

Repositório: `isaneplauer-debug/Teste` · branch `claude/animation-frame-analysis-lyc8vh`

## O que já foi feito
1. **Análise frame a frame** do vídeo de referência do TikTok ("E se tu acordasse amanhã e tivesse 1000 de QI?", @rmhkaiser):
   estilo, ritmo de cortes (~1 a cada 1,8 s), legendas, callouts com números, estrutura narrativa e decupagem
   segundo a segundo. Está em `roteiro/analise-e-roteiro.md`.
2. **Roteiro original nosso:** "E se tu acordasse amanhã com memória perfeita? (Parte 1)", com a personagem Lia
   e a "Lia de rascunho". Fica no mesmo arquivo, seção 5.
3. **Vídeo pronto, mas sem voz:** `video/memoria-perfeita-parte1.mp4` (89 s, 1080x1920, 30 fps, trilha lo-fi + efeitos).
   - Animação feita por código: `video/anim.html` (personagem, cenários, câmera, legendas, callouts, pós-efeitos).
   - Renderização: `video/render.js` (Playwright + ffmpeg). Trilha: `video/audio.py`.
   - Como gerar de novo: `video/README.md`. Troque `CHANNEL` (@ do canal) e `KEY` (cor) no topo do `anim.html`.
4. **Narração pronta para dublar:**
   - `video/narracao-elevenlabs.txt`: 12 blocos, um por cena, com o segundo em que cada um começa.
   - `video/narracao.srt`: cada legenda com o tempo exato.

## O que falta: dublagem com ElevenLabs
- Gerar no ElevenLabs (modelo Eleven Multilingual v2, voz jovem em português, tom de conversa, velocidade ~1.05)
  um áudio por bloco de `video/narracao-elevenlabs.txt`, com os nomes `00.mp3`, `04.mp3`, `09.mp3`, `15.mp3`, `22.mp3`,
  `27.mp3`, `32.mp3`, `45.mp3`, `54.mp3`, `67.mp3`, `78.mp3`, `83.mp3`.
- Colocar cada áudio no segundo indicado. Se algum passar do início do bloco seguinte, acelerar com `atempo` até 1,15x.
- Abaixar a trilha (`audio.py` → `trilha.wav`) uns 8 a 10 dB enquanto houver fala (sidechain/ducking), normalizar para ~-14 LUFS.
- Exportar `video/memoria-perfeita-parte1-dublado.mp4` e fazer commit neste branch.

## Observações
- A sessão anterior rodava na nuvem e não tinha acesso ao navegador do usuário, por isso a dublagem ficou pendente.
- O MP4 tem ~81 MB (o GitHub avisa acima de 50 MB, mas aceita).
