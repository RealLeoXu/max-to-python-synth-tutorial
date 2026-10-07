from common import *

EP = dict(
    zh_file="09_批量渲染_Max里很难做的事",
    en_file="09_batch_rendering_what_is_hard_in_max",
    cells=[
        M(r'''
# 第 9 集 — 批量渲染:Max 里很难做的事

⏱ 约 25 分钟

**这一集控制的音乐元素:没有新的。** 这一集的主题是 **数量**。

**Max 里的对应:** 想象你要在 Max 里随机拧 14 个旋钮、录 1 秒、存成文件、记下旋钮的值,然后重复 10000 次。可以做,但很别扭。在 Python 里是十几行。

**你会听到:** 20 个由电脑随机 "拧" 出来的声音。有的好听,有的奇怪,有的几乎没声音 — 这是正常的。

**学完你能做到:**
- 用随机数发生器,并让结果可以重现
- 解释为什么 cutoff 和时间类参数要 "按倍数" 随机
- 批量渲染、存 wav、存参数
- 把存下来的东西读回来,验证 "声音 ↔ 参数" 是配对的
- 把一批声音整理成两张表

**为什么这很重要:** 每个声音都附带一份 "它是用哪些参数做出来的" 记录。这种 **声音 ↔ 参数** 的配对,正是训练 machine learning 模型(比如 "听一个声音,猜出 synth 参数")需要的数据。
''', r'''
# Episode 9 — Batch Rendering: What Is Hard in Max

⏱ About 25 minutes

**Musical element this episode controls: nothing new.** This episode is about **quantity**.

**The Max equivalent:** imagine randomly setting 14 knobs in Max, recording 1 second, saving a file, writing down the knob values, and doing that 10000 times. Possible, but awkward. In Python it is a dozen lines.

**What you will hear:** 20 sounds "dialled in" at random by the computer. Some are nice, some are odd, some are nearly silent — that is normal.

**By the end you can:**
- use a random number generator and make results reproducible
- explain why cutoff and time parameters are randomised "by ratio"
- render in bulk, save wavs, save parameters
- load everything back and verify that "sound ↔ parameters" really are pairs
- arrange a batch of sounds into two tables

**Why it matters:** every sound comes with a record of the parameters that produced it. Such **sound ↔ parameter** pairs are exactly the data needed to train a machine learning model (for example "listen to a sound, guess the synth parameters").
'''),
        M(TOOLBOX_ZH, TOOLBOX_EN),
        C(J(BASE, r'''
import os
import json
import time
from scipy.io import wavfile
''', TABLE, FRAMES, ADSR, LOWPASS, PHASOR, SYNTH, r'''
frames = make_frames()
''')),
        M(r'''
## 1. 随机数

`rng` 是一个随机数发生器(random number generator)。Max 里对应 `random` 和 `noise~`。

- `rng.uniform(a, b)`:在 a 和 b 之间随机取一个数,每个位置的机会均等
- `rng.integers(a, b)`:随机取一个整数,从 a 到 b - 1

每运行一次,得到的数都不一样:
''', r'''
## 1. Random numbers

`rng` is a random number generator. The Max counterparts are `random` and `noise~`.

- `rng.uniform(a, b)`: a random number between a and b, every position equally likely
- `rng.integers(a, b)`: a random whole number from a to b - 1

Every run gives different numbers:
'''),
        C(r'''
rng = np.random.default_rng()

print(rng.uniform(0, 1))
print(rng.uniform(0, 1))
print(rng.integers(28, 61))
'''),
        M(r'''
### Seed:可以重现的随机

做实验时,"每次都不一样" 是个麻烦:你没法回头再生成同一批声音。

给发生器一个 **seed**(任意一个整数),它就会每次产生 **同一串** 随机数。换一个 seed,就换一串。

下面两个发生器 seed 都是 0,所以输出完全相同。第三个 seed 是 1,输出不同。
''', r'''
### The seed: randomness you can repeat

In an experiment "different every time" is a nuisance: you cannot go back and regenerate the same batch of sounds.

Give the generator a **seed** (any whole number) and it produces **the same** random sequence every time. Another seed gives another sequence.

The first two generators below both use seed 0, so their output is identical. The third uses seed 1 and differs.
'''),
        C(r'''
first = np.random.default_rng(seed=0)
second = np.random.default_rng(seed=0)
other = np.random.default_rng(seed=1)

print("seed 0:", np.round(first.uniform(0, 1, 4), 3))
print("seed 0:", np.round(second.uniform(0, 1, 4), 3))
print("seed 1:", np.round(other.uniform(0, 1, 4), 3))
'''),
        M(r'''
## 2. 怎么随机一个 cutoff

cutoff 的范围是 80 到 8000 Hz。直接 `rng.uniform(80, 8000)` 行不行?

第 7 集的结论:耳朵按 **倍数** 听频率。80 到 8000 大约是 6.6 个八度。但如果在 Hz 上均匀取:

- 4000–8000 Hz(最高的 **一个** 八度)占了整个范围的一半
- 80–160 Hz(最低的一个八度)只占 1%

结果就是:随机出来的声音大多数都很亮,几乎没有闷的。

解决:在 **log 上** 均匀取,再换算回来。这叫 log-uniform,和 `geomspace` 是同一个想法。

- `np.log(lo)`、`np.log(hi)`:把两端换成 log
- 在 log 值之间均匀随机
- `np.exp(...)`:换回原来的单位

下面各取 2000 个,画成直方图(每个柱子 = 落在那个区间里的个数)。横轴是按八度画的。

**应该看到:** 左图(普通 uniform)几乎全挤在右边;右图(log-uniform)各个八度大致一样多。
''', r'''
## 2. How to randomise a cutoff

The cutoff ranges from 80 to 8000 Hz. Would a plain `rng.uniform(80, 8000)` do?

Episode 7's conclusion: the ear hears frequency by **ratio**. 80 to 8000 is about 6.6 octaves. But drawing evenly in Hz:

- 4000–8000 Hz (the top **one** octave) takes up half the range
- 80–160 Hz (the bottom octave) takes up just 1%

The result: most random sounds come out bright and hardly any dull.

The fix: draw evenly **on a log scale** and convert back. This is log-uniform, the same idea as `geomspace`.

- `np.log(lo)`, `np.log(hi)`: put both ends on a log scale
- draw evenly between the log values
- `np.exp(...)`: convert back to the original unit

Below, 2000 draws of each as a histogram (each bar = how many fell into that interval). The horizontal axis is laid out by octaves.

**You should see:** the left plot (plain uniform) crowded almost entirely to the right; the right plot (log-uniform) roughly equal in every octave.
'''),
        C(r'''
rng = np.random.default_rng(seed=0)

def log_uniform(lo, hi):
    # [[在 log 值之间均匀取,再用 exp 换回来||draw evenly between the log values, then convert back with exp]]
    return float(np.exp(rng.uniform(np.log(lo), np.log(hi))))

plain = []
logged = []
for i in range(2000):
    plain.append(rng.uniform(80, 8000))
    logged.append(log_uniform(80, 8000))

bins = np.geomspace(80, 8000, 30)              # [[按倍数划分的 30 个区间||30 intervals spaced by ratio]]
fig, axes = plt.subplots(1, 2, figsize=(11, 3), sharey=True)
axes[0].hist(plain, bins=bins)
axes[0].set_title("uniform(80, 8000)")
axes[1].hist(logged, bins=bins)
axes[1].set_title("log_uniform(80, 8000)")
for ax in axes:
    ax.set_xscale("log")
    ax.set_xlabel("cutoff (Hz)")
plt.show()
'''),
        M(r'''
**规则:**

- 频率、时间类参数(`cutoff`、attack、decay、release)→ `log_uniform`
- 本来就是 0 到 1 的参数(`wt_pos`、`res`、sustain、amount)→ 普通 `uniform`

## 3. 随机一整组参数

14 个参数,每个按上面的规则取。`float(...)` 和 `int(...)` 是把 numpy 的数变成普通 Python 数字,后面存文件时需要。

为了每次运行这个 cell 都得到同样的结果,这里重新建了一次 `rng`。
''', r'''
**The rule:**

- frequency and time parameters (`cutoff`, attack, decay, release) → `log_uniform`
- parameters that already run 0 to 1 (`wt_pos`, `res`, sustain, amounts) → plain `uniform`

## 3. Randomising a whole set of parameters

14 parameters, each drawn by the rule above. `float(...)` and `int(...)` turn numpy numbers into plain Python numbers, which is needed for saving later.

The `rng` is created afresh here so that this cell gives the same result on every run.
'''),
        C(r'''
rng = np.random.default_rng(seed=0)

def random_params():
    return dict(
        note=int(rng.integers(28, 61)),            # [[MIDI 28..60||MIDI 28..60]]
        wt_pos=float(rng.uniform(0, 1)),
        wt_env=float(rng.uniform(0, 1)),
        cutoff=log_uniform(80, 8000),              # [[频率 → 按倍数||a frequency → by ratio]]
        res=float(rng.uniform(0, 0.9)),
        cut_env=float(rng.uniform(0, 5)),
        amp_a=log_uniform(0.002, 0.5),             # [[时间 → 按倍数||a time → by ratio]]
        amp_d=log_uniform(0.02, 0.5),
        amp_s=float(rng.uniform(0, 1)),
        amp_r=log_uniform(0.02, 0.4),
        mod_a=log_uniform(0.002, 0.5),
        mod_d=log_uniform(0.02, 0.5),
        mod_s=float(rng.uniform(0, 1)),
        mod_r=log_uniform(0.02, 0.4),
    )

p = random_params()
for name in p:
    print(f"{name:8} = {p[name]:.3f}")
'''),
        M(r'''
`f"{name:8} = {p[name]:.3f}"` 是 **f-string**:引号前面加 `f`,花括号里的东西会被换成它的值。`:8` 是 "占 8 格宽"(为了对齐),`:.3f` 是 "保留 3 位小数"。

听一下这一组。时长 1 秒,按住 0.6 秒。

**应该听到:** 一个随机的声音 — 不一定好听。
''', r'''
`f"{name:8} = {p[name]:.3f}"` is an **f-string**: put `f` before the quotes and whatever sits in curly braces is replaced by its value. `:8` means "8 characters wide" (for alignment), `:.3f` means "3 decimals".

Listen to this set. One second long, held for 0.6 seconds.

**You should hear:** a random sound — not necessarily a nice one.
'''),
        C(r'''
play(synth(p, dur=1.0, gate=0.6))
'''),
        M(r'''
## 4. 批量渲染

每一轮:

1. 随机一组参数
2. `synth()` 渲染 1 秒
3. 存成 `.wav`
4. 把参数和声音各记进一个 list

最后把所有参数存成一个 `params.json`。

- `os.makedirs("dataset", exist_ok=True)`:在 notebook 旁边建一个 `dataset` 文件夹(已经有就跳过)
- `f"{i:03d}.wav"`:把数字 `i` 变成三位数的文件名 — `000.wav`、`001.wav` ……
- `os.path.join(a, b)`:把文件夹名和文件名拼成路径
- **JSON** 是存 `dict` 和 list 的标准文本格式;`json.dump` 写,`json.load` 读
''', r'''
## 4. Rendering in bulk

Each round:

1. pick a random set of parameters
2. render 1 second with `synth()`
3. save it as a `.wav`
4. append the parameters and the sound to a list each

At the end all parameters go into one `params.json`.

- `os.makedirs("dataset", exist_ok=True)`: create a `dataset` folder next to the notebook (skipped if it exists)
- `f"{i:03d}.wav"`: turn the number `i` into a three-digit file name — `000.wav`, `001.wav` ...
- `os.path.join(a, b)`: join a folder name and a file name into a path
- **JSON** is the standard text format for a `dict` or list; `json.dump` writes, `json.load` reads
'''),
        C(r'''
rng = np.random.default_rng(seed=0)            # [[seed 固定:每次运行得到同一批 20 个声音||fixed seed: the same 20 sounds on every run]]

n_sounds = 20
out_dir = "dataset"
os.makedirs(out_dir, exist_ok=True)

all_params = []
sounds = []
start = time.time()

for i in range(n_sounds):
    p = random_params()                                        # [[1. 随机拧旋钮||1. turn the knobs at random]]
    x = synth(p, dur=1.0, gate=0.6)                            # [[2. 渲染||2. render]]
    audio = np.clip(0.3 * x, -1, 1).astype(np.float32)         # [[降音量、防爆、转成 wav 用的格式||lower the level, guard against clipping, convert to the wav format]]
    wavfile.write(os.path.join(out_dir, f"{i:03d}.wav"), sr, audio)     # [[3. 存盘||3. save]]
    all_params.append(p)                                       # [[4. 记下参数||4. record the parameters]]
    sounds.append(x)

with open(os.path.join(out_dir, "params.json"), "w") as f:
    json.dump(all_params, f, indent=2)

elapsed = time.time() - start
print(f"rendered {n_sounds} sounds in {elapsed:.1f} s")
print(f"at this speed, 10000 sounds would take about {10000 * elapsed / n_sounds / 60:.0f} minutes")
'''),
        M(r'''
`with open(...) as f:` 是 "打开文件 → 做下面缩进的事 → 自动关上"。

去 notebook 所在的文件夹看一下:`dataset/` 里应该有 `000.wav` 到 `019.wav` 和一个 `params.json`。用文本编辑器打开 `params.json` 就能看到每个声音的参数。

## 5. 听和看

### 前 6 个

**应该听到:** 6 个彼此很不一样的短音 — 音高、明暗、长短都不同。每个上面印着它的几个关键参数,试着把听到的和数字对上:`note` 大的音高,`cutoff` 大的亮,`amp_a` 大的淡入慢。
''', r'''
`with open(...) as f:` means "open the file → do the indented things → close it automatically".

Look in the notebook's folder: `dataset/` should contain `000.wav` to `019.wav` and a `params.json`. Open `params.json` in a text editor to see each sound's parameters.

## 5. Listening and looking

### The first 6

**You should hear:** 6 short sounds that differ a lot — in pitch, brightness and length. A few key parameters are printed above each; try matching what you hear to the numbers: higher `note` is higher in pitch, higher `cutoff` is brighter, higher `amp_a` fades in more slowly.
'''),
        C(r'''
for i in range(6):
    p = all_params[i]
    print(f"{i:03d}  note={p['note']}  cutoff={p['cutoff']:.0f} Hz  res={p['res']:.2f}  "
          f"cut_env={p['cut_env']:.1f} oct  amp_a={p['amp_a']:.3f} s")
    display(play(sounds[i]))
'''),
        M(r'''
### 20 个一眼扫过

每一格是一个声音的 spectrogram(横轴时间,纵轴频率,越亮越响)。

**应该看到:** 20 张很不一样的图 — 有的只有底下几条线(闷),有的铺满(亮),有的只有开头一小块(短),有的有明显向下收的形状(filter envelope)。
''', r'''
### All 20 at a glance

Each panel is the spectrogram of one sound (time across, frequency up, brighter = louder).

**You should see:** 20 quite different pictures — some with only a few lines at the bottom (dull), some filled (bright), some with just a patch at the start (short), some with a clear downward-closing shape (filter envelope).
'''),
        C(r'''
fig, axes = plt.subplots(4, 5, figsize=(12, 7), sharex=True, sharey=True)
for i, ax in enumerate(axes.flat):
    with np.errstate(divide="ignore"):         # [[完全静音的地方算 dB 会警告,这里忽略它||fully silent parts trigger a warning when converted to dB; ignore it here]]
        ax.specgram(sounds[i] + 1e-9, NFFT=1024, Fs=sr, noverlap=768, cmap="magma", vmin=-120)
    ax.set_ylim(0, 6000)
    ax.set_title(f"{i:03d}", fontsize=8)
fig.supxlabel("time (s)")
fig.supylabel("frequency (Hz)")
plt.tight_layout()
plt.show()
'''),
        M(r'''
## 6. 读回来,验证配对

"声音 ↔ 参数是配对的" 是什么意思?意思是:**拿存下来的参数重新渲染,应该得到和存下来的 wav 一模一样的声音。**

验证一下第 3 号:

1. 从 `params.json` 读出第 3 组参数
2. 用它重新 `synth()`
3. 从 `003.wav` 读出声音
4. 比较两者

`np.allclose(a, b, atol=1e-6)`:两个 array 是否 "几乎相等"(每个数相差不超过百万分之一)。
''', r'''
## 6. Loading back and verifying the pairs

What does "sound ↔ parameters are pairs" mean? It means: **re-rendering from the saved parameters should give exactly the sound in the saved wav.**

Check number 3:

1. read parameter set 3 from `params.json`
2. run `synth()` on it again
3. read the sound from `003.wav`
4. compare the two

`np.allclose(a, b, atol=1e-6)`: are two arrays "almost equal" (every number within one millionth)?
'''),
        C(r'''
with open(os.path.join(out_dir, "params.json")) as f:
    loaded_params = json.load(f)

p3 = loaded_params[3]
rerendered = np.clip(0.3 * synth(p3, dur=1.0, gate=0.6), -1, 1)       # [[和存盘时一样的处理||the same processing as when saving]]

file_sr, from_file = wavfile.read(os.path.join(out_dir, "003.wav"))

print("sample rate in file :", file_sr)
print("same length         :", len(rerendered) == len(from_file))
print("same sound          :", np.allclose(rerendered, from_file, atol=1e-6))
'''),
        M(r'''
`same sound: True` 说明:参数完整地描述了这个声音。这就是这个数据集的价值所在。

## 7. 质量检查

随机出来的声音响度差别很大,有些会非常小声(比如 cutoff 很低、sustain 又很低)。做数据集时通常要把它们找出来。

**RMS** 是 "平均响度" 的一种算法:每个 sample 平方 → 取平均 → 开根号。

**应该看到:** 20 根柱子,高矮不一。红线以下的算 "太小声"。
''', r'''
`same sound: True` shows that the parameters describe the sound completely. That is what makes this dataset valuable.

## 7. Quality check

Random sounds vary a lot in loudness and some come out very quiet (a very low cutoff with a low sustain, for instance). When building a dataset you normally want to find those.

**RMS** is one way to compute "average loudness": square each sample → average → square root.

**You should see:** 20 bars of varying height. Anything under the red line counts as "too quiet".
'''),
        C(r'''
rms = []
for x in sounds:
    rms.append(np.sqrt(np.mean(x ** 2)))       # [[平方 → 平均 → 开根号||square → mean → square root]]
rms = np.array(rms)

threshold = 0.1

plt.figure(figsize=(9, 3))
plt.bar(np.arange(n_sounds), rms)
plt.axhline(threshold, color="red")
plt.xlabel("sound number")
plt.ylabel("RMS")
plt.xticks(np.arange(n_sounds))
plt.show()

quiet = np.where(rms < threshold)[0]           # [[RMS 低于阈值的那些编号||the numbers of those whose RMS is below the threshold]]
print("too quiet:", quiet)
'''),
        M(r'''
听一下列出来的第一个,确认它确实比其他的小声,并看看它的参数,想想为什么。
''', r'''
Listen to the first one listed to confirm it really is quieter than the rest, then look at its parameters and work out why.
'''),
        C(r'''
if len(quiet) > 0:
    i = int(quiet[0])
    print("sound", i, " note =", all_params[i]["note"], " cutoff =", round(all_params[i]["cutoff"]),
          "Hz  cut_env =", round(all_params[i]["cut_env"], 1), " amp_s =", round(all_params[i]["amp_s"], 2))
    display(play(sounds[i]))
else:
    print("no sound is below the threshold")
'''),
        M(r'''
## 8. 整理成两张表

machine learning 模型不认 `dict` 和文件夹,它认 **表**(二维 array):每一行是一个例子。

- **X**:声音。20 行 × 44100 列(每行是一个 1 秒的声音)
- **Y**:参数。20 行 × 14 列(每行是那个声音的 14 个参数)

**第 i 行的 X 和第 i 行的 Y 是一对。** "听声音猜参数" 的模型,就是学习从 X 的一行算出 Y 的同一行。
''', r'''
## 8. Arranging everything into two tables

A machine learning model does not understand `dict`s and folders; it understands **tables** (2-D arrays) where each row is one example.

- **X**: the sounds. 20 rows × 44100 columns (each row is a 1-second sound)
- **Y**: the parameters. 20 rows × 14 columns (each row holds that sound's 14 parameters)

**Row i of X and row i of Y belong together.** A "listen and guess the parameters" model learns to compute a row of Y from the same row of X.
'''),
        C(r'''
names = list(all_params[0].keys())             # [[14 个参数名,顺序固定||the 14 parameter names, in a fixed order]]

rows = []
for p in all_params:
    row = []
    for name in names:
        row.append(p[name])                    # [[按同样的顺序取出 14 个值||take the 14 values in the same order]]
    rows.append(row)

X = np.array(sounds)
Y = np.array(rows)

print("names:", names)
print("X shape:", X.shape, "  (sounds x samples)")
print("Y shape:", Y.shape, "     (sounds x parameters)")
print()
print("row 3 of Y:", np.round(Y[3], 3))
'''),
        M(r'''
到这里,一个(很小的)数据集就完整了。把 `n_sounds` 改成 10000,同样的代码就能产出一个真正可以用来训练的数据集。

## 常见错误

| 现象 | 原因 |
|---|---|
| 每次运行得到的声音都不一样 | 建 `rng` 时没有给 seed,或者没有重新运行建 `rng` 的那一行 |
| `Object of type float32 is not JSON serializable` | 参数里混进了 numpy 的数。用 `float(...)` / `int(...)` 包一下 |
| 读回来 `same sound: False` | 重新渲染时的 `dur`、`gate` 或音量处理和存盘时不一样 |
| wav 文件在别的软件里爆音 | 存盘前没有 `np.clip` 或没有降音量 |

## 练习

**1.** 把 seed 改成 1,重新运行第 4 节和第 5 节。**应该听到:** 完全不同的 20 个声音。再改回 0,应该回到原来那一批。

**2.** 做一个 "只有 bass" 的数据集:`note` 限制在 28–40,`cutoff` 限制在 80–1000。提示:复制 `random_params`,改两行。

<details><summary>答案</summary>

```python
def random_bass():
    p = random_params()
    p["note"] = int(rng.integers(28, 41))
    p["cutoff"] = log_uniform(80, 1000)
    return p

rng = np.random.default_rng(seed=5)
for i in range(4):
    display(play(synth(random_bass(), dur=1.0, gate=0.6)))
```
</details>

**3.** 在 `Y` 里找出 cutoff 最高的那个声音并播放。提示:`names.index("cutoff")` 给出 cutoff 是第几列;`np.argmax(一列)` 给出最大值在第几行。

<details><summary>答案</summary>

```python
col = names.index("cutoff")
i = int(np.argmax(Y[:, col]))          # Y[:, col] = 所有行的第 col 列
print("sound", i, "cutoff", round(Y[i, col]))
play(sounds[i])
```
</details>

## 小结

| | Max / RNBO | Python |
|---|---|---|
| 实时演奏、拧旋钮 | 很擅长 | 不擅长 |
| 自动生成一万个声音并记录参数 | 别扭 | 一个循环 |

| Max | Python |
|---|---|
| `random` | `rng.uniform(a, b)`、`rng.integers(a, b)` |
| `seed` message | `np.random.default_rng(seed=0)` |
| `sfrecord~` | `wavfile.write(...)` |
| `dict` 的 `write` | `json.dump(...)` |

两者不是替代关系,而是分工:

- **Python**:离线、批量、可重现 — 做数据、做分析、做实验
- **Max / RNBO**:实时、可交互 — 做乐器、做给人用的东西

**下一集(最后一集):** 用 Python 看声音,然后把做好的 wavetable 和 preset 送回 Max。
''', r'''
At this point a (very small) dataset is complete. Change `n_sounds` to 10000 and the same code produces a dataset you could really train on.

## Common mistakes

| Symptom | Cause |
|---|---|
| Different sounds on every run | `rng` was created without a seed, or the line creating it was not re-run |
| `Object of type float32 is not JSON serializable` | A numpy number slipped into the parameters. Wrap it in `float(...)` / `int(...)` |
| `same sound: False` after loading | `dur`, `gate` or the level processing differ between re-rendering and saving |
| The wav files distort in other software | No `np.clip` or level reduction before saving |

## Exercises

**1.** Change the seed to 1 and re-run sections 4 and 5. **You should hear:** 20 completely different sounds. Change it back to 0 and the original batch returns.

**2.** Build a "bass only" dataset: restrict `note` to 28–40 and `cutoff` to 80–1000. Hint: copy `random_params` and change two lines.

<details><summary>Answer</summary>

```python
def random_bass():
    p = random_params()
    p["note"] = int(rng.integers(28, 41))
    p["cutoff"] = log_uniform(80, 1000)
    return p

rng = np.random.default_rng(seed=5)
for i in range(4):
    display(play(synth(random_bass(), dur=1.0, gate=0.6)))
```
</details>

**3.** Find the sound with the highest cutoff in `Y` and play it. Hint: `names.index("cutoff")` gives the column of cutoff; `np.argmax(column)` gives the row of the largest value.

<details><summary>Answer</summary>

```python
col = names.index("cutoff")
i = int(np.argmax(Y[:, col]))          # Y[:, col] = column col of every row
print("sound", i, "cutoff", round(Y[i, col]))
play(sounds[i])
```
</details>

## Recap

| | Max / RNBO | Python |
|---|---|---|
| playing live, turning knobs | excellent | poor |
| auto-generating ten thousand sounds with their parameters | awkward | one loop |

| Max | Python |
|---|---|
| `random` | `rng.uniform(a, b)`, `rng.integers(a, b)` |
| the `seed` message | `np.random.default_rng(seed=0)` |
| `sfrecord~` | `wavfile.write(...)` |
| `write` on `dict` | `json.dump(...)` |

The two do not replace each other; they split the work:

- **Python**: offline, in bulk, reproducible — building data, analysis, experiments
- **Max / RNBO**: real time, interactive — building instruments and things people use

**Next episode (the last):** looking at sound in Python, then sending the finished wavetable and presets back to Max.
'''),
    ])
