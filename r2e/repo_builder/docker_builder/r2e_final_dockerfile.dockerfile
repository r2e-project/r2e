FROM ubuntu
RUN apt-get update

ENV DEBIAN_FRONTEND noninteractive

RUN echo "tzdata tzdata/Areas select America" | debconf-set-selections && echo "tzdata tzdata/Zones/America select Los_Angeles" | debconf-set-selections

# Install standard and python specific system dependencies
RUN apt-get install -y git curl wget build-essential libatlas-base-dev gfortran python3-dev python3-pip python-dev-is-python3 libpq-dev libxml2-dev libxslt1-dev libmysqlclient-dev libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev libgmp3-dev libcurl4-openssl-dev portaudio19-dev libpcap-dev build-essential libssl-dev libffi-dev libsqlite3-dev libbz2-dev libreadline-dev libncursesw5-dev libgdbm-dev libc6-dev zlib1g-dev libjpeg-dev xclip tk-dev libasound2-dev libsasl2-dev libldap2-dev libavformat-dev libavcodec-dev libavdevice-dev libavutil-dev libswscale-dev libavfilter-dev libasound2-dev python3-xlib libblas-dev liblapack-dev graphviz-dev libhdf5-dev libblas-dev liblapack-dev libopenblas-dev gfortran libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev libxml2-dev libxslt-dev libopencv-dev libtiff-dev libpq-dev libmysqlclient-dev libgdal-dev libproj-dev portaudio19-dev libgraphviz-dev libxml2-dev libtiff-dev libfreetype6-dev libwebp-dev libopenjp2-7 liblcms2-dev libopenblas-dev liblapack-dev gfortran libatlas-base-dev libhdf5-dev libnetcdf-dev libgdal-dev libproj-dev libspatialite-dev libhdf4-alt-dev libsqlite3-dev libpq-dev libmysqlclient-dev libgtk2.0-dev libavcodec-dev libavformat-dev libswscale-dev libjpeg-dev libtiff-dev libatlas-base-dev libhdf5-serial-dev portaudio19-dev libreadline-dev libx11-dev libgtk-3-dev libgstreamer1.0-dev libzmq3-dev libgeos-dev libudunits2-dev

# Install Anaconda
RUN wget https://repo.anaconda.com/archive/Anaconda3-2023.09-0-Linux-x86_64.sh && \
    bash Anaconda3-2023.09-0-Linux-x86_64.sh -b -p /opt/anaconda && \
    rm Anaconda3-2023.09-0-Linux-x86_64.sh

# Add Anaconda to PATH
ENV PATH="/opt/anaconda/bin:${PATH}"

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

