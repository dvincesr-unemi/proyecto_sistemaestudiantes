import json
import os
from typing import List, Dict, Any

class GestorJSON:
    """Lee y guarda una lista de diccionarios. Es la unica parte que toca el disco."""

    def __init__(self, ruta: str) -> None:
        """
        Inicializa el gestor y asegura que la carpeta de destino exista.

        Args:
            ruta (str): La ruta relativa o absoluta del archivo JSON.

        Returns:
            None
        """
        self.ruta = ruta
        carpeta = os.path.dirname(ruta)
        if carpeta and not os.path.exists(carpeta):
            os.makedirs(carpeta)

    def leer(self) -> List[Dict[str, Any]]:
        """
        Lee el archivo JSON. 
        Devuelve SIEMPRE una lista: vacia si el archivo no existe o esta danado.

        Args:
            Ninguno

        Returns:
            List[Dict[str, Any]]: Lista de diccionarios con los datos leidos.
        """
        if not os.path.exists(self.ruta):
            return []
        try:
            with open(self.ruta, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
            return datos if isinstance(datos, list) else []
        except (json.JSONDecodeError, OSError):
            # Capturamos errores concretos, nunca un "except:" pelado
            return []

    def guardar(self, datos: List[Dict[str, Any]]) -> bool:
        """
        Guarda una lista de diccionarios en el archivo JSON.

        Args:
            datos (List[Dict[str, Any]]): La informacion a guardar (ya convertida a diccionarios).

        Returns:
            bool: True si se guardo correctamente, False en caso de error.
        """
        try:
            with open(self.ruta, "w", encoding="utf-8") as archivo:
                json.dump(datos, archivo, ensure_ascii=False, indent=2)
            return True
        except (TypeError, OSError):
            return False