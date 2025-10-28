document.addEventListener('DOMContentLoaded', function() {
    
    // API Base URL for admin endpoints
    const API_BASE_URL = '/api/admin';

    // --- Helper to format currency ---
    const formatCurrency = (num) => `Rs. ${num.toFixed(2)}`;

    // --- 1. Fetch Key Statistics ---
    async function fetchStats() {
        try {
            const response = await fetch(`${API_BASE_URL}/stats`);
            if (!response.ok) throw new Error('Failed to fetch stats');
            const data = await response.json();

            document.getElementById('total-users').textContent = data.total_users;
            document.getElementById('total-transactions').textContent = data.total_transactions;
            document.getElementById('total-income').textContent = formatCurrency(data.total_income);
            document.getElementById('total-expense').textContent = formatCurrency(data.total_expense);
        } catch (error) {
            console.error("Error fetching stats:", error);
        }
    }

    // --- 2. Fetch and Render Latest 50 Transactions ---
    async function fetchLatestTransactions() {
        const tableBody = document.getElementById('latest-transactions-body');
        try {
            const response = await fetch(`${API_BASE_URL}/latest_transactions`);
            if (!response.ok) throw new Error('Failed to fetch transactions');
            const transactions = await response.json();

            tableBody.innerHTML = '';
            if (transactions.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="5" style="text-align:center;">No transactions found.</td></tr>';
                return;
            }

            transactions.forEach(tx => {
                const row = document.createElement('tr');
                const sign = (tx.type === 'Income' || tx.type === 'Receivable') ? '+' : '-';
                let color = '';
                if (tx.type === 'Income') color = 'var(--income-color)';
                if (tx.type === 'Expense') color = 'var(--expense-color)';
                
                row.innerHTML = `
                    <td>${new Date(tx.date).toLocaleDateString()}</td>
                    <td>${tx.user_name} (ID: ${tx.user_id})</td>
                    <td>${tx.description}</td>
                    <td>${tx.type}</td>
                    <td style="color: ${color};">${sign} ${formatCurrency(tx.amount)}</td>
                `;
                tableBody.appendChild(row);
            });
        } catch (error) {
            console.error("Error fetching transactions:", error);
            tableBody.innerHTML = '<tr><td colspan="5" style="text-align:center; color: red;">Error loading data.</td></tr>';
        }
    }

    // --- 3. Render Charts ---
    
    // Generic function to create a LINE chart
    function createLineChart(canvasId, chartLabel, labels, data) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: chartLabel,
                    data: data,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    fill: true,
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { ticks: { color: '#dee2e6' } },
                    y: {
                        beginAtZero: true,
                        ticks: { 
                            color: '#dee2e6',
                            stepSize: 1
                        }
                    }
                },
                plugins: {
                    legend: { labels: { color: '#dee2e6' } }
                }
            }
        });
    }

    // Generic function for the Pie Chart
    function createPieChart(canvasId, chartLabel, labels, data) {
        const ctx = document.getElementById(canvasId).getContext('2d');

        const colorMap = {
            'Income': 'rgba(28, 200, 138, 0.8)', // Green
            'Expense': 'rgba(231, 74, 59, 0.8)',  // Red
            'Payable': 'rgba(255, 159, 64, 0.8)', // Orange
            'Receivable': 'rgba(54, 162, 235, 0.8)', // Blue
            'default': 'rgba(201, 203, 207, 0.8)' // Grey for any others
        };

        const backgroundColors = labels.map(label => colorMap[label] || colorMap['default']);

        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    label: chartLabel,
                    data: data,
                    backgroundColor: backgroundColors,
                    borderColor: '#dee2e6',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: { color: '#dee2e6' }
                    }
                }
            }
        });
    }

    // --- NEW: Renders the VALUE (Rs.) Pie Chart ---
    async function renderTransactionValueChart() {
        try {
            const response = await fetch(`${API_BASE_URL}/chart/types_by_value`);
            if (!response.ok) throw new Error('Failed to fetch transaction value data');
            const chartData = await response.json();
            createPieChart('transactionValueChart', 'Total Value (Rs.)', chartData.labels, chartData.data);
        } catch (error) {
            console.error("Error rendering transaction value chart:", error);
        }
    }

    // --- NEW: Renders the COUNT (#) Pie Chart ---
    async function renderTransactionCountChart() {
        try {
            const response = await fetch(`${API_BASE_URL}/chart/types_by_count`);
            if (!response.ok) throw new Error('Failed to fetch transaction count data');
            const chartData = await response.json();
            createPieChart('transactionCountChart', '# of Transactions', chartData.labels, chartData.data);
        } catch (error) {
            console.error("Error rendering transaction count chart:", error);
        }
    }

    // Fetch data for Transaction Activity chart
    async function renderTransactionActivityChart() {
        try {
            const response = await fetch(`${API_BASE_URL}/chart/transaction_activity`);
            if (!response.ok) throw new Error('Failed to fetch transaction activity data');
            const chartData = await response.json();
            createLineChart('transactionActivityChart', 'Transactions', chartData.labels, chartData.data);
        } catch (error) {
            console.error("Error rendering transaction activity chart:", error);
        }
    }

    // --- Initial Load ---
    fetchStats();
    fetchLatestTransactions();
    renderTransactionValueChart();   // <-- ADDED
    renderTransactionCountChart();     // <-- ADDED
    renderTransactionActivityChart();
});