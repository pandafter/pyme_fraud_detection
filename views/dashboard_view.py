import customtkinter as ctk
from utils.styles import AppStyles
from tkinter import messagebox
from datetime import datetime, timedelta
from core.report_generator import ReportGenerator
from core.monitoring import TransactionMonitor


class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, logout_callback, show_transactions_callback):
        super().__init__(parent)
        self.logout_callback = logout_callback
        self.show_transactions_callback = show_transactions_callback
        self.monitor = TransactionMonitor()
        self._setup_ui()

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)

        self.welcome_label = ctk.CTkLabel(
            self,
            text="Panel de Control",
            font=("Helvetica", 18, "bold")
        )
        self.welcome_label.grid(row=0, column=0, pady=10)

        # Monitoring Section
        self.monitoring_frame = ctk.CTkFrame(self)
        self.monitoring_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        ctk.CTkLabel(
            self.monitoring_frame,
            text="Monitoreo en Tiempo Real",
            font=("Helvetica", 14, "bold")
        ).pack(pady=5)

        self.monitor_status = ctk.CTkLabel(
            self.monitoring_frame,
            text="Estado: Inactivo",
            text_color="gray"
        )
        self.monitor_status.pack()

        self.start_monitor_btn = ctk.CTkButton(
            self.monitoring_frame,
            text="Iniciar Monitoreo",
            command=self.start_monitoring,
            **AppStyles.get_button_style()
        )
        self.start_monitor_btn.pack(pady=5, padx=20, fill='x')

        self.stop_monitor_btn = ctk.CTkButton(
            self.monitoring_frame,
            text="Detener Monitoreo",
            command=self.stop_monitoring,
            state="disabled",
            fg_color=AppStyles.DANGER_COLOR,
            hover_color="#C46A01"
        )
        self.stop_monitor_btn.pack(pady=5, padx=20, fill='x')

        # 🔹 Realtime Transaction Output
        self.realtime_output = RealTimeMonitorFrame(self.monitoring_frame)
        self.realtime_output.pack(pady=10, padx=10, fill='both', expand=True)

        # Reporting Section
        self.reporting_frame = ctk.CTkFrame(self)
        self.reporting_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")

        ctk.CTkLabel(
            self.reporting_frame,
            text="Generar Reportes",
            font=("Helvetica", 14, "bold")
        ).pack(pady=5)

        self.date_frame = ctk.CTkFrame(self.reporting_frame)
        self.date_frame.pack(pady=5, fill='x', padx=10)

        ctk.CTkLabel(self.date_frame, text="Desde:").grid(row=0, column=0, padx=5)
        self.start_date_entry = ctk.CTkEntry(self.date_frame)
        self.start_date_entry.grid(row=0, column=1, padx=5)

        ctk.CTkLabel(self.date_frame, text="Hasta:").grid(row=0, column=2, padx=5)
        self.end_date_entry = ctk.CTkEntry(self.date_frame)
        self.end_date_entry.grid(row=0, column=3, padx=5)

        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        self.start_date_entry.insert(0, start_date.strftime('%Y-%m-%d'))
        self.end_date_entry.insert(0, end_date.strftime('%Y-%m-%d'))

        self.report_format = ctk.StringVar(value="pdf")
        ctk.CTkRadioButton(
            self.reporting_frame,
            text="PDF",
            variable=self.report_format,
            value="pdf"
        ).pack(pady=2)

        ctk.CTkRadioButton(
            self.reporting_frame,
            text="CSV",
            variable=self.report_format,
            value="csv"
        ).pack(pady=2)

        self.generate_report_btn = ctk.CTkButton(
            self.reporting_frame,
            text="Generar Reporte",
            command=self.generate_report,
            **AppStyles.get_button_style()
        )
        self.generate_report_btn.pack(pady=10, padx=20, fill='x')

        self.transactions_btn = ctk.CTkButton(
            self,
            text="Ver Transacciones",
            command=self._safe_show_transactions,
            **AppStyles.get_button_style()
        )
        self.transactions_btn.grid(row=3, column=0, padx=20, pady=10)

        self.logout_btn = ctk.CTkButton(
            self,
            text="Cerrar Sesión",
            command=self.logout_callback,
            fg_color=AppStyles.DANGER_COLOR,
            hover_color="#C46A01"
        )
        self.logout_btn.grid(row=4, column=0, padx=20, pady=20)

    def _safe_show_transactions(self):
        try:
            transactions_view = self.show_transactions_callback()
            if hasattr(transactions_view, 'load_transactions'):
                transactions_view.load_transactions()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar las transacciones: {str(e)}")

    def start_monitoring(self):
        try:
            self.monitor.start_monitoring(callback=self.realtime_output.add_transaction)
            self.monitor_status.configure(text="Estado: Activo", text_color="green")
            self.start_monitor_btn.configure(state="disabled")
            self.stop_monitor_btn.configure(state="normal")
            messagebox.showinfo("Monitoreo", "El monitoreo en tiempo real ha sido iniciado")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo iniciar el monitoreo: {str(e)}")

    def stop_monitoring(self):
        try:
            self.monitor.stop_monitoring()
            self.monitor_status.configure(text="Estado: Inactivo", text_color="gray")
            self.start_monitor_btn.configure(state="normal")
            self.stop_monitor_btn.configure(state="disabled")
            messagebox.showinfo("Monitoreo", "El monitoreo en tiempo real ha sido detenido")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo detener el monitoreo: {str(e)}")

    def generate_report(self):
        try:
            start_date = datetime.strptime(self.start_date_entry.get(), '%Y-%m-%d')
            end_date = datetime.strptime(self.end_date_entry.get(), '%Y-%m-%d')

            if start_date > end_date:
                messagebox.showerror("Error", "La fecha de inicio no puede ser mayor a la fecha final")
                return

            report_generator = ReportGenerator()
            report_format = self.report_format.get()

            if report_format == "pdf":
                filename = report_generator.generate_pdf_report(start_date, end_date)
            else:
                filename = report_generator.generate_csv_report(start_date, end_date)

            messagebox.showinfo("Reporte Generado",
                                f"El reporte ha sido generado exitosamente:\n{filename}")

        except ValueError:
            messagebox.showerror("Error", "Formato de fecha inválido. Use YYYY-MM-DD")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el reporte: {str(e)}")


class RealTimeMonitorFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.textbox = ctk.CTkTextbox(self, width=300, height=150)
        self.textbox.pack(expand=True, fill='both', padx=5, pady=5)
        self.textbox.configure(state="disabled")

    def add_transaction(self, transaction):
        self.textbox.configure(state="normal")

        # Mensaje formateado bonito
        message = f"""🧾 Transacción Detectada
    -----------------------------
    📅 Fecha: {transaction.date.strftime('%Y-%m-%d %H:%M:%S')}
    🆔 ID: {transaction.id}
    💰 Monto: ${transaction.amount:.2f}
    🏷️ Tipo: {transaction.transaction_type}
    🏦 Cuenta: {transaction.account_number}
    -----------------------------
    """
        self.textbox.insert("end", message)
        self.textbox.insert("end", "\n")
        self.textbox.configure(state="disabled")
        self.textbox.see("end")