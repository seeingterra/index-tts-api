FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

SHELL ["/bin/bash", "-l", "-c"]
WORKDIR /python-docker

# 更新软件源并安装必要工具
RUN echo "deb http://mirrors.aliyun.com/ubuntu/ jammy main restricted universe multiverse" > /etc/apt/sources.list && \
    echo "deb http://mirrors.aliyun.com/ubuntu/ jammy-security main restricted universe multiverse" >> /etc/apt/sources.list && \
    echo "deb http://mirrors.aliyun.com/ubuntu/ jammy-updates main restricted universe multiverse" >> /etc/apt/sources.list && \
    apt-get update -y && \
    apt-get install -y --no-install-recommends ffmpeg wget git && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 安装Miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p /opt/conda && \
    rm /tmp/miniconda.sh

# 设置环境变量
ENV PATH=/opt/conda/bin:$PATH
# 初始化Conda
RUN /opt/conda/bin/conda init bash

# 设置Conda环境
RUN /opt/conda/bin/conda create -n index-tts python=3.10 -y && \
    echo "conda activate index-tts" >> ~/.bashrc

ENV PATH="/opt/conda/envs/index-tts/bin:$PATH"

COPY requirements.txt .
RUN conda run -n index-tts pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

RUN apt-get update -y
RUN apt-get install -y  build-essential
RUN apt-get install -y cuda-toolkit-11-8
RUN pip install deepspeed -i https://mirrors.aliyun.com/pypi/simple/


COPY fastapi_app/requirements.txt ./requirements-fastapi.txt
# 安装依赖时使用正确的文件名
RUN pip install -r requirements-fastapi.txt -i https://mirrors.aliyun.com/pypi/simple/

RUN apt-get install -y curl

EXPOSE 7860
EXPOSE 8010


CMD ["bash"]
