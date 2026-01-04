// Content List JavaScript
let allContent = [];
let filteredContent = [];
let currentSort = { field: null, direction: 'asc' };

// Load content data
async function loadContent() {
    try {
        const response = await fetch('data/content.json');
        const data = await response.json();
        allContent = data.content || [];
        filteredContent = [...allContent];
        
        populateTypeFilter();
        renderTable();
        updateResultsCount();
    } catch (error) {
        console.error('Error loading content:', error);
        document.getElementById('content-tbody').innerHTML = 
            '<tr><td colspan="7" style="color: red;">Error loading content. Please ensure data/content.json exists.</td></tr>';
    }
}

// Populate type filter dropdown
function populateTypeFilter() {
    const typeFilter = document.getElementById('type-filter');
    const types = [...new Set(allContent.map(item => item.type).filter(Boolean))].sort();
    
    types.forEach(type => {
        const option = document.createElement('option');
        option.value = type;
        option.textContent = type.charAt(0).toUpperCase() + type.slice(1);
        typeFilter.appendChild(option);
    });
}

// Apply filters
function applyFilters() {
    const searchTerm = document.getElementById('search-input').value.toLowerCase();
    const typeFilter = document.getElementById('type-filter').value;
    const restrictionFilter = document.getElementById('restriction-filter').value;
    
    filteredContent = allContent.filter(item => {
        // Search filter
        if (searchTerm && !item.title?.toLowerCase().includes(searchTerm)) {
            return false;
        }
        
        // Type filter
        if (typeFilter && item.type !== typeFilter) {
            return false;
        }
        
        // Restriction filter
        if (restrictionFilter !== '') {
            const isRestricted = item.is_geo_restricted;
            if (restrictionFilter === 'true' && !isRestricted) return false;
            if (restrictionFilter === 'false' && isRestricted !== false) return false;
            if (restrictionFilter === 'null' && isRestricted !== null) return false;
        }
        
        return true;
    });
    
    // Apply current sort
    if (currentSort.field) {
        sortContent(currentSort.field, currentSort.direction, false);
    }
    
    renderTable();
    updateResultsCount();
}

// Sort content
function sortContent(field, direction = 'asc', updateUI = true) {
    filteredContent.sort((a, b) => {
        let aVal = a[field];
        let bVal = b[field];
        
        // Handle null/undefined
        if (aVal == null) aVal = '';
        if (bVal == null) bVal = '';
        
        // Handle numbers
        if (typeof aVal === 'number' && typeof bVal === 'number') {
            return direction === 'asc' ? aVal - bVal : bVal - aVal;
        }
        
        // Handle strings
        aVal = String(aVal).toLowerCase();
        bVal = String(bVal).toLowerCase();
        
        if (direction === 'asc') {
            return aVal.localeCompare(bVal);
        } else {
            return bVal.localeCompare(aVal);
        }
    });
    
    if (updateUI) {
        currentSort = { field, direction };
        updateSortIndicators();
        renderTable();
    }
}

// Update sort indicators
function updateSortIndicators() {
    document.querySelectorAll('th').forEach(th => {
        th.removeAttribute('data-sort-direction');
        th.querySelector('.sort-indicator').textContent = '';
    });
    
    if (currentSort.field) {
        const th = document.querySelector(`th[data-sort="${currentSort.field}"]`);
        if (th) {
            th.setAttribute('data-sort-direction', currentSort.direction);
        }
    }
}

// Render table
function renderTable() {
    const tbody = document.getElementById('content-tbody');
    
    if (filteredContent.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="loading">No content found matching filters.</td></tr>';
        return;
    }
    
    tbody.innerHTML = filteredContent.map(item => {
        const restrictedStatus = item.is_geo_restricted === true ? 'Restricted' :
                                item.is_geo_restricted === false ? 'Accessible' : 'Unknown';
        const statusClass = item.is_geo_restricted === true ? 'status-restricted' :
                           item.is_geo_restricted === false ? 'status-accessible' : 'status-unknown';
        
        const duration = item.duration ? formatDuration(item.duration) : '-';
        const seriesInfo = item.series_title ? 
            `${item.series_title}${item.season_number ? ` S${item.season_number}` : ''}${item.episode_number ? ` E${item.episode_number}` : ''}` : 
            '-';
        
        return `
            <tr>
                <td>${escapeHtml(item.title || item.slug)}</td>
                <td>${escapeHtml(item.type || 'unknown')}</td>
                <td>${escapeHtml(seriesInfo)}</td>
                <td>${duration}</td>
                <td>${item.year || '-'}</td>
                <td><span class="status-badge ${statusClass}">${restrictedStatus}</span></td>
                <td>${escapeHtml(item.restriction_type || '-')}</td>
            </tr>
        `;
    }).join('');
}

// Format duration (seconds to HH:MM:SS)
function formatDuration(seconds) {
    if (!seconds) return '-';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
        return `${hours}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }
    return `${minutes}:${String(secs).padStart(2, '0')}`;
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Update results count
function updateResultsCount() {
    document.getElementById('results-count').textContent = filteredContent.length.toLocaleString();
}

// Clear filters
function clearFilters() {
    document.getElementById('search-input').value = '';
    document.getElementById('type-filter').value = '';
    document.getElementById('restriction-filter').value = '';
    applyFilters();
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    loadContent();
    
    // Filter inputs
    document.getElementById('search-input').addEventListener('input', applyFilters);
    document.getElementById('type-filter').addEventListener('change', applyFilters);
    document.getElementById('restriction-filter').addEventListener('change', applyFilters);
    document.getElementById('clear-filters').addEventListener('click', clearFilters);
    
    // Sort headers
    document.querySelectorAll('th[data-sort]').forEach(th => {
        th.addEventListener('click', () => {
            const field = th.getAttribute('data-sort');
            const currentDirection = currentSort.field === field ? currentSort.direction : 'asc';
            const newDirection = currentDirection === 'asc' ? 'desc' : 'asc';
            sortContent(field, newDirection);
        });
    });
});
