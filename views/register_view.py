import customtkinter as ctk
from tkinter import messagebox
from core.auth import register_user
from utils.styles import AppStyles
import re

class RegisterView(ctk.CTkFrame):
    def __init__(self, parent, switch_to_login_callback):
        super().__init__(parent)
        self.switch_to_login_callback = switch_to_login_callback
        self._setup_ui()

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)

        # Frame principal para centrar contenido
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=1, column=0, sticky="nsew", pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Título
        title = ctk.CTkLabel(
            self.main_frame,
            text="Registro de Usuario",
            font=("Helvetica", 20, "bold")
        )
        title.grid(row=0, column=0, pady=(0, 20))

        # Formulario
        self.form_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.form_frame.grid(row=1, column=0, sticky="nsew")
        self.form_frame.grid_columnconfigure(0, weight=1)

        # Nombre de usuario
        self.username_entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="Nombre de usuario",
            **AppStyles.get_entry_style()
        )
        self.username_entry.grid(row=0, column=0, padx=20, pady=10, sticky="ew")

        # Correo electrónico
        self.email_entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="Correo electrónico",
            **AppStyles.get_entry_style()
        )
        self.email_entry.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        # Contraseña
        self.password_entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="Contraseña",
            show="*",
            **AppStyles.get_entry_style()
        )
        self.password_entry.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        # Botón de registrar
        register_btn = ctk.CTkButton(
            self.form_frame,
            text="Registrarse",
            command=self._platform_register,
            **AppStyles.get_button_style()
        )
        register_btn.grid(row=3, column=0, padx=20, pady=20, sticky="ew")

        # Botón para volver al login
        back_btn = ctk.CTkButton(
            self,
            text="¿Ya tienes cuenta? Inicia sesión",
            command=self.switch_to_login_callback,
            fg_color="transparent",
            text_color=AppStyles.LINK_COLOR,
            hover_color=AppStyles.SECONDARY_COLOR
        )
        back_btn.grid(row=5, column=0, padx=20, pady=(0, 20))

        # Footer
        self.footer_label = ctk.CTkLabel(
            self,
            text="© 2025 Sistema de Detección de Fraudes - Versión 1.0",
            font=("Helvetica", 10),
            text_color=AppStyles.SECONDARY_TEXT_COLOR
        )
        self.footer_label.grid(row=6, column=0, pady=10)

    def _platform_register(self):
        username = self.username_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()

        if not username or not email or not password:
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        # Validación de seguridad de contraseña
        if len(password) < 8:
            messagebox.showerror("Contraseña débil", "La contraseña debe tener al menos 8 caracteres.")
            return
        if not re.search(r"[A-Z]", password):
            messagebox.showerror("Contraseña débil", "La contraseña debe incluir al menos una letra mayúscula.")
            return
        if not re.search(r"[a-z]", password):
            messagebox.showerror("Contraseña débil", "La contraseña debe incluir al menos una letra minúscula.")
            return
        if not re.search(r"[0-9]", password):
            messagebox.showerror("Contraseña débil", "La contraseña debe incluir al menos un número.")
            return
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            messagebox.showerror("Contraseña débil", "La contraseña debe incluir al menos un carácter especial.")
            return

        success = register_user(username, email, password)

        if success:
            messagebox.showinfo("Registro exitoso", "Usuario creado correctamente. Inicia sesión.")
            self.switch_to_login_callback()
        else:
            messagebox.showerror("Error", "No se pudo registrar el usuario. Revisa la consola.")