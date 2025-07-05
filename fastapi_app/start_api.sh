#!/bin/bash
#删除上次音频文件
rm -rf /workspace/index-tts-api/outputs/*  

cd /tmp/ && find . -empty -type d -delete 

rm -rf /tmp/gradio/* 
source $(conda info --base)/etc/profile.d/conda.sh
conda activate index-tts
python main.py
