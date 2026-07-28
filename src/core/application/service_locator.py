from threading import RLock
from typing import Any, TypeVar


ServiceType = TypeVar("ServiceType")


class ServiceLocator:
    def __init__(self):
        self._services: dict[type, Any] = {}
        self._lock = RLock()

    def register(self, service_type: type[ServiceType], instance: ServiceType) -> None:
        with self._lock:
            self._services[service_type] = instance

    def register_if_missing(self, service_type: type[ServiceType], instance: ServiceType) -> ServiceType:
        with self._lock:
            existing = self._services.get(service_type)

            if existing is not None:
                return existing

            self._services[service_type] = instance
            return instance

    def get(self, service_type: type[ServiceType]) -> ServiceType:
        with self._lock:
            instance = self._services.get(service_type)

        if instance is None:
            raise LookupError(
                f"Le service « {service_type.__name__} » "
                "n’est pas enregistré."
            )

        return instance

    def try_get(self, service_type: type[ServiceType]) -> ServiceType | None:
        with self._lock:
            return self._services.get(service_type)

    def contains(self, service_type: type) -> bool:
        with self._lock:
            return service_type in self._services

    def unregister(self, service_type: type) -> bool:
        with self._lock:
            return self._services.pop(service_type, None) is not None

    def clear(self) -> None:
        with self._lock:
            self._services.clear()

    def registered_services(self) -> tuple[type, ...]:
        with self._lock:
            return tuple(self._services.keys())


services = ServiceLocator()