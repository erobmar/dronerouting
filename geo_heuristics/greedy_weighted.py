from typing import List, Tuple, Optional
from common.graph import *

Cost = Tuple[float, float, int]

def greedy_weighted(
        grap: Graph, 
        hub: str, 
        start_battery: float, 
        w_distance: float= 1.0,
        w_risk: float = 100.0,
        w_recharges: float = 1000.0, 
        ) -> Optional[Tuple[Tuple[str, ...], Cost]]:

    remaining = set(grap.clients)
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
            result = grap.transfer(last, client, battery)
            
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

    result = grap.transfer(last, hub, battery)
    if result is None:
        return None
    
    distance, risk, recharges_used, battery = result

    total_distance += distance
    total_risk += risk
    total_recharges += recharges_used


    return tuple(order), (total_distance, total_risk, total_recharges)