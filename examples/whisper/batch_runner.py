import asyncio
from asyncio import Future
from asyncio.queues import Queue
from typing import Callable, Generic, TypeVar, Tuple, List

from collators import Collator


T = TypeVar("T")
U = TypeVar("U")


class BatchRunner(Generic[T, U]):
    def __init__(
        self,
        run_fn: Callable[[T], U],
        max_batch_size: int,
        max_latency_ms: int,
        collator: Collator[T],
    ) -> None:
        self.queue: Queue[Tuple[T, Future[U], float]] = Queue(
            maxsize=2 * max_batch_size
        )
        self.run_fn = run_fn
        self.max_batch_size = max_batch_size
        self.max_latency_ms = max_latency_ms
        self.collator = collator

    async def submit(self, input: T) -> U:
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        await self.queue.put((input, fut, loop.time()))
        return await fut

    async def main_loop(self):
        loop = asyncio.get_running_loop()

        while True:
            if not self.queue.empty():
                _, _, first_task_time = self.queue._queue[0]
                latency_ms = int((loop.time() - first_task_time) * 1000)
                if (
                    self.queue.qsize() >= self.max_batch_size
                    or latency_ms > self.max_latency_ms
                ):
                    batch_size = min(self.queue.qsize(), self.max_batch_size)
                    inputs_list: List[T] = []
                    futures: List[Future[U]] = []
                    for _ in range(batch_size):
                        input, future, _ = self.queue.get_nowait()
                        inputs_list.append(input)
                        futures.append(future)
                    inputs = self.collator.collate(inputs_list)

                    try:
                        outputs = await asyncio.to_thread(self.run_fn, inputs)
                        outputs_list = self.collator.uncollate(outputs)
                        for output, future in zip(outputs_list, futures):
                            future.set_result(output)
                    except BaseException as e:
                        err_msg = f"{e}"[:256]
                        print(f"Could not process batch:\n{err_msg}")

                        for future in futures:
                            future.set_exception(Exception("Could not process batch"))

                else:
                    # Relinquish control to the event loop
                    await asyncio.sleep(0.01)
            else:
                # Relinquish control to the event loop
                await asyncio.sleep(0.01)

    def run(self):
        loop = asyncio.get_running_loop()
        loop.create_task(self.main_loop())
