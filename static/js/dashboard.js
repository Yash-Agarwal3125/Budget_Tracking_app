document.addEventListener('DOMContentLoaded', function() {
    // --- INITIALIZATION ---
    const userInfo = JSON.parse(localStorage.getItem('userInfo'));
    if (!userInfo) {
        window.location.href = "/"; // Redirect to login if not logged in
        return;
    }

    // --- DOM ELEMENT SELECTORS ---
    const welcomeMessageEl = document.getElementById('welcome-message').querySelector('h1');
    const logoutButton = document.getElementById('logout-button');
    const resetDataButton = document.getElementById('reset-data-button'); // New button
    const balanceEl = document.getElementById('current-balance');
    const incomeEl = document.getElementById('total-income');
    const spentEl = document.getElementById('total-spent');
    const receivableEl = document.getElementById('total-receivable');
    const transactionForm = document.getElementById('addTransactionForm');
    const debtsTableBody = document.getElementById('debts-table-body');
    const incomeExpenseTableBody = document.getElementById('income-expense-table-body');
    const typeSelect = document.getElementById('type');
    const personInvolvedGroup = document.getElementById('person-involved-group');

    const API_BASE_URL = 'https://budget-tracking-mzav.onrender.com';

    // --- EVENT LISTENERS ---
    logoutButton.addEventListener('click', () => {
        localStorage.removeItem('userInfo');
        window.location.href = "/";
    });

    // New listener for the reset button
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
                throw new Error(errData.error || 'Failed to fetch data');
            }
            
            const data = await response.json();
            
            updateSummaryCards(data.summary);

            const debts = data.transactions.filter(tx => tx.type === 'Payable' || tx.type === 'Receivable');
            const incomeExpense = data.transactions.filter(tx => tx.type === 'Income' || tx.type === 'Expense');

            renderDebts(debts);
            renderIncomeExpense(incomeExpense);

        } catch (error) {
            console.error("Error fetching dashboard data:", error);
            alert("Error: Could not load dashboard data.");
        }
    }

    function updateSummaryCards(summary) {
        balanceEl.textContent = `$${summary.current_balance.toFixed(2)}`;
        incomeEl.textContent = `$${summary.total_income.toFixed(2)}`;
        spentEl.textContent = `$${summary.total_spend.toFixed(2)}`;
        receivableEl.textContent = `$${summary.total_receivable.toFixed(2)}`;
    }

    function renderDebts(debts) {
        debtsTableBody.innerHTML = '';
        if (debts.length === 0) {
            debtsTableBody.innerHTML = '<tr><td colspan="5" style="text-align:center;">No debts or loans to display.</td></tr>';
            return;
        }

        debts.forEach(tx => {
            const row = document.createElement('tr');
            const formattedDate = new Date(tx.date).toLocaleDateString();
            const amountStyle = tx.type === 'Receivable' ? 'color: var(--receivable-color);' : 'color: var(--payable-color);';

            let statusHtml = tx.status;
            if (tx.type === 'Payable' && tx.status === 'Pending') {
                statusHtml = `<button class="btn btn-pay" data-id="${tx.transaction_id}">Mark as Paid</button>`;
            } else if (tx.status === 'Paid') {
                statusHtml = `<span class="status-paid">Paid ✔️</span>`;
            }

            row.innerHTML = `
                <td>${formattedDate}</td>
                <td>${tx.description} (${tx.person_involved || 'N/A'})</td>
                <td>${tx.type}</td>
                <td style="${amountStyle}">$${tx.amount.toFixed(2)}</td>
                <td>${statusHtml}</td>
            `;
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
            const formattedDate = new Date(tx.date).toLocaleDateString();
            const amountStyle = tx.type === 'Income' ? 'color: var(--income-color);' : 'color: var(--expense-color);';
            const sign = tx.type === 'Income' ? '+' : '-';

            row.innerHTML = `
                <td>${formattedDate}</td>
                <td>${tx.description}</td>
                <td>${tx.category_name}</td>
                <td style="${amountStyle}">${sign} $${tx.amount.toFixed(2)}</td>
            `;
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
            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.error || 'Failed to add transaction');
            }
            
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
                     if (!response.ok) {
                        const errData = await response.json();
                        throw new Error(errData.error || 'Failed to pay debt');
                    }
                    
                    fetchAndRenderData();
                } catch (error) {
                    console.error("Error paying debt:", error);
                    alert('Failed to pay debt: ' + error.message);
                }
            }
        }
    }

    // New function to handle the data reset
    async function handleResetData() {
        const confirmation = confirm("WARNING: This will permanently delete all of your transaction data. This action cannot be undone. Are you sure you want to continue?");
        
        if (confirmation) {
            try {
                const response = await fetch(`${API_BASE_URL}/reset_transactions`, {
                    method: 'DELETE',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: userInfo.user_id })
                });

                if (!response.ok) {
                    const errData = await response.json();
                    throw new Error(errData.error || 'Failed to reset data');
                }
                
                // Refresh the dashboard to show the empty state
                fetchAndRenderData();
                alert("All your transaction data has been successfully reset.");

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
