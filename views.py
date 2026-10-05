# CONTROLADOR (se llama views.py por compatibilidad con Django).
# Regla: aquí NO hay print() ni input(). Toda función devuelve datos
# o una TUPLA (exito, mensaje / resultado).
from models import Estudiante, CAMPOS_ESTUDIANTE
from shared.json_manager import GestorJSON
from shared.herramientas import es_email_valido

gestor = GestorJSON("data/estudiantes.json")

# TUPLAS de configuración (fijas)
CAMPOS_OBLIGATORIOS = ("nombre", "apellido", "email", "carnet")
CAMPOS_BUSCABLES = ("nombre", "apellido", "email", "carnet")
NOTA_MIN, NOTA_MAX = 0, 20


# ===================== AYUDAS INTERNAS =====================
def valores_usados(campo, excepto_id=None):
    """CONJUNTO con los valores ya usados de un campo (email o carnet)."""
    return {
        str(r[campo]).lower()
        for r in gestor.leer()
        if r["id"] != excepto_id
    }


def siguiente_id():
    ids = [r["id"] for r in gestor.leer()]
    return max(ids) + 1 if ids else 1


def _posicion(registros, id_estudiante):
    for indice, registro in enumerate(registros):
        if registro["id"] == id_estudiante:
            return indice
    return None


# ===================== C · CREATE =====================
def crear_estudiante(datos):
    try:
        valores = {c: str(datos.get(c, "")).strip() for c in CAMPOS_ESTUDIANTE}
        faltantes = [c for c in CAMPOS_OBLIGATORIOS if not valores[c]]
        if faltantes:
            return False, f"Faltan campos obligatorios: {', '.join(faltantes)}"
        if not es_email_valido(valores["email"]):
            return False, f"El email '{valores['email']}' no tiene un formato válido"
        if valores["email"].lower() in valores_usados("email"):
            return False, "Ese email ya está registrado"
        valores["carnet"] = valores["carnet"].upper()
        if valores["carnet"].lower() in valores_usados("carnet"):
            return False, "Ese carnet ya está registrado"

        estudiante = Estudiante(siguiente_id(), **valores)
        registros = gestor.leer()
        registros.append(estudiante.a_diccionario())
        if not gestor.guardar(registros):
            return False, "No se pudo escribir el archivo"
        return True, (f"Estudiante {estudiante.obtener_nombre_completo()} "
                      f"creado con id {estudiante.id}")
    except Exception as error:
        return False, f"Error inesperado: {error}"


# ===================== R · READ =====================
def obtener_todos():
    return [Estudiante.desde_diccionario(r) for r in gestor.leer()]


def obtener_por_id(id_estudiante):
    for estudiante in obtener_todos():
        if estudiante.id == id_estudiante:
            return estudiante
    return None


# ===================== S · SEARCH =====================
def buscar_estudiantes(termino):
    termino = termino.strip().lower()
    if not termino:
        return []
    encontrados = []
    for registro in gestor.leer():
        for campo in CAMPOS_BUSCABLES:
            if termino in str(registro.get(campo, "")).lower():
                encontrados.append(Estudiante.desde_diccionario(registro))
                break
    return encontrados


# ===================== U · UPDATE =====================
def actualizar_estudiante(id_estudiante, cambios):
    try:
        desconocidos = set(cambios) - set(CAMPOS_ESTUDIANTE)   # diferencia de conjuntos
        if desconocidos:
            return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"
        if not cambios:
            return False, "No se indicó ningún cambio"
        if "email" in cambios:
            if not es_email_valido(cambios["email"]):
                return False, "El email no tiene un formato válido"
            if cambios["email"].lower() in valores_usados("email", id_estudiante):
                return False, "Ese email ya lo usa otro estudiante"
        if "carnet" in cambios:
            cambios["carnet"] = cambios["carnet"].strip().upper()
            if cambios["carnet"].lower() in valores_usados("carnet", id_estudiante):
                return False, "Ese carnet ya lo usa otro estudiante"

        registros = gestor.leer()
        posicion = _posicion(registros, id_estudiante)
        if posicion is None:
            return False, f"No existe un estudiante con id {id_estudiante}"
        registros[posicion].update(cambios)
        if not gestor.guardar(registros):
            return False, "No se pudo escribir el archivo"
        return True, f"Estudiante {id_estudiante} actualizado ({len(cambios)} campo/s)"
    except Exception as error:
        return False, f"Error inesperado: {error}"


# ===================== D · DELETE =====================
def eliminar_estudiante(id_estudiante):
    registros = gestor.leer()
    quedan = [r for r in registros if r["id"] != id_estudiante]   # lista nueva
    if len(quedan) == len(registros):
        return False, f"No existe un estudiante con id {id_estudiante}"
    gestor.guardar(quedan)
    return True, f"Estudiante {id_estudiante} eliminado"


# ===================== NOTAS Y CONJUNTOS =====================
def agregar_nota(id_estudiante, materia, nota):
    """nota llega como texto (lo que escribió el usuario) o número."""
    materia = str(materia).strip().title()
    if not materia:
        return False, "La materia es obligatoria"
    try:
        nota = float(nota)
    except (ValueError, TypeError):
        return False, "La nota debe ser un número"
    if not (NOTA_MIN <= nota <= NOTA_MAX):      # también rechaza nan
        return False, f"La nota debe estar entre {NOTA_MIN} y {NOTA_MAX}"
    if nota.is_integer():
        nota = int(nota)

    registros = gestor.leer()
    posicion = _posicion(registros, id_estudiante)
    if posicion is None:
        return False, f"No existe un estudiante con id {id_estudiante}"

    estudiante = Estudiante.desde_diccionario(registros[posicion])
    estudiante.agregar_nota(materia, nota)
    registros[posicion] = estudiante.a_diccionario()
    if not gestor.guardar(registros):
        return False, "No se pudo escribir el archivo"
    return True, f"Nota {nota} registrada en {materia}"


def obtener_promedio(id_estudiante):
    estudiante = obtener_por_id(id_estudiante)
    if not estudiante:
        return False, f"No existe un estudiante con id {id_estudiante}"
    return True, estudiante.obtener_promedio()


def materias_ofertadas():
    """SET con todas las materias inscritas por todos, sin repetir."""
    todas = set()
    for estudiante in obtener_todos():
        todas |= estudiante.materias          # unión
    return todas


def estudiantes_en_comun(id_a, id_b):
    """Devuelve (exito, set de materias comunes | mensaje de error)."""
    if id_a == id_b:
        return False, "Debe elegir dos estudiantes distintos"
    a, b = obtener_por_id(id_a), obtener_por_id(id_b)
    if not a or not b:
        return False, "Alguno de los dos ids no existe"
    return True, a.materias_en_comun(b)       # intersección
