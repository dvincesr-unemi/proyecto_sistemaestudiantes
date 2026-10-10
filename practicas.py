# ENUNCIADO 1:
# Dada ciudades = ["Quito", "Guayaquil", "Quito", "Cuenca", "Guayaquil"],
# obten una lista sin repetidos respetando el orden de aparicion.

# BOSQUEJO
# 1. Necesito una lista con el orden original y un set para verificar rapido.
# 2. Creo 'vistas' vacio (set) y 'unicas' vacio (lista).
# 3. Recorro cada ciudad de la lista original:
#    - Si la ciudad no esta en 'vistas':
#        a. La anado a 'vistas' para no procesarla de nuevo.
#        b. La guardo en 'unicas' para mantener su turno.
#    - Si ya esta en 'vistas', no hago nada y sigo con la siguiente.
# 4. Al terminar el recorrido, devuelvo 'unicas'.

# CODIGO:
ciudades = ["Quito", "Guayaquil", "Quito", "Cuenca", "Guayaquil"]

vistas = set()
unicas = []

for ciudad in ciudades:
    if ciudad not in vistas:
        vistas.add(ciudad)
        unicas.append(ciudad)

print(unicas)  # Salida: ['Quito', 'Guayaquil', 'Cuenca']

# ENUNCIADO 2:
# Dada ciudades = ["Quito", "Guayaquil", "Quito", "Cuenca", "Guayaquil"],
# obten una lista sin repetidos respetando el orden de aparicion.

# BOSQUEJO 
# 1. Necesito una lista con el orden original y un set para verificar rapido.
# 2. Creo 'vistas' vacio (set) y 'unicas' vacio (lista).
# 3. Recorro cada ciudad de la lista original:
#    - Si la ciudad no esta en 'vistas':
#        a. La anado a 'vistas' para no procesarla de nuevo.
#        b. La guardo en 'unicas' para mantener su turno.
#    - Si ya esta en 'vistas', no hago nada y sigo con la siguiente.
# 4. Al terminar el recorrido, devuelvo 'unicas'.

# CODIGO:
ciudades = ["Quito", "Guayaquil", "Quito", "Cuenca", "Guayaquil"]

vistas = set()
unicas = []

for ciudad in ciudades:
    if ciudad not in vistas:
        vistas.add(ciudad)
        unicas.append(ciudad)

print(unicas)  # Salida: ['Quito', 'Guayaquil', 'Cuenca']

# ENUNCIADO 3:
# Dados:
# inscritos_matematica = {"Ana", "Luis", "Sol", "Marco"}
# inscritos_ingles = {"Luis", "Marco", "Ruth"}
# Responder con codigo:
# 1. Quienes estan en las dos materias?
# 2. Quienes estan solo en matematica?
# 3. Cuantos estudiantes distintos hay en total?

# BOSQUEJO 
# 1. Identificar que ambas estructuras son conjuntos (set), ideales para operaciones algebraicas:
#    - Estudiantes en ambas: Interseccion (&) entre ambos conjuntos.
#    - Solo en matematica: Diferencia (-) quitando los de ingles.
#    - Total distintos: Cardinalidad (len) de la Union (|) de ambos conjuntos.
# 2. Aplicar las operaciones directas de conjuntos:
#    - ambas = inscritos_matematica & inscritos_ingles
#    - solo_mate = inscritos_matematica - inscritos_ingles
#    - total = len(inscritos_matematica | inscritos_ingles)
# 3. Ordenar las respuestas con sorted() para visualizarlas limpiamente.

# CODIGO:
inscritos_matematica = {"Ana", "Luis", "Sol", "Marco"}
inscritos_ingles = {"Luis", "Marco", "Ruth"}

ambas = inscritos_matematica & inscritos_ingles
solo_mate = inscritos_matematica - inscritos_ingles
total = len(inscritos_matematica | inscritos_ingles)

print(sorted(ambas), sorted(solo_mate), total)

# ENUNCIADO 4:
# Con clientes = [{"id": 1, "nombre": "Ana"}, {"id": 2, "nombre": "Luis"}],
# crea un diccionario {id: cliente} para acceder por id sin recorrer la lista.
# Luego imprime el nombre del id 2.

# BOSQUEJO
# 1. Problema actual: Buscar en una lista requiere recorrerla elemento por elemento O(N).
# 2. Objetivo: Indexar la coleccion para busquedas instantaneas en tiempo constante O(1).
# 3. Diseno de la estructura resultante:
#    - Clave: el identificador unico (cliente["id"])
#    - Valor: el diccionario completo del cliente (cliente)
# 4. Construccion:
#    - Usar diccionario por comprension: {c["id"]: c for c in clientes}
# 5. Acceso directo:
#    - Obtener el registro con indice[2] y luego acceder a su clave ["nombre"].

# CODIGO:
clientes = [{"id": 1, "nombre": "Ana"}, {"id": 2, "nombre": "Luis"}]

# Creacion del indice mediante diccionario por comprension
indice = {cliente["id"]: cliente for cliente in clientes}

# Acceso directo por clave O(1)
print(indice[2]["nombre"])  # Salida: Luis

# ENUNCIADO 5:
# Dada ventas = [("enero", 1500), ("febrero", 1800), ("marzo", 1200)],
# imprime el mes con mayor venta y el total, usando desempaquetado de tuplas.

# BOSQUEJO 
# 1. Cada elemento es una tupla inmutable de dos posiciones: (mes, monto).
# 2. Calcular el total:
#    - Recorrer cada tupla extrayendo solo el monto con desempaquetado (_mes, monto).
#    - Acumularlos con sum().
# 3. Encontrar la tupla lider:
#    - Usar max() indicando que compare por el segundo elemento (indice 1: monto).
#    - Desempaquetar la tupla ganadora directamente en dos variables: mejor_mes, mejor_monto.
# 4. Mostrar reporte:
#    - Imprimir metricas calculadas.
#    - Recorrer y desempaquetar (mes, monto) en el bucle for para listar con formato.

# CODIGO:
ventas = [("enero", 1500), ("febrero", 1800), ("marzo", 1200)]

# Desempaquetado en expresion generadora para sumar montos
total = sum(monto for _mes, monto in ventas)

# Busqueda del maximo por criterio de monto y desempaquetado directo
mejor_mes, mejor_monto = max(ventas, key=lambda venta: venta[1])

print(f"Total: {total}")
print(f"Mejor mes: {mejor_mes} con {mejor_monto}")

# Desempaquetado iterativo para formato en columnas
for mes, monto in ventas:
    print(f"{mes:<10} {monto}")

# ENUNCIADO 6:
# Agrega al Controlador la funcion clientes_por_ciudad() que devuelva
# un diccionario agrupando por ciudad: {"Guayaquil": ["Ana", "Luis"], "Quito": ["Sol"]}.

# BOSQUEJO 
# 1. Objetivo: Agrupar una coleccion uno-a-muchos (Ciudad -> Lista de Nombres).
# 2. Inicializar 'agrupados' como un diccionario vacio {}.
# 3. Leer los datos persistidos mediante el gestor:
#    - Recorrer cada registro individual.
#    - Extraer la ciudad limpiando el texto con .title(), asignando "Sin ciudad" si viene vacia.
# 4. Agrupacion segura con .setdefault():
#    - Si la clave 'ciudad' no existe en 'agrupados', crea una lista vacia [] asociada a esa clave.
#    - Recupera esa lista (nueva o existente) y hace .append() del nombre del cliente.
# 5. Retornar el diccionario con todas las ciudades y sus listas asociadas.

# CODIGO:
def clientes_por_ciudad():
    agrupados = {}
   # for registro in gestor.leer():
   #     ciudad = registro.get("ciudad", "").title() or "Sin ciudad"
    #   agrupados.setdefault(ciudad, []).append(registro["nombre"])
    return agrupados

# ENUNCIADO 7:
# Clasifica cada metodo y justifica:
# (a) calcular el total de una venta
# (b) crear un objeto Producto a partir de un diccionario
# (c) saber si un precio es valido
# (d) saber si un producto tiene stock bajo
# (e) calcular el IVA de cualquier monto

# (a) Calcular el total de una venta
# Tipo: Metodo de instancia.
# Explicacion: Necesita consultar atributos propios de ese objeto en especifico 
# (self.cantidad y self.precio_unitario) para realizar la multiplicacion.

# (b) Crear un objeto Producto a partir de un diccionario
# Tipo: Metodo de clase (@classmethod).
# Explicacion: Actua como fabrica. En el momento de la llamada la instancia todavia 
# no existe; recibe la referencia de la clase (cls) para construirla y retornarla.

# (c) Saber si un precio es valido
# Tipo: Metodo estatico (@staticmethod).
# Explicacion: Es una validacion logica pura (por ejemplo, comprobar si un numero 
# es mayor a cero). No depende de ningun objeto creado ni de variables de clase.

# (d) Saber si un producto tiene stock bajo
# Tipo: Metodo de instancia.
# Explicacion: Requiere leer el valor particular de self.stock de ese articulo 
# para evaluarlo frente al umbral minimo permitido.

# (e) Calcular el IVA de cualquier monto
# Tipo: Metodo estatico (@staticmethod).
# Explicacion: Es una operacion matematica utilitaria independiente. Recibe un numero, 
# aplica una formula y retorna el resultado sin consultar el estado del sistema.

# ENUNCIADO 8:
# Agrega la clase Proveedor, que hereda de Persona y suma ruc y empresa.
# Escribe __init__, a_diccionario() y etiqueta() reutilizando al padre.

# BOSQUEJO 
# 1. Definir la clase Proveedor heredando de Persona: class Proveedor(Persona).
# 2. En __init__:
#    - Recibir los datos del padre (id_registro, nombre, apellido, email) mas los propios (ruc, empresa).
#    - Delegar la inicializacion comun al padre con super().__init__(...).
#    - Asignar los atributos nuevos: self.ruc y self.empresa.
# 3. En a_diccionario:
#    - Obtener el diccionario base con super().a_diccionario().
#    - Extender ese diccionario agregando las claves "ruc" y "empresa".
#    - Retornar el diccionario completo.
# 4. En etiqueta:
#    - Reutilizar el texto formateado del padre con super().etiqueta().
#    - Concatenar la informacion de empresa y ruc para aprovechar el polimorfismo en __str__.
class Persona:
    pass
# CODIGO:
class Proveedor(Persona):

    def __init__(self, id_registro, nombre, apellido, email, ruc="", empresa=""):
        super().__init__(id_registro, nombre, apellido, email)
        self.ruc = ruc
        self.empresa = empresa

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["ruc"] = self.ruc
        datos["empresa"] = self.empresa
        return datos

    def etiqueta(self):
        return f"{super().etiqueta()} · {self.empresa or 'sin empresa'} · RUC {self.ruc}"


# Demostracion: hereda desde_diccionario() y __str__() sin escribir codigo extra
p = Proveedor.desde_diccionario({
    "id": 1,
    "nombre": "Luis",
    "apellido": "Mora",
    "email": "luis@x.com",
    "ruc": "0912345678001",
    "empresa": "Importadora Sur"
})
print(p)

# ENUNCIADO 9:
# Esta funcion tiene el olor a "falta polimorfismo". Reescribela sin ningun if de tipo.
# def describir(objeto, tipo):
#     if tipo == "cliente":
#         return f"{objeto.nombre} {objeto.apellido} de {objeto.ciudad}"
#     elif tipo == "producto":
#         return f"{objeto.nombre} a ${objeto.precio}"
#     elif tipo == "venta":
#         return f"venta de {objeto.cantidad} unidades"

# BOSQUEJO 
# 1. Detectar el problema:
#    - El condicional 'if/elif' pregunta por el tipo de dato, acoplando la funcion a clases concretas.
# 2. Principio clave de POO:
#    - No preguntes que tipo es; dile al objeto que haga su trabajo (Tell, Don't Ask).
#    - Cada clase (Cliente, Producto, Venta) implementa su propio metodo 'etiqueta()'.
# 3. Simplificacion:
#    - La funcion 'describir' elimina el parametro 'tipo' y solo delega: return objeto.etiqueta().
#    - En nuestra jerarquia con ModeloBase, invocar print(objeto) ya ejecuta __str__(),
#      el cual llama internamente a etiqueta() por enlace dinamico.

# CODIGO:
def describir(objeto):
    # Cada clase ya sabe describirse: solo hay que preguntarle
    return objeto.etiqueta()


# O directamente usando la sobrecarga de __str__ de ModeloBase:
# print(objeto)  # __str__ de ModeloBase llama a etiqueta()

# ENUNCIADO:
# Agrega a Producto el atributo estatico DESCUENTO_MAYORISTA = 0.10 y el metodo 
# estatico precio_mayorista(precio, cantidad), que aplica el descuento solo si 
# la cantidad es 12 o mas. Usalo en el comprobante.

# BOSQUEJO MENTAL (PSEUDO-ALGORITMO):
# 1. Definir constantes de clase (atributos estaticos) a nivel de Producto:
#    - DESCUENTO_MAYORISTA = 0.10
#    - CANTIDAD_MAYORISTA = 12 (evita numeros magicos en el codigo)
# 2. Crear metodo estatico con decorador @staticmethod:
#    - Recibe unicamente 'precio' y 'cantidad' (no necesita 'self' ni 'cls').
#    - Si cantidad >= CANTIDAD_MAYORISTA:
#        calcula precio * (1 - 0.10) y redondea a 2 decimales.
#    - Caso contrario:
#        retorna el precio original redondeado.
# 3. Integracion en el flujo de venta:
#    - Invocar Producto.precio_mayorista(precio, cantidad) antes de instanciar la Venta.
class ModeloBase:
    pass
# CODIGO:
class Producto(ModeloBase):
    DESCUENTO_MAYORISTA = 0.10
    CANTIDAD_MAYORISTA = 12

    @staticmethod
    def precio_mayorista(precio, cantidad):
        if cantidad >= Producto.CANTIDAD_MAYORISTA:
            return round(precio * (1 - Producto.DESCUENTO_MAYORISTA), 2)
        return round(precio, 2)


# En views.crear_venta(), al armar la venta:
#precio = Producto.precio_mayorista(producto.precio, int(datos["cantidad"]))
#venta = Venta(
   # siguiente_id(gestor_ventas),
  #  int(datos["cliente_id"]),
   # producto.id,
   # int(datos["cantidad"]),
   # precio
#)