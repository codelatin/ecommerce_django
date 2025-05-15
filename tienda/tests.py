from django.test import TestCase
from django.core.management import call_command
from carrito.models import (
    Carrito,
    Carrito_Item
)
from categorias.models import (
    Categoria,
) 
from tienda.models import (
    Producto,
    Variacion
)

class SeedCommandTest(TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Ejecuta el comando personalizado 'seed' para poblar la base de datos
        antes de que se ejecuten los tests. Es equivalente a correr
        `python manage.py seed` desde la terminal.
        """
        call_command("seed")
        super().setUpClass()

    def test_populates_productos_table(self):
        """
        Verifica que el comando 'seed' haya creado exactamente 8 productos,
        y que sus nombres coincidan con los esperados.
        """
        producto_count = Producto.objects.count()
        self.assertEqual(producto_count, 8)

        nombres = set(Producto.objects.values_list('nombre_producto', flat=True))
        nombres_esperados = {
            "Gorra wetscol",
            "Gorra Python-Estampada",
            "Zapatillas para Hombre",
            "Zapatillas para hombre latinShop",
            "Saco Django",
            "Saco Codelatin",
            "Camiseta Latinshop Jaguar",
            "Camiseta azul Sencilla",    
        }
        self.assertEqual(nombres, nombres_esperados)

    def test_populates_categorias_table(self):
        """
        Verifica que el comando 'seed' haya creado exactamente 4 categorías,
        y que sus nombres coincidan con los esperados.
        """
        categoria_count = Categoria.objects.count()
        self.assertEqual(categoria_count, 4)

        nombres = set(Categoria.objects.values_list('nombre_categoria', flat=True))
        nombres_esperados = {
            "Gorras",
            "Sacos",
            "Buzos",
            "Tennis"
        }
        self.assertEqual(nombres, nombres_esperados)

    def test_populates_variaciones_table(self):
        """
        Verifica que el comando 'seed' haya creado exactamente 8 variaciones
        de productos.
        """
        variacion_count = Variacion.objects.count()
        self.assertEqual(variacion_count, 8)

    def test_populates_carritos_table(self):
        """
        Verifica que el comando 'seed' haya creado exactamente 17 carritos.
        """
        carrito_count = Carrito.objects.count()
        self.assertEqual(carrito_count, 17)

    def test_populates_carrito_items_table(self):
        """
        Verifica que el comando 'seed' haya creado exactamente 10 ítems
        dentro de carritos.
        """
        carrito_item_count = Carrito_Item.objects.count()
        self.assertEqual(carrito_item_count, 10)
