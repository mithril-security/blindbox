import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import argparse
from huggingface_hub import snapshot_download
import os
import typing as t
from transformers import PreTrainedModel
import requests
from uuid import uuid4
import tarfile
import shutil


MODEL_STORE_ENABLED = os.environ.get("MODEL_STORE_ENABLED", None) == "true"


def serve(args):
    app = FastAPI()

    @app.get("/model_store/{name}")
    def get_model(name: str) -> FileResponse:
        filepath = f"./model_store/{name}.tar"
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404)

        return FileResponse(filepath)

    if __name__ == "__main__":
        uvicorn.run(app, host=args.address, port=args.port)


def download(args):
    if not os.path.exists("./model_store/"):
        os.mkdir("./model_store/")

    tmp_dir = f"/tmp/model-store-{uuid4()}"
    name = args.name.replace("/", "--")

    if args.registry == "huggingface":
        snapshot_download(
            repo_id=args.name,
            cache_dir=tmp_dir,
            ignore_patterns=[
                "*.tflite",
                "*.mlmodel",
                "*.msgpack",
                "*.safetensors",
                "*.ot",
                "*.h5",
            ],
        )

        cur_dir = os.getcwd()
        os.chdir(tmp_dir)
        tar = tarfile.open(f"{cur_dir}/model_store/{name}.tar", "w")
        tar.add(f"./models--{name}")
        tar.close()
        os.chdir(cur_dir)

        print(f"\n\nModel available at http://localhost:8000/model_store/{name}")

    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)


def remove(args):
    directory = f"./model_store/{args.name.replace('/', '--')}"
    if os.path.exists(directory):
        os.rmdir(directory)


def load_from_store(
    name: str,
    cls: t.Type[PreTrainedModel],
    host: str = "127.0.0.1",
    port: int = 8000,
    force_download: bool = False,
) -> PreTrainedModel:
    if MODEL_STORE_ENABLED:
        model_store_dir = "./local_model_store"
        url_name = name.replace("/", "--")

        if force_download or not os.path.exists(
            f"{model_store_dir}/models--{url_name}"
        ):
            if not os.path.exists(model_store_dir):
                os.mkdir(model_store_dir)

            url = f"http://{host}:{port}/model_store/{url_name}"
            response = requests.get(url)
            response.raise_for_status()

            tmp_file = f"/tmp/model-store-{uuid4()}.tar"
            with open(tmp_file, "wb") as f:
                f.write(response.content)

            tar = tarfile.open(tmp_file)
            tar.extractall(model_store_dir)
            tar.close()

            os.remove(tmp_file)

        return cls.from_pretrained(name, cache_dir=model_store_dir)

    else:
        return cls.from_pretrained(name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple model store")
    subparsers = parser.add_subparsers(
        title="Commands", description="Supported commands"
    )

    serve_parser = subparsers.add_parser("serve", help="Launch the model store server")
    serve_parser.add_argument(
        "--address", type=str, default="127.0.0.1", help="Listen address"
    )
    serve_parser.add_argument("--port", type=int, default="8000", help="Listen port")
    serve_parser.set_defaults(handler=serve)

    download_parser = subparsers.add_parser(
        "download", help="Download a model into the store"
    )
    download_parser.add_argument(
        "--registry",
        choices=["huggingface"],
        default="huggingface",
        help="Model registry from which to download the model",
    )
    download_parser.add_argument("name", help="Model name")
    download_parser.set_defaults(handler=download)

    remove_parser = subparsers.add_parser(
        "remove", help="Download a model into the store"
    )
    remove_parser.add_argument("name", help="Model name")
    remove_parser.set_defaults(handler=remove)

    args = parser.parse_args()
    args.handler(args)
