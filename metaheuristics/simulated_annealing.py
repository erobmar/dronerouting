"""
Metaheurística de Simulated Annealing para planificación de rutas

Este módulo implementa la metaheurística de Simulated Annealing que opera
sobre el orden de visita de los clientes. Parte de una solución inicial factible
y explora el espacio de permutaciones mediante intercambios de dos posiciones 
aleatorias, aceptando soluciones peores de forma probabilística para escapar 
de óptimos locales.
"""

from __future__ import annotations

import math
import random
from typing import Optional, Sequence, Tuple

from common.graph import *

Cost = Tuple[float, float, int]
"""Tupla que representa el coste de una ruta en términos de distancia, riesgo y recargas, respectivamente"""

def evaluate_order(graph: Graph,
                   hub: str,
                   start_battery: float,
                   order: Sequence[str],
                   ) -> Optional[Cost]:
    
    """
    Evalúa la factibilidad y el coste de un orden de visita de clientes.
    
    Dado un orden, el método intenta construir la ruta completa hub -> clientes -> hub
    utilizando el método transfer de la clase Graph para cada salto. Si en algún punto la transferencia
    no es factible, falla y devuelve None.
    
    Si todas las transferencias son factibles, acumula distancia, riesgo y recargas y las devuelve en
    forma de tupla Cost.
    """
    battery = start_battery
    last_node = hub

    total_distance = 0.0
    total_risk = 0.0
    total_recharges = 0

    for client in order:
        result = graph.transfer(last_node, client, battery)
        if result is None:
            return None
        distance, risk, recharges_used, battery = result

        total_distance += distance
        total_risk += risk
        total_recharges += int(recharges_used)
        last_node = client

    result = graph.transfer(last_node, hub, battery)
    if result is None:
        return None
    
    distance, risk, recharges_used, battery = result

    total_distance += distance
    total_risk += risk
    total_recharges += int(recharges_used)

    return (total_distance, total_risk, total_recharges)


def score_cost(cost: Cost,
               w_distance: float = 1.0,
               w_risk: float = 100.0,
               w_recharges: float = 1000.0,
               ) -> float:
    """
    Calcula un coste escalar a partir de un coste multiobjetivo
    
    
    Combina distancia, riesgo y recargas mediante una suma ponderada en un valor escalar
    que se utiliza como función objetivo en la metaheurística.
    """
    distance, risk, recharges_used = cost
    return w_distance * distance + w_risk * risk + w_recharges * recharges_used


def swap_neighbor(order: Sequence[str], random_neighbor: random.Random):

    """
    Genera un vecino intercambiando dos posiciones aleatorias
    """

    if len(order) < 2:
        return tuple(order)
    
    i = random_neighbor.randrange(0, len(order))
    j = random_neighbor.randrange(0, len(order))

    while i==j:
        j = random_neighbor.randrange(0, len(order))

    new_order = list(order)
    new_order[i], new_order[j] = new_order[j], new_order[i]
    
    return tuple(new_order)


def simulated_annealing(graph: Graph,
                        hub: str,
                        start_battery: float,
                        initial_order: Sequence[str],
                        *,
                        seed: int = 0,
                        iterations: int = 5000,
                        t0: float = 10.0,
                        alpha: float = 0.995,
                        w_distance: float = 1.0,
                        w_risk: float = 100.0,
                        w_recharges: float = 1000.0,
                        ) -> Optional[Tuple[Tuple[str, ...], Cost]]:
    
    """
    Aplica la metaheurística de Simulated Annealing al orden de visita de clientes
    
    Parte de un orden inicial factible y genera soluciones vecinas mediante intercambios
    aleatorios de posiciones. La aceptación de soluciones peores se realiza mediante un
    parámetro de temrperatura que disminuye a lo largo de las iteraciones.
    
    Devuelve el mejor orden encontrado junto con su coste o None si el orden inicial no es factible.
    """
    
    random_neighbor = random.Random(seed)
    
    current_order = tuple(initial_order)
    current_cost = evaluate_order(graph, hub, start_battery, current_order)
    if current_cost is None:
        return None
    
    current_score = score_cost(current_cost, w_distance, w_risk, w_recharges)
    
    best_order = current_order
    best_cost = current_cost
    best_score = current_score
    
    temperature = t0
    
    for iter in range(iterations):
        candidate_order = swap_neighbor(current_order, random_neighbor)
        
        candidate_cost = evaluate_order(graph, hub, start_battery, candidate_order)
        if candidate_cost is None:
            temperature += alpha
            continue
        
        candidate_score = score_cost(candidate_cost, w_distance, w_risk, w_recharges)
        delta = candidate_score - current_score
        
        # Si mejora, aceptar. Si empeora, aceptar con probabilidad exp(-delta/T)
        if delta <= 0:
            accept = True
        else:
            # Evitar overflow si T es muy pequeña
            if temperature <= 1e-12:
                accept = False
            else:
                accept = (random_neighbor.random() < math.exp(-delta / temperature))
                
        
        if accept:
            current_order = candidate_order
            current_cost = candidate_cost
            current_score = candidate_score
        
            if current_score < best_score:
                best_order = current_order
                best_cost = current_cost
                best_score = current_score
        
        temperature += alpha
        
    
    return best_order, best_cost