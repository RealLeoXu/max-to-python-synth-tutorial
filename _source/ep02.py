from common import *

EP = dict(
    zh_file="02_phasor_phase与基本波形",
    en_file="02_phasor_phase_and_basic_waveforms",
    cells=[
        M(r'''
# 第 2 集 — `phasor~`:phase 与基本波形

⏱ 约 25 分钟

**这一集控制的音乐元素:timbre(音色)。** pitch 和时长不变。

**Max 里的对应 patch:** `phasor~ 110`,后面接不同的东西把斜线变成不同波形。

**你会听到:** 同一个音高(A2)的多种音色 — sine、saw、square、triangle,然后是可以调 "宽度" 的 pulse,以及一种用 "扭曲 phase" 做出来的变亮效果。

**学完你能做到:**
- 解释 phase 是什么,以及它为什么等于 `phasor~`
- 用同一个 phase 做出四种基本波形
- 调 pulse width,做出从空心到尖细的音色
- 知道 aliasing 是什么、什么时候会出现
''', r'''
# Episode 2 — `phasor~`: Phase and Basic Waveforms

⏱ About 25 minutes

**Musical element this episode controls: timbre.** Pitch and duration stay the same.

**The equivalent Max patch:** `phasor~ 110`, followed by different objects that reshape the ramp.

**What you will hear:** several timbres at the same pitch (A2) — sine, saw, square, triangle, then a pulse with adjustable "width", and a brightening effect made by "bending the phase".

**By the end you can:**
- explain what phase is and why it equals `phasor~`
- build four basic waveforms from one phase
- change pulse width, from hollow to thin and nasal
- say what aliasing is and when it shows up
'''),
        M(TOOLBOX_ZH + "\n\n`play` 和 `scope` 是第 1 集做的。", TOOLBOX_EN + "\n\n`play` and `scope` come from Episode 1."),
        C(BASE + r'''
freq = 110
dur = 2.0
t = np.arange(int(sr * dur)) / sr
'''),
        M(r'''
## 1. 一个新运算:`%`

`%` 读作 "mod",意思是 **除完以后剩下多少**。

- `7 % 3` → 7 里面有两个 3,剩 1
- `2.75 % 1` → 2.75 里面有两个 1,剩 0.75

所以 **`% 1` 就是 "只留小数部分"**。Max 里对应的 object 是 `%~`(或 `wrap~ 0 1`)。

运行下面这格。注意最后一行:`% 1` 对 array 也是整串一起算。
''', r'''
## 1. A new operation: `%`

`%` is read "mod" and means **what is left over after dividing**.

- `7 % 3` → 7 holds two 3s, leaving 1
- `2.75 % 1` → 2.75 holds two 1s, leaving 0.75

So **`% 1` means "keep only the fractional part"**. The Max object is `%~` (or `wrap~ 0 1`).

Run the cell. Note the last line: `% 1` also works on a whole array at once.
'''),
        C(r'''
print("7 % 3     =", 7 % 3)
print("2.75 % 1  =", 2.75 % 1)

counting_up = np.array([0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25])
print("before    =", counting_up)
print("after % 1 =", counting_up % 1)
'''),
        M(r'''
看最后两行:上面一直往上涨;下面涨到快到 1 就跳回 0,重新开始。

## 2. phase

第 1 集里 `freq * t` 是 **"到现在为止走了几个周期"**,它会一直变大。

`(freq * t) % 1` 只留小数部分,回答的是另一个问题:**"当前这一个周期走到哪了"**。

- 0 = 这个周期刚开始
- 0.5 = 走了一半
- 快到 1 时跳回 0 = 下一个周期开始

这个东西叫 **phase**。它正是 `phasor~` 输出的那条 0→1 的斜线。
''', r'''
Look at the last two lines: the upper one keeps climbing; the lower one climbs almost to 1, jumps back to 0 and starts over.

## 2. Phase

In Episode 1, `freq * t` was **"how many cycles have elapsed so far"**, and it keeps growing.

`(freq * t) % 1` keeps only the fractional part and answers a different question: **"how far along are we inside the current cycle"**.

- 0 = this cycle just started
- 0.5 = halfway
- jumping back to 0 just before 1 = the next cycle begins

This is called **phase**. It is exactly the 0→1 ramp that `phasor~` outputs.
'''),
        C(r'''
cycles = freq * t          # [[走了几个周期,一直变大||cycles elapsed, keeps growing]]
phase = cycles % 1         # [[只留小数部分:当前这个周期走到哪了||fractional part only: where we are inside the current cycle]]

n = int(sr * 0.03)
fig, axes = plt.subplots(2, 1, figsize=(9, 4.5), sharex=True)
axes[0].plot(t[:n], cycles[:n])
axes[0].set_ylabel("freq * t")
axes[0].set_title("cycles elapsed (keeps growing)")
axes[1].plot(t[:n], phase[:n])
axes[1].set_ylabel("phase")
axes[1].set_title("phase = (freq * t) % 1   (same as phasor~)")
axes[1].set_xlabel("time (s)")
plt.tight_layout()
plt.show()
'''),
        M(r'''
上图一路爬到 3.3(0.03 秒走了 3.3 个周期)。下图是同一件事,只是每满 1 就归零。

### phase 的速度 = pitch

`phasor~ 110` 每秒从 0 走到 1 一共 110 次。`phasor~ 220` 是 220 次。斜线越陡,pitch 越高。

**先猜再运行:** 220 Hz 的 phase 在同样 0.03 秒内有几条斜线?
''', r'''
The upper plot climbs to 3.3 (3.3 cycles in 0.03 seconds). The lower plot is the same thing, reset to zero each time it reaches 1.

### The speed of phase = pitch

`phasor~ 110` runs from 0 to 1 a total of 110 times per second. `phasor~ 220` does it 220 times. The steeper the ramp, the higher the pitch.

**Guess before running:** how many ramps does a 220 Hz phase show in the same 0.03 seconds?
'''),
        C(r'''
plt.figure(figsize=(9, 3))
plt.plot(t[:n], phase[:n], label="110 Hz")
plt.plot(t[:n], ((220 * t) % 1)[:n], label="220 Hz", alpha=0.7)
plt.xlabel("time (s)")
plt.ylabel("phase")
plt.legend()
plt.show()
'''),
        M(r'''
答案:6.6 条,正好是 110 Hz 的两倍。

**phase 能直接听吗?** 可以,它本身就是一个波形(一条不断重复的斜线)。但它在 0 到 1 之间,不是以 0 为中心的,所以先别急着播,下面第 2 个波形会把它处理好。

## 3. 把 phase 变成波形

核心想法:

- **phase 决定 pitch**(每秒走几遍)
- **把 phase 变成什么形状,决定 timbre**

下面四种波形用的是 **同一个 `phase`**。

### 3.1 sine

Max:`phasor~` → `cycle~` 的右 inlet(phase inlet)。

**应该听到:** 和第 1 集一样的干净 "嗡"。
''', r'''
Answer: 6.6, exactly twice as many as at 110 Hz.

**Can you listen to phase directly?** Yes; it is a waveform itself (a repeating ramp). But it sits between 0 and 1 rather than centred on 0, so hold on: waveform 2 below takes care of that.

## 3. Turning phase into waveforms

The core idea:

- **phase sets the pitch** (how many runs per second)
- **the shape you turn phase into sets the timbre**

All four waveforms below use **the same `phase`**.

### 3.1 sine

Max: `phasor~` → right inlet (phase inlet) of `cycle~`.

**You should hear:** the same clean hum as in Episode 1.
'''),
        C(r'''
x_sine = np.sin(2 * np.pi * phase)

scope(x_sine, "sine")
play(x_sine)
'''),
        M(r'''
### 3.2 saw

phase 本身就是斜线。只需要把 0→1 拉伸到 -1→1:

- `2 * phase` → 0 到 2
- `- 1` → -1 到 1

Max:`phasor~` → `*~ 2` → `-~ 1`。

**应该听到:** 同一个音高,明亮、带毛刺的 "滋——"。
''', r'''
### 3.2 saw

Phase already is a ramp. Just stretch 0→1 to -1→1:

- `2 * phase` → 0 to 2
- `- 1` → -1 to 1

Max: `phasor~` → `*~ 2` → `-~ 1`.

**You should hear:** the same pitch, bright and buzzy.
'''),
        C(r'''
x_saw = 2 * phase - 1      # [[0..1 → 0..2 → -1..1||0..1 → 0..2 → -1..1]]

scope(x_saw, "saw")
play(x_saw)
'''),
        M(r'''
### 3.3 square

规则:phase 在前半个周期(小于 0.5)输出 1,后半个周期输出 -1。

`np.where(条件, A, B)`:条件成立的位置填 A,不成立的位置填 B。还是整串一起算。

Max:`phasor~` → `<~ 0.5`,再缩放到 ±1。

**应该听到:** 空心、像老游戏机的 "嘟——"。
''', r'''
### 3.3 square

The rule: output 1 during the first half of the cycle (phase below 0.5), -1 during the second half.

`np.where(condition, A, B)`: put A where the condition holds, B where it does not. Still the whole array at once.

Max: `phasor~` → `<~ 0.5`, then scale to ±1.

**You should hear:** a hollow tone, like an old game console.
'''),
        C(r'''
# [[phase < 0.5 的位置填 1.0,其余位置填 -1.0||1.0 where phase < 0.5, -1.0 everywhere else]]
x_square = np.where(phase < 0.5, 1.0, -1.0)

scope(x_square, "square")
play(x_square)
'''),
        M(r'''
### 3.4 triangle

分三步看:

- `phase - 0.5` → -0.5 到 0.5 的斜线
- `np.abs(...)` → 取绝对值,负的一半翻上来,变成 "V" 形(0.5 → 0 → 0.5)
- `4 * ... - 1` → 拉伸到 -1 到 1

Max:`phasor~` → `-~ 0.5` → `abs~` → `*~ 4` → `-~ 1`。

**应该听到:** 柔和,只比 sine 亮一点点。
''', r'''
### 3.4 triangle

In three steps:

- `phase - 0.5` → a ramp from -0.5 to 0.5
- `np.abs(...)` → absolute value; the negative half flips up into a "V" (0.5 → 0 → 0.5)
- `4 * ... - 1` → stretch to -1 ... 1

Max: `phasor~` → `-~ 0.5` → `abs~` → `*~ 4` → `-~ 1`.

**You should hear:** soft, only slightly brighter than the sine.
'''),
        C(r'''
# [[phase - 0.5:-0.5..0.5 的斜线 → abs:V 形 0.5..0..0.5 → ×4 再 -1:拉伸到 1..-1..1||phase - 0.5: ramp -0.5..0.5 → abs: a V, 0.5..0..0.5 → ×4 then -1: stretched to 1..-1..1]]
x_tri = 4 * np.abs(phase - 0.5) - 1

scope(x_tri, "triangle")
play(x_tri)
'''),
        M(r'''
### 四个放在一起

从暗到亮排一下:sine → triangle → square → saw。**波形里的拐角越尖、跳变越多,声音越亮。**
''', r'''
### All four together

From dark to bright: sine → triangle → square → saw. **The sharper the corners and the more jumps in a waveform, the brighter it sounds.**
'''),
        C(r'''
fig, axes = plt.subplots(4, 1, figsize=(9, 6), sharex=True)
for ax, sig, name in zip(axes, [x_sine, x_tri, x_square, x_saw],
                         ["sine", "triangle", "square", "saw"]):
    ax.plot(t[:n], sig[:n])
    ax.set_ylabel(name)
axes[-1].set_xlabel("time (s)")
plt.show()
'''),
        M(r'''
## 4. Pulse width

square 的规则是 "phase 小于 **0.5** 时输出 1"。把 0.5 换成别的数,就改变了 "高" 的部分占一个周期的多少。这个数叫 **pulse width**。

- `width = 0.5` → square,空心
- `width = 0.25` → 更薄
- `width = 0.05` → 很细、很鼻音

**应该听到:** 三个同音高的音,从空心逐渐变得尖细、像簧片乐器。
''', r'''
## 4. Pulse width

The square's rule was "output 1 while phase is below **0.5**". Replace 0.5 with another number and you change how much of each cycle is "high". That number is the **pulse width**.

- `width = 0.5` → square, hollow
- `width = 0.25` → thinner
- `width = 0.05` → very thin and nasal

**You should hear:** three tones at the same pitch, going from hollow to thin and reedy.
'''),
        C(r'''
def pulse(phase, width):
    # [[width = 一个周期里 "高" 的部分占多少||width = the fraction of each cycle that is "high"]]
    return np.where(phase < width, 1.0, -1.0)

for width in [0.5, 0.25, 0.05]:
    scope(pulse(phase, width), f"pulse, width = {width}")
    display(play(pulse(phase, width)))
'''),
        M(r'''
这里出现了第一个循环:`for width in [0.5, 0.25, 0.05]:` 的意思是 "让 `width` 依次等于这三个数,每次执行一遍下面缩进的内容"。在 Max 里你会复制三份 patch;这里是同一段代码跑三遍。

## 5. 扭曲 phase

到目前为止的流程是:phase → 形状。

也可以在中间加一步:**先把 phase 本身变形,再交给 sine。** 这叫 phase distortion(Casio CZ 系列 synth 的做法)。

`phase ** 3` 是 phase 的三次方。0 还是 0,1 还是 1,但中间被压低了:前大半个周期走得很慢,最后一小段冲得很快。

**应该听到:** 三个音,第一个是普通 sine,后两个越来越亮、越来越 "咬"。pitch 不变。
''', r'''
The first loop has appeared: `for width in [0.5, 0.25, 0.05]:` means "let `width` be each of these three numbers in turn, running the indented lines each time". In Max you would copy the patch three times; here the same code runs three times.

## 5. Bending the phase

So far the flow was: phase → shape.

You can add a step in between: **reshape the phase itself, then hand it to the sine.** This is phase distortion (the method of the Casio CZ synths).

`phase ** 3` is phase cubed. 0 stays 0 and 1 stays 1, but the middle is pushed down: most of the cycle moves slowly and the last stretch rushes.

**You should hear:** three tones — a plain sine, then two that get brighter and more "biting". The pitch does not change.
'''),
        C(r'''
fig, axes = plt.subplots(1, 2, figsize=(10, 3))
for power in [1, 2, 4]:
    bent = phase ** power          # [[0 和 1 不变,中间被压低:前面走得慢,最后冲得快||0 and 1 stay put, the middle sags: slow at first, rushing at the end]]
    axes[0].plot(t[:n], bent[:n], label=f"phase ** {power}")
    axes[1].plot(t[:n], np.sin(2 * np.pi * bent)[:n], label=f"power {power}")
axes[0].set_title("bent phase")
axes[1].set_title("sine of bent phase")
axes[0].legend()
plt.show()

for power in [1, 2, 4]:
    display(play(np.sin(2 * np.pi * phase ** power)))
'''),
        M(r'''
## 6. 两个 phase 小技巧

### 高一个八度

`(phase * 2) % 1`:把 phase 乘 2(0→2),再 `% 1`(变成两条 0→1 的斜线)。一个周期里走了两遍 → 高一个八度。

**应该听到:** 先是原来的 saw,然后是高八度的 saw。
''', r'''
## 6. Two phase tricks

### One octave up

`(phase * 2) % 1`: multiply phase by 2 (0→2), then `% 1` (two 0→1 ramps). Two runs per cycle → one octave higher.

**You should hear:** the original saw, then a saw an octave higher.
'''),
        C(r'''
phase_up = (phase * 2) % 1     # [[一个周期里走两遍 0→1 = 高一个八度||two 0→1 runs per cycle = one octave up]]

display(play(2 * phase - 1))
display(play(2 * phase_up - 1))
'''),
        M(r'''
### Phase offset

`(phase + 0.25) % 1`:让整个周期提前四分之一开始。

**应该听到:** 两个音听起来 **完全一样**。单独一个 oscillator 的 phase offset 是听不出来的;它只有在和别的声音叠加时才有影响。

**应该看到:** 第二条线形状相同,只是往左平移了四分之一个周期。
''', r'''
### Phase offset

`(phase + 0.25) % 1`: start the whole cycle a quarter earlier.

**You should hear:** two tones that sound **exactly the same**. The phase offset of a single oscillator is inaudible; it only matters once it is mixed with other sounds.

**You should see:** the second curve has the same shape, shifted left by a quarter cycle.
'''),
        C(r'''
phase_shift = (phase + 0.25) % 1     # [[提前四分之一个周期;% 1 让超过 1 的部分绕回去||a quarter cycle early; % 1 wraps whatever passes 1]]

plt.figure(figsize=(9, 2.5))
plt.plot(t[:n], np.sin(2 * np.pi * phase)[:n], label="offset 0")
plt.plot(t[:n], np.sin(2 * np.pi * phase_shift)[:n], label="offset 0.25")
plt.legend()
plt.xlabel("time (s)")
plt.show()

display(play(np.sin(2 * np.pi * phase)))
display(play(np.sin(2 * np.pi * phase_shift)))
'''),
        M(r'''
## 7. Aliasing:这些波形的一个问题

saw 和 square 里有 "瞬间跳变"。跳变意味着包含非常高的频率 — 理论上无限高。

但 sample rate 是 44100,它最高只能表示到 22050 Hz。超出的频率不会消失,而是 **折回来**,变成一些和音高无关的杂音。这叫 aliasing。

音低的时候听不太出来。音高的时候很明显。

**应该听到:**
1. 2500 Hz 的 sine — 干净的高音
2. 2500 Hz 的 saw — 除了高音之外,底下还多出一些不和谐的、偏低的杂音

(音量调小了,高频比较刺耳。)
''', r'''
## 7. Aliasing: a problem with these waveforms

A saw and a square contain "instant jumps". A jump implies very high frequencies — in theory infinitely high.

But the sample rate is 44100, which can represent nothing above 22050 Hz. Frequencies beyond that do not vanish; they **fold back** as tones unrelated to the pitch. This is aliasing.

At low pitches it is hard to hear. At high pitches it is obvious.

**You should hear:**
1. a 2500 Hz sine — a clean high tone
2. a 2500 Hz saw — the high tone plus some dissonant, lower junk tones underneath

(The level is reduced; high frequencies are harsh.)
'''),
        C(r'''
phase_hi = (2500 * t) % 1

display(play(np.sin(2 * np.pi * phase_hi), gain=0.1))
display(play(2 * phase_hi - 1, gain=0.1))
'''),
        M(r'''
在 Max 里直接拿 `phasor~` 当 saw 用,也有完全一样的问题;`saw~` 和 `rect~` 就是为了解决它而存在的(它们是 band-limited 的)。

下一集的 wavetable 会用另一种方式解决:表里只放有限个 harmonic。

## 常见错误

| 现象 | 原因 |
|---|---|
| 直接播放 `phase`,听起来偏一边 / 有 "噗" 声 | phase 在 0 到 1 之间,不以 0 为中心。用 `2 * phase - 1` |
| `np.where` 报错 | 三个东西都要给:条件、成立时的值、不成立时的值 |
| 忘了 `% 1` | `np.sin` 不受影响(它自己会绕回来),但 saw、square 会完全错掉 |

## 练习

**1.** 做一个 width 为 0.1 的 pulse,音高 220 Hz。

<details><summary>答案</summary>

```python
p220 = (220 * t) % 1
play(pulse(p220, 0.1))
```
</details>

**2.** 做一个 "半波 sine":sine 大于 0 的部分保留,小于 0 的部分变成 0。提示:`np.maximum(a, 0)` 会把 `a` 里所有负数换成 0。**先猜:** 比 sine 亮还是暗?

<details><summary>答案</summary>

```python
half = np.maximum(np.sin(2 * np.pi * phase), 0)
scope(half, "half-wave sine")
play(half)
```
更亮。波形里多了拐角。
</details>

**3.** 用第 6 节的技巧做一个高 **两个** 八度的 saw。

<details><summary>答案</summary>

```python
play(2 * ((phase * 4) % 1) - 1)
```
高一个八度是乘 2,高两个八度是乘 4。
</details>

## 小结

| Max | Python |
|---|---|
| `phasor~ 110` | `(110 * t) % 1` |
| `%~ 1` / `wrap~ 0 1` | `% 1` |
| `<~ 0.5` | `phase < 0.5` |
| `selector~` / `?` | `np.where(cond, a, b)` |
| `abs~` | `np.abs(...)` |
| `pow~` | `**` |
| 复制三份 patch | `for ... in [...]:` |

- pitch 由 phase 的速度决定
- timbre 由 "phase → 形状" 的那一步决定
- 有跳变的波形在高音区会 aliasing

**下一集:** 形状不再用公式写,而是存进一张表里读出来 — wavetable。
''', r'''
Using a raw `phasor~` as a saw in Max has exactly the same problem; `saw~` and `rect~` exist to solve it (they are band-limited).

Next episode's wavetable solves it another way: the table only contains a limited number of harmonics.

## Common mistakes

| Symptom | Cause |
|---|---|
| Playing `phase` directly sounds lopsided / thumps | Phase sits between 0 and 1, not centred on 0. Use `2 * phase - 1` |
| `np.where` raises an error | It needs all three: the condition, the value if true, the value if false |
| Forgot `% 1` | `np.sin` does not care (it wraps by itself), but saw and square break completely |

## Exercises

**1.** Make a pulse of width 0.1 at 220 Hz.

<details><summary>Answer</summary>

```python
p220 = (220 * t) % 1
play(pulse(p220, 0.1))
```
</details>

**2.** Make a "half-wave sine": keep the sine where it is above 0, and output 0 where it is below. Hint: `np.maximum(a, 0)` replaces every negative number in `a` with 0. **Guess first:** brighter or darker than a sine?

<details><summary>Answer</summary>

```python
half = np.maximum(np.sin(2 * np.pi * phase), 0)
scope(half, "half-wave sine")
play(half)
```
Brighter. The waveform gained corners.
</details>

**3.** Use the trick from section 6 to make a saw **two** octaves higher.

<details><summary>Answer</summary>

```python
play(2 * ((phase * 4) % 1) - 1)
```
One octave up is times 2, two octaves up is times 4.
</details>

## Recap

| Max | Python |
|---|---|
| `phasor~ 110` | `(110 * t) % 1` |
| `%~ 1` / `wrap~ 0 1` | `% 1` |
| `<~ 0.5` | `phase < 0.5` |
| `selector~` / `?` | `np.where(cond, a, b)` |
| `abs~` | `np.abs(...)` |
| `pow~` | `**` |
| copying a patch three times | `for ... in [...]:` |

- pitch comes from how fast phase runs
- timbre comes from the "phase → shape" step
- waveforms with jumps alias at high pitches

**Next episode:** no more formulas for the shape; store it in a table and read it back — the wavetable.
'''),
    ])
