import customtkinter as ctk
from tkinter import ttk
from datetime import datetime
from utils.styles import AppStyles
from core.fraud_detection import FraudDetector


class TransactionsView(ctk.CTkFrame):
    def __init__(self, parent, go_back_callback, user_id):
        super().__init__(parent)
        self.go_back_callback = go_back_callback
        self.user_id = user_id
        self.fraud_detector = FraudDetector()
        self._setup_ui()
        self.load_transactions()

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="Gestión de Transacciones",
            font=("Helvetica", 16, "bold")
        )
        self.title_label.pack(side="left")

        self.back_button = ctk.CTkButton(
            self.header_frame,
            text="Volver",
            command=self.go_back_callback,
            width=100,
            fg_color=AppStyles.SECONDARY_COLOR,
            hover_color="#7D2B54"
        )
        self.back_button.pack(side="right")

        self.tree_frame = ctk.CTkFrame(self)
        self.tree_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.tree_frame.grid_columnconfigure(0, weight=1)
        self.tree_frame.grid_rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=("id", "amount", "date", "method", "status"),
            show="headings",
            selectmode="browse"
        )

        self.tree.heading("id", text="ID")
        self.tree.heading("amount", text="Monto")
        self.tree.heading("date", text="Fecha")
        self.tree.heading("method", text="Método")
        self.tree.heading("status", text="Estado")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("amount", width=100, anchor="e")
        self.tree.column("date", width=150, anchor="center")
        self.tree.column("method", width=120, anchor="center")
        self.tree.column("status", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))

        ctk.CTkLabel(self.form_frame, text="Nueva Transacción", font=("Helvetica", 14)).grid(row=0, column=0,
                                                                                             columnspan=3, pady=5)

        ctk.CTkLabel(self.form_frame, text="Monto:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.amount_entry = ctk.CTkEntry(self.form_frame, **AppStyles.get_entry_style())
        self.amount_entry.grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkLabel(self.form_frame, text="Método:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.method_combobox = ctk.CTkComboBox(
            self.form_frame,
            values=["Tarjeta Crédito", "Tarjeta Débito", "Transferencia", "Efectivo"],
            **AppStyles.get_entry_style()
        )
        self.method_combobox.grid(row=1, column=3, padx=5, pady=5)

        self.add_button = ctk.CTkButton(
            self.form_frame,
            text="Agregar Transacción",
            command=self._add_transaction,
            **AppStyles.get_button_style()
        )
        self.add_button.grid(row=1, column=4, padx=10, pady=5)

        self.tree.tag_configure("fraud", foreground="red")
        self.tree.tag_configure("normal", foreground="black")

    def load_transactions(self):
        from core.database import Session
        from core.models import Transaction

        session = Session()
        try:
            transactions = session.query(Transaction).filter_by(user_id=self.user_id).all()

            for item in self.tree.get_children():
                self.tree.delete(item)

            for tx in transactions:
                tx_data = {
                    'id': tx.id,
                    'amount': tx.amount,
                    'date': tx.date
                }
                is_fraud = self.fraud_detector.detect_fraud(tx_data)

                status = "Fraude" if is_fraud else "Normal"
                tags = ("fraud",) if is_fraud else ("normal",)

                self.tree.insert("", "end",
                                 values=(
                                     tx.id,
                                     f"${tx.amount:,.2f}",
                                     tx.date.strftime("%Y-%m-%d %H:%M"),
                                     tx.payment_method,
                                     status
                                 ),
                                 tags=tags
                                 )
        finally:
            session.close()

    def _check_fraud(self, transaction):
        tx_data = {
            'id': transaction.id,
            'amount': transaction.amount,
            'date': transaction.date
        }
        return self.fraud_detector.detect_fraud(tx_data)

    def _add_transaction(self):
        from core.database import Session
        from core.models import Transaction

        try:
            amount = float(self.amount_entry.get())
            method = self.method_combobox.get()
            date = datetime.now()

            if amount <= 0:
                raise ValueError("El monto debe ser positivo")

            new_transaction = Transaction(
                user_id=self.user_id,
                amount=amount,
                payment_method=method,
                date=date
            )

            session = Session()
            session.add(new_transaction)
            session.commit()

            is_fraud = self._check_fraud(new_transaction)
            status = "Fraude" if is_fraud else "Normal"
            tags = ("fraud",) if is_fraud else ("normal",)

            self.tree.insert("", "end",
                             values=(
                                 new_transaction.id,
                                 f"${amount:,.2f}",
                                 date.strftime("%Y-%m-%d %H:%M"),
                                 method,
                                 status
                             ),
                             tags=tags
                             )

            self.amount_entry.delete(0, "end")

            if is_fraud:
                self._show_fraud_alert(new_transaction)

        except ValueError as e:
            error_label = ctk.CTkLabel(
                self.form_frame,
                text=f"Error: {str(e)}",
                text_color=AppStyles.DANGER_COLOR
            )
            error_label.grid(row=2, column=0, columnspan=5, pady=5)
            self.after(3000, error_label.destroy)

        except Exception as e:
            print(f"Error al agregar transacción: {e}")

    def _show_fraud_alert(self, transaction):
        alert_window = ctk.CTkToplevel(self)
        alert_window.title("Alerta de Fraude")
        alert_window.geometry("400x200")
        alert_window.grab_set()

        ctk.CTkLabel(
            alert_window,
            text="🚨 POSIBLE FRAUDE DETECTADO 🚨",
            font=("Helvetica", 16, "bold"),
            text_color=AppStyles.DANGER_COLOR
        ).pack(pady=10)

        ctk.CTkLabel(
            alert_window,
            text=f"Transacción ID: {transaction.id}\nMonto: ${transaction.amount:,.2f}\nFecha: {transaction.date.strftime('%Y-%m-%d %H:%M')}",
            font=("Helvetica", 12)
        ).pack(pady=5)

        ctk.CTkButton(
            alert_window,
            text="Aceptar",
            command=alert_window.destroy,
            **AppStyles.get_button_style()
        ).pack(pady=15)
