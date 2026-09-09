FROM ubuntu:latest
WORKDIR /app
VOLUME /output
ENV OUTPUT_DIR=/output
RUN apt-get update && apt-get install -y --no-install-recommends git python3 python3-pip python3-dev python3-venv gdal-bin libgdal-dev build-essential unzip
ENV PATH="/opt/venv/bin:$PATH"

ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

RUN python3 -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --upgrade pip && \
    GDAL_VER=$(ogrinfo --version | awk '{print $2}' | cut -d, -f1) && \
    pip install --no-cache-dir "GDAL==$GDAL_VER"

RUN git clone https://github.com/hammad93/hurricane-satellites.git

# Entrypoint
ADD entrypoint.sh /root/entrypoint.sh
RUN chmod +x /root/entrypoint.sh
ENTRYPOINT ["/root/entrypoint.sh"]
