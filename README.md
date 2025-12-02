# Simulador de Gestor de Memoria RAM y Swap

Este repositorio contiene una implementación completa de un **simulador del gestor de memoria** que soporta multiprogramación, paginación, swapping y visualización del estado de la memoria.  El objetivo del proyecto es ayudar a comprender cómo un sistema operativo asigna memoria física a distintos procesos y gestiona la memoria virtual cuando la memoria principal se agota【823107480250600†L0-L17】.

El simulador se desarrolla en **Python** con una interfaz de línea de comandos (CLI).  Lee un archivo de configuración para establecer el tamaño de la memoria física (RAM), el tamaño del área de intercambio (Swap) y el tamaño de página/marco, calcula cuántas páginas necesita cada proceso y asigna marcos en RAM o en Swap.  Cuando no hay marcos libres, emplea un algoritmo de reemplazo FIFO para mover páginas a Swap【823107480250600†L50-L99】.

## Integrantes

Incluye aquí los nombres completos de los integrantes del equipo que desarrollaron el proyecto.

## Estructura del repositorio

```
memory_simulator_repo/
├── src/             # Código fuente del simulador (módulos Python)
│   ├── config.py    # Lectura del archivo config.ini y cálculo de marcos
│   ├── process.py   # Clase `Process` con tabla de páginas y estados
│   ├── memory_manager.py  # Gestor de memoria que administra RAM, Swap, TLB y algoritmos de reemplazo
│   ├── replacement.py     # Implementación del algoritmo FIFO (y base para otros algoritmos)
│   ├── logger.py    # Registro de eventos y logs
│   ├── cli.py       # Interfaz de línea de comandos para interactuar con el simulador
│   └── main.py      # Punto de entrada para ejecutar el simulador
├── docs/            # Documentación en formato Markdown y PDF
│   ├── manual_usuario.md  # Manual de usuario de la CLI
│   ├── manual_tecnico.md  # Manual técnico y descripción de la arquitectura
│   └── reporte_tecnico.pdf # Informe técnico en formato PDF
├── tests/           # Casos de prueba y evidencias (capturas, logs)
│   └── ejemplo_log.txt    # Ejemplo de ejecución con registros
├── config.ini       # Archivo de configuración con tamaños de RAM, Swap y página
└── README.md        # Este documento
```

## Instalación y ejecución

1. **Prerrequisitos**: Se requiere Python 3.10 o superior. No se necesitan bibliotecas adicionales.
2. **Configurar los parámetros del simulador**: edite el archivo `config.ini` para indicar el tamaño de la memoria RAM y Swap (en KB) y el tamaño de página/marco.  Estos parámetros determinan el número de marcos disponibles en RAM y Swap【823107480250600†L50-L58】.
3. **Ejecutar el simulador**:

   Desde la raíz del repositorio, utilice el siguiente comando para iniciar la aplicación en modo CLI:

   ```bash
   python src/main.py
   ```

   Al iniciar, el programa mostrará un resumen de la configuración y un menú interactivo con las opciones para crear procesos, terminar procesos, acceder a páginas, visualizar el mapa de RAM y Swap, consultar la tabla de páginas de un proceso, mostrar métricas de rendimiento y revisar los eventos registrados【823107480250600†L73-L88】.

## Breve explicación del diseño

El simulador está construido con módulos que representan las principales entidades del gestor de memoria:

* **Config** (`config.py`): Lee el archivo `config.ini` y calcula el número total de marcos en RAM y Swap.
* **Process** (`process.py`): Representa cada proceso con su identificador (PID), tamaño en kilobytes, número de páginas necesarias y tabla de páginas con bits de presencia y referencias.
* **MemoryManager** (`memory_manager.py`): Es el núcleo del simulador.  Administra las listas de marcos en RAM y en Swap, asigna páginas a marcos, implementa el algoritmo FIFO para seleccionar una página víctima cuando la RAM se llena y realiza el swapping a Swap【823107480250600†L88-L99】.  Lleva métricas de fallos de página y swaps y mantiene una caché TLB de traducciones con política LRU.
* **ReplacementAlgorithm** (`replacement.py`): Define la interfaz para algoritmos de reemplazo y su implementación FIFO.  Puede extenderse para soportar LRU o reloj【823107480250600†L88-L93】.
* **Logger** (`logger.py`): Registra eventos importantes del simulador, como movimientos de páginas entre RAM y Swap y fallos de página.
* **CLI** (`cli.py`): Proporciona una interfaz en consola para que el usuario interactúe con el simulador.  Muestra menús, solicita datos al usuario y llama a los métodos del `MemoryManager` para ejecutar las operaciones correspondientes【823107480250600†L73-L88】.

El algoritmo de reemplazo implementado es **FIFO (First‑In, First‑Out)**; cuando la RAM se llena, la página que ingresó primero es seleccionada como víctima y se traslada a Swap【823107480250600†L88-L99】.  La estructura de datos de la tabla de páginas se implementa mediante un diccionario por proceso donde cada entrada incluye un bit de presencia, el índice de marco en RAM (si está presente) y el índice en Swap (si está intercambiada).

## Licencia

Este proyecto puede incluir una licencia de uso a elección del equipo.  Si se desea, agregue un archivo `LICENSE` en la raíz del repositorio.
