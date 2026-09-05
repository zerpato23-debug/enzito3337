"""
Proyecto Ventas
---------------
Programa único con tres funciones, elegibles por subcomando:

  generar   -> crea un CSV de ejemplo con columnas Fecha,Producto,Cantidad,ValorUnitario
  procesar  -> lee un CSV de ventas y genera un resumen acumulado por producto
  test      -> corre los tests unitarios del programa

Uso:
    python proyecto_ventas.py generar -o mis_ventas.csv
    python proyecto_ventas.py procesar mis_ventas.csv -o resumen.csv
    python proyecto_ventas.py test
"""

import argparse
import csv
import sys
import unittest
from datetime import datetime
from pathlib import Path

FORMATO_FECHA = "%Y-%m-%d"


# ---------------------------------------------------------------------------
# Excepciones propias
# ---------------------------------------------------------------------------

class ArchivoVentasError(Exception):
    """Error propio para problemas de formato o contenido del archivo de ventas."""
    pass


# ---------------------------------------------------------------------------
# Generación de un CSV de ejemplo
# ---------------------------------------------------------------------------

VENTAS_EJEMPLO = [
    ("2024-01-05", "Mouse", 3, 1500),
    ("2024-01-10", "Teclado", 1, 5000),
    ("2024-01-15", "Mouse", 2, 1500),
    ("2024-02-01", "Mouse", 1, 1600),
    ("2024-01-20", "Monitor", 2, 80000),
    ("2024-03-01", "Teclado", 4, 5200),
]


def generar_csv(ruta_salida: str) -> None:
    """Crea un CSV de ejemplo con el formato Fecha,Producto,Cantidad,ValorUnitario."""
    with open(ruta_salida, "w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        escritor.writerow(["Fecha", "Producto", "Cantidad", "ValorUnitario"])
        escritor.writerows(VENTAS_EJEMPLO)


# ---------------------------------------------------------------------------
# Procesamiento de ventas
# ---------------------------------------------------------------------------

def parsear_fecha(fecha_str: str) -> datetime:
    """Convierte un texto 'YYYY-MM-DD' en un objeto datetime."""
    try:
        return datetime.strptime(fecha_str.strip(), FORMATO_FECHA)
    except ValueError as e:
        raise ArchivoVentasError(f"fecha inválida '{fecha_str}' ({e})")


def procesar_archivo(ruta_entrada: str) -> dict:
    """
    Lee el CSV de ventas y devuelve un diccionario:
        { producto: {"fecha_inicio": datetime,
                      "fecha_fin": datetime,
                      "cantidad_total": int,
                      "valor_total": float} }
    Las filas con datos inválidos se informan por stderr y se descartan.
    """
    ruta = Path(ruta_entrada)
    if not ruta.exists():
        raise FileNotFoundError(f"no se encontró el archivo '{ruta_entrada}'")

    columnas_esperadas = {"Fecha", "Producto", "Cantidad", "ValorUnitario"}
    resumen: dict = {}

    with ruta.open(newline="", encoding="utf-8") as f:
        lector = csv.DictReader(f)

        if lector.fieldnames is None or not columnas_esperadas.issubset(set(lector.fieldnames)):
            raise ArchivoVentasError(
                f"el encabezado debe contener las columnas {columnas_esperadas}, "
                f"se encontró {lector.fieldnames}"
            )

        for num_fila, fila in enumerate(lector, start=2):  # la fila 1 es el encabezado
            try:
                producto = (fila.get("Producto") or "").strip()
                if not producto:
                    raise ArchivoVentasError("el producto está vacío")

                fecha = parsear_fecha(fila["Fecha"])
                cantidad = int(fila["Cantidad"])
                valor_unitario = float(fila["ValorUnitario"])

                if cantidad < 0 or valor_unitario < 0:
                    raise ArchivoVentasError("Cantidad y ValorUnitario deben ser >= 0")

                valor_fila = cantidad * valor_unitario

                if producto not in resumen:
                    resumen[producto] = {
                        "fecha_inicio": fecha,
                        "fecha_fin": fecha,
                        "cantidad_total": 0,
                        "valor_total": 0.0,
                    }

                datos = resumen[producto]
                datos["fecha_inicio"] = min(datos["fecha_inicio"], fecha)
                datos["fecha_fin"] = max(datos["fecha_fin"], fecha)
                datos["cantidad_total"] += cantidad
                datos["valor_total"] += valor_fila

            except (ArchivoVentasError, ValueError, KeyError) as e:
                print(f"Aviso: se ignora la fila {num_fila} ({e})", file=sys.stderr)
                continue

    return resumen


def guardar_resumen(resumen: dict, ruta_salida: str) -> None:
    """Guarda el diccionario de resumen en un CSV ordenado por producto."""
    campos = ["Producto", "FechaInicio", "FechaFin", "CantidadTotal", "ValorTotal"]
    with open(ruta_salida, "w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=campos)
        escritor.writeheader()
        for producto, datos in sorted(resumen.items()):
            escritor.writerow({
                "Producto": producto,
                "FechaInicio": datos["fecha_inicio"].strftime(FORMATO_FECHA),
                "FechaFin": datos["fecha_fin"].strftime(FORMATO_FECHA),
                "CantidadTotal": datos["cantidad_total"],
                "ValorTotal": f"{datos['valor_total']:.2f}",
            })


# ---------------------------------------------------------------------------
# Tests unitarios (se corren con el subcomando "test")
# ---------------------------------------------------------------------------

CSV_OK = """Fecha,Producto,Cantidad,ValorUnitario
2024-01-05,Mouse,3,1500
2024-01-10,Teclado,1,5000
2024-01-15,Mouse,2,1500
2024-02-01,Mouse,1,1600
"""

CSV_FILA_INVALIDA = """Fecha,Producto,Cantidad,ValorUnitario
2024-01-05,Mouse,tres,1500
2024-01-10,Teclado,1,5000
"""

CSV_ENCABEZADO_INVALIDO = """A,B,C,D
1,2,3,4
"""


class TestProcesarVentas(unittest.TestCase):

    def _crear_csv(self, contenido: str) -> str:
        import tempfile
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="")
        f.write(contenido)
        f.close()
        return f.name

    def test_acumulacion_correcta(self):
        import os
        ruta = self._crear_csv(CSV_OK)
        try:
            resumen = procesar_archivo(ruta)
            self.assertIn("Mouse", resumen)
            self.assertEqual(resumen["Mouse"]["cantidad_total"], 6)
            self.assertAlmostEqual(resumen["Mouse"]["valor_total"], 9100.0)
            self.assertEqual(resumen["Mouse"]["fecha_inicio"], datetime(2024, 1, 5))
            self.assertEqual(resumen["Mouse"]["fecha_fin"], datetime(2024, 2, 1))
            self.assertEqual(resumen["Teclado"]["cantidad_total"], 1)
        finally:
            os.remove(ruta)

    def test_archivo_inexistente(self):
        with self.assertRaises(FileNotFoundError):
            procesar_archivo("no_existe_1234.csv")

    def test_encabezado_invalido(self):
        import os
        ruta = self._crear_csv(CSV_ENCABEZADO_INVALIDO)
        try:
            with self.assertRaises(ArchivoVentasError):
                procesar_archivo(ruta)
        finally:
            os.remove(ruta)

    def test_fila_invalida_se_ignora(self):
        import os
        ruta = self._crear_csv(CSV_FILA_INVALIDA)
        try:
            resumen = procesar_archivo(ruta)
            self.assertNotIn("Mouse", resumen)
            self.assertIn("Teclado", resumen)
        finally:
            os.remove(ruta)

    def test_guardar_resumen(self):
        import os
        import tempfile
        ruta = self._crear_csv(CSV_OK)
        salida = tempfile.mktemp(suffix=".csv")
        try:
            resumen = procesar_archivo(ruta)
            guardar_resumen(resumen, salida)
            with open(salida, encoding="utf-8") as f:
                contenido = f.read()
            self.assertIn("Mouse", contenido)
            self.assertIn("Teclado", contenido)
            self.assertIn("FechaInicio", contenido)
        finally:
            os.remove(ruta)
            if os.path.exists(salida):
                os.remove(salida)


# ---------------------------------------------------------------------------
# Línea de comandos
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Genera, procesa o testea el manejo de ventas por CSV."
    )
    subparsers = parser.add_subparsers(dest="comando", required=True)

    p_generar = subparsers.add_parser("generar", help="genera un CSV de ejemplo")
    p_generar.add_argument(
        "-o", "--salida", default="mis_ventas.csv",
        help="nombre del CSV a generar (default: mis_ventas.csv)",
    )

    p_procesar = subparsers.add_parser("procesar", help="procesa un CSV de ventas")
    p_procesar.add_argument("archivo_entrada", help="ruta del CSV de entrada")
    p_procesar.add_argument(
        "-o", "--salida", default="resumen_ventas.csv",
        help="ruta del CSV de salida (default: resumen_ventas.csv)",
    )

    subparsers.add_parser("test", help="corre los tests unitarios")

    args = parser.parse_args()

    if args.comando == "generar":
        generar_csv(args.salida)
        print(f"CSV de ejemplo generado en: {args.salida}")

    elif args.comando == "procesar":
        try:
            resumen = procesar_archivo(args.archivo_entrada)
        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        except ArchivoVentasError as e:
            print(f"Error en el archivo: {e}", file=sys.stderr)
            sys.exit(1)

        if not resumen:
            print("No se procesó ninguna venta válida.", file=sys.stderr)
            sys.exit(1)

        guardar_resumen(resumen, args.salida)
        print(f"Resumen guardado en: {args.salida}")

    elif args.comando == "test":
        suite = unittest.TestLoader().loadTestsFromTestCase(TestProcesarVentas)
        runner = unittest.TextTestRunner(verbosity=2)
        resultado = runner.run(suite)
        sys.exit(0 if resultado.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
