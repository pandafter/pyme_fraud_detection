from sqlalchemy.exc import SQLAlchemyError
from core.database import Session
from core.models import User
from utils.security import encrypt_password, verify_password


def register_user(username: str, email: str, password: str, role: str = 'user') -> bool | None:
    session = Session()
    try:
        # Verificar si el usuario o email ya existen
        existing_user = session.query(User).filter(
            (User.email == email) | (User.username == username)
        ).first()

        if existing_user:
            error_msg = "❌ Error: "
            if existing_user.email == email:
                error_msg += f"El email {email} ya está registrado"
            else:
                error_msg += f"El nombre de usuario {username} ya existe"
            print(error_msg)
            return False

        # Crear y guardar el nuevo usuario
        new_user = User(
            username=username,
            email=email,
            password_hash=encrypt_password(password),
            role=role
        )
        session.add(new_user)
        session.commit()
        print(f"✅ Usuario {username} registrado exitosamente")
        return True

    except SQLAlchemyError as e:
        session.rollback()
        print(f"❌ Error de base de datos al registrar usuario: {str(e)}")
        return False
    except Exception as e:
        session.rollback()
        print(f"❌ Error inesperado al registrar usuario: {str(e)}")
        return False
    finally:
        session.close()


def login_user(email: str, password: str) -> User | None:
    session = Session()
    try:
        user = session.query(User).filter_by(email=email).first()

        if user and verify_password(password, user.password_hash):
            print(f"✅ Sesión iniciada, Bienvenido: {user.email}")
            return user

        print("❌ Credenciales inválidas")
        return None

    except SQLAlchemyError as e:
        print(f"❌ Error de base de datos al iniciar sesión: {str(e)}")
        return None
    finally:
        session.close()