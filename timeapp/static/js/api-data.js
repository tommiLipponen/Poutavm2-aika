// Global chart instances to allow updating without recreation
let weatherChart = null;
let solarChart = null;

// Countdown timer variables
let countdownSeconds = 300; // 5 minutes = 300 seconds
let countdownInterval = null;

function updateCountdown() {
    const timerElement = document.getElementById('countdown-timer');
    if (countdownSeconds > 0) {
        countdownSeconds--;
        timerElement.textContent = countdownSeconds;
    } else {
        // Reset to 5 minutes when it reaches 0
        countdownSeconds = 300;
        timerElement.textContent = countdownSeconds;
    }
}

function startCountdown() {
    // Update immediately
    document.getElementById('countdown-timer').textContent = countdownSeconds;
    
    // Then update every second
    if (countdownInterval) {
        clearInterval(countdownInterval);
    }
    countdownInterval = setInterval(updateCountdown, 1000);
}

function updateCharts() {
    fetch('/weather-data/api/stats')
        .then(response => response.json())
        .then(data => {
            // Update weather statistics cards
            document.getElementById('current-temp').textContent = 
                data.latest.weather.temperature !== null ? data.latest.weather.temperature.toFixed(1) : '--';
            document.getElementById('current-wind').textContent = 
                data.latest.weather.wind_speed !== null ? data.latest.weather.wind_speed.toFixed(1) : '--';
            document.getElementById('avg-temp').textContent = 
                data.latest.weather.avg_temp_24h !== null ? data.latest.weather.avg_temp_24h.toFixed(1) : '--';

            // Update solar wind statistics cards
            document.getElementById('current-solar-speed').textContent = 
                data.latest.solar.speed !== null ? data.latest.solar.speed.toFixed(0) : '--';
            document.getElementById('current-density').textContent = 
                data.latest.solar.density !== null ? data.latest.solar.density.toFixed(1) : '--';
            document.getElementById('avg-solar-speed').textContent = 
                data.latest.solar.avg_speed_24h !== null ? data.latest.solar.avg_speed_24h.toFixed(0) : '--';

            // Update or create weather chart (dual Y-axis: temperature + wind speed)
            const weatherCtx = document.getElementById('weatherChart').getContext('2d');
            
            if (weatherChart) {
                // Update existing chart
                weatherChart.data.labels = data.weather.timestamps;
                weatherChart.data.datasets[0].data = data.weather.temperature;
                weatherChart.data.datasets[1].data = data.weather.wind_speed;
                weatherChart.update();
            } else {
                // Create new chart
                weatherChart = new Chart(weatherCtx, {
                    type: 'line',
                    data: {
                        labels: data.weather.timestamps,
                        datasets: [
                            {
                                label: 'Lämpötila (°C)',
                                data: data.weather.temperature,
                                borderColor: 'rgb(255, 99, 132)',
                                backgroundColor: 'rgba(255, 99, 132, 0.1)',
                                yAxisID: 'y',
                                tension: 0.3,
                                pointRadius: 0
                            },
                            {
                                label: 'Tuulen nopeus (m/s)',
                                data: data.weather.wind_speed,
                                borderColor: 'rgb(54, 162, 235)',
                                backgroundColor: 'rgba(54, 162, 235, 0.1)',
                                yAxisID: 'y1',
                                tension: 0.3,
                                pointRadius: 0
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        interaction: {
                            mode: 'index',
                            intersect: false,
                        },
                        scales: {
                            x: {
                                ticks: {
                                    maxTicksLimit: 12
                                }
                            },
                            y: {
                                type: 'linear',
                                display: true,
                                position: 'left',
                                title: {
                                    display: true,
                                    text: 'Lämpötila (°C)'
                                }
                            },
                            y1: {
                                type: 'linear',
                                display: true,
                                position: 'right',
                                title: {
                                    display: true,
                                    text: 'Tuulen nopeus (m/s)'
                                },
                                grid: {
                                    drawOnChartArea: false,
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
            }

            // Update or create solar wind chart (dual Y-axis: speed + density)
            const solarCtx = document.getElementById('solarChart').getContext('2d');
            
            if (solarChart) {
                // Update existing chart
                solarChart.data.labels = data.solar.timestamps;
                solarChart.data.datasets[0].data = data.solar.speed;
                solarChart.data.datasets[1].data = data.solar.density;
                solarChart.update();
            } else {
                // Create new chart
                solarChart = new Chart(solarCtx, {
                    type: 'line',
                    data: {
                        labels: data.solar.timestamps,
                        datasets: [
                            {
                                label: 'Nopeus (km/s)',
                                data: data.solar.speed,
                                borderColor: 'rgb(255, 206, 86)',
                                backgroundColor: 'rgba(255, 206, 86, 0.1)',
                                yAxisID: 'y',
                                tension: 0.3,
                                pointRadius: 0
                            },
                            {
                                label: 'Tiheys (p/cm³)',
                                data: data.solar.density,
                                borderColor: 'rgb(75, 192, 192)',
                                backgroundColor: 'rgba(75, 192, 192, 0.1)',
                                yAxisID: 'y1',
                                tension: 0.3,
                                pointRadius: 0
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        interaction: {
                            mode: 'index',
                            intersect: false,
                        },
                        scales: {
                            x: {
                                ticks: {
                                    maxTicksLimit: 12
                                }
                            },
                            y: {
                                type: 'linear',
                                display: true,
                                position: 'left',
                                title: {
                                    display: true,
                                    text: 'Nopeus (km/s)'
                                }
                            },
                            y1: {
                                type: 'linear',
                                display: true,
                                position: 'right',
                                title: {
                                    display: true,
                                    text: 'Tiheys (p/cm³)'
                                },
                                grid: {
                                    drawOnChartArea: false,
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
            }

        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    updateCharts();
    startCountdown();
    // Update charts every 60 seconds (countdown continues independently)
    setInterval(updateCharts, 60000);
});
