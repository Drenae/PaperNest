import asyncio
import logging
from collections.abc import Awaitable, Callable
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from threading import RLock
from typing import Any


logger = logging.getLogger(__name__)

TaskCallable = Callable[..., Any]
AsyncTaskCallable = Callable[..., Awaitable[Any]]


@dataclass(frozen=True, slots=True)
class ScheduledTask:
    task_id: str
    label: str
    future: Future | asyncio.Task


class TaskScheduler:
    def __init__(self, max_workers: int = 4):
        self._executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="papernest",
        )

        self._tasks: dict[str, ScheduledTask] = {}
        self._lock = RLock()
        self._counter = 0
        self._closed = False

    def submit(
        self,
        function: TaskCallable,
        *args,
        label: str | None = None,
        **kwargs,
    ) -> Future:
        self._ensure_open()

        task_id = self._next_task_id()
        task_label = label or function.__name__

        future = self._executor.submit(
            function,
            *args,
            **kwargs,
        )

        self._register_task(
            task_id,
            task_label,
            future,
        )

        future.add_done_callback(
            lambda completed: self._handle_completion(
                task_id,
                completed,
            )
        )

        return future

    def submit_async(
        self,
        function: AsyncTaskCallable,
        *args,
        label: str | None = None,
        **kwargs,
    ) -> asyncio.Task:
        self._ensure_open()

        task_id = self._next_task_id()
        task_label = label or function.__name__

        task = asyncio.create_task(
            function(
                *args,
                **kwargs,
            )
        )

        self._register_task(
            task_id,
            task_label,
            task,
        )

        task.add_done_callback(
            lambda completed: self._handle_completion(
                task_id,
                completed,
            )
        )

        return task

    async def run_in_thread(
        self,
        function: TaskCallable,
        *args,
        **kwargs,
    ) -> Any:
        self._ensure_open()

        loop = asyncio.get_running_loop()

        return await loop.run_in_executor(
            self._executor,
            lambda: function(
                *args,
                **kwargs,
            ),
        )

    def cancel(self, task_id: str) -> bool:
        with self._lock:
            scheduled_task = self._tasks.get(task_id)

            if scheduled_task is None:
                return False

            cancelled = scheduled_task.future.cancel()

            if cancelled:
                self._tasks.pop(task_id, None)

            return cancelled

    def cancel_all(self) -> int:
        with self._lock:
            tasks = list(self._tasks.values())

        cancelled_count = 0

        for scheduled_task in tasks:
            if scheduled_task.future.cancel():
                cancelled_count += 1

        with self._lock:
            self._tasks = {
                task_id: scheduled_task
                for task_id, scheduled_task in self._tasks.items()
                if not scheduled_task.future.cancelled()
            }

        return cancelled_count

    def active_tasks(self) -> list[ScheduledTask]:
        with self._lock:
            return [
                scheduled_task
                for scheduled_task in self._tasks.values()
                if not scheduled_task.future.done()
            ]

    def active_task_count(self) -> int:
        return len(self.active_tasks())

    def shutdown(self, wait: bool = False) -> None:
        with self._lock:
            if self._closed:
                return

            self._closed = True

        self.cancel_all()

        self._executor.shutdown(
            wait=wait,
            cancel_futures=True,
        )

    def _register_task(
        self,
        task_id: str,
        label: str,
        future: Future | asyncio.Task,
    ) -> None:
        with self._lock:
            self._tasks[task_id] = ScheduledTask(
                task_id=task_id,
                label=label,
                future=future,
            )

    def _handle_completion(
        self,
        task_id: str,
        future: Future | asyncio.Task,
    ) -> None:
        with self._lock:
            scheduled_task = self._tasks.pop(
                task_id,
                None,
            )

        if scheduled_task is None:
            return

        if future.cancelled():
            logger.info(
                "Tâche annulée : %s.",
                scheduled_task.label,
            )
            return

        try:
            future.result()

        except Exception:
            logger.exception(
                "La tâche « %s » a échoué.",
                scheduled_task.label,
            )

        else:
            logger.info(
                "Tâche terminée : %s.",
                scheduled_task.label,
            )

    def _next_task_id(self) -> str:
        with self._lock:
            self._counter += 1
            return f"task-{self._counter}"

    def _ensure_open(self) -> None:
        if self._closed:
            raise RuntimeError(
                "Le planificateur PaperNest est arrêté."
            )


task_scheduler = TaskScheduler()