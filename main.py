from __future__ import annotations

from pathlib import Path

from common.io import JsonLoader
from common.geometry import *
from common.graph import *
from exact_bb.branch_and_bound import *
from geo_heuristics.nearest_feasible import nearest_feasible
from geo_heuristics.greedy_weighted import greedy_weighted
from metaheuristics.simulated_annealing import simulated_annealing

def main() -> None:
   
 
    graph = build_from_json("data/gotham.json")

    nf = nearest_feasible(graph, graph.hub, 100.0 )
    gw = greedy_weighted(graph, graph.hub, 100.0)

    print("nearest_feasible: ", nf)
    print("greedy_weigthed: ", gw)

    initial_order, _= greedy_weighted(graph, graph.hub, 100.0)
    sa = simulated_annealing(graph, graph.hub, 100.0, initial_order, iterations=5000)
    print("SA: ", sa)





    return
    
if __name__ == "__main__":
   main()