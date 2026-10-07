from common import *

EP = dict(
    zh_file="08_一个函数就是一个synth_参数与preset",
    en_file="08_one_function_is_a_synth_params_and_presets",
    cells=[
        M(r'''
# 第 8 集 — 一个函数就是一个 synth:参数与 preset

⏱ 约 25 分钟

**这一集控制的音乐元素:全部** — pitch、timbre、brightness、articulation、movement,第一次同时出现。

**Max / RNBO 里的对应:** 一个完整的 RNBO patch,顶上一排 `param` object,里面是 osc → filter → VCA,外加两个 envelope。

**你会听到:** 三个 preset —
1. `pluck`:短促、开头亮的拨弦音
2. `pad`:慢慢淡入、逐渐变亮的长音
3. `wow`:低音,filter 和 wavetable 一起慢慢张开再合上,"wow——"

然后用这个 synth 弹一段旋律。

**学完你能做到:**
- 用 `dict` 存一组参数
- 读懂 `synth()` 的每一行,知道它对应哪一集
- 改参数、做自己的 preset
- 用一个 preset 弹出一串音

这一集没有新的 DSP,只有 "接线" 和一个新的 Python 工具:`dict`。
''', r'''
# Episode 8 — One Function Is a Synth: Parameters and Presets

⏱ About 25 minutes

**Musical element this episode controls: all of them** — pitch, timbre, brightness, articulation and movement, together for the first time.

**The Max / RNBO equivalent:** a complete RNBO patch with a row of `param` objects on top and osc → filter → VCA inside, plus two envelopes.

**What you will hear:** three presets —
1. `pluck`: short, bright at the start
2. `pad`: a long note that fades in and slowly brightens
3. `wow`: a bass whose filter and wavetable open and close together, "wowww"

Then a melody played with this synth.

**By the end you can:**
- store a set of parameters in a `dict`
- read every line of `synth()` and say which episode it comes from
- change parameters and build your own presets
- play a series of notes with one preset

There is no new DSP in this episode, only "patching" and one new Python tool: the `dict`.
'''),
        M(TOOLBOX_ZH, TOOLBOX_EN),
        C(J(BASE, TABLE, FRAMES, ADSR, LOWPASS, PHASOR, r'''
frames = make_frames()
''')),
        M(r'''
## 1. Signal flow

```
note ──► mtof ──► phasor ──► wavetable osc ──► lowpass ──► × ──► out
                                 ▲                ▲         ▲
                              wt_pos           cutoff    amp env
                                 ▲                ▲
                                 └──── mod env ───┘
```

两个 envelope:

- **amp env**:控制音量(第 5 集)
- **mod env**:同时去推 wavetable position 和 cutoff(第 7 集),各自有一个 amount

## 2. `dict`:有名字的参数

到目前为止,参数都是一个个单独的变量(`cutoff = 300`、`res = 0.5` ……)。参数一多就很乱。

RNBO 里每个 `param` 有 **名字** 和 **值**。Python 里对应的是 `dict`:一张 **名字 → 值** 的表。Max 里也有同名的 `dict` object,是同一个东西。

- 建立:`{"名字": 值, "名字": 值}`
- 取值:`p["名字"]`
- 改值:`p["名字"] = 新值`
''', r'''
## 1. Signal flow

```
note ──► mtof ──► phasor ──► wavetable osc ──► lowpass ──► × ──► out
                                 ▲                ▲         ▲
                              wt_pos           cutoff    amp env
                                 ▲                ▲
                                 └──── mod env ───┘
```

Two envelopes:

- **amp env**: controls loudness (Episode 5)
- **mod env**: pushes both the wavetable position and the cutoff (Episode 7), each with its own amount

## 2. `dict`: parameters with names

Until now every parameter was its own variable (`cutoff = 300`, `res = 0.5` ...). With many parameters that gets messy.

In RNBO each `param` has a **name** and a **value**. Python's equivalent is the `dict`: a table of **name → value**. Max has a `dict` object of the same name, and it is the same thing.

- create: `{"name": value, "name": value}`
- read: `p["name"]`
- change: `p["name"] = new_value`
'''),
        C(r'''
p = {"note": 45, "cutoff": 300, "res": 0.2}

print("the whole dict :", p)
print("p['cutoff']    :", p["cutoff"])

p["cutoff"] = 1200                             # [[拧了一下 cutoff 旋钮||turning the cutoff knob]]
print("after change   :", p)

for name in p:                                 # [[依次取出每个名字||take each name in turn]]
    print(name, "=", p[name])
'''),
        M(r'''
还有一种写法 `dict(note=45, cutoff=300)`,结果完全一样,只是名字不用加引号,打起来快。下面的 preset 用这种写法。

## 3. `mtof`

Max 的 `mtof`:MIDI 音符号 → Hz。

- MIDI 69 = A4 = 440 Hz
- 每高 12 个半音,频率翻一倍(第 7 集的 `2 ** 八度数`)
''', r'''
There is another spelling, `dict(note=45, cutoff=300)`, with exactly the same result; the names need no quotes, so it is quicker to type. The presets below use it.

## 3. `mtof`

Max's `mtof`: MIDI note number → Hz.

- MIDI 69 = A4 = 440 Hz
- every 12 semitones up, the frequency doubles (Episode 7's `2 ** octaves`)
'''),
        C(r'''
def mtof(m):
    return 440 * 2 ** ((m - 69) / 12)          # [[(m - 69) / 12 = 离 A4 几个八度||(m - 69) / 12 = octaves away from A4]]

for m in [69, 57, 45, 33, 60]:
    print("MIDI", m, "->", round(mtof(m), 2), "Hz")
'''),
        M(r'''
## 4. 一步一步搭起来

不直接给出最终版本,而是分三步搭,每一步都听一下。

### 第一步:oscillator + amp envelope

只用到 6 个参数:`note`、`wt_pos`、`amp_a`、`amp_d`、`amp_s`、`amp_r`。

函数的第二、三个 inlet 是 `dur`(整段多长)和 `gate`(按住多久),都有默认值。

**应该听到:** 一个 A2 的音,没有 filter,音色全程不变,只有音量在动。
''', r'''
## 4. Building it step by step

Rather than presenting the final version outright, we build it in three steps and listen after each.

### Step 1: oscillator + amp envelope

Only 6 parameters are used: `note`, `wt_pos`, `amp_a`, `amp_d`, `amp_s`, `amp_r`.

The function's second and third inlets are `dur` (total length) and `gate` (time held), both with defaults.

**You should hear:** an A2 note with no filter; the timbre never changes, only the loudness moves.
'''),
        C(r'''
def synth_v1(p, dur=2.0, gate=1.2):
    n = int(sr * dur)
    t = np.arange(n) / sr
    amp_env = adsr(t, p["amp_a"], p["amp_d"], p["amp_s"], p["amp_r"], gate)
    phase = phasor(mtof(p["note"]), n)                     # [[note → Hz → phase||note → Hz → phase]]
    x = osc_wavetable(frames, phase, p["wt_pos"])
    return x * amp_env

test = dict(note=45, wt_pos=0.6,
            amp_a=0.01, amp_d=0.3, amp_s=0.5, amp_r=0.3)

play(synth_v1(test))
'''),
        M(r'''
### 第二步:加上 filter

多两个参数:`cutoff`、`res`。只多了一行。

**应该听到:** 同一个音,变闷了(cutoff 600 Hz),带一点共鸣。
''', r'''
### Step 2: add the filter

Two more parameters: `cutoff` and `res`. Just one extra line.

**You should hear:** the same note, duller (cutoff 600 Hz) with a little resonance.
'''),
        C(r'''
def synth_v2(p, dur=2.0, gate=1.2):
    n = int(sr * dur)
    t = np.arange(n) / sr
    amp_env = adsr(t, p["amp_a"], p["amp_d"], p["amp_s"], p["amp_r"], gate)
    phase = phasor(mtof(p["note"]), n)
    x = osc_wavetable(frames, phase, p["wt_pos"])
    x = lowpass(x, p["cutoff"], p["res"])                  # [[新加的一行||the new line]]
    return x * amp_env

test = dict(test, cutoff=600, res=0.4)                     # [[复制 test,并加上两个新参数||copy test and add two new parameters]]
play(synth_v2(test))
'''),
        M(r'''
`dict(test, cutoff=600, res=0.4)`:复制一份 `test`,并加上(或改掉)后面写的那几项。原来的 `test` 不会被动到 — 不过这里我们又把结果存回了 `test` 这个名字。

### 第三步:加上 mod envelope

再多 6 个参数:

- `mod_a`、`mod_d`、`mod_s`、`mod_r`:第二条 envelope
- `wt_env`:它推 wavetable position 推多少(0–1)
- `cut_env`:它推 cutoff 推多少(八度)

`wt_pos` 和 `cutoff` 不再是固定的数,而是 **旋钮的值 + envelope 推上去的量**。这正是第 7 集做的事。

这就是最终版本,一共 14 个参数。
''', r'''
`dict(test, cutoff=600, res=0.4)`: copy `test` and add (or override) the items listed after it. The original `test` is untouched — although here we store the result back under the name `test`.

### Step 3: add the mod envelope

Six more parameters:

- `mod_a`, `mod_d`, `mod_s`, `mod_r`: the second envelope
- `wt_env`: how much it pushes the wavetable position (0–1)
- `cut_env`: how much it pushes the cutoff (octaves)

`wt_pos` and `cutoff` are no longer fixed numbers but **the knob value plus what the envelope adds**. That is exactly what Episode 7 did.

This is the final version, with 14 parameters in total.
'''),
        C(SYNTH.replace("def mtof(m):\n    return 440 * 2 ** ((m - 69) / 12)          # [[MIDI 69 = 440 Hz;每 12 个半音翻一倍||MIDI 69 = 440 Hz; doubles every 12 semitones]]\n\n", "")),
        M(r'''
逐行对照:

| 行 | 做什么 | 哪一集 |
|---|---|---|
| `t = ...` | 时间表 | 1 |
| `amp_env`、`mod_env` | 两个 `adsr~` | 5 |
| `phase = phasor(mtof(...))` | `mtof` → `phasor~` | 7 |
| `osc_wavetable(...)` | position = 旋钮 + amount × mod env | 4、7 |
| `lowpass(...)` | cutoff = 旋钮,被 mod env 往上推 `cut_env` 个八度 | 6、7 |
| `x * amp_env` | VCA(`*~`) | 5 |

### 14 个参数

| 名字 | 意思 | 建议范围 |
|---|---|---|
| `note` | MIDI 音高 | 28–60 |
| `wt_pos` | wavetable position | 0–1 |
| `wt_env` | mod env → wt_pos 的 amount | 0–1 |
| `cutoff` | filter cutoff (Hz) | 80–8000 |
| `res` | resonance | 0–0.9 |
| `cut_env` | mod env → cutoff 的 amount(八度) | 0–5 |
| `amp_a` `amp_d` `amp_s` `amp_r` | amp envelope | 时间:秒;`amp_s`:0–1 |
| `mod_a` `mod_d` `mod_s` `mod_r` | mod envelope | 同上 |

## 5. Preset

一个 preset 就是一个填好了的 `dict`。`presets` 是一个 "装着 dict 的 dict":名字 → preset。
''', r'''
Line by line:

| line | what it does | episode |
|---|---|---|
| `t = ...` | the time table | 1 |
| `amp_env`, `mod_env` | two `adsr~` | 5 |
| `phase = phasor(mtof(...))` | `mtof` → `phasor~` | 7 |
| `osc_wavetable(...)` | position = knob + amount × mod env | 4, 7 |
| `lowpass(...)` | cutoff = knob, pushed up `cut_env` octaves by the mod env | 6, 7 |
| `x * amp_env` | the VCA (`*~`) | 5 |

### The 14 parameters

| name | meaning | suggested range |
|---|---|---|
| `note` | MIDI pitch | 28–60 |
| `wt_pos` | wavetable position | 0–1 |
| `wt_env` | amount of mod env → wt_pos | 0–1 |
| `cutoff` | filter cutoff (Hz) | 80–8000 |
| `res` | resonance | 0–0.9 |
| `cut_env` | amount of mod env → cutoff (octaves) | 0–5 |
| `amp_a` `amp_d` `amp_s` `amp_r` | amp envelope | times in seconds; `amp_s` 0–1 |
| `mod_a` `mod_d` `mod_s` `mod_r` | mod envelope | same |

## 5. Presets

A preset is simply a filled-in `dict`. `presets` is a "dict of dicts": name → preset.
'''),
        C(PRESETS),
        M(r'''
### 一个 "看 preset" 的小工具

听之前先看:`show(p)` 画出这个 preset 的两条 envelope,以及 cutoff 随时间的实际曲线。这相当于 Serum 界面上那几个 envelope 窗口。
''', r'''
### A small "look at the preset" tool

Look before listening: `show(p)` draws the preset's two envelopes and the actual cutoff curve over time — like the envelope panels of Serum's interface.
'''),
        C(r'''
def show(p, dur=2.0, gate=1.2):
    t = np.arange(int(sr * dur)) / sr
    amp_env = adsr(t, p["amp_a"], p["amp_d"], p["amp_s"], p["amp_r"], gate)
    mod_env = adsr(t, p["mod_a"], p["mod_d"], p["mod_s"], p["mod_r"], gate)
    fig, axes = plt.subplots(1, 2, figsize=(11, 2.5))
    axes[0].plot(t, amp_env, label="amp env")
    axes[0].plot(t, mod_env, label="mod env")
    axes[0].axvline(gate, linestyle="--", color="gray")
    axes[0].legend()
    axes[0].set_xlabel("time (s)")
    axes[1].plot(t, p["cutoff"] * 2 ** (p["cut_env"] * mod_env))      # [[和 synth() 里算 cutoff 的式子一样||the same cutoff formula as inside synth()]]
    axes[1].set_ylabel("cutoff (Hz)")
    axes[1].set_xlabel("time (s)")
    plt.show()
'''),
        M(r'''
### pluck

**应该听到:** 短促的拨弦音,开头有一个亮的 "嗒",随后迅速变闷消失。

**看图:** mod env 比 amp env 更短,所以先变闷、再变小声。cutoff 从 4800 Hz 在 0.15 秒内掉到 300 Hz。
''', r'''
### pluck

**You should hear:** a short plucked note with a bright "tick" at the start that quickly dulls and dies away.

**In the plot:** the mod env is shorter than the amp env, so the note goes dull first and quiet afterwards. The cutoff falls from 4800 Hz to 300 Hz within 0.15 seconds.
'''),
        C(r'''
show(presets["pluck"])
play(synth(presets["pluck"]))
'''),
        M(r'''
### pad

**应该听到:** 一个中音区的长音,慢慢淡入,同时逐渐变亮,松开后缓缓消失。

**看图:** 两条 envelope 的 attack 都很长;mod env 用 1 秒升到顶,所以亮度的变化比音量更慢。
''', r'''
### pad

**You should hear:** a long mid-range note that fades in while slowly brightening, then fades away gently after release.

**In the plot:** both envelopes have long attacks; the mod env takes 1 second to reach the top, so brightness changes more slowly than loudness.
'''),
        C(r'''
show(presets["pad"])
play(synth(presets["pad"]))
'''),
        M(r'''
### wow

**应该听到:** 一个很低的 bass,音色像嘴巴慢慢张开再合上:"wow——"。

**看图:** amp env 几乎立刻到顶并保持;mod env 用 0.35 秒升上去再落下来 — "wow" 的形状就是 mod env 的形状。
''', r'''
### wow

**You should hear:** a very low bass whose tone opens and closes like a mouth: "wowww".

**In the plot:** the amp env reaches the top almost instantly and stays; the mod env rises over 0.35 seconds and falls again — the shape of the "wow" is the shape of the mod env.
'''),
        C(r'''
show(presets["wow"])
play(synth(presets["wow"]))
'''),
        M(r'''
## 6. 拧旋钮

Python 里 "拧旋钮" 不是实时的:**改数字 → 重新算一遍 → 再听**。

好处是可以让循环帮你拧:一次听同一个旋钮的好几个位置。

### `cutoff`

**应该听到:** 同一个 `pluck`,四次,一次比一次亮。
''', r'''
## 6. Turning knobs

"Turning a knob" in Python is not live: **change a number → recompute → listen again**.

The upside: a loop can turn it for you, so you hear several positions of one knob in a row.

### `cutoff`

**You should hear:** the same `pluck` four times, brighter each time.
'''),
        C(r'''
for value in [100, 300, 900, 2700]:
    print("cutoff =", value)
    display(play(synth(dict(presets["pluck"], cutoff=value))))      # [[复制 pluck,只换掉 cutoff||copy pluck, replacing only cutoff]]
'''),
        M(r'''
### `cut_env`

**应该听到:** `wow` 四次。amount 为 0 时完全没有 "wow"(filter 不动);越大张得越开。
''', r'''
### `cut_env`

**You should hear:** `wow` four times. With amount 0 there is no "wow" at all (the filter stays put); the larger the amount, the wider it opens.
'''),
        C(r'''
for value in [0, 1.5, 3, 4.5]:
    print("cut_env =", value)
    display(play(synth(dict(presets["wow"], cut_env=value))))
'''),
        M(r'''
### `mod_a`

**应该听到:** `wow` 四次。"wow" 张开的速度从很快("wa")到很慢("wooooow")。
''', r'''
### `mod_a`

**You should hear:** `wow` four times. The opening speeds range from very fast ("wa") to very slow ("wooooow").
'''),
        C(r'''
for value in [0.02, 0.15, 0.35, 0.8]:
    print("mod_a =", value)
    display(play(synth(dict(presets["wow"], mod_a=value))))
'''),
        M(r'''
## 7. 用 preset 弹一段音

和第 5 集的 bassline 一样:循环里每次换一个 `note`,渲染一个短音,最后接起来。

**应该听到:** 用 `pluck` 音色弹的一段 8 个音的琶音,A 小调。
''', r'''
## 7. Playing notes with a preset

Like the bassline in Episode 5: the loop swaps in a different `note` each time, renders a short sound, and everything is joined at the end.

**You should hear:** an 8-note arpeggio in A minor, played with the `pluck` sound.
'''),
        C(r'''
def play_notes(p, notes, dur=0.3):
    out = []
    for m in notes:
        one = synth(dict(p, note=m), dur=dur, gate=dur * 0.6)      # [[换音高,其余参数不变||new pitch, everything else unchanged]]
        out.append(one)
    return np.concatenate(out)

arp = [45, 52, 57, 60, 64, 60, 57, 52]         # A2 E3 A3 C4 E4 C4 A3 E3
play(play_notes(presets["pluck"], arp))
'''),
        M(r'''
换一个 preset,同一段音:

**应该听到:** 同样的音符,但每个音都是 "wow" 的音色(这里把 `mod_a` 调短了,不然 0.3 秒里来不及张开)。
''', r'''
Another preset, the same notes:

**You should hear:** the same notes, each with the "wow" tone (`mod_a` is shortened here; otherwise it would not open within 0.3 seconds).
'''),
        C(r'''
fast_wow = dict(presets["wow"], mod_a=0.08, mod_d=0.12)
play(play_notes(fast_wow, [33, 33, 40, 33, 36, 33, 43, 40]), gain=0.25)
'''),
        M(r'''
## 8. 做自己的 preset

从一个现成的 preset 出发,改几个值。下面是一个起点,改数字、重新运行、看图、听。

想不出怎么改的话,试试这些目标:

- **更像笛子:** `wt_pos` 很低,`cut_env` 为 0,`amp_a` 0.08 左右
- **更像 "laser":** `cut_env` 5,`mod_d` 0.08,`res` 0.8
- **更像弦乐:** `wt_pos` 0.8,`amp_a` 0.3,`cutoff` 2000
''', r'''
## 8. Making your own preset

Start from an existing preset and change a few values. Below is a starting point: edit numbers, re-run, look at the plot, listen.

If you are short of ideas, aim for one of these:

- **more flute-like:** very low `wt_pos`, `cut_env` 0, `amp_a` around 0.08
- **more "laser":** `cut_env` 5, `mod_d` 0.08, `res` 0.8
- **more string-like:** `wt_pos` 0.8, `amp_a` 0.3, `cutoff` 2000
'''),
        C(r'''
my_patch = dict(presets["wow"],
                note=21,
                res=0.85,
                cut_env=5.0)

show(my_patch)
play(synth(my_patch), gain=0.2)
'''),
        M(r'''
**应该听到(没改之前):** 同一个 `wow`,低一个八度,resonance 更强,"wow" 更夸张。

## 常见错误

| 现象 | 原因 |
|---|---|
| `KeyError: 'cutof'` | 名字拼错了。`dict` 里没有这个名字 |
| `KeyError: 'mod_a'` | 把只有 6 个参数的 `test` 传给了需要 14 个参数的 `synth()` |
| 改了 preset 但声音没变 | 改完没有重新运行调用 `synth()` 的那个 cell |
| 声音很小或没有 | `cutoff` 很低而 `cut_env` 为 0;或者 `amp_s` 为 0 且 decay 很短 |
| 高音区有杂音 | `note` 太高,wavetable 里的 32 个 harmonic 超过了 sr / 2(第 3 集) |

## 练习

**1.** 做一个 `organ` preset:立刻出声、立刻停、音色不变。提示:`wt_env` 和 `cut_env` 都设 0。

<details><summary>答案</summary>

```python
organ = dict(note=57, wt_pos=0.4, wt_env=0.0, cutoff=3000, res=0.0, cut_env=0.0,
             amp_a=0.005, amp_d=0.01, amp_s=1.0, amp_r=0.01,
             mod_a=0.01, mod_d=0.01, mod_s=0.0, mod_r=0.01)
play(synth(organ))
```
</details>

**2.** 用循环听 `pad` 在 `res` 为 0、0.4、0.8 时的区别。

<details><summary>答案</summary>

```python
for value in [0, 0.4, 0.8]:
    display(play(synth(dict(presets["pad"], res=value)), gain=0.2))
```
</details>

**3.** 把琶音 `arp` 整体移高 5 个半音再弹。提示:循环里对每个音加 5。

<details><summary>答案</summary>

```python
higher = []
for m in arp:
    higher.append(m + 5)
play(play_notes(presets["pluck"], higher))
```
</details>

## 小结

| Max / RNBO | Python |
|---|---|
| 一个 RNBO patch | `synth(p)` 函数 |
| `param` object | `dict` 里的一项 |
| `dict` object | `dict` |
| preset | 一个 `dict` |
| `mtof` | `mtof(m)` |
| 拧旋钮 | `dict(旧的, 名字=新值)`,再调一次 `synth()` |

Python 里拧旋钮要 "重新算一遍",听起来比 Max 笨。但它换来一个 Max 很难做到的能力。

**下一集:** 让电脑自己拧旋钮,一口气生成一堆声音。
''', r'''
**You should hear (before editing):** the same `wow`, one octave lower, with stronger resonance and a more exaggerated "wow".

## Common mistakes

| Symptom | Cause |
|---|---|
| `KeyError: 'cutof'` | A misspelt name. The `dict` has no such entry |
| `KeyError: 'mod_a'` | The 6-parameter `test` was passed to `synth()`, which needs all 14 |
| A preset was changed but the sound was not | The cell calling `synth()` was not re-run |
| Very quiet or no sound | A very low `cutoff` with `cut_env` 0; or `amp_s` 0 with a very short decay |
| Junk tones at high pitches | `note` is too high; the 32 harmonics in the wavetable exceed sr / 2 (Episode 3) |

## Exercises

**1.** Make an `organ` preset: instant on, instant off, unchanging timbre. Hint: set both `wt_env` and `cut_env` to 0.

<details><summary>Answer</summary>

```python
organ = dict(note=57, wt_pos=0.4, wt_env=0.0, cutoff=3000, res=0.0, cut_env=0.0,
             amp_a=0.005, amp_d=0.01, amp_s=1.0, amp_r=0.01,
             mod_a=0.01, mod_d=0.01, mod_s=0.0, mod_r=0.01)
play(synth(organ))
```
</details>

**2.** Use a loop to hear `pad` with `res` at 0, 0.4 and 0.8.

<details><summary>Answer</summary>

```python
for value in [0, 0.4, 0.8]:
    display(play(synth(dict(presets["pad"], res=value)), gain=0.2))
```
</details>

**3.** Transpose the arpeggio `arp` up 5 semitones and play it. Hint: add 5 to every note inside a loop.

<details><summary>Answer</summary>

```python
higher = []
for m in arp:
    higher.append(m + 5)
play(play_notes(presets["pluck"], higher))
```
</details>

## Recap

| Max / RNBO | Python |
|---|---|
| an RNBO patch | the `synth(p)` function |
| a `param` object | one entry in a `dict` |
| the `dict` object | `dict` |
| a preset | a `dict` |
| `mtof` | `mtof(m)` |
| turning a knob | `dict(old, name=new_value)`, then call `synth()` again |

Having to "recompute" for every knob turn sounds clumsier than Max. But it buys an ability that is hard to get in Max.

**Next episode:** letting the computer turn the knobs and generate a pile of sounds in one go.
'''),
    ])
