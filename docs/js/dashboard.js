// Dashboard JavaScript
let statistics = null;

// Load statistics data
async function loadStatistics() {
    try {
        const response = await fetch('data/statistics.json');
        const data = await response.json();
        statistics = data.statistics;
        displayStatistics();
        createCharts();
    } catch (error) {
        console.error('Error loading statistics:', error);
        document.getElementById('stats-overview').innerHTML = 
            '<p style="color: red;">Error loading statistics. Please ensure data/statistics.json exists.</p>';
    }
}

// Display statistics
function displayStatistics() {
    if (!statistics) return;

    document.getElementById('total-content').textContent = 
        statistics.total_content.toLocaleString();
    
    document.getElementById('geo-restricted').textContent = 
        statistics.geo_restricted_count.toLocaleString();
    
    document.getElementById('accessible').textContent = 
        statistics.accessible_count.toLocaleString();
    
    document.getElementById('restriction-percentage').textContent = 
        statistics.geo_restricted_percentage.toFixed(1) + '%';
    
    // Format last updated date
    if (statistics.last_check) {
        const date = new Date(statistics.last_check);
        document.getElementById('last-updated').textContent = 
            date.toLocaleString();
    }
}

// Create charts
function createCharts() {
    if (!statistics) return;

    // Status Chart (Pie)
    const statusCtx = document.getElementById('status-chart');
    if (statusCtx) {
        new Chart(statusCtx, {
            type: 'pie',
            data: {
                labels: ['Accessible', 'Geo-Restricted', 'Unknown'],
                datasets: [{
                    data: [
                        statistics.accessible_count,
                        statistics.geo_restricted_count,
                        statistics.unknown_count
                    ],
                    backgroundColor: [
                        '#00D7B6',  // Primary teal for accessible
                        '#FF6B6B',  // Softer coral-red for restricted
                        '#95a5a6'   // Grey for unknown
                    ],
                    borderWidth: 2,
                    borderColor: '#fff',
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    // Contents by Year (Bar)
    const yearCtx = document.getElementById('year-chart');
    if (yearCtx && statistics.by_year) {
        const years = Object.keys(statistics.by_year).sort();
        const yearCounts = years.map(year => statistics.by_year[year]);

        new Chart(yearCtx, {
            type: 'bar',
            data: {
                labels: years,
                datasets: [{
                    label: 'Edukia kopurua',
                    data: yearCounts,
                    backgroundColor: '#00D7B6',
                    borderColor: '#00b89a',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        ticks: {
                            maxRotation: 45,
                            minRotation: 0
                        }
                    },
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // Contents by Language (Horizontal Bar)
    const langCtx = document.getElementById('language-chart');
    if (langCtx && statistics.by_language) {
        const languages = Object.keys(statistics.by_language);
        const langCounts = languages.map(code => statistics.by_language[code]);

        new Chart(langCtx, {
            type: 'bar',
            data: {
                labels: languages.map(code => code.toUpperCase()),
                datasets: [{
                    label: 'Edukia kopurua',
                    data: langCounts,
                    backgroundColor: '#00D7B6',
                    borderColor: '#00b89a',
                    borderWidth: 1
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // Contents by Age Rating (Bar)
    const ageCtx = document.getElementById('age-rating-chart');
    if (ageCtx && statistics.by_age_rating) {
        const ratings = Object.keys(statistics.by_age_rating);
        const ratingCounts = ratings.map(r => statistics.by_age_rating[r]);

        new Chart(ageCtx, {
            type: 'bar',
            data: {
                labels: ratings,
                datasets: [{
                    label: 'Edukia kopurua',
                    data: ratingCounts,
                    backgroundColor: '#00D7B6',
                    borderColor: '#00b89a',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // Geo-Restricted by Platform (Stacked Bar)
    const platformCtx = document.getElementById('geo-platform-chart');
    if (platformCtx && statistics.geo_restricted_by_platform) {
        const platforms = Object.keys(statistics.geo_restricted_by_platform);
        const restricted = platforms.map(p => statistics.geo_restricted_by_platform[p].restricted || 0);
        const accessible = platforms.map(p => statistics.geo_restricted_by_platform[p].accessible || 0);

        new Chart(platformCtx, {
            type: 'bar',
            data: {
                labels: platforms.map(p => p.replace('.eus', '').replace('.', ' ').replace(/\b\w/g, l => l.toUpperCase())),
                datasets: [
                    {
                        label: 'Geo-murriztua',
                        data: restricted,
                        backgroundColor: '#FF6B6B',
                        borderColor: '#e85c5c',
                        borderWidth: 1
                    },
                    {
                        label: 'Murriztu gabea',
                        data: accessible,
                        backgroundColor: '#00D7B6',
                        borderColor: '#00b89a',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { position: 'bottom' }
                },
                scales: {
                    x: {
                        stacked: true
                    },
                    y: {
                        stacked: true,
                        beginAtZero: true
                    }
                }
            }
        });
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', loadStatistics);
