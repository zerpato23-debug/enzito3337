"""
Pruebas unitarias para proyecto2.py

Ejecutar con:
    python3 -m unittest test_proyecto2.py -v
"""

import unittest
import os
import csv
import tempfile
from datetime import date

from proyecto2 import (
    parsear_fecha,
    leer_ventas_csv,
    procesar_ventas,
    escribir_resumen_csv,
    parsear_argumentos,
)


class TestParsearFecha(unittest.TestCase):

    def test_formato_iso(self):
        self.assertEqual(parsear_fecha("2026-01-15"), date(2026, 1, 15))

    def test_formato_barra(self):
        self.assertEqual(parsear_fecha("15/01/2026"), date(2026, 1, 15))

    def test_formato_guion(self):
        self.assertEqual(parsear_fecha("15-01-2026"), date(2026, 1, 15))

    def test_con_espacios(self):
        self.assertEqual(parsear_fecha("  2026-01-15  "), date(2026, 1, 15))

    def test_formato_invalido(self):
        with self.assertRaises(ValueError):
            parsear_fecha("15 de enero de 2026")


class TestLeerVentasCsv(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmpdir.cleanup()

    def _crear_csv(self, contenido):
        ruta = os.path.join(self.tmpdir.name, "ventas.csv")
        with open(ruta, "w", encoding="utf-8", newline="") as f:
            f.write(contenido)
        return ruta

    def test_lectura_basica(self):
        contenido = (
            "Fecha,Producto,Cantidad,ValorUnitario\n"
            "2026-01-10,Lapicera,5,100.0\n"
            "2026-01-12,Cuaderno,2,250.5\n"
        )
        ruta = self._crear_csv(contenido)
        registros = leer_ventas_csv(ruta)
        self.assertEqual(len(registros), 2)
        self.assertEqual(registros[0], (date(2026, 1, 10), "Lapicera", 5, 100.0))
        self.assertEqual(registros[1], (date(2026, 1, 12), "Cuaderno", 2, 250.5))

    def test_archivo_inexistente(self):
        with self.assertRaises(FileNotFoundError):
            leer_ventas_csv(os.path.join(self.tmpdir.name, "no_existe.csv"))

    def test_columna_faltante(self):
        contenido = "Fecha,Producto,Cantidad\n2026-01-10,Lapicera,5\n"
        ruta = self._crear_csv(contenido)
        with self.assertRaises(ValueError):
            leer_ventas_csv(ruta)

    def test_cantidad_no_entera(self):
        contenido = (
            "Fecha,Producto,Cantidad,ValorUnitario\n"
            "2026-01-10,Lapicera,cinco,100.0\n"
        )
        ruta = self._crear_csv(contenido)
        with self.assertRaises(ValueError):
            leer_ventas_csv(ruta)

    def test_cantidad_negativa(self):
        contenido = (
            "Fecha,Producto,Cantidad,ValorUnitario\n"
            "2026-01-10,Lapicera,-3,100.0\n"
        )
        ruta = self._crear_csv(contenido)
        with self.assertRaises(ValueError):
            leer_ventas_csv(ruta)

    def test_valor_unitario_invalido(self):
        contenido = (
            "Fecha,Producto,Cantidad,ValorUnitario\n"
            "2026-01-10,Lapicera,3,caro\n"
        )
        ruta = self._crear_csv(contenido)
        with self.assertRaises(ValueError):
            leer_ventas_csv(ruta)

    def test_producto_vacio(self):
        contenido = (
            "Fecha,Producto,Cantidad,ValorUnitario\n"
            "2026-01-10,,3,100.0\n"
        )
        ruta = self._crear_csv(contenido)
        with self.assertRaises(ValueError):
            leer_ventas_csv(ruta)

    def test_archivo_vacio_sin_encabezado(self):
        ruta = self._crear_csv("")
        with self.assertRaises(ValueError):
            leer_ventas_csv(ruta)


class TestProcesarVentas(unittest.TestCase):

    def test_acumula_un_solo_producto(self):
        registros = [
            (date(2026, 1, 10), "Lapicera", 5, 100.0),
            (date(2026, 1, 15), "Lapicera", 3, 100.0),
        ]
        resumen = procesar_ventas(registros)
        self.assertEqual(resumen["Lapicera"]["fecha_inicio"], date(2026, 1, 10))
        self.assertEqual(resumen["Lapicera"]["fecha_fin"], date(2026, 1, 15))
        self.assertEqual(resumen["Lapicera"]["cantidad_total"], 8)
        self.assertEqual(resumen["Lapicera"]["valor_total"], 800.0)

    def test_varios_productos(self):
        registros = [
            (date(2026, 1, 10), "Lapicera", 5, 100.0),
            (date(2026, 1, 11), "Cuaderno", 2, 250.0),
            (date(2026, 1, 12), "Lapicera", 1, 100.0),
        ]
        resumen = procesar_ventas(registros)
        self.assertEqual(set(resumen.keys()), {"Lapicera", "Cuaderno"})
        self.assertEqual(resumen["Lapicera"]["cantidad_total"], 6)
        self.assertEqual(resumen["Cuaderno"]["cantidad_total"], 2)

    def test_fechas_desordenadas(self):
        # La fecha más antigua y más nueva deben detectarse aunque no
        # vengan en orden cronológico en el archivo
        registros = [
            (date(2026, 3, 1), "Lapicera", 1, 10.0),
            (date(2026, 1, 1), "Lapicera", 1, 10.0),
            (date(2026, 2, 1), "Lapicera", 1, 10.0),
        ]
        resumen = procesar_ventas(registros)
        self.assertEqual(resumen["Lapicera"]["fecha_inicio"], date(2026, 1, 1))
        self.assertEqual(resumen["Lapicera"]["fecha_fin"], date(2026, 3, 1))

    def test_lista_vacia(self):
        self.assertEqual(procesar_ventas([]), {})


class TestEscribirResumenCsv(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_escritura_y_relectura(self):
        resumen = {
            "Cuaderno": {
                "fecha_inicio": date(2026, 1, 11),
                "fecha_fin": date(2026, 1, 11),
                "cantidad_total": 2,
                "valor_total": 500.0,
            },
            "Lapicera": {
                "fecha_inicio": date(2026, 1, 10),
                "fecha_fin": date(2026, 1, 12),
                "cantidad_total": 6,
                "valor_total": 600.0,
            },
        }
        ruta_salida = os.path.join(self.tmpdir.name, "resumen.csv")
        escribir_resumen_csv(resumen, ruta_salida)

        with open(ruta_salida, "r", encoding="utf-8", newline="") as f:
            filas = list(csv.reader(f))

        self.assertEqual(
            filas[0], ["Producto", "FechaInicio", "FechaFin", "CantidadTotal", "ValorTotal"]
        )
        # Orden alfabético: Cuaderno antes que Lapicera
        self.assertEqual(filas[1][0], "Cuaderno")
        self.assertEqual(filas[2][0], "Lapicera")
        self.assertEqual(filas[2][1], "2026-01-10")
        self.assertEqual(filas[2][2], "2026-01-12")
        self.assertEqual(filas[2][4], "600.00")


class TestParsearArgumentos(unittest.TestCase):

    def test_argumentos_validos(self):
        entrada, salida = parsear_argumentos(["ventas.csv", "resumen.csv"])
        self.assertEqual(entrada, "ventas.csv")
        self.assertEqual(salida, "resumen.csv")

    def test_cantidad_incorrecta(self):
        with self.assertRaises(ValueError):
            parsear_argumentos(["ventas.csv"])

        with self.assertRaises(ValueError):
            parsear_argumentos(["ventas.csv", "resumen.csv", "extra.csv"])


if __name__ == "__main__":
    unittest.main()
