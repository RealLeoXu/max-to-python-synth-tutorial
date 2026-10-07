from common import *

EP = dict(
    zh_file="10_看见声音_再回到Max",
    en_file="10_seeing_sound_and_back_to_max",
    cells=[
        M(r'''
# 第 10 集 — 看见声音,再回到 Max

⏱ 约 25 分钟

**这一集控制的音乐元素:没有新的。** 这一集是把 Python 里做的东西 **看清楚** 并 **带回 Max**。

**Max 里的对应:** `spectroscope~`(看),`buffer~` 的 `read`(读 wavetable),`dict` 的 `read`(读 preset)。

**你会听到:** 第 8 集的三个 preset — 这次同时看着它们的 spectrogram 听。

**你会得到两个文件:**
- `export/wavetable.wav`:16 个 frame 的 wavetable
- `export/presets.json`:三个 preset

**学完你能做到:**
- 读懂 spectrum 和 spectrogram
- 从 spectrogram 上认出 filter envelope、pitch 变化、wavetable morph
- 把 wavetable 和 preset 导出成 Max 能读的文件
''', r'''
# Episode 10 — Seeing Sound, and Back to Max

⏱ About 25 minutes

**Musical element this episode controls: nothing new.** This episode is about **seeing clearly** what we built in Python and **taking it back to Max**.

**The Max equivalents:** `spectroscope~` (look), `read` on `buffer~` (load the wavetable), `read` on `dict` (load presets).

**What you will hear:** the three presets from Episode 8 — this time while looking at their spectrograms.

**You will end up with two files:**
- `export/wavetable.wav`: the 16-frame wavetable
- `export/presets.json`: the three presets

**By the end you can:**
- read a spectrum and a spectrogram
- recognise a filter envelope, a pitch change and a wavetable morph in a spectrogram
- export a wavetable and presets as files Max can read
'''),
        M(TOOLBOX_ZH, TOOLBOX_EN),
        C(J(BASE, r'''
import os
import json
from scipy.io import wavfile
''', TABLE, FRAMES, ADSR, LOWPASS, PHASOR, SYNTH, PRESETS, r'''
frames = make_frames()

n = sr                                         # [[1 秒||1 second]]
t = np.arange(n) / sr
''')),
        M(r'''
## 1. Spectrum:声音的 "成分表"

波形图(`scope~`)告诉你 **每一刻的振幅**。它回答不了 "这个声音亮不亮"。

spectrum(`spectroscope~`)换一个角度:**这个声音里有哪些频率,各有多响。**

把声音变成 spectrum 的运算叫 FFT。这里不讲它怎么算,只讲怎么读。下面的函数第 6 集见过。

- 横轴:频率(Hz)
- 纵轴:响度(dB)。0 = 最响的那个频率;每低 20 dB,振幅变成十分之一

### 一个 sine

**先猜:** 一个 440 Hz 的 sine,spectrum 长什么样?
''', r'''
## 1. The spectrum: a sound's "list of ingredients"

A waveform plot (`scope~`) shows **the amplitude at each moment**. It cannot answer "is this sound bright?".

A spectrum (`spectroscope~`) takes another view: **which frequencies are in this sound, and how loud is each.**

The operation that turns a sound into a spectrum is the FFT. How it computes is not covered here, only how to read it. The function below appeared in Episode 6.

- horizontal: frequency (Hz)
- vertical: level (dB). 0 = the loudest frequency; every 20 dB down is one tenth of the amplitude

### One sine

**Guess first:** what does the spectrum of a 440 Hz sine look like?
'''),
        C(r'''
def spectrum(x):
    X = np.abs(np.fft.rfft(x * np.hanning(len(x))))        # [[每个频率的强度||the strength of every frequency]]
    f = np.fft.rfftfreq(len(x), 1 / sr)                    # [[对应的频率刻度(Hz)||the matching frequency axis (Hz)]]
    return f, 20 * np.log10(X / np.max(X) + 1e-9)          # [[换成 dB,最响的是 0||converted to dB, loudest = 0]]

def spec_plot(signals, max_freq=5000):
    plt.figure(figsize=(9, 3.5))
    for name in signals:
        f, db = spectrum(signals[name])
        plt.plot(f, db, label=name, linewidth=0.8)
    plt.xlim(0, max_freq)
    plt.ylim(-90, 5)
    plt.xlabel("frequency (Hz)")
    plt.ylabel("level (dB)")
    plt.legend()
    plt.show()

sine440 = np.sin(2 * np.pi * 440 * t)
spec_plot({"sine 440 Hz": sine440}, max_freq=2000)
'''),
        M(r'''
答案:一根竖线,在 440 Hz。sine 只包含一个频率 — 这就是它听起来 "干净" 的原因。

### 两个 sine 加起来

第 1 集做过和弦:把 sine 加起来。

**应该看到:** 两根竖线,在 440 和 660 Hz。660 那根矮 6 dB,因为它的振幅是一半。
''', r'''
Answer: a single spike at 440 Hz. A sine contains one frequency only — which is why it sounds "clean".

### Two sines added

Episode 1 built a chord by adding sines.

**You should see:** two spikes, at 440 and 660 Hz. The one at 660 is 6 dB shorter because its amplitude is half.
'''),
        C(r'''
two = np.sin(2 * np.pi * 440 * t) + 0.5 * np.sin(2 * np.pi * 660 * t)
spec_plot({"440 Hz + 660 Hz at half level": two}, max_freq=2000)
'''),
        M(r'''
### Wavetable 的 frame

第 3 集的表是 "叠 harmonic" 做的。spectrum 把这些 harmonic 重新摊开给你看。

**应该看到:**
- frame 0:一根线(110 Hz)
- frame 15:32 根等间距的线(110、220、330 …… 到 3520 Hz),越往右越矮

**"暗" 和 "亮" 在图上就是:竖线少 / 竖线多。**
''', r'''
### Wavetable frames

The tables of Episode 3 were built by "stacking harmonics". The spectrum spreads those harmonics back out for you.

**You should see:**
- frame 0: one spike (110 Hz)
- frame 15: 32 evenly spaced spikes (110, 220, 330 ... up to 3520 Hz), getting shorter to the right

**"Dark" and "bright" on the plot simply mean: few spikes / many spikes.**
'''),
        C(r'''
phase = phasor(110, n)

spec_plot({
    "frame 15 (wt_pos = 1)": osc_wavetable(frames, phase, 1.0),
    "frame 0 (wt_pos = 0)": osc_wavetable(frames, phase, 0.0),
})
'''),
        M(r'''
### Filter 做了什么

**应该看到:** 过了 lowpass 之后,同样那一排竖线,600 Hz 以上的被压低了,而 600 Hz 那里因为 resonance 顶起了一个峰。
''', r'''
### What the filter did

**You should see:** after the lowpass the same row of spikes, with those above 600 Hz pushed down and a peak raised at 600 Hz by the resonance.
'''),
        C(r'''
raw = osc_wavetable(frames, phase, 1.0)

spec_plot({
    "raw": raw,
    "lowpass 600 Hz, res 0.8": lowpass(raw, 600, 0.8),
}, max_freq=4000)
'''),
        M(r'''
## 2. Spectrogram:会动的 spectrum

spectrum 是一张 "照片":它把整段声音压成一张图,看不出 **什么时候** 发生了什么。

spectrogram 是 "录像":把声音切成很多小段,每段算一次 spectrum,竖着排起来。

- 横轴:时间
- 纵轴:频率
- 颜色:越亮越响

### 一个上滑的 sine

**先猜:** 一个从 100 Hz 滑到 4000 Hz 的 sine,spectrogram 长什么样?
''', r'''
## 2. The spectrogram: a spectrum that moves

A spectrum is a "photo": it squeezes the whole sound into one picture and cannot show **when** something happened.

A spectrogram is a "video": cut the sound into many short pieces, compute a spectrum for each and line them up side by side.

- horizontal: time
- vertical: frequency
- colour: brighter = louder

### A rising sine

**Guess first:** what does the spectrogram of a sine gliding from 100 Hz to 4000 Hz look like?
'''),
        C(r'''
def spectrogram(x, title="", max_freq=4000):
    plt.figure(figsize=(9, 3.5))
    # [[NFFT = 每一小段多长;noverlap = 相邻两段重叠多少||NFFT = length of each piece; noverlap = how much neighbouring pieces overlap]]
    with np.errstate(divide="ignore"):         # [[完全静音的地方算 dB 会警告,这里忽略它||fully silent parts trigger a warning when converted to dB; ignore it here]]
        plt.specgram(x + 1e-9, NFFT=2048, Fs=sr, noverlap=1536, cmap="magma", vmin=-120)
    plt.ylim(0, max_freq)
    plt.xlabel("time (s)")
    plt.ylabel("frequency (Hz)")
    plt.title(title)
    plt.show()

glide = np.sin(2 * np.pi * phasor(np.geomspace(100, 4000, n), n))

spectrogram(glide, "sine gliding 100 -> 4000 Hz")
play(glide)
'''),
        M(r'''
答案:一条往上弯的亮线。它是弯的而不是直的,因为我们用了 `geomspace`(按倍数走),而图的纵轴是按 Hz 画的。

### 三个 preset

现在看第 8 集的三个 preset。**先听,再看图,把听到的东西在图上找出来。**

**pluck — 应该看到:** 最左边一条很窄的竖直亮带(开头那一下很亮),然后迅速只剩底部几条线,0.4 秒后全黑。
''', r'''
Answer: a bright line curving upward. It curves rather than running straight because we used `geomspace` (moving by ratio) while the plot's vertical axis is in Hz.

### The three presets

Now the three presets from Episode 8. **Listen first, then look, and find what you heard in the picture.**

**pluck — you should see:** a very narrow bright vertical band at the far left (the bright onset), then quickly only a few lines at the bottom, and black after 0.4 seconds.
'''),
        C(r'''
x = synth(presets["pluck"])
display(play(x))
spectrogram(x, "pluck")
'''),
        M(r'''
**pad — 应该看到:** 水平的线从左边慢慢 "亮起来"(淡入),同时亮的区域慢慢往上长(变亮),1.2 秒后整体渐暗。
''', r'''
**pad — you should see:** horizontal lines slowly "lighting up" from the left (the fade-in) while the bright region grows upward (brightening), then everything dimming after 1.2 seconds.
'''),
        C(r'''
x = synth(presets["pad"])
display(play(x))
spectrogram(x, "pad")
'''),
        M(r'''
**wow — 应该看到:** 底部一排很密的水平线(低音的 harmonic 间距小)。亮的区域先往上鼓起来,到 0.35 秒左右最高,然后落回去。

你听到的 "wow" 就是图上那个鼓包。它的形状就是 mod envelope 的形状。
''', r'''
**wow — you should see:** a dense row of horizontal lines at the bottom (a low note's harmonics are close together). The bright region bulges upward, peaks around 0.35 seconds and settles back.

The "wow" you hear is that bulge. Its shape is the shape of the mod envelope.
'''),
        C(r'''
x = synth(presets["wow"])
display(play(x))
spectrogram(x, "wow", max_freq=3000)
'''),
        M(r'''
### 小测验:看图猜参数

下面三个声音是同一个 preset 改了 **一个** 参数得到的。不听,只看图,猜每张图改的是什么:

- (a) `cut_env` 改成 0
- (b) `note` 提高一个八度
- (c) `mod_a` 改成 1.0
''', r'''
### A quiz: guess the parameter from the picture

The three sounds below are one preset with **one** parameter changed each. Without listening, look at the pictures and guess what was changed in each:

- (a) `cut_env` set to 0
- (b) `note` raised one octave
- (c) `mod_a` set to 1.0
'''),
        C(r'''
base = presets["wow"]
quiz = {
    "A": dict(base, mod_a=1.0),
    "B": dict(base, cut_env=0.0),
    "C": dict(base, note=base["note"] + 12),
}

fig, axes = plt.subplots(1, 3, figsize=(13, 3), sharey=True)
for ax, name in zip(axes, quiz):
    with np.errstate(divide="ignore"):
        ax.specgram(synth(quiz[name]) + 1e-9, NFFT=2048, Fs=sr, noverlap=1536, cmap="magma", vmin=-120)
    ax.set_ylim(0, 3000)
    ax.set_title(name)
    ax.set_xlabel("time (s)")
axes[0].set_ylabel("frequency (Hz)")
plt.show()
'''),
        M(r'''
<details><summary>答案</summary>

- **A = (c)** `mod_a = 1.0`:鼓包的最高点移到了 1 秒处,上升得很慢。
- **B = (a)** `cut_env = 0`:没有鼓包,亮的区域全程一样高(filter 不动)。
- **C = (b)** 高一个八度:水平线之间的间距变成两倍。

</details>

听一下确认:
''', r'''
<details><summary>Answer</summary>

- **A = (c)** `mod_a = 1.0`: the top of the bulge has moved to 1 second; it rises very slowly.
- **B = (a)** `cut_env = 0`: no bulge; the bright region stays at one height throughout (the filter does not move).
- **C = (b)** one octave up: the spacing between the horizontal lines has doubled.

</details>

Listen to confirm:
'''),
        C(r'''
for name in quiz:
    print(name)
    display(play(synth(quiz[name])))
'''),
        M(r'''
## 3. 把 wavetable 送回 Max

`frames` 是 16 × 2048 的二维 array。wav 文件是一维的。所以要把它 "摊平":frame 0 接 frame 1 接 frame 2……

`.reshape(-1)` 就是摊平。先看一个小例子:
''', r'''
## 3. Sending the wavetable back to Max

`frames` is a 16 × 2048 2-D array. A wav file is 1-D. So it has to be "flattened": frame 0, then frame 1, then frame 2 ...

`.reshape(-1)` does the flattening. A small example first:
'''),
        C(r'''
m = np.array([[1, 2, 3],
              [10, 20, 30]])

print("2-D:", m.shape)
print(m)
print("flattened:", m.reshape(-1))             # [[一行接一行||one row after another]]
'''),
        M(r'''
这是 wavetable 文件最常见的排法:每个 frame 2048 个 sample,首尾相接。Serum 这类 wavetable synth 可以按这个格式导入。

文件会写到 notebook 旁边的 `export/` 文件夹。
''', r'''
This is the most common layout for wavetable files: 2048 samples per frame, end to end. Wavetable synths such as Serum can import it.

The file is written to an `export/` folder next to the notebook.
'''),
        C(r'''
os.makedirs("export", exist_ok=True)

flat = frames.reshape(-1).astype(np.float32)   # [[16 × 2048 → 32768 个 sample 的一条||16 × 2048 → one run of 32768 samples]]
wavfile.write("export/wavetable.wav", sr, 0.9 * flat)

print("frames:", frames.shape[0])
print("samples per frame:", frames.shape[1])
print("total samples in file:", len(flat))
'''),
        M(r'''
### 验证

读回来,取出第 5 个 frame(sample 5 × 2048 到 6 × 2048),和原来的 `frames[5]` 比较。
''', r'''
### Verify

Load it back, take out frame 5 (samples 5 × 2048 to 6 × 2048) and compare with the original `frames[5]`.
'''),
        C(r'''
file_sr, loaded = wavfile.read("export/wavetable.wav")

k = 5
N = frames.shape[1]
frame_from_file = loaded[k * N : (k + 1) * N]          # [[第 k 个 frame 在文件里的位置||where frame k sits in the file]]

print("frame 5 matches:", np.allclose(frame_from_file, 0.9 * frames[k], atol=1e-6))
'''),
        M(r'''
### 在 Max 里怎么用

1. `buffer~ wt` → 发送 `read wavetable.wav`
2. `phasor~` 接到 `wave~ wt` 的第 1 个 inlet
3. `wave~` 的第 2、3 个 inlet 是读取范围的起点和终点,**单位是毫秒**

所以需要把 "第 k 个 frame" 换算成毫秒:

- 起点 = `k × 2048 / sr × 1000`
- 终点 = `(k + 1) × 2048 / sr × 1000`

下面打印出每个 frame 的起止毫秒数,可以直接抄进 Max。要在两个 frame 之间 crossfade,就用两个 `wave~` 读相邻的两段,再用第 4 集的 `(1 - mix) * a + mix * b`(Max 里是 `xfade~` 或一对 `*~`)。
''', r'''
### How to use it in Max

1. `buffer~ wt` → send it `read wavetable.wav`
2. patch `phasor~` into inlet 1 of `wave~ wt`
3. inlets 2 and 3 of `wave~` are the start and end of the range to read, **in milliseconds**

So "frame k" has to be converted to milliseconds:

- start = `k × 2048 / sr × 1000`
- end = `(k + 1) × 2048 / sr × 1000`

The cell below prints the start and end of every frame in milliseconds, ready to copy into Max. To crossfade between two frames, use two `wave~` objects reading neighbouring ranges and Episode 4's `(1 - mix) * a + mix * b` (in Max: `xfade~`, or a pair of `*~`).
'''),
        C(r'''
for k in range(frames.shape[0]):
    start_ms = k * N / sr * 1000
    end_ms = (k + 1) * N / sr * 1000
    print(f"frame {k:2d}:  {start_ms:8.3f} ms  to  {end_ms:8.3f} ms")
'''),
        M(r'''
## 4. 把 preset 送回 Max

preset 是 `dict`。第 9 集用过 JSON 来存参数。Max 的 `dict` object 可以直接读 JSON 文件。
''', r'''
## 4. Sending presets back to Max

A preset is a `dict`. Episode 9 used JSON to store parameters. Max's `dict` object reads JSON files directly.
'''),
        C(r'''
with open("export/presets.json", "w") as f:
    json.dump(presets, f, indent=2)

print(json.dumps(presets["wow"], indent=2))    # [[文件里 "wow" 那一段长这样||this is what the "wow" section of the file looks like]]
'''),
        M(r'''
### 在 Max 里怎么用

1. `dict presets` → 发送 `read presets.json`
2. 发送 `get wow::cutoff` → `dict` 输出这个值(150)。`::` 是 "进到里面一层" 的意思
3. 用 `route` 把取出的值分发到 RNBO patch 里同名的 `param` 上

只要 Max 那边的 synth 用 **同样的参数名和同样的 signal flow**(第 8 集那张图),同一个 preset 在两边就应该是同一个声音。

实际做的时候,两边的 filter 和 envelope 曲线不会完全一样(`lores~` 和我们的 `lowpass()` 不是同一个算法),所以听起来会 **很接近但不完全相同**。如果需要完全一致,就要在 gen~ 里把第 6 集的那几行算式原样写一遍。
''', r'''
### How to use it in Max

1. `dict presets` → send it `read presets.json`
2. send `get wow::cutoff` → the `dict` outputs that value (150). `::` means "one level down"
3. use `route` to send the retrieved values to the `param` objects of the same name in your RNBO patch

As long as the synth on the Max side uses **the same parameter names and the same signal flow** (the diagram from Episode 8), one preset should give the same sound in both places.

In practice the filter and envelope curves on the two sides will not be identical (`lores~` and our `lowpass()` are different algorithms), so the result will be **very close but not the same**. For an exact match you would write the arithmetic of Episode 6 out in gen~, line for line.
'''),
        M(r'''
## 5. 全系列对照表

| 集 | Max / RNBO | Python |
|---|---|---|
| 1 | `cycle~`、`dac~`、`scope~`、signal | `np.sin`、`play`、`scope`、array |
| 2 | `phasor~`、`<~`、`abs~` | `(freq * t) % 1`、`np.where`、`np.abs` |
| 3 | `buffer~`、`index~`、`wave~` | `table[idx]`、线性插值 |
| 4 | WT POS、`xfade~`、`line~` | 二维 `frames`、`np.linspace` |
| 5 | `adsr~`、`function`、`*~` | `np.interp`、`osc * env` |
| 6 | `onepole~`、`lores~`、gen~ `history`、`noise~` | `for` 循环 + 状态变量 |
| 7 | signal 接参数 inlet、LFO、`phasor~` 的 signal 输入 | 参数传 array、`np.cumsum` |
| 8 | RNBO patch、`param`、`dict`、`mtof` | 函数、`dict` |
| 9 | `random`、`sfrecord~`(很别扭) | `rng` + 循环 + 存文件 |
| 10 | `spectroscope~`、`buffer~ read`、`dict read` | `np.fft`、`specgram`、`wavfile`、`json` |

## 三句话带走

1. **Python 里声音是一个 array。** 没有 feedback 的东西整串一起算;有 feedback 的东西(filter、phase 累加)要 "记住上一次"。
2. **参数和 signal 是同一种东西。** 传一个数是静态的,传一个 array 就是 modulation。
3. **Python 负责离线和批量,Max 负责实时和交互。** 用同一套参数名,它们可以互相传东西。

## 练习

**1.** 画出第 2 集的朴素 saw(`2 * phase - 1`)在 2500 Hz 时的 spectrum,横轴到 22050 Hz。找出那些不在 2500 的整数倍上的线 — 那就是 aliasing。

<details><summary>答案</summary>

```python
ph = phasor(2500, n)
spec_plot({"naive saw 2500 Hz": 2 * ph - 1}, max_freq=22050)
```
2500、5000、7500 …… 是真正的 harmonic。夹在它们之间的那些矮线是折回来的。
</details>

**2.** 画第 7 集的 vibrato(220 Hz,每秒 5 次,上下半个半音)的 spectrogram,纵轴只看 0–1500 Hz。**先猜:** 线是什么形状?

<details><summary>答案</summary>

```python
vib = 220 * 2 ** (0.5 / 12 * np.sin(2 * np.pi * 5 * t))
spectrogram(osc_wavetable(frames, phasor(vib, n), 0.8), "vibrato", max_freq=1500)
```
每条 harmonic 都是一条波浪线;越高的 harmonic 波浪幅度越大(因为它们的频率是基音的整数倍,抖动也被放大同样的倍数)。
</details>

**3.** 把第 4 集练习里的 "sine 到 square" frames(或者任何一套你自己的 frames)导出成 `export/my_wavetable.wav`。

<details><summary>答案</summary>

```python
sq = []
for f in range(16):
    amps = []
    for k in range(1, 2 * f + 2):
        amps.append(1 / k if k % 2 == 1 else 0)
    sq.append(make_table(amps))
sq = np.array(sq)
wavfile.write("export/my_wavetable.wav", sr, (0.9 * sq.reshape(-1)).astype(np.float32))
```
</details>

## 接下来可以做什么

- 把 envelope 换成 exponential 曲线(第 5 集第 7 节的思路)
- 加第二个 oscillator、detune、noise
- 用 `sounddevice` 库在 Python 里做实时输出
- 在 gen~ / RNBO 里按第 8 集的 signal flow 重建这个 synth,读入这一集导出的两个文件
- 用第 9 集的数据集训练一个模型:听声音 → 预测参数
''', r'''
## 5. The whole series at a glance

| Ep. | Max / RNBO | Python |
|---|---|---|
| 1 | `cycle~`, `dac~`, `scope~`, signals | `np.sin`, `play`, `scope`, arrays |
| 2 | `phasor~`, `<~`, `abs~` | `(freq * t) % 1`, `np.where`, `np.abs` |
| 3 | `buffer~`, `index~`, `wave~` | `table[idx]`, linear interpolation |
| 4 | WT POS, `xfade~`, `line~` | 2-D `frames`, `np.linspace` |
| 5 | `adsr~`, `function`, `*~` | `np.interp`, `osc * env` |
| 6 | `onepole~`, `lores~`, gen~ `history`, `noise~` | a `for` loop + state variables |
| 7 | signals into parameter inlets, LFO, signal input of `phasor~` | arrays as parameters, `np.cumsum` |
| 8 | RNBO patch, `param`, `dict`, `mtof` | a function, a `dict` |
| 9 | `random`, `sfrecord~` (awkward) | `rng` + a loop + saving files |
| 10 | `spectroscope~`, `buffer~ read`, `dict read` | `np.fft`, `specgram`, `wavfile`, `json` |

## Three things to take away

1. **In Python, sound is an array.** Anything without feedback is computed all at once; anything with feedback (filters, phase accumulation) has to "remember the last time".
2. **Parameters and signals are the same kind of thing.** Pass one number for static, pass an array for modulation.
3. **Python handles offline and bulk work; Max handles real time and interaction.** With shared parameter names they can hand things to each other.

## Exercises

**1.** Plot the spectrum of Episode 2's naive saw (`2 * phase - 1`) at 2500 Hz with the horizontal axis up to 22050 Hz. Find the lines that are not at whole multiples of 2500 — that is aliasing.

<details><summary>Answer</summary>

```python
ph = phasor(2500, n)
spec_plot({"naive saw 2500 Hz": 2 * ph - 1}, max_freq=22050)
```
2500, 5000, 7500 ... are the real harmonics. The shorter lines between them are the folded-back ones.
</details>

**2.** Plot the spectrogram of Episode 7's vibrato (220 Hz, 5 per second, half a semitone each way), showing only 0–1500 Hz. **Guess first:** what shape are the lines?

<details><summary>Answer</summary>

```python
vib = 220 * 2 ** (0.5 / 12 * np.sin(2 * np.pi * 5 * t))
spectrogram(osc_wavetable(frames, phasor(vib, n), 0.8), "vibrato", max_freq=1500)
```
Every harmonic is a wavy line; higher harmonics wave more widely (their frequencies are whole multiples of the fundamental, so the wobble is multiplied by the same factor).
</details>

**3.** Export the "sine to square" frames from Episode 4's exercise (or any frames of your own) as `export/my_wavetable.wav`.

<details><summary>Answer</summary>

```python
sq = []
for f in range(16):
    amps = []
    for k in range(1, 2 * f + 2):
        amps.append(1 / k if k % 2 == 1 else 0)
    sq.append(make_table(amps))
sq = np.array(sq)
wavfile.write("export/my_wavetable.wav", sr, (0.9 * sq.reshape(-1)).astype(np.float32))
```
</details>

## Where to go next

- swap the envelopes for exponential curves (the idea from Episode 5, section 7)
- add a second oscillator, detune, noise
- use the `sounddevice` library for real-time output from Python
- rebuild this synth in gen~ / RNBO following Episode 8's signal flow and load the two files exported here
- train a model on Episode 9's dataset: listen to a sound → predict its parameters
'''),
    ])
