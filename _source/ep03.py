from common import *

EP = dict(
    zh_file="03_buffer与wave_wavetable_oscillator",
    en_file="03_buffer_and_wave_wavetable_oscillator",
    cells=[
        M(r'''
# 第 3 集 — `buffer~` + `wave~`:wavetable oscillator

⏱ 约 30 分钟

**这一集控制的音乐元素:timbre(音色),而且是你自己设计的音色。**

**Max 里的对应 patch:** 一个存了单周期波形的 `buffer~`,`phasor~` → `wave~` 去读它。

**你会听到:**
1. 一个像小风琴的音(3 个 harmonic 叠在一起)
2. 改 harmonic 的比例后,同一个音高变得更亮、更暗、更空心
3. 一个你 "手画" 出来的波形

**学完你能做到:**
- 用叠 harmonic 的方式做一张 wavetable
- 用 phase 读表,并解释 interpolation 为什么需要
- 设计自己的音色
- 解释 wavetable 怎么避开上一集的 aliasing
''', r'''
# Episode 3 — `buffer~` + `wave~`: the Wavetable Oscillator

⏱ About 30 minutes

**Musical element this episode controls: timbre — a timbre you design yourself.**

**The equivalent Max patch:** a `buffer~` holding one cycle of a waveform, read by `phasor~` → `wave~`.

**What you will hear:**
1. a small-organ-like tone (3 harmonics stacked)
2. the same pitch getting brighter, darker or more hollow as the harmonic mix changes
3. a waveform you "draw by hand"

**By the end you can:**
- build a wavetable by stacking harmonics
- read a table with phase, and explain why interpolation is needed
- design your own timbres
- explain how a wavetable sidesteps last episode's aliasing
'''),
        M(TOOLBOX_ZH, TOOLBOX_EN),
        C(BASE + r'''
freq = 110
dur = 2.0
t = np.arange(int(sr * dur)) / sr
phase = (freq * t) % 1
'''),
        M(r'''
## 1. 想法

上一集:phase → **公式** → 波形。

这一集:phase → **查表** → 波形。

表里存的是 **一个周期的波形**。phase 说 "现在走到这个周期的 30%",我们就去表的 30% 那个位置把数读出来。

好处:表里可以放 **任何形状**,不需要能写成公式。

## 2. 做一张表:叠 harmonic

表有 `N = 2048` 个位置。`p` 是每个位置对应的 phase(0 到 1) — 做法和第 1 集的 `t` 一模一样,只是这次不是 "第几秒",而是 "一个周期里的第几成"。

**harmonic** 是基音的整数倍:

- 第 1 harmonic:在一张表里走完 **1** 个周期
- 第 2 harmonic:走完 **2** 个周期
- 第 3 harmonic:走完 **3** 个周期

先分别做出来看看。
''', r'''
## 1. The idea

Last episode: phase → **formula** → waveform.

This episode: phase → **table lookup** → waveform.

The table stores **one cycle of a waveform**. Phase says "we are 30% into this cycle", so we go to the 30% position of the table and read the number there.

The benefit: the table can hold **any shape**; it need not be expressible as a formula.

## 2. Making a table: stacking harmonics

The table has `N = 2048` positions. `p` is the phase (0 to 1) of each position — built exactly like `t` in Episode 1, except it is not "which second" but "what fraction of one cycle".

A **harmonic** is a whole-number multiple of the fundamental:

- harmonic 1: completes **1** cycle across the table
- harmonic 2: completes **2** cycles
- harmonic 3: completes **3** cycles

Build each one separately first.
'''),
        C(r'''
N = 2048
p = np.arange(N) / N                 # [[表里每个位置的 phase:0, 1/2048, 2/2048 ...||the phase of each table position: 0, 1/2048, 2/2048 ...]]

h1 = np.sin(2 * np.pi * 1 * p)
h2 = np.sin(2 * np.pi * 2 * p)
h3 = np.sin(2 * np.pi * 3 * p)

fig, axes = plt.subplots(3, 1, figsize=(9, 4.5), sharex=True)
for ax, h, name in zip(axes, [h1, h2, h3], ["harmonic 1", "harmonic 2", "harmonic 3"]):
    ax.plot(h)
    ax.set_ylabel(name)
axes[-1].set_xlabel("table index (0 to 2047)")
plt.show()
'''),
        M(r'''
现在各乘一个音量,加起来。这和第 1 集做和弦是同一个操作(`+` = mixing),只是这次加的是 harmonic。

- 第 1 harmonic 音量 1
- 第 2 harmonic 音量 0.5
- 第 3 harmonic 音量 0.3
''', r'''
Now scale each by a level and add them. It is the same operation as the chord in Episode 1 (`+` = mixing), only this time we add harmonics.

- harmonic 1 at level 1
- harmonic 2 at level 0.5
- harmonic 3 at level 0.3
'''),
        C(r'''
table = 1.0 * h1 + 0.5 * h2 + 0.3 * h3

plt.figure(figsize=(9, 3))
plt.plot(table)
plt.xlabel("table index (0 to 2047)")
plt.ylabel("amplitude")
plt.title("the table: one cycle, three harmonics added")
plt.show()

print("max amplitude:", np.max(np.abs(table)))
'''),
        M(r'''
最大振幅超过 1 了。把整张表除以它自己的最大值,峰值就正好是 1。这叫 **normalize**(Max 里对 `buffer~` 发 `normalize 1`)。

### 包成函数

`harmonic_amps` 是一个 list,比如 `[1, 0.5, 0.3]`,依次是第 1、2、3…… harmonic 的音量。

`for k, amp in enumerate(harmonic_amps, start=1):` 的意思是:依次取出 list 里的每个音量 `amp`,同时 `k` 从 1 开始数(1, 2, 3 …)。所以每一轮就是 "把第 `k` 个 harmonic 以音量 `amp` 加进表里"。
''', r'''
The maximum amplitude exceeds 1. Divide the whole table by its own maximum and the peak is exactly 1. This is **normalizing** (in Max: send `normalize 1` to `buffer~`).

### Wrap it in a function

`harmonic_amps` is a list such as `[1, 0.5, 0.3]`: the levels of harmonics 1, 2, 3 ... in order.

`for k, amp in enumerate(harmonic_amps, start=1):` means: take each level `amp` from the list in turn while `k` counts from 1 (1, 2, 3 ...). Each round is therefore "add harmonic `k` at level `amp` to the table".
'''),
        C(TABLE + r'''
table = make_table([1, 0.5, 0.3])
print("length:", len(table), "  max amplitude:", np.max(np.abs(table)))
'''),
        M(r'''
## 3. 读表:先用小数字

假设一张只有 8 个位置的表,里面的数故意写得很好认。

- `ph * 8` → phase 对应表的哪个位置
- `.astype(int)` → 砍掉小数,变成整数编号

然后是 numpy 的一个关键用法:**方括号里放一整串编号,就一次取出一整串数。**
''', r'''
## 3. Reading the table: small numbers first

Take a table with only 8 positions, filled with numbers that are easy to recognise.

- `ph * 8` → which table position the phase points at
- `.astype(int)` → chop off the decimals to get a whole-number index

Then a key numpy move: **put a whole array of indices in the brackets and you get a whole array of values back.**
'''),
        C(r'''
tiny_table = np.array([0, 10, 20, 30, 40, 50, 60, 70])
ph = np.array([0.0, 0.25, 0.5, 0.9])

position = ph * len(tiny_table)      # [[phase 0..1 → 表的位置 0..8||phase 0..1 → table position 0..8]]
ix = position.astype(int)            # [[砍掉小数,得到可以用的编号||drop the decimals to get a usable index]]

print("phase       :", ph)
print("position    :", position)
print("index       :", ix)
print("values read :", tiny_table[ix])
'''),
        M(r'''
读一下:phase 0.25 → 位置 2 → 读到 20。phase 0.9 → 位置 7.2 → 砍成 7 → 读到 70。

## 4. 读真正的表

一样的两行。`idx` 有 88200 个编号,所以 `table[idx]` 就是 88200 个 sample。

**应该听到:** 一个像小风琴的持续音,A2。比 sine 厚,比 saw 柔和。
''', r'''
Read it: phase 0.25 → position 2 → reads 20. Phase 0.9 → position 7.2 → chopped to 7 → reads 70.

## 4. Reading the real table

The same two lines. `idx` holds 88200 indices, so `table[idx]` is 88200 samples.

**You should hear:** a sustained small-organ-like tone at A2. Thicker than a sine, softer than a saw.
'''),
        C(r'''
idx = (phase * N).astype(int)        # [[每个 sample 该读表的哪个位置||which table position each sample should read]]
x = table[idx]                       # [[一次把 88200 个位置的值全取出来||fetch the values at all 88200 positions at once]]

print("phase[:4] =", phase[:4])
print("idx[:4]   =", idx[:4])

scope(x, "table read by phase")
play(x)
'''),
        M(r'''
图里的形状和上面那张表一样,只是在 0.03 秒里重复了 3.3 遍。**phase 决定读表的速度(pitch),表里的形状决定 timbre。**

Max 里这一步是 `index~`(不插值)。

## 5. Interpolation(插值)

`phase * N` 通常不是整数。上面直接砍掉小数,等于 "读最近的左边那个位置"。

表有 2048 个位置时,误差很小,几乎听不出来。为了让问题变明显,故意用一张 **只有 16 个位置** 的 sine 表。

**应该听到:** 一个本该干净的 sine,但带着明显的 "滋滋" 毛刺。

**应该看到:** 波形是一级一级的台阶。
''', r'''
The shape in the plot matches the table above, repeated 3.3 times in 0.03 seconds. **Phase sets how fast the table is read (pitch); the shape in the table sets the timbre.**

In Max this step is `index~` (no interpolation).

## 5. Interpolation

`phase * N` is usually not a whole number. Chopping the decimals means "read the nearest position to the left".

With 2048 positions the error is tiny and hard to hear. To make the problem obvious, use a sine table with **only 16 positions** on purpose.

**You should hear:** what should be a clean sine, with a clear buzzy fuzz on top.

**You should see:** a waveform made of stair steps.
'''),
        C(r'''
coarse = np.sin(2 * np.pi * np.arange(16) / 16)

stepped = coarse[(phase * 16).astype(int)]     # [[不插值:只读左边最近的那个位置||no interpolation: read only the nearest position on the left]]

scope(stepped, "16-point table, no interpolation", seconds=0.015)
play(stepped)
'''),
        M(r'''
解决办法:不只读左边那个,**左右两个都读,按距离混合。**

比如位置是 5.3:

- 左边是 5 号,右边是 6 号
- 离 5 号近(只差 0.3),所以 5 号占 0.7,6 号占 0.3
- 结果 = `0.7 * table[5] + 0.3 * table[6]`

代码里:

- `i0`:左边的编号
- `i1`:右边的编号。`% N` 是为了到表尾时绕回 0(最后一个位置的右边是第一个位置)
- `frac`:小数部分(上面例子里的 0.3)

这是 **linear interpolation**,`wave~` 默认就是这么读的。
''', r'''
The fix: do not read only the left position; **read both neighbours and mix them by distance.**

Say the position is 5.3:

- left is index 5, right is index 6
- it is closer to 5 (only 0.3 away), so index 5 gets 0.7 and index 6 gets 0.3
- result = `0.7 * table[5] + 0.3 * table[6]`

In the code:

- `i0`: the left index
- `i1`: the right index. `% N` wraps to 0 at the end of the table (to the right of the last position is the first)
- `frac`: the fractional part (0.3 in the example)

This is **linear interpolation**, which is how `wave~` reads by default.
'''),
        C(r'''
def osc_table(table, phase):
    N = len(table)
    pos = phase * N                            # [[带小数的位置,比如 5.3||a position with decimals, e.g. 5.3]]
    i0 = np.floor(pos).astype(int) % N         # [[左边:5||left neighbour: 5]]
    i1 = (i0 + 1) % N                          # [[右边:6(到表尾绕回 0)||right neighbour: 6 (wraps to 0 at the end)]]
    frac = pos - np.floor(pos)                 # [[小数部分:0.3||the fractional part: 0.3]]
    # [[左边占 0.7,右边占 0.3||0.7 of the left, 0.3 of the right]]
    return (1 - frac) * table[i0] + frac * table[i1]

smooth = osc_table(coarse, phase)

scope(smooth, "16-point table, linear interpolation", seconds=0.015)
play(smooth)
'''),
        M(r'''
**应该听到:** 同一张 16 点的表,毛刺基本消失了,接近干净的 sine。

**应该看到:** 台阶变成了折线。

从现在起都用 `osc_table(table, phase)`。它就是我们的 `wave~`。
''', r'''
**You should hear:** the same 16-point table, with the fuzz mostly gone and close to a clean sine.

**You should see:** the stair steps have turned into straight segments.

From now on we always use `osc_table(table, phase)`. It is our `wave~`.
'''),
        C(r'''
x = osc_table(table, phase)
play(x)
'''),
        M(r'''
## 6. 设计音色

换表,pitch 不变,timbre 变。

`[1 / k for k in range(1, 17)]` 是一种简写,意思是 "让 `k` 从 1 数到 16,每次算 `1 / k`,把结果排成一个 list":`[1, 1/2, 1/3, ... 1/16]`。

**应该听到四个音:**

1. `dark`:只有基音 → 就是 sine
2. `bright`:16 个 harmonic,音量按 1/k 递减 → 接近 saw
3. `hollow`:只有奇数 harmonic(1、3、5、7…) → 接近 square,空心
4. `nasal`:高次 harmonic 比低次响 → 很薄、很鼻音
''', r'''
## 6. Designing timbres

Swap the table: pitch stays, timbre changes.

`[1 / k for k in range(1, 17)]` is shorthand for "let `k` count from 1 to 16, compute `1 / k` each time and collect the results in a list": `[1, 1/2, 1/3, ... 1/16]`.

**You should hear four tones:**

1. `dark`: fundamental only → a plain sine
2. `bright`: 16 harmonics with levels falling as 1/k → close to a saw
3. `hollow`: odd harmonics only (1, 3, 5, 7 ...) → close to a square, hollow
4. `nasal`: upper harmonics louder than lower ones → thin and nasal
'''),
        C(r'''
tables = {
    "dark":   make_table([1]),
    "bright": make_table([1 / k for k in range(1, 17)]),
    "hollow": make_table([1, 0, 1/3, 0, 1/5, 0, 1/7, 0, 1/9, 0, 1/11]),
    "nasal":  make_table([0.2, 0.3, 0.5, 0.8, 1.0, 0.8, 0.5, 0.3]),
}

fig, axes = plt.subplots(1, 4, figsize=(12, 2.5), sharey=True)
for ax, name in zip(axes, tables):
    ax.plot(tables[name])
    ax.set_title(name)
plt.show()

for name in tables:
    print(name)
    display(play(osc_table(tables[name], phase)))
'''),
        M(r'''
**规律:** harmonic 越多、高次 harmonic 越响 → 越亮。只有奇数 harmonic → 空心。

### 自己试

改下面 list 里的数字,重新运行,听变化。list 可以更长或更短。
''', r'''
**The pattern:** more harmonics, and louder upper harmonics → brighter. Odd harmonics only → hollow.

### Try your own

Edit the numbers in the list below, re-run and listen. The list can be longer or shorter.
'''),
        C(r'''
my_table = make_table([1, 0, 0.6, 0, 0.4, 0, 0.2])

scope(osc_table(my_table, phase), "my_table")
play(osc_table(my_table, phase))
'''),
        M(r'''
## 7. 手画一张表

表里可以放任何形状。这里用几个 "拐点" 连成折线,相当于在 Max 的 `waveform~` 里用鼠标画。

`np.interp(p, points_x, points_y)`:给几个 (x, y) 点,它在中间连直线,并算出 `p` 里每个位置上的高度。

注意:第一个点和最后一个点的高度要 **一样**(这里都是 0),否则每个周期接头处会有一个跳变。

**应该听到:** 一个不像任何标准波形的音色,偏亮,有点粗糙。
''', r'''
## 7. Drawing a table by hand

A table can hold any shape. Here a few "corner points" are joined by straight lines — like drawing with the mouse in Max's `waveform~`.

`np.interp(p, points_x, points_y)`: give it a few (x, y) points and it joins them with straight lines and returns the height at every position in `p`.

Note: the first and last points must have **the same** height (both 0 here), or there will be a jump where each cycle meets the next.

**You should hear:** a timbre unlike any standard waveform, fairly bright and a little rough.
'''),
        C(r'''
points_x = [0.0, 0.10, 0.35, 0.50, 0.60, 0.90, 1.0]
points_y = [0.0, 1.00, 0.20, 0.60, -0.4, -1.0, 0.0]

# [[在这些点之间连直线,算出表里 2048 个位置各自的高度||join the points with straight lines and get the height at all 2048 table positions]]
drawn = np.interp(p, points_x, points_y)

plt.figure(figsize=(9, 3))
plt.plot(p, drawn)
plt.plot(points_x, points_y, "o")
plt.xlabel("phase")
plt.title("hand-drawn table")
plt.show()

play(osc_table(drawn, phase))
'''),
        M(r'''
## 8. Wavetable 和 aliasing

上一集:2500 Hz 的朴素 saw 有 aliasing,因为它包含无限高的 harmonic。

用 `make_table` 做的表,**里面有几个 harmonic 是我们自己决定的**。只要最高的那个 harmonic 不超过 22050 Hz,就没有东西会折回来。

规则:**harmonic 数量 × 音高 < sr / 2**

2500 Hz 时:22050 / 2500 = 8.8,所以最多放 8 个 harmonic。

**应该听到:**
1. 朴素 saw(上一集的):高音 + 底下的杂音
2. 8 个 harmonic 的表:同样亮的高音,但底下干净了
''', r'''
## 8. Wavetables and aliasing

Last episode: a naive 2500 Hz saw aliased because it contains infinitely high harmonics.

With a table built by `make_table`, **we decide how many harmonics it contains**. As long as the highest one stays below 22050 Hz, nothing folds back.

The rule: **number of harmonics × pitch < sr / 2**

At 2500 Hz: 22050 / 2500 = 8.8, so at most 8 harmonics.

**You should hear:**
1. the naive saw (from last episode): the high tone plus junk underneath
2. the 8-harmonic table: an equally bright high tone, but clean underneath
'''),
        C(r'''
phase_hi = (2500 * t) % 1
saw8 = make_table([1 / k for k in range(1, 9)])     # [[8 个 harmonic:最高 8 × 2500 = 20000 Hz < 22050||8 harmonics: the highest is 8 × 2500 = 20000 Hz < 22050]]

display(play(2 * phase_hi - 1, gain=0.1))
display(play(osc_table(saw8, phase_hi), gain=0.1))
'''),
        M(r'''
反过来说:同一张表,音弹得越高,越容易超出这个规则。真正的 wavetable synth(包括 Serum)会为不同音区准备 harmonic 数量不同的几张表,自动切换。这个系列里我们把音高限制在低音和中音区,就不需要这一步。

## 常见错误

| 现象 | 原因 |
|---|---|
| `IndexError: index 2048 is out of bounds` | 编号超出了表。读右边那个位置时忘了 `% N` |
| `only integer ... arrays are valid indices` | 方括号里放了带小数的数。先 `.astype(int)` |
| 音色里有持续的 "嗒嗒" 或毛刺 | 表的头和尾接不上(手画表时首尾高度不同) |
| 高音区有杂音 | harmonic 太多,超过了 sr / 2 |

## 练习

**1.** 做一张只有第 1 和第 5 harmonic 的表(音量都是 1)。**先猜:** 会听到一个音还是两个音?

<details><summary>答案</summary>

```python
play(osc_table(make_table([1, 0, 0, 0, 1]), phase))
```
听起来像两个音:基音 A2,加上一个高两个八度又一个大三度的音(550 Hz)。harmonic 隔得远、又一样响时,耳朵会把它们分开听。
</details>

**2.** 把 `bright` 那张表的 harmonic 数量从 16 改成 4,再改成 40。**应该听到:** 4 个时较暗,40 个时更亮更像 saw。

<details><summary>答案</summary>

```python
for count in [4, 16, 40]:
    display(play(osc_table(make_table([1 / k for k in range(1, count + 1)]), phase)))
```
</details>

**3.** 110 Hz 时,一张表最多能放多少个 harmonic 而不 aliasing?

<details><summary>答案</summary>

22050 / 110 = 200.45,所以最多 200 个。低音区几乎不用担心。
</details>

## 小结

| Max | Python |
|---|---|
| `buffer~`(单周期波形) | `table`(长度 2048 的 array) |
| `normalize 1` | `table / np.max(np.abs(table))` |
| `index~`(不插值) | `table[idx]` |
| `wave~`(线性插值) | `osc_table(table, phase)` |
| `waveform~` 里手画 | `np.interp(p, points_x, points_y)` |

- phase 决定读表的速度 → pitch
- 表里的形状 → timbre
- 表里的 harmonic 数量由你决定 → 可以避开 aliasing

**下一集:** 不只一张表,而是一叠表,在它们之间滑动 — Serum 的 WT POS 旋钮。
''', r'''
Put the other way round: the higher you play one table, the sooner it breaks this rule. Real wavetable synths (Serum included) keep several versions of a table with different harmonic counts for different registers and switch automatically. In this series we stay in the bass and mid range, so we skip that step.

## Common mistakes

| Symptom | Cause |
|---|---|
| `IndexError: index 2048 is out of bounds` | The index ran past the table. `% N` was forgotten when reading the right neighbour |
| `only integer ... arrays are valid indices` | A number with decimals went into the brackets. Use `.astype(int)` first |
| A constant ticking or fuzz in the tone | The table's start and end do not meet (different heights in a hand-drawn table) |
| Junk tones at high pitches | Too many harmonics, exceeding sr / 2 |

## Exercises

**1.** Make a table with only harmonics 1 and 5 (both at level 1). **Guess first:** will you hear one note or two?

<details><summary>Answer</summary>

```python
play(osc_table(make_table([1, 0, 0, 0, 1]), phase))
```
It sounds like two notes: the fundamental A2 plus a tone two octaves and a major third above (550 Hz). When harmonics are far apart and equally loud, the ear separates them.
</details>

**2.** Change the harmonic count of the `bright` table from 16 to 4, then to 40. **You should hear:** darker with 4, brighter and more saw-like with 40.

<details><summary>Answer</summary>

```python
for count in [4, 16, 40]:
    display(play(osc_table(make_table([1 / k for k in range(1, count + 1)]), phase)))
```
</details>

**3.** At 110 Hz, how many harmonics can a table hold without aliasing?

<details><summary>Answer</summary>

22050 / 110 = 200.45, so at most 200. In the bass range it is hardly a concern.
</details>

## Recap

| Max | Python |
|---|---|
| `buffer~` (single-cycle waveform) | `table` (an array of length 2048) |
| `normalize 1` | `table / np.max(np.abs(table))` |
| `index~` (no interpolation) | `table[idx]` |
| `wave~` (linear interpolation) | `osc_table(table, phase)` |
| drawing in `waveform~` | `np.interp(p, points_x, points_y)` |

- phase sets how fast the table is read → pitch
- the shape in the table → timbre
- you decide how many harmonics the table holds → aliasing can be avoided

**Next episode:** not one table but a stack of them, and sliding between them — Serum's WT POS knob.
'''),
    ])
