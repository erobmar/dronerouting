"""
Utilidades de entrada/salida para la carga de mapas en formato JSON

Este módulo proporciona una clase auxiliar para cargar y validar
archivos JSON que contienen mapas válidos para la aplicación.
"""

import json
from pathlib import Path


class JsonLoader:
    """
    Carga de archivos JSON

    Encapsula la lectura de archivos JSON y proporciona una lectura controlada
    de los datos cargados. Incluye cierto control de errores, comprobando si
    la carga del archivo se ha realizado correctamente antes de acceder al contenido.
    """

    def __init__(self, file_path: str):
        """
        Inicializa el cargador con la ruta del archivo JSON

        Recibe como parámetro la ruta del archivo JSON
        """

        # El uso de la clase Path asegura compatibilidad multiplataforma
        self.file_path = Path(file_path)
        self.data = None

    def load(self) -> bool:
        """
        Carga el archivo JSON desde disco

        Intenta leer el archivo JSON y deserializar su contenido. En caso de éxito lo
        almacena en memoria y devuelve True, en caso contrario devuelve False
        """
        try:
            if not self.file_path.exists():
                raise FileNotFoundError("JSON No encontrado " + self.file_path)

            with open(self.file_path) as file:
                self.data = json.load(file)

            return True

        except Exception:

            return False

    def get_data(self):
        """
        Devuelve los datos del JSON cargado

        Levanta una excepción en tiempo de ejecución si se intenta recuperar datos
        antes de haber cargado un JSON.

        Devuelve la estructura de datos resultante de deserializar el JSON
        """
        if self.data is None:
            raise RuntimeError("JSON no cargado")
        return self.data
