#Proyecto 1#

import sys
import os


def leer_lista_desde_archivo(ruta_archivo):
    """
    Lee un archivo de texto y construye una lista de enteros con su contenido.

    Se admite que los números estén separados por espacios y/o saltos de
    línea. Lanza excepciones específicas si el archivo no existe, no se
    puede leer, o contiene datos que no son enteros.

    :param ruta_archivo: ruta al archivo a leer
    :return: lista de enteros
    :raises FileNotFoundError: si el archivo no existe
    :raises PermissionError: si no hay permisos de lectura
    :raises ValueError: si el archivo contiene un valor no entero
    """
    if not os.path.isfile(ruta_archivo):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_archivo}")

    lista = []
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            contenido = f.read()
    except PermissionError:
        raise PermissionError(f"No hay permisos para leer el archivo: {ruta_archivo}")
    except OSError as e:
        raise OSError(f"Error al leer el archivo {ruta_archivo}: {e}")

    tokens = contenido.split()
    for i, token in enumerate(tokens):
        try:
            lista.append(int(token))
        except ValueError:
            raise ValueError(
                f"El archivo contiene un valor no entero en la posición {i}: '{token}'"
            )

    return lista


def calcular_promedio(lista, n1, n2):
    """
    Calcula el promedio de los elementos de 'lista' entre las posiciones
    n1 y n2 (ambas inclusive), aplicando las reglas del enunciado.

    :param lista: lista de enteros
    :param n1: posición inicial (entero >= 0)
    :param n2: posición final (entero >= 0)
    :return: promedio (float) o 0 según las reglas indicadas
    :raises ValueError: si n1 o n2 son negativos
    """
    if n1 < 0 or n2 < 0:
        raise ValueError("Los parámetros n1 y n2 deben ser mayores o iguales que 0")

    longitud = len(lista)

    
    if n2 < n1:
        return 0

    
    if n1 > longitud:
        return 0

    
    limite_superior = min(n2, longitud - 1)

    if n1 > limite_superior:
        return 0

    sublista = lista[n1:limite_superior + 1]

    if not sublista:
        return 0

    return sum(sublista) / len(sublista)


def parsear_argumentos(argv):
    """
    Valida y convierte los argumentos de línea de comandos.

    :param argv: lista de argumentos (sin el nombre del script)
    :return: tupla (ruta_archivo, n1, n2)
    :raises ValueError: si la cantidad o el tipo de argumentos es incorrecto
    """
    if len(argv) != 3:
        raise ValueError(
            "Uso: python3 proyecto1.py <archivo> <n1> <n2>"
        )

    ruta_archivo = argv[0]

    try:
        n1 = int(argv[1])
        n2 = int(argv[2])
    except ValueError:
        raise ValueError("Los parámetros n1 y n2 deben ser números enteros")

    if n1 < 0 or n2 < 0:
        raise ValueError("Los parámetros n1 y n2 deben ser mayores o iguales que 0")

    return ruta_archivo, n1, n2


def main():
    try:
        ruta_archivo, n1, n2 = parsear_argumentos(sys.argv[1:])

        
        if not os.path.isabs(ruta_archivo) and not os.path.isfile(ruta_archivo):
            ruta_candidata = os.path.join(os.path.dirname(__file__), ruta_archivo)
            if os.path.isfile(ruta_candidata):
                ruta_archivo = ruta_candidata

        lista = leer_lista_desde_archivo(ruta_archivo)
        promedio = calcular_promedio(lista, n1, n2)

        print(f"Lista leída ({len(lista)} elementos): {lista}")
        print(f"Promedio entre posiciones {n1} y {n2}: {promedio}")

    except (FileNotFoundError, PermissionError, ValueError, OSError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error inesperado: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
