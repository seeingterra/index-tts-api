#!/bin/bash
cd /workspace/index-tts-api/fastapi_app/
source $(conda info --base)/etc/profile.d/conda.sh
conda activate index-tts
python main.py
