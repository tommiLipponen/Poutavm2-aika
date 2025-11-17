// Chinook Database Analytics Dashboard

// Store chart instances globally
let countryChart, monthlyChart, genreChart, artistChart;

// Fetch and display analytics data
async function fetchAnalytics() {
    try {
        const response = await fetch('/data-analysis/api/stats');
        const data = await response.json();
        
        if (data.error) {
            console.error('API Error:', data.error);
            return;
        }
        
        // Update summary stats
        document.getElementById('total-revenue').textContent = '$' + data.summary.total_revenue.toLocaleString('en-US', {minimumFractionDigits: 2});
        document.getElementById('total-invoices').textContent = data.summary.total_invoices.toLocaleString();
        document.getElementById('total-customers').textContent = data.summary.total_customers.toLocaleString();
        document.getElementById('total-tracks').textContent = data.summary.total_tracks.toLocaleString();
        
        // Create or update charts
        if (!countryChart) {
            createCountryChart(data.sales_by_country);
            createMonthlyChart(data.monthly_sales);
            createGenreChart(data.genre_data);
            createArtistChart(data.top_artists);
        } else {
            updateCharts(data);
        }
        
    } catch (error) {
        console.error('Error fetching analytics:', error);
    }
}

function updateCharts(data) {
    // Update country chart
    countryChart.data.labels = data.sales_by_country.map(item => item.country);
    countryChart.data.datasets[0].data = data.sales_by_country.map(item => item.sales);
    countryChart.update();
    
    // Update monthly chart
    monthlyChart.data.labels = data.monthly_sales.map(item => item.month);
    monthlyChart.data.datasets[0].data = data.monthly_sales.map(item => item.sales);
    monthlyChart.update();
    
    // Update genre chart
    genreChart.data.labels = data.genre_data.map(item => item.genre);
    genreChart.data.datasets[0].data = data.genre_data.map(item => item.tracks);
    genreChart.update();
    
    // Update artist chart
    artistChart.data.labels = data.top_artists.map(item => item.artist);
    artistChart.data.datasets[0].data = data.top_artists.map(item => item.albums);
    artistChart.update();
}

function createCountryChart(data) {
    const ctx = document.getElementById('countryChart').getContext('2d');
    
    countryChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(item => item.country),
            datasets: [{
                label: 'Total Sales ($)',
                data: data.map(item => item.sales),
                backgroundColor: '#667eea',
                borderColor: '#764ba2',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return '$' + context.parsed.y.toFixed(2);
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value;
                        }
                    }
                }
            }
        }
    });
}

function createMonthlyChart(data) {
    const ctx = document.getElementById('monthlyChart').getContext('2d');
    
    monthlyChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(item => item.month),
            datasets: [{
                label: 'Sales ($)',
                data: data.map(item => item.sales),
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return 'Sales: $' + context.parsed.y.toFixed(2);
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value;
                        }
                    }
                }
            }
        }
    });
}

function createGenreChart(data) {
    const ctx = document.getElementById('genreChart').getContext('2d');
    
    genreChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(item => item.genre),
            datasets: [{
                data: data.map(item => item.tracks),
                backgroundColor: [
                    '#667eea',
                    '#764ba2',
                    '#f093fb',
                    '#4facfe',
                    '#43e97b',
                    '#fa709a',
                    '#fee140',
                    '#30cfd0'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'right'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            return label + ': ' + value.toLocaleString() + ' tracks';
                        }
                    }
                }
            }
        }
    });
}

function createArtistChart(data) {
    const ctx = document.getElementById('artistChart').getContext('2d');
    
    artistChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(item => item.artist),
            datasets: [{
                label: 'Albums',
                data: data.map(item => item.albums),
                backgroundColor: '#764ba2',
                borderColor: '#667eea',
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y', // Horizontal bar chart
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });
}

// Auto-refresh analytics every 60 seconds
setInterval(fetchAnalytics, 60000);

// Initial load
fetchAnalytics();
