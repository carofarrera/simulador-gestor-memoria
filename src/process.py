"""
Módulo que define la clase Process y estructuras relacionadas.

Un proceso tiene un identificador, un tamaño en KB y una tabla de páginas
que será completada por el gestor de memoria. También se mantiene el estado
del proceso (activo, intercambiado, terminado).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Optional, Tuple


class ProcessState(Enum):
    """Estados posibles de un proceso en la simulación."""

    ACTIVE = auto()
    SWAPPED = auto()
    TERMINATED = auto()


@dataclass
class PageTableEntry:
    """Entrada de la tabla de páginas."""

    present: bool = False
    frame_index: Optional[int] = None
    swap_index: Optional[int] = None
    referenced: bool = False


class Process:
    """Representa un proceso con tamaño y tabla de páginas."""

    _next_pid = 1

    def __init__(self, size_kb: int, page_size_kb: int) -> None:
        self.pid: int = Process._next_pid
        Process._next_pid += 1
        self.size_kb: int = size_kb
        self.page_size_kb: int = page_size_kb
        self.pages_needed: int = (size_kb + page_size_kb - 1) // page_size_kb
        # Inicialmente la tabla de páginas está vacía; se rellena al asignar marcos
        self.page_table: Dict[int, PageTableEntry] = {
            i: PageTableEntry() for i in range(self.pages_needed)
        }
        self.state: ProcessState = ProcessState.ACTIVE

    def __repr__(self) -> str:
        return f"Process(pid={self.pid}, size_kb={self.size_kb}, pages={self.pages_needed}, state={self.state})"

    def terminate(self) -> None:
        """Marca el proceso como terminado."""
        self.state = ProcessState.TERMINATED

    def swap_out(self) -> None:
        """Marca el proceso como intercambiado."""
        self.state = ProcessState.SWAPPED

    def swap_in(self) -> None:
        """Marca el proceso como activo de nuevo."""
        self.state = ProcessState.ACTIVE