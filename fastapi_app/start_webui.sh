#!/bin/bash
cd /workspace/index-tts-api
source $(conda info --base)/etc/profile.d/conda.sh
conda activate index-tts
python ./webui.py
