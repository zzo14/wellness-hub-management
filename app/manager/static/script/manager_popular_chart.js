document.addEventListener("DOMContentLoaded", function(){
    createCharts();
});

// funcitons to show chart for financial report
const barChartData = {
    labels: [],
    datasets: []
};

// different colors for the bar chart
var backgroundColors = [
        '#198754',
        '#B0DA7D',
        '#FFD166',
        '#EF476F',
        '#06D6A0',
        '#118AB2',
        '#073B4C',
    ];

let barChartInstance = null;

//reset the data
function resetData() {
    barChartData.labels = [];
    barChartData.datasets = [];
}

// this is a utility function to format the data by class
function processClassesData(classesData) {
    resetData();
    const typeData = {};
    const color = [];

    classesData.forEach(item => {
        const type = item[0];
        const booking_count = parseFloat(item[1]);
        typeData[type] = booking_count;
        color.push(backgroundColors[Object.keys(typeData).length-1 % backgroundColors.length])
    });

    barChartData.labels = Object.keys(typeData);
    const data = barChartData.labels.map(type => typeData[type]);
    
    // add data to the bar chart
    barChartData.datasets.push({ label: "Classes", data: data, backgroundColor: color, barThickness: 100});
}



// function to create the financial charts with the Chart.js library
function createCharts() {
    // ensure the data is loaded
    if (typeof popular_class_reports === 'undefined' || popular_class_reports.length === 0) {
        console.error("Classes report data is not loaded");
        return;
    }

    //destroy the previous chart instance
    if (barChartInstance) {
        barChartInstance.destroy();
    }

    // process the data
    processClassesData(popular_class_reports);

    // create the bar chart
    const barChartCanvas = document.getElementById('classBarChart').getContext('2d');
    barChartInstance = new Chart(barChartCanvas, {
        type: 'bar',
        data: barChartData,
        options: {
            scales: {
                x:{
                    indexAxis: 'x',
                    ticks: {
                        autoSkip: false,
                        maxRotation: 0,
                        minRotation: 0
                    }
                },
                y: {
                    beginAtZero: true,
                }
            },
            plugins:{
                legend: {
                    labels: {
                        filter: function(legendItem, chartData) {
                            return chartData.datasets[legendItem.datasetIndex].label.indexOf("Classes") === -1;
                        }
                    }
                }
            },
        }
    });
}


