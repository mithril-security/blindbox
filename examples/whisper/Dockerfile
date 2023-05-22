FROM python:3.10.10-bullseye as base

RUN pip install \
    torch==1.13.1 \
    transformers==4.26.1 \
    fastapi==0.95.1 \
    python-multipart==0.0.6 \
    uvicorn==0.22.0 \
    soundfile==0.12.1 \
    messages \
    librosa==0.10.0 \
    pydantic==1.10.7 \
    requests==2.28.2 \
    --extra-index-url https://download.pytorch.org/whl/cpu

COPY batch_runner.py /
COPY collators.py /
COPY messages.py /
COPY model_store.py /
COPY openchatkit_utils.py /
COPY serializers.py /
COPY server.py /
COPY start.sh /

RUN chmod +x /start.sh

ENV MODEL_STORE_ENABLED=false
ENV OPENCHATKIT_ENABLED=false
ENV NITRIDING_PROXY_ENABLED=false

CMD ["/start.sh"]
