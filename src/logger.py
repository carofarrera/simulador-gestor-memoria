"""
Registro de eventos para el simulador de memoria. Permite almacenar mensajes
significativos y recuperar el historial completo.
"""

from typing import List


class Logger:
    """Acumula mensajes de eventos."""

    def __init__(self) -> None:
        self._events: List[str] = []

    def log(self, message: str) -> None:
        self._events.append(message)

    def get_events(self) -> List[str]:
        return list(self._events)

    def clear(self) -> None:
        self._events.clear()