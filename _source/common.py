# Code comments that differ per language are written as  # [[中文||English]]
# and resolved by build.py.


def M(zh, en):
    return ("md", zh.strip("\n"), en.strip("\n"))


def C(code):
    return ("code", code.strip("\n"))


def J(*parts):
    return "\n".join(p.strip("\n") + "\n" for p in parts)


BASE = r'''
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import Audio, display

sr = 44100

def play(x, gain=0.3):
    # [[np.clip 把超过 ±1 的部分压住,防止爆音||np.clip holds anything beyond ±1 so nothing blows up]]
    return Audio(np.clip(gain * np.asarray(x), -1, 1), rate=sr, normalize=False)

def scope(x, title="", seconds=0.03):
    n = int(sr * seconds)                      # [[只画开头这么多个 sample||only plot this many samples from the start]]
    plt.figure(figsize=(9, 2.5))
    plt.plot(np.arange(n) / sr, np.asarray(x)[:n])
    plt.xlabel("time (s)")
    plt.title(title)
    plt.show()
'''

TABLE = r'''
def make_table(harmonic_amps, N=2048):
    p = np.arange(N) / N                       # [[表里每个位置的 phase,0 到 1||phase of every table position, 0 to 1]]
    table = np.zeros(N)                        # [[先做一张全是 0 的空表||start from an empty table of zeros]]
    for k, amp in enumerate(harmonic_amps, start=1):
        # [[第 k 个 harmonic:在表里走 k 个周期,音量 amp||harmonic k: k cycles across the table, at level amp]]
        table += amp * np.sin(2 * np.pi * k * p)
    return table / np.max(np.abs(table))       # [[normalize:峰值变成 1||normalize: peak becomes 1]]
'''

FRAMES = r'''
def make_frames(F=16, max_harmonics=32, N=2048):
    frames = []
    for f in range(F):
        # [[第 f 张表有几个 harmonic:从 1 个均匀增加到 max_harmonics 个||how many harmonics frame f gets: rising evenly from 1 to max_harmonics]]
        n_h = 1 + round(f * (max_harmonics - 1) / (F - 1))
        frames.append(make_table([1 / k for k in range(1, n_h + 1)], N))
    return np.array(frames)                    # [[叠成二维 array:F 行 × N 列||stack into a 2-D array: F rows × N columns]]

def osc_wavetable(frames, phase, pos):
    F, N = frames.shape

    # [[--- 在哪两张表之间 ---||--- which two frames are we between ---]]
    fpos = np.clip(pos, 0, 1) * (F - 1)        # [[0..1 换算成 0..F-1 的 "表编号",可以带小数||turn 0..1 into a frame number 0..F-1, decimals allowed]]
    f0 = np.floor(fpos).astype(int)            # [[下面那张表||the frame below]]
    f1 = np.minimum(f0 + 1, F - 1)             # [[上面那张表(不超过最后一张)||the frame above (never past the last one)]]
    ffrac = fpos - f0                          # [[离下面那张有多远,0..1||how far above the lower frame, 0..1]]

    # [[--- 在表里的哪两个位置之间(和第 3 集一样)---||--- which two positions inside a table (same as Episode 3) ---]]
    p = phase * N
    i0 = np.floor(p).astype(int) % N           # [[左边的位置||left position]]
    i1 = (i0 + 1) % N                          # [[右边的位置,到表尾绕回 0||right position, wrapping to 0 at the end]]
    frac = p - np.floor(p)                     # [[小数部分||the fractional part]]

    # [[先在每张表内部插值,再在两张表之间插值||interpolate inside each frame first, then between the two frames]]
    a = (1 - frac) * frames[f0, i0] + frac * frames[f0, i1]
    b = (1 - frac) * frames[f1, i0] + frac * frames[f1, i1]
    return (1 - ffrac) * a + ffrac * b
'''

ADSR = r'''
def adsr(t, a, d, s, r, gate):
    a, d, r = max(a, 1e-4), max(d, 1e-4), max(r, 1e-4)    # [[时间不能是 0,否则下面会除以 0||times must not be 0, or we would divide by zero below]]
    # [[按住期间:(0,0) → (a,1) → (a+d,s),之后停在 s||while held: (0,0) → (a,1) → (a+d,s), then stays at s]]
    held = np.interp(t, [0, a, a + d], [0, 1, s])
    # [[松开那一刻 envelope 有多高(可能还没走完 attack)||how high the envelope is at the moment of release (attack may not be finished)]]
    level_at_release = np.interp(gate, [0, a, a + d], [0, 1, s])
    # [[从那个高度用 r 秒直线降到 0;np.clip 让它降到 0 后不再变负||fall from that level to 0 over r seconds; np.clip stops it going negative]]
    released = level_at_release * np.clip(1 - (t - gate) / r, 0, 1)
    return np.where(t < gate, held, released)  # [[松开前用 held,松开后用 released||held before release, released after]]
'''

LOWPASS = r'''
def lowpass(x, cutoff, res=0.0):
    x = np.asarray(x, dtype=float)
    n_samples = len(x)
    # [[cutoff 给一个数或一个 array 都行:统一变成和声音一样长的 array||cutoff may be one number or an array: make it an array as long as the sound]]
    cutoff = np.clip(np.broadcast_to(cutoff, n_samples), 20, sr * 0.45)

    # [[--- 把 cutoff / res 换算成 filter 内部用的系数(每个 sample 一组)---||--- turn cutoff / res into the filter's internal coefficients (one set per sample) ---]]
    g = np.tan(np.pi * cutoff / sr)
    k = 1.414 * (1 - res) + 0.05 * res         # [[damping:res 越大 k 越小,共鸣越强||damping: higher res → smaller k → stronger resonance]]
    a1 = 1 / (1 + g * (g + k))
    a2 = g * a1
    a3 = g * a2

    # [[.tolist() 把 array 变成普通 list:在循环里逐个取数时快很多||.tolist() turns arrays into plain lists: much faster to read one by one in a loop]]
    xs, A1, A2, A3 = x.tolist(), a1.tolist(), a2.tolist(), a3.tolist()
    y = [0.0] * n_samples
    ic1 = ic2 = 0.0                            # [[两个状态变量 = gen~ 里的两个 history||two state variables = two history objects in gen~]]

    for n in range(n_samples):                 # [[一个 sample 一个 sample 按顺序算||one sample at a time, in order]]
        v3 = xs[n] - ic2
        v1 = A1[n] * ic1 + A2[n] * v3
        v2 = ic2 + A2[n] * ic1 + A3[n] * v3    # [[v2 就是 lowpass 的输出||v2 is the lowpass output]]
        ic1 = 2 * v1 - ic1                     # [[更新状态,留给下一个 sample 用||update the state for the next sample]]
        ic2 = 2 * v2 - ic2
        y[n] = v2
    return np.array(y)
'''

PHASOR = r'''
def phasor(freq, n_samples):
    # [[freq / sr = 这一个 sample 里 phase 往前走多少||freq / sr = how far phase advances during one sample]]
    # [[cumsum 把每一步累加起来;% 1 只留小数部分||cumsum adds the steps up; % 1 keeps the fractional part]]
    return np.cumsum(np.broadcast_to(freq, n_samples) / sr) % 1
'''

SYNTH = r'''
def mtof(m):
    return 440 * 2 ** ((m - 69) / 12)          # [[MIDI 69 = 440 Hz;每 12 个半音翻一倍||MIDI 69 = 440 Hz; doubles every 12 semitones]]

def synth(p, dur=2.0, gate=1.2):
    n = int(sr * dur)
    t = np.arange(n) / sr

    # [[两个 envelope||two envelopes]]
    amp_env = adsr(t, p["amp_a"], p["amp_d"], p["amp_s"], p["amp_r"], gate)
    mod_env = adsr(t, p["mod_a"], p["mod_d"], p["mod_s"], p["mod_r"], gate)

    # [[oscillator:wt_pos 旋钮 + mod env 推上去的量||oscillator: the wt_pos knob plus what the mod env adds]]
    phase = phasor(mtof(p["note"]), n)
    x = osc_wavetable(frames, phase, p["wt_pos"] + p["wt_env"] * mod_env)

    # [[filter:cutoff 旋钮,被 mod env 往上推 cut_env 个八度||filter: the cutoff knob, pushed up by cut_env octaves by the mod env]]
    x = lowpass(x, p["cutoff"] * 2 ** (p["cut_env"] * mod_env), p["res"])

    return x * amp_env                         # [[VCA||VCA]]
'''

PRESETS = r'''
presets = {
    "pluck": dict(note=45, wt_pos=0.6, wt_env=0.0, cutoff=300, res=0.2, cut_env=4.0,
                  amp_a=0.005, amp_d=0.30, amp_s=0.0, amp_r=0.10,
                  mod_a=0.001, mod_d=0.15, mod_s=0.0, mod_r=0.10),
    "pad":   dict(note=57, wt_pos=0.2, wt_env=0.5, cutoff=800, res=0.1, cut_env=2.0,
                  amp_a=0.60, amp_d=0.30, amp_s=0.8, amp_r=0.70,
                  mod_a=1.00, mod_d=0.50, mod_s=0.6, mod_r=0.50),
    "wow":   dict(note=33, wt_pos=0.3, wt_env=0.7, cutoff=150, res=0.6, cut_env=4.5,
                  amp_a=0.01, amp_d=0.10, amp_s=0.9, amp_r=0.10,
                  mod_a=0.35, mod_d=0.40, mod_s=0.2, mod_r=0.20),
}
'''

TOOLBOX_ZH = "## 工具箱\n\n前几集做好的东西,原样搬过来。运行一下就行,不用重读(难的地方都有 `#` 注释)。"
TOOLBOX_EN = "## Toolbox\n\nEverything built in earlier episodes, copied as-is. Just run it; no need to re-read (the tricky lines carry `#` comments)."
