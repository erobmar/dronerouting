from __future__ import annotations

from pathlib import Path

from common.io import JsonLoader
from common.geometry import *
from common.tests import GeometryTests, print_results
from common.graph import *

"""
loader = JsonLoader('data/gotham.json')

if not loader.load():
    print("JSON no cargado")
else:
    city=loader.get_data()

    nodes = city["nodes"]
    forbidden = city["forbidden_zones"]
    risk = city["risk_zones"]

    print(city["city_name"])

a = Point(0.0, 2.0)
b = Point(5.0, 4.0)

print(distance(a,b))

def try_integration_json_load() -> None:
    """
"""
    Intento de test integral (opcional):
    - Carga un JSON con tu JsonLoader si existe.
    - Comprueba que hay nodos y zonas y que se pueden construir objetos Polygon.
    No rompe si todavía no cuadra tu API: lo deja como "skipped".
    """
"""
    # Cambia esta ruta si tu dataset está en otro sitio.
    candidate = Path("data") / "gotham.json"

    # Si no existe, no insistimos.
    if not candidate.exists():
        print("(Integración JSON) SKIP: no existe data/gotham.json")
        return

    # Ajusta estos imports a tu proyecto real cuando lo tengas a tiro.
    try:
        # Ejemplos típicos. Cambia según tu io.py
        from io import JsonLoader  # o: from common.io import JsonLoader
    except Exception:
        print("(Integración JSON) SKIP: no puedo importar JsonLoader (ajusta el import en main.py)")
        return

    try:
        loader = JsonLoader()
        data = loader.load(str(candidate))  # o loader.load_json / loader.read / etc.
    except Exception as e:
        print(f"(Integración JSON) SKIP: JsonLoader existe pero falló al cargar: {e}")
        return

    # Aquí depende 100% de tu modelo. Intentamos varios patrones comunes.
    # La idea es: que al menos veamos que hay nodos y polígonos.
    try:
        # Caso A: data es dict crudo (lo más probable)
        if isinstance(data, dict):
            nodes = data.get("nodes", [])
            fz = data.get("forbidden_zones", [])
            rz = data.get("risk_zones", [])
            print(f"(Integración JSON) Cargado dict: nodes={len(nodes)} forbidden={len(fz)} risk={len(rz)}")
        else:
            # Caso B: data es un objeto "mapa" con atributos
            nodes = getattr(data, "nodes", [])
            fz = getattr(data, "forbidden_zones", [])
            rz = getattr(data, "risk_zones", [])
            print(f"(Integración JSON) Cargado objeto: nodes={len(nodes)} forbidden={len(fz)} risk={len(rz)}")

        # No hacemos asserts duros aquí todavía, porque es integración temprana.
        # Si quieres endurecerlo: if len(nodes)==0: raise ...
    except Exception as e:
        print(f"(Integración JSON) SKIP: no pude inspeccionar la estructura cargada: {e}")
        return

    print("(Integración JSON) OK (básico): el loader devuelve algo con pinta de mapa.")
"""


def main() -> None:

    
    # build_from_json('data/gotham.json')

    """
    graph, nodes = build_from_json("data/gotham.json")

    print("Nodos: ", list(nodes.keys()))
    print("\nAristas:")
    for i, edge in graph.items():
        for j, w in edge.items():
            print(f"{i} -> {j} | dist={w[0]:.2f} risk={w[1]:.2f} bat={w[2]:.2f}")

    """

    g = build_from_json("data/gotham.json")


    # Salgo del hub con batería llena
    res = g.transfer(g.hub, "C2", g.max_battery)
    print("H -> C2:", res)

    # Intento H -> C1 (debería ser None porque está bloqueado por no-fly)
    res = g.transfer(g.hub, "C1", g.max_battery)
    print("H -> C1:", res)

    return
    ## Unit tests geometry
    # suite = GeometryTests()
    # results = suite.run_all()
    # print_results(results)

    ## Optional integration smoke test
    # try_integration_json_load()


if __name__ == "__main__":
   main()