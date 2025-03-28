from core.auth import register_user, login_user
from core.models import Transaction
from core.database import Session, init_db
from datetime import datetime
import logging

# Configurar logging para ver más detalles
logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    # Inicializar base de datos
    init_db()

    try:
        # Registrar usuario admin
        """registro = register_user("admin", "admin@example.com", "Admin123!", "admin")

        if not registro:
            print("❌ No se pudo registrar el usuario admin")
            exit(1)"""

        # Iniciar sesión
        user = login_user("admin@example.com", "Admin123!")

        if user:
            print(f"✅ Bienvenido, {user.username} (Rol: {user.role})!")

            # Crear transacción
            session = Session()
            try:
                new_transaction = Transaction(
                    user_id=user.id,
                    amount=500000,
                    date=datetime.now(),
                    payment_method="card"
                )
                session.add(new_transaction)
                session.commit()
                print("✅ Transacción creada exitosamente.")
            except Exception as e:
                session.rollback()
                print(f"❌ Error al crear transacción: {e}")
            finally:
                session.close()
        else:
            print("❌ Credenciales incorrectas.")

    except Exception as e:
        print(f"❌ Error inesperado: {e}")