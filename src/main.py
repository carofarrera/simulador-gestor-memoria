"""
Punto de entrada del simulador de gestión de memoria. Crea la interfaz
CLI y la pone en marcha. Este archivo permite ejecutar el simulador
directamente con `python -m memory_simulator` o `python src/main.py`.
"""

# Importación absoluta para permitir ejecución directa
from cli import CLI


def main() -> None:
    cli = CLI(config_path="../config.ini")
    cli.run()


if __name__ == "__main__":
    main()