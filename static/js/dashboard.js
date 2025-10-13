document.addEventListener('DOMContentLoaded', function() {
    // --- INITIALIZATION ---
    const userInfo = JSON.parse(localStorage.getItem('userInfo'));
    if (!userInfo || !userInfo.user_id) {
        localStorage.removeItem('userInfo');
        window.location.href = "/";
        return;
    }

    // --- DOM ELEMENT SELECTORS ---
    const welcomeMessageEl = document.getElementById('welcome-message').querySelector('h1');
    const logoutButton = document.getElementById('logout-button');
    const resetDataButton = document.getElementById('reset-data-button');
    const balanceEl = document.getElementById('current-balance');
    const incomeEl = document.getElementById('total-income');
    const spentEl = document.getElementById('total-spent');
    const receivableEl = document.getElementById('total-receivable');
    const transactionForm = document.getElementById('addTransactionForm');
    const debtsTableBody = document.getElementById('debts-table-body');
    const incomeExpenseTableBody = document.getElementById('income-expense-table-body');
    const typeSelect = document.getElementById('type');
    const personInvolvedGroup = document.getElementById('person-involved-group');

    const API_BASE_URL = 'http://127.0.0.1:5000/api';

    // --- EVENT LISTENERS ---
    logoutButton.addEventListener('click', () => {
        localStorage.removeItem('userInfo');
        window.location.href = "/";
    });

    resetDataButton.addEventListener('click', handleResetData);

    typeSelect.addEventListener('change', () => {
        const selectedType = typeSelect.value;
        personInvolvedGroup.style.display = (selectedType === 'Payable' || selectedType === 'Receivable') ? 'block' : 'none';
    });

    transactionForm.addEventListener('submit', handleAddTransaction);
    document.addEventListener('click', handleTableActions);

    // --- CORE FUNCTIONS ---

    async function fetchAndRenderData() {
        try {
            const response = await fetch(`${API_BASE_URL}/dashboard_data?user_id=${userInfo.user_id}`);
            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.error || 'Failed to fetch dashboard data');
            }
            const data = await response.json();
            
            updateSummaryCards(data.summary);
            const debts = data.transactions.filter(tx => tx.type === 'Payable' || tx.type === 'Receivable');
            const incomeExpense = data.transactions.filter(tx => tx.type === 'Income' || tx.type === 'Expense');
            renderDebts(debts);
            renderIncomeExpense(incomeExpense);

            renderExpenseChart();
            renderIncomeExpenseBarChart();

        } catch (error) {
            console.error("Error fetching dashboard data:", error);
            alert("Error: Could not load dashboard data.");
        }
    }

    async function renderExpenseChart() {
        try {
            const response = await fetch(`${API_BASE_URL}/chart_data/expenses_by_category?user_id=${userInfo.user_id}`);
            if (!response.ok) throw new Error('Failed to fetch pie chart data');
            const data = await response.json();
            
            const ctx = document.getElementById('expenseChart').getContext('2d');
            if (window.myExpenseChart) window.myExpenseChart.destroy();

            window.myExpenseChart = new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Expenses by Category',
                        data: data.values,
                        backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'],
                        borderColor: '#dee2e6',
                        borderWidth: 2,
                        hoverOffset: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: {
                                color: '#495057'
                            }
                        }
                    }
                }
            });
        } catch (error) {
            console.error("Error rendering expense chart:", error);
        }
    }

    async function renderIncomeExpenseBarChart() {
        try {
            const response = await fetch(`${API_BASE_URL}/chart_data/monthly_summary?user_id=${userInfo.user_id}`);
            if (!response.ok) throw new Error('Failed to fetch bar chart data');
            const data = await response.json();

            const ctx = document.getElementById('incomeExpenseBarChart').getContext('2d');
            if (window.myBarChart) window.myBarChart.destroy();

            window.myBarChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Income',
                        data: data.incomeData,
                        backgroundColor: 'rgba(28, 200, 138, 0.8)',
                        borderColor: 'rgba(28, 200, 138, 1)',
                        borderWidth: 1,
                        maxBarThickness: 40
                    }, {
                        label: 'Expense',
                        data: data.expenseData,
                        backgroundColor: 'rgba(231, 74, 59, 0.8)',
                        borderColor: 'rgba(231, 74, 59, 1)',
                        borderWidth: 1,
                        maxBarThickness: 40
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: value => 'Rs. ' + value
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top'
                        }
                    }
                }
            });
        } catch (error) {
            console.error("Error rendering bar chart:", error);
        }
    }

    function updateSummaryCards(summary) {
        balanceEl.textContent = `Rs. ${summary.current_balance.toFixed(2)}`;
        incomeEl.textContent = `Rs. ${summary.total_income.toFixed(2)}`;
        spentEl.textContent = `Rs. ${summary.total_spend.toFixed(2)}`;
        receivableEl.textContent = `Rs. ${summary.total_receivable.toFixed(2)}`;
    }

    function renderDebts(debts) {
        debtsTableBody.innerHTML = '';
        if (debts.length === 0) {
            debtsTableBody.innerHTML = '<tr><td colspan="5" style="text-align:center;">No debts or loans to display.</td></tr>';
            return;
        }
        debts.forEach(tx => {
            const row = document.createElement('tr');
            let statusHtml = tx.status;
            if (tx.type === 'Payable' && tx.status === 'Pending') {
                statusHtml = `<button class="btn btn-pay" data-id="${tx.transaction_id}">Mark as Paid</button>`;
            } else if (tx.status === 'Paid') {
                statusHtml = `<span class="status-paid">Paid ✔️</span>`;
            }
            row.innerHTML = `
                <td>${new Date(tx.date).toLocaleDateString()}</td>
                <td>${tx.description} (${tx.person_involved || 'N/A'})</td>
                <td>${tx.type}</td>
                <td style="color: ${tx.type === 'Receivable' ? 'var(--receivable-color)' : 'var(--payable-color)'};">Rs. ${tx.amount.toFixed(2)}</td>
                <td>${statusHtml}</td>`;
            debtsTableBody.appendChild(row);
        });
    }

    function renderIncomeExpense(transactions) {
        incomeExpenseTableBody.innerHTML = '';
        if (transactions.length === 0) {
            incomeExpenseTableBody.innerHTML = '<tr><td colspan="4" style="text-align:center;">No income or expense history.</td></tr>';
            return;
        }
        transactions.forEach(tx => {
            const row = document.createElement('tr');
            const sign = tx.type === 'Income' ? '+' : '-';
            row.innerHTML = `
                <td>${new Date(tx.date).toLocaleDateString()}</td>
                <td>${tx.description}</td>
                <td>${tx.category_name}</td>
                <td style="color: ${tx.type === 'Income' ? 'var(--income-color)' : 'var(--expense-color)'};">${sign} Rs. ${tx.amount.toFixed(2)}</td>`;
            incomeExpenseTableBody.appendChild(row);
        });
    }

    async function handleAddTransaction(e) {
        e.preventDefault();
        const newTransaction = {
            user_id: userInfo.user_id,
            description: document.getElementById('description').value,
            amount: parseFloat(document.getElementById('amount').value),
            category_name: document.getElementById('category').value,
            type: document.getElementById('type').value,
            person_involved: document.getElementById('person-involved').value || null,
        };
        try {
            const response = await fetch(`${API_BASE_URL}/transactions`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(newTransaction)
            });
            if (!response.ok) throw new Error((await response.json()).error || 'Failed to add transaction');
            transactionForm.reset();
            personInvolvedGroup.style.display = 'none';
            fetchAndRenderData();
        } catch (error) {
            console.error("Error adding transaction:", error);
            alert('Failed to add transaction: ' + error.message);
        }
    }

    async function handleTableActions(e) {
        if (e.target.classList.contains('btn-pay')) {
            const transactionId = e.target.dataset.id;
            if (confirm('Are you sure you want to mark this debt as paid? This will create a new expense transaction.')) {
                try {
                    const response = await fetch(`${API_BASE_URL}/pay_debt`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ transaction_id: transactionId })
                    });
                    if (!response.ok) throw new Error((await response.json()).error || 'Failed to pay debt');
                    fetchAndRenderData();
                } catch (error) {
                    console.error("Error paying debt:", error);
                    alert('Failed to pay debt: ' + error.message);
                }
            }
        }
    }

    async function handleResetData() {
        if (confirm("WARNING: This will permanently delete all transaction data. This action cannot be undone. Continue?")) {
            try {
                const response = await fetch(`${API_BASE_URL}/reset_transactions`, {
                    method: 'DELETE',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: userInfo.user_id })
                });
                if (!response.ok) throw new Error((await response.json()).error || 'Failed to reset data');
                fetchAndRenderData();
                alert("All transaction data has been reset.");
            } catch (error) {
                console.error("Error resetting data:", error);
                alert('Failed to reset data: ' + error.message);
            }
        }
    }

    // --- INITIAL LOAD ---
    welcomeMessageEl.textContent = `Welcome, ${userInfo.username}!`;
    fetchAndRenderData();
});