FROM ubuntu
RUN apt-get update

ENV DEBIAN_FRONTEND noninteractive

RUN echo "tzdata tzdata/Areas select America" | debconf-set-selections && echo "tzdata tzdata/Zones/America select Los_Angeles" | debconf-set-selections

# Install standard and python specific system dependencies
# Install dependencies -- Manual Addition
RUN apt-get update && apt-get install -y \
    wget \
    bzip2 \
    ca-certificates \
    libglib2.0-0 \
    libxext6 \
    libsm6 \
    libxrender1 \
    git \
    curl \
    software-properties-common

# Install Python 3.11 -- Manual Addition
RUN apt-get update && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.11 python3.11-venv python3.11-dev

# Install Anaconda -- Not compatible with Apple ARM machines
#RUN wget https://repo.anaconda.com/archive/Anaconda3-2023.09-0-Linux-x86_64.sh && \
#    bash Anaconda3-2023.09-0-Linux-x86_64.sh -b -p /opt/anaconda && \
#    rm Anaconda3-2023.09-0-Linux-x86_64.sh

# Download and install Miniforge (for ARM machine) -- Manual Addition
RUN wget -O /tmp/Miniforge3-Linux-aarch64.sh https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-aarch64.sh && \
    chmod +x /tmp/Miniforge3-Linux-aarch64.sh && \
    /bin/bash /tmp/Miniforge3-Linux-aarch64.sh -b -p /opt/miniforge && \
    rm /tmp/Miniforge3-Linux-aarch64.sh

# Add Anaconda to PATH
ENV PATH="/opt/miniforge/bin:${PATH}"

RUN curl -sSLO https://pdm-project.org/install-pdm.py \
    && curl -sSL https://pdm-project.org/install-pdm.py.sha256 | shasum -a 256 -c - \
    && python3.11 install-pdm.py \
    && echo 'export PATH=/root/.local/bin:$PATH' >> ~/.bashrc \
    && echo "Installed pdm"

RUN git clone https://github.com/r2e-project/r2e-docker-setup.git /install_code

COPY . /repos

WORKDIR /install_code

RUN pip install -r requirements.txt

RUN python3 parallel_installer.py 0 10 10

