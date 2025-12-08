import os
import django
import getpass

# Configura Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto.settings')
django.setup()

from app2.models import User_admin
from django.contrib.auth.hashers import make_password

def registrar_usuario_console():
    # Solicita datos por consola en lugar de usar Tkinter
    nombre = input("Nombre: ").strip()
    if not nombre:
        print("Error: Nombre es obligatorio.")
        return

    password = getpass.getpass("Contraseña: ").strip()
    if not password:
        print("Error: Contraseña es obligatoria.")
        return

    email = input("Email (opcional): ").strip()
    telefono = input("Teléfono (opcional): ").strip()

    if User_admin.objects.filter(nombre=nombre).exists():
        print("Error: El nombre de usuario ya existe.")
        return

    if email and User_admin.objects.filter(email=email).exists():
        print("Error: El email ya está registrado.")
        return

    hashed_password = make_password(password)
    user = User_admin(
        nombre=nombre,
        password=hashed_password,
        email=email if email else None,
        telefono=telefono if telefono else None
    )
    user.save()
    print("Usuario registrado correctamente.")

def main():
    while True:
        registrar_usuario_console()
        again = input("Registrar otro usuario? [y/N]: ").strip().lower()
        if again != 'y':
            break

if __name__ == '__main__':
    main()