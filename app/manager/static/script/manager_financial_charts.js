document.addEventListener("DOMContentLoaded", function(){
    populateYearSelector();
    updateFinancialCharts();
    // createFinanicalCharts();
});

// funcitons to show chart for financial report
const barChartData = {
    labels: [],
    datasets: [
        {
            label: 'Revenue',
            type: 'bar',
            data: [],
        },
    ]
};

const pieChartData = {
    labels: [],
    datasets: [{
        data: [],
        backgroundColor: [
            '#198754',
            '#B0DA7D',
        ],
    }],
};
let barChartInstance = null;
let pieChartInstance = null;

//reset the data
function resetData() {
    barChartData.labels = [];
    barChartData.datasets = [];
    pieChartData.labels = [];  
    pieChartData.datasets[0].data = [];
    pieChartData.datasets[0].backgroundColor = [
        '#198754',
        '#B0DA7D',
    ];
}

// this is a utility function to format the data by month and type
function processFinancialData(financialReportData) {
    resetData();
    const monthlyData = {};
    const typeData = {};

    financialReportData.forEach(item => {
        const monthYear = `${item[0]}-${item[1].toString().padStart(2, '0')}`
        const type = item[2];
        const revenue = parseFloat(item[3]);

        //process for bar chart
        if (!monthlyData[monthYear]) {
            monthlyData[monthYear] = {};
            barChartData.labels.push(monthYear); // add monthYear to the bar chart labels
        }
        if (!monthlyData[monthYear][type]) {
            monthlyData[monthYear][type] = 0;
        }
        monthlyData[monthYear][type] += revenue;

        //process for pie chart
        if (!typeData[type]) {
            typeData[type] = 0;
            pieChartData.labels.push(type); // add payment type to the pie chart labels
        }
        typeData[type] += revenue;
    });

    // add data to the bar chart
    Object.keys(typeData).forEach((type, index) => {
        const color = pieChartData.datasets[0].backgroundColor[index];
        const data = barChartData.labels.map(monthYear => (monthlyData[monthYear] && monthlyData[monthYear][type]) ? monthlyData[monthYear][type] : 0);
        barChartData.datasets.push({ label: type, data: data, backgroundColor: color});
    })

    // add data to the pie chart
    pieChartData.datasets[0].data = pieChartData.labels.map(type => typeData[type]);
}

function populateYearSelector() {
    const years = financialReportData.map(item => item[0]).filter((value, index, self) => self.indexOf(value) === index);
    const yearSelector = document.getElementById('yearSelector');
    years.forEach(year => {
        const option = document.createElement('option');
        option.value = year;
        option.text = year;
        if (year == new Date().getFullYear()) {
            option.selected = true;
        }
        yearSelector.appendChild(option);
    });
}

function updateFinancialCharts() {
    const selectedYear = document.getElementById('yearSelector').value;
    const filteredData = financialReportData.filter(item => item[0] == selectedYear);
    resetData();
    createFinanicalCharts(filteredData)
}

// function to create the financial charts with the Chart.js library
function createFinanicalCharts(filteredData) {
    // ensure the data is loaded
    //console.log(financialReportData);
    if (!filteredData || filteredData.length === 0) {
        console.error("Financial report data is not loaded");
        return;
    }

    //destroy the previous chart instance
    if (barChartInstance) {
        barChartInstance.destroy();
    }
    if (pieChartInstance) {
        pieChartInstance.destroy();
    }

    // process the data
    processFinancialData(filteredData);

    // create the bar chart
    const barChartCanvas = document.getElementById('monthlyRevenueBarChart').getContext('2d');
    barChartInstance = new Chart(barChartCanvas, {
        type: 'bar',
        data: barChartData,
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value, index, values) {
                            return '$' + value;
                        }
                    }
                }
            },
            plugins:{
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            label += '$' + context.raw.toFixed(2);
                            return label
                        }
                    }
                },
            },
        }
    });

    // create the pie chart
    const pieChartCanvas = document.getElementById('annualRevenuePieChart').getContext('2d');
    pieChartInstance = new Chart(pieChartCanvas, {
        type: 'pie',
        data: pieChartData,
        options: {
            plugins:{
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = pieChartData.labels[context.dataIndex] || '';
                            if (label) {
                                label += ': ';
                            }
                            label += '$' + context.parsed.toFixed(2);
                            return label
                        }
                    }
                }
            }
        }
    });
    updateTotalRevenue();
}

function updateTotalRevenue() {
    const totalRevenue = pieChartData.datasets[0].data.reduce((total, value) => total + Number(value), 0);
    document.getElementById('annualTotalRevenue').textContent = "Total Revenue: $" + totalRevenue.toFixed(2);
}


