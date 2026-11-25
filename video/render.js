// Uso:
//   node render.js preview <saida_dir> t1 t2 ...   -> PNGs de quadros específicos
//   node render.js video <saida.mp4> [fps]          -> vídeo mudo (H.264)
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

(async () => {
  const [mode, out, ...rest] = process.argv.slice(2);
  const browser = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  page.on('pageerror', e => console.error('PAGE ERROR', e.message));
  await page.goto('file://' + path.join(__dirname, 'anim.html'));
  await page.evaluate(() => window.ready);
  const grab = async t => {
    const url = await page.evaluate(t => { window.render(t); return document.getElementById('c').toDataURL('image/jpeg', 0.93); }, t);
    return Buffer.from(url.split(',')[1], 'base64');
  };
  if (mode === 'preview') {
    fs.mkdirSync(out, { recursive: true });
    for (const t of rest.map(Number)) fs.writeFileSync(path.join(out, `t${t.toFixed(2)}.jpg`), await grab(t));
  } else {
    const fps = Number(rest[0] || 30), dur = 89, n = Math.round(dur * fps);
    const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
    for (let i = 0; i < n; i++) {
      const buf = await grab(i / fps);
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (i % 150 === 0) console.log(`frame ${i}/${n}`);
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
  }
  await browser.close();
})();
