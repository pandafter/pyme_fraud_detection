// Toggle de visibilidad de contraseña
document.querySelectorAll('.toggle-password').forEach(button => {
    button.addEventListener('click', function() {
        const input = this.previousElementSibling;
        const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
        input.setAttribute('type', type);
        this.textContent = type === 'password' ? '👁️' : '🔒';
    });
});

// Dashboard - Monitoreo en tiempo real
if (document.getElementById('startMonitorBtn')) {
    const startBtn = document.getElementById('startMonitorBtn');
    const stopBtn = document.getElementById('stopMonitorBtn');
    const statusText = document.getElementById('monitorStatus');
    const outputDiv = document.getElementById('realtimeOutput');

    let monitorInterval;

    startBtn.addEventListener('click', () => {
        statusText.textContent = 'Estado: Activo';
        statusText.style.color = 'green';
        startBtn.disabled = true;
        stopBtn.disabled = false;

        // Simulación de monitoreo en tiempo real
        monitorInterval = setInterval(() => {
            fetch('/api/transactions/realtime')
                .then(response => response.json())
                .then(data => {
                    const transaction = data.transaction;
                    const transactionDiv = document.createElement('div');
                    transactionDiv.className = 'transaction';
                    transactionDiv.innerHTML = `
                        <p><strong>🧾 Transacción Detectada</strong></p>
                        <p>📅 Fecha: ${new Date(transaction.date).toLocaleString()}</p>
                        <p>🆔 ID: ${transaction.id}</p>
                        <p>💰 Monto: $${transaction.amount.toFixed(2)}</p>
                        <p>🏷️ Tipo: ${transaction.method}</p>
                        <hr>
                    `;
                    outputDiv.prepend(transactionDiv);
                });
        }, 5000);
    });

    stopBtn.addEventListener('click', () => {
        clearInterval(monitorInterval);
        statusText.textContent = 'Estado: Inactivo';
        statusText.style.color = 'gray';
        startBtn.disabled = false;
        stopBtn.disabled = true;
    });
}

// Generación de reportes
if (document.getElementById('generateReportBtn')) {
    document.getElementById('generateReportBtn').addEventListener('click', () => {
        const startDate = document.getElementById('startDate').value;
        const endDate = document.getElementById('endDate').value;
        const format = document.querySelector('input[name="reportFormat"]:checked').value;

        fetch('/api/reports/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                startDate,
                endDate,
                format
            })
        })
        .then(response => response.json())
        .then(data => {
            alert(`Reporte generado exitosamente: ${data.filename}`);
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error al generar el reporte');
        });
    });
}

// Agregar transacción
if (document.getElementById('addTransactionForm')) {
    document.getElementById('addTransactionForm').addEventListener('submit', function(e) {
        e.preventDefault();

        const amount = parseFloat(document.getElementById('amount').value);
        const method = document.getElementById('method').value;

        fetch('/api/transactions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                amount,
                method
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Agregar fila a la tabla
                const table = document.getElementById('transactionsTable').getElementsByTagName('tbody')[0];
                const newRow = table.insertRow(0);
                newRow.className = data.is_fraud ? 'fraud' : 'normal';

                newRow.innerHTML = `
                    <td>${data.transaction.id}</td>
                    <td>$${data.transaction.amount.toFixed(2)}</td>
                    <td>${new Date(data.transaction.date).toLocaleString()}</td>
                    <td>${data.transaction.method}</td>
                    <td>${data.is_fraud ? 'Fraude' : 'Normal'}</td>
                `;

                // Mostrar alerta si es fraude
                if (data.is_fraud) {
                    const modal = document.getElementById('fraudAlertModal');
                    const fraudDetails = document.getElementById('fraudDetails');

                    fraudDetails.innerHTML = `
                        <p>Transacción ID: ${data.transaction.id}</p>
                        <p>Monto: $${data.transaction.amount.toFixed(2)}</p>
                        <p>Fecha: ${new Date(data.transaction.date).toLocaleString()}</p>
                    `;

                    modal.style.display = 'block';

                    document.getElementById('confirmFraudAlert').onclick = function() {
                        modal.style.display = 'none';
                    };

                    document.querySelector('.close').onclick = function() {
                        modal.style.display = 'none';
                    };
                }

                // Limpiar formulario
                document.getElementById('amount').value = '';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error al agregar la transacción');
        });
    });
}

// Inicializar fechas en el dashboard
if (document.getElementById('startDate') && document.getElementById('endDate')) {
    const today = new Date().toISOString().split('T')[0];
    const lastWeek = new Date();
    lastWeek.setDate(lastWeek.getDate() - 7);
    const lastWeekFormatted = lastWeek.toISOString().split('T')[0];

    document.getElementById('startDate').value = lastWeekFormatted;
    document.getElementById('endDate').value = today;
}