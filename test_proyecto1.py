"""
Pruebas unitarias para proyecto1.py

Ejecutar con:
    python3 -m unittest test_proyecto1.py -v
"""

import unittest
import os
import tempfile

from proyecto1 import (
    leer_lista_desde_archivo,
    calcular_promedio,
    parsear_argumentos,
)


class TestLeerListaDesdeArchivo(unittest.TestCase):

    def setUp(self):
        # Crea un archivo temporal para cada prueba
        self.tmpdir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmpdir.cleanup()

    def _crear_archivo(self, contenido):
        ruta = os.path.join(self.tmpdir.name, "datos.txt")
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(contenido)
        return ruta

    def test_lectura_basica_separado_por_espacios(self):
        ruta = self._crear_archivo("10 20 30 40 50")
        self.assertEqual(leer_lista_desde_archivo(ruta), [10, 20, 30, 40, 50])

    def test_lectura_separado_por_saltos_de_linea(self):
        ruta = self._crear_archivo("1\n2\n3\n4\n")
        self.assertEqual(leer_lista_desde_archivo(ruta), [1, 2, 3, 4])

    def test_lectura_mixta_espacios_y_saltos(self):
        ruta = self._crear_archivo("1 2\n3   4\n5")
        self.assertEqual(leer_lista_desde_archivo(ruta), [1, 2, 3, 4, 5])

    def test_archivo_vacio(self):
        ruta = self._crear_archivo("")
        self.assertEqual(leer_lista_desde_archivo(ruta), [])

    def test_numeros_negativos_en_archivo(self):
        ruta = self._crear_archivo("-5 10 -3 8")
        self.assertEqual(leer_lista_desde_archivo(ruta), [-5, 10, -3, 8])

    def test_archivo_inexistente_lanza_excepcion(self):
        with self.assertRaises(FileNotFoundError):
            leer_lista_desde_archivo(os.path.join(self.tmpdir.name, "no_existe.txt"))

    def test_valor_no_entero_lanza_excepcion(self):
        ruta = self._crear_archivo("1 2 tres 4")
        with self.assertRaises(ValueError):
            leer_lista_desde_archivo(ruta)

    def test_valor_flotante_lanza_excepcion(self):
        ruta = self._crear_archivo("1 2 3.5 4")
        with self.assertRaises(ValueError):
            leer_lista_desde_archivo(ruta)


class TestCalcularPromedio(unittest.TestCase):

    def setUp(self):
        self.lista = [10, 20, 30, 40, 50, 60]  # longitud 6, índices 0..5

    def test_rango_normal(self):
        self.assertEqual(calcular_promedio(self.lista, 1, 3), 30.0)

    def test_rango_de_un_solo_elemento(self):
        self.assertEqual(calcular_promedio(self.lista, 2, 2), 30.0)

    def test_rango_completo(self):
        self.assertAlmostEqual(calcular_promedio(self.lista, 0, 5), 35.0)

    def test_n2_menor_que_n1_devuelve_cero(self):
        self.assertEqual(calcular_promedio(self.lista, 4, 1), 0)

    def test_n1_mayor_que_longitud_devuelve_cero(self):
        self.assertEqual(calcular_promedio(self.lista, 100, 200), 0)

    def test_n1_igual_a_longitud_devuelve_cero(self):
        # longitud = 6, índices válidos 0..5 -> n1 = 6 está fuera de rango
        self.assertEqual(calcular_promedio(self.lista, 6, 10), 0)

    def test_n2_mayor_que_longitud_se_trunca(self):
        # Debe calcular desde la posición 2 hasta la última posición (5)
        self.assertEqual(calcular_promedio(self.lista, 2, 100), 45.0)

    def test_n1_cero_n2_cero(self):
        self.assertEqual(calcular_promedio(self.lista, 0, 0), 10.0)

    def test_lista_vacia_devuelve_cero(self):
        self.assertEqual(calcular_promedio([], 0, 3), 0)

    def test_n1_negativo_lanza_excepcion(self):
        with self.assertRaises(ValueError):
            calcular_promedio(self.lista, -1, 3)

    def test_n2_negativo_lanza_excepcion(self):
        with self.assertRaises(ValueError):
            calcular_promedio(self.lista, 1, -3)


class TestParsearArgumentos(unittest.TestCase):

    def test_argumentos_validos(self):
        ruta, n1, n2 = parsear_argumentos(["datos.txt", "2", "5"])
        self.assertEqual(ruta, "datos.txt")
        self.assertEqual(n1, 2)
        self.assertEqual(n2, 5)

    def test_cantidad_incorrecta_de_argumentos(self):
        with self.assertRaises(ValueError):
            parsear_argumentos(["datos.txt", "2"])

    def test_n1_no_entero(self):
        with self.assertRaises(ValueError):
            parsear_argumentos(["datos.txt", "dos", "5"])

    def test_n2_no_entero(self):
        with self.assertRaises(ValueError):
            parsear_argumentos(["datos.txt", "2", "cinco"])

    def test_n1_negativo(self):
        with self.assertRaises(ValueError):
            parsear_argumentos(["datos.txt", "-1", "5"])

    def test_n2_negativo(self):
        with self.assertRaises(ValueError):
            parsear_argumentos(["datos.txt", "1", "-5"])


if __name__ == "__main__":
    unittest.main()
