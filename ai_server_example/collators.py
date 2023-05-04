import torch
from typing import Generic, TypeVar, List


T = TypeVar("T")


class Collator(Generic[T]):
    def collate(self, inputs: List[T]) -> T:
        raise NotImplementedError()

    def uncollate(self, input: T) -> List[T]:
        raise NotImplementedError()


class TorchCollator(Collator[T]):
    def __init__(self, stack: bool = False) -> None:
        super().__init__()
        self.stack = stack

    def collate(self, inputs: List[T]) -> T:
        return torch.stack(inputs) if self.stack else torch.cat(inputs)

    def uncollate(self, input: T) -> List[T]:
        return [x if self.stack else x.unsqueeze(0) for x in input]
