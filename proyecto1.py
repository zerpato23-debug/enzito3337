import os
import sys


def leer_archivo(ruta):
    """Lee un archivo con enteros y devuelve una lista con los datos."""
    lista = []
    with open(ruta, "r") as archivo:
        for linea in archivo:
            for palabra in linea.split():
                lista.append(int(palabra))  # ValueError si no es entero
    return lista


def promedio(lista, inicio, fin):
    """Promedio de los valores entre las posiciones inicio y fin (inclusive).
    Las posiciones cuentan desde 1."""
    if fin < inicio or inicio > len(lista):
        return 0
    if fin > len(lista):
        fin = len(lista)
    if inicio < 1:
        inicio = 1
    segmento = lista[inicio - 1:fin]
    return sum(segmento) / len(segmento)


def main():
    try:
        ruta = os.path.join(os.path.dirname(__file__), sys.argv[1])
        inicio = int(sys.argv[2])
        fin = int(sys.argv[3])
        if inicio < 0 or fin < 0:
            raise ValueError("los enteros deben ser mayores o iguales que 0")
        lista = leer_archivo(ruta)
        print(promedio(lista, inicio, fin))
    except IndexError:
        print("Uso: python promedio.py <archivo> <entero1> <entero2>")
    except FileNotFoundError:
        print("Error: no se encontró el archivo", sys.argv[1])
    except ValueError as error:
        print("Error: valor inválido:", error)


main()
