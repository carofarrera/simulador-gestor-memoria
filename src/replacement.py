"""
Módulo que define algoritmos de reemplazo de páginas. Por ahora solo se
implementa FIFO, pero la arquitectura permite incorporar otros algoritmos
como LRU o Clock.
"""

from collections import deque
from typing import Deque, Tuple, Dict, Optional, Callable


class ReplacementAlgorithm:
    """Interfaz base para algoritmos de reemplazo de páginas."""

    def select_victim(self, page_queue: Deque[Tuple[int, int]], is_valid: Callable[[Tuple[int, int]], bool]) -> Tuple[int, int]:
        """Devuelve la tupla (pid, page_number) de la página víctima."""
        raise NotImplementedError


class FIFOReplacement(ReplacementAlgorithm):
    """Implementa la política FIFO (First-In, First-Out)."""

    def select_victim(self, page_queue: Deque[Tuple[int, int]], is_valid: Callable[[Tuple[int, int]], bool]) -> Tuple[int, int]:
        # Avanza hasta encontrar una entrada válida
        while page_queue:
            candidate = page_queue.popleft()
            if is_valid(candidate):
                return candidate
        raise RuntimeError("No hay páginas válidas para reemplazar.")