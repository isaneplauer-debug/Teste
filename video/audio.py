"""Gera a trilha (música lo-fi + efeitos sonoros) sincronizada com anim.html.
Uso: python3 audio.py saida.wav
"""
import sys, wave
import numpy as np

SR = 44100
DUR = 89.0
N = int(SR * DUR)
rng = np.random.default_rng(7)
mix = np.zeros((N, 2))


def add(sig, t0, gain=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N:
        return
    sig = sig[: N - i]
    l, r = np.sqrt(0.5 * (1 - pan)), np.sqrt(0.5 * (1 + pan))
    mix[i:i + len(sig), 0] += sig * gain * l
    mix[i:i + len(sig), 1] += sig * gain * r


def env(n, a=0.01, r=0.3):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / r)
    return e


def lowpass(x, cutoff):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (f / cutoff) ** 4)
    return np.fft.irfft(X, len(x))


def bandpass(x, lo, hi):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= (f > lo) & (f < hi)
    return np.fft.irfft(X, len(x))


def note(freq, dur, kind='pad'):
    n = int(dur * SR)
    t = np.arange(n) / SR
    if kind == 'pad':
        s = sum(np.sin(2 * np.pi * freq * d * t + p) for d, p in [(1, 0), (1.003, 1), (0.997, 2), (2.0, .5)]) / 4
        a = np.minimum(1, t / 0.35) * np.minimum(1, (dur - t) / 0.4)
        return s * np.clip(a, 0, 1)
    if kind == 'keys':
        s = np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(4 * np.pi * freq * t) + 0.1 * np.sin(6 * np.pi * freq * t)
        return s * env(n, 0.005, 0.45)
    if kind == 'bass':
        s = np.sin(2 * np.pi * freq * t) + 0.2 * np.sin(4 * np.pi * freq * t)
        return s * np.minimum(1, t / 0.01) * np.exp(-t / 0.6)


def hz(m):
    return 440 * 2 ** ((m - 69) / 12)


# ---------------- music ----------------
BPM = 88
beat = 60 / BPM
bar = 4 * beat
# Am9 - Fmaj7 - C(add9) - G6   (midi)
CHORDS = [[57, 60, 64, 67, 71], [53, 57, 60, 64], [48, 55, 60, 62, 64], [55, 59, 62, 64]]
DARK = [[45, 52, 57, 60, 63], [44, 51, 56, 59]]  # tension (night)

def section(t):
    if t < 4.0: return 'intro'
    if 67.0 <= t < 78.0: return 'dark'
    if t >= 83.0: return 'outro'
    return 'groove'

t = 0.0
k = 0
while t < DUR:
    sec = section(t)
    ch = DARK[k % 2] if sec == 'dark' else CHORDS[k % 4]
    for m in ch:
        add(note(hz(m), bar + 0.4, 'pad'), t, 0.05)
    if sec != 'intro':
        add(note(hz(ch[0] - 12), bar, 'bass'), t, 0.22)
        add(note(hz(ch[0] - 12), beat * 2, 'bass'), t + beat * 2.5, 0.14)
    if sec in ('groove', 'outro'):
        # simple key arpeggio
        for i in range(8):
            m = ch[(i * 2) % len(ch)] + 12
            add(note(hz(m), 0.6, 'keys'), t + i * beat / 2 + (0.02 if i % 2 else 0), 0.035, pan=(-.4 if i % 2 else .4))
    t += bar
    k += 1

# drums
kick_n = int(0.35 * SR); tk = np.arange(kick_n) / SR
kick = np.sin(2 * np.pi * (45 * tk + 60 * (1 - np.exp(-tk * 25)) / 25)) * np.exp(-tk / 0.12)
hat = np.diff(rng.standard_normal(int(0.06 * SR) + 1)) * env(int(0.06 * SR), 0.001, 0.018)
snare = bandpass(rng.standard_normal(int(0.25 * SR)), 900, 6000) * env(int(0.25 * SR), 0.002, 0.07)
t = 4.0
i = 0
while t < DUR:
    sec = section(t)
    if sec in ('groove', 'outro') and not (82.4 < t < 83.0):
        if i % 8 in (0, 5): add(kick, t, 0.55)
        if i % 8 in (2, 6): add(snare, t, 0.18)
        add(hat, t + (0.03 if i % 2 else 0), 0.07 if i % 2 else 0.04, pan=.3)
    elif sec == 'dark' and i % 8 == 0:
        add(kick, t, 0.35)
    t += beat / 2
    i += 1

# ---------------- SFX ----------------
def whoosh(dur=0.45, lo=300, hi=5000, rev=False):
    n = int(dur * SR)
    x = bandpass(rng.standard_normal(n), lo, hi)
    tt = np.linspace(0, 1, n)
    e = np.sin(np.pi * tt ** (0.6 if not rev else 1.6)) ** 2
    return x * e / (np.abs(x).max() + 1e-9)


def pop(f=900, dur=0.09):
    n = int(dur * SR); tt = np.arange(n) / SR
    fr = f * (1 + 1.5 * np.exp(-tt * 60))
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * env(n, 0.001, 0.03)


def chime(base=1320, dur=1.2):
    n = int(dur * SR); tt = np.arange(n) / SR; s = np.zeros(n)
    for j, m in enumerate([0, 7, 12, 19]):
        d = int(j * 0.06 * SR)
        s[d:] += np.sin(2 * np.pi * base * 2 ** (m / 12) * tt[: n - d]) * np.exp(-tt[: n - d] / 0.35)
    return s / 3


def thud():
    n = int(0.5 * SR); tt = np.arange(n) / SR
    return np.sin(2 * np.pi * (55 * tt + 120 * (1 - np.exp(-tt * 30)) / 30)) * np.exp(-tt / 0.15) + 0.4 * lowpass(rng.standard_normal(n), 1200) * env(n, .001, .05)


def blip(f=1500):
    n = int(0.12 * SR); tt = np.arange(n) / SR
    return np.sin(2 * np.pi * f * tt) * env(n, 0.002, 0.04)


def riser(dur):
    n = int(dur * SR); tt = np.arange(n) / SR
    f = 200 * 2 ** (tt / dur * 3)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.4 + bandpass(rng.standard_normal(n), 2000, 9000) * 0.6
    return s * (tt / dur) ** 2


CUTS = [1.65, 4.0, 5.6, 9.0, 15.0, 17.35, 22.0, 27.0, 32.0, 36.9, 39.65, 45.0, 54.0, 58.75, 67.0, 78.0, 80.0, 83.0, 86.4]
for c in CUTS:
    add(whoosh(0.4), c - 0.2, 0.16, pan=rng.uniform(-.5, .5))
add(whoosh(0.5, 200, 3000), 1.45, 0.3)                    # smear ao sentar
add(whoosh(1.0, 400, 7000, rev=True), 4.6, 0.18)           # rewind das datas
add(whoosh(0.35, 1500, 9000), 28.7, 0.22)                  # risco vermelho
add(thud(), 29.4, 0.6)                                      # carimbo MITO
for t0 in [7.2, 10.7, 19.3, 22.8, 33.6, 37.9, 42.4, 47.0, 54.9, 59.0, 60.7]:
    add(pop(900), t0, 0.28)
for j in range(8):
    add(pop(1100 + j * 60, .07), 54.9 + j * .18, 0.15, pan=(j / 4 - 1))
for j in range(12):
    add(pop(1500 + j * 40, .05), 55.4 + j * .14, 0.08, pan=rng.uniform(-.8, .8))
for j in range(3):
    add(pop(500 - j * 60, .12), 64.0 + j * .2, 0.25)
for j in range(5):
    add(pop(420, .14), 69.6 + j * .55, 0.3, pan=rng.uniform(-.6, .6))
for j in range(22):
    add(pop(380 + rng.uniform(-40, 40), .08), 75.6 + j * .07, 0.12, pan=rng.uniform(-.9, .9))
add(lowpass(rng.standard_normal(int(2 * SR)), 140) * env(int(2 * SR), .3, .8), 73.6, 0.6)  # rumble "com detalhe"
add(thud(), 78.3, 0.35); add(chime(1760, 1.0), 78.6, 0.12)
for t0 in [0.42, 6.3, 17.35]:
    add(chime(), t0, 0.14)
add(riser(0.8), 83.0, 0.12); add(chime(990, 1.8), 83.8, 0.2); add(thud(), 83.8, 0.3)
for kk in range(4):  # synapse blips
    add(blip(1300), 32 + 1.2 * kk + .94, 0.12)
for t0 in [40.2, 41.4, 42.6]:
    add(blip(1600 + 200 * (t0 - 40.2)), t0, 0.2)
for j in range(10):  # pencil scribble
    add(bandpass(rng.standard_normal(int(.08 * SR)), 2500, 7000) * env(int(.08 * SR), .005, .03), 85.9 + j * .17, 0.05)

# ---------------- master ----------------
fade = np.minimum(1, np.arange(N) / (0.05 * SR)) * np.minimum(1, (N - np.arange(N)) / (1.2 * SR))
mix *= fade[:, None]
mix = np.tanh(mix * 1.4) / np.tanh(1.4)
mix *= 0.89 / np.abs(mix).max()
pcm = (mix * 32767).astype('<i2')
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('ok', sys.argv[1])
