FROM python:3.10-alpine

RUN pip install \
        fastapi==0.95.0 \
        python-multipart==0.0.6 \
        uvicorn==0.21.1 \
        pydantic==1.10.7 \
        requests==2.28.2 \
    --extra-index-url https://download.pytorch.org/whl/cpu

COPY server.py /

EXPOSE 80

CMD ["python", "/server.py"]
