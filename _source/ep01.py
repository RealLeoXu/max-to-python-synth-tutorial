from common import *

EP = dict(
    zh_file="01_没有dac_声音就是array",
    en_file="01_no_dac_sound_is_an_array",
    cells=[
        M(r'''
# 第 1 集 — 没有 `dac~`:声音就是一个 array

⏱ 约 25 分钟

**这一集控制的音乐元素:pitch(音高)、时长、音量。**

**Max 里的对应 patch:** `cycle~ 110` → `*~ 0.3` → `dac~`,开 2 秒再关。

**你会听到:** 一个干净、低沉的 "嗡——"(A2,110 Hz),持续 2 秒。之后你会自己做出三个音的小旋律和一个和弦。

**学完你能做到:**
- 说清楚 Max 的 signal 和 Python 的 array 有什么不同
- 从零写出一个 sine,并听到、看到它
- 改 pitch、时长、音量
- 把几个音接成旋律、叠成和弦
- 把声音存成 `.wav` 文件

---

### Max 和 Python 最大的区别

| | Max / RNBO | Python |
|---|---|---|
| 时间 | 自己在走,打开 `dac~` 就一直流 | 没有 "正在走的时间" |
| 声音 | 一个一个 sample 实时送出去 | **一次把整段算完**,放进一个 array |
| 听 | 立刻听到 | 算完以后再播放 |

所以在 Python 里做 synth,本质上是:**算出一长串数字,然后播放它。**
''', r'''
# Episode 1 — No `dac~`: Sound Is an Array

⏱ About 25 minutes

**Musical elements this episode controls: pitch, duration and volume.**

**The equivalent Max patch:** `cycle~ 110` → `*~ 0.3` → `dac~`, switched on for 2 seconds.

**What you will hear:** a clean, low hum (A2, 110 Hz) lasting 2 seconds. Later you will build a three-note melody and a chord yourself.

**By the end you can:**
- explain how a Max signal differs from a Python array
- write a sine from scratch, hear it and see it
- change pitch, duration and volume
- join notes into a melody and stack them into a chord
- save the sound as a `.wav` file

---

### The biggest difference between Max and Python

| | Max / RNBO | Python |
|---|---|---|
| Time | Runs by itself; turn on `dac~` and audio flows | There is no "running time" |
| Sound | Sent out one sample at a time, live | **The whole sound is computed at once** into an array |
| Listening | Immediate | Compute first, then play |

So building a synth in Python really means: **compute a long list of numbers, then play it.**
'''),
        M(r'''
## 0. 怎么用这个 notebook

- 每个灰色格子叫一个 **cell**。点进去,按 **Shift + Enter** 运行它。
- **从上往下按顺序运行。** 后面的 cell 会用到前面 cell 里算出来的东西。
- 改了某个 cell 里的数字之后,要 **重新运行那个 cell 以及它下面用到它的 cell**,改动才会生效。这一点和 Max 不一样:Max 改了数字立刻生效,这里要 "重新算一遍"。
- ⚠️ 先把系统音量调小一点再开始。

下面这格是 "载入工具":

| 这一行 | 是什么 | 像 Max 里的 |
|---|---|---|
| `numpy`(简写 `np`) | 对一整串数字做数学运算 | 所有带 `~` 的数学 object |
| `matplotlib`(简写 `plt`) | 画图 | `scope~` |
| `Audio` | 播放器 | `dac~` |
| `wavfile` | 读写 wav 文件 | `sfrecord~` / `buffer~` 的 write |
''', r'''
## 0. How to use this notebook

- Each grey box is a **cell**. Click into it and press **Shift + Enter** to run it.
- **Run from top to bottom, in order.** Later cells use what earlier cells computed.
- After changing a number in a cell, **re-run that cell and the cells below that depend on it** for the change to take effect. This differs from Max: there a change is live, here you "recompute".
- ⚠️ Turn your system volume down a little before you start.

The cell below "loads the tools":

| This line | What it is | Like, in Max |
|---|---|---|
| `numpy` (short: `np`) | math on whole lists of numbers | every math object with a `~` |
| `matplotlib` (short: `plt`) | plotting | `scope~` |
| `Audio` | a player | `dac~` |
| `wavfile` | read/write wav files | `sfrecord~` / write on `buffer~` |
'''),
        C(r'''
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import Audio, display
from scipy.io import wavfile
'''),
        M(r'''
## 1. 什么是 array

array 就是 **一串按顺序排好的数字**。先做一个只有 4 个数的。

要记住的四件事:

1. **整串一起算。** `a * 2` 会把里面每个数都乘 2。不需要循环。
2. **`len(a)`** 是它有多少个数。
3. **方括号取数,从 0 开始数。** `a[0]` 是第一个,`a[3]` 是第四个。
4. **`a[:2]`** 是 "从头取到第 2 个之前",也就是前两个。这叫 slicing。

运行下面这格,对照输出看。
''', r'''
## 1. What an array is

An array is **a list of numbers in a fixed order**. Start with one that holds just 4 numbers.

Four things to remember:

1. **Math happens on the whole thing.** `a * 2` multiplies every number by 2. No loop needed.
2. **`len(a)`** is how many numbers it holds.
3. **Square brackets pick a number, counting from 0.** `a[0]` is the first, `a[3]` the fourth.
4. **`a[:2]`** means "from the start up to, but not including, index 2" — the first two. This is slicing.

Run the cell and compare with the output.
'''),
        C(r'''
a = np.array([10, 20, 30, 40])

print("a        =", a)
print("a * 2    =", a * 2)
print("a + 1    =", a + 1)
print("len(a)   =", len(a))
print("a[0]     =", a[0])
print("a[3]     =", a[3])
print("a[:2]    =", a[:2])
'''),
        M(r'''
**和 Max 对照:** 一条 signal patch cord 里流着无数个 sample,你看不到它们的 "编号"。array 是把这些 sample **停下来、排成一排、编上号**,所以可以随便取其中任何一个。

## 2. 三个数字

- `sr`:sample rate,每秒多少个 sample(Max 的 Audio Status 里那个数)
- `freq`:频率,单位 Hz → 决定 **pitch**
- `dur`:时长,单位秒
''', r'''
**Compared with Max:** a signal patch cord carries endless samples and you never see their "numbers". An array is those samples **stopped, lined up and numbered**, so you can pick any one of them.

## 2. Three numbers

- `sr`: sample rate, samples per second (the number in Max's Audio Status)
- `freq`: frequency in Hz → sets the **pitch**
- `dur`: duration in seconds
'''),
        C(r'''
sr = 44100
freq = 110
dur = 2.0
'''),
        M(r'''
## 3. 时间表 `t`

Max 里时间自己在走。Python 里要先把 **每个 sample 发生在第几秒** 写成一张表。

### 先用小数字

假设每秒只有 4 个 sample,一共 2 秒。

- `small_sr * small_dur` = 8 → 一共 8 个 sample
- `np.arange(8)` → 从 0 数到 7,是每个 sample 的编号
- `/ small_sr` → 每个编号除以 4,编号变成秒
''', r'''
## 3. The time table `t`

In Max, time runs by itself. In Python you first write down **at which second each sample happens**.

### Small numbers first

Suppose there are only 4 samples per second, for 2 seconds.

- `small_sr * small_dur` = 8 → 8 samples in total
- `np.arange(8)` → counts 0 to 7, the index of each sample
- `/ small_sr` → divide each index by 4; indices become seconds
'''),
        C(r'''
small_sr = 4
small_dur = 2

index = np.arange(int(small_sr * small_dur))   # [[每个 sample 的编号:0, 1, 2 ...||the index of each sample: 0, 1, 2 ...]]
small_t = index / small_sr                     # [[编号 ÷ 每秒个数 = 第几秒||index ÷ samples per second = which second]]

print("index   =", index)
print("small_t =", small_t)
'''),
        M(r'''
读一下输出:第 0 个 sample 在 0 秒,第 1 个在 0.25 秒……第 4 个正好在 1 秒(因为每秒 4 个)。

`int(...)` 的作用:`4 * 2` 在这里其实是 `8.0`(带小数点),而 "个数" 必须是整数,所以用 `int` 把它变成 `8`。

### 真实的数字

完全一样的写法,只是 `sr = 44100`。
''', r'''
Read the output: sample 0 is at 0 s, sample 1 at 0.25 s ... sample 4 lands exactly on 1 s (there are 4 per second).

What `int(...)` does: `4 * 2` here is really `8.0` (with a decimal point), but a count has to be a whole number, so `int` turns it into `8`.

### Real numbers

Exactly the same code, only with `sr = 44100`.
'''),
        C(r'''
# [[和上面完全一样:编号 ÷ sr = 每个 sample 的时间(秒)||same as above: index ÷ sr = the time of each sample in seconds]]
t = np.arange(int(sr * dur)) / sr

print("number of samples:", len(t))
print("first five:", t[:5])
print("last one:", t[-1])
'''),
        M(r'''
`t[-1]` 是 "最后一个"。它不是 2.0,而是比 2 秒少一个 sample 的时间 — 因为是从 0 开始数的。

**`t` 里还没有声音,只有时间。**

## 4. 振幅 `x`

现在在每个时间点上填一个振幅。

### 先用小数字

每秒 8 个 sample,频率 1 Hz(每秒 1 个周期),只看 1 秒。

- `freq * t` → 到这个时间点为止,**走了几个周期**
- `2 * np.pi *` → `sin` 只认角度,1 个周期 = 2π。这里只是换单位。
- `np.sin(...)` → sine 在那个位置的高度
''', r'''
`t[-1]` means "the last one". It is not 2.0 but one sample short of 2 seconds — because we count from 0.

**`t` holds no sound yet, only time.**

## 4. The amplitude `x`

Now fill in an amplitude at each time point.

### Small numbers first

8 samples per second, frequency 1 Hz (1 cycle per second), 1 second only.

- `freq * t` → **how many cycles have elapsed** by that time point
- `2 * np.pi *` → `sin` wants an angle, and 1 cycle = 2π. Just a unit conversion.
- `np.sin(...)` → the height of the sine at that position
'''),
        C(r'''
tiny_t = np.arange(8) / 8                 # [[1 秒,8 个 sample||1 second, 8 samples]]
cycles = 1 * tiny_t                       # [[freq × 时间 = 走了几个周期||freq × time = cycles elapsed]]
tiny_x = np.sin(2 * np.pi * cycles)       # [[周期数 × 2π = 角度,再取 sine||cycles × 2π = angle, then take the sine]]

print("time           :", tiny_t)
print("cycles elapsed :", cycles)
print("amplitude      :", np.round(tiny_x, 2))
'''),
        M(r'''
读一下 `amplitude` 那一行:0 → 0.71 → 1(最高点)→ 0.71 → 0 → -0.71 → -1(最低点)→ -0.71。正好一个完整的 sine 周期。

(`np.round(..., 2)` 只是为了打印时保留两位小数,好读。)

### 真实的数字
''', r'''
Read the `amplitude` row: 0 → 0.71 → 1 (the top) → 0.71 → 0 → -0.71 → -1 (the bottom) → -0.71. Exactly one full sine cycle.

(`np.round(..., 2)` only rounds to two decimals for printing.)

### Real numbers
'''),
        C(r'''
# [[freq * t = 走了几个周期;× 2π 换成角度;sin 给出那一刻的振幅||freq * t = cycles elapsed; × 2π makes it an angle; sin gives the amplitude at that moment]]
x = np.sin(2 * np.pi * freq * t)

print("number of samples:", len(x))
print("t[100] =", t[100], "   x[100] =", x[100])
'''),
        M(r'''
### 关于 `t` 和 `x`

- 两个 array 一样长(88200 个数)
- **位置就是编号**:`t[100]` 和 `x[100]` 说的是同一个 sample,一个是它的时间,一个是它的振幅
- `x[100]` 是用 `t[100]` 算出来的,所以顺序自然对得上,不需要另外做标记
- **`x` 就是声音本身。** `t` 只是为了算出 `x`(以及画图的横轴)

## 5. 听(这就是 `dac~`)

`Audio(array, rate=sr)` 会显示一个播放器。

- 第一个位置:要播放的 array
- `rate=sr`:每秒播多少个 sample。它需要这个数才知道用多快的速度播放
- `normalize=False`:不要自动把音量拉到最大

**应该听到:** 一个干净、低沉的 "嗡——",2 秒。
''', r'''
### About `t` and `x`

- both arrays have the same length (88200 numbers)
- **position is the index**: `t[100]` and `x[100]` describe the same sample; one is its time, the other its amplitude
- `x[100]` was computed from `t[100]`, so the order matches by itself; no extra labelling needed
- **`x` is the sound.** `t` exists only to compute `x` (and to label the plot axis)

## 5. Listen (this is your `dac~`)

`Audio(array, rate=sr)` shows a small player.

- first slot: the array to play
- `rate=sr`: samples per second. It needs this to know how fast to play
- `normalize=False`: do not auto-maximize the volume

**You should hear:** a clean, low hum for 2 seconds.
'''),
        C(r'''
Audio(0.3 * x, rate=sr, normalize=False)
'''),
        M(r'''
### 音量

`0.3 * x` 就是 `*~ 0.3`:每个 sample 都乘 0.3。

`x` 原本在 -1 到 1 之间。-1 到 1 是 "满刻度",超过就会 clipping。

**应该听到:** 下面两个音,第一个明显比第二个小声。pitch 完全一样。
''', r'''
### Volume

`0.3 * x` is `*~ 0.3`: every sample is multiplied by 0.3.

`x` originally sits between -1 and 1. That range is full scale; beyond it you clip.

**You should hear:** two tones below, the first clearly quieter than the second. Same pitch.
'''),
        C(r'''
display(Audio(0.05 * x, rate=sr, normalize=False))
display(Audio(0.4 * x, rate=sr, normalize=False))
'''),
        M(r'''
(一个 cell 里要显示多个播放器时,每个外面包一层 `display(...)`。只有一个时可以不包。)

## 6. 看(这就是 `scope~`)

`plt.plot(横轴, 纵轴)`。只画前 0.03 秒,否则 88200 个点挤在一起什么都看不清。

`n = int(sr * 0.03)` 是 0.03 秒对应多少个 sample;`t[:n]`、`x[:n]` 是各取前 `n` 个。

**先猜再运行:** 110 Hz 的音,0.03 秒里应该有几个周期?
''', r'''
(To show several players from one cell, wrap each in `display(...)`. With a single one you can leave it out.)

## 6. Look (this is your `scope~`)

`plt.plot(horizontal, vertical)`. Plot only the first 0.03 seconds; otherwise 88200 points are squeezed together and you see nothing.

`n = int(sr * 0.03)` is how many samples 0.03 seconds is; `t[:n]` and `x[:n]` take the first `n` of each.

**Guess before running:** how many cycles should a 110 Hz tone show in 0.03 seconds?
'''),
        C(r'''
n = int(sr * 0.03)                # [[0.03 秒 = 多少个 sample||how many samples 0.03 seconds is]]

plt.figure(figsize=(9, 3))
plt.plot(t[:n], x[:n])            # [[横轴:时间,纵轴:振幅,各取前 n 个||horizontal: time, vertical: amplitude, first n of each]]
plt.xlabel("time (s)")
plt.ylabel("amplitude")
plt.title(f"sine, {freq} Hz")
plt.show()
'''),
        M(r'''
答案:110 × 0.03 = 3.3 个周期。数一下图里的波峰。

### 放大到能看见 sample

只画前 60 个 sample,并且用圆点标出每一个。**声音其实是这些点,线只是画图时连起来的。**
''', r'''
Answer: 110 × 0.03 = 3.3 cycles. Count the peaks in the plot.

### Zoom in until you see samples

Plot only the first 60 samples, with a dot on each. **The sound really is these dots; the line is only drawn between them.**
'''),
        C(r'''
plt.figure(figsize=(9, 3))
plt.plot(t[:60], x[:60], marker="o", markersize=3)
plt.xlabel("time (s)")
plt.ylabel("amplitude")
plt.title("first 60 samples")
plt.show()
'''),
        M(r'''
## 7. 包成自己的 object

每次都打 `Audio(0.3 * x, rate=sr, normalize=False)` 很累。在 Max 里你会把常用的一组 object 做成 **abstraction / subpatcher**。Python 里对应的是 **函数**(`def`)。

```python
def 名字(inlet1, inlet2):
    ...做事...
    return outlet
```

- 括号里的是 **inlet**(叫 argument)
- `return` 后面的是 **outlet**
- `gain=0.3` 表示这个 inlet 有默认值,不给就是 0.3
- 缩进的那几行属于这个函数

下面定义三个,之后每一集都会用:

- `play(x)` → `dac~`(里面的 `np.clip` 把超过 ±1 的部分压住,保护耳朵)
- `scope(x)` → `scope~`
- `tone(freq, dur)` → `cycle~` 开一段时间
''', r'''
## 7. Wrapping things into your own objects

Typing `Audio(0.3 * x, rate=sr, normalize=False)` every time is tiring. In Max you would turn a group of objects you reuse into an **abstraction / subpatcher**. The Python equivalent is a **function** (`def`).

```python
def name(inlet1, inlet2):
    ...do things...
    return outlet
```

- what is in the parentheses are the **inlets** (called arguments)
- what follows `return` is the **outlet**
- `gain=0.3` gives that inlet a default: leave it out and it is 0.3
- the indented lines belong to the function

Three definitions follow; every later episode uses them:

- `play(x)` → `dac~` (the `np.clip` inside holds anything beyond ±1, protecting your ears)
- `scope(x)` → `scope~`
- `tone(freq, dur)` → `cycle~` switched on for a while
'''),
        C(r'''
def play(x, gain=0.3):
    # [[gain * x 是音量;np.clip 把超过 ±1 的部分压住||gain * x is the volume; np.clip holds anything beyond ±1]]
    return Audio(np.clip(gain * np.asarray(x), -1, 1), rate=sr, normalize=False)

def scope(x, title="", seconds=0.03):
    n = int(sr * seconds)                      # [[只画开头这么多个 sample||only plot this many samples from the start]]
    plt.figure(figsize=(9, 2.5))
    plt.plot(np.arange(n) / sr, np.asarray(x)[:n])
    plt.xlabel("time (s)")
    plt.title(title)
    plt.show()

def tone(freq, dur):
    t = np.arange(int(sr * dur)) / sr          # [[这个 t 只在函数里面用,和外面的 t 互不影响||this t lives only inside the function and does not touch the outer t]]
    return np.sin(2 * np.pi * freq * t)
'''),
        M(r'''
定义函数时 **什么都不会发生**(就像把 abstraction 存了盘但还没放进 patch)。要 "调用" 它才会运行:

**应该听到:** 220 Hz、1 秒的 sine(比刚才高一个八度)。图里 0.03 秒内有 6.6 个周期。
''', r'''
Defining a function **does nothing by itself** (like saving an abstraction without putting it in a patch). It runs when you "call" it:

**You should hear:** a 220 Hz sine for 1 second (an octave above the earlier one). The plot shows 6.6 cycles in 0.03 seconds.
'''),
        C(r'''
y = tone(220, 1.0)

scope(y, "tone(220, 1.0)")
play(y)
'''),
        M(r'''
## 8. 旋律:把 array 接起来

`np.concatenate([a, b, c])` 把几个 array **首尾相接** 成一个更长的 array。

在 Max 里要做旋律得有 `metro`、`counter`、`mtof`…… 在 Python 里,时间就是 array 里的位置,所以 "先后" 就是 "接在后面"。

**应该听到:** 三个音依次响起,A – C# – E(一个上行的大三和弦分解),每个 0.4 秒。
''', r'''
## 8. A melody: joining arrays

`np.concatenate([a, b, c])` joins several arrays **end to end** into one longer array.

In Max a melody needs `metro`, `counter`, `mtof` ... In Python, time is the position inside the array, so "after" simply means "appended".

**You should hear:** three notes in sequence, A – C# – E (a rising major arpeggio), 0.4 seconds each.
'''),
        C(r'''
melody = np.concatenate([tone(220.00, 0.4), tone(277.18, 0.4), tone(329.63, 0.4)])

print("total samples:", len(melody), "=", len(melody) / sr, "seconds")
play(melody)
'''),
        M(r'''
你可能在音与音交界处听到很轻的 "嗒" 一声。那是因为前一个音没有正好结束在 0 上,波形突然跳了一下。第 5 集的 envelope 会解决它。

## 9. 和弦:把 array 加起来

**接起来 = 先后。加起来 = 同时。**

`a + b` 把两个一样长的 array 逐个 sample 相加。这就是 mixing — 在 Max 里把两根 patch cord 接到同一个 inlet 上,做的就是这件事。

三个 sine 加起来,振幅最大可能到 3,所以音量要调低(`gain=0.1`)。

**应该听到:** 同样三个音,这次同时响,一个 A 大三和弦,2 秒。
''', r'''
You may hear a faint "tick" where one note meets the next. The earlier note did not end exactly on 0, so the waveform jumps. The envelope in Episode 5 fixes that.

## 9. A chord: adding arrays

**Joining = one after another. Adding = at the same time.**

`a + b` adds two arrays of equal length sample by sample. That is mixing — patching two cords into the same inlet in Max does exactly this.

Three sines added can reach an amplitude of 3, so lower the level (`gain=0.1`).

**You should hear:** the same three notes, now together: an A major chord for 2 seconds.
'''),
        C(r'''
chord = tone(220.00, 2.0) + tone(277.18, 2.0) + tone(329.63, 2.0)

print("max amplitude:", np.max(np.abs(chord)))
scope(chord, "three sines added")
play(chord, gain=0.1)
'''),
        M(r'''
图里的波形不再是 sine 了 — 三个 sine 叠在一起会形成更复杂的形状。记住这一点,第 3 集会用同样的办法(叠 sine)来设计音色。

## 10. 存成文件

Python 的 output 不只是播放器。`wavfile.write(文件名, sr, array)` 会在这个 notebook 旁边写出一个 wav 文件,可以拖进 Max、Ableton 或任何 DAW。

`.astype(np.float32)` 是把数字存成 32-bit float 格式(wav 的标准格式之一)。
''', r'''
The waveform is no longer a sine — three sines stacked form a more complex shape. Keep that in mind: Episode 3 uses the same trick (stacking sines) to design timbres.

## 10. Saving a file

Python's output is not only the player. `wavfile.write(filename, sr, array)` writes a wav file next to this notebook, ready to drop into Max, Ableton or any DAW.

`.astype(np.float32)` stores the numbers as 32-bit floats (one of the standard wav formats).
'''),
        C(r'''
wavfile.write("ep01_melody.wav", sr, (0.3 * melody).astype(np.float32))
print("saved ep01_melody.wav")
'''),
        M(r'''
## 11. 一个小实验:`rate` 说谎会怎样

array 只是一串数字,它自己不知道 "每秒该播多少个"。那是 `rate` 告诉播放器的。

如果我们骗它说 sample rate 只有一半:

**先猜再运行:** pitch 会怎样?时长会怎样?
''', r'''
## 11. A small experiment: lying about `rate`

An array is just numbers; it does not know "how many per second". The `rate` tells the player.

Suppose we lie and say the sample rate is half:

**Guess before running:** what happens to the pitch? To the duration?
'''),
        C(r'''
# [[sr // 2 = 22050:告诉播放器每秒只播一半的 sample||sr // 2 = 22050: tell the player to play half as many samples per second]]
Audio(0.3 * x, rate=sr // 2, normalize=False)
'''),
        M(r'''
答案:低一个八度,时长变成 4 秒。同样的数字,播得慢一倍 — 和把磁带放慢、或者 `groove~` 的速度设成 0.5 是同一件事。

## 常见错误

| 现象 | 原因 |
|---|---|
| 改了 `freq` 但声音没变 | 没有重新运行下面算 `x` 的那个 cell |
| `NameError: name 'x' is not defined` | 跳过了上面的 cell,从头按顺序运行一遍 |
| 声音爆掉 / 很刺 | 振幅超过 ±1 了,调低 gain |
| `operands could not be broadcast together` | 两个长度不同的 array 相加了 |

## 练习

**1.** 做一个 440 Hz、0.5 秒的音并播放。

<details><summary>答案</summary>

```python
play(tone(440, 0.5))
```
</details>

**2.** 把第 8 节的旋律改成下行(E – C# – A),每个音 0.25 秒。**应该听到:** 更快的、往下走的三个音。

<details><summary>答案</summary>

```python
play(np.concatenate([tone(329.63, 0.25), tone(277.18, 0.25), tone(220.00, 0.25)]))
```
</details>

**3.** 把 `tone(220, 2.0)` 和 `tone(223, 2.0)` 加起来播放。**先猜:** 会听到什么?

<details><summary>答案</summary>

```python
play(tone(220, 2.0) + tone(223, 2.0), gain=0.15)
```
一个音,音量每秒起伏 3 次(beating)。两个频率差 3 Hz,所以每秒有 3 次互相抵消。
</details>

## 小结

| Max | Python |
|---|---|
| signal(一直在流) | array(一次算完) |
| `cycle~ 110` | `np.sin(2 * np.pi * 110 * t)` |
| `*~ 0.3` | `0.3 * x` |
| 两根线接同一个 inlet | `a + b` |
| `dac~` | `play(x)` |
| `scope~` | `scope(x)` |
| abstraction | `def` 函数 |
| `sfrecord~` | `wavfile.write(...)` |

**下一集:** `phasor~` — 把 pitch 和 timbre 拆开。
''', r'''
Answer: an octave lower, and 4 seconds long. The same numbers played half as fast — the same thing as slowing a tape, or setting `groove~` to speed 0.5.

## Common mistakes

| Symptom | Cause |
|---|---|
| Changed `freq` but the sound is the same | The cell that computes `x` was not re-run |
| `NameError: name 'x' is not defined` | A cell above was skipped; run everything in order |
| The sound is harsh / blown out | Amplitude exceeds ±1; lower the gain |
| `operands could not be broadcast together` | Two arrays of different lengths were added |

## Exercises

**1.** Make and play a 440 Hz tone lasting 0.5 seconds.

<details><summary>Answer</summary>

```python
play(tone(440, 0.5))
```
</details>

**2.** Turn the melody of section 8 into a falling one (E – C# – A), 0.25 seconds per note. **You should hear:** three faster notes going down.

<details><summary>Answer</summary>

```python
play(np.concatenate([tone(329.63, 0.25), tone(277.18, 0.25), tone(220.00, 0.25)]))
```
</details>

**3.** Add `tone(220, 2.0)` and `tone(223, 2.0)` and play the result. **Guess first:** what will you hear?

<details><summary>Answer</summary>

```python
play(tone(220, 2.0) + tone(223, 2.0), gain=0.15)
```
One tone whose volume swells 3 times per second (beating). The frequencies differ by 3 Hz, so they cancel 3 times per second.
</details>

## Recap

| Max | Python |
|---|---|
| signal (always flowing) | array (computed all at once) |
| `cycle~ 110` | `np.sin(2 * np.pi * 110 * t)` |
| `*~ 0.3` | `0.3 * x` |
| two cords into one inlet | `a + b` |
| `dac~` | `play(x)` |
| `scope~` | `scope(x)` |
| abstraction | a `def` function |
| `sfrecord~` | `wavfile.write(...)` |

**Next episode:** `phasor~` — separating pitch from timbre.
'''),
    ])
