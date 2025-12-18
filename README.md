actividad2_lcs_drones/
├─ data/
│  ├─ valladolid.json
│  ├─ gotham.json
│  ├─ mordor.json
│  └─ ... (instancias N=10,15,20,25)
│
├─ common/
│  ├─ model.py         # Clases Node, Edge, Graph, Solution (ruta), etc.
│  ├─ io.py            # Lectura de JSON -> Graph
│  ├─ geometry.py      # Intersección segmento-polígono, distancia, etc.
│  ├─ battery.py       # Funciones de chequeo de batería, consumo, recargas
│  └─ pareto.py        # Dominancia, cálculo de conjunto no dominado, etc.
│
├─ exact_bb/
│  └─ exact_solver.py  # Backtracking + poda (branch & bound)
│
├─ heuristic_geo/
│  └─ geo_solver.py    # Heurística geométrica (grafo restringido, etc.)
│
├─ metaheuristic/
│  └─ sa_solver.py     # Simulated Annealing (u otra heurística que elijas)
│
├─ experiments/
│  ├─ run_experiments.py  # Lanza los 3 métodos sobre las instancias
│  ├─ results/            # CSVs con tiempos, memoria, fronteras, etc.
│  └─ plots/              # (opcional) gráficas si las generas con Python
│
├─ main.py             # Menú interactivo simple: elegir instancia + método
└─ README.md
