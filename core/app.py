import customtkinter as ctk
from views.login_view import LoginView
from views.dashboard_view import DashboardView
from views.transactions_view import TransactionsView
from views.register_view import RegisterView
from utils.styles import AppStyles
from core.auth import login_user
from core.database import init_db


class FraudDetectionApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Detección de Fraudes - PYME")
        self.geometry("1000x700")
        AppStyles.configure_app()

        # Usuario actual
        self.current_user = None

        # Contenedor principal
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Vistas
        self.views = {
            "LoginView": LoginView(
                self.container,
                login_callback=self.handle_login,
                switch_to_register_callback=lambda: self.show_view("RegisterView")
            ),
            "RegisterView": RegisterView(
                self.container,
                switch_to_login_callback=lambda: self.show_view("LoginView")
            ),
            "DashboardView": DashboardView(
                self.container,
                logout_callback=self.handle_logout,
                show_transactions_callback=self.show_transactions_view
            )
        }

        # Configurar vistas iniciales
        for view in self.views.values():
            view.grid(row=0, column=0, sticky="nsew")

        self.show_view("LoginView")

    def show_transactions_view(self):
        """Muestra la vista de transacciones con carga dinámica"""
        if self.current_user:
            if "TransactionsView" not in self.views:
                self.views["TransactionsView"] = TransactionsView(
                    self.container,
                    go_back_callback=lambda: self.show_view("DashboardView"),
                    user_id=self.current_user.id
                )
                self.views["TransactionsView"].grid(row=0, column=0, sticky="nsew")

            self.views["TransactionsView"].load_transactions()
            self.show_view("TransactionsView")

    def show_view(self, view_name):
        """Muestra la vista especificada"""
        if view_name in self.views:
            self.views[view_name].tkraise()

    def handle_login(self, email, password):
        """Maneja el proceso de autenticación"""
        user = login_user(email, password)
        if user:
            self.current_user = user
            self.views["DashboardView"].welcome_label.configure(
                text=f"Bienvenido, {user.username} ({user.role})"
            )
            self.show_view("DashboardView")

    def handle_logout(self):
        """Maneja el cierre de sesión"""
        self.current_user = None

        # Limpiar vista de login
        self.views["LoginView"].email_entry.delete(0, "end")
        self.views["LoginView"].password_entry.delete(0, "end")

        # Eliminar vista de transacciones si existe
        if "TransactionsView" in self.views:
            self.views["TransactionsView"].destroy()
            del self.views["TransactionsView"]

        self.show_view("LoginView")


if __name__ == "__main__":
    init_db()  # Inicializar base de datos
    app = FraudDetectionApp()
    app.mainloop()