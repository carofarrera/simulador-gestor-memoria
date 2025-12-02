"""
Módulo de configuración para el simulador de memoria.

Lee los parámetros de tamaño de RAM, área de intercambio (Swap) y tamaño de página
desde un archivo INI. Si el archivo no existe o no define los parámetros,
se utilizarán valores por defecto. Los valores se exponen a través de
atributos de la clase Config.
"""

import configparser
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class ConfigValues:
    """Estructura de datos simple para almacenar la configuración."""

    ram_size_kb: int
    swap_size_kb: int
    page_size_kb: int


class Config:
    """Clase encargada de cargar la configuración desde un archivo INI."""

    DEFAULT_RAM_SIZE_KB = 2048
    DEFAULT_SWAP_SIZE_KB = 4096
    DEFAULT_PAGE_SIZE_KB = 256

    def __init__(self, path: str) -> None:
        self.path = path
        self.values: Optional[ConfigValues] = None
        self._load()

    def _load(self) -> None:
        """Carga el archivo INI y almacena los valores en ConfigValues."""
        parser = configparser.ConfigParser()
        if not os.path.exists(self.path):
            # Si el archivo no existe, usar valores por defecto
            self.values = ConfigValues(
                ram_size_kb=self.DEFAULT_RAM_SIZE_KB,
                swap_size_kb=self.DEFAULT_SWAP_SIZE_KB,
                page_size_kb=self.DEFAULT_PAGE_SIZE_KB,
            )
            return

        parser.read(self.path)
        # Intentar leer la sección 'Memory'
        try:
            ram = int(parser.get('Memory', 'RAM_SIZE_KB', fallback=self.DEFAULT_RAM_SIZE_KB))
            swap = int(parser.get('Memory', 'SWAP_SIZE_KB', fallback=self.DEFAULT_SWAP_SIZE_KB))
            page = int(parser.get('Memory', 'PAGE_SIZE_KB', fallback=self.DEFAULT_PAGE_SIZE_KB))
        except (configparser.NoSectionError, ValueError):
            # Si no existe la sección o hay valores inválidos, se usan por defecto
            ram = self.DEFAULT_RAM_SIZE_KB
            swap = self.DEFAULT_SWAP_SIZE_KB
            page = self.DEFAULT_PAGE_SIZE_KB

        # Validaciones básicas
        if page <= 0:
            page = self.DEFAULT_PAGE_SIZE_KB
        if ram <= 0:
            ram = self.DEFAULT_RAM_SIZE_KB
        if swap <= 0:
            swap = self.DEFAULT_SWAP_SIZE_KB

        self.values = ConfigValues(ram_size_kb=ram, swap_size_kb=swap, page_size_kb=page)

    @property
    def ram_frames(self) -> int:
        """Número de marcos en RAM según el tamaño de página."""
        assert self.values is not None
        return self.values.ram_size_kb // self.values.page_size_kb

    @property
    def swap_frames(self) -> int:
        """Número de marcos en Swap según el tamaño de página."""
        assert self.values is not None
        return self.values.swap_size_kb // self.values.page_size_kb

    def summary(self) -> str:
        """Devuelve un resumen legible de la configuración."""
        assert self.values is not None
        return (
            f"Tamaño RAM: {self.values.ram_size_kb} KB\n"
            f"Tamaño Swap: {self.values.swap_size_kb} KB\n"
            f"Tamaño de página: {self.values.page_size_kb} KB\n"
            f"Marcos en RAM: {self.ram_frames}\n"
            f"Marcos en Swap: {self.swap_frames}"
        )