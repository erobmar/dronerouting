"""
Módulo de grafo de navegación para la planificación de rutas con drones

Este módulo define la clase Graph, que modela en forma de grafo el entorno
de operación del dron. El grafo se construye a partir de una descripción en
formato JSON.

Las aristas del grafo representan trayectorias rectilíneas factibles entre pares
de nodos, ponderadas por distancia, riesgo y consumo de batería. 

Adicionalmente, se proporciona una función de transferencia que evalúa si existe
un camino factible entre dos nodos.
"""

from common.geometry import (Point, Segment, Polygon, distance, segment_intersects_polygon)

from common.io import JsonLoader

import heapq

class Graph:
    """
    Representa un grafo dirigido ponderado para la navegación del dron
    
    El grafo contiene los nodos del mapa (hub, clientes y recargas), los polígonos
    de zonas de riesgo y exclusión aérea y las aristas dirigidas entre nodos factibles con
    su coste asociado.
    
    Se proporcionan métodos asociados al trabajo con el grafo.    
    """
    max_battery : float
    nodes: dict[str, Point]
    clients: list[str]
    recharges: list[str]
    hub: str
    forbidden_zones: list[Polygon]
    risk_zones: list[tuple[Polygon, float]]
    edges: dict[str, dict[str, tuple[float, float,float]]]

    def __init__(self, max_battery : float,
                 nodes: dict[str, Point],
                 clients: list[str],
                 recharges: list[str],
                 hub: str,
                 forbidden_zones: list[Polygon],
                 risk_zones: list[tuple[Polygon, float]],
                 edges: dict[str, dict[str, tuple[float, float,float]]]):
        
        self.max_battery = max_battery
        self.nodes = nodes
        self.clients = clients
        self.recharges = recharges
        self.hub = hub
        self.forbidden_zones = forbidden_zones
        self.risk_zones = risk_zones
        self.edges = edges


    def is_recharge(self, node: str) -> bool:
        """
        Indica si un nodo es punto de recarga
        """
        return node in self.recharges

            
    def edge_cost(self, point_a: str, point_b: str):
        """
        Devuelve el coste de una arista
        
        El coste se expresa como una tupla (distancia, riesgo, consumo)
        Si la arista no existe, devuelve None
        """
        return self.edges.get(point_a,{}).get(point_b, None)


    def transfer(self, start: str, goal: str, battery_left: float):
        """
        Determina si es posible desplazarse de un nodo origen a un nodo destino
        
        Busca un camino factible para alcanzar el nodo destino desde el inicio, teniendo en
        cuenta el consumo de batería y la posibilidad de recargarla. Se priorizan las soluciones
        con un menor número de recargas.
        
        Devuelve una tupla con la distancia y riesgo acumulados, el número de recargas realizadas
        y la batería restante al llegar a destino. Si no hya un camino factible devuelve None        
        """

        # Creamos una cola de prioridades con los estados parciales
        priority_queue = [(0, 0.0, 0.0, start, battery_left)]

        # Diccionario indexado por tuplas para almacenar el mejor battery_left visto
        best_battery = {}

        while priority_queue:

            # Almacenamos las recargas utilizadas, distancia y riesgo acumulados y número
            # de paradas para recargar desde start al nodo actual, así como la batería restante
            recharges_used, distance_acc, risk_acc, current_node, battery_remaining = heapq.heappop(priority_queue)

            # Sale del bucle            
            if recharges_used > len(self.recharges):
                continue

            if current_node == goal:
                return distance_acc, risk_acc, recharges_used, battery_remaining

            key = (current_node, recharges_used)
            previous_best_battery = best_battery.get(key)

            if previous_best_battery is not None and previous_best_battery >= battery_remaining:
                continue
            best_battery[key] = battery_remaining

            # Expandir vecinos
            for v, (dist, risk, batt_cost) in self.edges.get(current_node, {}).items():
                if batt_cost > battery_remaining:
                    continue

                new_best_batt = battery_remaining - batt_cost
                new_recharges_used = recharges_used

                # Si llega a un punto de recarga o hub, recarga y cuenta como parada si no es un hub
                if self.is_recharge(v):

                    # Si es recarga, sumamos 1
                    if v != self.hub:
                        new_recharges_used += 1

                    new_best_batt = self.max_battery

                heapq.heappush(priority_queue, (new_recharges_used, distance_acc + dist, 
                                                    risk_acc + risk, v, new_best_batt))
                    
        return None




# Construye un grafo desde un archivo JSON
def build_from_json(path: str) -> Graph:
    """
    Construye un grafo a partir de un archivo JSON
    
    A partir de la información contenida en un archivo JSON válido se generan las aristas dirigidas
    entre nodos cuya trayectoria no intersecta zonas prohibidas. Cada arista lleva su coste de
    distancia, riesgo y consumo de batería asociado.
    
    Devuelve una instancia de Graph inicializada
    """
    clients = []
    recharges = []
    hub = None
    
    
    # Cargamos el JSON
    loader = JsonLoader(path)
    if not loader.load():
        raise RuntimeError("Error al cargar el JSON")
    
    data = loader.get_data()

    # Extraemos los nodos
    nodes = {node["id"]: Point(float(node["x"]), float(node["y"])) for node in data["nodes"]}

    for node in data["nodes"]:
        node_type = node["type"]
        if node_type == "client":
            clients.append(node["id"])
        elif node_type == "recharge":
            recharges.append(node["id"])
        elif node_type == "hub":
            if hub is not None:
                raise ValueError("JSON incorrecto: Contiene más de un hub")
            hub = node["id"]

    # Extraemos los polígonos de zonas prohibidas 
    forbidden_zones = []
    for zone in data.get("forbidden_zones", []):
        vertices = [Point(p["x"], p["y"]) for p in zone["polygon"]]
        forbidden_zones.append(Polygon(vertices))
    
    # Extraemos los polígonos de zonas de peligro
    risk_zones = []
    for zone in data.get("risk_zones", []):
        vertices = [Point(p["x"], p["y"]) for p in zone["polygon"]]
        risk_zones.append((Polygon(vertices), float(zone["risk_factor"])))
    
    # Creamos el grafo dirigido
    graph = {i: {} for i in nodes}

    for i, point_i in nodes.items():
        for j, point_j in nodes.items():
            if i==j:
                continue

            # Creamos un segmento con esos puntos
            segment = Segment(point_i, point_j)

            blocked = False
            for polygon in forbidden_zones:
                if segment_intersects_polygon(segment, polygon, include_boundary=True):
                    blocked = True
                    break

            if blocked:
                continue


            # Calculamos los pesos
            dist_i_j = distance(point_i, point_j)
            battery = dist_i_j

            risk = 0.0

            for polygon, risk_factor in risk_zones:
                if segment_intersects_polygon(segment, polygon, include_boundary=True):
                    risk += risk_factor * dist_i_j

            graph[i][j] = (dist_i_j, risk, battery)

    if hub is None:
        raise ValueError("No se ha definido un hub en el archivo JSON")

    graph_from_json = Graph(float(data["max_battery"]), nodes, clients, recharges, hub, forbidden_zones, risk_zones, graph)
    
    return graph_from_json


