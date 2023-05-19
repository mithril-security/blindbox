from typing import (
    Callable,
    Tuple,
    Annotated,
    Type,
    Coroutine,
    TypeVar,
    Generic,
    Optional,
    Union,
)
import numpy as np
import torch
from fastapi import File, HTTPException
from fastapi.responses import Response
from io import BytesIO
import librosa
import soundfile as sf


T = TypeVar("T")


class Serializer(Generic[T]):
    def serialize(self, value: T) -> bytes:
        raise NotImplementedError()

    def deserialize(self, data: Annotated[bytes, File()], *args, **kwargs) -> T:
        raise NotImplementedError()


class ArraySerializer(Serializer[T]):
    def __init__(self, torch_format: bool = False) -> None:
        super().__init__()
        self.torch_format = torch_format

    def serialize(self, value: T) -> bytes:
        buff = BytesIO()
        if self.torch_format:
            torch.save(value, buff)
        else:
            np.save(buff, value)
        buff.seek(0)
        return buff.read()

    def deserialize(
        self,
        data: Annotated[bytes, File()],
        dtype: Optional[Union[torch.dtype, Type]] = None,
        size: Optional[Tuple[int, ...]] = None,
    ) -> T:
        buff = BytesIO()
        buff.write(data)
        buff.seek(0)

        try:
            x = torch.load(buff) if self.torch_format else np.load(buff)
        except:
            raise HTTPException(
                status_code=400,
                detail=f"Could not deserialize data: not a {'torch' if self.torch_format else 'numpy'} file",
            )

        if self._get_generic_type() is not None and not isinstance(
            x, self._get_generic_type()
        ):
            print(type(x))
            raise HTTPException(
                status_code=400,
                detail=f"Not a {'torch tensor' if self.torch_format else 'numpy array'}",
            )

        if dtype is not None and x.dtype != dtype:
            raise HTTPException(
                status_code=400,
                detail=f"{'Torch tensor' if self.torch_format else 'Numpy array'} has a wrong dtype",
            )

        if size is not None and not (
            len(x.size()) == len(size)
            and all([a == b or b == -1 for a, b in zip(x.size(), size)])
        ):
            raise HTTPException(
                status_code=400,
                detail=f"{'Torch tensor' if self.torch_format else 'Numpy array'} has a wrong size",
            )

        return x


class AudioSerializer(Serializer[T]):
    def __init__(self, torch_format: bool = False, sample_rate: int = 16000) -> None:
        super().__init__()
        self.torch_format = torch_format
        self.sample_rate = sample_rate

    def serialize(self, value: T) -> bytes:
        buff = BytesIO()
        if self.torch_format:
            value = value.numpy()
        sf.write(buff, value, self.sample_rate)
        buff.seek(0)
        return buff.read()

    def deserialize(
        self,
        data: Annotated[bytes, File()],
    ) -> T:
        buff = BytesIO()
        buff.write(data)
        buff.seek(0)

        try:
            x, _ = librosa.load(buff, sr=self.sample_rate)
        except:
            raise HTTPException(
                status_code=400, detail="Could not deserialize data: not an audio file"
            )

        if self.torch_format:
            x = torch.tensor(x)

        return x


def array_endpoint(
    dtype: Optional[Union[torch.dtype, Type]] = None,
    size: Optional[Tuple[int, ...]] = None,
    torch_format: bool = False,
) -> Callable[[Callable[[T], T]], Callable[[Annotated[bytes, File()]], Response]]:
    def inner(f: Callable[[T], T]) -> Callable[[Annotated[bytes, File()]], Response]:
        def g(data: Annotated[bytes, File()]) -> Response:
            serializer = ArraySerializer(torch_format=torch_format)
            x = serializer.deserialize(data, dtype, size)
            y = f(x)
            return Response(
                content=serializer.serialize(y), media_type="application/octet-stream"
            )

        return g

    return inner


def async_array_endpoint(
    dtype: Optional[Union[torch.dtype, Type]] = None,
    size: Optional[Tuple[int, ...]] = None,
    torch_format: bool = False,
) -> Callable[
    [Callable[[T], Coroutine[T, None, None]]],
    Callable[[Annotated[bytes, File()]], Coroutine[Response, None, None]],
]:
    def inner(
        f: Callable[[T], Coroutine[T, None, None]]
    ) -> Callable[[Annotated[bytes, File()]], Coroutine[Response, None, None]]:
        async def g(data: Annotated[bytes, File()]) -> Response:
            serializer = ArraySerializer(torch_format=torch_format)
            x = serializer.deserialize(data, dtype, size)
            y = await f(x)
            return Response(
                content=serializer.serialize(y), media_type="application/octet-stream"
            )

        return g

    return inner


def speech_to_text_endpoint(
    sample_rate: int = 16000,
    torch_format: bool = False,
) -> Callable[[Callable[[T], str]], Callable[[Annotated[bytes, File()]], str]]:
    def inner(f: Callable[[T], str]) -> Callable[[Annotated[bytes, File()]], str]:
        def g(audio: Annotated[bytes, File()]) -> str:
            serializer = AudioSerializer(
                torch_format=torch_format, sample_rate=sample_rate
            )
            x = serializer.deserialize(audio)
            return f(x)

        return g

    return inner


def async_speech_to_text_endpoint(
    sample_rate: int = 16000,
    torch_format: bool = False,
) -> Callable[
    [Callable[[T], Coroutine[str, None, None]]],
    Callable[[Annotated[bytes, File()]], Coroutine[str, None, None]],
]:
    def inner(f: Callable[[T], str]) -> Callable[[Annotated[bytes, File()]], str]:
        async def g(audio: Annotated[bytes, File()]) -> str:
            serializer = AudioSerializer(
                torch_format=torch_format, sample_rate=sample_rate
            )
            x = serializer.deserialize(audio)
            return await f(x)

        return g

    return inner
