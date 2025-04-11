from core.app import FraudDetectionApp
from core.database import init_db

def main():
    init_db()  # Inicializar base de datos
    app = FraudDetectionApp()
    app.mainloop()

if __name__ == "__main__":
    main()