"""
Interfaz de línea de comandos (CLI) para interactuar con el simulador de
gestión de memoria. Permite crear y eliminar procesos, acceder a páginas,
consultar el estado de la memoria, ver tablas de páginas y métricas de
rendimiento.
"""

import random
from typing import Optional

# Importaciones absolutas para permitir ejecución directa del script
from config import Config
from process import Process
from memory_manager import MemoryManager
from logger import Logger


class CLI:
    """Clase que encapsula el ciclo de interacción con el usuario."""

    def __init__(self, config_path: str = "config.ini") -> None:
        # Cargar configuración
        self.config = Config(config_path)
        # Instanciar gestor de memoria y logger
        self.memory_manager = MemoryManager(self.config)
        self.logger = Logger()

    def _print_menu(self) -> None:
        print("\n=== Simulador de Gestor de Memoria ===")
        print("Seleccione una opción:")
        print("1. Crear nuevo proceso")
        print("2. Terminar proceso")
        print("3. Acceder a página de proceso")
        print("4. Mostrar mapa de memoria (RAM y Swap)")
        print("5. Mostrar tabla de páginas de un proceso")
        print("6. Mostrar métricas de rendimiento")
        print("7. Mostrar eventos registrados")
        print("0. Salir")

    def run(self) -> None:
        """Ejecuta el ciclo principal de la CLI."""
        print(self.config.summary())
        while True:
            self._print_menu()
            option = input("Opción: ").strip()
            if option == "1":
                self._create_process()
            elif option == "2":
                self._terminate_process()
            elif option == "3":
                self._access_page()
            elif option == "4":
                self._show_memory_map()
            elif option == "5":
                self._show_page_table()
            elif option == "6":
                self._show_metrics()
            elif option == "7":
                self._show_logs()
            elif option == "0":
                print("Saliendo del simulador.")
                break
            else:
                print("Opción no válida. Intente de nuevo.")

    # ------------------------------------------------------------------
    # Acciones de menú
    # ------------------------------------------------------------------
    def _create_process(self) -> None:
        """Crea un nuevo proceso solicitando tamaño al usuario."""
        size_str = input("Tamaño del proceso en KB (o 'r' para aleatorio): ").strip()
        if size_str.lower() == 'r':
            # Generar tamaño aleatorio entre 1 página y mitad de la RAM
            max_size = self.config.values.ram_size_kb // 2
            size_kb = random.randint(self.config.values.page_size_kb, max_size)
        else:
            try:
                size_kb = int(size_str)
                if size_kb <= 0:
                    raise ValueError
            except ValueError:
                print("Tamaño inválido.")
                return
        process = Process(size_kb, self.config.values.page_size_kb)
        messages = self.memory_manager.add_process(process)
        print(f"Proceso {process.pid} creado con tamaño {process.size_kb} KB y {process.pages_needed} páginas.")
        for msg in messages:
            self.logger.log(msg)
            print(msg)

    def _terminate_process(self) -> None:
        """Termina un proceso solicitando PID al usuario."""
        pid_str = input("PID del proceso a terminar: ").strip()
        try:
            pid = int(pid_str)
        except ValueError:
            print("PID inválido.")
            return
        if pid not in self.memory_manager.processes:
            print("Proceso no encontrado.")
            return
        self.memory_manager.remove_process(pid)
        msg = f"Proceso {pid} terminado y memoria liberada."
        self.logger.log(msg)
        print(msg)

    def _access_page(self) -> None:
        """Solicita PID y número de página y realiza el acceso."""
        pid_str = input("PID del proceso: ").strip()
        page_str = input("Número de página a acceder: ").strip()
        try:
            pid = int(pid_str)
            page = int(page_str)
        except ValueError:
            print("PID o número de página inválidos.")
            return
        msg = self.memory_manager.access_page(pid, page)
        self.logger.log(msg)
        print(msg)

    def _show_memory_map(self) -> None:
        """Muestra el mapa de RAM y Swap."""
        print("\n--- Mapa de RAM ---")
        print(self.memory_manager.get_ram_map())
        print("\n--- Mapa de Swap ---")
        print(self.memory_manager.get_swap_map())

    def _show_page_table(self) -> None:
        """Muestra la tabla de páginas de un proceso."""
        pid_str = input("PID del proceso: ").strip()
        try:
            pid = int(pid_str)
        except ValueError:
            print("PID inválido.")
            return
        print(self.memory_manager.get_page_table(pid))

    def _show_metrics(self) -> None:
        """Muestra las métricas de rendimiento."""
        print("\n--- Métricas ---")
        print(self.memory_manager.get_metrics())

    def _show_logs(self) -> None:
        """Muestra los eventos registrados."""
        print("\n--- Eventos ---")
        for event in self.logger.get_events():
            print(event)