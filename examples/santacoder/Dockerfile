FROM python:3.10.10-bullseye as base

RUN pip install \
    torch==1.13.1 \
    transformers==4.26.1 \
    fastapi==0.95.0 \
    python-multipart==0.0.6 \
    uvicorn==0.21.1 \
    pydantic==1.10.7 \
    intel_extension_for_pytorch==1.13.100 \
    --extra-index-url https://download.pytorch.org/whl/cpu

COPY ./server.py ./

CMD python ./server.py