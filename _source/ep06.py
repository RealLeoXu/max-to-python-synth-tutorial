from common import *

EP = dict(
    zh_file="06_lores_filter与sample循环",
    en_file="06_lores_filter_and_the_sample_loop",
    cells=[
        M(r'''
# 第 6 集 — `lores~`:filter 与 sample 循环

⏱ 约 30 分钟

**这一集控制的音乐元素:brightness(明暗)和 resonance(共鸣的 "鼻音" 感)。**

**Max 里的对应 patch:** saw → `onepole~`,然后 saw → `lores~`(或 `svf~`)。

**你会听到:**
1. 原始的亮 saw,和过了 lowpass 之后变闷的同一个音
2. 加上 resonance 后,在 cutoff 附近多出的 "鼻音 / 口哨" 尖峰
3. 一段白噪声被 filter 变成 "风声" 和 "口哨"

**学完你能做到:**
- 解释为什么 filter 必须写循环,而 oscillator 不用
- 逐行读懂一个 one-pole lowpass
- 把它和 gen~ 里的 `history` 对上
- 使用带 resonance 的 `lowpass()`
- 用 spectrum 看 filter 做了什么

这是整个系列里概念最新的一集。慢一点没关系。
''', r'''
# Episode 6 — `lores~`: the Filter and the Sample Loop

⏱ About 30 minutes

**Musical element this episode controls: brightness and resonance (the "nasal" ring).**

**The equivalent Max patch:** saw → `onepole~`, then saw → `lores~` (or `svf~`).

**What you will hear:**
1. the raw bright saw, and the same note made dull by a lowpass
2. with resonance, a "nasal / whistling" peak near the cutoff
3. white noise turned into "wind" and a "whistle" by the filter

**By the end you can:**
- explain why a filter needs a loop while an oscillator does not
- read a one-pole lowpass line by line
- match it to `history` in gen~
- use a `lowpass()` with resonance
- see what a filter did by looking at a spectrum

This is the episode with the most new concepts in the series. Take your time.
'''),
        M(TOOLBOX_ZH, TOOLBOX_EN),
        C(J(BASE, r'''
import time
''', TABLE, FRAMES, r'''
frames = make_frames()

freq = 110
dur = 2.0
t = np.arange(int(sr * dur)) / sr
phase = (freq * t) % 1

saw = osc_wavetable(frames, phase, 1.0)
''')),
        M(r'''
`saw` 是 wavetable 的最后一个 frame(32 个 harmonic),2 秒,110 Hz。这一集用它当 filter 的输入。

## 1. 为什么 filter 不一样

到目前为止,每个 sample 都可以 **独立** 算出来:`x[n]` 只取决于 `t[n]`,和别的 sample 无关。所以可以整串一起算,不用循环。

filter 不行。filter 的输出取决于 **它自己的上一个输出** — 这叫 feedback。

要算第 100 个输出,必须先知道第 99 个输出;要算第 99 个,必须先知道第 98 个…… 所以只能 **从头开始,一个一个按顺序算**。

在 Max 里,audio engine 本来就是这么工作的,你感觉不到。你在 `gen~` 里用 `history` 的时候碰到过它:`history` 就是 "记住上一个 sample 的结果"。

在 Python 里,"一个一个按顺序" 就是 `for` 循环。

## 2. `for` 循环

`for n in range(4):` 的意思是:让 `n` 依次等于 0、1、2、3,每次执行一遍下面缩进的那些行。
''', r'''
`saw` is the last wavetable frame (32 harmonics), 2 seconds, 110 Hz. It is the filter input throughout this episode.

## 1. Why a filter is different

So far every sample could be computed **independently**: `x[n]` depended only on `t[n]`, not on any other sample. That is why whole arrays could be computed at once with no loop.

A filter cannot work that way. Its output depends on **its own previous output** — this is feedback.

To compute output 100 you need output 99; to compute 99 you need 98 ... So the only way is to **start at the beginning and go one by one, in order**.

In Max the audio engine already works like this and you never notice. You met it when using `history` inside `gen~`: `history` is "remember the result of the previous sample".

In Python, "one by one, in order" is a `for` loop.

## 2. The `for` loop

`for n in range(4):` means: let `n` be 0, 1, 2, 3 in turn, running the indented lines each time.
'''),
        C(r'''
for n in range(4):
    print("this is round", n)
'''),
        M(r'''
循环 **外面** 定义的变量,在循环里改了之后会被 **带到下一轮**。这就是 "记住上一次" 的办法:
''', r'''
A variable defined **outside** the loop and changed inside it is **carried into the next round**. That is how you "remember the last time":
'''),
        C(r'''
total = 0                          # [[循环外面:只执行一次||outside the loop: runs once]]
for n in range(4):
    total = total + 10             # [[每一轮都在上一轮的结果上再加 10||each round adds 10 to the previous round's result]]
    print("round", n, "  total is now", total)
'''),
        M(r'''
`total` 就是一个 `history`。

## 3. 最简单的 filter:one-pole lowpass

每个 sample 只做一件事:

> **新输出 = 上一个输出 + a × (输入 − 上一个输出)**

用话说:看一下输入离我现在的位置有多远,**朝它走一小步**。`a` 决定步子多大(0 到 1)。

### 先用 10 个数走一遍

输入是一个 "台阶":前两个是 0,然后突然跳到 1。`a = 0.5`,每次走剩余距离的一半。
''', r'''
`total` is a `history`.

## 3. The simplest filter: a one-pole lowpass

For each sample it does one thing:

> **new output = previous output + a × (input − previous output)**

In words: look how far the input is from where I am now, and **take a small step toward it**. `a` sets the size of the step (0 to 1).

### Walk through it with 10 numbers

The input is a "step": two zeros, then a sudden jump to 1. `a = 0.5`, so each step covers half the remaining distance.
'''),
        C(r'''
xs = [0, 0, 1, 1, 1, 1, 1, 1, 1, 1]
a = 0.5

prev = 0.0                                     # [[上一个输出;一开始是 0||the previous output; starts at 0]]
for n in range(len(xs)):
    distance = xs[n] - prev                    # [[输入离我现在有多远||how far the input is from where I am]]
    prev = prev + a * distance                 # [[朝它走 a 那么大的一步||step toward it by a fraction a]]
    print(f"n = {n}   input = {xs[n]}   output = {prev:.3f}")
'''),
        M(r'''
读一下输出:输入在 `n = 2` 时 **瞬间** 跳到 1。输出没有跟着跳,而是 0.5 → 0.75 → 0.875 → …… 慢慢靠近 1。

**"瞬间的跳变" 被磨成了 "平滑的上升"。** 跳变就是高频。所以这个东西磨掉了高频 — 它是一个 lowpass。

### `a` 的大小

`a` 越小,步子越小,越跟不上快速变化,磨掉的高频越多。
''', r'''
Read the output: the input jumps to 1 **instantly** at `n = 2`. The output does not jump with it; it goes 0.5 → 0.75 → 0.875 → ... creeping toward 1.

**An "instant jump" has been worn into a "smooth rise".** A jump means high frequencies. So this thing wears away highs — it is a lowpass.

### The size of `a`

The smaller `a`, the smaller the step, the worse it follows fast changes, and the more highs it removes.
'''),
        C(r'''
step = np.concatenate([np.zeros(20), np.ones(180)])        # [[20 个 0,然后 180 个 1||20 zeros, then 180 ones]]

plt.figure(figsize=(9, 3))
plt.plot(step, color="gray", label="input")
for a in [0.5, 0.1, 0.02]:
    out = np.zeros(len(step))
    prev = 0.0
    for n in range(len(step)):
        prev = prev + a * (step[n] - prev)
        out[n] = prev                                      # [[把这一轮的结果存进输出 array 的第 n 格||store this round's result in slot n of the output array]]
    plt.plot(out, label=f"a = {a}")
plt.legend()
plt.xlabel("sample")
plt.show()
'''),
        M(r'''
### 包成函数:`onepole~`

用户想给的是 cutoff(Hz),不是 `a`。第一行把 cutoff 换算成 `a`:cutoff 越高,`a` 越接近 1(步子越大,放过的高频越多)。这个换算式子不用记。
''', r'''
### Wrap it in a function: `onepole~`

The user wants to give a cutoff in Hz, not `a`. The first line converts cutoff to `a`: the higher the cutoff, the closer `a` is to 1 (bigger steps, more highs let through). No need to memorise the formula.
'''),
        C(r'''
def onepole(x, cutoff):
    a = 1 - np.exp(-2 * np.pi * cutoff / sr)       # [[cutoff (Hz) → 步子大小 a (0..1)||cutoff (Hz) → step size a (0..1)]]
    y = np.zeros(len(x))                           # [[先准备一个空的输出 array||prepare an empty output array]]
    prev = 0.0                                     # [[= gen~ 里的 history||= history in gen~]]
    for n in range(len(x)):                        # [[n = 0, 1, 2 ... 88199||n = 0, 1, 2 ... 88199]]
        prev = prev + a * (x[n] - prev)            # [[朝输入走一小步||one small step toward the input]]
        y[n] = prev                                # [[存下这个 sample 的输出||store this sample's output]]
    return y

for cutoff in [100, 1000, 10000]:
    print(f"cutoff {cutoff:>5} Hz  ->  a = {1 - np.exp(-2 * np.pi * cutoff / sr):.3f}")
'''),
        M(r'''
### 和 gen~ 对照

同一个 filter,在 gen~ 的 codebox 里是这样写的:

```
History prev(0);
a = 1 - exp(-twopi * in2 / samplerate);
y = prev + a * (in1 - prev);
prev = y;
out1 = y;
```

| gen~ | Python |
|---|---|
| `History prev(0);` | 循环外面的 `prev = 0.0` |
| 这段代码每个 sample 自动跑一次 | 你自己写 `for n in range(len(x)):` |
| `in1` | `x[n]` |
| `out1 = y;` | `y[n] = prev` |

**唯一的区别:gen~ 的循环是隐藏的,Python 的循环要自己写出来。**

### 听

**应该听到:** 第一个是原始的亮 saw;第二个(cutoff 300 Hz)是同一个音,但明显变闷、变远。
''', r'''
### Side by side with gen~

The same filter in a gen~ codebox looks like this:

```
History prev(0);
a = 1 - exp(-twopi * in2 / samplerate);
y = prev + a * (in1 - prev);
prev = y;
out1 = y;
```

| gen~ | Python |
|---|---|
| `History prev(0);` | `prev = 0.0` outside the loop |
| this code runs once per sample automatically | you write `for n in range(len(x)):` yourself |
| `in1` | `x[n]` |
| `out1 = y;` | `y[n] = prev` |

**The only difference: gen~'s loop is hidden; in Python you write it out.**

### Listen

**You should hear:** the raw bright saw first; then (cutoff 300 Hz) the same note, clearly duller and more distant.
'''),
        C(r'''
display(play(saw))
display(play(onepole(saw, 300)))
'''),
        M(r'''
**应该看到:** saw 的尖角被磨圆了。
''', r'''
**You should see:** the saw's sharp corners rounded off.
'''),
        C(r'''
n = int(sr * 0.03)
plt.figure(figsize=(9, 3))
plt.plot(t[:n], saw[:n], label="saw")
plt.plot(t[:n], onepole(saw, 300)[:n], label="onepole 300 Hz")
plt.legend()
plt.xlabel("time (s)")
plt.show()
'''),
        M(r'''
### 循环的代价

整串一起算很快,循环很慢。量一下:
''', r'''
### The price of a loop

Whole-array math is fast; loops are slow. Measure it:
'''),
        C(r'''
start = time.time()
_ = np.sin(2 * np.pi * 110 * t)                # [[没有 feedback:整串一起算||no feedback: the whole array at once]]
print(f"whole-array sine : {1000 * (time.time() - start):.2f} ms")

start = time.time()
_ = onepole(saw, 300)                          # [[有 feedback:88200 轮循环||feedback: 88200 loop rounds]]
print(f"one-pole loop    : {1000 * (time.time() - start):.2f} ms")
'''),
        M(r'''
循环慢了几十到上百倍。对 2 秒的声音来说还是一眨眼,但这就是为什么 **能不写循环就不写循环**,只有 feedback 这种非写不可的地方才写。

## 4. Highpass:顺手得到的

lowpass 留下低频。**原始信号减去 lowpass 的结果,剩下的就是高频** — 一个 highpass。

**应该听到:** 很薄、只剩 "滋滋" 的声音,低音的 "身体" 没了。
''', r'''
The loop is tens to hundreds of times slower. For a 2-second sound it is still the blink of an eye, but this is why you **avoid loops whenever you can** and write them only where feedback forces you to.

## 4. Highpass: a free extra

A lowpass keeps the lows. **The original minus the lowpassed signal leaves the highs** — a highpass.

**You should hear:** a thin, fizzy sound with the low "body" gone.
'''),
        C(r'''
highpassed = saw - onepole(saw, 2000)
play(highpassed)
'''),
        M(r'''
## 5. 看 filter 做了什么:spectrum

Max 里你会接一个 `spectroscope~`。这里做一个对应的函数:输入一段声音,输出 "每个频率有多响"。

里面用的 FFT 这里不展开,**先当成一个现成的 object**。第 10 集会多讲一点。

- 横轴:频率(Hz)
- 纵轴:响度(dB),0 是最响的那个频率,越往下越弱

**应该看到:** saw 是一排等间距的竖线(harmonic),缓慢地往右变矮。过了 one-pole 之后,300 Hz 以上的竖线被压低了,越往右压得越多。
''', r'''
## 5. Seeing what a filter did: the spectrum

In Max you would patch in a `spectroscope~`. Here is a matching function: a sound goes in, "how loud is each frequency" comes out.

The FFT inside is not explained here; **treat it as a ready-made object for now**. Episode 10 says a little more.

- horizontal: frequency (Hz)
- vertical: level (dB); 0 is the loudest frequency, lower means weaker

**You should see:** the saw as a row of evenly spaced spikes (harmonics) getting slowly shorter to the right. After the one-pole, spikes above 300 Hz are pushed down, more so the further right you go.
'''),
        C(r'''
def spectrum(x):
    X = np.abs(np.fft.rfft(x * np.hanning(len(x))))        # [[每个频率的强度||the strength of every frequency]]
    f = np.fft.rfftfreq(len(x), 1 / sr)                    # [[对应的频率刻度(Hz)||the matching frequency axis (Hz)]]
    return f, 20 * np.log10(X / np.max(X) + 1e-9)          # [[换成 dB,最响的是 0||converted to dB, loudest = 0]]

def spec_plot(signals, max_freq=5000):
    plt.figure(figsize=(9, 4))
    for name in signals:
        f, db = spectrum(signals[name])
        plt.plot(f, db, label=name, linewidth=0.8)
    plt.xlim(0, max_freq)
    plt.ylim(-90, 5)
    plt.xlabel("frequency (Hz)")
    plt.ylabel("level (dB)")
    plt.legend()
    plt.show()

spec_plot({"raw saw": saw, "onepole 300 Hz": onepole(saw, 300)})
'''),
        M(r'''
## 6. 带 resonance 的 filter:`lores~` / `svf~`

one-pole 很温和(每高一个八度只降 6 dB),也没有 resonance。synth 里常用的是 2-pole 的 **state variable filter**(`svf~`):降得更陡(12 dB / 八度),而且可以在 cutoff 处顶起一个共鸣峰。

它的结构和 one-pole **完全一样**:一个循环,循环里记住上一步的状态。区别只是:

- 状态从 1 个变成 2 个(`ic1`、`ic2`)
- 每一步的算式从 1 行变成 5 行

你在 Max 里不会打开 `lores~` 去看里面。这里也一样:**知道它是 "一个循环 + 两个 history" 就够了**,算式本身不用懂。函数里每一段都有注释。

- `cutoff`:Hz(可以是一个数,也可以是 array — 下一集会用到)
- `res`:0 到 1,越大共鸣峰越尖
''', r'''
## 6. A filter with resonance: `lores~` / `svf~`

The one-pole is gentle (only 6 dB per octave) and has no resonance. Synths normally use a 2-pole **state variable filter** (`svf~`): steeper (12 dB per octave) and able to push up a resonant peak at the cutoff.

Its structure is **exactly the same** as the one-pole: a loop that remembers the previous state. The only differences:

- two state values instead of one (`ic1`, `ic2`)
- five lines of arithmetic per step instead of one

You would not open `lores~` in Max to look inside. Same here: **knowing it is "a loop plus two history values" is enough**; the arithmetic itself need not be understood. Every part of the function is commented.

- `cutoff`: Hz (one number, or an array — next episode uses that)
- `res`: 0 to 1; the higher, the sharper the resonant peak
'''),
        C(LOWPASS),
        M(r'''
### 听:cutoff

**应该听到:** 三个音,越来越亮 — 200 Hz 很闷,800 Hz 中等,4000 Hz 接近原始 saw。
''', r'''
### Listen: cutoff

**You should hear:** three notes getting brighter — 200 Hz is very dull, 800 Hz medium, 4000 Hz close to the raw saw.
'''),
        C(r'''
for cutoff in [200, 800, 4000]:
    print("cutoff", cutoff, "Hz")
    display(play(lowpass(saw, cutoff)))
'''),
        M(r'''
### 听:resonance

cutoff 固定在 800 Hz,只改 `res`。

**应该听到:** `res = 0` 是普通的闷音。`res` 升高后,在 800 Hz 附近多出一个越来越明显的 "鼻音 / 口哨" 尖峰,像嘴巴做出 "诶" 的口型。

(resonance 高的时候峰值会变大,所以后两个的 gain 调低了。)
''', r'''
### Listen: resonance

Cutoff fixed at 800 Hz, only `res` changes.

**You should hear:** `res = 0` is a plain dull tone. As `res` rises, an increasingly clear "nasal / whistling" peak appears near 800 Hz, like a mouth shaping an "eh".

(High resonance raises the peak level, so the gain is lowered for the last two.)
'''),
        C(r'''
display(play(lowpass(saw, 800, res=0.0)))
display(play(lowpass(saw, 800, res=0.6), gain=0.2))
display(play(lowpass(saw, 800, res=0.9), gain=0.15))
'''),
        M(r'''
**应该看到:** 三条线在 800 Hz 之前差不多;`res` 越大,800 Hz 那里顶起的峰越高。
''', r'''
**You should see:** the three curves are similar below 800 Hz; the higher `res`, the taller the peak pushed up at 800 Hz.
'''),
        C(r'''
spec_plot({
    "res 0.0": lowpass(saw, 800, 0.0),
    "res 0.6": lowpass(saw, 800, 0.6),
    "res 0.9": lowpass(saw, 800, 0.9),
}, max_freq=3000)
'''),
        M(r'''
## 7. Filter 一段噪声

`rng.uniform(-1, 1, n)`:`n` 个 -1 到 1 之间的随机数。每个 sample 都和前后无关 — 这就是白噪声,Max 里的 `noise~`。它包含所有频率。

**应该听到:**
1. 原始白噪声:"沙——"
2. lowpass 400 Hz:闷闷的 "轰",像远处的风或海浪
3. lowpass 1200 Hz + 很高的 resonance:噪声里浮出一个有音高的 "口哨"(在 1200 Hz 附近)
''', r'''
## 7. Filtering noise

`rng.uniform(-1, 1, n)`: `n` random numbers between -1 and 1. Each sample is unrelated to its neighbours — that is white noise, `noise~` in Max. It contains all frequencies.

**You should hear:**
1. raw white noise: "shhh"
2. lowpass at 400 Hz: a dull rumble, like distant wind or surf
3. lowpass at 1200 Hz with very high resonance: a pitched "whistle" (near 1200 Hz) rising out of the noise
'''),
        C(r'''
rng = np.random.default_rng(0)
noise = rng.uniform(-1, 1, len(t))

display(play(noise, gain=0.15))
display(play(lowpass(noise, 400), gain=0.5))
display(play(lowpass(noise, 1200, res=0.98), gain=0.15))
'''),
        M(r'''
## 8. 串联两个 filter

把 filter 的输出再送进一个同样的 filter,降得就陡一倍(24 dB / 八度)。Max 里就是两个 `lores~` 串起来。

**应该听到:** 第二个比第一个更闷、更 "圆"。
''', r'''
## 8. Two filters in series

Send a filter's output into another identical filter and the slope doubles (24 dB per octave). In Max: two `lores~` in a row.

**You should hear:** the second one duller and "rounder" than the first.
'''),
        C(r'''
once = lowpass(saw, 600)
twice = lowpass(once, 600)

display(play(once))
display(play(twice))

spec_plot({"raw saw": saw, "one filter": once, "two filters": twice}, max_freq=4000)
'''),
        M(r'''
## 常见错误

| 现象 | 原因 |
|---|---|
| filter 的输出全是 0 | 忘了 `y[n] = prev`,或者把它写到了循环外面(缩进错了) |
| 输出只是变小声了,没有变闷 | `prev = 0.0` 写在了循环 **里面**,每一轮都被重置成 0,等于没有 "记住上一次" |
| 运行特别慢 | 循环里用了不必要的 numpy 运算;或者声音太长 |
| resonance 很高时爆音 | 峰值超过 1 了,调低 gain |

缩进在 Python 里是有意义的:缩进的行属于循环,不缩进的行在循环结束后才执行。

## 练习

**1.** 把 `onepole` 的 cutoff 设成 50、500、5000,听三个结果。**先猜:** 哪个最接近原始 saw?

<details><summary>答案</summary>

```python
for c in [50, 500, 5000]:
    display(play(onepole(saw, c)))
```
5000 最接近。cutoff 越高,放过的越多。
</details>

**2.** 用 `saw - lowpass(saw, 1500, res=0.5)` 做一个带 resonance 的 highpass,听一下并画 spectrum。

<details><summary>答案</summary>

```python
hp = saw - lowpass(saw, 1500, res=0.5)
play(hp, gain=0.2)
spec_plot({"highpass": hp})
```
</details>

**3.** 把第 7 节的 "口哨" 的 cutoff 改成 300 和 3000。**应该听到:** 口哨的音高跟着 cutoff 走。

<details><summary>答案</summary>

```python
for c in [300, 1200, 3000]:
    display(play(lowpass(noise, c, res=0.98), gain=0.15))
```
</details>

## 小结

| Max | Python |
|---|---|
| audio engine 逐 sample 运行 | `for n in range(len(x)):` |
| `history`(gen~) | 循环外面定义、循环里更新的变量 |
| `onepole~` | `onepole(x, cutoff)` |
| `lores~` / `svf~` | `lowpass(x, cutoff, res)` |
| `noise~` | `rng.uniform(-1, 1, n)` |
| `spectroscope~` | `spec_plot({...})` |

**规则:** 没有 feedback → 整串 array 一起算。有 feedback → 必须写循环。

**下一集:** 把 envelope 和 LFO 接到 cutoff 和 pitch 上 — modulation。
''', r'''
## Common mistakes

| Symptom | Cause |
|---|---|
| The filter output is all zeros | `y[n] = prev` is missing, or sits outside the loop (wrong indentation) |
| The output is only quieter, not duller | `prev = 0.0` sits **inside** the loop and is reset every round, so nothing is "remembered" |
| It runs very slowly | Unnecessary numpy work inside the loop, or a very long sound |
| Distortion at high resonance | The peak exceeds 1; lower the gain |

Indentation has meaning in Python: indented lines belong to the loop; unindented lines run after the loop has finished.

## Exercises

**1.** Set the `onepole` cutoff to 50, 500 and 5000 and listen. **Guess first:** which is closest to the raw saw?

<details><summary>Answer</summary>

```python
for c in [50, 500, 5000]:
    display(play(onepole(saw, c)))
```
5000 is closest. The higher the cutoff, the more gets through.
</details>

**2.** Build a resonant highpass with `saw - lowpass(saw, 1500, res=0.5)`; listen and plot its spectrum.

<details><summary>Answer</summary>

```python
hp = saw - lowpass(saw, 1500, res=0.5)
play(hp, gain=0.2)
spec_plot({"highpass": hp})
```
</details>

**3.** Change the cutoff of the "whistle" in section 7 to 300 and 3000. **You should hear:** the whistle's pitch following the cutoff.

<details><summary>Answer</summary>

```python
for c in [300, 1200, 3000]:
    display(play(lowpass(noise, c, res=0.98), gain=0.15))
```
</details>

## Recap

| Max | Python |
|---|---|
| the audio engine running per sample | `for n in range(len(x)):` |
| `history` (gen~) | a variable defined outside the loop and updated inside it |
| `onepole~` | `onepole(x, cutoff)` |
| `lores~` / `svf~` | `lowpass(x, cutoff, res)` |
| `noise~` | `rng.uniform(-1, 1, n)` |
| `spectroscope~` | `spec_plot({...})` |

**The rule:** no feedback → compute whole arrays at once. Feedback → you need a loop.

**Next episode:** patching envelopes and LFOs into cutoff and pitch — modulation.
'''),
    ])
