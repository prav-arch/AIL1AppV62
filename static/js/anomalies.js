// Anomalies JavaScript for AI Assistant Platform

document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts
    initializeAnomalyCharts();
    
    // Initialize network visualization
    initializeNetworkTopology();
    
    // Setup event handlers for "Get Recommendations" buttons
    setupRecommendationButtons();
    
    // Initialize DataTable for anomalies
    if ($.fn.DataTable) {
        $('#anomalies-table').DataTable({
            responsive: true,
            order: [[1, 'desc']] // Sort by timestamp desc
        });
    }
    
    // Refresh button
    document.getElementById('refresh-anomalies')?.addEventListener('click', fetchAnomalies);
    
    // Filter buttons
    const filterButtons = document.querySelectorAll('[data-filter]');
    filterButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            filterAnomalies(this.getAttribute('data-filter'));
        });
    });
    
    // Fetch initial data
    fetchAnomalyStats();
    fetchAnomalies();
    
    // Setup Socket.IO event listeners for real-time updates
    socket.on('new_anomaly', (data) => {
        addNewAnomaly(data);
        updateAnomalyStats();
    });
    
    socket.on('anomaly_recommendation', (data) => {
        updateRecommendationContent(data);
    });
});

// Initialize anomaly charts
function initializeAnomalyCharts() {
    // Anomaly Trends Chart
    const anomalyTrendsCtx = document.getElementById('anomaly-trends-chart');
    if (anomalyTrendsCtx) {
        new Chart(anomalyTrendsCtx, {
            type: 'line',
            data: {
                labels: ['7 Days Ago', '6 Days Ago', '5 Days Ago', '4 Days Ago', '3 Days Ago', '2 Days Ago', 'Yesterday', 'Today'],
                datasets: [
                    {
                        label: 'Critical',
                        data: [3, 5, 4, 6, 2, 3, 4, 5],
                        borderColor: 'rgba(255, 99, 132, 1)',
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        fill: true,
                        tension: 0.1
                    },
                    {
                        label: 'Warning',
                        data: [8, 7, 10, 9, 6, 9, 11, 12],
                        borderColor: 'rgba(255, 205, 86, 1)',
                        backgroundColor: 'rgba(255, 205, 86, 0.2)',
                        fill: true,
                        tension: 0.1
                    },
                    {
                        label: 'Info',
                        data: [5, 4, 6, 3, 7, 5, 6, 7],
                        borderColor: 'rgba(54, 162, 235, 1)',
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        fill: true,
                        tension: 0.1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Anomaly Detection Trends'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        stacked: false
                    }
                }
            }
        });
    }

    // Anomaly Types Chart
    const anomalyTypesCtx = document.getElementById('anomaly-types-chart');
    if (anomalyTypesCtx) {
        new Chart(anomalyTypesCtx, {
            type: 'doughnut',
            data: {
                labels: ['Network', 'System', 'Database', 'Application', 'Security'],
                datasets: [{
                    data: [8, 5, 3, 4, 4],
                    backgroundColor: [
                        'rgba(54, 162, 235, 0.7)',
                        'rgba(255, 99, 132, 0.7)',
                        'rgba(255, 205, 86, 0.7)',
                        'rgba(75, 192, 192, 0.7)',
                        'rgba(153, 102, 255, 0.7)'
                    ],
                    borderColor: [
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 99, 132, 1)',
                        'rgba(255, 205, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    // Traffic In Chart
    const trafficInCtx = document.getElementById('traffic-in-chart');
    if (trafficInCtx) {
        new Chart(trafficInCtx, {
            type: 'line',
            data: {
                labels: Array.from({length: 12}, (_, i) => `${11-i}h ago`).reverse(),
                datasets: [{
                    label: 'Inbound Traffic (MB/s)',
                    data: [2.8, 3.1, 3.5, 4.2, 5.1, 8.7, 7.2, 5.8, 4.9, 4.5, 4.1, 3.8],
                    borderColor: 'rgba(54, 162, 235, 1)',
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Inbound Network Traffic'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // Traffic Out Chart
    const trafficOutCtx = document.getElementById('traffic-out-chart');
    if (trafficOutCtx) {
        new Chart(trafficOutCtx, {
            type: 'line',
            data: {
                labels: Array.from({length: 12}, (_, i) => `${11-i}h ago`).reverse(),
                datasets: [{
                    label: 'Outbound Traffic (MB/s)',
                    data: [1.5, 1.7, 1.9, 2.2, 2.8, 4.5, 3.8, 3.1, 2.7, 2.3, 2.0, 1.8],
                    borderColor: 'rgba(255, 99, 132, 1)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Outbound Network Traffic'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
}

// Initialize network topology visualization using D3.js
function initializeNetworkTopology() {
    const container = document.getElementById('network-topology');
    if (!container) return;
    
    // Set up SVG
    const width = container.clientWidth;
    const height = container.clientHeight;
    
    const svg = d3.select('#network-topology')
        .append('svg')
        .attr('width', width)
        .attr('height', height);
    
    // Sample network data
    const nodes = [
        { id: 1, name: "Router", group: 1, status: "normal" },
        { id: 2, name: "Firewall", group: 1, status: "normal" },
        { id: 3, name: "App Server 1", group: 2, status: "normal" },
        { id: 4, name: "App Server 2", group: 2, status: "warning" },
        { id: 5, name: "Database", group: 3, status: "normal" },
        { id: 6, name: "Storage", group: 3, status: "normal" },
        { id: 7, name: "Client 1", group: 4, status: "normal" },
        { id: 8, name: "Client 2", group: 4, status: "critical" },
        { id: 9, name: "Client 3", group: 4, status: "normal" }
    ];
    
    const links = [
        { source: 1, target: 2 },
        { source: 2, target: 3 },
        { source: 2, target: 4 },
        { source: 3, target: 5 },
        { source: 4, target: 5 },
        { source: 5, target: 6 },
        { source: 2, target: 7 },
        { source: 2, target: 8 },
        { source: 2, target: 9 }
    ];
    
    // Create a force simulation
    const simulation = d3.forceSimulation(nodes)
        .force("link", d3.forceLink(links).id(d => d.id).distance(100))
        .force("charge", d3.forceManyBody().strength(-300))
        .force("center", d3.forceCenter(width / 2, height / 2));
    
    // Add links
    const link = svg.append("g")
        .selectAll("line")
        .data(links)
        .enter().append("line")
        .attr("class", "link")
        .style("stroke-width", 2);
    
    // Color based on status
    const statusColor = (status) => {
        switch(status) {
            case "critical": return "#dc3545";
            case "warning": return "#ffc107";
            default: return "#28a745";
        }
    };
    
    // Add nodes
    const node = svg.append("g")
        .selectAll("circle")
        .data(nodes)
        .enter().append("circle")
        .attr("class", "node")
        .attr("r", 10)
        .style("fill", d => statusColor(d.status))
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended));
    
    // Add text labels
    const text = svg.append("g")
        .selectAll("text")
        .data(nodes)
        .enter().append("text")
        .attr("text-anchor", "middle")
        .attr("dy", 20)
        .style("fill", "#fff")
        .style("font-size", "8px")
        .text(d => d.name);
    
    // Add tooltip on hover
    node.append("title")
        .text(d => `${d.name}\nStatus: ${d.status}`);
    
    // Update positions on tick
    simulation.on("tick", () => {
        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);
        
        node
            .attr("cx", d => d.x)
            .attr("cy", d => d.y);
        
        text
            .attr("x", d => d.x)
            .attr("y", d => d.y);
    });
    
    // Drag functions
    function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }
    
    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }
    
    function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }
}

// Setup event handlers for recommendation buttons
function setupRecommendationButtons() {
    const recommendationButtons = document.querySelectorAll('.get-recommendation-btn');
    
    recommendationButtons.forEach(button => {
        button.addEventListener('click', function() {
            const anomalyId = this.getAttribute('data-anomaly-id');
            getRecommendationForAnomaly(anomalyId);
        });
    });
}

// Get recommendation for a specific anomaly
async function getRecommendationForAnomaly(anomalyId) {
    try {
        // Show modal with loading state
        const modal = new bootstrap.Modal(document.getElementById('recommendationModal'));
        modal.show();
        
        // Update modal title with anomaly ID
        document.getElementById('recommendationModalLabel').textContent = `Recommendations for Anomaly ${anomalyId}`;
        
        // Set loading state
        document.getElementById('recommendation-content').innerHTML = `
            <div class="d-flex justify-content-center my-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading recommendations...</span>
                </div>
            </div>
        `;
        
        // Fetch anomaly details
        const detailsResponse = await fetchWithTimeout(`/api/anomalies/${anomalyId}`);
        const anomalyDetails = await detailsResponse.json();
        
        // Update modal with anomaly details
        if (anomalyDetails.success) {
            document.getElementById('anomaly-title').textContent = anomalyDetails.data.title;
            document.getElementById('anomaly-description').textContent = anomalyDetails.data.description;
            
            // Update similar incidents
            updateSimilarIncidents(anomalyDetails.data.similar_incidents);
        }
        
        // Fetch recommendations
        const recommendationResponse = await fetchWithTimeout(`/api/anomalies/${anomalyId}/recommendation`);
        const recommendationData = await recommendationResponse.json();
        
        if (recommendationData.success) {
            // Update recommendation content
            updateRecommendationContent(recommendationData.data);
        } else {
            throw new Error(recommendationData.message || 'Failed to get recommendations');
        }
    } catch (error) {
        handleFetchError(error, 'get recommendations');
        
        // Update content with error
        document.getElementById('recommendation-content').innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Failed to get recommendations: ${error.message}
            </div>
        `;
    }
}

// Update recommendation content in the modal
function updateRecommendationContent(data) {
    const contentElement = document.getElementById('recommendation-content');
    if (!contentElement) return;
    
    let htmlContent = '';
    
    // Add immediate actions
    if (data.immediate_actions && data.immediate_actions.length > 0) {
        htmlContent += `
            <h6 class="fw-bold">Immediate Actions:</h6>
            <ol class="mb-3">
        `;
        
        data.immediate_actions.forEach(action => {
            htmlContent += `<li>${escapeHtml(action)}</li>`;
        });
        
        htmlContent += `</ol>`;
    }
    
    // Add root cause analysis
    if (data.root_cause_analysis) {
        htmlContent += `
            <h6 class="fw-bold">Root Cause Analysis:</h6>
            <p class="mb-3">${escapeHtml(data.root_cause_analysis)}</p>
        `;
    }
    
    // Add long-term recommendations
    if (data.long_term_recommendations && data.long_term_recommendations.length > 0) {
        htmlContent += `
            <h6 class="fw-bold">Long-term Recommendations:</h6>
            <ul class="mb-3">
        `;
        
        data.long_term_recommendations.forEach(recommendation => {
            htmlContent += `<li>${escapeHtml(recommendation)}</li>`;
        });
        
        htmlContent += `</ul>`;
    }
    
    // Add prevention tips
    if (data.prevention_tips) {
        htmlContent += `
            <h6 class="fw-bold">Prevention Tips:</h6>
            <p>${escapeHtml(data.prevention_tips)}</p>
        `;
    }
    
    // If no content was added, show a message
    if (!htmlContent) {
        htmlContent = `<p>No specific recommendations available for this anomaly.</p>`;
    }
    
    contentElement.innerHTML = htmlContent;
}

// Update similar incidents in the modal
function updateSimilarIncidents(incidents) {
    const incidentsElement = document.getElementById('similar-incidents');
    if (!incidentsElement) return;
    
    // Clear existing incidents
    incidentsElement.innerHTML = '';
    
    if (!incidents || incidents.length === 0) {
        incidentsElement.innerHTML = '<div class="alert alert-info">No similar past incidents found</div>';
        return;
    }
    
    // Add incidents to the list
    incidents.forEach(incident => {
        const incidentItem = document.createElement('li');
        incidentItem.className = 'list-group-item d-flex justify-content-between align-items-start';
        
        incidentItem.innerHTML = `
            <div class="ms-2 me-auto">
                <div class="fw-bold">${escapeHtml(incident.id)}: ${escapeHtml(incident.title)}</div>
                <span class="text-muted">${incident.date} - ${incident.resolution}</span>
            </div>
            <span class="badge bg-primary rounded-pill">${incident.similarity}% similar</span>
        `;
        
        incidentsElement.appendChild(incidentItem);
    });
}

// Fetch anomaly statistics
async function fetchAnomalyStats() {
    try {
        const response = await fetchWithTimeout('/api/anomalies/stats');
        const data = await response.json();
        
        if (data.success) {
            updateAnomalyStats(data.stats);
        } else {
            throw new Error(data.message || 'Failed to fetch anomaly statistics');
        }
    } catch (error) {
        handleFetchError(error, 'fetch anomaly statistics');
    }
}

// Update anomaly statistics display
function updateAnomalyStats(stats) {
    // Update counts
    if (document.getElementById('total-anomalies')) {
        document.getElementById('total-anomalies').textContent = stats.total || '0';
    }
    
    if (document.getElementById('critical-anomalies')) {
        document.getElementById('critical-anomalies').textContent = stats.critical || '0';
    }
    
    if (document.getElementById('warning-anomalies')) {
        document.getElementById('warning-anomalies').textContent = stats.warning || '0';
    }
    
    if (document.getElementById('info-anomalies')) {
        document.getElementById('info-anomalies').textContent = stats.info || '0';
    }
    
    // Update trend chart if available
    if (stats.trends && Chart.getChart('anomaly-trends-chart')) {
        const chart = Chart.getChart('anomaly-trends-chart');
        
        chart.data.datasets[0].data = stats.trends.critical || Array(8).fill(0);
        chart.data.datasets[1].data = stats.trends.warning || Array(8).fill(0);
        chart.data.datasets[2].data = stats.trends.info || Array(8).fill(0);
        
        chart.update();
    }
    
    // Update type distribution chart if available
    if (stats.type_distribution && Chart.getChart('anomaly-types-chart')) {
        const chart = Chart.getChart('anomaly-types-chart');
        
        chart.data.labels = Object.keys(stats.type_distribution);
        chart.data.datasets[0].data = Object.values(stats.type_distribution);
        
        chart.update();
    }
}

// Fetch anomalies list
async function fetchAnomalies() {
    try {
        const response = await fetchWithTimeout('/api/anomalies/list');
        const data = await response.json();
        
        if (data.success) {
            updateAnomaliesTable(data.anomalies);
        } else {
            throw new Error(data.message || 'Failed to fetch anomalies');
        }
    } catch (error) {
        handleFetchError(error, 'fetch anomalies');
    }
}

// Update anomalies table with fetched data
function updateAnomaliesTable(anomalies) {
    const tableBody = document.querySelector('#anomalies-table tbody');
    if (!tableBody) return;
    
    // If DataTable is initialized, destroy it first
    if ($.fn.DataTable.isDataTable('#anomalies-table')) {
        $('#anomalies-table').DataTable().destroy();
    }
    
    // Clear the table body
    tableBody.innerHTML = '';
    
    // Add anomalies to the table
    anomalies.forEach((anomaly) => {
        const tr = document.createElement('tr');
        tr.setAttribute('data-anomaly-id', anomaly.id);
        
        // Status badge class
        let severityBadgeClass = 'bg-info';
        if (anomaly.severity === 'Critical') {
            severityBadgeClass = 'bg-danger';
        } else if (anomaly.severity === 'Warning') {
            severityBadgeClass = 'bg-warning';
        }
        
        tr.innerHTML = `
            <td>${anomaly.id}</td>
            <td>${anomaly.timestamp}</td>
            <td>${escapeHtml(anomaly.type)}</td>
            <td>${escapeHtml(anomaly.source)}</td>
            <td>${escapeHtml(anomaly.description)}</td>
            <td><span class="badge ${severityBadgeClass}">${anomaly.severity}</span></td>
            <td>
                <button class="btn btn-sm btn-primary get-recommendation-btn" data-anomaly-id="${anomaly.id}">Get Recommendations</button>
            </td>
        `;
        
        tableBody.appendChild(tr);
    });
    
    // Re-attach event listeners for recommendation buttons
    setupRecommendationButtons();
    
    // Reinitialize DataTable
    $('#anomalies-table').DataTable({
        responsive: true,
        order: [[1, 'desc']] // Sort by timestamp desc
    });
}

// Add a new anomaly to the table
function addNewAnomaly(anomaly) {
    // Check if the anomaly already exists
    if (document.querySelector(`tr[data-anomaly-id="${anomaly.id}"]`)) {
        return;
    }
    
    const tableBody = document.querySelector('#anomalies-table tbody');
    if (!tableBody) return;
    
    // If DataTable is initialized, get its API
    let dataTable;
    if ($.fn.DataTable.isDataTable('#anomalies-table')) {
        dataTable = $('#anomalies-table').DataTable();
    }
    
    // Status badge class
    let severityBadgeClass = 'bg-info';
    if (anomaly.severity === 'Critical') {
        severityBadgeClass = 'bg-danger';
    } else if (anomaly.severity === 'Warning') {
        severityBadgeClass = 'bg-warning';
    }
    
    // Create row HTML
    const rowHtml = `
        <tr data-anomaly-id="${anomaly.id}">
            <td>${anomaly.id}</td>
            <td>${anomaly.timestamp}</td>
            <td>${escapeHtml(anomaly.type)}</td>
            <td>${escapeHtml(anomaly.source)}</td>
            <td>${escapeHtml(anomaly.description)}</td>
            <td><span class="badge ${severityBadgeClass}">${anomaly.severity}</span></td>
            <td>
                <button class="btn btn-sm btn-primary get-recommendation-btn" data-anomaly-id="${anomaly.id}">Get Recommendations</button>
            </td>
        </tr>
    `;
    
    // Add to DataTable if it exists, otherwise add to the table body
    if (dataTable) {
        dataTable.row.add($(rowHtml)).draw(false);
    } else {
        tableBody.insertAdjacentHTML('afterbegin', rowHtml);
    }
    
    // Re-attach event listeners for recommendation buttons
    setupRecommendationButtons();
    
    // Show notification
    showToast(`New anomaly detected: ${anomaly.description}`, 'warning');
    
    // Play alert sound if available
    const alertSound = new Audio('/static/sounds/alert.mp3');
    alertSound.play().catch(e => console.log('Could not play alert sound', e));
    
    // Update traffic charts if it's a network anomaly
    if (anomaly.type === 'Network' && Chart.getChart('traffic-in-chart') && Chart.getChart('traffic-out-chart')) {
        const trafficInChart = Chart.getChart('traffic-in-chart');
        const trafficOutChart = Chart.getChart('traffic-out-chart');
        
        // Add spike to most recent data point
        let inData = [...trafficInChart.data.datasets[0].data];
        let outData = [...trafficOutChart.data.datasets[0].data];
        
        if (anomaly.traffic_data) {
            inData[inData.length - 1] = anomaly.traffic_data.in;
            outData[outData.length - 1] = anomaly.traffic_data.out;
        } else {
            // If no specific data, just add a random spike
            inData[inData.length - 1] = inData[inData.length - 2] * 1.5;
            outData[outData.length - 1] = outData[outData.length - 2] * 1.5;
        }
        
        trafficInChart.data.datasets[0].data = inData;
        trafficOutChart.data.datasets[0].data = outData;
        
        trafficInChart.update();
        trafficOutChart.update();
    }
    
    // Update network visualization if it's a network anomaly
    if (anomaly.type === 'Network') {
        updateNetworkNodeStatus(anomaly.source, 'critical');
    }
}

// Filter anomalies by severity
function filterAnomalies(filter) {
    const dataTable = $('#anomalies-table').DataTable();
    
    if (filter === 'all') {
        dataTable.search('').columns().search('').draw();
    } else {
        dataTable.column(5).search(filter, true, false).draw();
    }
}

// Update network node status in the visualization
function updateNetworkNodeStatus(nodeName, status) {
    const svg = d3.select('#network-topology svg');
    if (!svg.empty()) {
        const nodes = svg.selectAll('.node');
        
        nodes.each(function(d) {
            if (d.name === nodeName) {
                d3.select(this)
                    .style('fill', status === 'critical' ? '#dc3545' : 
                           status === 'warning' ? '#ffc107' : '#28a745');
                
                // Add animation effect
                d3.select(this)
                    .transition()
                    .duration(200)
                    .attr('r', 15)
                    .transition()
                    .duration(200)
                    .attr('r', 10);
            }
        });
    }
}
