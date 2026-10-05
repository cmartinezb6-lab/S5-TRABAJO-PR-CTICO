# VISTA: solo menú, input() y print(). Sin reglas de negocio ni acceso a archivos.
from models import CAMPOS_ESTUDIANTE
from shared.herramientas import (
    imprimir_titulo, imprimir_exito, imprimir_error, imprimir_info, confirmar
)
from views import (
    crear_estudiante, obtener_todos, obtener_por_id, buscar_estudiantes,
    actualizar_estudiante, eliminar_estudiante, agregar_nota,
    obtener_promedio, materias_ofertadas, estudiantes_en_comun
)


def pausa():
    input("\nPresione Enter para continuar...")


def pedir_id(texto="Id del estudiante"):
    """Devuelve un int, o None si el usuario no escribió un entero."""
    try:
        return int(input(f"{texto}: "))
    except ValueError:
        imprimir_error("El id debe ser un número entero")
        return None


def mostrar_resultado(exito, mensaje):
    (imprimir_exito if exito else imprimir_error)(mensaje)


def mostrar_tabla(estudiantes):
    print(f"{'ID':<5}{'CARNET':<14}{'NOMBRE':<25}{'EMAIL':<28}{'PROMEDIO':<9}")
    print("-" * 81)
    for e in estudiantes:
        print(f"{e.id:<5}{e.carnet:<14}{e.obtener_nombre_completo():<25}"
              f"{e.email:<28}{e.obtener_promedio():<9}")
    print("-" * 81)
    imprimir_info(f"Total: {len(estudiantes)} estudiante(s)")


# ---------- C ----------
def opcion_crear():
    imprimir_titulo("CREAR NUEVO ESTUDIANTE")
    datos = {campo: input(f"{campo.capitalize()}: ") for campo in CAMPOS_ESTUDIANTE}
    mostrar_resultado(*crear_estudiante(datos))
    pausa()


# ---------- R ----------
def opcion_ver_todos():
    imprimir_titulo("LISTA DE ESTUDIANTES")
    estudiantes = obtener_todos()
    if not estudiantes:
        imprimir_info("Todavía no hay estudiantes. Use la opción 1.")
    else:
        mostrar_tabla(estudiantes)
    pausa()


# ---------- S ----------
def opcion_buscar():
    imprimir_titulo("BUSCAR ESTUDIANTE")
    termino = input("Nombre, apellido, email o carnet: ")
    encontrados = buscar_estudiantes(termino)
    if not encontrados:
        imprimir_info(f"Ningún estudiante coincide con '{termino}'.")
    else:
        mostrar_tabla(encontrados)
    pausa()


def opcion_ver_por_id():
    imprimir_titulo("VER ESTUDIANTE POR ID")
    id_est = pedir_id()
    if id_est is None:
        return pausa()
    est = obtener_por_id(id_est)
    if not est:
        imprimir_error(f"No existe un estudiante con id {id_est}")
        return pausa()
    for clave, valor in est.a_diccionario().items():
        if clave == "notas":
            print(f"  {'Notas':<12}:")
            for materia, lista in valor.items():
                print(f"      {materia}: {lista}")
        else:
            print(f"  {clave.capitalize():<12}: {valor}")
    pausa()


# ---------- U ----------
def opcion_actualizar():
    imprimir_titulo("ACTUALIZAR ESTUDIANTE")
    id_est = pedir_id()
    if id_est is None:
        return pausa()
    est = obtener_por_id(id_est)
    if not est:
        imprimir_error(f"No existe un estudiante con id {id_est}")
        return pausa()
    imprimir_info(f"Editando a {est.obtener_nombre_completo()}")
    print("Deje en blanco el campo que no quiera cambiar.\n")
    cambios = {}
    for campo in CAMPOS_ESTUDIANTE:
        nuevo = input(f"{campo.capitalize()} [{getattr(est, campo)}]: ").strip()
        if nuevo:
            cambios[campo] = nuevo
    mostrar_resultado(*actualizar_estudiante(id_est, cambios))
    pausa()


# ---------- D ----------
def opcion_eliminar():
    imprimir_titulo("ELIMINAR ESTUDIANTE")
    id_est = pedir_id()
    if id_est is None:
        return pausa()
    est = obtener_por_id(id_est)
    if not est:
        imprimir_error(f"No existe un estudiante con id {id_est}")
        return pausa()
    imprimir_info(f"Se eliminará: {est}")
    if confirmar("¿Confirma la eliminación?"):
        mostrar_resultado(*eliminar_estudiante(id_est))
    else:
        imprimir_info("Operación cancelada")
    pausa()


# ---------- NOTAS ----------
def opcion_agregar_nota():
    imprimir_titulo("AGREGAR NOTA")
    id_est = pedir_id()
    if id_est is None:
        return pausa()
    materia = input("Materia: ")
    nota = input("Nota (0-20): ")
    mostrar_resultado(*agregar_nota(id_est, materia, nota))
    pausa()


def opcion_promedio():
    imprimir_titulo("VER PROMEDIO")
    id_est = pedir_id()
    if id_est is None:
        return pausa()
    exito, resultado = obtener_promedio(id_est)
    if exito:
        imprimir_info(f"Promedio general: {resultado}")
    else:
        imprimir_error(resultado)
    pausa()


def opcion_materias_comun():
    imprimir_titulo("MATERIAS EN COMÚN")
    id_a = pedir_id("Id del primer estudiante")
    if id_a is None:
        return pausa()
    id_b = pedir_id("Id del segundo estudiante")
    if id_b is None:
        return pausa()
    exito, resultado = estudiantes_en_comun(id_a, id_b)
    if not exito:
        imprimir_error(resultado)
    elif not resultado:
        imprimir_info("No comparten ninguna materia.")
    else:
        imprimir_exito("Materias en común: " + ", ".join(sorted(resultado)))
    pausa()


def opcion_materias_ofertadas():
    imprimir_titulo("MATERIAS OFERTADAS")
    materias = materias_ofertadas()
    if not materias:
        imprimir_info("Aún no hay materias registradas.")
    else:
        for materia in sorted(materias):
            print(f"  • {materia}")
    pausa()


def salir():
    imprimir_info("¡Hasta luego! 👋")
    return "salir"


# DICCIONARIO de opciones: tecla -> (texto del menú, función)
OPCIONES = {
    "1": ("Crear estudiante", opcion_crear),
    "2": ("Ver todos", opcion_ver_todos),
    "3": ("Buscar", opcion_buscar),
    "4": ("Ver por id", opcion_ver_por_id),
    "5": ("Actualizar", opcion_actualizar),
    "6": ("Eliminar", opcion_eliminar),
    "7": ("Agregar nota", opcion_agregar_nota),
    "8": ("Ver promedio", opcion_promedio),
    "9": ("Materias en común", opcion_materias_comun),
    "10": ("Materias ofertadas", opcion_materias_ofertadas),
    "0": ("Salir", salir),
}


def mostrar_menu():
    imprimir_titulo("SISTEMA DE GESTIÓN DE ESTUDIANTES")
    for tecla, (texto, _funcion) in OPCIONES.items():
        print(f"  {tecla}. {texto}")
    print()


def main():
    while True:
        mostrar_menu()
        tecla = input("Seleccione una opción: ").strip()
        if tecla not in OPCIONES:
            imprimir_error("Opción no válida")
            pausa()
            continue
        _texto, funcion = OPCIONES[tecla]
        if funcion() == "salir":
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario.")
