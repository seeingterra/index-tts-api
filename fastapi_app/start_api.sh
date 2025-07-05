#!/bin/bash
source $(conda info --base)/etc/profile.d/conda.sh
conda activate index-tts
python main.py
