from common import *

EP = dict(
    zh_file="05_adsr_envelope",
    en_file="05_adsr_envelope",
    cells=[
        M(r'''
# 第 5 集 — `adsr~`:envelope

⏱ 约 25 分钟

**这一集控制的音乐元素:音量随时间的形状(articulation)** — 一个音是 "弹" 出来的还是 "推" 出来的。

**Max 里的对应 patch:** `adsr~` → `*~`。

**你会听到:**
1. 同一个音色、同一个音高,三种 "手感":pluck、pad、organ
2. 没有 envelope 时的 "咔" 一声,以及它是怎么被消掉的
3. 一段 8 个音的 bassline

**学完你能做到:**
- 解释 envelope 为什么 "也只是一个 array"
- 用 `np.interp` 连点成线
- 写出并使用 `adsr()`
- 知道 click 从哪来、怎么去掉
- 把多个带 envelope 的音接成一段 sequence
''', r'''
# Episode 5 — `adsr~`: the Envelope

⏱ About 25 minutes

**Musical element this episode controls: the shape of loudness over time (articulation)** — whether a note is "plucked" or "swelled".

**The equivalent Max patch:** `adsr~` → `*~`.

**What you will hear:**
1. one timbre and pitch with three different feels: pluck, pad, organ
2. the "click" you get without an envelope, and how it is removed
3. an 8-note bassline

**By the end you can:**
- explain why an envelope "is just another array"
- connect dots into lines with `np.interp`
- write and use `adsr()`
- say where clicks come from and how to remove them
- join several enveloped notes into a sequence
'''),
        M(TOOLBOX_ZH, TOOLBOX_EN),
        C(J(BASE, TABLE, FRAMES, r'''
frames = make_frames()

freq = 110
dur = 2.0
t = np.arange(int(sr * dur)) / sr
phase = (freq * t) % 1

osc = osc_wavetable(frames, phase, 0.6)
''')),
        M(r'''
`osc` 是一个 2 秒的、音量不变的持续音(wavetable position 0.6)。这一集所有的例子都是在它上面 "盖" 不同的 envelope。

## 1. 最简单的 envelope:fade out

envelope 就是 **一个和声音一样长的 array,值在 0 到 1 之间**。把它和声音逐个 sample 相乘(`*~`),声音在每一刻的音量就被它决定了。

最简单的一条:从 1 直线走到 0。上一集的 `np.linspace` 正好能做。

**应该听到:** 一个音从满音量开始,2 秒内均匀地淡出到无声。
''', r'''
`osc` is a steady 2-second tone (wavetable position 0.6). Every example in this episode lays a different envelope over it.

## 1. The simplest envelope: a fade-out

An envelope is **an array as long as the sound, with values between 0 and 1**. Multiply it with the sound sample by sample (`*~`) and it decides the loudness at every moment.

The simplest one: a straight line from 1 to 0. Last episode's `np.linspace` does exactly that.

**You should hear:** a note starting at full volume and fading evenly to silence over 2 seconds.
'''),
        C(r'''
fade_out = np.linspace(1, 0, len(t))

plt.figure(figsize=(9, 2.5))
plt.plot(t, osc * fade_out, linewidth=0.3)     # [[声音 × envelope||sound × envelope]]
plt.plot(t, fade_out, color="red")             # [[envelope 本身||the envelope itself]]
plt.xlabel("time (s)")
plt.show()

play(osc * fade_out)
'''),
        M(r'''
红线是 envelope;蓝色是乘完以后的声音,它的轮廓跟着红线走。"envelope"(包络)这个词就是这个意思。

## 2. 连点成线:`np.interp`

直线不够用。我们想要的是 "几段直线连起来" 的形状。

`np.interp(t, 时间点, 高度)`:给几个 (时间, 高度) 的点,它在相邻的点之间画直线,并算出 `t` 里每一刻的高度。相当于 Max 的 `function` object 接 `line~`。

下面三个点:(0 秒, 0) → (0.1 秒, 1) → (1.5 秒, 0)。也就是 0.1 秒升到顶,然后 1.4 秒降到 0。

最后一个点之后,`np.interp` 会 **一直停在最后那个高度**(这里是 0)。

**应该听到:** 一个快速出现、然后慢慢消失的音,1.5 秒后完全无声。
''', r'''
The red line is the envelope; the blue is the sound after multiplying, and its outline follows the red line. That is what the word "envelope" means.

## 2. Connecting dots: `np.interp`

A single straight line is not enough. We want shapes made of "several straight segments".

`np.interp(t, times, levels)`: give it a few (time, level) points; it draws straight lines between neighbours and returns the level at every moment in `t`. Think Max's `function` object feeding `line~`.

Three points below: (0 s, 0) → (0.1 s, 1) → (1.5 s, 0). So 0.1 seconds up to the top, then 1.4 seconds down to 0.

After the last point `np.interp` **stays at the last level** (0 here).

**You should hear:** a note that appears quickly and then fades slowly, fully silent after 1.5 seconds.
'''),
        C(r'''
points_time = [0.0, 0.1, 1.5]
points_level = [0.0, 1.0, 0.0]

env = np.interp(t, points_time, points_level)

plt.figure(figsize=(9, 2.5))
plt.plot(t, env)
plt.plot(points_time, points_level, "o", color="red")     # [[我们给的三个点||the three points we supplied]]
plt.xlabel("time (s)")
plt.ylabel("level")
plt.show()

play(osc * env)
'''),
        M(r'''
## 3. Click 从哪来

为什么需要 envelope?除了表现力,还有一个很实际的原因。

下面把一个音在 0.5037 秒处 **直接砍断**(后面接上一段静音)。砍断的那一刻波形不在 0 上,而是突然从某个值跳到 0。

**应该听到:** 音结束的瞬间有一声 "咔"。

**应该看到:** 波形在中间突然被切掉,有一条竖直的跳变。
''', r'''
## 3. Where clicks come from

Why have an envelope at all? Beyond expression there is a very practical reason.

Below a note is **cut off abruptly** at 0.5037 seconds (followed by silence). At that instant the waveform is not at 0; it jumps from some value straight to 0.

**You should hear:** a "click" at the moment the note ends.

**You should see:** the waveform chopped off mid-way, with a vertical jump.
'''),
        C(r'''
n_cut = int(sr * 0.5037)                       # [[在第几个 sample 砍断||the sample at which we cut]]
silence = np.zeros(int(sr * 0.5))              # [[0.5 秒的静音 = 一串 0||0.5 seconds of silence = a run of zeros]]

chopped = np.concatenate([osc[:n_cut], silence])

plt.figure(figsize=(9, 2.5))
plt.plot(chopped[n_cut - 600 : n_cut + 300])   # [[只画砍断点附近||plot only the area around the cut]]
plt.title("abrupt cut")
plt.show()

play(chopped)
'''),
        M(r'''
解决办法:在结尾加一个很短的 fade(这里是 10 毫秒)。10 毫秒短到听不出 "淡出",但足够让波形平滑地回到 0。

**应该听到:** 同样长度的音,结尾干净,没有 "咔"。

这就是 release 最基本的作用。attack 同理:它防止音头的 click。
''', r'''
The fix: add a very short fade at the end (10 milliseconds here). Too short to hear as a "fade-out", but long enough for the waveform to return to 0 smoothly.

**You should hear:** a note of the same length with a clean ending and no click.

This is the most basic job of a release. Attack is the same idea: it prevents a click at the start.
'''),
        C(r'''
t_cut = np.arange(n_cut) / sr
end = n_cut / sr                                           # [[音结束的时间(秒)||the time the note ends, in seconds]]

# [[一直是 1,最后 10 ms 降到 0||stays at 1, then falls to 0 over the last 10 ms]]
safe_env = np.interp(t_cut, [0, end - 0.01, end], [1, 1, 0])

faded = np.concatenate([osc[:n_cut] * safe_env, silence])

plt.figure(figsize=(9, 2.5))
plt.plot(faded[n_cut - 600 : n_cut + 300])
plt.title("10 ms fade")
plt.show()

play(faded)
'''),
        M(r'''
## 4. ADSR

Max 里你按下键、松开键。Python 里没有键盘,所以直接说 "按了多少秒",这个数叫 **gate**。`gate = 1.2` 就是按住 1.2 秒后松开。

五个数字:

| | 名字 | 单位 | 意思 |
|---|---|---|---|
| `a` | attack | 秒 | 从 0 升到 1 用多久 |
| `d` | decay | 秒 | 从 1 降到 sustain 用多久 |
| `s` | sustain | **高度**(0–1) | 按住时停留的高度。**不是时间。** |
| `r` | release | 秒 | 松开后降到 0 用多久 |
| `gate` | | 秒 | 按住多久 |

### 分两段做

**按住期间:** 三个点 (0, 0) → (a, 1) → (a+d, s)。之后 `np.interp` 自动停在 `s`。这正好就是 sustain。
''', r'''
## 4. ADSR

In Max you press and release a key. Python has no keyboard, so we simply state how long the key was held; that number is the **gate**. `gate = 1.2` means held for 1.2 seconds, then released.

Five numbers:

| | name | unit | meaning |
|---|---|---|---|
| `a` | attack | seconds | time to rise from 0 to 1 |
| `d` | decay | seconds | time to fall from 1 to the sustain level |
| `s` | sustain | **level** (0–1) | the level held while the key is down. **Not a time.** |
| `r` | release | seconds | time to fall to 0 after release |
| `gate` | | seconds | how long the key is held |

### Built in two parts

**While held:** three points (0, 0) → (a, 1) → (a+d, s). After that `np.interp` stays at `s` by itself — which is exactly the sustain.
'''),
        C(r'''
a, d, s, r, gate = 0.2, 0.3, 0.5, 0.5, 1.2

held = np.interp(t, [0, a, a + d], [0, 1, s])

plt.figure(figsize=(9, 2.5))
plt.plot(t, held)
plt.axvline(gate, linestyle="--", color="gray")
plt.title("held: what the envelope does if the key is never released")
plt.xlabel("time (s)")
plt.show()
'''),
        M(r'''
**松开之后:** 从松开那一刻的高度,用 `r` 秒直线降到 0。

- `(t - gate) / r`:松开后过了多久,以 `r` 为单位。刚松开是 0,过了 `r` 秒是 1。
- `1 - ...`:倒过来,刚松开是 1,过了 `r` 秒是 0。
- `np.clip(..., 0, 1)`:松开之前这个数会大于 1,`r` 秒之后会小于 0,都压回 0 到 1 之间。
- 再乘上 `level_at_release`(松开那一刻的高度)。
''', r'''
**After release:** fall in a straight line from the level at the moment of release down to 0 over `r` seconds.

- `(t - gate) / r`: time since release, in units of `r`. 0 at release, 1 after `r` seconds.
- `1 - ...`: flipped, so 1 at release and 0 after `r` seconds.
- `np.clip(..., 0, 1)`: before release this number exceeds 1 and after `r` seconds it drops below 0; both are held within 0 to 1.
- then multiply by `level_at_release` (the level at the moment of release).
'''),
        C(r'''
level_at_release = np.interp(gate, [0, a, a + d], [0, 1, s])      # [[只问一个时间点:松开时有多高||ask about one time point only: how high at release]]
released = level_at_release * np.clip(1 - (t - gate) / r, 0, 1)

plt.figure(figsize=(9, 2.5))
plt.plot(t, released)
plt.axvline(gate, linestyle="--", color="gray")
plt.title("released: only the part after the dashed line is used")
plt.xlabel("time (s)")
plt.show()
'''),
        M(r'''
**拼起来:** 松开之前用 `held`,之后用 `released`。`np.where` 第 2 集见过。
''', r'''
**Put together:** `held` before release, `released` after. `np.where` appeared in Episode 2.
'''),
        C(r'''
env = np.where(t < gate, held, released)

plt.figure(figsize=(9, 2.5))
plt.plot(t, env)
plt.axvline(gate, linestyle="--", color="gray")
plt.title("ADSR  (dashed line = key released)")
plt.xlabel("time (s)")
plt.show()
'''),
        M(r'''
### 包成函数
''', r'''
### Wrap it in a function
'''),
        C(ADSR),
        M(r'''
## 5. 三种 articulation

**1. pluck** — attack 极短,sustain 为 0。

**应该听到:** 短促的 "咚",约 0.3 秒就没了。gate 有 1.2 秒,但声音早就结束了 — 因为 sustain 是 0。
''', r'''
## 5. Three articulations

**1. pluck** — tiny attack, zero sustain.

**You should hear:** a short "dunk" gone in about 0.3 seconds. The gate lasts 1.2 seconds but the sound is over long before — because sustain is 0.
'''),
        C(r'''
pluck = adsr(t, a=0.005, d=0.3, s=0.0, r=0.1, gate=1.2)
play(osc * pluck)
'''),
        M(r'''
**2. pad** — attack 很长。

**应该听到:** 声音用 0.8 秒慢慢淡入,1.2 秒松开后再用 0.7 秒慢慢消失。
''', r'''
**2. pad** — long attack.

**You should hear:** the sound fading in over 0.8 seconds, then fading away over 0.7 seconds after the release at 1.2 seconds.
'''),
        C(r'''
pad = adsr(t, a=0.8, d=0.2, s=0.8, r=0.7, gate=1.2)
play(osc * pad)
'''),
        M(r'''
**3. organ** — attack 和 release 都只有 5 毫秒,sustain 为 1。

**应该听到:** 立刻满音量,1.2 秒时立刻停,而且两头都没有 click。
''', r'''
**3. organ** — attack and release of just 5 milliseconds, sustain at 1.

**You should hear:** full volume instantly, stopping at 1.2 seconds, with no click at either end.
'''),
        C(r'''
organ = adsr(t, a=0.005, d=0.01, s=1.0, r=0.005, gate=1.2)
play(osc * organ)
'''),
        C(r'''
fig, axes = plt.subplots(3, 1, figsize=(9, 5), sharex=True)
for ax, e, name in zip(axes, [pluck, pad, organ], ["pluck", "pad", "organ"]):
    ax.plot(t, osc * e, linewidth=0.3)
    ax.plot(t, e, color="red")
    ax.set_ylabel(name)
axes[-1].set_xlabel("time (s)")
plt.show()
'''),
        M(r'''
## 6. Gate 的长短

同一组 ADSR,只改 `gate`。

**应该听到:** 第一个是短音(按 0.15 秒),第二个是长音(按 1.4 秒)。音头的感觉完全一样,只是 "按住" 的时间不同。

注意第一个:0.15 秒时 attack(0.05)已经走完,decay(0.2)才走到一半,所以松开时的高度在 1 和 sustain 之间 — 这就是函数里要算 `level_at_release` 的原因。
''', r'''
## 6. Gate length

The same ADSR, with only `gate` changed.

**You should hear:** a short note first (held 0.15 s), then a long one (held 1.4 s). The onset feels identical; only the time "held" differs.

Note the first one: at 0.15 seconds the attack (0.05) is done and the decay (0.2) is halfway, so the level at release lies between 1 and sustain — which is why the function computes `level_at_release`.
'''),
        C(r'''
short_note = adsr(t, a=0.05, d=0.2, s=0.6, r=0.3, gate=0.15)
long_note = adsr(t, a=0.05, d=0.2, s=0.6, r=0.3, gate=1.4)

plt.figure(figsize=(9, 2.5))
plt.plot(t, short_note, label="gate 0.15")
plt.plot(t, long_note, label="gate 1.4")
plt.legend()
plt.xlabel("time (s)")
plt.show()

display(play(osc * short_note))
display(play(osc * long_note))
'''),
        M(r'''
## 7. 曲线的形状

我们的 envelope 是直线段。但耳朵对音量的感觉不是线性的:直线下降听起来像 "先撑着,最后突然没了"。

真实的 synth 用的是 exponential 曲线:一开始掉得快,越来越慢。一个简单的近似:把 envelope **取三次方**。0 还是 0,1 还是 1,中间被压低。

**应该听到:** 两个 pluck。第一个(直线)比较 "硬";第二个(曲线)开头更脆,尾巴更自然,像真的拨弦。
''', r'''
## 7. The shape of the curve

Our envelope uses straight segments. But the ear does not hear loudness linearly: a straight fall sounds like "holding on, then suddenly gone".

Real synths use exponential curves: falling fast at first, then slower and slower. A simple approximation: **cube** the envelope. 0 stays 0, 1 stays 1, the middle is pushed down.

**You should hear:** two plucks. The first (straight) is "stiffer"; the second (curved) has a crisper start and a more natural tail, like a real plucked string.
'''),
        C(r'''
linear = adsr(t, a=0.005, d=0.8, s=0.0, r=0.1, gate=1.2)
curved = linear ** 3

plt.figure(figsize=(9, 2.5))
plt.plot(t, linear, label="linear")
plt.plot(t, curved, label="linear ** 3")
plt.legend()
plt.xlabel("time (s)")
plt.show()

display(play(osc * linear))
display(play(osc * curved))
'''),
        M(r'''
## 8. 一段 bassline

把 "oscillator + envelope" 包成一个函数 `note()`,每调用一次就产生一个完整的音。然后像第 1 集做旋律那样,用 `np.concatenate` 接起来。

`gate=dur * 0.7`:每个音按住它时值的 70%,剩下 30% 留给 release。

循环里:

- `notes = []`:一个空 list
- `notes.append(...)`:往 list 末尾加一个东西
- 循环结束后 list 里有 8 个 array,`np.concatenate` 把它们接成一条

**应该听到:** 一段 8 个音的低音 pluck bassline,每个音 0.25 秒,共 2 秒。
''', r'''
## 8. A bassline

Wrap "oscillator + envelope" in a function `note()`; each call produces one complete note. Then join them with `np.concatenate`, as with the melody in Episode 1.

`gate=dur * 0.7`: each note is held for 70% of its length, leaving 30% for the release.

Inside the loop:

- `notes = []`: an empty list
- `notes.append(...)`: add one item to the end of the list
- after the loop the list holds 8 arrays, which `np.concatenate` joins into one

**You should hear:** an 8-note low pluck bassline, 0.25 seconds per note, 2 seconds in total.
'''),
        C(r'''
def note(freq, dur, a, d, s, r, pos=0.6):
    t = np.arange(int(sr * dur)) / sr
    phase = (freq * t) % 1
    env = adsr(t, a, d, s, r, gate=dur * 0.7)      # [[按住 70%,留 30% 给 release||hold 70%, leave 30% for the release]]
    return osc_wavetable(frames, phase, pos) * env ** 2

pitches = [55.00, 55.00, 82.41, 55.00, 65.41, 55.00, 98.00, 82.41]      # A1 A1 E2 A1 C2 A1 G2 E2

notes = []
for f in pitches:
    notes.append(note(f, 0.25, a=0.003, d=0.15, s=0.2, r=0.05))

bassline = np.concatenate(notes)

plt.figure(figsize=(9, 2.5))
plt.plot(np.arange(len(bassline)) / sr, bassline, linewidth=0.3)
plt.xlabel("time (s)")
plt.show()

play(bassline)
'''),
        M(r'''
## 常见错误

| 现象 | 原因 |
|---|---|
| 音头或音尾有 "咔" | attack 或 release 是 0;或者 release 比留给它的时间长,被砍断了 |
| 改了 sustain 但听不出区别 | gate 比 attack + decay 短,还没走到 sustain 就松开了 |
| 把 sustain 当成时间填了 `2.0` | sustain 是高度(0–1),不是秒 |
| 声音完全没有 | envelope 全是 0。检查 `a`、`d`、`s` 是否写反 |

## 练习

**1.** 做一个 "反向" 的感觉:attack 1 秒,sustain 1,release 0.01,gate 1.0。**先猜:** 听起来像什么?

<details><summary>答案</summary>

```python
play(osc * adsr(t, a=1.0, d=0.01, s=1.0, r=0.01, gate=1.0))
```
声音慢慢涨起来然后突然停 — 像一段倒放的 pluck。
</details>

**2.** 把 bassline 的每个音改成 0.125 秒,并把 `pitches` 重复两遍。提示:`pitches + pitches` 会把 list 接起来。

<details><summary>答案</summary>

```python
notes = []
for f in pitches + pitches:
    notes.append(note(f, 0.125, a=0.003, d=0.08, s=0.2, r=0.03))
play(np.concatenate(notes))
```
</details>

**3.** 用 `np.interp` 做一条 "两个峰" 的 envelope:0 → 1 → 0.2 → 1 → 0,盖在 `osc` 上。

<details><summary>答案</summary>

```python
env2 = np.interp(t, [0, 0.05, 0.5, 0.55, 1.5], [0, 1, 0.2, 1, 0])
play(osc * env2)
```
</details>

## 小结

| Max | Python |
|---|---|
| `adsr~` | `adsr(t, a, d, s, r, gate)` |
| note on / note off | `gate`(按住多少秒) |
| `function` + `line~` | `np.interp(t, times, levels)` |
| `*~` | `osc * env` |
| `sig~ 0`(静音) | `np.zeros(n)` |

- envelope 是一个 array
- attack 和 release 至少几毫秒,否则有 click
- 第 4 集说过:array 可以接到任何参数上。同一个 `adsr()` 之后还会去控制 filter 和 wavetable position。

**下一集:** `lores~` — filter,以及 Python 里第一次必须写 sample 循环的地方。
''', r'''
## Common mistakes

| Symptom | Cause |
|---|---|
| A click at the start or end of a note | Attack or release is 0; or the release is longer than the time left for it and gets cut off |
| Changing sustain makes no audible difference | The gate is shorter than attack + decay, so the key is released before sustain is reached |
| Sustain was filled in as a time, e.g. `2.0` | Sustain is a level (0–1), not seconds |
| No sound at all | The envelope is all zeros. Check whether `a`, `d`, `s` are swapped |

## Exercises

**1.** Make a "reversed" feel: attack 1 second, sustain 1, release 0.01, gate 1.0. **Guess first:** what does it sound like?

<details><summary>Answer</summary>

```python
play(osc * adsr(t, a=1.0, d=0.01, s=1.0, r=0.01, gate=1.0))
```
The sound swells slowly and then stops dead — like a pluck played backwards.
</details>

**2.** Make each bassline note 0.125 seconds long and play `pitches` twice. Hint: `pitches + pitches` joins the two lists.

<details><summary>Answer</summary>

```python
notes = []
for f in pitches + pitches:
    notes.append(note(f, 0.125, a=0.003, d=0.08, s=0.2, r=0.03))
play(np.concatenate(notes))
```
</details>

**3.** Use `np.interp` to make an envelope with "two peaks": 0 → 1 → 0.2 → 1 → 0, and lay it over `osc`.

<details><summary>Answer</summary>

```python
env2 = np.interp(t, [0, 0.05, 0.5, 0.55, 1.5], [0, 1, 0.2, 1, 0])
play(osc * env2)
```
</details>

## Recap

| Max | Python |
|---|---|
| `adsr~` | `adsr(t, a, d, s, r, gate)` |
| note on / note off | `gate` (seconds held) |
| `function` + `line~` | `np.interp(t, times, levels)` |
| `*~` | `osc * env` |
| `sig~ 0` (silence) | `np.zeros(n)` |

- an envelope is an array
- attack and release need at least a few milliseconds, or you get clicks
- Episode 4 said an array can be patched into any parameter. This same `adsr()` will soon control the filter and the wavetable position too.

**Next episode:** `lores~` — the filter, and the first place in Python where a sample loop is unavoidable.
'''),
    ])
