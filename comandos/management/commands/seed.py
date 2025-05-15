from django.core.management.base import BaseCommand
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

class Command(BaseCommand):
    help = "Seeds database"

    def handle(self, *args, **options):
        self.create_categorias()
        self.create_productos()
        self.create_variaciones()
        self.create_carritos()
        self.create_carrito_items()

        self.stdout.write(
            self.style.SUCCESS("comando seeder ejecutado")
        )

    def helper_show_exception(self, instance_name:str, e: Exception):
        self.stdout.write(
            self.style.ERROR(f"Error al Registrar {instance_name}: \n{e}")
        )
        self.stdout.write(
            self.style.WARNING(f"Pasando a siguiente registro...")
        )

    def create_categorias(self) -> None:
        creation_count = 0
        try:
            for categoria in CATEGORIAS:
                Categoria.objects.create(**categoria)
                creation_count += 1

        except Exception as e:
            self.helper_show_exception(instance_name="categorias", e=e)
        finally:
            if creation_count:
                self.stdout.write(
                    self.style.SUCCESS(f"Registradas {creation_count} categorias")
                )

    def create_productos(self) -> None:
        creation_count = 0
        try:
            for producto in PRODUCTOS:
                categoria_id = producto["categoria"]
                producto["categoria"] = Categoria.objects.get(id=categoria_id)
                Producto.objects.create(**producto)
                creation_count += 1
           
        except Exception as e:
            self.helper_show_exception(instance_name="productos", e=e)
        finally:
            if creation_count:
                self.stdout.write(
                    self.style.SUCCESS(f"Registrados {creation_count} productos")
                )


    def create_variaciones(self) -> None:
        creation_count = 0
        try:
            for variacion in VARIACIONES:
                producto_id = variacion["producto"]
                variacion["producto"] = Producto.objects.get(id=producto_id)
                Variacion.objects.create(**variacion)
                creation_count += 1

        except Exception as e:
            self.helper_show_exception(instance_name="variaciones", e=e)
        finally:
            if creation_count:
                self.stdout.write(
                    self.style.SUCCESS(f"Registradas {creation_count} variaciones")
                )

    def create_carritos(self) -> None:
        try:
            creation_count = 0
            for carrito in CARRITOS:
                Carrito.objects.create(**carrito)
                creation_count += 1

            self.stdout.write(
                self.style.SUCCESS(f"Registrados {creation_count} carritos")
            )
        except Exception as e:
            self.helper_show_exception(instance_name="variaciones", e=e)

    def create_carrito_items(self) -> None:
        creation_count = 0
        try:
            for item in CARRITO_ITEMS:
                producto = Producto.objects.get(id=item["producto"])
                carrito = Carrito.objects.get(id=item["carrito"])
                variaciones_ids = item.pop("variaciones", [])

                item = Carrito_Item.objects.create(
                    producto=producto,
                    carrito=carrito,
                    cantidad=item["cantidad"],
                    is_active=item["is_active"]
                )

                # adding ManyToMany relationships
                if variaciones_ids:
                    item.variaciones.set(Variacion.objects.filter(id__in=variaciones_ids))

                creation_count += 1

        except Exception as e:
            self.helper_show_exception(instance_name="carrito_items", e=e)
        finally:
            if creation_count:
                self.stdout.write(
                    self.style.SUCCESS(f"Registrados {creation_count} items en carrito")
                )


CATEGORIAS = [
    {
        "nombre_categoria": "Sacos",
        "slug": "sacos",
        "descripcion": "Sacos hechos con Algodon  100% Colombiano",
        "imagen_categoria": "fotos/mis_categorias/sacos.jpg"
    },
    {
        "nombre_categoria": "Buzos",
        "slug": "buzos",
        "descripcion": "Busos personalizados 100% Colombianos",
        "imagen_categoria": "fotos/mis_categorias/camiseta.jpg"
    },
    {
        "nombre_categoria": "Tennis",
        "slug": "tennis",
        "descripcion": "Zapatillas o tennis personalizadas para Hombre",
        "imagen_categoria": "fotos/mis_categorias/tennis.jpg"
    },
    {
        "nombre_categoria": "Gorras",
        "slug": "gorras",
        "descripcion": "Gorras Colores Neon personalizadas Para Hombres",
        "imagen_categoria": "fotos/mis_categorias/gorras.jpg"
    }
]

PRODUCTOS = [
    {
        "nombre_producto": "Gorra wetscol",
        "slug": "gorra-python",
        "descripcion": "Gorra con materiales Neon 2025",
        "precio": 50000,
        "imagen": "fotos/mis_productos/gorra_1.jpg",
        "stock": 0,
        "esta_disponible": True,
        "categoria": 4,
        "fecha_creacion": "2025-01-28T23:23:06.764Z",
        "fecha_modificacion": "2025-01-28T23:23:06.764Z"
    }
    ,
    {
        "nombre_producto": "Gorra Python-Estampada",
        "slug": "gorra-python-estampada",
        "descripcion": "Gorra Python 2025 Personalizada",
        "precio": 80000,
        "imagen": "fotos/mis_productos/gorra_2.jpg",
        "stock": 10,
        "esta_disponible": True,
        "categoria": 4,
        "fecha_creacion": "2025-01-28T23:24:12.209Z",
        "fecha_modificacion": "2025-01-28T23:24:12.209Z"
    }
    ,
    {
        "nombre_producto": "Zapatillas para Hombre",
        "slug": "zapatillas-para-hombre",
        "descripcion": "Zapatillas Para Hombre Color Neon",
        "precio": 120000,
        "imagen": "fotos/mis_productos/tennis1.jpg",
        "stock": 21,
        "esta_disponible": True,
        "categoria": 3,
        "fecha_creacion": "2025-01-28T23:25:16.571Z",
        "fecha_modificacion": "2025-01-28T23:25:16.571Z"
    }
    ,
    {
        "nombre_producto": "Zapatillas para hombre latinShop",
        "slug": "zapatillas-para-hombre-latinshop",
        "descripcion": "Zapatillas personalizadas para hombre",
        "precio": 150000,
        "imagen": "fotos/mis_productos/adidas.jpg",
        "stock": 23,
        "esta_disponible": True,
        "categoria": 3,
        "fecha_creacion": "2025-01-28T23:26:49.786Z",
        "fecha_modificacion": "2025-01-28T23:26:49.786Z"
    }
    ,
    {
        "nombre_producto": "Saco Django",
        "slug": "saco-django",
        "descripcion": "Saco Personalizado Logo Django 2025",
        "precio": 90000,
        "imagen": "fotos/mis_productos/saco2.jpg",
        "stock": 13,
        "esta_disponible": True,
        "categoria": 1,
        "fecha_creacion": "2025-01-28T23:27:50.346Z",
        "fecha_modificacion": "2025-01-28T23:27:50.346Z"
    }
    ,
    {
        "nombre_producto": "Saco Codelatin",
        "slug": "saco-codelatin",
        "descripcion": "Saco Personalizado Codelatin",
        "precio": 90000,
        "imagen": "fotos/mis_productos/saco1.jpg",
        "stock": 32,
        "esta_disponible": True,
        "categoria": 1,
        "fecha_creacion": "2025-01-28T23:28:29.814Z",
        "fecha_modificacion": "2025-01-28T23:28:29.814Z"
    }
    ,
    {
        "nombre_producto": "Camiseta Latinshop Jaguar",
        "slug": "camiseta-latinshop-jaguar",
        "descripcion": "Camiseta con estampado animal",
        "precio": 85000,
        "imagen": "fotos/mis_productos/buso2.jpg",
        "stock": 11,
        "esta_disponible": True,
        "categoria": 2,
        "fecha_creacion": "2025-01-28T23:29:24.767Z",
        "fecha_modificacion": "2025-01-28T23:29:24.767Z"
    }
    ,
    {
        "nombre_producto": "Camiseta azul Sencilla",
        "slug": "camiseta-azul-sencilla",
        "descripcion": "Camiseta Azul de algodon",
        "precio": 65000,
        "imagen": "fotos/mis_productos/buso1.jpg",
        "stock": 23,
        "esta_disponible": True,
        "categoria": 2,
        "fecha_creacion": "2025-01-28T23:30:12.354Z",
        "fecha_modificacion": "2025-01-28T23:30:12.355Z"
    }
]

VARIACIONES = [
    {
        "producto": 5,
        "variacion_categoria": "color",
        "valor_variacion": "Azul",
        "is_active": True,
        "fecha_creacion": "2025-02-20T17:33:56.857Z"
    },
    {
        "producto": 5,
        "variacion_categoria": "color",
        "valor_variacion": "Negro",
        "is_active": True,
        "fecha_creacion": "2025-02-20T17:34:41.496Z"
    },
    {
        "producto": 5,
        "variacion_categoria": "color",
        "valor_variacion": "Gris",
        "is_active": True,
        "fecha_creacion": "2025-02-20T17:35:04.156Z"
    },
    {
        "producto": 5,
        "variacion_categoria": "talla",
        "valor_variacion": "Grande",
        "is_active": True,
        "fecha_creacion": "2025-02-22T02:28:08.789Z"
    },
    {
        "producto": 5,
        "variacion_categoria": "talla",
        "valor_variacion": "Mediana",
        "is_active": True,
        "fecha_creacion": "2025-02-22T02:28:25.374Z"
    },
    {
        "producto": 5,
        "variacion_categoria": "talla",
        "valor_variacion": "Pequeña",
        "is_active": True,
        "fecha_creacion": "2025-02-22T02:28:50.318Z"
    },
    {
        "producto": 3,
        "variacion_categoria": "color",
        "valor_variacion": "Azul",
        "is_active": True,
        "fecha_creacion": "2025-03-03T15:10:01.256Z"
    },
    {
        "producto": 3,
        "variacion_categoria": "talla",
        "valor_variacion": "Mediana",
        "is_active": True,
        "fecha_creacion": "2025-03-05T01:36:45.966Z"
    }
]

CARRITOS = [
    {
        "id_carrito": "qpmz0j8xre63x1tnze2rwrnh3e14b1w8",
        "fecha_agregado": "2025-02-02"
    },
    {
        "id_carrito": "ms3pjmr7jull21wxl8dp1vdkd17j5418",
        "fecha_agregado": "2025-02-15"
    },
    {
        "id_carrito": "muawzs681v0655qszfsnrtb8ui07hp1v",
        "fecha_agregado": "2025-02-22"
    },
    {
        "id_carrito": "dc26c5sy9lhq3zzuz1djy6galh21breq",
        "fecha_agregado": "2025-02-27"
    },
    {
        "id_carrito": "z53i1bidx0vdutr8ame0jmct3o0wpxl1",
        "fecha_agregado": "2025-03-04"
    },
    {
        "id_carrito": "jvhkkv84566vm5xi8vozi19fqo2z5td3",
        "fecha_agregado": "2025-03-05"
    },
    {
        "id_carrito": "4n16vdo7418vr1ougrw64rvylahsgu2p",
        "fecha_agregado": "2025-03-09"
    },
    {
        "id_carrito": "qo3bjgtuloqmmfjxueo6rdi0yj7aymb5",
        "fecha_agregado": "2025-04-04"
    },
    {
        "id_carrito": "mckjlo4jmzdq7tgxygfyz8uqkbrf6a8i",
        "fecha_agregado": "2025-04-06"
    },
    {
        "id_carrito": "7erlz2b51czwza2h4y5qt78rytrf7fbg",
        "fecha_agregado": "2025-04-06"
    },
    {
        "id_carrito": "w9bapg89y3986k7h03kv6zmz0d4h7r3k",
        "fecha_agregado": "2025-05-05"
    },
    {
        "id_carrito": "d2ypmxnmago9sos0oj1q5oszhsfame5a",
        "fecha_agregado": "2025-05-05"
    },
    {
        "id_carrito": "1gomkdh6rmddz410968z2j1meub62giv",
        "fecha_agregado": "2025-05-05"
    },
    {
        "id_carrito": "7p0nk4o1bcngjkgp2efypoja2ae67nw4",
        "fecha_agregado": "2025-05-05"
    },
    {
        "id_carrito": "9wt3y2350nywhm6lmrj4k12czw9to5z8",
        "fecha_agregado": "2025-05-05"
    },
    {
        "id_carrito": "hupj2ibnjeug4am6ev9ovnwx14sds2fq",
        "fecha_agregado": "2025-05-05"
    },
    {
        "id_carrito": "sogia8gec3xn9xv4eav1zv1yhopx0aim",
        "fecha_agregado": "2025-05-14"
    }

]

CARRITO_ITEMS = [
    {
        "producto": 7,
        "carrito": 1,
        "cantidad": 2,
        "is_active": True,
        "variaciones": []
    },
    {
        "producto": 4,
        "carrito": 1,
        "cantidad": 1,
        "is_active": True,
        "variaciones": []
    },
    {
        "producto": 3,
        "carrito": 2,
        "cantidad": 2,
        "is_active": True,
        "variaciones": []
    },
    {
        "producto": 5,
        "carrito": 4,
        "cantidad": 3,
        "is_active": True,
        "variaciones": [
        6
        ]
    },
    {
        "producto": 5,
        "carrito": 4,
        "cantidad": 3,
        "is_active": True,
        "variaciones": [
        5
        ]
    },
    {
        "producto": 5,
        "carrito": 5,
        "cantidad": 1,
        "is_active": True,
        "variaciones": [
        5
        ]
    },
    {
        "producto": 5,
        "carrito": 6,
        "cantidad": 2,
        "is_active": True,
        "variaciones": [
        6
        ]
    },
    {
        "producto": 3,
        "carrito": 7,
        "cantidad": 1,
        "is_active": True,
        "variaciones": [
        8
        ]
    },
    {
        "producto": 5,
        "carrito": 7,
        "cantidad": 1,
        "is_active": True,
        "variaciones": [
        4
        ]
    },
    {
        "producto": 5,
        "carrito": 8,
        "cantidad": 3,
        "is_active": True,
        "variaciones": [
        4
        ]
    }
]