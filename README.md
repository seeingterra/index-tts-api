<div align="center">
<img src='assets/index_icon.png' width="250"/>
</div>

<div align="center">
<a href="docs/README_zh.md" style="font-size: 24px">简体中文</a> | 
<a href="README.md" style="font-size: 24px">English</a>
Discord: https://discord.gg/uT32E7KDmy
## 👉🏻 IndexTTS2 👈🏻

<center><h3>IndexTTS2: A Breakthrough in Emotionally Expressive and Duration-Controlled Auto-Regressive Zero-Shot Text-to-Speech</h3></center>

2. Clone the repository and fetch large files (Windows PowerShell):

```powershell
git clone https://github.com/index-tts/index-tts.git
cd index-tts
git lfs pull
```
  <a href='https://arxiv.org/abs/2506.21619'>
    <img src='https://img.shields.io/badge/ArXiv-2506.21619-red?logo=arxiv'/>
If you prefer using a mirror for faster downloads, pass the `-i` option to pip. Example:

```powershell
python -m pip install -e . -i https://mirrors.aliyun.com/pypi/simple/
```
<!-- mirrors omitted for brevity -->
  </a>
  <a href='https://huggingface.co/IndexTeam/IndexTTS-2'>
    <img src='https://img.shields.io/badge/HuggingFace-Model-blue?logo=huggingface' />
  </a>
  <br/>
  <!--a href='https://modelscope.cn/studios/IndexTeam/IndexTTS-Demo'>
    <img src='https://img.shields.io/badge/ModelScope-Demo-purple?logo=modelscope'/>
  </a-->
  <a href='https://modelscope.cn/models/IndexTeam/IndexTTS-2'>
    <img src='https://img.shields.io/badge/ModelScope-Model-purple?logo=modelscope'/>
  </a>
</div>


### Abstract

Existing autoregressive large-scale text-to-speech (TTS) models have advantages in speech naturalness, but their token-by-token generation mechanism makes it difficult to precisely control the duration of synthesized speech. This becomes a significant limitation in applications requiring strict audio-visual synchronization, such as video dubbing.

This paper introduces IndexTTS2, which proposes a novel, general, and autoregressive model-friendly method for speech duration control.

The method supports two generation modes: one explicitly specifies the number of generated tokens to precisely control speech duration; the other freely generates speech in an autoregressive manner without specifying the number of tokens, while faithfully reproducing the prosodic features of the input prompt.

Furthermore, IndexTTS2 achieves disentanglement between emotional expression and speaker identity, enabling independent control over timbre and emotion. In the zero-shot setting, the model can accurately reconstruct the target timbre (from the timbre prompt) while perfectly reproducing the specified emotional tone (from the style prompt).

To enhance speech clarity in highly emotional expressions, we incorporate GPT latent representations and design a novel three-stage training paradigm to improve the stability of the generated speech. Additionally, to lower the barrier for emotional control, we designed a soft instruction mechanism based on text descriptions by fine-tuning Qwen3, effectively guiding the generation of speech with the desired emotional orientation.

Finally, experimental results on multiple datasets show that IndexTTS2 outperforms state-of-the-art zero-shot TTS models in terms of word error rate, speaker similarity, and emotional fidelity. Audio samples are available at: <a href="https://index-tts.github.io/index-tts2.github.io/">IndexTTS2 demo page</a>.
Run the web UI with your Python interpreter (after activating the project venv):

```powershell
python webui.py
```


```powershell
python webui.py -h
```
### Feel IndexTTS2

<div align="center">

**IndexTTS2: The Future of Voice, Now Generating**

[![IndexTTS2 Demo](assets/IndexTTS2-video-pic.png)](https://www.bilibili.com/video/BV136a9zqEk5)

*Click the image to watch the IndexTTS2 introduction video.*

</div>


### Contact

QQ Group：553460296(No.1) 663272642(No.4)  \
Discord：https://discord.gg/uT32E7KDmy  \
### ⚙️ Environment Setup (Windows 11 - recommended)

1. Ensure that you have both [git](https://git-scm.com/downloads) and
  [git-lfs](https://git-lfs.com/) on your system.

The Git-LFS plugin must also be enabled for your user account:

```powershell
git lfs install
```

2. Clone the repository and fetch large files:

```powershell
git clone https://github.com/index-tts/index-tts.git && cd index-tts
git lfs pull
```

3. Create and activate a Python virtual environment (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

4. Install required dependencies:

Install the project in editable mode so the `indextts` package is importable
and easy to develop against. For optional features (webui, deepspeed), install
the relevant extras explicitly.

```powershell
python -m pip install -e .
# Optional extras:
python -m pip install -e .[webui]
python -m pip install -e .[deepspeed]
```

If you prefer using a mirror for faster downloads, pass the `-i` option to pip,
for example:

```powershell
python -m pip install -e . -i https://mirrors.aliyun.com/pypi/simple/
```

5. Download the required models (HuggingFace or ModelScope):

HuggingFace (requires `huggingface_hub`):

```powershell
python -m pip install huggingface_hub
hf download IndexTeam/IndexTTS-2 --local-dir checkpoints
```

ModelScope:

```powershell
python -m pip install modelscope
modelscope download --model IndexTeam/IndexTTS-2 --local_dir checkpoints
```
local mirrors in China (choose one mirror from the list below):

```powershell
# Use pip with a mirror; example installing the project in editable mode with a mirror:
python -m pip install -e . --index-url https://mirrors.aliyun.com/pypi/simple/

python -m pip install -e . --index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
```

> [!TIP]
> **Available Extra Features:**
> 
> - `--all-extras`: Automatically adds *every* extra feature listed below. You can
>   remove this flag if you want to customize your installation choices.
> - `--extra webui`: Adds WebUI support (recommended).
> - `--extra deepspeed`: Adds DeepSpeed support (may speed up inference on some
>   systems).

> [!IMPORTANT]
> **Important (Windows):** The DeepSpeed library may be difficult to install for
> some Windows users. You can skip it by removing the `--all-extras` flag. If you
> want any of the other extra features above, you can manually add their specific
> feature flags instead.
> 
> **Important (Linux/Windows):** If you see an error about CUDA during the installation,
> please ensure that you have installed NVIDIA's [CUDA Toolkit](https://developer.nvidia.com/cuda-toolkit)
> version **12.8** (or newer) on your system.

5. Download the required models:

Download via `huggingface-cli`:

```powershell
python -m pip install huggingface_hub[cli]

hf download IndexTeam/IndexTTS-2 --local-dir=checkpoints
```

Or download via `modelscope`:

```powershell
python -m pip install modelscope

modelscope download --model IndexTeam/IndexTTS-2 --local_dir checkpoints
```

### Windows PowerShell helper scripts

This repository includes small PowerShell helper scripts under `fastapi_app/` that create a `.venv`, install the project's `requirements.txt`, and start the API or Web UI on Windows PowerShell.

- `fastapi_app\start_api.ps1` — create/activate `.venv`, install requirements, and start the FastAPI server (uvicorn).
- `fastapi_app\start_webui.ps1` — create/activate `.venv`, install requirements, and run the `webui.py` demo.
- `fastapi_app\start_all.ps1` — run both scripts as background jobs.

Additionally, there is a helper for creating a Python 3.11 environment that installs the full set of pinned dependencies (including `numba`):

- `scripts\setup_venv_py311.ps1` — finds a Python 3.11 interpreter (or accepts `-PythonCmd`), creates `.venv`, installs `requirements.txt`, writes `requirements-lock.txt`, and runs a brief smoke test.

Usage (PowerShell):

```powershell
# Create a Python 3.11 venv and install everything (if Python 3.11 is available via 'py -3.11')
.\scripts\setup_venv_py311.ps1

# Or pass an explicit python path:
.\scripts\setup_venv_py311.ps1 -PythonCmd 'C:\\Program Files\\Python311\\python.exe'
```

These helpers are convenience wrappers for Windows users; you can also manage the virtual environment manually as described above.


> [!NOTE]
> In addition to the above models, some small models will also be automatically
> downloaded when the project is run for the first time. If your network environment
> has slow access to HuggingFace, it is recommended to execute the following
> command before running the code:
> 
> 除了以上模型外，项目初次运行时还会自动下载一些小模型，如果您的网络环境访问HuggingFace的速度较慢，推荐执行：
> 
> ```bash
> export HF_ENDPOINT="https://hf-mirror.com"
> ```


#### 🖥️ Checking PyTorch GPU Acceleration

If you need to diagnose your environment to see which GPUs are detected,
you can use our included utility to check your system. Run it from the repo root after activating your venv:

```powershell
.\.venv\Scripts\Activate.ps1
python tools/gpu_check.py
```

### Windows: PyTorch import errors (WinError 126)

If you see errors like:

```
IMPORT-ERROR torch: [WinError 126] The specified module could not be found. Error loading "...\\torch_python.dll" or one of its dependencies.
```

This commonly means one of two things: the Microsoft Visual C++ runtime is missing, or the installed PyTorch wheel expects CUDA libraries that are not present on your system. Recommended fixes:

1. Install the Microsoft Visual C++ Redistributable (2015-2022) x64:

  - https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist

2. If you don't have CUDA or want a CPU-only installation, install the CPU wheels for PyTorch and torchaudio instead of letting pip choose a GPU/CUDA wheel. Example (PowerShell, Python 3.11):

```powershell
python -m pip install --upgrade pip
python -m pip install --index-url https://download.pytorch.org/whl/cpu "torch==2.8.*+cpu" "torchaudio==2.8.*+cpu" -f https://download.pytorch.org/whl/torch_stable.html
```

3. If you have a specific CUDA version, use the corresponding PyTorch CUDA wheel. Example for CUDA 12.1 (adjust the +cu121 tag to match the desired CUDA version):

```powershell
python -m pip install --index-url https://download.pytorch.org/whl/cu121 "torch==2.8.*+cu121" "torchaudio==2.8.*+cu121" -f https://download.pytorch.org/whl/torch_stable.html
```

4. If you change the PyTorch wheel or the interpreter, recreate the `.venv` (delete and re-run `scripts\setup_venv_py311.ps1` or recreate manually) so all binary wheels match the interpreter ABI.

For the most up-to-date install commands tailored to your OS, CUDA and Python version, consult the official instructions at https://pytorch.org/get-started/locally/.



### 🔥 IndexTTS2 Quickstart

#### 🌐 Web Demo

```bash
uv run webui.py
```

Open your browser and visit `http://127.0.0.1:7860` to see the demo.

You can also adjust the settings to enable features such as FP16 inference (lower
VRAM usage), DeepSpeed acceleration, compiled CUDA kernels for speed, etc. All
available options can be seen via the following command:

```bash
uv run webui.py -h
```

Have fun!

> [!IMPORTANT]
> It can be very helpful to use **FP16** (half-precision) inference. It is faster
> and uses less VRAM, with a very small quality loss.
> 
> **DeepSpeed** *may* also speed up inference on some systems, but it could also
> make it slower. The performance impact is highly dependent on your specific
> hardware, drivers and operating system. Please try with and without it,
> to discover what works best on your personal system.


#### 📝 Using IndexTTS2 in Python

To run scripts, create and activate a Python virtual environment so the project's package is importable and scripts run with the venv interpreter.

Example (PowerShell) – create and activate a venv, install the project, then run the script:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .

# Run the script (editable install makes the package importable):
python indextts\infer_v2.py
```

Note: this repository historically included helper commands for the 'uv' environment manager; the recommended, cross-platform workflow is to use a Python virtual environment (`venv`) and pip as shown above.

Here are several examples of how to use IndexTTS2 in your own scripts:

1. Synthesize new speech with a single reference audio file (voice cloning):

```python
from indextts.infer_v2 import IndexTTS2
tts = IndexTTS2(cfg_path="checkpoints/config.yaml", model_dir="checkpoints", use_fp16=False, use_cuda_kernel=False, use_deepspeed=False)
text = "Translate for me, what is a surprise!"
tts.infer(spk_audio_prompt='examples/voice_01.wav', text=text, output_path="gen.wav", verbose=True)
```

2. Using a separate, emotional reference audio file to condition the speech synthesis:

```python
from indextts.infer_v2 import IndexTTS2
tts = IndexTTS2(cfg_path="checkpoints/config.yaml", model_dir="checkpoints", use_fp16=False, use_cuda_kernel=False, use_deepspeed=False)
text = "酒楼丧尽天良，开始借机竞拍房间，哎，一群蠢货。"
tts.infer(spk_audio_prompt='examples/voice_07.wav', text=text, output_path="gen.wav", emo_audio_prompt="examples/emo_sad.wav", verbose=True)
```

3. When an emotional reference audio file is specified, you can optionally set
   the `emo_alpha` to adjust how much it affects the output.
   Valid range is `0.0 - 1.0`, and the default value is `1.0` (100%):

```python
from indextts.infer_v2 import IndexTTS2
tts = IndexTTS2(cfg_path="checkpoints/config.yaml", model_dir="checkpoints", use_fp16=False, use_cuda_kernel=False, use_deepspeed=False)
text = "酒楼丧尽天良，开始借机竞拍房间，哎，一群蠢货。"
tts.infer(spk_audio_prompt='examples/voice_07.wav', text=text, output_path="gen.wav", emo_audio_prompt="examples/emo_sad.wav", emo_alpha=0.9, verbose=True)
```

4. It's also possible to omit the emotional reference audio and instead provide
   an 8-float list specifying the intensity of each emotion, in the following order:
   `[happy, angry, sad, afraid, disgusted, melancholic, surprised, calm]`.
   You can additionally use the `use_random` parameter to introduce stochasticity
   during inference; the default is `False`, and setting it to `True` enables
   randomness:

> [!NOTE]
> Enabling random sampling will reduce the voice cloning fidelity of the speech
> synthesis.

```python
from indextts.infer_v2 import IndexTTS2
tts = IndexTTS2(cfg_path="checkpoints/config.yaml", model_dir="checkpoints", use_fp16=False, use_cuda_kernel=False, use_deepspeed=False)
text = "哇塞！这个爆率也太高了！欧皇附体了！"
tts.infer(spk_audio_prompt='examples/voice_10.wav', text=text, output_path="gen.wav", emo_vector=[0, 0, 0, 0, 0, 0, 0.45, 0], use_random=False, verbose=True)
```

5. Alternatively, you can enable `use_emo_text` to guide the emotions based on
   your provided `text` script. Your text script will then automatically
   be converted into emotion vectors.
   It's recommended to use `emo_alpha` around 0.6 (or lower) when using the text
   emotion modes, for more natural sounding speech.
   You can introduce randomness with `use_random` (default: `False`;
   `True` enables randomness):

```python
from indextts.infer_v2 import IndexTTS2
tts = IndexTTS2(cfg_path="checkpoints/config.yaml", model_dir="checkpoints", use_fp16=False, use_cuda_kernel=False, use_deepspeed=False)
text = "快躲起来！是他要来了！他要来抓我们了！"
tts.infer(spk_audio_prompt='examples/voice_12.wav', text=text, output_path="gen.wav", emo_alpha=0.6, use_emo_text=True, use_random=False, verbose=True)
```

6. It's also possible to directly provide a specific text emotion description
   via the `emo_text` parameter. Your emotion text will then automatically be
   converted into emotion vectors. This gives you separate control of the text
   script and the text emotion description:

```python
from indextts.infer_v2 import IndexTTS2
tts = IndexTTS2(cfg_path="checkpoints/config.yaml", model_dir="checkpoints", use_fp16=False, use_cuda_kernel=False, use_deepspeed=False)
text = "快躲起来！是他要来了！他要来抓我们了！"
emo_text = "你吓死我了！你是鬼吗？"
tts.infer(spk_audio_prompt='examples/voice_12.wav', text=text, output_path="gen.wav", emo_alpha=0.6, use_emo_text=True, emo_text=emo_text, use_random=False, verbose=True)
```


### Legacy: IndexTTS1 User Guide

You can also use our previous IndexTTS1 model by importing a different module:

```python
from indextts.infer import IndexTTS
tts = IndexTTS(model_dir="checkpoints",cfg_path="checkpoints/config.yaml")
voice = "examples/voice_07.wav"
text = "大家好，我现在正在bilibili 体验 ai 科技，说实话，来之前我绝对想不到！AI技术已经发展到这样匪夷所思的地步了！比如说，现在正在说话的其实是B站为我现场复刻的数字分身，简直就是平行宇宙的另一个我了。如果大家也想体验更多深入的AIGC功能，可以访问 bilibili studio，相信我，你们也会吃惊的。"
tts.infer(voice, text, 'gen.wav')
```

For more detailed information, see [README_INDEXTTS_1_5](archive/README_INDEXTTS_1_5.md),
or visit the IndexTTS1 repository at <a href="https://github.com/index-tts/index-tts/tree/v1.5.0">index-tts:v1.5.0</a>.


## Our Releases and Demos

### IndexTTS2: [[Paper]](https://arxiv.org/abs/2506.21619); [[Demo]](https://index-tts.github.io/index-tts2.github.io/); [[HuggingFace]](https://huggingface.co/spaces/IndexTeam/IndexTTS-2-Demo)

### IndexTTS1: [[Paper]](https://arxiv.org/abs/2502.05512); [[Demo]](https://index-tts.github.io/); [[ModelScope]](https://modelscope.cn/studios/IndexTeam/IndexTTS-Demo); [[HuggingFace]](https://huggingface.co/spaces/IndexTeam/IndexTTS)


## Acknowledgements

1. [tortoise-tts](https://github.com/neonbjb/tortoise-tts)
2. [XTTSv2](https://github.com/coqui-ai/TTS)
3. [BigVGAN](https://github.com/NVIDIA/BigVGAN)
4. [wenet](https://github.com/wenet-e2e/wenet/tree/main)
5. [icefall](https://github.com/k2-fsa/icefall)
6. [maskgct](https://github.com/open-mmlab/Amphion/tree/main/models/tts/maskgct)
7. [seed-vc](https://github.com/Plachtaa/seed-vc)


## 📚 Citation

🌟 If you find our work helpful, please leave us a star and cite our paper.


IndexTTS2:

```
@article{zhou2025indextts2,
  title={IndexTTS2: A Breakthrough in Emotionally Expressive and Duration-Controlled Auto-Regressive Zero-Shot Text-to-Speech},
  author={Siyi Zhou, Yiquan Zhou, Yi He, Xun Zhou, Jinchao Wang, Wei Deng, Jingchen Shu},
  journal={arXiv preprint arXiv:2506.21619},
  year={2025}
}
```


IndexTTS:

```
@article{deng2025indextts,
  title={IndexTTS: An Industrial-Level Controllable and Efficient Zero-Shot Text-To-Speech System},
  author={Wei Deng, Siyi Zhou, Jingchen Shu, Jinchao Wang, Lu Wang},
  journal={arXiv preprint arXiv:2502.05512},
  year={2025},
  doi={10.48550/arXiv.2502.05512},
  url={https://arxiv.org/abs/2502.05512}
}
```
