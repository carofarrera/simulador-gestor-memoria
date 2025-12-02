# Manual de Usuario

El **Manual de Usuario** describe el funcionamiento de la interfaz de línea de comandos (CLI) del simulador del gestor de memoria.  Asegúrese de haber configurado correctamente el archivo `config.ini` y de ejecutar el programa como se indica en el README.

## Inicio del simulador

Para ejecutar el simulador, sitúese en la raíz del repositorio y ejecute:

```bash
python src/main.py
```

El programa leerá `config.ini` y mostrará un resumen de la configuración actual de la memoria (tamaño de RAM, Swap y página).  A continuación, aparecerá el menú principal:

```
=== Simulador de Gestor de Memoria ===
1. Crear nuevo proceso
2. Terminar proceso
3. Acceder a página de proceso
4. Mostrar mapa de memoria (RAM y Swap)
5. Mostrar tabla de páginas de un proceso
6. Mostrar métricas de rendimiento
7. Mostrar eventos registrados
0. Salir
```

### 1. Crear nuevo proceso

Esta opción permite simular la llegada de un nuevo proceso.  El sistema preguntará el tamaño del proceso en kilobytes (KB).  Puede introducir un valor numérico o `r` para generar un tamaño aleatorio entre una página y la mitad de la RAM.  El simulador calculará cuántas páginas necesita el proceso en función del tamaño de página y asignará marcos disponibles en RAM.  Si no hay marcos libres, se invocará el algoritmo de reemplazo FIFO para seleccionar una página víctima y realizar el intercambio con Swap【823107480250600†L88-L99】.  Al finalizar, se mostrará el **PID** asignado al proceso, el número de páginas y cualquier operación de swapping realizada.

### 2. Terminar proceso

Permite liberar toda la memoria utilizada por un proceso.  El sistema solicitará el **PID** del proceso a terminar; al ingresar el PID correspondiente, el simulador liberará los marcos en RAM y en Swap asociados a sus páginas y removerá su tabla de páginas.  Se registrará el evento en los logs.

### 3. Acceder a página de proceso

Esta opción simula una referencia de memoria a una página lógica de un proceso.  El usuario debe introducir el **PID** y el número de página (a partir de cero).  El simulador resolverá la dirección utilizando la TLB y la tabla de páginas.  Si la página está en RAM, se indicará el marco físico y se actualizará la TLB.  Si la página se encuentra en Swap, se contará un fallo de página, se traerá la página a RAM (reemplazando otra página si es necesario) y se informará del swapping【823107480250600†L88-L99】.

### 4. Mostrar mapa de memoria (RAM y Swap)

Muestra una representación textual de todos los marcos en RAM y Swap.  En RAM, cada entrada indica el índice del marco y el proceso y página que lo ocupan o que está libre.  En Swap, se muestra el mismo formato.  Ejemplo:

```
--- Mapa de RAM ---
[0] P1, Pag 0 | [1] P1, Pag 1 | [2] Libre | [3] P2, Pag 0 | ...
--- Mapa de Swap ---
[0] Libre | [1] P2, Pag 3 | ...
```

### 5. Mostrar tabla de páginas de un proceso

Permite consultar la tabla de páginas de un proceso activo.  Introduzca el **PID** y se mostrará cada página lógica junto con su localización actual: `RAM[marco]` si está presente en memoria principal, `Swap[marco]` si está intercambiada o `No asignada` si aún no se ha asignado.

### 6. Mostrar métricas de rendimiento

Presenta estadísticas acumuladas desde que se inició el simulador:

* **Fallas de página**: cantidad de veces que se accedió a una página que no estaba en RAM【823107480250600†L88-L99】.
* **Operaciones de swapping**: número de veces que se movieron páginas entre RAM y Swap.
* **Utilización de RAM**: porcentaje de marcos ocupados en la memoria principal.

### 7. Mostrar eventos registrados

Muestra una lista de todos los eventos registrados durante la ejecución, como mensajes de swapping, creación y terminación de procesos y fallos de página.  Este registro sirve para analizar el comportamiento del simulador.

### 0. Salir

Finaliza la ejecución del simulador.  Los datos no se guardan de forma persistente, por lo que al reiniciar el programa todos los procesos se deberán crear nuevamente.

## 📸 Capturas del funcionamiento

Para ilustrar el uso del simulador, a continuación se presentan algunas capturas de pantalla tomadas durante su ejecución:

### Menú principal

Esta captura muestra el menú inicial del sistema con sus opciones para crear procesos, terminar procesos, acceder a páginas y consultar la memoria:

![Menú principal del simulador](img/captura_menu.png)

### Vista del mapa de memoria

En la siguiente captura se observa la representación textual de la memoria RAM y del área de swap tras la creación de varios procesos.  Se aprecian los marcos ocupados por las páginas de distintos procesos y los marcos libres tanto en RAM como en Swap:

![Representación de memoria RAM y Swap](img/captura_memoria.png)
