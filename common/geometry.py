"""
Módulo de utilidades geométricas en 2D

Este módulo proporciona las estructuras y funciones necesarias para realizar
cálculos geométricos en el plano. Es utilizada por el resto de módulos del
proyecto para validar trayectorias de vuelo. Incluye representación de puntos,
segmentos y polígonos, así como comprobaciones de intersección, pertenencia a
polígonos y cálculo de distancias.

El módulo está diseñado para ser independiete de la lógica de planificación,
actuando, simplemente, de capa de soporte de cálculo geométrico
"""

from __future__ import annotations

from typing import Iterable, List, Optional, Tuple
from math import sqrt


EPSILON = 1e-9  # Número muy pequeño para aclarar casos límite


class Point:
    """
    Representa un punto en el plano

    Se define mediante sus coordenadas cartesianas (x, y) y es el elemento básico
    para la construcción de segmentos, planos y trayectorias
    """

    x: float
    y: float

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y


class Segment:
    """
    Representa un segmento dirigido en el plano

    Definido por sus dos extremos 'a' y 'b'. Modela trayectorias entre nodos y aristas
    de polígonos
    """

    a: Point
    b: Point

    def __init__(self, a: Point, b: Point):
        self.a = a
        self.b = b


class Polygon:
    """
    Representa un polígono en el plano

    Se define mediante una secuencia ordenada de vértices y se asume cerrado. Proporciona
    acceso a sus vértices, aristas y su bound box.
    """

    def __init__(self, vertices: Iterable[Point]):
        vertex_list = list(vertices)

        if len(vertex_list) < 3:
            raise ValueError("Un polígono debe tener 3 o más vértices")

        self._vertices: List[Point] = vertex_list
        self._edges: Optional[List[Segment]] = None

        x_coords = [point.x for point in vertex_list]
        y_coords = [point.y for point in vertex_list]

        self._bound_box: Tuple[float, float, float, float] = (
            min(x_coords),
            min(y_coords),
            max(x_coords),
            max(y_coords),
        )

    @property
    def vertices(self) -> List[Point]:
        return self._vertices

    @property
    def bound_box(self) -> Tuple[float, float, float, float]:
        return self._bound_box

    @property
    def edges(self) -> List[Segment]:

        if self._edges is None:

            vertex_list = self._vertices
            n = len(vertex_list)

            self._edges = [
                Segment(vertex_list[i], vertex_list[(i + 1) % n]) for i in range(n)
            ]

        return self._edges

    def contains_point(self, p: Point) -> bool:

        return False


def distance(a: Point, b: Point) -> float:
    """
    Calcula la distancia euclídea entre dos puntos en el plano
    """
    # Devuelve la raíz del cuadrado de las diferencias entre sus coordenadas
    # La distancia entre esos dos puntos
    return sqrt(((a.x - b.x) ** 2) + ((a.y - b.y) ** 2))


def _turn(a: Point, b: Point, c: Point) -> float:
    """
    Calcula el giro (horario, antihorario, colineal) entre los dos vectores definidos por
    los puntos a, b y c
    """
    return ((b.x - a.x) * (c.y - a.y)) - ((b.y - a.y) * (c.x - a.x))


def _on_segment(a: Point, b: Point, c: Point) -> bool:
    """
    Comprueba si el punto c se encuentra en el segmento AB
    """
    if (
        min(a.x, b.x) - EPSILON <= c.x <= max(a.x, b.x) + EPSILON
        and min(a.y, b.y) - EPSILON <= c.y <= max(a.y, b.y) + EPSILON
    ):
        return True
    return False


def point_in_polygon(a: Point, p: Polygon, *, include_boundary: bool = True) -> bool:
    """
    Determina si un punto pertenece al interior de un polígono

    Permite considerar los puntos situados en el borde como pertenecientes al interior o no
    """
    # Definimos el include_boundary por defecto a True por precisión

    min_x, min_y, max_x, max_y = p.bound_box

    # Primer chequeo rápido con bound box
    if (
        (a.x < min_x - EPSILON)
        or (a.x > max_x + EPSILON)
        or (a.y < min_y - EPSILON)
        or (a.y > max_y + EPSILON)
    ):
        return False

    # Comprobamos si está en los límites
    if include_boundary:
        for edge in p.edges:
            if (abs(_turn(edge.a, edge.b, a))) <= EPSILON and _on_segment(
                edge.a, edge.b, a
            ):
                return True

    # Si no queremos contar el borde como dentro lo detectamos y excluimos
    if not include_boundary:
        for edge in p.edges:
            if abs(_turn(edge.a, edge.b, a)) <= EPSILON and _on_segment(
                edge.a, edge.b, a
            ):
                return False

    inside = False
    vertices = p.vertices
    n = len(vertices)

    # Proyectamos rayos al infinito en cada dirección
    for i in range(n):
        point_a = vertices[i]
        point_b = vertices[(i + 1) % n]

        # Y comprobamos si el rayo cruza la horizontal que pasa por el punto a
        horizontal = (point_a.y > a.y) != (point_b.y > a.y)
        if not horizontal:
            continue

        intersection_point_x = point_a.x + (a.y - point_a.y) * (
            point_b.x - point_a.x
        ) / (point_b.y - point_a.y)

        if intersection_point_x > a.x:
            inside = not inside

    return inside


def segments_intersect(
    segment_a: Segment, segment_b: Segment, *, include_endpoints: bool = True
) -> bool:
    """
    Comprueba si dos segmentos del plano se intersectan

    Permite configurar si los extremos se consideran intersecciones válidas o no
    """

    # Almacenamos los cuatro puntos que definen a los dos segmentos
    point_a, point_b = segment_a.a, segment_a.b
    point_c, point_d = segment_b.a, segment_b.b

    # Calculamos los giros de los vectores que defines 3 a 3
    turn_abc = _turn(point_a, point_b, point_c)
    turn_abd = _turn(point_a, point_b, point_d)
    turn_cda = _turn(point_c, point_d, point_a)
    turn_cdb = _turn(point_c, point_d, point_b)

    # Comprobamos si intersectan
    if (
        turn_abc > EPSILON
        and turn_abd < -EPSILON
        or turn_abc < -EPSILON
        and turn_abd > EPSILON
    ) and (
        turn_cda > EPSILON
        and turn_cdb < -EPSILON
        or turn_cda < -EPSILON
        and turn_cdb > EPSILON
    ):
        return True

    # Comprobamos colinearidad y casos límite
    if (abs(turn_abc) <= EPSILON) and _on_segment(point_a, point_b, point_c):
        return include_endpoints or (point_c != point_a and point_c != point_b)
    if (abs(turn_abd) <= EPSILON) and _on_segment(point_a, point_b, point_d):
        return include_endpoints or (point_d != point_a and point_d != point_b)
    if (abs(turn_cda) <= EPSILON) and _on_segment(point_c, point_d, point_a):
        return include_endpoints or (point_a != point_c and point_a != point_d)
    if (abs(turn_cdb) <= EPSILON) and _on_segment(point_c, point_d, point_b):
        return include_endpoints or (point_b != point_c and point_b != point_d)

    return False


def _bbox_intersect(
    bound_box_1: Tuple[float, float, float, float],
    bound_box_2: Tuple[float, float, float, float],
) -> bool:
    """
    Comprueba si dos bound boxes intersectan
    """
    # Extraemos las coordenadas máximas y mínimas de las bound box
    min_x_1, min_y_1, max_x_1, max_y_1 = bound_box_1
    min_x_2, min_y_2, max_x_2, max_y_2 = bound_box_2

    condition_1 = max_x_1 < min_x_2 - EPSILON
    condition_2 = max_x_2 < min_x_1 - EPSILON
    condition_3 = max_y_1 < min_y_2 - EPSILON
    condition_4 = max_y_2 < min_y_1 - EPSILON

    return not (condition_1 or condition_2 or condition_3 or condition_4)


def segment_intersects_polygon(
    segment: Segment, polygon: Polygon, *, include_boundary: bool = True
) -> bool:
    """
    Comprueba si un segmento intersecta un polígono
    """
    # Extraemos las coordenadas de los extremos del segmento y creamos una bound box con ellas
    coord_a_x, coord_a_y, coord_b_x, coord_b_y = (
        segment.a.x,
        segment.a.y,
        segment.b.x,
        segment.b.y,
    )
    segment_bound_box = (
        min(coord_a_x, coord_b_x),
        min(coord_a_y, coord_b_y),
        max(coord_a_x, coord_b_x),
        max(coord_a_y, coord_b_y),
    )

    # Y comprobamos si esa bound box y el la del polígono colisionan
    if not (_bbox_intersect(segment_bound_box, polygon.bound_box)):
        return False

    for edge in polygon.edges:
        if segments_intersect(segment, edge, include_endpoints=include_boundary):
            return True

    return False


def segment_crosses_polygon(segment: Segment, polygon: Polygon) -> bool:
    """
    Comprueba si un segmento atraviesa el interior de un polígono
    """
    # Comprobamos si los extremos del segmento están dentro del polígono
    a_inside = point_in_polygon(segment.a, polygon, include_boundary=False)
    b_inside = point_in_polygon(segment.b, polygon, include_boundary=False)

    # Si un punto está dentro y el otro no -> el segmento atraviesa el polígono
    if a_inside != b_inside:
        return True

    # Si ambos extremos están dentro, contaremos el número de intersecciones
    # Si lo hace dos o más veces es porque lo atraviesa
    count = 0
    for edge in polygon.edges:
        if segments_intersect(segment, edge, include_endpoints=True):
            count += 1
            if count >= 2:
                return True

    return False
