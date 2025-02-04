FROM continuumio/anaconda3

ARG EUMETSAT_PASS
ENV EUMETSAT_PASS=$EUMETSAT_PASS

ARG EUMETSAT_SECRET
ENV EUMETSAT_SECRET=$EUMETSAT_SECRET

ARG BASE64_SSH_GEOSERVER
ENV BASE64_SSH_GEOSERVER=$BASE64_SSH_GEOSERVER

ARG HOST_SSH
ENV HOST_SSH=$HOST_SSH

ARG USER_SSH
ENV USER_SSH=$USER_SSH

RUN git clone --single-branch --branch main https://github.com/hammad93/hurricane-satellites.git
RUN conda install gdal
RUN pip install -r hurricane-satellites/requirements.txt

# Entrypoint
ADD entrypoint.sh /root/entrypoint.sh
RUN chmod +x /root/entrypoint.sh
ENTRYPOINT /root/entrypoint.sh
