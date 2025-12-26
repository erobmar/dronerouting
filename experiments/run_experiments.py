"""
Ejecución automatizada de experimentos

Este script recorre todas las instancias de datos en formato JSON, dentro del
directorio /data, y aplica cada uno de los métodos implementados (si procede).
Mide el tiempo de ejecución de cada uno de ellos y guarda los resultados en
un archivo CSV dentro del directorio /experiments/results.
"""

from __future__ import annotations

import csv
import time
from pathlib import Path
from typing import Any, Optional, Tuple

from common.graph import build_from_json
from exact_bb.branch_and_bound import BranchAndBoundSolver
from geo_heuristics.nearest_feasible import nearest_feasible
from geo_heuristics.greedy_weighted import greedy_weighted
from metaheuristics.simulated_annealing import simulated_annealing

Cost = tuple[float, float, int]


def ensure_dirs(results_dir: Path) -> None:
    """
    Crea el directorio de salida si no existe
    """
    results_dir.mkdir(parents=True, exist_ok=True)


def timed(callable_function, *args, **kwargs):
    """
    Ejecuta una función y devuelve su salida junto con el tiempo de ejecución
    """

    t0 = time.perf_counter()
    out = callable_function(*args, **kwargs)
    t1 = time.perf_counter()
    return out, (t1 - t0)


def add_row(
    rows,
    instance_name: str,
    n_clients: int,
    method: str,
    ok: bool,
    t: float,
    order,
    cost,
    frontier_size: int | None = None,
) -> None:
    """
    Añade una fila de resultados a la lista que posteriormente se escribirá en el CSV

    Normaliza los campos para que distintos métodos puedan compartir la misma estructura
    de salida.
    """

    rows.append(
        {
            "instance": instance_name,
            "n_clients": n_clients,
            "method": method,
            "ok": int(ok),
            "time_sec": f"{t:.6f}",
            "order": "" if order is None else ",".join(order),
            "distance": "" if cost is None else f"{cost[0]:.6f}",
            "risk": "" if cost is None else f"{cost[1]:.6f}",
            "recharges": "" if cost is None else str(int(cost[2])),
            "frontier_size": "" if frontier_size is None else str(frontier_size),
        }
    )


def main() -> None:
    """
    Función principal que ejecuta los experimentos

    Para cada isntancia, carga el grafo desde JSON, ejecuta cada uno de los métodos
    (nearest feasible, greedy weighted, simulated annealing y exacto branch and bound
    sólo para instancias pequeñas), registra el tiempo de ejecución de cada método con
    cada instancia y guarda los resultados en un CSV.
    """
    project_root = Path(__file__).resolve().parents[1]
    data_dir = project_root / "data"
    results_dir = project_root / "experiments" / "results"
    ensure_dirs(results_dir)

    instances = sorted(data_dir.glob("*.json"))

    if not instances:
        print("No hay archivos JSON en el directorio")
        return

    out_csv = results_dir / "results.csv"

    rows = []

    print("\n*** Experimentos ***\n")
    print(f"Instancias: {len(instances)}")
    print(f"CSV: {out_csv}\n")

    for json_path in instances:
        graph = build_from_json(str(json_path))
        hub = graph.hub
        start_battery = graph.max_battery

        print(f"\n--- {json_path.name} ---")
        print(
            f"hub = {hub} | clients = {len(graph.clients)} | start_battery = {start_battery}"
        )

        # 1 nearest feasible
        (nf_res, nf_time) = timed(nearest_feasible, graph, hub, start_battery)
        nf_order = nf_res[0] if nf_res else None
        nf_cost = nf_res[1] if nf_res else None
        add_row(
            rows,
            json_path.name,
            len(graph.clients),
            "nearest_feasible",
            nf_res is not None,
            nf_time,
            nf_order,
            nf_cost,
        )
        print(
            f"nearest feasible: ok={nf_res is not None} time={nf_time:.4f}s cost={nf_cost}"
        )

        # 2 greedy weighted
        (gw_res, gw_time) = timed(greedy_weighted, graph, hub, start_battery)
        gw_order = gw_res[0] if gw_res else None
        gw_cost = gw_res[1] if gw_res else None
        add_row(
            rows,
            json_path.name,
            len(graph.clients),
            "greedy_weighted",
            gw_res is not None,
            gw_time,
            gw_order,
            gw_cost,
        )
        print(
            f"greedy weighted: ok={gw_res is not None} time={gw_time:.4f}s cost={gw_cost}"
        )

        # 3 SA (inicializa desde greedy si existe, si no desde nearest)
        sa_init_order = None
        if gw_order is not None:
            sa_init_order = gw_order
        elif nf_order is not None:
            sa_init_order = nf_order

        if sa_init_order is not None:
            (sa_res, sa_time) = timed(
                simulated_annealing,
                graph,
                hub,
                start_battery,
                sa_init_order,
                iterations=5000,
                seed=0,
                t0=10.0,
                alpha=0.995,
            )
            sa_order = sa_res[0] if sa_res else None
            sa_cost = sa_res[1] if sa_res else None
            add_row(
                rows,
                json_path.name,
                len(graph.clients),
                "simulated_annealing",
                sa_res is not None,
                sa_time,
                sa_order,
                sa_cost,
            )
            print(
                f"SA:              ok={sa_res is not None} time={sa_time:.4f}s cost={sa_cost}"
            )
        else:
            sa_res, sa_time, sa_order, sa_cost = None, 0.0, None, None
            print("SA:              Saltado - No hay un orden inicial factible")

        # 4 Exact BB
        # Limitamos por nº de clientes para evitar sobrecarga
        bb_solutions = None
        bb_time = 0.0
        bb_frontier_size = 0
        bb_best_cost = None

        if (
            len(graph.clients) <= 12
        ):  # Ajustar este umbral en función del equipo en que se ejecute
            solver = BranchAndBoundSolver(graph, hub)
            (bb_solutions, bb_time) = timed(solver.solve, start_battery)
            bb_frontier_size = len(bb_solutions)

            if bb_frontier_size > 0:
                bb_best_cost = min(
                    (cost for _, cost in bb_solutions), key=lambda c: c[0]
                )

            add_row(
                rows,
                json_path.name,
                len(graph.clients),
                "exact_bb",
                bb_frontier_size > 0,
                bb_time,
                None,
                bb_best_cost,
                frontier_size=bb_frontier_size,
            )
            print(
                f"BB exact:          frontier={bb_frontier_size} time={bb_time:.4f}s best_cost={bb_best_cost}"
            )
        else:
            print("BB exact:           saltando (instancia demasiado grande)")

    # Escribir CSV

    headers = [
        "instance",
        "n_clients",
        "method",
        "ok",
        "time_sec",
        "order",
        "distance",
        "risk",
        "recharges",
        "frontier_size",
    ]

    with out_csv.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n CSV guardado en: {out_csv}\n")


if __name__ == "__main__":
    main()
