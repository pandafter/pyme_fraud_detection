from core.auth import register_user
from core.database import Session
from core.models import User


def create_test_user():
    """Crea un usuario de prueba en la base de datos"""
    test_user = {
        "username": "admin_test",
        "email": "admin@test.com",
        "password": "Admin123!",
        "role": "admin"
    }

    print("⚙️ Creando usuario de prueba...")
    success = register_user(**test_user)

    if success:
        print(f"""
        ✅ Usuario de prueba creado exitosamente!
        ----------------------------
        Username: {test_user['username']}
        Email: {test_user['email']}
        Password: {test_user['password']}
        Role: {test_user['role']}
        ----------------------------
        """)
    else:
        print("❌ Error al crear usuario de prueba")

    # Verificar que el usuario existe
    session = Session()
    try:
        user = session.query(User).filter_by(email=test_user["email"]).first()
        if user:
            print(f"Usuario encontrado en DB: ID {user.id} - {user.username}")
        else:
            print("Usuario no encontrado en la base de datos")
    finally:
        session.close()


if __name__ == "__main__":
    create_test_user()