FROM python:3.10

ARG EUMETSAT_PASS
ENV EUMETSAT_PASS=$EUMETSAT_PASS

ARG EUMETSAT_SECRET
ENV EUMETSAT_SECRET=$EUMETSAT_SECRET

# Entrypoint
ADD entrypoint.sh /root/entrypoint.sh
RUN chmod +x /root/entrypoint.sh
ENTRYPOINT /root/entrypoint.sh