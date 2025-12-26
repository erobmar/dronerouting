# DroneRouting

Autor: Eduardo ROBLEDO MARTÍNEZ
Versión: 1.0 (Enero 2025)

Programa para planificación multiobjetivo de rutas de drones en entornos urbanos - Actividad 2 de la asignatura Diseño Avanzado de Algoritmos del 3er curso del Báchelor en Informática de la Universidad UNIPRO.

El programa aplica diferentes métodos de planificación teniendo en cuenta restricciones geométricas y limitaciones de batería. Implementa un método exacto (Branch & Bound) y métodos aproximados (heurísticas geométricas y metaheurísticas).

## Estructura del proyecto

- `data/`  
  Instancias del problema en formato JSON (mapas).
  - `01_gotham.json` (N=10)
  - `02_mordor.json` (N=15)
  - `03_valladolid.json` (N=20)
  - `04_andorra.json` (N=25)

- `common/`  
  Funcionalidad compartida:
  - `geometry.py`: primitivas y operaciones geométricas (segmentos, polígonos, intersecciones).
  - `io.py`: carga de JSON.
  - `graph.py`: construcción del grafo y método `transfer()` (factibilidad + recargas).

- `exact_bb/`  
  Algoritmo exacto:
  - `branch_and_bound.py`: Branch & Bound multiobjetivo (Pareto).

- `geo_heuristics/`  
  Heurísticas geométricas:
  - `nearest_feasible.py`: vecino más cercano factible.
  - `greedy_weighted.py`: voraz ponderada (distancia/riesgo/recargas).

- `metaheuristics/`  
  Metaheurística:
  - `simulated_annealing.py`: Simulated Annealing sobre el orden de clientes.

- `experiments/`  
  Experimentación empírica:
  - `run_experiments.py`: ejecuta métodos sobre instancias y genera CSV.
  - `results/`: salida del CSV (`results.csv`).

- `main.py`  
  Menú de consola para ejecutar experimentos.

## Requisitos

- Python 3.x

## Ejecución

Desde la raíz del proyecto:

```bash
python3 main.py

(En entornos Windows es posible que haya que sustituir 'python3' por 'pyhton')