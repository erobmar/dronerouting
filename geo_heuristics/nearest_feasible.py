"""
Heurística geométrica de Vecino más cercano factible

Este módulo implementa una heurística constructiva que, partiendo del hub, selecciona
iterativamente el cliente no visitado más cercano para el que exista una transferencia
factible, continuando hasta visitar todos los clientes e intentando regresar al hub.

Si en algún punto no existe un cliente factible, falla y devuelve None
"""

from typing import List, Tuple, Optional
from common.graph import *

Cost = Tuple[float, float, int]
""" Tupla que representa el coste de una ruta en términos de distancia, riesgo y recargas, respectivamente"""


def nearest_feasible(
    graph: Graph, hub: str, start_battery: float
) -> Optional[Tuple[Tuple[str, ...], Cost]]:
    """
    Construye una ruta utilizando la heurística del vecino más cercano factible

    En cada iteración se selecciona el cliente no visitado más cercano para el que exista
    transferencia factible usando el método transfer de la clase Graph.

    Devuelve una tupla con el orden de visita de los clientes y el coste total o None si
    no existe ruta factible
    """
    # Inicializamos
    remaining = set(graph.clients)
    order: List[str] = []
    last = hub
    battery = start_battery
    total_distance = 0.0
    total_risk = 0.0
    total_recharges = 0

    while remaining:

        # Ordenamos los candidatos por distancia, seleccionamos el de menor coste y lo añadimos
        candidates = []

        for cand in remaining:
            result = graph.transfer(last, cand, battery)
            if result is not None:
                distance, _, _, _ = result
                candidates.append((distance, cand))

        candidates.sort(key=lambda x: x[0])
        candidates = [c for _, c in candidates]

        chosen = None
        chosen_result = None

        for client in candidates:
            result = graph.transfer(last, client, battery)
            if result is not None:
                chosen = client
                chosen_result = result
                break

        if chosen is None:
            return None

        distance, risk, recharges_used, battery = chosen_result
        total_distance += distance
        total_risk += risk
        total_recharges += int(recharges_used)

        order.append(chosen)
        remaining.remove(chosen)
        last = chosen

    # Una vez visitados todos, volvemos al hub
    result = graph.transfer(last, hub, battery)
    if result is None:
        return None

    distance, risk, recharges_used, battery = result
    total_distance += distance
    total_risk += risk
    total_recharges += int(recharges_used)

    return tuple(order), (total_distance, total_risk, total_recharges)
