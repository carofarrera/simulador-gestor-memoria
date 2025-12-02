"""
Gestor de memoria que maneja la asignación de marcos en RAM y Swap, la tabla de
páginas de cada proceso y el algoritmo de reemplazo de páginas. Implementa
la funcionalidad de paginación y swapping necesaria para la simulación.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict
from collections import deque

# Importaciones absolutas para permitir ejecución directa del script
from config import Config
from process import Process


@dataclass
class Frame:
    """Representa un marco de memoria física o de swap."""

    process_id: Optional[int] = None
    page_number: Optional[int] = None

    @property
    def free(self) -> bool:
        return self.process_id is None


class MemoryManager:
    """Maneja RAM y Swap, asignaciones y reemplazos de páginas."""

    def __init__(self, config: Config) -> None:
        # Crear los marcos de RAM y Swap
        self.ram: List[Frame] = [Frame() for _ in range(config.ram_frames)]
        self.swap: List[Frame] = [Frame() for _ in range(config.swap_frames)]
        # Cola FIFO de páginas en RAM: almacena tuplas (pid, page_number)
        self.page_queue: deque[Tuple[int, int]] = deque()
        # Almacena procesos activos por PID
        self.processes: Dict[int, Process] = {}
        # Configuración
        self.config = config
        # Métricas de rendimiento
        self.page_faults: int = 0
        self.swaps: int = 0
        # Estructura de TLB con política LRU. Cada entrada es un dict
        # { 'pid': pid, 'page_number': page_number, 'frame_index': frame_index }
        self.tlb_capacity: int = 4
        self.tlb: List[Dict[str, int]] = []

    # ------------------------------------------------------------------
    # Asignación de procesos
    # ------------------------------------------------------------------
    def add_process(self, process: Process) -> List[str]:
        """
        Añade un proceso y asigna sus páginas a marcos en RAM o Swap según
        disponibilidad. Devuelve una lista de mensajes de asignación y swapping
        para registro.
        """
        messages: List[str] = []
        self.processes[process.pid] = process
        for page_number in range(process.pages_needed):
            msg = self._allocate_page(process, page_number)
            if msg:
                messages.append(msg)
        return messages

    def _allocate_page(self, process: Process, page_number: int) -> Optional[str]:
        """Intenta asignar una página a un marco en RAM; si no hay espacio,
        selecciona una víctima y realiza swapping. Devuelve mensaje si hubo
        operación de swapping."""
        # Buscar marco libre en RAM
        for idx, frame in enumerate(self.ram):
            if frame.free:
                # Asignar página a este marco
                self._assign_frame(process, page_number, idx)
                return None
        # No hay marcos libres, se requiere swapping
        return self._swap_and_assign(process, page_number)

    def _assign_frame(self, process: Process, page_number: int, frame_index: int) -> None:
        """Asigna una página de un proceso a un marco específico de RAM."""
        frame = self.ram[frame_index]
        frame.process_id = process.pid
        frame.page_number = page_number
        # Actualizar tabla de páginas
        entry = process.page_table[page_number]
        entry.present = True
        entry.frame_index = frame_index
        entry.swap_index = None
        # Añadir a la cola FIFO
        self.page_queue.append((process.pid, page_number))
        # Actualizar TLB con esta traducción
        self._update_tlb(process.pid, page_number, frame_index)

    # ------------------------------------------------------------------
    # Reemplazo y swapping
    # ------------------------------------------------------------------
    def _swap_and_assign(self, new_process: Process, new_page_number: int) -> str:
        """
        Selecciona una página víctima usando FIFO, la mueve a Swap y asigna su
        marco liberado a la nueva página. Devuelve un mensaje de swapping.
        """
        # Elegir página víctima
        while self.page_queue:
            victim_pid, victim_page_number = self.page_queue.popleft()
            victim_process = self.processes.get(victim_pid)
            if victim_process is None:
                continue
            victim_entry = victim_process.page_table[victim_page_number]
            # Solo considerar páginas que siguen presentes en RAM
            if victim_entry.present and victim_entry.frame_index is not None:
                frame_index = victim_entry.frame_index
                break
        else:
            # Si la cola está vacía (no debería ocurrir), asignar aleatoriamente
            frame_index = 0
            victim_process = None
            victim_page_number = None

        # Mover víctima a Swap
        if victim_process is not None and victim_page_number is not None:
            swap_index = self._move_to_swap(victim_process, victim_page_number, frame_index)
            # Incrementar contador de swaps
            self.swaps += 1
            message = (
                f"Página {victim_page_number} del Proceso {victim_process.pid} movida a "
                f"Swap en marco {swap_index} por falta de espacio."
            )
        else:
            message = ""

        # Asignar el marco liberado a la nueva página
        self._assign_frame(new_process, new_page_number, frame_index)
        return message

    def _move_to_swap(self, process: Process, page_number: int, frame_index: int) -> int:
        """Mueve la página especificada de RAM a la primera posición libre de Swap."""
        # Encontrar marco libre en Swap
        for swap_idx, swap_frame in enumerate(self.swap):
            if swap_frame.free:
                # Copiar datos
                swap_frame.process_id = process.pid
                swap_frame.page_number = page_number
                # Actualizar tabla de páginas
                entry = process.page_table[page_number]
                entry.present = False
                entry.frame_index = None
                entry.swap_index = swap_idx
                # Liberar marco en RAM
                frame = self.ram[frame_index]
                frame.process_id = None
                frame.page_number = None
                # Invalidar la entrada correspondiente en la TLB
                self._invalidate_tlb(process.pid, page_number)
                return swap_idx
        # Si no hay espacio en Swap, levantar excepción
        raise MemoryError("No hay espacio en Swap para mover páginas.")

    # ------------------------------------------------------------------
    # Liberación de procesos
    # ------------------------------------------------------------------
    def remove_process(self, pid: int) -> None:
        """Libera todos los marcos en RAM y Swap ocupados por un proceso y elimina su tabla de páginas."""
        process = self.processes.get(pid)
        if not process:
            return
        # Liberar marcos de RAM
        for entry_page, entry in process.page_table.items():
            if entry.present and entry.frame_index is not None:
                frame = self.ram[entry.frame_index]
                frame.process_id = None
                frame.page_number = None
            if not entry.present and entry.swap_index is not None:
                swap_frame = self.swap[entry.swap_index]
                swap_frame.process_id = None
                swap_frame.page_number = None
        process.terminate()
        # Eliminar de procesos activos
        del self.processes[pid]
        # Reconstruir la cola FIFO eliminando entradas de este proceso
        self.page_queue = deque(
            (p, pg) for (p, pg) in self.page_queue if p != pid
        )
        # Eliminar entradas de la TLB asociadas a este proceso
        self.tlb = [entry for entry in self.tlb if entry['pid'] != pid]

    # ------------------------------------------------------------------
    # Visualización
    # ------------------------------------------------------------------
    def get_ram_map(self) -> str:
        """Devuelve una cadena que representa el mapa de RAM."""
        entries = []
        for i, frame in enumerate(self.ram):
            if frame.free:
                entries.append(f"[{i}] Libre")
            else:
                entries.append(f"[{i}] P{frame.process_id}, Pag {frame.page_number}")
        return " | ".join(entries)

    def get_swap_map(self) -> str:
        """Devuelve una cadena que representa el mapa de Swap."""
        entries = []
        for i, frame in enumerate(self.swap):
            if frame.free:
                entries.append(f"[{i}] Libre")
            else:
                entries.append(f"[{i}] P{frame.process_id}, Pag {frame.page_number}")
        return " | ".join(entries)

    def get_page_table(self, pid: int) -> str:
        """Devuelve una representación de la tabla de páginas de un proceso."""
        process = self.processes.get(pid)
        if not process:
            return "Proceso no encontrado."
        lines = [f"Tabla de páginas del Proceso {pid}:"]
        for page_number, entry in process.page_table.items():
            if entry.present:
                location = f"RAM[{entry.frame_index}]"
            elif entry.swap_index is not None:
                location = f"Swap[{entry.swap_index}]"
            else:
                location = "No asignada"
            lines.append(f"Página {page_number} -> {location}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Métricas de rendimiento
    # ------------------------------------------------------------------
    def get_metrics(self) -> str:
        """Devuelve un resumen de métricas de rendimiento."""
        used_frames = sum(1 for f in self.ram if not f.free)
        total_frames = len(self.ram)
        utilization = (used_frames / total_frames) * 100 if total_frames > 0 else 0.0
        return (
            f"Fallas de página: {self.page_faults}\n"
            f"Operaciones de swapping: {self.swaps}\n"
            f"Marcos usados en RAM: {used_frames}/{total_frames} ({utilization:.1f}% de utilización)"
        )

    # ------------------------------------------------------------------
    # Acceso a páginas (fallos de página)
    # ------------------------------------------------------------------
    def access_page(self, pid: int, page_number: int) -> str:
        """
        Simula el acceso a una página por parte de un proceso. Si la página no
        está presente en RAM, se considera un fallo de página y se trae desde
        Swap al realizar swapping. Devuelve un mensaje indicando el resultado.
        """
        process = self.processes.get(pid)
        if not process:
            return "Proceso no encontrado."
        if page_number < 0 or page_number >= process.pages_needed:
            return "Número de página fuera de rango."
        # Comprobar TLB para traducción rápida
        for idx, tlb_entry in enumerate(self.tlb):
            if tlb_entry['pid'] == pid and tlb_entry['page_number'] == page_number:
                # Política LRU: mover entrada al final para marcarla como usada recientemente
                self.tlb.pop(idx)
                self.tlb.append(tlb_entry)
                return (
                    f"Acceso exitoso a P{pid} página {page_number} en RAM["
                    f"{tlb_entry['frame_index']}] (TLB hit)."
                )
        # No se encontró en TLB, consultar tabla de páginas
        entry = process.page_table[page_number]
        # Si la página está presente en RAM
        if entry.present and entry.frame_index is not None:
            entry.referenced = True
            # Actualizar TLB con esta nueva traducción
            self._update_tlb(pid, page_number, entry.frame_index)
            return f"Acceso exitoso a P{pid} página {page_number} en RAM[{entry.frame_index}]."
        # Si la página no está en RAM pero está en Swap, traerla
        if entry.swap_index is not None:
            # Registrar fallo de página
            self.page_faults += 1
            # Liberar marco en Swap
            swap_index = entry.swap_index
            self.swap[swap_index].process_id = None
            self.swap[swap_index].page_number = None
            # Asignar nuevo marco en RAM
            msg = self._allocate_page(process, page_number)
            # Actualizar la entrada de la tabla de páginas y TLB
            entry = process.page_table[page_number]
            if entry.present and entry.frame_index is not None:
                self._update_tlb(pid, page_number, entry.frame_index)
            entry.referenced = True
            return (
                f"Fallo de página: página {page_number} de P{pid} traída desde Swap."
                f" {msg or ''}"
            ).strip()
        return "La página no está asignada ni en RAM ni en Swap."

    # ------------------------------------------------------------------
    # Gestión de la TLB
    # ------------------------------------------------------------------
    def _update_tlb(self, pid: int, page_number: int, frame_index: int) -> None:
        """
        Agrega o actualiza una entrada en la TLB para la traducción (pid, page_number)
        a frame_index utilizando política LRU. Si la TLB está llena, elimina la
        entrada menos recientemente usada.
        """
        # Eliminar cualquier entrada existente para esta página
        for i, entry in enumerate(self.tlb):
            if entry['pid'] == pid and entry['page_number'] == page_number:
                self.tlb.pop(i)
                break
        # Si la TLB está llena, eliminar la entrada menos recientemente usada (primer elemento)
        if len(self.tlb) >= self.tlb_capacity:
            self.tlb.pop(0)
        # Añadir la nueva entrada al final
        self.tlb.append({'pid': pid, 'page_number': page_number, 'frame_index': frame_index})

    def _invalidate_tlb(self, pid: int, page_number: int) -> None:
        """Elimina una entrada específica de la TLB, si existe."""
        self.tlb = [entry for entry in self.tlb if not (entry['pid'] == pid and entry['page_number'] == page_number)]