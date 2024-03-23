// mortgage.js

// Function to calculate and display monthly mortgage payment
function calculateMonthlyPayment(principal, interestRate, loanTerm) {
    var monthlyInterestRate = interestRate / 100 / 12;
    var monthlyPayment = (principal * monthlyInterestRate) / (1 - Math.pow(1 + monthlyInterestRate, -loanTerm));
    document.getElementById('result').innerHTML = 'Monthly Payment: $' + monthlyPayment.toFixed(2);
}

// Event listener for the mortgage form submission
document.getElementById('mortgageForm').addEventListener('submit', function(e) {
    e.preventDefault();
    var principal = parseFloat(document.getElementById('principal').value);
    var loanTerm = parseFloat(document.getElementById('loanTerm').value) * 12;
    var interestRate = parseFloat(document.getElementById('interestRate').value);
    calculateMonthlyPayment(principal, interestRate, loanTerm);
});

// Helper function to add months to a date
function addMonthsToDate(startDate, months) {
    const date = new Date(startDate);
    date.setMonth(date.getMonth() + months);
    return date;
}

// Function to format date as 'Month Year'
function formatDate(date) {
    const options = { year: 'numeric', month: 'short' };
    return date.toLocaleDateString('en-US', options);
}

// Function to calculate amortization details
function calculateAmortization(principal, interestRate, loanTerm, startDate) {
    let schedule = [];
    let monthlyInterestRate = interestRate / 100 / 12;
    let monthlyPayment = (principal * monthlyInterestRate) / (1 - Math.pow(1 + monthlyInterestRate, -loanTerm * 12));
    let totalPrincipalPaid = 0;
    let totalInterestPaid = 0;
    let currentDate = new Date();

    for (let i = 0; i < loanTerm * 12; i++) {
        let paymentDate = addMonthsToDate(startDate, i);
        let interestPayment = principal * monthlyInterestRate;
        let principalPayment = monthlyPayment - interestPayment;
        principal -= principalPayment;
        totalPrincipalPaid += principalPayment;
        totalInterestPaid += interestPayment;
        schedule.push({
            paymentDate: paymentDate,
            principalPayment: principalPayment,
            interestPayment: interestPayment,
            totalPayment: monthlyPayment,
            balance: principal,
            totalPrincipalPaid: totalPrincipalPaid,
            totalInterestPaid: totalInterestPaid,
            isCurrent: paymentDate >= currentDate && addMonthsToDate(startDate, i - 1) < currentDate
        });
    }
    return schedule;
}

// Calculate monthly mortgage payment
function calculateMonthlyPayment(principal, annualInterestRate, loanTermYears) {
    const monthlyInterestRate = annualInterestRate / 100 / 12;
    const loanTermMonths = loanTermYears * 12;
    const monthlyPayment = (principal * monthlyInterestRate) / (1 - Math.pow(1 + monthlyInterestRate, -loanTermMonths));
    return monthlyPayment;
}

// Calculate end date from start date + term years
function calculateMortgageEndDate(startDate, termYears) {
    const start = new Date(startDate);
    
    // Add the term years to the start date's year
    start.setFullYear(start.getFullYear() + termYears);
    
    // Set the date to the first day of the following month
    start.setMonth(start.getMonth() + 1, 1);
    
    // Format the end date
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    const formattedEndDate = start.toLocaleDateString('en-US', options);
    
    return formattedEndDate;
}

// Function to build chart data
function buildChartData(amortizationSchedule) {
    return {
        labels: amortizationSchedule.map(item => formatDate(item.paymentDate)),
        datasets: [
            {
                label: 'Remaining Balance',
                backgroundColor: 'rgba(135, 206, 250, 0.2)', // Light blue
                borderColor: 'rgba(135, 206, 250, 1)', // Blue
                pointStyle: false,
                data: amortizationSchedule.map(item => item.balance),
            },
            {
                label: 'Principal Paid To Date',
                backgroundColor: 'rgba(0, 0, 0, 0.2)', // Light black
                borderColor: 'rgba(0, 0, 0, 1)', // Black
                pointStyle: false,
                data: amortizationSchedule.map(item => item.totalPrincipalPaid),
            },
            {
                label: 'Interest Paid To Date',
                backgroundColor: 'rgba(255, 165, 0, 0.2)', // Light orange
                borderColor: 'rgba(255, 165, 0, 1)', // Orange
                pointStyle: false,
                data: amortizationSchedule.map(item => item.totalInterestPaid),
            }
        ]
    };
}

// Function to create and return a mortgage table element
function createMortgageTable(mortgages) {
    const table = document.createElement('table');
    table.className = 'table';
    table.innerHTML = `
        <thead>
            <tr>
                <th scope="col">Principal</th>
                <th scope="col">Interest Rate</th>
                <th scope="col">Loan Term</th>
                <th scope="col">Start Date</th>
                <th scope="col">End Date</th>
                <th scope="col">Monthly Escrow</th>
                <th scope="col">Monthly Payment</th>
                <th scope="col">Actions</th>
            </tr>
        </thead>
        <tbody>
            ${mortgages.map(mortgage => {
                const formattedStartDate = new Date(mortgage.start_date).toLocaleDateString('en-US', {
                    year: 'numeric', month: 'long', day: 'numeric'
                });
                const endDate = calculateMortgageEndDate(mortgage.start_date, mortgage.loan_term);
                const monthlyPayment = calculateMonthlyPayment(mortgage.principal, mortgage.interest_rate, mortgage.loan_term).toFixed(2);
                const totalMonthlyPayment = (parseFloat(monthlyPayment) + parseFloat(mortgage.monthly_escrow || 0)).toFixed(2);
                return `
                    <tr>
                        <td>$${mortgage.principal}</td>
                        <td>${mortgage.interest_rate}%</td>
                        <td>${mortgage.loan_term} years</td>
                        <td>${formattedStartDate}</td>
                        <td>${endDate}</td>
                        <td>
                            <input type="number" class="form-control" id="escrow-${mortgage.id}" value="${mortgage.monthly_escrow || 0}">
                        </td>
                        <td>$${totalMonthlyPayment}</td>
                        <td>
                            <button type="button" class="btn btn-primary" onclick="updateEscrow(${mortgage.id})">Update</button>
                        </td>
                    </tr>
                    <tr>
                        <td colspan="7">
                            <canvas id="chart-${mortgage.id}"></canvas>
                        </td>
                    </tr>
                `;
            }).join('')}
        </tbody>
    `;
    return table;
}

// build mortgage chart
function buildChart(ctx, chartData, currentPeriodIndex) {
    const chart = new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: {
            plugins: {
                annotation: {
                    annotations: {
                        line1: {
                            type: 'line',
                            mode: 'vertical',
                            scaleID: 'x',
                            value: chartData.labels[currentPeriodIndex],
                            borderColor: 'gray',
                            borderWidth: 2,
                            label: {
                                content: 'Today',
                                display: true,
                                position: 'top'
                            }
                        },
                    }
                }
            }
        }
    });
}


function updateEscrow(mortgageId) {
    var escrowAmount = parseFloat(document.getElementById('escrow-' + mortgageId).value);
    // Perform validation on escrowAmount if necessary

    // Make a PUT request to update the escrow amount in the database
    fetch('/finances/api/mortgage/' + mortgageId, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ monthly_escrow: escrowAmount }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Handle the response from the server
        console.log('Escrow updated:', data);
        // Optionally, refresh the data on the page to reflect the updated escrow
    })
    .catch((error) => {
        console.error('Error updating escrow:', error);
    });
}

// Function to calculate monthly interest
function calculateMonthlyInterest(principal, annualInterestRate) {
    const monthlyInterestRate = annualInterestRate / 12 / 100;
    return principal * monthlyInterestRate;
}

// Function to calculate monthly principal
function calculateMonthlyPrincipal(monthlyPayment, monthlyInterest) {
    return monthlyPayment - monthlyInterest;
}

// Function to fetch bonus payments
function fetchBonusPayments() {
    return fetch('/finances/api/aggregated_rsu_payouts').then(response => response.json());
}

// Fetch savings amount
function fetchLatestSavings() {
    return fetch('/finances/api/savings/latest').then(response => response.json());
}

// Do the comma thing
function formatCurrency(number) {
    return '$' + parseFloat(number).toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
}

// Function to calculate monthly interest
function calculateMonthlyInterest(remainingPrincipal, annualInterestRate) {
    const monthlyInterestRate = annualInterestRate / 12 / 100;
    return remainingPrincipal * monthlyInterestRate;
}

// Function to calculate monthly principal
function calculateMonthlyPrincipal(totalMonthlyPayment, monthlyInterest, monthlyEscrow) {
    return totalMonthlyPayment - monthlyInterest - monthlyEscrow;
}

// Function to build the finance table HTML
function buildTableHTML(mortgages, payouts, latestSavings) {
    let tableHTML = `
        <div class="table-responsive">
            <table class="table table-striped table-hover table-bordered">
                <thead class="table-dark">
                    <tr>
                        <th>Month</th>
                        <th>Account Balance</th>
                        <th>Total Mortgage Payment</th>
                        <th>Escrow</th>
                        <th>Principal</th>
                        <th>Interest</th>
                        <th>Bonus/RSU Payout</th>
                    </tr>
                </thead>
                <tbody>
    `;

    const currentDate = new Date();
    const currentYear = currentDate.getFullYear();

    mortgages.forEach(mortgage => {
        let remainingPrincipal = mortgage.principal;

        for (let monthOffset = 0; monthOffset < 24; monthOffset++) {
            const date = new Date(currentYear, currentDate.getMonth() + monthOffset, 1);
            const monthlyInterest = calculateMonthlyInterest(remainingPrincipal, mortgage.interest_rate);
            const monthlyPrincipal = calculateMonthlyPrincipal(mortgage.monthly_payment, monthlyInterest, mortgage.monthly_escrow);
            remainingPrincipal -= monthlyPrincipal;
            latestSavings += (payouts[monthOffset] ? payouts[monthOffset].amount : 0) - (monthlyPrincipal + monthlyInterest);

            tableHTML += `
                <tr>
                    <td>${date.toLocaleDateString('en-US', { year: 'numeric', month: 'long' })}</td>
                    <td>${formatCurrency(latestSavings)}</td>
                    <td>${formatCurrency(mortgage.monthly_payment)}</td>
                    <td>${formatCurrency(mortgage.monthly_escrow)}</td>
                    <td>${formatCurrency(monthlyPrincipal)}</td>
                    <td>${formatCurrency(monthlyInterest)}</td>
                    <td>${formatCurrency((payouts[monthOffset] ? payouts[monthOffset].amount : 0))}</td>
                </tr>
            `;
        }
    });

    tableHTML += `</tbody></table></div>`;
    return tableHTML;
}


// Function to fetch mortgage details
function fetchMortgages() {
    return fetch('/finances/api/mortgage').then(response => response.json());
}

// Function to handle the response for mortgages
function handleMortgagesResponse(mortgages) {
    const list = document.getElementById('mortgagesList');
    list.innerHTML = '';
    const mortgageTable = createMortgageTable(mortgages);
    list.appendChild(mortgageTable);
    mortgages.forEach(mortgage => {
        renderMortgageChart(mortgage);
    });
}

// Function to render the chart for a mortgage
function renderMortgageChart(mortgage) {
    const amortizationSchedule = calculateAmortization(mortgage.principal, mortgage.interest_rate, mortgage.loan_term, mortgage.start_date);
    const chartData = buildChartData(amortizationSchedule);
    const currentPeriodIndex = amortizationSchedule.findIndex(item => item.isCurrent);
    const ctx = document.getElementById(`chart-${mortgage.id}`).getContext('2d');
    buildChart(ctx, chartData, currentPeriodIndex);
}

// Function to handle the response for latest savings
function handleLatestSavingsResponse(latestSavings, mortgages, payouts) {
    const financeDiv = document.getElementById('financeOverview');
    if (latestSavings && !latestSavings.error) {
        // Ensure you are using the mortgages and payouts data correctly here
        financeDiv.innerHTML = buildTableHTML(mortgages, payouts, latestSavings.balance);
    } else {
        console.error('Error fetching latest savings data:', latestSavings.error);
    }
}

// Main function to build the finance table
function buildFinanceTable() {
    Promise.all([fetchMortgages(), fetchBonusPayments(), fetchLatestSavings()])
        .then(([mortgages, payouts, latestSavings]) => {
            // Now pass the mortgages and payouts to the function that needs them
            handleLatestSavingsResponse(latestSavings, mortgages, payouts);
            handleMortgagesResponse(mortgages);
            // You can also handle payouts here if needed
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            // Handle the error appropriately in the UI
        });
}

// Code that interacts with the DOM goes here
document.addEventListener('DOMContentLoaded', function() {
    buildFinanceTable();
});