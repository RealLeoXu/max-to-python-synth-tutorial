from common import *

EP = dict(
    zh_file="04_wavetable_position_在波形之间morph",
    en_file="04_wavetable_position_morphing",
    cells=[
        M(r'''
# 第 4 集 — Wavetable position:在波形之间 morph

⏱ 约 25 分钟

**这一集控制的音乐元素:timbre 随时间的变化。**

**Max 里的对应 patch:** 一个存了很多个单周期的 `buffer~`,`wave~` 读其中相邻的两个再 crossfade。在 Serum 里就是 **WT POS** 旋钮。

**你会听到:**
1. `pos = 0`:暗(sine);`pos = 1`:亮(接近 saw)
2. `pos` 在 2 秒内从 0 滑到 1:声音从 "呜" 逐渐打开成 "哇"
3. `pos` 被一个 LFO 推着来回走:"呜哇呜哇"
4. 一套你自己做的、形状奇怪的 wavetable

**学完你能做到:**
- 读懂二维 array(一叠表)
- 解释 wavetable position 是怎么在两张表之间 crossfade 的
- 让 position 随时间变化
- 做一套自己的 frames
''', r'''
# Episode 4 — Wavetable Position: Morphing Between Waveforms

⏱ About 25 minutes

**Musical element this episode controls: how timbre changes over time.**

**The equivalent Max patch:** a `buffer~` holding many single cycles, with `wave~` reading two neighbours and crossfading. In Serum this is the **WT POS** knob.

**What you will hear:**
1. `pos = 0`: dark (sine); `pos = 1`: bright (close to a saw)
2. `pos` sliding from 0 to 1 over 2 seconds: the sound opens from "ooh" to "aah"
3. `pos` pushed back and forth by an LFO: "wah-wah"
4. a strangely shaped wavetable of your own

**By the end you can:**
- read a 2-D array (a stack of tables)
- explain how wavetable position crossfades between two tables
- make the position change over time
- build your own set of frames
'''),
        M(TOOLBOX_ZH, TOOLBOX_EN),
        C(J(BASE, TABLE, r'''
def osc_table(table, phase):
    N = len(table)
    pos = phase * N
    i0 = np.floor(pos).astype(int) % N
    i1 = (i0 + 1) % N
    frac = pos - np.floor(pos)
    return (1 - frac) * table[i0] + frac * table[i1]

freq = 110
dur = 2.0
t = np.arange(int(sr * dur)) / sr
phase = (freq * t) % 1
''')),
        M(r'''
## 1. 先从两张表开始:crossfade

一张暗的表(sine)和一张亮的表(32 个 harmonic)。

用一个 0 到 1 的数 `mix` 在它们之间混合:

`(1 - mix) * 暗 + mix * 亮`

- `mix = 0` → 全是暗的
- `mix = 1` → 全是亮的
- `mix = 0.5` → 各一半

这个式子你已经见过了:第 3 集的 interpolation 就是它(`(1 - frac) * 左 + frac * 右`)。在 Max 里是 `xfade~` 或 `mix~`。

**应该听到:** 三个同音高的音,一个比一个亮。
''', r'''
## 1. Start with two tables: a crossfade

One dark table (a sine) and one bright table (32 harmonics).

Blend them with a number `mix` between 0 and 1:

`(1 - mix) * dark + mix * bright`

- `mix = 0` → all dark
- `mix = 1` → all bright
- `mix = 0.5` → half of each

You have seen this formula before: Episode 3's interpolation is the same thing (`(1 - frac) * left + frac * right`). In Max it is `xfade~` or `mix~`.

**You should hear:** three tones at the same pitch, each brighter than the last.
'''),
        C(r'''
dark = make_table([1])
bright = make_table([1 / k for k in range(1, 33)])

for mix in [0.0, 0.5, 1.0]:
    blended = (1 - mix) * dark + mix * bright      # [[先把两张表混成一张新表,再去读它||blend the two tables into a new one, then read that]]
    scope(osc_table(blended, phase), f"mix = {mix}")
    display(play(osc_table(blended, phase)))
'''),
        M(r'''
两张表之间只有一种 "中间状态"。要做更丰富的变化,就要 **很多张表排成一排**,在相邻的两张之间 crossfade。

## 2. 二维 array

一张表是一排数(一维)。很多张表叠起来,就是 **几行几列** 的一个方阵(二维)。

先看一个小的:2 行 3 列。

- `m.shape` → (行数, 列数)
- `m[0]` → 第 0 行(一整行)
- `m[1, 2]` → 第 1 行的第 2 个
''', r'''
Between two tables there is only one kind of "in between". For richer movement you need **many tables in a row**, crossfading between neighbours.

## 2. 2-D arrays

One table is one row of numbers (1-D). Many tables stacked form a grid with **rows and columns** (2-D).

Look at a small one first: 2 rows, 3 columns.

- `m.shape` → (rows, columns)
- `m[0]` → row 0 (the whole row)
- `m[1, 2]` → item 2 of row 1
'''),
        C(r'''
m = np.array([[1, 2, 3],
              [10, 20, 30]])

print("shape   =", m.shape)
print("m[0]    =", m[0])
print("m[1]    =", m[1])
print("m[1, 2] =", m[1, 2])
'''),
        M(r'''
## 3. 一叠表:frames

做 16 张表,每一张叫一个 **frame**:

- frame 0:1 个 harmonic(sine)
- frame 15:32 个 harmonic(接近 saw)
- 中间的:harmonic 数量均匀递增

`frames` 的 shape 是 (16, 2048):16 行,每行是一张 2048 点的表。`frames[3]` 就是第 3 张表。
''', r'''
## 3. A stack of tables: frames

Make 16 tables, each called a **frame**:

- frame 0: 1 harmonic (a sine)
- frame 15: 32 harmonics (close to a saw)
- in between: the harmonic count rises evenly

`frames` has shape (16, 2048): 16 rows, each a 2048-point table. `frames[3]` is table number 3.
'''),
        C(r'''
def make_frames(F=16, max_harmonics=32, N=2048):
    frames = []                                    # [[一个空 list,用来装每一张表||an empty list to collect each table]]
    for f in range(F):                             # [[f = 0, 1, 2 ... 15||f = 0, 1, 2 ... 15]]
        # [[第 f 张表有几个 harmonic:从 1 个均匀增加到 max_harmonics 个||how many harmonics frame f gets: rising evenly from 1 to max_harmonics]]
        n_h = 1 + round(f * (max_harmonics - 1) / (F - 1))
        frames.append(make_table([1 / k for k in range(1, n_h + 1)], N))
    return np.array(frames)                        # [[叠成二维 array:F 行 × N 列||stack into a 2-D array: F rows × N columns]]

frames = make_frames()
print("shape:", frames.shape)
'''),
        M(r'''
把 16 张表从下到上排开看(每张往上错开一点):
''', r'''
All 16 frames, spread out from bottom to top (each shifted up a little):
'''),
        C(r'''
plt.figure(figsize=(9, 6))
for f in range(len(frames)):
    plt.plot(frames[f] + 1.5 * f, color="C0")      # [[+ 1.5 * f 只是为了画图时错开,不改变表本身||+ 1.5 * f only spreads them out in the plot; the tables are unchanged]]
plt.yticks(1.5 * np.arange(len(frames)), [f"frame {f}" for f in range(len(frames))])
plt.xlabel("table index")
plt.show()
'''),
        M(r'''
单独听几张。**应该听到:** frame 0 最暗,frame 15 最亮,中间的逐渐变亮。
''', r'''
Listen to a few on their own. **You should hear:** frame 0 darkest, frame 15 brightest, the ones between getting gradually brighter.
'''),
        C(r'''
for f in [0, 3, 8, 15]:
    print("frame", f)
    display(play(osc_table(frames[f], phase)))
'''),
        M(r'''
## 4. Position

`pos` 是 0 到 1 的一个数:0 = 第一张,1 = 最后一张。

中间的值怎么办?先把它换算成 "表的编号",可以带小数:

`fpos = pos * (F - 1)`

16 张表时,`F - 1 = 15`:

| `pos` | `fpos` | 意思 |
|---|---|---|
| 0 | 0 | 正好是 frame 0 |
| 1 | 15 | 正好是 frame 15 |
| 0.5 | 7.5 | frame 7 和 frame 8 各一半 |
| 0.3 | 4.5 | frame 4 和 frame 5 各一半 |
| 0.1 | 1.5 | frame 1 和 frame 2 各一半 |

然后和第 3 集读表时一模一样:取整得到 "下面那张",加 1 得到 "上面那张",小数部分决定混合比例。
''', r'''
## 4. Position

`pos` is a number from 0 to 1: 0 = the first frame, 1 = the last.

What about values in between? First convert to a "frame number" that may have decimals:

`fpos = pos * (F - 1)`

With 16 frames, `F - 1 = 15`:

| `pos` | `fpos` | meaning |
|---|---|---|
| 0 | 0 | exactly frame 0 |
| 1 | 15 | exactly frame 15 |
| 0.5 | 7.5 | half frame 7, half frame 8 |
| 0.3 | 4.5 | half frame 4, half frame 5 |
| 0.1 | 1.5 | half frame 1, half frame 2 |

Then exactly as when reading a table in Episode 3: round down for "the frame below", add 1 for "the frame above", and the fractional part sets the blend.
'''),
        C(r'''
F = len(frames)

for pos in [0.0, 0.1, 0.5, 0.98, 1.0]:
    fpos = pos * (F - 1)
    f0 = int(np.floor(fpos))               # [[下面那张||the frame below]]
    f1 = min(f0 + 1, F - 1)                # [[上面那张;min 防止超过最后一张||the frame above; min keeps it from passing the last one]]
    ffrac = fpos - f0                      # [[上面那张占多少||how much of the upper frame]]
    print(f"pos = {pos:<5} fpos = {fpos:<6.2f} frame {f0} x {1 - ffrac:.2f}  +  frame {f1} x {ffrac:.2f}")
'''),
        M(r'''
## 5. 完整的 wavetable oscillator

现在有 **两层 interpolation**:

1. 在一张表 **内部**,左右两个 sample 之间(第 3 集)
2. 在 **两张表之间**(这一集)

`frames[f0, i0]` 的意思是:第 `f0` 张表的第 `i0` 个位置。

函数分三段,每段前面有注释。
''', r'''
## 5. The complete wavetable oscillator

There are now **two layers of interpolation**:

1. **inside** one table, between two neighbouring samples (Episode 3)
2. **between two tables** (this episode)

`frames[f0, i0]` means: position `i0` of table number `f0`.

The function has three parts, each with a comment in front.
'''),
        C(r'''
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

    # [[--- 先在每张表内部插值,再在两张表之间插值 ---||--- interpolate inside each frame first, then between the two frames ---]]
    a = (1 - frac) * frames[f0, i0] + frac * frames[f0, i1]     # [[下面那张表读出来的值||the value read from the lower frame]]
    b = (1 - frac) * frames[f1, i0] + frac * frames[f1, i1]     # [[上面那张表读出来的值||the value read from the upper frame]]
    return (1 - ffrac) * a + ffrac * b                          # [[两者 crossfade||crossfade the two]]
'''),
        M(r'''
### 听:固定的 position

**应该听到:** 三个同音高的音,一个比一个亮。
''', r'''
### Listen: a fixed position

**You should hear:** three tones at the same pitch, each brighter than the last.
'''),
        C(r'''
for pos in [0.0, 0.3, 1.0]:
    print("pos =", pos)
    display(play(osc_wavetable(frames, phase, pos)))
'''),
        M(r'''
## 6. 会动的 position

这是这一集最重要的一步。

上面 `pos` 是 **一个数**:整个 2 秒都停在同一个位置。

`pos` 也可以是 **一个和声音一样长的 array**:每个 sample 有自己的 position。函数一行都不用改 — 因为里面所有运算(乘、取整、读表)本来就是整串一起算的。

在 Max 里,这就是 "往 WT POS 的 inlet 接一个 number" 和 "接一条 signal" 的区别。

### 6.1 `line~`:直线扫过

`np.linspace(0, 1, len(t))`:从 0 均匀走到 1,一共 `len(t)` 个数。就是 `line~`。

**应该听到:** 一个音在 2 秒内从 "呜"(暗)平滑地打开成 "哇"(亮)。
''', r'''
## 6. A moving position

This is the most important step of the episode.

Above, `pos` was **one number**: the whole 2 seconds stayed in one place.

`pos` can also be **an array as long as the sound**: each sample gets its own position. The function needs no change at all — every operation inside it (multiply, round, look up) already works on whole arrays.

In Max this is the difference between patching a number into the WT POS inlet and patching a signal into it.

### 6.1 `line~`: a straight sweep

`np.linspace(0, 1, len(t))`: walk evenly from 0 to 1 in `len(t)` steps. That is `line~`.

**You should hear:** one note opening smoothly from "ooh" (dark) to "aah" (bright) over 2 seconds.
'''),
        C(r'''
pos = np.linspace(0, 1, len(t))        # [[每个 sample 一个 position:0, ..., 1||one position per sample: 0, ..., 1]]

print("pos is an array of length", len(pos), "  first:", pos[0], "  last:", pos[-1])
play(osc_wavetable(frames, phase, pos))
'''),
        M(r'''
用 spectrogram 看一下(横轴时间,纵轴频率,越亮越响;第 10 集会细讲)。

**应该看到:** 一开始只有最底下一条线(基音),然后上面的 harmonic 一条一条地长出来。
''', r'''
Look at it as a spectrogram (time across, frequency up, brighter = louder; Episode 10 covers this properly).

**You should see:** only the bottom line (the fundamental) at first, then the harmonics above it appearing one by one.
'''),
        C(r'''
plt.figure(figsize=(9, 3.5))
plt.specgram(osc_wavetable(frames, phase, pos) + 1e-9, NFFT=2048, Fs=sr, noverlap=1536, cmap="magma", vmin=-120)
plt.ylim(0, 4000)
plt.xlabel("time (s)")
plt.ylabel("frequency (Hz)")
plt.show()
'''),
        M(r'''
### 6.2 LFO:来回走

一个每秒来回 2 次的 sine。`np.sin` 的范围是 -1 到 1,而 position 要 0 到 1,所以:`0.5 + 0.5 * sin`。

**应该听到:** 音色以每秒 2 次的速度 "呜哇呜哇" 地开合。
''', r'''
### 6.2 An LFO: back and forth

A sine that goes back and forth twice per second. `np.sin` ranges from -1 to 1 but position needs 0 to 1, hence `0.5 + 0.5 * sin`.

**You should hear:** the timbre opening and closing, "wah-wah", twice per second.
'''),
        C(r'''
lfo = np.sin(2 * np.pi * 2 * t)        # [[2 Hz 的 sine,-1..1||a 2 Hz sine, -1..1]]
pos = 0.5 + 0.5 * lfo                  # [[挪到 0..1||shifted to 0..1]]

plt.figure(figsize=(9, 2))
plt.plot(t, pos)
plt.xlabel("time (s)")
plt.ylabel("pos")
plt.show()

play(osc_wavetable(frames, phase, pos))
'''),
        M(r'''
### 6.3 快速落下

`np.exp(-6 * t)`:从 1 开始,很快掉下来,越掉越慢(exponential decay)。

**应该听到:** 开头很亮,不到半秒就变暗 — 一个 "piu" 的感觉。
''', r'''
### 6.3 A quick fall

`np.exp(-6 * t)`: starts at 1, drops fast, then slower and slower (exponential decay).

**You should hear:** bright at the start, dark within half a second — a "pew" feel.
'''),
        C(r'''
pos = np.exp(-6 * t)

plt.figure(figsize=(9, 2))
plt.plot(t, pos)
plt.xlabel("time (s)")
plt.ylabel("pos")
plt.show()

play(osc_wavetable(frames, phase, pos))
'''),
        M(r'''
## 7. 做自己的 frames

`frames` 不一定要 "从暗到亮"。任何一组 2048 点的表叠起来都行。

下面做 8 张表,每张的 12 个 harmonic 音量是 **随机** 的。

- `rng = np.random.default_rng(3)`:一个随机数发生器。`3` 是 seed — 同一个 seed 每次得到同一组随机数,换一个数就换一套表。
- `rng.uniform(0, 1, 12)`:12 个 0 到 1 之间的随机数
- `/ np.arange(1, 13)`:第 k 个除以 k,让高次 harmonic 整体弱一些,不至于太刺

**应该听到:** `pos` 扫过时,音色不是单纯变亮,而是不断变形,有点像元音在变化。
''', r'''
## 7. Building your own frames

`frames` does not have to run "dark to bright". Any set of 2048-point tables stacked up will do.

Below are 8 tables whose 12 harmonic levels are **random**.

- `rng = np.random.default_rng(3)`: a random number generator. `3` is the seed — the same seed gives the same random numbers every time; another number gives another set of tables.
- `rng.uniform(0, 1, 12)`: 12 random numbers between 0 and 1
- `/ np.arange(1, 13)`: divide the k-th by k so upper harmonics are weaker overall and not too harsh

**You should hear:** as `pos` sweeps, the timbre does not simply brighten; it keeps reshaping, a bit like changing vowels.
'''),
        C(r'''
rng = np.random.default_rng(3)

weird = []
for f in range(8):
    amps = rng.uniform(0, 1, 12) / np.arange(1, 13)     # [[12 个随机音量,越高次越弱||12 random levels, weaker for higher harmonics]]
    weird.append(make_table(amps))
weird = np.array(weird)

fig, axes = plt.subplots(1, 8, figsize=(13, 1.8), sharey=True)
for f, ax in enumerate(axes):
    ax.plot(weird[f])
    ax.set_title(f"frame {f}", fontsize=8)
    ax.set_xticks([])
plt.show()

play(osc_wavetable(weird, phase, np.linspace(0, 1, len(t))))
'''),
        M(r'''
## 常见错误

| 现象 | 原因 |
|---|---|
| `IndexError` 说 index 16 超出范围 | `pos` 超过了 1。函数里的 `np.clip(pos, 0, 1)` 就是防这个的 |
| `shape mismatch` | `pos` 是 array,但长度和 `phase` 不一样 |
| position 在动,但听不出变化 | 相邻的 frame 太像了;或者 `pos` 变化范围太小 |
| 扫过时有 "咔哒" 声 | 相邻两张表差别太大,或者 frame 太少 |

## 练习

**1.** 让 `pos` 从 1 走到 0(反过来)。**应该听到:** 从亮到暗。

<details><summary>答案</summary>

```python
play(osc_wavetable(frames, phase, np.linspace(1, 0, len(t))))
```
</details>

**2.** 把 6.2 的 LFO 速度改成每秒 8 次,并让 position 只在 0.2 到 0.6 之间来回。提示:中心是 0.4,幅度是 0.2。

<details><summary>答案</summary>

```python
pos = 0.4 + 0.2 * np.sin(2 * np.pi * 8 * t)
play(osc_wavetable(frames, phase, pos))
```
</details>

**3.** 做一套 "从 sine 到 square" 的 frames:16 张,只用奇数 harmonic,数量递增。提示:奇数 harmonic 的 list 是 `[1, 0, 1/3, 0, 1/5, ...]`。

<details><summary>答案</summary>

```python
sq = []
for f in range(16):
    amps = []
    for k in range(1, 2 * f + 2):
        amps.append(1 / k if k % 2 == 1 else 0)     # 奇数给 1/k,偶数给 0
    sq.append(make_table(amps))
sq = np.array(sq)
play(osc_wavetable(sq, phase, np.linspace(0, 1, len(t))))
```
</details>

## 小结

| Max / Serum | Python |
|---|---|
| `xfade~` / `mix~` | `(1 - mix) * a + mix * b` |
| 多个单周期的 `buffer~` | `frames`(二维 array) |
| WT POS 旋钮 | `pos`(一个数) |
| signal 接到 WT POS | `pos`(一个 array) |
| `line~` | `np.linspace(start, end, n)` |

**最重要的一点:** 在 Python 里,"参数" 和 "signal" 没有区别 — 传一个数就是静态的,传一个 array 就是会动的。

**下一集:** `adsr~` — 让声音有头有尾。
''', r'''
## Common mistakes

| Symptom | Cause |
|---|---|
| `IndexError` saying index 16 is out of range | `pos` went above 1. The `np.clip(pos, 0, 1)` inside the function guards against this |
| `shape mismatch` | `pos` is an array whose length differs from `phase` |
| The position moves but nothing audible changes | Neighbouring frames are too alike, or `pos` covers too small a range |
| Clicks during a sweep | Neighbouring tables differ too much, or there are too few frames |

## Exercises

**1.** Let `pos` run from 1 to 0 (reversed). **You should hear:** bright to dark.

<details><summary>Answer</summary>

```python
play(osc_wavetable(frames, phase, np.linspace(1, 0, len(t))))
```
</details>

**2.** Change the LFO of 6.2 to 8 times per second and keep the position between 0.2 and 0.6. Hint: the centre is 0.4, the depth is 0.2.

<details><summary>Answer</summary>

```python
pos = 0.4 + 0.2 * np.sin(2 * np.pi * 8 * t)
play(osc_wavetable(frames, phase, pos))
```
</details>

**3.** Build a "sine to square" set of frames: 16 of them, odd harmonics only, with a rising count. Hint: the odd-harmonic list is `[1, 0, 1/3, 0, 1/5, ...]`.

<details><summary>Answer</summary>

```python
sq = []
for f in range(16):
    amps = []
    for k in range(1, 2 * f + 2):
        amps.append(1 / k if k % 2 == 1 else 0)     # 1/k for odd k, 0 for even k
    sq.append(make_table(amps))
sq = np.array(sq)
play(osc_wavetable(sq, phase, np.linspace(0, 1, len(t))))
```
</details>

## Recap

| Max / Serum | Python |
|---|---|
| `xfade~` / `mix~` | `(1 - mix) * a + mix * b` |
| a `buffer~` with many single cycles | `frames` (a 2-D array) |
| the WT POS knob | `pos` (one number) |
| a signal into WT POS | `pos` (an array) |
| `line~` | `np.linspace(start, end, n)` |

**The most important point:** in Python there is no difference between a "parameter" and a "signal" — pass one number and it is static, pass an array and it moves.

**Next episode:** `adsr~` — giving the sound a beginning and an end.
'''),
    ])
