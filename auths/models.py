from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class MiAdministradorCuentas(BaseUserManager):
    def create_user(self, nombre, apellido, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El usuario debe tener una dirección de correo electrónico")
        if not username:
            raise ValueError("El usuario debe tener un Nombre de Usuario")
        
        usuario = self.model(
            email=self.normalize_email(email),
            username=username,
            nombre=nombre,
            apellido=apellido,
            **extra_fields
        )
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario
    
    def create_superuser(self, nombre, apellido, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_admin", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superadmin", True)

        return self.create_user(
            nombre=nombre, apellido=apellido, username=username, email=email, password=password, **extra_fields
        )



class Auth(AbstractBaseUser, PermissionsMixin):  # Agrega PermissionsMixin
    nombre = models.CharField(max_length=50)
    apellido= models.CharField(max_length=50)
    username= models.CharField(max_length=50, unique=True)
    email= models.EmailField(max_length=100, unique=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)


    # requeridos
    fecha_registro = models.DateTimeField(auto_now_add=True)
    ultimo_login = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)  # Cambia a True para permitir inicios de sesión
    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'nombre', 'apellido']

    objects = MiAdministradorCuentas()

    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True
