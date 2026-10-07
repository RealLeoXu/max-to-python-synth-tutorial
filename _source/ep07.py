from common import *

EP = dict(
    zh_file="07_modulation_用signal控制参数",
    en_file="07_modulation_signals_controlling_parameters",
    cells=[
        M(r'''
# 第 7 集 — Modulation:用 signal 控制参数

⏱ 约 30 分钟

**这一集控制的音乐元素:movement(动态)** — filter 的开合、wobble 的节奏、pitch 的滑动。

**Max 里的对应 patch:** 把 `adsr~`、`cycle~ 3`、`line~` 的输出接到 `lores~` 的 cutoff inlet 和 `phasor~` 的 frequency inlet。

**你会听到:**
1. filter sweep:声音从闷逐渐打开
2. filter envelope:带 "piu" 感的 pluck bass
3. LFO → cutoff:"wub wub wub",并且对上 BPM
4. tremolo、vibrato、pitch drop
5. 一个完整的 wobble bass

**学完你能做到:**
- 把任何 array 接到 cutoff、音量、wavetable position 上
- 解释 modulation amount 为什么用 "八度" 做单位
- 把 LFO 的速度对上 BPM
- 解释 `freq * t` 在 pitch 变化时为什么是错的,以及 `phasor~` 实际怎么做
''', r'''
# Episode 7 — Modulation: Signals Controlling Parameters

⏱ About 30 minutes

**Musical element this episode controls: movement** — the filter opening and closing, the rhythm of a wobble, pitch glides.

**The equivalent Max patch:** the outputs of `adsr~`, `cycle~ 3` and `line~` patched into the cutoff inlet of `lores~` and the frequency inlet of `phasor~`.

**What you will hear:**
1. a filter sweep: the sound gradually opening up
2. a filter envelope: a pluck bass with a "pew" character
3. LFO → cutoff: "wub wub wub", locked to a BPM
4. tremolo, vibrato and a pitch drop
5. a complete wobble bass

**By the end you can:**
- patch any array into cutoff, volume or wavetable position
- explain why modulation amount is measured in octaves
- lock an LFO rate to a BPM
- explain why `freq * t` is wrong when pitch changes, and what `phasor~` really does
'''),
        M(TOOLBOX_ZH, TOOLBOX_EN),
        C(J(BASE, TABLE, FRAMES, ADSR, LOWPASS, r'''
frames = make_frames()

freq = 55
dur = 2.0
n_samples = int(sr * dur)
t = np.arange(n_samples) / sr
phase = (freq * t) % 1

saw = osc_wavetable(frames, phase, 1.0)
''')),
        M(r'''
`saw` 是一个 55 Hz(A1)的低音 saw,2 秒。这一集大部分例子都拿它当原料。

## 1. 回顾:数 vs array

第 4 集的结论:

> 传一个数就是静态的,传一个 array 就是会动的。

`lowpass(x, cutoff, res)` 的 `cutoff` 也一样。在 Max 里这就是 "往 cutoff inlet 接 number" 和 "接 signal" 的区别。

**modulation 的全部内容就是:做一个 array,把它接到某个参数上。** 这一集剩下的部分只是在换不同的 array 和不同的参数。

## 2. Filter sweep(`line~` → cutoff)

先用第 4 集的 `np.linspace`,让 cutoff 从 100 Hz 直线走到 6000 Hz。

**应该听到:** 声音一开始很快变亮,然后后面大半段几乎没什么变化。
''', r'''
`saw` is a low 55 Hz (A1) saw lasting 2 seconds. Most examples in this episode use it as raw material.

## 1. Recall: a number vs an array

The conclusion of Episode 4:

> Pass one number and it is static, pass an array and it moves.

The `cutoff` of `lowpass(x, cutoff, res)` behaves the same. In Max this is the difference between patching a number and patching a signal into the cutoff inlet.

**All of modulation comes down to this: build an array and patch it into a parameter.** The rest of this episode merely swaps in different arrays and different parameters.

## 2. Filter sweep (`line~` → cutoff)

Start with `np.linspace` from Episode 4 and take the cutoff in a straight line from 100 Hz to 6000 Hz.

**You should hear:** the sound brightening quickly at first, then barely changing for most of the remaining time.
'''),
        C(r'''
cutoff_linear = np.linspace(100, 6000, n_samples)
play(lowpass(saw, cutoff_linear, res=0.5))
'''),
        M(r'''
为什么不均匀?因为耳朵按 **倍数**(八度)听频率,不是按 Hz。

- 100 → 200 Hz 是一个八度
- 3000 → 6000 Hz 也是一个八度

直线走的话,第一个八度只用了 100 Hz 的距离(一瞬间就过去了),最后一个八度却占了 3000 Hz 的距离(整整后半段)。

`np.geomspace(100, 6000, n)`:也是从 100 走到 6000,但 **每一步乘同一个数**,而不是加同一个数。这样每个八度花的时间一样长。

**应该听到:** 从闷到亮,全程匀速地打开。
''', r'''
Why is it uneven? Because the ear hears frequency by **ratio** (octaves), not by Hz.

- 100 → 200 Hz is one octave
- 3000 → 6000 Hz is also one octave

On a straight line the first octave covers only 100 Hz (gone in an instant) while the last octave covers 3000 Hz (the entire second half).

`np.geomspace(100, 6000, n)`: also from 100 to 6000, but **each step multiplies by the same number** rather than adding the same number. Every octave then takes equally long.

**You should hear:** dull to bright, opening at a steady rate throughout.
'''),
        C(r'''
cutoff_geo = np.geomspace(100, 6000, n_samples)

plt.figure(figsize=(9, 3))
plt.plot(t, cutoff_linear, label="linspace")
plt.plot(t, cutoff_geo, label="geomspace")
plt.xlabel("time (s)")
plt.ylabel("cutoff (Hz)")
plt.legend()
plt.show()

play(lowpass(saw, cutoff_geo, res=0.5))
'''),
        M(r'''
**记住:** 和频率有关的东西(cutoff、pitch),都按倍数走。

## 3. Filter envelope(`adsr~` → cutoff)

用第 5 集的 `adsr()` 做一条 envelope,让它去推 cutoff。

envelope 的值在 0 到 1 之间。怎么把它变成 Hz?按上面的结论,用倍数:

`cutoff = base * 2 ** (amount * env)`

- `2 ** 八度数` = 升高这么多个八度(`2 ** 1` = 2 倍,`2 ** 2` = 4 倍,`2 ** 3` = 8 倍)
- `env = 0` 时:`2 ** 0 = 1`,cutoff 就是 `base`
- `env = 1` 时:cutoff 比 `base` 高 `amount` 个八度

所以 `base` 是 filter 的 cutoff 旋钮,`amount` 是 envelope amount 旋钮,单位是八度。
''', r'''
**Remember:** anything to do with frequency (cutoff, pitch) moves by ratio.

## 3. Filter envelope (`adsr~` → cutoff)

Build an envelope with `adsr()` from Episode 5 and let it push the cutoff.

The envelope runs from 0 to 1. How do we turn that into Hz? By ratio, as concluded above:

`cutoff = base * 2 ** (amount * env)`

- `2 ** octaves` = go up that many octaves (`2 ** 1` = ×2, `2 ** 2` = ×4, `2 ** 3` = ×8)
- at `env = 0`: `2 ** 0 = 1`, so cutoff equals `base`
- at `env = 1`: cutoff is `amount` octaves above `base`

So `base` is the filter's cutoff knob and `amount` is the envelope amount knob, measured in octaves.
'''),
        C(r'''
flt_env = adsr(t, a=0.001, d=0.25, s=0.0, r=0.1, gate=1.0)
amp_env = adsr(t, a=0.005, d=0.6, s=0.0, r=0.1, gate=1.0)

base = 150
amount = 5
cutoff = base * 2 ** (amount * flt_env)        # [[env 0 → 150 Hz;env 1 → 150 × 2^5 = 4800 Hz||env 0 → 150 Hz; env 1 → 150 × 2^5 = 4800 Hz]]

plt.figure(figsize=(9, 2.5))
plt.plot(t, cutoff)
plt.xlabel("time (s)")
plt.ylabel("cutoff (Hz)")
plt.show()

play(lowpass(saw, cutoff, res=0.5) * amp_env)
'''),
        M(r'''
**应该听到:** 一个开头很亮、迅速变闷的 pluck bass,带一点 "piu" 的感觉。

注意这里用了 **两条** envelope:`flt_env` 管 cutoff,`amp_env` 管音量。filter envelope 比 amp envelope 短,所以先变闷、再变小声。

### Amount 的大小

**应该听到:** 三个 pluck。amount 为 1 时几乎没有 "piu";3 时明显;5 时很夸张。
''', r'''
**You should hear:** a pluck bass that starts bright and quickly turns dull, with a bit of a "pew".

Note the **two** envelopes: `flt_env` handles the cutoff, `amp_env` the loudness. The filter envelope is shorter than the amp envelope, so the note goes dull first and quiet afterwards.

### The size of the amount

**You should hear:** three plucks. With amount 1 there is hardly any "pew"; with 3 it is clear; with 5 it is exaggerated.
'''),
        C(r'''
for amount in [1, 3, 5]:
    print("amount =", amount, "octaves")
    display(play(lowpass(saw, 150 * 2 ** (amount * flt_env), res=0.5) * amp_env))
'''),
        M(r'''
## 4. LFO → cutoff(`cycle~ 3` → cutoff)

LFO 就是一个很慢的 oscillator。第 1 集的 sine,频率改成 3 Hz 就是了。

`lfo` 在 -1 到 1 之间摆动。套进同一个式子:

`cutoff = 300 * 2 ** (2 * lfo)`

- `lfo = -1` → 300 低 2 个八度 = 75 Hz
- `lfo = 0` → 300 Hz
- `lfo = +1` → 300 高 2 个八度 = 1200 Hz

**应该听到:** "wub wub wub",每秒 3 次。
''', r'''
## 4. LFO → cutoff (`cycle~ 3` → cutoff)

An LFO is just a very slow oscillator: Episode 1's sine with the frequency set to 3 Hz.

`lfo` swings between -1 and 1. Put it into the same formula:

`cutoff = 300 * 2 ** (2 * lfo)`

- `lfo = -1` → 2 octaves below 300 = 75 Hz
- `lfo = 0` → 300 Hz
- `lfo = +1` → 2 octaves above 300 = 1200 Hz

**You should hear:** "wub wub wub", three per second.
'''),
        C(r'''
lfo_rate = 3
lfo = np.sin(2 * np.pi * lfo_rate * t)         # [[和第 1 集的 sine 一样,只是频率很低||the same sine as Episode 1, just very slow]]

cutoff = 300 * 2 ** (2 * lfo)

plt.figure(figsize=(9, 2.5))
plt.plot(t, cutoff)
plt.xlabel("time (s)")
plt.ylabel("cutoff (Hz)")
plt.show()

play(lowpass(saw, cutoff, res=0.6))
'''),
        M(r'''
### 对上 BPM

LFO 的速度(Hz)= 每秒几次。音乐里更想说的是 "每拍几次"。

- `bpm / 60` = 每秒几拍
- 乘上 "每拍几次" = 每秒几次 = LFO 的 Hz

140 BPM、每拍 2 次(八分音符):`140 / 60 * 2 = 4.67 Hz`。

**应该听到:** wobble 的速度是 140 BPM 的八分音符。2 秒里大约 9 次。
''', r'''
### Locking to a BPM

LFO rate in Hz = times per second. Musically you would rather say "times per beat".

- `bpm / 60` = beats per second
- times "per beat" = times per second = the LFO's Hz

At 140 BPM with 2 per beat (eighth notes): `140 / 60 * 2 = 4.67 Hz`.

**You should hear:** a wobble at eighth notes of 140 BPM. About 9 of them in 2 seconds.
'''),
        C(r'''
bpm = 140
per_beat = 2                                   # [[每拍 2 次 = 八分音符;改成 4 是十六分,改成 3 是三连音||2 per beat = eighth notes; 4 gives sixteenths, 3 gives triplets]]
lfo_rate = bpm / 60 * per_beat
print("LFO rate:", round(lfo_rate, 2), "Hz")

lfo = np.sin(2 * np.pi * lfo_rate * t)
play(lowpass(saw, 300 * 2 ** (2 * lfo), res=0.6))
'''),
        M(r'''
### LFO 的形状

LFO 是 oscillator,所以第 2 集的做法全都能用:先做一个慢的 phase,再变成不同形状。

- **sine**:平滑地开合 → "wub"
- **saw down**(从 1 掉到 -1):每次突然打开、然后慢慢合上 → "yoi yoi"
- **square**:只有开和关两种状态 → 一亮一暗交替

**应该听到:** 三种不同性格的 wobble,速度相同。
''', r'''
### LFO shapes

An LFO is an oscillator, so everything from Episode 2 applies: build a slow phase, then turn it into different shapes.

- **sine**: opens and closes smoothly → "wub"
- **saw down** (falling from 1 to -1): snaps open, then closes slowly → "yoi yoi"
- **square**: only two states, open and closed → bright and dark alternating

**You should hear:** three wobbles of different character at the same speed.
'''),
        C(r'''
lfo_phase = (lfo_rate * t) % 1                 # [[慢的 phasor~||a slow phasor~]]

lfo_shapes = {
    "sine":     np.sin(2 * np.pi * lfo_phase),
    "saw down": 1 - 2 * lfo_phase,                         # [[1 → -1||1 → -1]]
    "square":   np.where(lfo_phase < 0.5, 1.0, -1.0),
}

fig, axes = plt.subplots(3, 1, figsize=(9, 4), sharex=True)
for ax, name in zip(axes, lfo_shapes):
    ax.plot(t, lfo_shapes[name])
    ax.set_ylabel(name)
axes[-1].set_xlabel("time (s)")
plt.show()

for name in lfo_shapes:
    print(name)
    display(play(lowpass(saw, 300 * 2 ** (2 * lfo_shapes[name]), res=0.6)))
'''),
        M(r'''
## 5. 同一个 LFO,别的参数

modulation 不限于 cutoff。

### 音量 → tremolo

音量不能是负的,所以把 -1..1 的 LFO 挪到 0..1:`0.5 + 0.5 * lfo`。

**应该听到:** 音量以 140 BPM 八分音符的速度一强一弱。
''', r'''
## 5. The same LFO, other parameters

Modulation is not limited to cutoff.

### Volume → tremolo

Volume cannot be negative, so shift the -1..1 LFO to 0..1: `0.5 + 0.5 * lfo`.

**You should hear:** the volume pulsing at eighth notes of 140 BPM.
'''),
        C(r'''
tremolo = 0.5 + 0.5 * lfo                      # [[-1..1 → 0..1||-1..1 → 0..1]]
play(lowpass(saw, 800) * tremolo)
'''),
        M(r'''
### Wavetable position

第 4 集做过。**应该听到:** 音色本身在暗和亮之间来回,和 filter wobble 类似但更 "干净",因为没有 resonance。
''', r'''
### Wavetable position

As in Episode 4. **You should hear:** the timbre itself moving between dark and bright; similar to a filter wobble but "cleaner", since there is no resonance.
'''),
        C(r'''
play(osc_wavetable(frames, phase, 0.5 + 0.5 * lfo))
'''),
        M(r'''
## 6. Pitch modulation:这里有个坑

想让 pitch 在 2 秒内从 110 Hz 滑到 220 Hz(升一个八度)。直觉的写法是把 `freq` 换成一个 array:
''', r'''
## 6. Pitch modulation: there is a trap here

Say the pitch should glide from 110 Hz to 220 Hz over 2 seconds (one octave up). The intuitive move is to replace `freq` with an array:
'''),
        C(r'''
freq_glide = np.geomspace(110, 220, n_samples)

wrong_phase = (freq_glide * t) % 1             # [[看起来合理,其实是错的||looks reasonable, but is wrong]]
play(np.sin(2 * np.pi * wrong_phase))
'''),
        M(r'''
**应该听到:** 音高上升得 **明显超过** 一个八度(最后到了 370 Hz 左右,而不是 220 Hz)。这是错的。

**为什么:** `freq * t` 的意思是 "从头到现在 **一直** 是这个频率,所以一共走了这么多个周期"。频率在变的时候,这句话不成立。在第 2 秒,它算的是 "220 × 2 = 440 个周期",好像从一开始就是 220 Hz 一样 — 但实际上前面大部分时间频率都比 220 低,根本走不了那么多。为了凑够这个数,phase 被迫越跑越快。

### `phasor~` 实际上是怎么做的

它不看 "从头到现在",只看 **这一个 sample 该往前走多少**,然后一直累加。

- 一秒走 `freq` 个周期,一秒有 `sr` 个 sample
- 所以 **每个 sample 走 `freq / sr` 个周期**
- 把每一步累加起来,就是 phase

"累加" 是 `np.cumsum`(cumulative sum):第 n 个数 = 前 n 个数的总和。
''', r'''
**You should hear:** the pitch rising **clearly more** than one octave (it ends near 370 Hz rather than 220 Hz). That is wrong.

**Why:** `freq * t` means "the frequency has been this value **all along**, so this many cycles have elapsed". Once the frequency changes, that is false. At second 2 it computes "220 × 2 = 440 cycles", as if the frequency had been 220 Hz from the start — but for most of that time it was lower, and nowhere near that many cycles fit. To make up the number, phase is forced to run faster and faster.

### What `phasor~` really does

It does not look at "from the start until now", only at **how far to advance during this one sample**, and it keeps a running total.

- `freq` cycles per second, `sr` samples per second
- so **each sample advances by `freq / sr` cycles**
- add up every step and you have the phase

The "running total" is `np.cumsum` (cumulative sum): the n-th number is the sum of the first n numbers.
'''),
        C(r'''
steps = np.array([1, 2, 3, 4])
print("steps  =", steps)
print("cumsum =", np.cumsum(steps))            # [[1, 1+2, 1+2+3, 1+2+3+4||1, 1+2, 1+2+3, 1+2+3+4]]
'''),
        M(r'''
这也是一种 "记住上一次" — 和上一集的 `history` 是同一个想法。只不过累加太常用了,numpy 提供了现成的 `cumsum`,不用自己写循环。

这叫 **phase accumulation**。
''', r'''
This too is a way of "remembering the last time" — the same idea as last episode's `history`. Running totals are so common that numpy provides `cumsum`, so no hand-written loop is needed.

This is called **phase accumulation**.
'''),
        C(PHASOR + r'''
right_phase = phasor(freq_glide, n_samples)
play(np.sin(2 * np.pi * right_phase))
'''),
        M(r'''
**应该听到:** 正好升一个八度,停在 220 Hz。

`np.broadcast_to(freq, n_samples)` 的作用:如果 `freq` 是一个数,就把它变成 `n_samples` 个一样的数;如果已经是 array,就原样用。所以 `phasor(110, n)` 和 `phasor(某个array, n)` 都行。

**从现在起,phase 都用 `phasor(freq, n_samples)` 来做。** 之前的 `(freq * t) % 1` 只在 freq 不变时才对。

### Vibrato

pitch 也按倍数走。半音是八度的 1/12,所以:

`freq = 220 * 2 ** (半音数 / 12 * lfo)`

**应该听到:** 一个音高每秒抖动 5 次的音,上下各半个半音,像歌手的颤音。
''', r'''
**You should hear:** exactly one octave up, landing on 220 Hz.

What `np.broadcast_to(freq, n_samples)` does: if `freq` is one number it becomes `n_samples` copies of it; if it already is an array it is used as is. So both `phasor(110, n)` and `phasor(some_array, n)` work.

**From now on phase is always made with `phasor(freq, n_samples)`.** The earlier `(freq * t) % 1` is only right when freq never changes.

### Vibrato

Pitch moves by ratio too. A semitone is 1/12 of an octave, so:

`freq = 220 * 2 ** (semitones / 12 * lfo)`

**You should hear:** a note whose pitch wavers 5 times per second, half a semitone up and down, like a singer's vibrato.
'''),
        C(r'''
vib_lfo = np.sin(2 * np.pi * 5 * t)
freq_vib = 220 * 2 ** (0.5 / 12 * vib_lfo)     # [[上下各 0.5 个半音||0.5 semitones up and down]]

play(osc_wavetable(frames, phasor(freq_vib, n_samples), 0.8))
'''),
        M(r'''
### Modulate 一个 modulator

歌手通常不是一开口就颤,而是先平着唱,再慢慢加上颤音。

做法:让 vibrato 的 **深度** 也随时间变化 — 用一条 envelope 去乘 LFO。前 0.5 秒深度是 0,之后 1 秒内升到 1。

**应该听到:** 先是一个平稳的音,然后颤音逐渐出现并加深。
''', r'''
### Modulating a modulator

A singer rarely wavers from the first instant; the note starts straight and vibrato is added gradually.

To do that, let the **depth** of the vibrato change over time too — multiply the LFO by an envelope. Depth is 0 for the first 0.5 seconds, then rises to 1 over 1 second.

**You should hear:** a steady note at first, then vibrato gradually appearing and deepening.
'''),
        C(r'''
depth = np.interp(t, [0, 0.5, 1.5], [0, 0, 1])             # [[0.5 秒前是 0,1.5 秒时到 1||0 until 0.5 s, reaching 1 at 1.5 s]]
freq_vib = 220 * 2 ** (0.7 / 12 * vib_lfo * depth)         # [[LFO × 深度||LFO × depth]]

play(osc_wavetable(frames, phasor(freq_vib, n_samples), 0.8))
'''),
        M(r'''
### Pitch drop

pitch 从高处(50 Hz 往上 4 个八度 = 800 Hz)快速掉到 50 Hz,配一个短的 amp envelope。

**应该听到:** 一声 "咚 / piu",像电子 kick 或 laser。把 `d=0.12` 改短会更像 kick,改长会更像 laser。
''', r'''
### Pitch drop

The pitch falls quickly from high (4 octaves above 50 Hz = 800 Hz) to 50 Hz, with a short amp envelope.

**You should hear:** a "boom / pew", like an electronic kick or a laser. A shorter `d=0.12` leans toward a kick, a longer one toward a laser.
'''),
        C(r'''
pitch_env = adsr(t, a=0.001, d=0.12, s=0.0, r=0.1, gate=1.0)
freq_drop = 50 * 2 ** (4 * pitch_env)                      # [[env 1 → 800 Hz;env 0 → 50 Hz||env 1 → 800 Hz; env 0 → 50 Hz]]
kick_amp = adsr(t, a=0.001, d=0.5, s=0.0, r=0.1, gate=1.0)

play(np.sin(2 * np.pi * phasor(freq_drop, n_samples)) * kick_amp, gain=0.6)
'''),
        M(r'''
## 7. 全部接在一起:wobble bass

- oscillator:55 Hz 的 wavetable
- 一个 saw-down LFO(140 BPM 八分音符)同时推 **wavetable position** 和 **cutoff**
- 再加一点点 pitch 上的 LFO,让它更 "脏"

**应该听到:** 一个典型的 "yoi yoi yoi" wobble bass。
''', r'''
## 7. Everything patched together: a wobble bass

- oscillator: a 55 Hz wavetable
- one saw-down LFO (eighth notes at 140 BPM) pushing both the **wavetable position** and the **cutoff**
- a touch of the LFO on pitch as well, to make it "dirtier"

**You should hear:** a typical "yoi yoi yoi" wobble bass.
'''),
        C(r'''
wob = lfo_shapes["saw down"]                                   # -1..1
wob01 = 0.5 + 0.5 * wob                                        # 0..1

bass_phase = phasor(55 * 2 ** (0.3 / 12 * wob), n_samples)     # [[pitch:上下 0.3 个半音||pitch: 0.3 semitones up and down]]
bass = osc_wavetable(frames, bass_phase, 0.2 + 0.8 * wob01)    # [[wavetable position:0.2..1||wavetable position: 0.2..1]]
bass = lowpass(bass, 200 * 2 ** (3 * wob01), res=0.7)          # [[cutoff:200..1600 Hz||cutoff: 200..1600 Hz]]

plt.figure(figsize=(9, 3.5))
plt.specgram(bass + 1e-9, NFFT=2048, Fs=sr, noverlap=1792, cmap="magma", vmin=-120)
plt.ylim(0, 3000)
plt.xlabel("time (s)")
plt.ylabel("frequency (Hz)")
plt.show()

play(bass, gain=0.2)
'''),
        M(r'''
spectrogram 里每一个 "鼓包" 就是一次 "yoi":亮的区域突然冲高,再慢慢落回去 — 正是 saw-down LFO 的形状。

## 常见错误

| 现象 | 原因 |
|---|---|
| sweep 听起来不匀速 | 对频率用了 `linspace`,应该用 `geomspace` 或 `base * 2 ** (...)` |
| pitch 滑动的幅度不对 | 用了 `(freq * t) % 1`。freq 会变时必须用 `phasor()` |
| cutoff 变成负数 / 报错 | 用了 `base + amount * lfo`(加法)。用乘法形式就不会变负 |
| tremolo 听起来像失真 | 音量的 LFO 没有挪到 0..1,负的那一半把波形翻转了 |

## 练习

**1.** 把第 4 节的 BPM wobble 改成十六分音符(每拍 4 次),再改成三连音(每拍 3 次)。

<details><summary>答案</summary>

```python
for per_beat in [4, 3]:
    rate = 140 / 60 * per_beat
    l = np.sin(2 * np.pi * rate * t)
    display(play(lowpass(saw, 300 * 2 ** (2 * l), res=0.6)))
```
</details>

**2.** 做一个往 **上** 滑的音:从 110 Hz 在 0.3 秒内升到 440 Hz,然后停住。提示:`np.interp` 做一条 0 → 1 的线,再用 `110 * 2 ** (2 * 线)`。

<details><summary>答案</summary>

```python
rise = np.interp(t, [0, 0.3], [0, 1])
play(np.sin(2 * np.pi * phasor(110 * 2 ** (2 * rise), n_samples)))
```
</details>

**3.** 让 LFO 的 **速度** 本身逐渐加快:从 1 Hz 到 12 Hz。提示:LFO 也是 oscillator,速度会变时它的 phase 也要用 `phasor()`。

<details><summary>答案</summary>

```python
rate = np.geomspace(1, 12, n_samples)
l = np.sin(2 * np.pi * phasor(rate, n_samples))
play(lowpass(saw, 300 * 2 ** (2 * l), res=0.6))
```
wobble 越来越快。
</details>

## 小结

| Max | Python |
|---|---|
| signal 接到 cutoff inlet | `lowpass(x, cutoff_array, res)` |
| `line~`(线性) | `np.linspace(a, b, n)` |
| `line~` → `mtof~`(按音高走) | `np.geomspace(a, b, n)` |
| LFO:`cycle~ 3` | `np.sin(2 * np.pi * 3 * t)` |
| mod amount(八度) | `base * 2 ** (amount * mod)` |
| `phasor~`(signal-rate 频率) | `phasor(freq, n)` = `np.cumsum(freq / sr) % 1` |
| `+=`(gen~)/ `accum` | `np.cumsum(...)` |

- modulation = 做一个 array,接到一个参数上
- 和频率有关的参数按倍数走:`base * 2 ** (八度数)`
- pitch 会变时,phase 必须用累加的方式算

**下一集:** 把 oscillator、filter、envelope、modulation 全部装进一个函数 — 一个完整的 synth。
''', r'''
Each "bulge" in the spectrogram is one "yoi": the bright region shoots up and slowly settles back — exactly the shape of the saw-down LFO.

## Common mistakes

| Symptom | Cause |
|---|---|
| A sweep sounds uneven | `linspace` was used for a frequency; use `geomspace` or `base * 2 ** (...)` |
| A pitch glide covers the wrong range | `(freq * t) % 1` was used. When freq changes you must use `phasor()` |
| Cutoff goes negative / errors | `base + amount * lfo` (addition) was used. The multiplying form never goes negative |
| Tremolo sounds like distortion | The volume LFO was not shifted to 0..1; its negative half flips the waveform |

## Exercises

**1.** Change the BPM wobble of section 4 to sixteenth notes (4 per beat), then to triplets (3 per beat).

<details><summary>Answer</summary>

```python
for per_beat in [4, 3]:
    rate = 140 / 60 * per_beat
    l = np.sin(2 * np.pi * rate * t)
    display(play(lowpass(saw, 300 * 2 ** (2 * l), res=0.6)))
```
</details>

**2.** Make a note that glides **up**: from 110 Hz to 440 Hz in 0.3 seconds, then holds. Hint: build a 0 → 1 line with `np.interp`, then use `110 * 2 ** (2 * line)`.

<details><summary>Answer</summary>

```python
rise = np.interp(t, [0, 0.3], [0, 1])
play(np.sin(2 * np.pi * phasor(110 * 2 ** (2 * rise), n_samples)))
```
</details>

**3.** Make the LFO **rate** itself speed up, from 1 Hz to 12 Hz. Hint: an LFO is an oscillator, so when its rate changes its phase needs `phasor()` too.

<details><summary>Answer</summary>

```python
rate = np.geomspace(1, 12, n_samples)
l = np.sin(2 * np.pi * phasor(rate, n_samples))
play(lowpass(saw, 300 * 2 ** (2 * l), res=0.6))
```
The wobble gets faster and faster.
</details>

## Recap

| Max | Python |
|---|---|
| a signal into the cutoff inlet | `lowpass(x, cutoff_array, res)` |
| `line~` (linear) | `np.linspace(a, b, n)` |
| `line~` → `mtof~` (moving in pitch) | `np.geomspace(a, b, n)` |
| LFO: `cycle~ 3` | `np.sin(2 * np.pi * 3 * t)` |
| mod amount (octaves) | `base * 2 ** (amount * mod)` |
| `phasor~` (signal-rate frequency) | `phasor(freq, n)` = `np.cumsum(freq / sr) % 1` |
| `+=` (gen~) / `accum` | `np.cumsum(...)` |

- modulation = build an array, patch it into a parameter
- frequency-like parameters move by ratio: `base * 2 ** (octaves)`
- when pitch changes, phase must be computed by accumulation

**Next episode:** oscillator, filter, envelopes and modulation packed into one function — a complete synth.
'''),
    ])
