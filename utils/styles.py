import customtkinter as ctk


class AppStyles:
    """Configuración centralizada de estilos para la aplicación de detección de fraudes"""

    # ============ Paleta de colores principal ============
    PRIMARY_COLOR = "#2E86AB"  # Azul principal
    PRIMARY_HOVER = "#1E5F7A"  # Azul oscuro (hover)
    SECONDARY_COLOR = "#A23B72"  # Morado/magenta
    DANGER_COLOR = "#F18F01"  # Naranja (alertas/errores)
    SUCCESS_COLOR = "#3BB273"  # Verde (éxito)
    WARNING_COLOR = "#FF9F1C"  # Amarillo/naranja (advertencias)

    # ============ Colores de texto ============
    TEXT_COLOR = "#2B2D42"  # Color de texto principal (casi negro)
    SECONDARY_TEXT_COLOR = "#8D99AE"  # Texto secundario (gris)
    LIGHT_TEXT = "#EDF2F4"  # Texto claro (para fondos oscuros)
    LINK_COLOR = "#F9F1C0"

    # ============ Colores de fondo ============
    BG_COLOR = "#F8F9FA"  # Color de fondo claro
    CARD_COLOR = "#FFFFFF"  # Color para tarjetas/paneles
    DARK_BG = "#2B2D42"  # Fondo oscuro

    # ============ Bordes y detalles ============
    BORDER_COLOR = "#DEE2E6"  # Color de bordes claros
    ENTRY_BORDER = "#ADB5BD"  # Borde para campos de entrada
    SEPARATOR_COLOR = "#E9ECEF"  # Color para separadores

    @staticmethod
    def configure_app():
        """Configuración global de la aplicación"""
        ctk.set_appearance_mode("System")  # Puede ser "Light", "Dark" o "System"
        ctk.set_default_color_theme("blue")

        # Establecer fuentes por defecto
        ctk.FontManager.load_font("Helvetica")  # Asegurarse que la fuente esté disponible

    # ============ Estilos para widgets específicos ============

    @classmethod
    def get_button_style(cls):
        """Estilo base para botones principales"""
        return {
            "fg_color": cls.PRIMARY_COLOR,
            "hover_color": cls.PRIMARY_HOVER,
            "text_color": "white",
            "font": ("Helvetica", 12, "bold"),
            "corner_radius": 8,
            "border_width": 0
        }

    @classmethod
    def get_secondary_button_style(cls):
        """Estilo para botones secundarios"""
        return {
            "fg_color": cls.SECONDARY_COLOR,
            "hover_color": "#7D2B57",
            "text_color": "white",
            "font": ("Helvetica", 12),
            "corner_radius": 8
        }

    @classmethod
    def get_danger_button_style(cls):
        """Estilo para botones de acción peligrosa"""
        return {
            "fg_color": cls.DANGER_COLOR,
            "hover_color": "#C46A01",
            "text_color": "white",
            "font": ("Helvetica", 12, "bold"),
            "corner_radius": 8
        }

    @classmethod
    def get_entry_style(cls):
        """Estilo para campos de entrada"""
        return {
            "border_width": 1,
            "border_color": cls.ENTRY_BORDER,
            "font": ("Helvetica", 14),
            "corner_radius": 6,
            "text_color": "black",
            "fg_color": "white"
        }

    @classmethod
    def get_card_style(cls):
        """Estilo para tarjetas/paneles"""
        return {
            "fg_color": cls.CARD_COLOR,
            "border_width": 1,
            "border_color": cls.BORDER_COLOR,
            "corner_radius": 12
        }

    @classmethod
    def get_label_style(cls, size=12, bold=False):
        """Estilo para etiquetas"""
        return {
            "font": ("Helvetica", size, "bold" if bold else ""),
            "text_color": cls.TEXT_COLOR
        }

    @classmethod
    def get_title_style(cls):
        """Estilo para títulos"""
        return {
            "font": ("Helvetica", 18, "bold"),
            "text_color": cls.TEXT_COLOR
        }

    @classmethod
    def get_subtitle_style(cls):
        """Estilo para subtítulos"""
        return {
            "font": ("Helvetica", 14),
            "text_color": cls.SECONDARY_TEXT_COLOR
        }