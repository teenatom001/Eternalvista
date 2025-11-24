document.addEventListener('DOMContentLoaded', function() {
    const lineCtx = document.getElementById('lineChart').getContext('2d');
    new Chart(lineCtx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [{
                label: 'Bookings',
                data: [12, 19, 14, 22, 28, 33],
                borderColor: '#4fa3ff',
                backgroundColor: 'rgba(79, 163, 255, 0.3)',
                tension: 0.4,
                borderWidth: 3,
                pointRadius: 4,
                pointBackgroundColor: '#4fa3ff'
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true },
                x: { grid: { color: "rgba(255,255,255,0.1)" } }
            },
            plugins: { legend: { labels: { color: "#fff" } } }
        }
    });
    const barCtx = document.getElementById('barChart').getContext('2d');
    new Chart(barCtx, {
        type: 'bar',
        data: {
            labels: ['Photography', 'Catering', 'Decoration', 'Music'],
            datasets: [{
                label: 'Performance',
                data: [25, 35, 20, 15],
                backgroundColor: ['#ffa726', '#fb8c00', '#ff7043', '#ff5722']
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { labels: { color: "#fff" } } },
            scales: {
                y: { beginAtZero: true },
                x: { ticks: { color: "#fff" }, grid: { color: "rgba(255,255,255,0.1)" } }
            }
        }
    });
    const pieCtx = document.getElementById('pieChart').getContext('2d');
    new Chart(pieCtx, {
        type: 'pie',
        data: {
            labels: ['Venue', 'Catering', 'Photography', 'Decoration'],
            datasets: [{
                data: [40, 25, 20, 15],
                backgroundColor: ['#66bb6a', '#ffa726', '#42a5f5', '#ab47bc']
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { labels: { color: "#fff" } } }
        }
    });
});
