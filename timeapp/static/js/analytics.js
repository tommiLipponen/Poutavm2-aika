// Analytics Dashboard JavaScript

// Fetch and display analytics data
async function fetchAnalytics() {
    try {
        const response = await fetch('/data-analysis/api/stats');
        const data = await response.json();
        
        // Update stats cards
        document.getElementById('total-requests').textContent = data.total_requests.toLocaleString();
        document.getElementById('avg-response').textContent = data.response_times.avg + ' ms';
        document.getElementById('uptime').textContent = data.uptime_hours + ' hours';
        
        // Update response times table
        const statsTable = document.getElementById('response-stats');
        statsTable.innerHTML = `
            <tr>
                <td>Average</td>
                <td>${data.response_times.avg} ms</td>
            </tr>
            <tr>
                <td>Minimum</td>
                <td>${data.response_times.min} ms</td>
            </tr>
            <tr>
                <td>Maximum</td>
                <td>${data.response_times.max} ms</td>
            </tr>
            <tr>
                <td>95th Percentile</td>
                <td>${data.response_times.p95} ms</td>
            </tr>
        `;
        
        // Create hourly requests chart
        createHourlyChart(data.hourly_requests);
        
        // Create geographic distribution chart
        createGeoChart(data.geo_data);
        
    } catch (error) {
        console.error('Error fetching analytics:', error);
    }
}

function createHourlyChart(data) {
    const ctx = document.getElementById('hourlyChart').getContext('2d');
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(item => item.hour),
            datasets: [{
                label: 'Requests',
                data: data.map(item => item.requests),
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
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });
}

function createGeoChart(data) {
    const ctx = document.getElementById('geoChart').getContext('2d');
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(item => item.country),
            datasets: [{
                data: data.map(item => item.requests),
                backgroundColor: [
                    '#667eea',
                    '#764ba2',
                    '#f093fb',
                    '#4facfe',
                    '#43e97b'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Auto-refresh analytics every 30 seconds
setInterval(fetchAnalytics, 30000);

// Initial load
fetchAnalytics();
