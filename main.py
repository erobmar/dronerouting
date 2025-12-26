"""
Punto de entrada principal del proyecto

Este módulo ofrece un menú de consola sencillo para ejecutar el flujo principal.
Permite lanzar los experimentos definidos en experiments/run_experiments.py y
salir del programa.
"""

from __future__ import annotations

from experiments.run_experiments import main as run_experiments_main


def main() -> None:
    """
    Muestra un menú interactivo por consola y ejecuta la opción seleccionada

        1 - Ejecutar los experimentos, generando el correspondiente CSV
        2 - Salir del programa
    """

    while True:
        print("\n-----------------------------------")
        print("|    Bienvenido a DroneRouting    |")
        print("|  V1.0   Autor: Eduardo Robledo  |")
        print("-----------------------------------")
        print("   Seleccione una opción: ")
        print("\n      1) Ejecutar experimentos")
        print("      2) Salir")

        option = input("").strip()

        if option == "1":
            print("\n *** Ejecutando experimentos ***")
            run_experiments_main()
            print("\n Fin de los experimentos ")
        elif option == "2":
            print("\n Saliendo")
            return
        else:
            print("\n Opción no válida. Pruebe de nuevo")


if __name__ == "__main__":

    main()
