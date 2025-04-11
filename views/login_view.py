import customtkinter as ctk
from utils.styles import AppStyles
from tkinter import messagebox
import re


class LoginView(ctk.CTkFrame):
    def __init__(self, parent, login_callback, switch_to_register_callback):
        super().__init__(parent)
        self.login_callback = login_callback
        self.switch_to_register_callback = switch_to_register_callback
        self._setup_ui()

    def _setup_ui(self):
        # Configuración de la vista
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)

        # Frame principal para centrar contenido
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=1, column=0, sticky="nsew", pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Logo o icono
        self.logo_label = ctk.CTkLabel(
            self.main_frame,
            text="🔒",
            font=("Arial", 48),
            text_color=AppStyles.PRIMARY_COLOR
        )
        self.logo_label.grid(row=0, column=0, pady=(0, 20))

        # Título
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="Detección de Fraudes",
            font=("Helvetica", 20, "bold"),
            text_color="white"
        )
        self.title_label.grid(row=1, column=0, pady=(0, 10))

        # Subtítulo
        self.subtitle_label = ctk.CTkLabel(
            self.main_frame,
            text="Inicie sesión con sus credenciales",
            font=("Helvetica", 12),
            text_color=AppStyles.SECONDARY_TEXT_COLOR
        )
        self.subtitle_label.grid(row=2, column=0, pady=(0, 20))

        # Formulario en un frame separado
        self.form_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.form_frame.grid(row=3, column=0, sticky="nsew")
        self.form_frame.grid_columnconfigure(0, weight=1)

        # Campo de email con validación
        self.email_label = ctk.CTkLabel(
            self.form_frame,
            text="Correo electrónico",
            font=("Helvetica", 12),
            anchor="w"
        )
        self.email_label.grid(row=0, column=0, padx=20, pady=(0, 5), sticky="ew")

        self.email_entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="usuario@example.com",
            **AppStyles.get_entry_style()
        )
        self.email_entry.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="ew")
        self.email_entry.bind("<FocusOut>", self._validate_email)

        # Campo de contraseña con toggle de visibilidad
        self.password_label = ctk.CTkLabel(
            self.form_frame,
            text="Contraseña",
            font=("Helvetica", 12),
            anchor="w"
        )
        self.password_label.grid(row=2, column=0, padx=20, pady=(0, 5), sticky="ew")

        self.password_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        self.password_frame.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.password_frame.grid_columnconfigure(0, weight=1)

        self.password_entry = ctk.CTkEntry(
            self.password_frame,
            placeholder_text="*********",
            show="*",
            **AppStyles.get_entry_style()
        )
        self.password_entry.grid(row=0, column=0, sticky="ew")

        self.show_password = ctk.CTkButton(
            self.password_frame,
            text="👁️",
            width=30,
            command=self._toggle_password_visibility,
            fg_color="transparent",
            hover_color=AppStyles.SECONDARY_COLOR
        )
        self.show_password.grid(row=0, column=1, padx=(5, 0))

        # Botón de inicio de sesión
        self.login_button = ctk.CTkButton(
            self.form_frame,
            text="Iniciar Sesión",
            command=self._on_login,
            **AppStyles.get_button_style()
        )
        self.login_button.grid(row=4, column=0, padx=20, pady=(10, 0), sticky="ew")
        self.login_button.bind("<Return>", lambda e: self._on_login())

        # Enlace a registro
        self.register_link = ctk.CTkLabel(
            self,
            text="¿No tienes cuenta? Regístrate aquí",
            font=("Helvetica", 12),
            text_color=AppStyles.LINK_COLOR,
            cursor="hand2"
        )
        self.register_link.grid(row=5, column=0, pady=(0, 10))
        self.register_link.bind("<Button-1>", lambda e: self.switch_to_register_callback())

        # Footer
        self.footer_label = ctk.CTkLabel(
            self,
            text="© 2025 Sistema de Detección de Fraudes - Versión 1.0",
            font=("Helvetica", 10),
            text_color=AppStyles.SECONDARY_TEXT_COLOR
        )
        self.footer_label.grid(row=6, column=0, pady=10)

    def _toggle_password_visibility(self):
        """Alternar visibilidad de la contraseña"""
        current_show = self.password_entry.cget("show")
        self.password_entry.configure(show="" if current_show == "*" else "*")
        self.show_password.configure(text="👁️" if current_show == "*" else "🔒")

    def _validate_email(self, event=None):
        """Validación básica de formato de email"""
        email = self.email_entry.get()
        if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            self.email_entry.configure(border_color=AppStyles.DANGER_COLOR)
            return False
        self.email_entry.configure(border_color=AppStyles.ENTRY_BORDER)
        return True

    def _on_login(self):
        """Manejar el evento de inicio de sesión"""
        email = self.email_entry.get()
        password = self.password_entry.get()

        if not email:
            messagebox.showerror("Error", "Por favor ingrese su correo electrónico")
            self.email_entry.focus()
            return

        if not self._validate_email():
            messagebox.showerror("Error", "Por favor ingrese un correo electrónico válido")
            self.email_entry.focus()
            return

        if not password:
            messagebox.showerror("Error", "Por favor ingrese su contraseña")
            self.password_entry.focus()
            return

        self.login_callback(email, password)