from collections.abc import Callable
from typing import Any

from core.events.event_bus import EventBus, event_bus


EventHandler = Callable[[Any], Any]


class EventSubscription:
    def __init__(self, bus: EventBus = event_bus):
        self.bus = bus
        self._subscriptions: list[
            tuple[type, EventHandler]
        ] = []

    def add(
        self,
        event_type: type,
        handler: EventHandler,
    ) -> None:
        subscription = (
            event_type,
            handler,
        )

        if subscription in self._subscriptions:
            return

        self.bus.subscribe(
            event_type,
            handler,
        )

        self._subscriptions.append(
            subscription
        )

    def add_many(
        self,
        event_types: tuple[type, ...],
        handler: EventHandler,
    ) -> None:
        for event_type in event_types:
            self.add(
                event_type,
                handler,
            )

    def remove(
        self,
        event_type: type,
        handler: EventHandler,
    ) -> None:
        subscription = (
            event_type,
            handler,
        )

        if subscription not in self._subscriptions:
            return

        self.bus.unsubscribe(
            event_type,
            handler,
        )

        self._subscriptions.remove(
            subscription
        )

    def clear(self) -> None:
        for event_type, handler in reversed(
            self._subscriptions
        ):
            self.bus.unsubscribe(
                event_type,
                handler,
            )

        self._subscriptions.clear()

    @property
    def count(self) -> int:
        return len(
            self._subscriptions
        )

    @property
    def is_empty(self) -> bool:
        return not self._subscriptions