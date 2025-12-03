from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict
from collections import deque

from config import Config
from process import Process


@dataclass
class Frame:
    process_id: Optional[int] = None
    page_number: Optional[int] = None

    @property
    def free(self) -> bool:
        return self.process_id is None


class MemoryManager:
    """Gestor de memoria con RAM, Swap, FIFO, TLB y métricas completas."""

    def __init__(self, config: Config) -> None:
        # Inicializar marcos de RAM y Swap
        self.ram: List[Frame] = [Frame() for _ in range(config.ram_frames)]
        self.swap: List[Frame] = [Frame() for _ in range(config.swap_frames)]

        # FIFO para reemplazo de páginas
        self.page_queue: deque[Tuple[int, int]] = deque()

        # Procesos activos
        self.processes: Dict[int, Process] = {}

        # Configuración
        self.config = config

        # MÉTRICAS COMPLETAS
        self.total_accesses = 0
        self.page_faults = 0
        self.swaps_in = 0
        self.swaps_out = 0
        self.tlb_hits = 0
        self.tlb_misses = 0

        # TLB con política LRU
        self.tlb_capacity: int = 4
        self.tlb: List[Dict[str, int]] = []

    # CREAR PROCESO
    def add_process(self, process: Process) -> List[str]:
        messages: List[str] = []
        self.processes[process.pid] = process
        for page_number in range(process.pages_needed):
            msg = self._allocate_page(process, page_number)
            if msg:
                messages.append(msg)
        return messages

    def _allocate_page(self, process: Process, page_number: int):
        # Buscar marco libre en RAM
        for idx, frame in enumerate(self.ram):
            if frame.free:
                self._assign_frame(process, page_number, idx)
                return None
        return self._swap_and_assign(process, page_number)

    def _assign_frame(self, process: Process, page_number: int, frame_index: int):
        frame = self.ram[frame_index]
        frame.process_id = process.pid
        frame.page_number = page_number
        entry = process.page_table[page_number]
        entry.present = True
        entry.frame_index = frame_index
        entry.swap_index = None
        self.page_queue.append((process.pid, page_number))
        self._update_tlb(process.pid, page_number, frame_index)

    # SWAPPING
    def _swap_and_assign(self, new_process: Process, new_page_number: int):
        while self.page_queue:
            victim_pid, victim_page = self.page_queue.popleft()
            victim_proc = self.processes.get(victim_pid)
            if not victim_proc:
                continue
            entry = victim_proc.page_table[victim_page]
            if entry.present and entry.frame_index is not None:
                frame_index = entry.frame_index
                break
        swap_idx = self._move_to_swap(victim_proc, victim_page, frame_index)
        self.swaps_out += 1
        msg = f"Página {victim_page} del Proceso {victim_proc.pid} movida a Swap[{swap_idx}]"
        self._assign_frame(new_process, new_page_number, frame_index)
        return msg

    def _move_to_swap(self, process: Process, page_number: int, frame_index: int) -> int:
        for idx, frame in enumerate(self.swap):
            if frame.free:
                frame.process_id = process.pid
                frame.page_number = page_number
                entry = process.page_table[page_number]
                entry.present = False
                entry.swap_index = idx
                entry.frame_index = None
                ram_f = self.ram[frame_index]
                ram_f.process_id = None
                ram_f.page_number = None
                self._invalidate_tlb(process.pid, page_number)
                return idx
        raise MemoryError("Swap lleno.")

    # TERMINAR PROCESO
    def remove_process(self, pid: int):
        process = self.processes.get(pid)
        if not process:
            return
        for entry in process.page_table.values():
            if entry.present and entry.frame_index is not None:
                ram_f = self.ram[entry.frame_index]
                ram_f.process_id = None
                ram_f.page_number = None
            if not entry.present and entry.swap_index is not None:
                swap_f = self.swap[entry.swap_index]
                swap_f.process_id = None
                swap_f.page_number = None
        del self.processes[pid]
        self.page_queue = deque([(p, pg) for (p, pg) in self.page_queue if p != pid])
        self.tlb = [e for e in self.tlb if e["pid"] != pid]

    # MAPAS DE MEMORIA
    def get_ram_map(self):
        return " | ".join(
            f"[{i}] {'Libre' if f.free else f'P{f.process_id},Pag{f.page_number}'}"
            for i, f in enumerate(self.ram)
        )

    def get_swap_map(self):
        return " | ".join(
            f"[{i}] {'Libre' if f.free else f'P{f.process_id},Pag{f.page_number}'}"
            for i, f in enumerate(self.swap)
        )

    # TABLA DE PÁGINAS
    def get_page_table(self, pid: int) -> str:
        process = self.processes.get(pid)
        if not process:
            return "Proceso no encontrado."
        lines = [f"Tabla de páginas del Proceso {pid}:"]
        for page_number, entry in process.page_table.items():
            if entry.present and entry.frame_index is not None:
                location = f"RAM[{entry.frame_index}]"
            elif entry.swap_index is not None:
                location = f"Swap[{entry.swap_index}]"
            else:
                location = "No asignada"
            lines.append(f"Página {page_number} -> {location}")
        return "\n".join(lines)

    # MÉTRICAS COMPLETAS
    def get_page_fault_rate(self):
        return (self.page_faults / self.total_accesses * 100) if self.total_accesses > 0 else 0.0

    def get_ram_occupancy(self):
        used = sum(not f.free for f in self.ram)
        return used / len(self.ram) * 100

    def get_swap_occupancy(self):
        used = sum(not f.free for f in self.swap)
        return used / len(self.swap) * 100

    def get_metrics(self):
        return (
            f"Accesos totales: {self.total_accesses}\n"
            f"Fallos de página: {self.page_faults}\n"
            f"Tasa de fallos: {self.get_page_fault_rate():.2f}%\n"
            f"Swaps OUT (RAM→Swap): {self.swaps_out}\n"
            f"Swaps IN (Swap→RAM): {self.swaps_in}\n"
            f"Ocupación RAM: {self.get_ram_occupancy():.2f}%\n"
            f"Ocupación Swap: {self.get_swap_occupancy():.2f}%\n"
            f"TLB hits: {self.tlb_hits}\n"
            f"TLB misses: {self.tlb_misses}\n"
        )

    # ACCESO A PÁGINAS
    def access_page(self, pid: int, page_number: int) -> str:
        self.total_accesses += 1
        process = self.processes.get(pid)
        if not process:
            return "Proceso no encontrado."
        if not (0 <= page_number < process.pages_needed):
            return "Número de página inválido."
        for i, entry in enumerate(self.tlb):
            if entry["pid"] == pid and entry["page_number"] == page_number:
                self.tlb_hits += 1
                e = self.tlb.pop(i)
                self.tlb.append(e)
                return f"Acceso exitoso a P{pid} Pag{page_number} en RAM[{e['frame_index']}] (TLB hit)."
        self.tlb_misses += 1
        pte = process.page_table[page_number]
        if pte.present and pte.frame_index is not None:
            self._update_tlb(pid, page_number, pte.frame_index)
            return f"Acceso exitoso a P{pid} Pag{page_number} en RAM[{pte.frame_index}]."
        if pte.swap_index is not None:
            self.page_faults += 1
            self.swaps_in += 1
            swap_idx = pte.swap_index
            self.swap[swap_idx].process_id = None
            self.swap[swap_idx].page_number = None
            msg = self._allocate_page(process, page_number)
            pte = process.page_table[page_number]
            if pte.present:
                self._update_tlb(pid, page_number, pte.frame_index)
            return f"Fallo de página: página {page_number} de P{pid} traída desde Swap. {msg or ''}"
        return "La página no está asignada en RAM ni Swap."

    # TLB
    def _update_tlb(self, pid: int, page_number: int, frame_index: int):
        self.tlb = [e for e in self.tlb if not (e["pid"] == pid and e["page_number"] == page_number)]
        if len(self.tlb) >= self.tlb_capacity:
            self.tlb.pop(0)
        self.tlb.append({"pid": pid, "page_number": page_number, "frame_index": frame_index})

    def _invalidate_tlb(self, pid: int, page_number: int):
        self.tlb = [e for e in self.tlb if not (e["pid"] == pid and e["page_number"] == page_number)]
