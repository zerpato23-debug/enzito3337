
#Proyecto 2#


import sys
import os
import csv
from datetime import datetime


COLUMNAS_ESPERADAS = ["Fecha", "Producto", "Cantidad", "ValorUnitario"]


FORMATOS_FECHA = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"]


def parsear_fecha(texto_fecha):
    """
    Convierte un texto a un objeto datetime.date probando varios formatos
    comunes (YYYY-MM-DD, DD/MM/YYYY, DD-MM-YYYY).

    :param texto_fecha: fecha en formato de texto
    :return: objeto datetime.date
    :raises ValueError: si el texto no coincide con ningún formato admitido
    """
    texto_fecha = texto_fecha.strip()
    for formato in FORMATOS_FECHA:
        try:
            return datetime.strptime(texto_fecha, formato).date()
        except ValueError:
            continue
    raise ValueError(f"Formato de fecha no reconocido: '{texto_fecha}'")


def leer_ventas_csv(ruta_archivo):
    """
    Lee un archivo CSV de ventas y devuelve una lista de registros, donde
    cada registro es una tupla (fecha, producto, cantidad, valor_unitario)
    ya convertida a los tipos correctos.

    :param ruta_archivo: ruta al archivo CSV de entrada
    :return: lista de tuplas (datetime.date, str, int, float)
    :raises FileNotFoundError: si el archivo no existe
    :raises ValueError: si falta alguna columna esperada o hay datos inválidos
    """
    if not os.path.isfile(ruta_archivo):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_archivo}")

    registros = []
    try:
        with open(ruta_archivo, "r", encoding="utf-8", newline="") as f:
            lector = csv.DictReader(f)

            if lector.fieldnames is None:
                raise ValueError("El archivo CSV está vacío o no tiene encabezado")

            columnas_faltantes = [c for c in COLUMNAS_ESPERADAS if c not in lector.fieldnames]
            if columnas_faltantes:
                raise ValueError(
                    f"Faltan columnas requeridas en el CSV: {columnas_faltantes}"
                )

            for num_fila, fila in enumerate(lector, start=2):  # fila 1 es el encabezado
                try:
                    fecha = parsear_fecha(fila["Fecha"])
                    producto = fila["Producto"].strip()
                    if not producto:
                        raise ValueError("El campo 'Producto' está vacío")

                    cantidad = int(fila["Cantidad"])
                    valor_unitario = float(fila["ValorUnitario"])

                    if cantidad < 0:
                        raise ValueError("La cantidad no puede ser negativa")
                    if valor_unitario < 0:
                        raise ValueError("El valor unitario no puede ser negativo")

                except (ValueError, KeyError) as e:
                    raise ValueError(f"Error en la fila {num_fila} del CSV: {e}")

                registros.append((fecha, producto, cantidad, valor_unitario))

    except PermissionError:
        raise PermissionError(f"No hay permisos para leer el archivo: {ruta_archivo}")
    except csv.Error as e:
        raise ValueError(f"Error al parsear el archivo CSV: {e}")

    return registros


def procesar_ventas(registros):
    """
    Acumula las ventas por producto a partir de una lista de registros.

    Para cada producto guarda:
        - fecha_inicio: fecha de la primera venta
        - fecha_fin: fecha de la última venta
        - cantidad_total: suma de las cantidades vendidas
        - valor_total: suma de (cantidad * valor_unitario)

    :param registros: lista de tuplas (fecha, producto, cantidad, valor_unitario)
    :return: diccionario {producto: {...}}
    """
    resumen = {}

    for fecha, producto, cantidad, valor_unitario in registros:
        valor_venta = cantidad * valor_unitario

        if producto not in resumen:
            resumen[producto] = {
                "fecha_inicio": fecha,
                "fecha_fin": fecha,
                "cantidad_total": cantidad,
                "valor_total": valor_venta,
            }
        else:
            datos = resumen[producto]
            if fecha < datos["fecha_inicio"]:
                datos["fecha_inicio"] = fecha
            if fecha > datos["fecha_fin"]:
                datos["fecha_fin"] = fecha
            datos["cantidad_total"] += cantidad
            datos["valor_total"] += valor_venta

    return resumen


def escribir_resumen_csv(resumen, ruta_salida):
    """
    Escribe el diccionario de resumen de ventas en un archivo CSV.

    Columnas de salida: Producto, FechaInicio, FechaFin, CantidadTotal, ValorTotal

    :param resumen: diccionario devuelto por procesar_ventas
    :param ruta_salida: ruta del archivo CSV a generar
    :raises PermissionError: si no se puede escribir el archivo
    """
    try:
        with open(ruta_salida, "w", encoding="utf-8", newline="") as f:
            escritor = csv.writer(f)
            escritor.writerow(
                ["Producto", "FechaInicio", "FechaFin", "CantidadTotal", "ValorTotal"]
            )

            # Orden alfabético por producto para que la salida sea determinística
            for producto in sorted(resumen.keys()):
                datos = resumen[producto]
                escritor.writerow([
                    producto,
                    datos["fecha_inicio"].strftime("%Y-%m-%d"),
                    datos["fecha_fin"].strftime("%Y-%m-%d"),
                    datos["cantidad_total"],
                    f"{datos['valor_total']:.2f}",
                ])
    except PermissionError:
        raise PermissionError(f"No hay permisos para escribir el archivo: {ruta_salida}")


def parsear_argumentos(argv):
    """
    Valida los argumentos de línea de comandos.

    :param argv: lista de argumentos (sin el nombre del script)
    :return: tupla (ruta_entrada, ruta_salida)
    :raises ValueError: si la cantidad de argumentos es incorrecta
    """
    if len(argv) != 2:
        raise ValueError("Uso: python3 proyecto2.py <archivo_entrada.csv> <archivo_salida.csv>")

    return argv[0], argv[1]


def main():
    try:
        ruta_entrada, ruta_salida = parsear_argumentos(sys.argv[1:])

        # Si la ruta de entrada es relativa y no se encuentra, se busca junto al script
        if not os.path.isabs(ruta_entrada) and not os.path.isfile(ruta_entrada):
            candidata = os.path.join(os.path.dirname(__file__), ruta_entrada)
            if os.path.isfile(candidata):
                ruta_entrada = candidata

        registros = leer_ventas_csv(ruta_entrada)
        resumen = procesar_ventas(registros)
        escribir_resumen_csv(resumen, ruta_salida)

        print(f"Se procesaron {len(registros)} ventas de {len(resumen)} productos.")
        print(f"Resumen guardado en: {ruta_salida}")

    except (FileNotFoundError, PermissionError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error inesperado: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
