from common import *

EP = dict(
    zh_file="00_开始之前_目的_难度_环境",
    en_file="00_before_you_start_purpose_difficulty_setup",
    cells=[
        M(r'''
# Max to Python Synth — 开始之前

⏱ 约 10 分钟(不含安装)

这个 notebook 不教 synth。它回答三个问题:**这个教程是干什么的、有多难、怎么把环境装好。** 最后有一个检查环境的 cell,它能出声,就可以开始第 1 集。

---

## 1. 这个教程的目的

你已经会在 Max / RNBO 里做 synth:知道 `phasor~`、`cycle~`、`buffer~`、`adsr~`、`lores~` 是什么,会连线。

这个教程用 10 集,把你 **已经懂的这些概念** 一个一个翻译成 Python。每一集都从一个你熟悉的 Max object 出发,做出它在 Python 里的对应物,并且 **听到声音**。

10 集之后你会有:

- 一个自己写的、完整的 wavetable synth(oscillator + filter + 两个 envelope + modulation),一共约 100 行 Python
- 一套参数和 preset 系统
- 批量生成 "声音 ↔ 参数" 数据集的能力
- 把 wavetable 和 preset 送回 Max 的方法

### 为什么 Max 用户要学这个

不是为了取代 Max。两者擅长的事情不同:

| | Max / RNBO | Python |
|---|---|---|
| 实时演奏、拧旋钮、做乐器 | ✅ 很擅长 | ❌ 不擅长 |
| 自动生成一万个声音并记录每个的参数 | 😖 别扭 | ✅ 一个循环 |
| 分析声音、画图、做实验 | 有限 | ✅ 很擅长 |
| machine learning | 基本做不了 | ✅ 主流工具都在这里 |

如果你想做音频分析、做数据集、或者往 audio machine learning 的方向走,Python 是绕不开的。而 "已经懂 synth" 是学它最好的起点 — 你不用同时学 DSP 概念和编程语言,只需要学后者。

### 这个教程 **不** 教什么

- 实时音频(Python 版的 synth 是 "算完再播",不能边弹边响)
- 图形界面、插件(VST / AU)
- Python 语言的全貌 — 只教做 synth 用得到的那一小部分
- 数学推导 — filter 和 FFT 都当作现成的 object 来用
''', r'''
# Max to Python Synth — Before You Start

⏱ About 10 minutes (installation not included)

This notebook does not teach synthesis. It answers three questions: **what this tutorial is for, how hard it is, and how to set up the environment.** At the end is a cell that checks your setup; once it makes sound you are ready for Episode 1.

---

## 1. What this tutorial is for

You can already build synths in Max / RNBO: you know what `phasor~`, `cycle~`, `buffer~`, `adsr~` and `lores~` are and you can patch them.

Over 10 episodes this tutorial translates **the concepts you already understand**, one at a time, into Python. Each episode starts from a Max object you know, builds its Python counterpart, and lets you **hear the result**.

After 10 episodes you will have:

- a complete wavetable synth you wrote yourself (oscillator + filter + two envelopes + modulation), about 100 lines of Python in total
- a parameter and preset system
- the ability to generate "sound ↔ parameter" datasets in bulk
- a way to send wavetables and presets back to Max

### Why a Max user should learn this

Not to replace Max. The two are good at different things:

| | Max / RNBO | Python |
|---|---|---|
| Playing live, turning knobs, building instruments | ✅ excellent | ❌ poor |
| Auto-generating ten thousand sounds with their parameters | 😖 awkward | ✅ one loop |
| Analysing sound, plotting, experimenting | limited | ✅ excellent |
| Machine learning | essentially not possible | ✅ where the mainstream tools live |

If you want to do audio analysis, build datasets, or head toward audio machine learning, Python is unavoidable. And "already understanding synths" is the best starting point for it — you do not have to learn DSP concepts and a programming language at once, only the latter.

### What this tutorial does **not** teach

- real-time audio (the Python synth "computes, then plays"; you cannot play it live)
- graphical interfaces or plugins (VST / AU)
- the whole Python language — only the small part needed for a synth
- mathematical derivations — filters and the FFT are used as ready-made objects
'''),
        M(r'''
## 2. 难度

### 你需要已经会的

- **Max 基础:** 知道 signal(带 `~` 的)和 message 的区别;用过 `phasor~`、`cycle~`、`buffer~`、`adsr~`、一个 filter
- **synth 基础:** 知道 oscillator、filter、envelope、LFO 各是干什么的
- 用过 `gen~` 更好(第 6 集会拿 `history` 做对照),没用过也能跟上

### 你 **不** 需要会的

- **Python:零基础可以。** 每个新写法第一次出现时都会解释,并且对上一个 Max object
- **数学:** 只用到加减乘除、`sin`、乘方。没有微积分,没有复数

### 每一集的难度和时间

| 集 | 主题 | 时间 | 难度 | 新的 Python 写法 |
|---|---|---|---|---|
| 1 | 声音就是一个 array | 25 分钟 | ★☆☆ | array、`[ ]` 取数、`def` 函数 |
| 2 | phase 与基本波形 | 25 分钟 | ★☆☆ | `%`、`np.where`、`for` 循环(初见) |
| 3 | wavetable oscillator | 30 分钟 | ★★☆ | 用 array 当编号去读另一个 array |
| 4 | wavetable position | 25 分钟 | ★★☆ | 二维 array |
| 5 | envelope | 25 分钟 | ★★☆ | `np.interp`、list 和 `append` |
| 6 | filter 与 sample 循环 | 30 分钟 | ★★★ | 带 "记忆" 的 `for` 循环 |
| 7 | modulation | 30 分钟 | ★★★ | `np.cumsum`、`2 ** x` |
| 8 | 完整的 synth 与 preset | 25 分钟 | ★★☆ | `dict` |
| 9 | 批量渲染 | 25 分钟 | ★★☆ | 随机数、读写文件、f-string |
| 10 | 看见声音,再回到 Max | 25 分钟 | ★★☆ | spectrum、spectrogram |

全部加起来大约 4.5 小时。**建议一次只做一集。**

第 6、7 集是最难的两集(filter 的循环、pitch modulation 的 phase 累加)。如果卡住,这很正常 — 那两集的概念在 Max 里是被 audio engine 藏起来的,这是你第一次亲手写出来。

### 每一集的结构

1. **开头:** 这一集控制哪个音乐元素、对应哪个 Max patch、你会听到什么
2. **正文:** 每一步都是 "先用小数字走一遍 → 再用真实的数字 → 听 → 看图"
3. **代码里的 `#` 注释:** 难的那几行旁边都写了它在干什么
4. **常见错误:** 报错信息和原因的对照表
5. **练习:** 3 道,答案折叠在下面(点 "答案" 展开)
6. **小结:** Max ↔ Python 对照表
''', r'''
## 2. Difficulty

### What you need to know already

- **Max basics:** the difference between signals (objects with `~`) and messages; some use of `phasor~`, `cycle~`, `buffer~`, `adsr~` and a filter
- **Synth basics:** what an oscillator, a filter, an envelope and an LFO each do
- Experience with `gen~` helps (Episode 6 uses `history` for comparison), but you can follow without it

### What you do **not** need

- **Python: none at all is fine.** Each new piece of syntax is explained on first use and matched to a Max object
- **Maths:** only arithmetic, `sin` and powers. No calculus, no complex numbers

### Difficulty and time per episode

| Ep. | Topic | Time | Difficulty | New Python |
|---|---|---|---|---|
| 1 | sound is an array | 25 min | ★☆☆ | arrays, `[ ]` indexing, `def` functions |
| 2 | phase and basic waveforms | 25 min | ★☆☆ | `%`, `np.where`, first `for` loop |
| 3 | wavetable oscillator | 30 min | ★★☆ | using an array as indices into another |
| 4 | wavetable position | 25 min | ★★☆ | 2-D arrays |
| 5 | envelope | 25 min | ★★☆ | `np.interp`, lists and `append` |
| 6 | filter and the sample loop | 30 min | ★★★ | a `for` loop with "memory" |
| 7 | modulation | 30 min | ★★★ | `np.cumsum`, `2 ** x` |
| 8 | the full synth and presets | 25 min | ★★☆ | `dict` |
| 9 | batch rendering | 25 min | ★★☆ | random numbers, file I/O, f-strings |
| 10 | seeing sound, back to Max | 25 min | ★★☆ | spectrum, spectrogram |

About 4.5 hours in total. **One episode per sitting is recommended.**

Episodes 6 and 7 are the two hardest (the filter loop, and phase accumulation for pitch modulation). Getting stuck there is normal — in Max those ideas are hidden inside the audio engine, and this is the first time you write them out by hand.

### How each episode is laid out

1. **Opening:** which musical element it controls, the matching Max patch, what you will hear
2. **Body:** every step goes "small numbers first → real numbers → listen → look at a plot"
3. **`#` comments in the code:** the tricky lines say what they are doing right beside them
4. **Common mistakes:** a table of error messages and their causes
5. **Exercises:** three, with answers folded underneath (click "Answer" to open)
6. **Recap:** a Max ↔ Python table
'''),
        M(r'''
## 3. 装环境

需要五样东西:

| | 作用 | 最低版本 |
|---|---|---|
| **Python** | 语言本身 | 3.9 |
| **JupyterLab** | 打开和运行 `.ipynb` notebook 的程序 | 任意较新版本 |
| **numpy** | 对 array 做运算 | 1.20 |
| **scipy** | 读写 wav 文件 | 1.6 |
| **matplotlib** | 画图 | 3.4 |

(这套 notebook 是在 Python 3.14、numpy 2.4、scipy 1.18 上测试的。)

下面三种方式选 **一种** 就行。

### 方式 A:Anaconda(推荐,最省事)

Anaconda 是一个安装包,上面五样东西它 **全都自带**。

1. 去 anaconda.com 下载 Anaconda Distribution(免费),按提示安装
2. 打开 **Anaconda Navigator**,点 **JupyterLab** 下面的 Launch
3. 浏览器里会打开 JupyterLab。在左边的文件栏里找到这个教程的文件夹,双击 `01_…ipynb`

### 方式 B:已经有 Python,用 pip 装

打开 Terminal(macOS)或命令提示符(Windows),运行:

```
python3 -m pip install numpy scipy matplotlib jupyterlab
```

装好之后,先 `cd` 到这个教程的文件夹,再运行:

```
jupyter lab
```

### 方式 C:不想装任何东西 — Google Colab

1. 打开 colab.research.google.com(需要 Google 账号)
2. File → Upload notebook,把某一集的 `.ipynb` 传上去
3. numpy、scipy、matplotlib 都已经装好,可以直接运行

注意:Colab 里第 1、9、10 集存出来的文件(wav、json)是存在 Colab 的临时空间里的,要从左边的文件栏手动下载。

### 用 VS Code 也可以

装好 Python 和上面的库之后,在 VS Code 里装 **Jupyter** 扩展,就能直接打开 `.ipynb`。
''', r'''
## 3. Setting up the environment

Five things are needed:

| | What it does | Minimum version |
|---|---|---|
| **Python** | the language itself | 3.9 |
| **JupyterLab** | the program that opens and runs `.ipynb` notebooks | any recent version |
| **numpy** | math on arrays | 1.20 |
| **scipy** | reading and writing wav files | 1.6 |
| **matplotlib** | plotting | 3.4 |

(These notebooks were tested with Python 3.14, numpy 2.4 and scipy 1.18.)

Pick **one** of the three routes below.

### Route A: Anaconda (recommended, least effort)

Anaconda is one installer that **includes all five** of the above.

1. Download Anaconda Distribution (free) from anaconda.com and install it
2. Open **Anaconda Navigator** and click Launch under **JupyterLab**
3. JupyterLab opens in your browser. Find this tutorial's folder in the file panel on the left and double-click `01_….ipynb`

### Route B: you already have Python — install with pip

Open Terminal (macOS) or Command Prompt (Windows) and run:

```
python3 -m pip install numpy scipy matplotlib jupyterlab
```

When that is done, `cd` into this tutorial's folder and run:

```
jupyter lab
```

### Route C: install nothing — Google Colab

1. Open colab.research.google.com (a Google account is required)
2. File → Upload notebook, and upload an episode's `.ipynb`
3. numpy, scipy and matplotlib are already installed, so it runs straight away

Note: in Colab the files that Episodes 1, 9 and 10 save (wav, json) land in Colab's temporary storage and have to be downloaded by hand from the file panel on the left.

### VS Code works too

With Python and the libraries above installed, add the **Jupyter** extension in VS Code and it opens `.ipynb` files directly.
'''),
        M(r'''
## 4. Notebook 的基本操作

- 每个灰色格子叫一个 **cell**。点进去,按 **Shift + Enter** 运行它,并跳到下一个
- **从上往下按顺序运行。** 后面的 cell 会用到前面算出来的东西
- 改了某个 cell 里的数字之后,要 **重新运行那个 cell 和它下面的 cell**,改动才生效。这和 Max 不一样:Max 改了立刻生效,这里要 "重新算一遍"
- 想从头来过:菜单 **Kernel → Restart Kernel and Run All Cells**
- 想自己试点东西:选中一个 cell,按 **B** 在下面加一个空 cell
- 文字部分(像这一段)双击会进入编辑状态,按 Shift + Enter 就恢复了

## 5. 检查环境

运行下面这个 cell。

**应该看到:** 四行版本号,最后一行是 `everything is installed`。

如果出现 `ModuleNotFoundError: No module named '...'`,说明那个库没装上,回到第 3 节。
''', r'''
## 4. Notebook basics

- Each grey box is a **cell**. Click into it and press **Shift + Enter** to run it and move to the next
- **Run from top to bottom, in order.** Later cells use what earlier cells computed
- After changing a number in a cell, **re-run that cell and the cells below it** for the change to take effect. This differs from Max: there a change is live, here you "recompute"
- To start over: menu **Kernel → Restart Kernel and Run All Cells**
- To try something of your own: select a cell and press **B** to add an empty one below
- Text sections (like this one) go into edit mode on a double-click; Shift + Enter restores them

## 5. Checking the environment

Run the cell below.

**You should see:** four version lines, ending with `everything is installed`.

If you get `ModuleNotFoundError: No module named '...'`, that library is missing; go back to section 3.
'''),
        C(r'''
import sys
import numpy as np
import scipy
import matplotlib
import matplotlib.pyplot as plt
from IPython.display import Audio

print("Python     ", sys.version.split()[0])
print("numpy      ", np.__version__)
print("scipy      ", scipy.__version__)
print("matplotlib ", matplotlib.__version__)
print("everything is installed")
'''),
        M(r'''
### 能不能出声

⚠️ 先把系统音量调小一点。

运行下面的 cell,会出现一个播放器。按播放键。

**应该听到:** 两声短促的 "哔",第二声比第一声高。

现在不需要看懂这段代码 — 第 1 集会一行一行讲。
''', r'''
### Can it make sound

⚠️ Turn your system volume down a little first.

Run the cell below; a player appears. Press play.

**You should hear:** two short beeps, the second higher than the first.

You do not need to understand this code yet — Episode 1 goes through it line by line.
'''),
        C(r'''
sr = 44100
t = np.arange(int(sr * 0.25)) / sr                         # [[0.25 秒的时间表||a time table of 0.25 seconds]]
fade = np.interp(t, [0, 0.01, 0.24, 0.25], [0, 1, 1, 0])   # [[头尾各 10 ms 的 fade,防止 click||10 ms fades at both ends to prevent clicks]]
beep_low = np.sin(2 * np.pi * 440 * t) * fade
beep_high = np.sin(2 * np.pi * 660 * t) * fade
gap = np.zeros(int(sr * 0.1))                              # [[0.1 秒静音||0.1 seconds of silence]]

Audio(0.3 * np.concatenate([beep_low, gap, beep_high]), rate=sr, normalize=False)
'''),
        M(r'''
### 能不能画图

**应该看到:** 一张图,里面是几个周期的 sine。
''', r'''
### Can it plot

**You should see:** a plot showing a few cycles of a sine.
'''),
        C(r'''
plt.figure(figsize=(9, 2.5))
plt.plot(t[:400], beep_low[:400])
plt.xlabel("time (s)")
plt.title("if you can see this, plotting works")
plt.show()
'''),
        M(r'''
## 6. 常见问题

| 现象 | 怎么办 |
|---|---|
| `ModuleNotFoundError` | 库没装。方式 B 的那行 pip 命令再跑一次;用 Anaconda 的话确认是从 Anaconda Navigator 启动的 JupyterLab |
| 播放器出来了但没声音 | 检查浏览器这个标签页有没有被静音;检查系统输出设备;换 Chrome 试试 |
| 图没有显示 | 在那个 cell 最上面加一行 `%matplotlib inline` 再运行 |
| cell 左边一直是 `[*]` | 还在算。第 6 集以后有的 cell 要几秒钟。超过一分钟就 Kernel → Restart |
| `NameError: name '...' is not defined` | 跳过了前面的 cell。Kernel → Restart Kernel and Run All Cells |
| 图里的中文是方框 | 这套 notebook 图里的文字全是英文,就是为了避开这个问题 |

## 7. 这套 notebook 会生成的文件

都写在 notebook 所在的文件夹里,可以随时删掉:

| 集 | 文件 |
|---|---|
| 1 | `ep01_melody.wav` |
| 9 | `dataset/`(20 个 wav + `params.json`) |
| 10 | `export/wavetable.wav`、`export/presets.json` |

## 8. 目录

| 集 | 文件 | Max 里的对应 |
|---|---|---|
| 0 | 开始之前(本篇) | — |
| 1 | 没有 `dac~`:声音就是一个 array | `cycle~`、`dac~`、`scope~` |
| 2 | `phasor~`:phase 与基本波形 | `phasor~` |
| 3 | `buffer~` + `wave~`:wavetable oscillator | `buffer~`、`wave~` |
| 4 | Wavetable position:在波形之间 morph | Serum 的 WT POS |
| 5 | `adsr~`:envelope | `adsr~`、`*~` |
| 6 | `lores~`:filter 与 sample 循环 | `onepole~`、`lores~`、gen~ `history` |
| 7 | Modulation:用 signal 控制参数 | signal 接参数 inlet、LFO |
| 8 | 一个函数就是一个 synth:参数与 preset | RNBO patch、`param` |
| 9 | 批量渲染:Max 里很难做的事 | — |
| 10 | 看见声音,再回到 Max | `spectroscope~`、`buffer~ read`、`dict read` |

每一集都可以单独打开运行(需要的前几集的函数会在开头的 "工具箱" cell 里原样带上),但内容是按顺序讲的,**第一次请按顺序学。**

环境检查通过了,就打开第 1 集。
''', r'''
## 6. Troubleshooting

| Symptom | What to do |
|---|---|
| `ModuleNotFoundError` | A library is missing. Run the pip line from Route B again; with Anaconda, make sure JupyterLab was launched from Anaconda Navigator |
| The player appears but there is no sound | Check whether the browser tab is muted; check the system output device; try Chrome |
| Plots do not appear | Add the line `%matplotlib inline` at the top of that cell and run it again |
| A cell shows `[*]` on the left for a long time | It is still computing. From Episode 6 on some cells take a few seconds. Beyond a minute, use Kernel → Restart |
| `NameError: name '...' is not defined` | An earlier cell was skipped. Kernel → Restart Kernel and Run All Cells |

## 7. Files these notebooks create

All are written to the notebook's own folder and can be deleted at any time:

| Ep. | Files |
|---|---|
| 1 | `ep01_melody.wav` |
| 9 | `dataset/` (20 wavs + `params.json`) |
| 10 | `export/wavetable.wav`, `export/presets.json` |

## 8. Contents

| Ep. | Notebook | Max counterpart |
|---|---|---|
| 0 | Before you start (this one) | — |
| 1 | No `dac~`: sound is an array | `cycle~`, `dac~`, `scope~` |
| 2 | `phasor~`: phase and basic waveforms | `phasor~` |
| 3 | `buffer~` + `wave~`: the wavetable oscillator | `buffer~`, `wave~` |
| 4 | Wavetable position: morphing between waveforms | Serum's WT POS |
| 5 | `adsr~`: the envelope | `adsr~`, `*~` |
| 6 | `lores~`: the filter and the sample loop | `onepole~`, `lores~`, gen~ `history` |
| 7 | Modulation: signals controlling parameters | signals into parameter inlets, LFO |
| 8 | One function is a synth: parameters and presets | RNBO patch, `param` |
| 9 | Batch rendering: what is hard in Max | — |
| 10 | Seeing sound, and back to Max | `spectroscope~`, `buffer~ read`, `dict read` |

Every episode can be opened and run on its own (the functions it needs from earlier episodes are carried along in a "toolbox" cell at the top), but the material builds up in order, so **follow the order the first time through.**

Once the environment check passes, open Episode 1.
'''),
    ])
