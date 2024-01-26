FROM ghcr.io/ecoextreml/stemmus_scope:1.5.0

LABEL maintainer="Bart Schilperoort <b.schilperoort@esciencecenter.nl>"
LABEL org.opencontainers.image.source = "https://github.com/EcoExtreML/STEMMUS_SCOPE_Processing"

# Requirements for building Python 3.10
RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev \
    libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev
RUN apt-get install -y libhdf5-serial-dev

# Get Python source and compile
WORKDIR /python
RUN wget https://www.python.org/ftp/python/3.10.12/Python-3.10.12.tgz --no-check-certificate
RUN tar -xf Python-3.10.*.tgz
WORKDIR /python/Python-3.10.12
RUN ./configure --prefix=/usr/local --enable-optimizations --enable-shared LDFLAGS="-Wl,-rpath /usr/local/lib"
RUN make -j $(nproc)
RUN make altinstall
WORKDIR /

# Pip install PyStemmusScope and dependencies
COPY . /opt/PyStemmusScope
RUN pip3.10 install /opt/PyStemmusScope/[docker]
RUN pip3.10 install grpc4bmi==0.5.0

# # Set the STEMMUS_SCOPE environmental variable, so the BMI can find the executable
WORKDIR /
ENV STEMMUS_SCOPE /STEMMUS_SCOPE

EXPOSE 55555
# Start grpc4bmi server
CMD run-bmi-server --name "PyStemmusScope.bmi.implementation.StemmusScopeBmi" --port 55555 --debug
