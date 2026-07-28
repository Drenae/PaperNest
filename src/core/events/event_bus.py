import asyncio
import inspect
import logging
from collections import defaultdict
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime
from threading import RLock
from typing import Any, TypeVar


logger = logging.getLogger(__name__)

EventHandler = Callable[[Any], Any | Awaitable[Any]]
EventType = TypeVar("EventType")


@dataclass(frozen=True, slots=True)
class ApplicationEvent:
    created_at: str = datetime.now().astimezone().isoformat(
        timespec="seconds"
    )


@dataclass(frozen=True, slots=True)
class DocumentImported(ApplicationEvent):
    document_id: int = 0
    category_key: str = ""
    relative_path: str = ""


@dataclass(frozen=True, slots=True)
class DocumentRenamed(ApplicationEvent):
    document_id: int = 0
    old_relative_path: str = ""
    new_relative_path: str = ""


@dataclass(frozen=True, slots=True)
class DocumentMoved(ApplicationEvent):
    document_id: int = 0
    old_category_key: str = ""
    new_category_key: str = ""


@dataclass(frozen=True, slots=True)
class DocumentDeleted(ApplicationEvent):
    document_id: int = 0
    relative_path: str = ""


@dataclass(frozen=True, slots=True)
class DocumentRestored(ApplicationEvent):
    document_id: int = 0
    category_key: str = ""
    relative_path: str = ""


@dataclass(frozen=True, slots=True)
class DocumentMetadataUpdated(ApplicationEvent):
    document_id: int = 0


@dataclass(frozen=True, slots=True)
class DocumentFavoriteChanged(ApplicationEvent):
    document_id: int = 0
    is_favorite: bool = False


@dataclass(frozen=True, slots=True)
class CategoryCreated(ApplicationEvent):
    category_key: str = ""


@dataclass(frozen=True, slots=True)
class CategoryRenamed(ApplicationEvent):
    old_category_key: str = ""
    new_category_key: str = ""


@dataclass(frozen=True, slots=True)
class CategoryDeleted(ApplicationEvent):
    category_key: str = ""


@dataclass(frozen=True, slots=True)
class BackupCreated(ApplicationEvent):
    backup_path: str = ""


@dataclass(frozen=True, slots=True)
class BackupRestored(ApplicationEvent):
    backup_path: str = ""


@dataclass(frozen=True, slots=True)
class TrashChanged(ApplicationEvent):
    document_count: int = 0


@dataclass(frozen=True, slots=True)
class IndexUpdated(ApplicationEvent):
    new_count: int = 0
    updated_count: int = 0
    missing_count: int = 0
    error_count: int = 0


class EventBus:
    def __init__(self):
        self._handlers: dict[type, list[EventHandler]] = defaultdict(list)
        self._lock = RLock()

    def subscribe(self, event_type: type[EventType], handler: EventHandler) -> None:
        with self._lock:
            handlers = self._handlers[event_type]

            if handler not in handlers:
                handlers.append(handler)

    def unsubscribe(self, event_type: type[EventType], handler: EventHandler) -> None:
        with self._lock:
            handlers = self._handlers.get(event_type)

            if not handlers:
                return

            if handler in handlers:
                handlers.remove(handler)

            if not handlers:
                self._handlers.pop(event_type, None)

    def clear(self, event_type: type | None = None) -> None:
        with self._lock:
            if event_type is None:
                self._handlers.clear()
                return

            self._handlers.pop(event_type, None)

    def publish(self, event: ApplicationEvent) -> None:
        handlers = self._get_handlers(type(event))

        for handler in handlers:
            try:
                result = handler(event)

                if inspect.isawaitable(result):
                    self._schedule_awaitable(result)

            except Exception:
                logger.exception(
                    "Erreur pendant le traitement de l’événement %s.",
                    type(event).__name__,
                )

    async def publish_async(self, event: ApplicationEvent) -> None:
        handlers = self._get_handlers(type(event))
        tasks: list[Awaitable[Any]] = []

        for handler in handlers:
            try:
                result = handler(event)

                if inspect.isawaitable(result):
                    tasks.append(result)

            except Exception:
                logger.exception(
                    "Erreur pendant le traitement de l’événement %s.",
                    type(event).__name__,
                )

        if tasks:
            results = await asyncio.gather(
                *tasks,
                return_exceptions=True,
            )

            for result in results:
                if isinstance(result, Exception):
                    logger.error(
                        "Un gestionnaire d’événement asynchrone a échoué.",
                        exc_info=(
                            type(result),
                            result,
                            result.__traceback__,
                        ),
                    )

    def subscriber_count(self, event_type: type) -> int:
        with self._lock:
            return len(
                self._handlers.get(
                    event_type,
                    [],
                )
            )

    def _get_handlers(self, event_type: type) -> list[EventHandler]:
        with self._lock:
            handlers: list[EventHandler] = []

            for registered_type, registered_handlers in self._handlers.items():
                if issubclass(event_type, registered_type):
                    handlers.extend(registered_handlers)

            return list(handlers)

    @staticmethod
    def _schedule_awaitable(awaitable: Awaitable[Any]) -> None:
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(awaitable)

        except RuntimeError:
            asyncio.run(awaitable)


event_bus = EventBus()