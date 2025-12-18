from typing import Tuple
from common.graph import Graph

Cost = Tuple[float, float, int]

class BranchAndBoundSolver:
    
    def __init__(self, graph: Graph, hub):
        self.graph = graph
        self.hub = hub
        
        self.clients = graph.clients
        self.best_cost = None
        self.best_solution: None

        self.pareto = {}

    def solve(self, start_battery: float):
        self.best_solutions = []
        self.pareto.clear()

        self._bb(last_node = self.hub, visited = frozenset(), cost=(0.0, 0.0, 0.0), battery_left=start_battery, order=())
        return self.best_solutions

    def _bb(self, last_node, visited, cost, battery_left, order):

        # Caso 1: Poda por dominancia
        if self._is_dominated(last_node, visited, cost, battery_left):
            return
        self._register_pareto(last_node, visited, cost, battery_left)

        # Caso 2: Si se han visitado todos los nodos, volver al hub
        if len(visited) == len(self.clients):
            result = self.graph.transfer(last_node, self.hub, battery_left)

            if result is None:
                return
            
            distance, risk, recharges_used, new_battery = result

            final_cost = (cost[0] + distance,
                          cost[1] + risk,
                          cost[2] + recharges_used)
            
            self._try_complete_solution(order, final_cost)
            
            return
        
        # Caso 3: Expandir a cada cliente no visitado
        for client in self.clients:
            if client in visited:
                continue

            result = self.graph.transfer(last_node, client, battery_left)
            if result is None:
                continue

            distance, risk, recharges_used, new_battery = result
            new_cost = (cost[0] + distance,
                        cost[1] + risk,
                        cost[2] + recharges_used)
            
            self._bb(last_node = client,
                     visited = visited | {client},
                     cost = new_cost,
                     battery_left = new_battery,
                     order = order + (client,))
        

    def bound(self, last_node, visited, cost):
        pass

    def _is_dominated(self, last_node, visited, cost, battery_left) -> bool:
        
        key = (last_node, visited)
        pareto_frontier = self.pareto.get(key)

        if not pareto_frontier:        
            return False
        
        new_distance, new_risk, new_recharges = cost

        for current_cost, current_battery in pareto_frontier:
            current_distance, current_risk, current_recharges = current_cost

            dominates = (current_distance <= new_distance and
                         current_risk <= new_risk and
                         current_recharges <= new_recharges and
                         current_battery <= battery_left and(
                             current_distance < new_distance or
                             current_risk < new_risk or
                             current_recharges < new_recharges or
                             current_battery > battery_left
                         ))
            
            if dominates:
                return True
            return False
        

    def _register_pareto(self, last_node, visited, cost, battery_left) -> None:
        
        key = (last_node, visited)

        pareto_frontier = self.pareto.get(key, [])

        new_distance, new_risk, new_recharges = cost

        # Si está dominado por alguno existente no hacemos nada
        for current_cost, current_battery in pareto_frontier:
            current_distance, current_risk, current_recharges = current_cost

            current_dominates_new = (current_distance <= new_distance and
                                     current_risk <= new_risk and
                                     current_recharges <= new_recharges and
                                     current_battery >= battery_left and(
                                         current_distance < new_distance or
                                         current_risk < new_risk or
                                         current_recharges < new_recharges or
                                         current_battery > battery_left
                                     ))
            
            if current_dominates_new:
                self.pareto[key] = pareto_frontier
                return
            
        new_pareto_frontier = []
        for current_cost, current_battery in pareto_frontier:
            current_distance, current_risk, current_recharges = current_cost
        
        new_dominates_current = (new_distance <= current_distance and
                                 new_risk <= current_risk and
                                 new_recharges <= current_recharges and
                                 battery_left >= current_battery and(
                                     new_distance < current_distance or
                                     new_risk < current_risk or
                                     new_recharges < current_recharges or
                                     battery_left > current_battery
                                 ))
        if not new_dominates_current:
            new_pareto_frontier.append((current_cost, current_battery))

        new_pareto_frontier.append((cost, battery_left))
        self.pareto[key] = new_pareto_frontier

        

    def _try_complete_solution(self, order, cost):
        distance, risk, recharges_used = cost
        
        # Caso 1: Está dominada
        for _, (dist, r, rc) in self.best_solutions:
            if (dist <= distance) and (r <= risk) and rc <= recharges_used:
                if(dist <= distance) or (r < risk) or rc < recharges_used:
                    return # Dominada -> Se elimina
                
        non_dominated = []

        for existing_order, (d,r,rc) in self.best_solutions:
            if not ((distance <= d) and (risk <= r) and (recharges_used <= rc) and
                    (distance < d) or (risk < r) or (recharges_used < rc)):
                non_dominated.append(existing_order, (d,r,rc))
            
        non_dominated.append((order, cost))

        self.best_solutions = non_dominated

