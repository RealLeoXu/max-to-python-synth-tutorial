# Max to Python Synth Tutorial

> I know a bit of Max, but I'm new to Python and wanted to learn it fast.
> So I had Claude make this tutorial. If you need it too, give it a try!
>
> — Leo

**[English](#english) · [中文](#中文)**

---

## English

### What this is

Each episode starts from a Max object you already know (`phasor~`, `buffer~`, `adsr~`, `lores~` ...), builds its Python counterpart, and lets you **hear the result**. After ten episodes you will have a complete wavetable synth you wrote yourself, a preset system, and the ability to generate "sound ↔ parameter" datasets in bulk.

- **You need:** Max basics (the difference between signals and messages; some use of oscillators, filters and envelopes)
- **You do not need:** any Python, or advanced maths
- **Not covered:** real-time audio, graphical interfaces, plugins

### Getting started

1. Download this repo (green **Code** button → Download ZIP), or `git clone` it
2. Set up the environment, one of:
   - **Anaconda** (least effort, includes everything): install it and launch JupyterLab from Anaconda Navigator
   - **pip:** `python3 -m pip install -r requirements.txt`, then `jupyter lab`
   - **Google Colab:** install nothing; upload a notebook at colab.research.google.com
3. Open [`English/00_before_you_start_purpose_difficulty_setup.ipynb`](English/00_before_you_start_purpose_difficulty_setup.ipynb). It has detailed setup instructions and an environment check. Once it makes sound, move on to Episode 1

> Viewing the notebooks on the GitHub website gives you **no sound and no plots**. This tutorial only makes sense when you download it and run it yourself.

### Contents

| Ep. | Notebook | Max counterpart | Time | Difficulty |
|---|---|---|---|---|
| 0 | [Before you start: purpose, difficulty, setup](English/00_before_you_start_purpose_difficulty_setup.ipynb) | — | 10 min | — |
| 1 | [No `dac~`: sound is an array](English/01_no_dac_sound_is_an_array.ipynb) | `cycle~`, `dac~`, `scope~` | 25 min | ★☆☆ |
| 2 | [`phasor~`: phase and basic waveforms](English/02_phasor_phase_and_basic_waveforms.ipynb) | `phasor~` | 25 min | ★☆☆ |
| 3 | [`buffer~` + `wave~`: the wavetable oscillator](English/03_buffer_and_wave_wavetable_oscillator.ipynb) | `buffer~`, `wave~` | 30 min | ★★☆ |
| 4 | [Wavetable position: morphing between waveforms](English/04_wavetable_position_morphing.ipynb) | Serum's WT POS | 25 min | ★★☆ |
| 5 | [`adsr~`: the envelope](English/05_adsr_envelope.ipynb) | `adsr~`, `*~` | 25 min | ★★☆ |
| 6 | [`lores~`: the filter and the sample loop](English/06_lores_filter_and_the_sample_loop.ipynb) | `onepole~`, `lores~`, gen~ `history` | 30 min | ★★★ |
| 7 | [Modulation: signals controlling parameters](English/07_modulation_signals_controlling_parameters.ipynb) | signals into parameter inlets, LFO | 30 min | ★★★ |
| 8 | [One function is a synth: parameters and presets](English/08_one_function_is_a_synth_params_and_presets.ipynb) | RNBO patch, `param` | 25 min | ★★☆ |
| 9 | [Batch rendering: what is hard in Max](English/09_batch_rendering_what_is_hard_in_max.ipynb) | — | 25 min | ★★☆ |
| 10 | [Seeing sound, and back to Max](English/10_seeing_sound_and_back_to_max.ipynb) | `spectroscope~`, `buffer~ read`, `dict read` | 25 min | ★★☆ |

About 4.5 hours in total. One episode per sitting, in order, is recommended.

### What an episode looks like

1. **Opening:** which musical element it controls, the matching Max patch, what you will hear
2. **Body:** small numbers first → real numbers → listen → look at a plot
3. **`#` comments:** the tricky lines say what they are doing right beside them
4. **Common mistakes:** a table of error messages and their causes
5. **Exercises:** three, with answers folded underneath
6. **Recap:** a Max ↔ Python table

### Notes

- This tutorial was written with the help of [Claude Code](https://claude.com/claude-code). All notebook code (exercise answers included) has been run successfully; the test environment was Python 3.14, numpy 2.4 and scipy 1.18.
- **The Max-side steps have not been tested in Max:** the gen~ codebox in Episode 6, and "how to use it in Max" in Episode 10 (`buffer~ read`, the `wave~` range, `get` on `dict`). If something there is wrong, please open an issue.
- Corrections and suggestions are welcome as issues or pull requests.

---

## 中文

### 这是什么

每一集从一个你熟悉的 Max object 出发(`phasor~`、`buffer~`、`adsr~`、`lores~` ……),做出它在 Python 里的对应物,并且**听到声音**。10 集之后,你会有一个自己写的完整 wavetable synth、一套 preset 系统,以及批量生成 "声音 ↔ 参数" 数据集的能力。

- **需要会的:** Max 基础(知道 signal 和 message 的区别,用过 oscillator / filter / envelope)
- **不需要会的:** Python(零基础可以)、高等数学
- **不教的:** 实时音频、图形界面、插件

### 怎么开始

1. 下载这个 repo(绿色的 **Code** 按钮 → Download ZIP),或者 `git clone`
2. 装环境,三选一:
   - **Anaconda**(最省事,什么都自带):装好后从 Anaconda Navigator 启动 JupyterLab
   - **pip**:`python3 -m pip install -r requirements.txt`,然后 `jupyter lab`
   - **Google Colab**:不用装任何东西,把 notebook 上传到 colab.research.google.com
3. 打开 [`中文/00_开始之前_目的_难度_环境.ipynb`](中文/00_开始之前_目的_难度_环境.ipynb),里面有详细的安装说明和一个环境检查。它能出声,就可以开始第 1 集

> 在 GitHub 网页上直接看 notebook 是**没有声音和图**的。这个教程要下载下来自己运行才有意义。

### 目录

| 集 | Notebook | Max 里的对应 | 时间 | 难度 |
|---|---|---|---|---|
| 0 | [开始之前:目的、难度、环境](中文/00_开始之前_目的_难度_环境.ipynb) | — | 10 分钟 | — |
| 1 | [没有 `dac~`:声音就是一个 array](中文/01_没有dac_声音就是array.ipynb) | `cycle~`、`dac~`、`scope~` | 25 分钟 | ★☆☆ |
| 2 | [`phasor~`:phase 与基本波形](中文/02_phasor_phase与基本波形.ipynb) | `phasor~` | 25 分钟 | ★☆☆ |
| 3 | [`buffer~` + `wave~`:wavetable oscillator](中文/03_buffer与wave_wavetable_oscillator.ipynb) | `buffer~`、`wave~` | 30 分钟 | ★★☆ |
| 4 | [Wavetable position:在波形之间 morph](中文/04_wavetable_position_在波形之间morph.ipynb) | Serum 的 WT POS | 25 分钟 | ★★☆ |
| 5 | [`adsr~`:envelope](中文/05_adsr_envelope.ipynb) | `adsr~`、`*~` | 25 分钟 | ★★☆ |
| 6 | [`lores~`:filter 与 sample 循环](中文/06_lores_filter与sample循环.ipynb) | `onepole~`、`lores~`、gen~ `history` | 30 分钟 | ★★★ |
| 7 | [Modulation:用 signal 控制参数](中文/07_modulation_用signal控制参数.ipynb) | signal 接参数 inlet、LFO | 30 分钟 | ★★★ |
| 8 | [一个函数就是一个 synth:参数与 preset](中文/08_一个函数就是一个synth_参数与preset.ipynb) | RNBO patch、`param` | 25 分钟 | ★★☆ |
| 9 | [批量渲染:Max 里很难做的事](中文/09_批量渲染_Max里很难做的事.ipynb) | — | 25 分钟 | ★★☆ |
| 10 | [看见声音,再回到 Max](中文/10_看见声音_再回到Max.ipynb) | `spectroscope~`、`buffer~ read`、`dict read` | 25 分钟 | ★★☆ |

全部大约 4.5 小时。建议一次只做一集,按顺序学。

### 每一集长什么样

1. **开头:** 这一集控制哪个音乐元素、对应哪个 Max patch、你会听到什么
2. **正文:** 先用小数字走一遍 → 再用真实的数字 → 听 → 看图
3. **`#` 注释:** 难的那几行旁边都写了它在干什么
4. **常见错误:** 报错信息和原因的对照表
5. **练习:** 3 道,答案折叠在下面
6. **小结:** Max ↔ Python 对照表

### 说明

- 这套教程是借助 [Claude Code](https://claude.com/claude-code) 写的。所有 notebook 的代码(包括练习答案)都实际运行通过,测试环境是 Python 3.14、numpy 2.4、scipy 1.18。
- **Max 那一侧的步骤没有在 Max 里实测过:** 第 6 集的 gen~ codebox,以及第 10 集里 "在 Max 里怎么读回去"(`buffer~ read`、`wave~` 的范围、`dict` 的 `get`)。如果你发现不对,欢迎开 issue。
- 发现错误或有建议,欢迎开 issue 或 pull request。

---

## For contributors / 修改内容

The notebooks are generated. Do not edit the `.ipynb` files directly; edit `_source/` and rebuild, so both languages stay in sync.

notebook 是生成出来的。不要直接改 `.ipynb`,请改 `_source/` 再重新生成,这样两种语言才会保持同步。

```
python3 _source/build.py .          # rebuild everything / 全部重新生成
python3 _source/build.py . 3 4      # only episodes 3 and 4 / 只生成第 3、4 集
```

- `_source/epNN.py` — one file per episode; each text cell is `M(中文, English)` / 每集一个文件
- `_source/common.py` — code shared across episodes / 各集共用的代码
- language-specific code comments are written `# [[中文||English]]` / 随语言变化的注释写法
