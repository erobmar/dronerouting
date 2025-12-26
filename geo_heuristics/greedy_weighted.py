"""
Heurística geométrica voraz con función de coste ponderada

Este módulo implementa una heurística constructiva que selecciona, en cada
iteración, el siguiente cliente a visitar minimizando una función de coste
escalar que combina distancia, riesgo y número de recargar mediante pesos
configurables.

Utiliza el método transfer de la clase Graph para comprobar la factibilidad
de cada salto
"""

from typing import List, Tuple, Optional
from common.graph import *

Cost = Tuple[float, float, int]
"""Tupla que representa el coste de una ruta en términos de distancia, riesgo y recargas, respectivamente"""

def greedy_weighted(
        graph: Graph, 
        hub: str, 
        start_battery: float, 
        w_distance: float= 1.0,
        w_risk: float = 100.0,
        w_recharges: float = 1000.0, 
        ) -> Optional[Tuple[Tuple[str, ...], Cost]]:
    """
    Construye una ruta mediante una heurística voraz basada en coste ponderado
    
    En cada iteración, evalúa todos los clientes no visitados y selecciona aquel cuya transferencia
    factible minimiza una funcón de coste escalar que combina distancia, riesgo y número de recargas
    utilizando pesos configurables (w_distance, w_risk y w_recharges).
    
    Devuelve una tupla con el orden de visita de los clientes y el coste total o None si 
    no existe ruta factible
    """
    
    remaining = set(graph.clients)
    order: List[str] = []
    last = hub
    battery = start_battery
    total_distance = 0.0
    total_risk = 0.0
    total_recharges = 0

    while remaining:
        best_client = None
        best_result = None
        best_score = None

        for client in remaining:
            result = graph.transfer(last, client, battery)
            
            if result is None:
                continue

            distance, risk, recharges_used, new_battery = result
            score = w_distance * distance + w_risk * risk + w_recharges * recharges_used

            if best_score is None or score < best_score:
                best_score = score
                best_client = client
                best_result = result
            
        if best_client is None:
            return None
        
        distance, risk, recharges_used, battery = best_result
        total_distance += distance
        total_risk += risk
        total_recharges += recharges_used

        order.append(best_client)
        remaining.remove(best_client)
        last = best_client

    result = graph.transfer(last, hub, battery)
    if result is None:
        return None
    
    distance, risk, recharges_used, battery = result

    total_distance += distance
    total_risk += risk
    total_recharges += recharges_used


    return tuple(order), (total_distance, total_risk, total_recharges)