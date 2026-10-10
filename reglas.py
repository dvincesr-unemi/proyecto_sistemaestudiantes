"""
GUIA DE REGLAS Y BUENAS PRACTICAS DE DISENO ORIENTADO A OBJETOS (POO)
PROYECTO: SISTEMA DE GESTION ACADEMICA (CRUD)

Este archivo contiene las reglas fundamentales de arquitectura, herencia,
polimorfismo y encapsulamiento implementadas en este proyecto.
Cero tildes y cero uso de la decimoquinta letra del abecedario.
"""

from abc import ABC, abstractmethod
from datetime import date
from typing import Dict, Any, List, Optional


# =====================================================================
# REGLA 1: CLASES BASE Y FABRICAS HEREDABLES (SINGLE RESPONSIBILITY)
# =====================================================================
# Regla: La clase raiz debe centralizar atributos y comportamientos
# comunes para evitar duplicacion de codigo en clases hijas.
# Regla: La reconstruccion desde diccionario (deserializacion) debe 
# resolverse una unica vez mediante un metodo de clase (@classmethod)
# que delegue a los constructores via cls(**datos).

class ModeloBase:
    """Clase raiz que define el ciclo de vida e identidad de cada entidad."""

    def __init__(self, id_registro: int) -> None:
        """
        Constructor base. Centraliza el identificador unico.

        Args:
            id_registro (int): Identificador primario de la entidad.
        """
        self.id = int(id_registro)

    @classmethod
    def desde_diccionario(cls, datos: Dict[str, Any]) -> "ModeloBase":
        """
        Patron Factory Method heredable.
        Saca el identificador del diccionario y desempaqueta los atributos
        al constructor correspondiente mediante **kwargs.

        Args:
            datos (Dict[str, Any]): Datos en crudo leidos desde el JSON.

        Returns:
            ModeloBase: Instancia polimorfica de la clase que lo invoco.
        """
        copia = dict(datos)
        id_registro = copia.pop("id")
        return cls(id_registro, **copia)

    def a_diccionario(self) -> Dict[str, Any]:
        """
        Serializacion base. Cada clase hija debe llamar a super().a_diccionario()
        y extender este diccionario.

        Returns:
            Dict[str, Any]: Diccionario con la clave primaria.
        """
        return {"id": self.id}

    def etiqueta(self) -> str:
        """
        Punto de anclaje para polimorfismo. Representacion en cadena simple.

        Returns:
            str: Descripcion basica del registro.
        """
        return f"registro {self.id}"

    def __str__(self) -> str:
        """
        Aprovecha el enlace dinamico en tiempo de ejecucion: delega
        siempre a etiqueta(), logrando que cada subclase se imprima
        distinto sin sobreescribir __str__.

        Returns:
            str: Representacion formal para terminal.
        """
        return f"[{self.id}] {self.etiqueta()}"


# =====================================================================
# REGLA 2: HERENCIA MULTINIVEL Y EXTENSION POLIMORFICA
# =====================================================================
# Regla: Al especializar (Persona -> Estudiante), siempre se debe invocar
# super().__init__(...) para delegar la inicializacion hacia arriba.
# Regla: Al implementar metodos sobrescritos (a_diccionario, etiqueta),
# siempre se debe llamar a super().metodo() para extender en lugar de
# sobrescribir a ciegas (Principio Open/Closed).

class Persona(ModeloBase):
    """Especializacion intermedia: Modela atributos de individuos."""

    def __init__(self, id_registro: int, nombre: str, apellido: str, email: str) -> None:
        super().__init__(id_registro)
        self.nombre = nombre
        self.apellido = apellido
        self.email = email

    def nombre_completo(self) -> str:
        """Devuelve nombres y apellidos concatenados."""
        return f"{self.nombre} {self.apellido}"

    def a_diccionario(self) -> Dict[str, Any]:
        datos = super().a_diccionario()
        datos.update({
            "nombre": self.nombre,
            "apellido": self.apellido,
            "email": self.email
        })
        return datos

    def etiqueta(self) -> str:
        # Polimorfismo nivel 1: Persona reemplaza la etiqueta generica
        return self.nombre_completo()


class Estudiante(Persona):
    """Especializacion final: Estudiante ES UNA Persona."""

    def __init__(
        self, id_registro: int, nombre: str, apellido: str, email: str,
        carnet: str = "", carrera: str = ""
    ) -> None:
        super().__init__(id_registro, nombre, apellido, email)
        self.carnet = carnet
        self.carrera = carrera

    def a_diccionario(self) -> Dict[str, Any]:
        # Extiende el diccionario de Persona (que ya incluye el de ModeloBase)
        datos = super().a_diccionario()
        datos.update({
            "carnet": self.carnet,
            "carrera": self.carrera
        })
        return datos

    def etiqueta(self) -> str:
        # Polimorfismo nivel 2: Extiende la etiqueta del padre (nombre_completo)
        return f"{super().etiqueta()} · {self.carnet or 'sin carnet'} · {self.carrera}"


# =====================================================================
# REGLA 3: ENCAPSULAMIENTO DE REGLAS DE NEGOCIO Y ELEMENTOS ESTATICOS
# =====================================================================
# Regla: Los limites globales del dominio (cupos maximos, notas maximas,
# notas de aprobacion) deben ser constantes de clase (atributos estaticos).
# Regla: Metodos que validan datos puros sin depender del estado del objeto
# deben declararse como @staticmethod para facilitar reutilizacion.
# Regla: Modificaciones de estado interno (cupos) deben realizarse a traves
# de metodos explicitos (ocupar_cupo, liberar_cupo), nunca mutando directamente.

class Materia(ModeloBase):
    """Entidad de dominio curricular con encapsulamiento de negocio."""

    CUPOS_MAXIMOS: int = 30
    NOTA_APROBACION: float = 14.0
    NOTA_MAXIMA: float = 20.0
    NOTA_MINIMA: float = 0.0

    def __init__(
        self, id_registro: int, nombre: str, codigo: str,
        creditos: int = 0, cupos: int = 30
    ) -> None:
        super().__init__(id_registro)
        self.nombre = nombre
        self.codigo = codigo
        self.creditos = int(creditos)
        self.cupos = int(cupos)

    @staticmethod
    def es_nota_valida(valor: Any) -> bool:
        """
        Regla de negocio pura: Determina si una calificacion es computable.
        Valida tipos y rango cerrado [0, 20].

        Args:
            valor (Any): Entrada a evaluar.

        Returns:
            bool: True si la nota es numerica y se ubica entre 0 y 20.
        """
        try:
            nota = float(valor)
            return Materia.NOTA_MINIMA <= nota <= Materia.NOTA_MAXIMA
        except (TypeError, ValueError):
            return False

    def hay_cupo(self) -> bool:
        """Verifica disponibilidad antes de matricular."""
        return self.cupos > 0

    def ocupar_cupo(self) -> bool:
        """Reduce un cupo de forma controlada."""
        if self.hay_cupo():
            self.cupos -= 1
            return True
        return False

    def liberar_cupo(self) -> bool:
        """Devuelve un cupo respetando el limite maximo permitido."""
        if self.cupos < Materia.CUPOS_MAXIMOS:
            self.cupos += 1
            return True
        return False

    def a_diccionario(self) -> Dict[str, Any]:
        datos = super().a_diccionario()
        datos.update({
            "nombre": self.nombre,
            "codigo": self.codigo,
            "creditos": self.creditos,
            "cupos": self.cupos
        })
        return datos

    def etiqueta(self) -> str:
        estado = " ⚠ LLENA" if not self.hay_cupo() else ""
        return f"[{self.codigo}] {self.nombre} · Cupos: {self.cupos}/{Materia.CUPOS_MAXIMOS}{estado}"


# =====================================================================
# REGLA 4: TABLAS TRANSACCIONALES (ENTIDADES PUENTE)
# =====================================================================
# Regla: Las relaciones muchos a muchos se modelan como entidades independientes.
# Regla: Las propiedades derivadas (esta_aprobada, estado) deben calcularse
# dinamicamente a traves de metodos para evitar inconsistencia si la nota cambia.

class Matricula(ModeloBase):
    """Entidad transaccional: Vincula Estudiante y Materia."""

    def __init__(
        self, id_registro: int, estudiante_id: int, materia_id: int,
        periodo: str, nota: float = 0.0, fecha: str = ""
    ) -> None:
        super().__init__(id_registro)
        self.estudiante_id = int(estudiante_id)
        self.materia_id = int(materia_id)
        self.periodo = periodo
        self.nota = float(nota)
        self.fecha = fecha or date.today().isoformat()

    def esta_aprobada(self) -> bool:
        """Calcula aprobacion consumiendo la constante de la clase Materia."""
        return self.nota >= Materia.NOTA_APROBACION

    def estado(self) -> str:
        """Traduce el estado academico a texto legible."""
        return "Aprobada" if self.esta_aprobada() else "Reprobada"

    def a_diccionario(self) -> Dict[str, Any]:
        datos = super().a_diccionario()
        datos.update({
            "estudiante_id": self.estudiante_id,
            "materia_id": self.materia_id,
            "periodo": self.periodo,
            "nota": self.nota,
            "fecha": self.fecha
        })
        return datos

    def etiqueta(self) -> str:
        return (f"{self.fecha} · Alumno {self.estudiante_id} · "
                f"Materia {self.materia_id} ({self.periodo}) · "
                f"Nota: {self.nota} [{self.estado()}]")


# =====================================================================
# REGLA 5: ABSTRACCION EN CONTROLADORES Y POLIMORFISMO DE CONSUMO
# =====================================================================
# Regla: Usar clases base abstractas (ABC) para definir contratos obligatorios.
# Regla: El modulo visual (main.py) debe consumir objetos de forma polimorfica:
# una sola funcion de renderizado (mostrar_lista) debe imprimir cualquier
# modelo gracias al metodo __str__ heredado de ModeloBase.

class CrudBase(ABC):
    """Contrato abstracto para garantizar consistencia en la capa controladora."""

    @abstractmethod
    def leer(self) -> List[Any]:
        pass

    @abstractmethod
    def obtener(self, id_registro: int) -> Optional[Any]:
        pass

    @abstractmethod
    def crear(self, datos: Dict[str, Any]) -> tuple[bool, str]:
        pass

    @abstractmethod
    def eliminar(self, id_registro: int) -> tuple[bool, str]:
        pass


# =====================================================================
# DEMOSTRACION Y VERIFICACION DE REGLAS (TEST RUNNER)
# =====================================================================
if __name__ == "__main__":
    print("--- 1. VERIFICACION DE POLIMORFISMO EN IMPRESION ---")
    est = Estudiante(1, "Carlos", "Perez", "carlos@demo.com", "EST2026", "Software")
    mat = Materia(10, "Calculo Integral", "MAT101", 4, 30)
    ins = Matricula(100, est.id, mat.id, "2026-1", nota=15.5)

    # Una lista heterogenea tratada de forma polimorfica
    registros: List[ModeloBase] = [est, mat, ins]
    for r in registros:
        # Se invoca __str__ que a su vez llama al metodo polimorfico etiqueta()
        print(r)

    print("\n--- 2. VERIFICACION DE REGLAS ESTATICAS EN MATERIA ---")
    print(f"Es nota 25 valida?: {Materia.es_nota_valida(25)}")      # False (> 20)
    print(f"Es nota -2 valida?: {Materia.es_nota_valida(-2)}")      # False (< 0)
    print(f"Es nota 18 valida?: {Materia.es_nota_valida(18)}")      # True
    print(f"Es nota 'abc' valida?: {Materia.es_nota_valida('abc')}") # False

    print("\n--- 3. CONTROL DE CUPOS Y TRANSACCIONES ---")
    print(f"Cupos iniciales de {mat.codigo}: {mat.cupos}")
    mat.ocupar_cupo()
    print(f"Cupo tras inscripcion: {mat.cupos}")
    mat.liberar_cupo()
    print(f"Cupo tras anulacion: {mat.cupos}")

    print("\n--- 4. DESERIALIZACION AUTOMATICA (FACTORY METHOD) ---")
    datos_crudos = {
        "id": 2,
        "nombre": "Elena",
        "apellido": "Rios",
        "email": "elena@demo.com",
        "carnet": "EST2027",
        "carrera": "Redes"
    }
    # La clase hija aprovecha la fabrica del padre sin reescribir codigo
    est2 = Estudiante.desde_diccionario(datos_crudos)
    print(f"Objeto reconstruido desde dict: {est2}")

    """
SISTEMA DE GESTION ACADEMICA UNIVERSITARIA
Implementacion unificada en un solo archivo.
Arquitectura: MVC + POO (Herencia, Polimorfismo, Encapsulamiento, Abstraccion).
"""

import os
import json
from abc import ABC, abstractmethod
from datetime import date
from typing import List, Dict, Any, Optional, Tuple


# =====================================================================
# SECCION 1: UTILIDADES DE CONSOLA Y VALIDACION (HERRAMIENTAS)
# =====================================================================

COLORES: Dict[str, str] = {
    "ROJO": "\033[91m",
    "VERDE": "\033[92m",
    "AZUL": "\033[94m",
    "AMARILLO": "\033[93m",
    "CYAN": "\033[96m",
    "BLANCO": "\033[97m",
    "RESET": "\033[0m",
}

RESPUESTAS_SI: Tuple[str, ...] = ("si", "s", "yes", "y")


def limpiar_pantalla() -> None:
    """Limpia la terminal segun el sistema operativo."""
    os.system("clear" if os.name == "posix" else "cls")


def imprimir_color(texto: str, color: str) -> None:
    """Imprime texto con secuencias de escape ANSI."""
    codigo = COLORES.get(color, COLORES["BLANCO"])
    print(f"{codigo}{texto}{COLORES['RESET']}")


def imprimir_titulo(texto: str) -> None:
    """Limpia pantalla y dibuja un encabezado delimitado."""
    limpiar_pantalla()
    imprimir_color("=" * 65, "AZUL")
    print(f"  {texto}".center(65))
    imprimir_color("=" * 65, "AZUL")
    print()


def imprimir_exito(mensaje: str) -> None:
    """Muestra un mensaje afirmativo en verde."""
    imprimir_color(f"[OK] {mensaje}", "VERDE")


def imprimir_error(mensaje: str) -> None:
    """Muestra un mensaje de fallo en rojo."""
    imprimir_color(f"[ERROR] {mensaje}", "ROJO")


def imprimir_info(mensaje: str) -> None:
    """Muestra un mensaje informativo en celeste."""
    imprimir_color(f"[INFO] {mensaje}", "CYAN")


def confirmar(pregunta: str) -> bool:
    """Solicita confirmacion al usuario mediante respuestas predefinidas."""
    respuesta = input(f"{pregunta} (si/no): ").strip().lower()
    return respuesta in RESPUESTAS_SI


def es_email_valido(texto: str) -> bool:
    """Valida formato estructural de un correo electronico."""
    texto = texto.strip()
    if texto.count("@") != 1:
        return False
    usuario, dominio = texto.split("@")
    return len(usuario) > 0 and "." in dominio and not dominio.endswith(".")


# =====================================================================
# SECCION 2: PERSISTENCIA DE DATOS (GESTOR JSON)
# =====================================================================

class GestorJSON:
    """Maneja lectura y escritura de colecciones de diccionarios en disco."""

    def __init__(self, ruta: str) -> None:
        """
        Inicializa el gestor y asegura el directorio contenedor.

        Args:
            ruta (str): Ruta relativa o absoluta del archivo.
        """
        self.ruta = ruta
        carpeta = os.path.dirname(ruta)
        if carpeta and not os.path.exists(carpeta):
            os.makedirs(carpeta, exist_ok=True)

    def leer(self) -> List[Dict[str, Any]]:
        """
        Lee el archivo JSON y retorna una lista de diccionarios.

        Returns:
            List[Dict[str, Any]]: Datos cargados o lista vacia en caso de error.
        """
        if not os.path.exists(self.ruta):
            return []
        try:
            with open(self.ruta, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
            return datos if isinstance(datos, list) else []
        except (json.JSONDecodeError, OSError):
            return []

    def guardar(self, datos: List[Dict[str, Any]]) -> bool:
        """
        Serializa y guarda la lista de diccionarios en el disco.

        Args:
            datos (List[Dict[str, Any]]): Coleccion a guardar.

        Returns:
            bool: True si la operacion fue exitosa, False en caso de fallo.
        """
        try:
            with open(self.ruta, "w", encoding="utf-8") as archivo:
                json.dump(datos, archivo, ensure_ascii=False, indent=2)
            return True
        except (TypeError, OSError):
            return False


# =====================================================================
# SECCION 3: MODELOS DE DOMINIO Y REGLAS DE NEGOCIO (MODELS)
# =====================================================================

class ModeloBase:
    """Clase raiz que centraliza el identificador unico y metodos comunes."""

    def __init__(self, id_registro: int) -> None:
        """
        Inicializa la entidad base con su clave primaria.

        Args:
            id_registro (int): Identificador numerico del registro.
        """
        self.id = int(id_registro)

    @classmethod
    def desde_diccionario(cls, datos: Dict[str, Any]) -> "ModeloBase":
        """
        Fabrica polimorfica para instanciar cualquier modelo hijo.

        Args:
            datos (Dict[str, Any]): Diccionario extraido del JSON.

        Returns:
            ModeloBase: Instancia de la clase que invoco el metodo.
        """
        copia = dict(datos)
        id_registro = copia.pop("id")
        return cls(id_registro, **copia)

    def a_diccionario(self) -> Dict[str, Any]:
        """
        Serializa atributos base de la entidad a un diccionario.

        Returns:
            Dict[str, Any]: Diccionario con la clave primaria.
        """
        return {"id": self.id}

    def etiqueta(self) -> str:
        """
        Representacion polimorfica en texto legible.

        Returns:
            str: Descripcion generica de la entidad.
        """
        return f"registro {self.id}"

    def __str__(self) -> str:
        """Delega la impresion en consola al metodo polimorfico etiqueta()."""
        return f"[{self.id}] {self.etiqueta()}"


class Persona(ModeloBase):
    """Especializacion de ModeloBase para entidades humanas."""

    def __init__(self, id_registro: int, nombre: str, apellido: str, email: str) -> None:
        super().__init__(id_registro)
        self.nombre = nombre
        self.apellido = apellido
        self.email = email

    def nombre_completo(self) -> str:
        """Retorna nombre y apellido unidos."""
        return f"{self.nombre} {self.apellido}"

    def a_diccionario(self) -> Dict[str, Any]:
        datos = super().a_diccionario()
        datos.update({
            "nombre": self.nombre,
            "apellido": self.apellido,
            "email": self.email
        })
        return datos

    def etiqueta(self) -> str:
        return self.nombre_completo()


class Estudiante(Persona):
    """Estudiante ES UNA Persona, con carnet y carrera universitaria."""

    def __init__(
        self, id_registro: int, nombre: str, apellido: str, email: str,
        carnet: str = "", carrera: str = ""
    ) -> None:
        super().__init__(id_registro, nombre, apellido, email)
        self.carnet = carnet
        self.carrera = carrera

    def a_diccionario(self) -> Dict[str, Any]:
        datos = super().a_diccionario()
        datos.update({
            "carnet": self.carnet,
            "carrera": self.carrera
        })
        return datos

    def etiqueta(self) -> str:
        return f"{super().etiqueta()} · {self.carnet or 'sin carnet'} · {self.carrera}"


class Docente(Persona):
    """Demuestra reusabilidad de Persona: Docente con titulo y departamento."""

    def __init__(
        self, id_registro: int, nombre: str, apellido: str, email: str,
        titulo: str = "", departamento: str = ""
    ) -> None:
        super().__init__(id_registro, nombre, apellido, email)
        self.titulo = titulo
        self.departamento = departamento

    def a_diccionario(self) -> Dict[str, Any]:
        datos = super().a_diccionario()
        datos.update({
            "titulo": self.titulo,
            "departamento": self.departamento
        })
        return datos

    def etiqueta(self) -> str:
        return f"Prof. {super().etiqueta()} · {self.titulo} · Depto: {self.departamento}"


class Materia(ModeloBase):
    """Entidad academica con reglas estaticas y control de plazas."""

    CUPOS_MAXIMOS: int = 30
    NOTA_APROBACION: float = 14.0
    NOTA_MAXIMA: float = 20.0
    NOTA_MINIMA: float = 0.0

    def __init__(
        self, id_registro: int, nombre: str, codigo: str,
        creditos: int = 0, cupos: int = 30
    ) -> None:
        super().__init__(id_registro)
        self.nombre = nombre
        self.codigo = codigo
        self.creditos = int(creditos)
        self.cupos = int(cupos)

    @staticmethod
    def es_nota_valida(valor: Any) -> bool:
        """Valida que una calificacion sea numerica y este dentro del rango [0, 20]."""
        try:
            nota = float(valor)
            return Materia.NOTA_MINIMA <= nota <= Materia.NOTA_MAXIMA
        except (TypeError, ValueError):
            return False

    def hay_cupo(self) -> bool:
        """Verifica existencia de cupos disponibles."""
        return self.cupos > 0

    def ocupar_cupo(self) -> bool:
        """Disminuye una plaza si hay disponibilidad."""
        if self.hay_cupo():
            self.cupos -= 1
            return True
        return False

    def liberar_cupo(self) -> bool:
        """Incrementa una plaza sin exceder el tope maximo."""
        if self.cupos < Materia.CUPOS_MAXIMOS:
            self.cupos += 1
            return True
        return False

    def a_diccionario(self) -> Dict[str, Any]:
        datos = super().a_diccionario()
        datos.update({
            "nombre": self.nombre,
            "codigo": self.codigo,
            "creditos": self.creditos,
            "cupos": self.cupos
        })
        return datos

    def etiqueta(self) -> str:
        alerta = " [LLENA]" if not self.hay_cupo() else ""
        return f"[{self.codigo}] {self.nombre} ({self.creditos} Cr) · cupos: {self.cupos}/{Materia.CUPOS_MAXIMOS}{alerta}"


class Matricula(ModeloBase):
    """Entidad puente: relaciona Estudiante con Materia en un ciclo."""

    def __init__(
        self, id_registro: int, estudiante_id: int, materia_id: int,
        periodo: str, nota: float = 0.0, fecha: str = ""
    ) -> None:
        super().__init__(id_registro)
        self.estudiante_id = int(estudiante_id)
        self.materia_id = int(materia_id)
        self.periodo = periodo
        self.fecha = fecha or date.today().isoformat()
        self._nota = 0.0
        self.nota = nota  # Invoca el setter para validacion defensiva

    @property
    def nota(self) -> float:
        """Getter de la calificacion."""
        return self._nota

    @nota.setter
    def nota(self, valor: Any) -> None:
        """Setter con validacion contra la regla de negocio de Materia."""
        if not Materia.es_nota_valida(valor):
            raise ValueError(f"Nota invalida: '{valor}'. Debe ser numerica entre 0 y 20.")
        self._nota = round(float(valor), 2)

    def esta_aprobada(self) -> bool:
        """Evalua si la nota supera o iguala la constante de aprobacion."""
        return self.nota >= Materia.NOTA_APROBACION

    def estado(self) -> str:
        """Determina condicion academica en texto."""
        return "Aprobada" if self.esta_aprobada() else "Reprobada"

    def a_diccionario(self) -> Dict[str, Any]:
        datos = super().a_diccionario()
        datos.update({
            "estudiante_id": self.estudiante_id,
            "materia_id": self.materia_id,
            "periodo": self.periodo,
            "nota": self.nota,
            "fecha": self.fecha
        })
        return datos

    def etiqueta(self) -> str:
        return (f"{self.fecha} · Estudiante ID: {self.estudiante_id} · "
                f"Materia ID: {self.materia_id} ({self.periodo}) · "
                f"Nota: {self.nota} [{self.estado()}]")


# =====================================================================
# SECCION 4: CONTROLADORES DE NEGOCIO (VIEWS / CONTROLLERS)
# =====================================================================

class CrudBase(ABC):
    """Contrato base obligatorio para todos los controladores."""

    @abstractmethod
    def leer(self) -> List[Any]:
        pass

    @abstractmethod
    def obtener(self, id_registro: int) -> Optional[Any]:
        pass

    @abstractmethod
    def buscar(self, texto: str) -> List[Any]:
        pass

    @abstractmethod
    def siguiente(self) -> int:
        pass

    @abstractmethod
    def crear(self, datos: Dict[str, Any]) -> Tuple[bool, str]:
        pass

    @abstractmethod
    def actualizar(self, id_registro: int, datos: Dict[str, Any]) -> Tuple[bool, str]:
        pass

    @abstractmethod
    def eliminar(self, id_registro: int) -> Tuple[bool, str]:
        pass


class EstudianteController(CrudBase):
    """Controlador para el catalogo de estudiantes."""

    def __init__(self, archivo: str = "datos/estudiantes.json") -> None:
        self.gestor = GestorJSON(archivo)
        self.lista: List[Estudiante] = []
        for datos in self.gestor.leer():
            self.lista.append(Estudiante.desde_diccionario(datos))

    def guardar(self) -> None:
        self.gestor.guardar([e.a_diccionario() for e in self.lista])

    def validar(self, datos: Dict[str, Any], id_actual: Optional[int] = None) -> Optional[str]:
        if id_actual is None:
            for campo in ("nombre", "apellido", "email"):
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio."

        if "email" in datos:
            email = str(datos["email"]).strip().lower()
            if not es_email_valido(email):
                return f"Email invalido: '{email}'."
            emails_usados = {e.email for e in self.lista if e.id != id_actual}
            if email in emails_usados:
                return "Ese email ya pertenece a otro estudiante."

        if "carnet" in datos and str(datos["carnet"]).strip():
            carnet = str(datos["carnet"]).strip().upper()
            carnets_usados = {e.carnet for e in self.lista if e.id != id_actual and e.carnet}
            if carnet in carnets_usados:
                return "Ese carnet ya esta registrado para otro estudiante."

        return None

    def leer(self) -> List[Estudiante]:
        return self.lista

    def obtener(self, id_registro: int) -> Optional[Estudiante]:
        for est in self.lista:
            if est.id == id_registro:
                return est
        return None

    def buscar(self, texto: str) -> List[Estudiante]:
        texto = texto.strip().lower()
        if not texto:
            return []
        encontrados = []
        for e in self.lista:
            if (texto in e.nombre.lower() or texto in e.apellido.lower()
                    or texto in e.email.lower() or texto in e.carnet.lower()
                    or texto in e.carrera.lower()):
                encontrados.append(e)
        return encontrados

    def siguiente(self) -> int:
        return max([e.id for e in self.lista], default=0) + 1

    def crear(self, datos: Dict[str, Any]) -> Tuple[bool, str]:
        error = self.validar(datos)
        if error:
            return False, error

        nuevo = Estudiante(
            self.siguiente(),
            str(datos["nombre"]).strip().title(),
            str(datos["apellido"]).strip().title(),
            str(datos["email"]).strip().lower(),
            str(datos.get("carnet", "")).strip().upper(),
            str(datos.get("carrera", "")).strip().title()
        )
        self.lista.append(nuevo)
        self.guardar()
        return True, f"Estudiante creado: {nuevo.etiqueta()}"

    def actualizar(self, id_registro: int, datos: Dict[str, Any]) -> Tuple[bool, str]:
        est = self.obtener(id_registro)
        if est is None:
            return False, f"No existe un estudiante con id {id_registro}."
        if not datos:
            return False, "No se indicaron cambios para procesar."

        permitidos = {"nombre", "apellido", "email", "carnet", "carrera"}
        desconocidos = set(datos) - permitidos
        if desconocidos:
            return False, f"Campos no validos: {', '.join(sorted(desconocidos))}."

        error = self.validar(datos, id_registro)
        if error:
            return False, error

        for campo, valor in datos.items():
            valor = str(valor).strip()
            if campo in ("nombre", "apellido", "carrera"):
                valor = valor.title()
            elif campo == "email":
                valor = valor.lower()
            elif campo == "carnet":
                valor = valor.upper()
            setattr(est, campo, valor)

        self.guardar()
        return True, f"Estudiante {id_registro} actualizado."

    def eliminar(self, id_registro: int) -> Tuple[bool, str]:
        est = self.obtener(id_registro)
        if est is None:
            return False, f"No existe un estudiante con id {id_registro}."
        self.lista.remove(est)
        self.guardar()
        return True, f"Estudiante {id_registro} eliminado."

    def carreras_registradas(self) -> List[str]:
        """Conjunto unico de carreras registradas."""
        return sorted({e.carrera for e in self.lista if e.carrera})


class MateriaController(CrudBase):
    """Controlador para la oferta de asignaturas academicas."""

    def __init__(self, archivo: str = "datos/materias.json") -> None:
        self.gestor = GestorJSON(archivo)
        self.lista: List[Materia] = []
        for datos in self.gestor.leer():
            self.lista.append(Materia.desde_diccionario(datos))

    def guardar(self) -> None:
        self.gestor.guardar([m.a_diccionario() for m in self.lista])

    def validar(self, datos: Dict[str, Any], id_actual: Optional[int] = None) -> Optional[str]:
        if id_actual is None:
            for campo in ("nombre", "codigo"):
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio."

        creditos = str(datos.get("creditos", "")).strip()
        if creditos != "" and not creditos.isdigit():
            return "Los creditos deben ser un numero entero no negativo."

        cupos = str(datos.get("cupos", "")).strip()
        if cupos != "" and not cupos.isdigit():
            return "Los cupos deben ser un numero entero positivo."

        if "codigo" in datos:
            codigo = str(datos["codigo"]).strip().upper()
            codigos_usados = {m.codigo for m in self.lista if m.id != id_actual}
            if codigo in codigos_usados:
                return f"Ya existe una materia con el codigo '{codigo}'."

        return None

    def leer(self) -> List[Materia]:
        return self.lista

    def obtener(self, id_registro: int) -> Optional[Materia]:
        for mat in self.lista:
            if mat.id == id_registro:
                return mat
        return None

    def buscar(self, texto: str) -> List[Materia]:
        texto = texto.strip().lower()
        if not texto:
            return []
        return [m for m in self.lista if texto in m.nombre.lower() or texto in m.codigo.lower()]

    def siguiente(self) -> int:
        return max([m.id for m in self.lista], default=0) + 1

    def crear(self, datos: Dict[str, Any]) -> Tuple[bool, str]:
        error = self.validar(datos)
        if error:
            return False, error

        creditos_raw = str(datos.get("creditos", "")).strip()
        cupos_raw = str(datos.get("cupos", "")).strip()

        nueva = Materia(
            self.siguiente(),
            str(datos["nombre"]).strip().title(),
            str(datos["codigo"]).strip().upper(),
            int(creditos_raw) if creditos_raw else 0,
            int(cupos_raw) if cupos_raw else Materia.CUPOS_MAXIMOS
        )
        self.lista.append(nueva)
        self.guardar()
        return True, f"Materia creada: {nueva.etiqueta()}"

    def actualizar(self, id_registro: int, datos: Dict[str, Any]) -> Tuple[bool, str]:
        mat = self.obtener(id_registro)
        if mat is None:
            return False, f"No existe la materia con id {id_registro}."
        if not datos:
            return False, "No se indicaron cambios."

        desconocidos = set(datos) - {"nombre", "codigo", "creditos", "cupos"}
        if desconocidos:
            return False, f"Campos invalidos: {', '.join(sorted(desconocidos))}."

        error = self.validar(datos, id_registro)
        if error:
            return False, error

        if "nombre" in datos:
            mat.nombre = str(datos["nombre"]).strip().title()
        if "codigo" in datos:
            mat.codigo = str(datos["codigo"]).strip().upper()
        if "creditos" in datos:
            mat.creditos = int(datos["creditos"])
        if "cupos" in datos:
            mat.cupos = int(datos["cupos"])

        self.guardar()
        return True, f"Materia {id_registro} actualizada."

    def eliminar(self, id_registro: int) -> Tuple[bool, str]:
        mat = self.obtener(id_registro)
        if mat is None:
            return False, f"No existe la materia con id {id_registro}."
        self.lista.remove(mat)
        self.guardar()
        return True, f"Materia {id_registro} eliminada."


class MatriculaController(CrudBase):
    """Controlador transaccional con reglas academicas integradas."""

    LIMITE_CREDITOS_PERIODO: int = 15

    def __init__(
        self, estudiantes: EstudianteController, materias: MateriaController,
        archivo: str = "datos/matriculas.json"
    ) -> None:
        self.estudiantes = estudiantes
        self.materias = materias
        self.gestor = GestorJSON(archivo)
        self.lista: List[Matricula] = []
        for datos in self.gestor.leer():
            self.lista.append(Matricula.desde_diccionario(datos))

    def guardar(self) -> None:
        self.gestor.guardar([m.a_diccionario() for m in self.lista])

    def validar_reglas(self, estudiante_id: int, materia_id: int, periodo: str) -> Tuple[bool, str]:
        """Verifica existencia, cupos, doble matricula y carga maxima de creditos."""
        estudiante = self.estudiantes.obtener(estudiante_id)
        if estudiante is None:
            return False, f"No existe el estudiante con id {estudiante_id}."

        materia = self.materias.obtener(materia_id)
        if materia is None:
            return False, f"No existe la materia con id {materia_id}."

        if not materia.hay_cupo():
            return False, f"La materia [{materia.codigo}] ya no tiene plazas disponibles."

        # Regla 1: Bloqueo de duplicados en el mismo ciclo
        matriculas_ciclo = [
            m for m in self.lista
            if m.estudiante_id == estudiante_id and m.periodo.upper() == periodo.upper()
        ]
        for m in matriculas_ciclo:
            if m.materia_id == materia_id:
                return False, f"El estudiante ya cursa la materia [{materia.codigo}] en el periodo {periodo}."

        # Regla 2: Limite maximo de creditos en el ciclo
        creditos_actuales = 0
        for m in matriculas_ciclo:
            mat_cursando = self.materias.obtener(m.materia_id)
            if mat_cursando:
                creditos_actuales += mat_cursando.creditos

        if (creditos_actuales + materia.creditos) > self.LIMITE_CREDITOS_PERIODO:
            return False, (
                f"Limite de carga horaria excedido: tiene {creditos_actuales} creditos cursando, "
                f"sumaria {creditos_actuales + materia.creditos} "
                f"(maximo permitido: {self.LIMITE_CREDITOS_PERIODO})."
            )

        return True, "Validacion correcta."

    def leer(self) -> List[Matricula]:
        return self.lista

    def obtener(self, id_registro: int) -> Optional[Matricula]:
        for mat in self.lista:
            if mat.id == id_registro:
                return mat
        return None

    def buscar(self, texto: str) -> List[Matricula]:
        texto = texto.strip().lower()
        if not texto:
            return []
        return [m for m in self.lista if texto in m.periodo.lower() or texto in m.fecha]

    def siguiente(self) -> int:
        return max([m.id for m in self.lista], default=0) + 1

    def crear(self, datos: Dict[str, Any]) -> Tuple[bool, str]:
        try:
            estudiante_id = int(datos.get("estudiante_id", 0))
            materia_id = int(datos.get("materia_id", 0))
        except (TypeError, ValueError):
            return False, "estudiante_id y materia_id deben ser numeros enteros."

        periodo = str(datos.get("periodo", "Actual")).strip().upper()
        es_valido, mensaje = self.validar_reglas(estudiante_id, materia_id, periodo)
        if not es_valido:
            return False, mensaje

        materia = self.materias.obtener(materia_id)
        assert materia is not None

        # Reduccion de plaza mediante metodo del modelo
        materia.ocupar_cupo()
        self.materias.guardar()

        nueva_matricula = Matricula(
            self.siguiente(),
            estudiante_id,
            materia_id,
            periodo,
            nota=0.0
        )
        self.lista.append(nueva_matricula)
        self.guardar()
        return True, f"Inscripcion registrada exitosamente. Plazas restantes: {materia.cupos}."

    def actualizar(self, id_registro: int, datos: Dict[str, Any]) -> Tuple[bool, str]:
        matricula = self.obtener(id_registro)
        if matricula is None:
            return False, f"No existe la matricula con id {id_registro}."

        if "nota" not in datos:
            return False, "Solo se permite asentar la nota de una inscripcion."

        try:
            matricula.nota = datos["nota"]  # Activa el setter con validacion defensiva
            self.guardar()
            return True, f"Calificacion guardada. Estado academico: [{matricula.estado()}]."
        except ValueError as err:
            return False, str(err)

    def eliminar(self, id_registro: int) -> Tuple[bool, str]:
        matricula = self.obtener(id_registro)
        if matricula is None:
            return False, f"No existe la matricula con id {id_registro}."

        # Devolucion automatica del cupo al catalogo de materias
        materia = self.materias.obtener(matricula.materia_id)
        if materia is not None:
            materia.liberar_cupo()
            self.materias.guardar()

        self.lista.remove(matricula)
        self.guardar()
        return True, f"Matricula {id_registro} anulada y plaza liberada."

    def calcular_promedio(self, estudiante_id: int) -> float:
        """Calcula el promedio general ponderado por los creditos de cada asignatura."""
        inscripciones = [m for m in self.lista if m.estudiante_id == estudiante_id]
        if not inscripciones:
            return 0.0

        suma_ponderada = 0.0
        total_creditos = 0
        for ins in inscripciones:
            mat = self.materias.obtener(ins.materia_id)
            peso = mat.creditos if mat and mat.creditos > 0 else 1
            suma_ponderada += (ins.nota * peso)
            total_creditos += peso

        return round(suma_ponderada / total_creditos, 2) if total_creditos > 0 else 0.0

    def reporte_academico(self, estudiante_id: int) -> Optional[str]:
        """Genera el boletin completo de notas y estado por estudiante."""
        estudiante = self.estudiantes.obtener(estudiante_id)
        if estudiante is None:
            return None

        linea = "-" * 60
        texto = f"{linea}\n"
        texto += f"BOLETIN ACADEMICO: {estudiante.nombre_completo()}\n"
        texto += f"Carnet: {estudiante.carnet or 'Sin carnet'} | Carrera: {estudiante.carrera}\n"
        texto += f"{linea}\n"

        inscripciones = [m for m in self.lista if m.estudiante_id == estudiante_id]
        if not inscripciones:
            texto += "El estudiante no registra asignaturas cursadas.\n"
        else:
            for ins in inscripciones:
                mat = self.materias.obtener(ins.materia_id)
                nombre_mat = mat.nombre if mat else "Asignatura eliminada"
                cred = mat.creditos if mat else 0
                texto += f"[{ins.periodo}] {nombre_mat} ({cred} Cr) -> Nota: {ins.nota} [{ins.estado()}]\n"

            prom = self.calcular_promedio(estudiante_id)
            texto += f"{linea}\n"
            texto += f"PROMEDIO PONDERADO ACUMULADO: {prom:.2f} / 20.00\n"

        texto += linea
        return texto


# =====================================================================
# SECCION 5: VISTA DE CONSOLA E INTERFAZ INTERACTIVA (MAIN / CLI)
# =====================================================================

estudiantes_ctrl = EstudianteController()
materias_ctrl = MateriaController()
matriculas_ctrl = MatriculaController(estudiantes_ctrl, materias_ctrl)


def pausa() -> None:
    input("\nPresione Enter para continuar...")


def pedir_entero(etiqueta: str) -> Optional[int]:
    try:
        return int(input(etiqueta))
    except ValueError:
        return None


def mostrar_resultado(exito: bool, mensaje: str) -> None:
    if exito:
        imprimir_exito(mensaje)
    else:
        imprimir_error(mensaje)


def mostrar_lista(objetos: List[Any], vacio: str = "No existen registros registrados.") -> None:
    """Muestra polimorficamente cualquier lista de entidades."""
    if not objetos:
        imprimir_info(vacio)
        return
    for obj in objetos:
        print(f"  {obj}")
    imprimir_info(f"Total registros: {len(objetos)}")


def mostrar_detalle(objeto: ModeloBase) -> None:
    for clave, valor in objeto.a_diccionario().items():
        print(f"  {str(clave).replace('_', ' ').capitalize():<18}: {valor}")


# --- SUBMENU: ESTUDIANTES ---

def crear_estudiante() -> None:
    imprimir_titulo("CREAR ESTUDIANTE")
    datos = {
        "nombre": input("Nombre: "),
        "apellido": input("Apellido: "),
        "email": input("Email: "),
        "carnet": input("Carnet universitario: "),
        "carrera": input("Carrera: "),
    }
    mostrar_resultado(*estudiantes_ctrl.crear(datos))
    pausa()


def listar_estudiantes() -> None:
    imprimir_titulo("LISTADO DE ESTUDIANTES")
    mostrar_lista(estudiantes_ctrl.leer(), "No existen estudiantes registrados todavia.")
    pausa()


def buscar_estudiante() -> None:
    imprimir_titulo("BUSCAR ESTUDIANTE")
    termino = input("Termino de busqueda (nombre, apellido, email, carnet o carrera): ")
    encontrados = estudiantes_ctrl.buscar(termino)
    mostrar_lista(encontrados, f"Ningun estudiante coincide con '{termino}'.")
    pausa()


def ver_estudiante() -> None:
    imprimir_titulo("VER ESTUDIANTE POR ID")
    ide = pedir_entero("ID del estudiante: ")
    if ide is None:
        imprimir_error("ID invalido.")
    else:
        est = estudiantes_ctrl.obtener(ide)
        if est is None:
            imprimir_error("Estudiante no encontrado.")
        else:
            mostrar_detalle(est)
    pausa()


def actualizar_estudiante() -> None:
    imprimir_titulo("ACTUALIZAR ESTUDIANTE")
    ide = pedir_entero("ID del estudiante: ")
    if ide is None:
        imprimir_error("ID invalido.")
        return pausa()

    est = estudiantes_ctrl.obtener(ide)
    if est is None:
        imprimir_error("Estudiante no encontrado.")
        return pausa()

    imprimir_info(f"Editando: {est.etiqueta()}")
    print("Deje en blanco los campos que no desee modificar.\n")

    cambios = {}
    for campo in ("nombre", "apellido", "email", "carnet", "carrera"):
        actual = getattr(est, campo)
        nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
        if nuevo:
            cambios[campo] = nuevo

    mostrar_resultado(*estudiantes_ctrl.actualizar(ide, cambios))
    pausa()


def eliminar_estudiante() -> None:
    imprimir_titulo("ELIMINAR ESTUDIANTE")
    ide = pedir_entero("ID del estudiante a eliminar: ")
    if ide is None:
        imprimir_error("ID invalido.")
        return pausa()

    est = estudiantes_ctrl.obtener(ide)
    if est is None:
        imprimir_error("Estudiante no encontrado.")
        return pausa()

    # Integridad referencial: bloqueo defensivo si existen matriculas
    tiene_matriculas = any(m.estudiante_id == ide for m in matriculas_ctrl.leer())
    if tiene_matriculas:
        imprimir_error("Operacion rechazada: El estudiante posee registros de matricula activos.")
        return pausa()

    imprimir_info(f"Se eliminara: {est.etiqueta()}")
    if confirmar("Confirma la eliminacion definitiva?"):
        mostrar_resultado(*estudiantes_ctrl.eliminar(ide))
    else:
        imprimir_info("Operacion cancelada por el usuario.")
    pausa()


# --- SUBMENU: MATERIAS ---

def crear_materia() -> None:
    imprimir_titulo("CREAR ASIGNATURA")
    datos = {
        "nombre": input("Nombre de la asignatura: "),
        "codigo": input("Codigo institucional: "),
        "creditos": input("Creditos academicos: "),
        "cupos": input("Cupos iniciales [Enter = 30]: "),
    }
    mostrar_resultado(*materias_ctrl.crear(datos))
    pausa()


def listar_materias() -> None:
    imprimir_titulo("LISTADO DE MATERIAS")
    mostrar_lista(materias_ctrl.leer(), "No existen materias registradas todavia.")
    pausa()


def buscar_materia() -> None:
    imprimir_titulo("BUSCAR MATERIA")
    termino = input("Termino de busqueda (nombre o codigo): ")
    mostrar_lista(materias_ctrl.buscar(termino), "Sin coincidencias encontradas.")
    pausa()


def ver_materia() -> None:
    imprimir_titulo("VER MATERIA POR ID")
    ide = pedir_entero("ID de la materia: ")
    if ide is None:
        imprimir_error("ID invalido.")
    else:
        mat = materias_ctrl.obtener(ide)
        if mat is None:
            imprimir_error("Materia no encontrada.")
        else:
            mostrar_detalle(mat)
    pausa()


def actualizar_materia() -> None:
    imprimir_titulo("ACTUALIZAR MATERIA")
    ide = pedir_entero("ID de la materia: ")
    if ide is None:
        imprimir_error("ID invalido.")
        return pausa()

    mat = materias_ctrl.obtener(ide)
    if mat is None:
        imprimir_error("Materia no encontrada.")
        return pausa()

    imprimir_info(f"Editando: {mat.etiqueta()}")
    print("Deje en blanco los campos que no desee modificar.\n")

    cambios = {}
    for campo in ("nombre", "codigo", "creditos", "cupos"):
        actual = getattr(mat, campo)
        nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
        if nuevo:
            cambios[campo] = nuevo

    mostrar_resultado(*materias_ctrl.actualizar(ide, cambios))
    pausa()


def eliminar_materia() -> None:
    imprimir_titulo("ELIMINAR MATERIA")
    ide = pedir_entero("ID de la materia a eliminar: ")
    if ide is None:
        imprimir_error("ID invalido.")
        return pausa()

    mat = materias_ctrl.obtener(ide)
    if mat is None:
        imprimir_error("Materia no encontrada.")
        return pausa()

    # Integridad referencial
    tiene_alumnos = any(m.materia_id == ide for m in matriculas_ctrl.leer())
    if tiene_alumnos:
        imprimir_error("Operacion rechazada: Existen estudiantes matriculados en esta asignatura.")
        return pausa()

    imprimir_info(f"Se eliminara: {mat.etiqueta()}")
    if confirmar("Confirma la eliminacion definitiva?"):
        mostrar_resultado(*materias_ctrl.eliminar(ide))
    else:
        imprimir_info("Operacion cancelada por el usuario.")
    pausa()


# --- SUBMENU: MATRICULAS ---

def registrar_matricula() -> None:
    imprimir_titulo("REGISTRAR MATRICULA ACADEMICA")
    imprimir_info("Estudiantes disponibles:")
    mostrar_lista(estudiantes_ctrl.leer())
    print()
    imprimir_info("Materias con oferta:")
    mostrar_lista(materias_ctrl.leer())
    print()

    est_id = pedir_entero("ID del estudiante: ")
    mat_id = pedir_entero("ID de la materia: ")
    if est_id is None or mat_id is None:
        imprimir_error("Los identificadores deben ser numeros enteros.")
        return pausa()

    periodo = input("Periodo lectivo (ej. 2026-1): ").strip()
    datos = {
        "estudiante_id": est_id,
        "materia_id": mat_id,
        "periodo": periodo
    }
    mostrar_resultado(*matriculas_ctrl.crear(datos))
    pausa()


def listar_matriculas() -> None:
    imprimir_titulo("HISTORIAL DE MATRICULAS")
    mostrar_lista(matriculas_ctrl.leer(), "No existen matriculas registradas.")
    pausa()


def asentar_calificacion() -> None:
    imprimir_titulo("ASENTAR CALIFICACION")
    ide = pedir_entero("ID de la matricula: ")
    if ide is None:
        imprimir_error("ID invalido.")
        return pausa()

    nota_raw = input("Ingrese la calificacion final (0.00 a 20.00): ").strip()
    mostrar_resultado(*matriculas_ctrl.actualizar(ide, {"nota": nota_raw}))
    pausa()


def ver_reporte_estudiante() -> None:
    imprimir_titulo("BOLETIN ACADEMICO")
    ide = pedir_entero("ID del estudiante: ")
    if ide is None:
        imprimir_error("ID invalido.")
        return pausa()

    boletin = matriculas_ctrl.reporte_academico(ide)
    if boletin is None:
        imprimir_error("Estudiante no registrado en el sistema.")
    else:
        print(boletin)
    pausa()


def anular_matricula() -> None:
    imprimir_titulo("ANULAR MATRICULA")
    ide = pedir_entero("ID de la matricula a anular: ")
    if ide is None:
        imprimir_error("ID invalido.")
        return pausa()

    if confirmar("Se devolvera la plaza a la materia. Confirma anular?"):
        mostrar_resultado(*matriculas_ctrl.eliminar(ide))
    else:
        imprimir_info("Operacion cancelada por el usuario.")
    pausa()


def resumen_sistema() -> None:
    imprimir_titulo("METRICAS GLOBALES DEL SISTEMA")
    total_est = len(estudiantes_ctrl.leer())
    total_mat = len(materias_ctrl.leer())
    total_ins = len(matriculas_ctrl.leer())
    carreras = estudiantes_ctrl.carreras_registradas()

    materias_sin_cupo = [m for m in materias_ctrl.leer() if not m.hay_cupo()]

    print(f"  Total estudiantes registrados : {total_est}")
    print(f"  Carreras activas              : {', '.join(carreras) if carreras else 'Ninguna'}")
    print(f"  Total asignaturas en malla    : {total_mat}")
    print(f"  Asignaturas sin cupos         : {len(materias_sin_cupo)}")
    print(f"  Total matriculas asentadas    : {total_ins}")
    pausa()


# --- MAPAS DE NAVEGACION POR DICCIONARIO ---

MENU_ESTUDIANTES = {
    "1": ("Crear estudiante", crear_estudiante),
    "2": ("Listar todos", listar_estudiantes),
    "3": ("Buscar estudiante", buscar_estudiante),
    "4": ("Ver por identificador", ver_estudiante),
    "5": ("Actualizar datos", actualizar_estudiante),
    "6": ("Eliminar estudiante", eliminar_estudiante),
    "0": ("Volver al menu principal", None),
}

MENU_MATERIAS = {
    "1": ("Crear materia", crear_materia),
    "2": ("Listar todas", listar_materias),
    "3": ("Buscar materia", buscar_materia),
    "4": ("Ver por identificador", ver_materia),
    "5": ("Actualizar datos", actualizar_materia),
    "6": ("Eliminar materia", eliminar_materia),
    "0": ("Volver al menu principal", None),
}

MENU_MATRICULAS = {
    "1": ("Registrar matricula", registrar_matricula),
    "2": ("Listar matriculas", listar_matriculas),
    "3": ("Asentar calificacion", asentar_calificacion),
    "4": ("Ver boletin por alumno", ver_reporte_estudiante),
    "5": ("Anular inscripcion", anular_matricula),
    "0": ("Volver al menu principal", None),
}


def ejecutar_submenu(titulo: str, opciones: Dict[str, Tuple[str, Any]]) -> None:
    """Ejecutor generico para bucles de submenus."""
    while True:
        imprimir_titulo(titulo)
        for tecla, (texto, _) in opciones.items():
            print(f"  {tecla}. {texto}")
        print()

        tecla = input("Seleccione una opcion: ").strip()
        if tecla not in opciones:
            imprimir_error("Opcion fuera de rango.")
            pausa()
            continue

        _, funcion = opciones[tecla]
        if funcion is None:
            break
        funcion()


def main() -> None:
    """Punto de entrada principal del aplicativo."""
    while True:
        imprimir_titulo("SISTEMA DE GESTION ACADEMICA UNIVERSITARIA")
        print("  1. Modulo de Estudiantes")
        print("  2. Modulo de Materias")
        print("  3. Modulo de Matriculas y Calificaciones")
        print("  4. Metricas y Resumen General")
        print("  0. Salir de la aplicacion\n")

        tecla = input("Seleccione una opcion: ").strip()
        if tecla == "1":
            ejecutar_submenu("ADMINISTRACION DE ESTUDIANTES", MENU_ESTUDIANTES)
        elif tecla == "2":
            ejecutar_submenu("ADMINISTRACION DE MATERIAS", MENU_MATERIAS)
        elif tecla == "3":
            ejecutar_submenu("CONTROL ACADEMICO Y MATRICULAS", MENU_MATRICULAS)
        elif tecla == "4":
            resumen_sistema()
        elif tecla == "0":
            imprimir_info("Cierre de sesion satisfactorio. Hasta luego.")
            break
        else:
            imprimir_error("Opcion no valida.")
            pausa()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nEjecucion interrumpida por el usuario.")

