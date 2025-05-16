// Dashboard JavaScript for AI Assistant Platform

document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts and metrics
    initializeDashboardCharts();
    
    // Update dashboard metrics every 10 seconds
    fetchDashboardMetrics();
    setInterval(fetchDashboardMetrics, 10000);
    
    // Fetch recent Kafka messages
    fetchRecentKafkaMessages();
    
    // Fetch pipeline status
    fetchPipelineStatus();
    
    // Fetch latest anomalies
    fetchLatestAnomalies();
    
    // Socket.IO event listeners for real-time updates
    socket.on('dashboard_metrics_update', (data) => {
        updateDashboardMetrics(data);
    });
    
    socket.on('kafka_message', (data) => {
        addRecentKafkaMessage(data);
    });
    
    socket.on('pipeline_status_update', (data) => {
        updatePipelineStatus(data);
    });
    
    socket.on('anomaly_detected', (data) => {
        addLatestAnomaly(data);
    });
});

// Initialize all dashboard charts
function initializeDashboardCharts() {
    // LLM Usage Trends Chart
    const llmUsageCtx = document.getElementById('llmUsageChart');
    if (llmUsageCtx) {
        const llmUsageChart = new Chart(llmUsageCtx, {
            type: 'line',
            data: {
                labels: ['7 Days Ago', '6 Days Ago', '5 Days Ago', '4 Days Ago', '3 Days Ago', '2 Days Ago', 'Yesterday', 'Today'],
                datasets: [{
                    label: 'Queries',
                    data: [65, 78, 92, 85, 110, 95, 120, 130],
                    borderColor: 'rgba(75, 192, 192, 1)',
                    tension: 0.1,
                    fill: false
                }, {
                    label: 'Documents Processed',
                    data: [15, 25, 18, 30, 42, 38, 55, 62],
                    borderColor: 'rgba(255, 159, 64, 1)',
                    tension: 0.1,
                    fill: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'LLM Activity Over Time'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
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

    // Resource Distribution Chart
    const resourceDistributionCtx = document.getElementById('resourceDistributionChart');
    if (resourceDistributionCtx) {
        const resourceDistributionChart = new Chart(resourceDistributionCtx, {
            type: 'doughnut',
            data: {
                labels: ['LLM Processing', 'RAG Operations', 'Anomaly Detection', 'Data Pipelines', 'Other'],
                datasets: [{
                    data: [40, 25, 15, 15, 5],
                    backgroundColor: [
                        'rgba(54, 162, 235, 0.7)',
                        'rgba(75, 192, 192, 0.7)',
                        'rgba(255, 99, 132, 0.7)',
                        'rgba(255, 205, 86, 0.7)',
                        'rgba(201, 203, 207, 0.7)'
                    ],
                    borderColor: [
                        'rgba(54, 162, 235, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(255, 99, 132, 1)',
                        'rgba(255, 205, 86, 1)',
                        'rgba(201, 203, 207, 1)'
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
                    },
                    title: {
                        display: true,
                        text: 'Resource Allocation'
                    }
                }
            }
        });
    }

    // GPU Utilization Chart
    const gpuUtilizationCtx = document.getElementById('gpuUtilizationChart');
    if (gpuUtilizationCtx) {
        const gpuUtilizationChart = new Chart(gpuUtilizationCtx, {
            type: 'line',
            data: {
                labels: Array.from({length: 12}, (_, i) => `${11-i} min ago`).reverse(),
                datasets: [{
                    label: 'GPU Utilization (%)',
                    data: [78, 82, 85, 90, 92, 86, 88, 91, 85, 80, 83, 87],
                    borderColor: 'rgba(255, 99, 132, 1)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    fill: true
                }, {
                    label: 'GPU Memory Usage (%)',
                    data: [65, 68, 70, 72, 75, 73, 78, 80, 77, 75, 72, 74],
                    borderColor: 'rgba(54, 162, 235, 1)',
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Tesla P40 GPU Utilization'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        suggestedMax: 100
                    }
                }
            }
        });
    }
}

// Fetch dashboard metrics from the server
async function fetchDashboardMetrics() {
    try {
        const response = await fetchWithTimeout('/api/dashboard/metrics');
        const data = await response.json();
        if (data) {
            updateDashboardMetrics(data);
        } else {
            // If data is null or undefined, use default values
            updateDashboardMetrics({
                llm_requests: 250,
                today_llm_requests: 25,
                documents_indexed: 120,
                today_indexed: 15,
                anomalies_detected: 45,
                today_anomalies: 5,
                pipeline_jobs: 12,
                active_jobs: 3
            });
        }
    } catch (error) {
        console.error('Error fetching dashboard metrics:', error);
        // Use default metrics on error
        updateDashboardMetrics({
            llm_requests: 250,
            today_llm_requests: 25,
            documents_indexed: 120,
            today_indexed: 15,
            anomalies_detected: 45,
            today_anomalies: 5,
            pipeline_jobs: 12,
            active_jobs: 3
        });
    }
}

// Update dashboard metrics with the fetched data
function updateDashboardMetrics(data) {
    // Update counter cards - direct values from API
    if (document.getElementById('llm-request-count') && data.llm_requests !== undefined) {
        document.getElementById('llm-request-count').textContent = data.llm_requests;
    }
    
    if (document.getElementById('docs-indexed-count') && data.documents_indexed !== undefined) {
        document.getElementById('docs-indexed-count').textContent = data.documents_indexed;
    }
    
    if (document.getElementById('anomalies-count') && data.anomalies_detected !== undefined) {
        document.getElementById('anomalies-count').textContent = data.anomalies_detected;
    }
    
    if (document.getElementById('pipeline-jobs-count') && data.pipeline_jobs !== undefined) {
        document.getElementById('pipeline-jobs-count').textContent = data.pipeline_jobs;
    }
    
    // Update system health metrics
    if (data.system_health) {
        const { memory_usage, cpu_load, disk_usage, network_throughput } = data.system_health;
        
        if (document.getElementById('memory-usage')) {
            const memoryBar = document.getElementById('memory-usage');
            memoryBar.style.width = `${memory_usage}%`;
            memoryBar.textContent = `${memory_usage}%`;
            
            // Change color based on usage
            if (memory_usage > 80) {
                memoryBar.className = 'progress-bar bg-danger';
            } else if (memory_usage > 60) {
                memoryBar.className = 'progress-bar bg-warning';
            } else {
                memoryBar.className = 'progress-bar bg-info';
            }
        }
        
        if (document.getElementById('cpu-load')) {
            const cpuBar = document.getElementById('cpu-load');
            cpuBar.style.width = `${cpu_load}%`;
            cpuBar.textContent = `${cpu_load}%`;
            
            if (cpu_load > 80) {
                cpuBar.className = 'progress-bar bg-danger';
            } else if (cpu_load > 60) {
                cpuBar.className = 'progress-bar bg-warning';
            } else {
                cpuBar.className = 'progress-bar bg-success';
            }
        }
        
        if (document.getElementById('disk-usage')) {
            const diskBar = document.getElementById('disk-usage');
            diskBar.style.width = `${disk_usage}%`;
            diskBar.textContent = `${disk_usage}%`;
            
            if (disk_usage > 85) {
                diskBar.className = 'progress-bar bg-danger';
            } else if (disk_usage > 70) {
                diskBar.className = 'progress-bar bg-warning';
            } else {
                diskBar.className = 'progress-bar bg-primary';
            }
        }
        
        if (document.getElementById('network-throughput')) {
            const networkBar = document.getElementById('network-throughput');
            networkBar.style.width = `${network_throughput}%`;
            networkBar.textContent = `${network_throughput}%`;
        }
    }
}

// Fetch recent Kafka messages
async function fetchRecentKafkaMessages() {
    try {
        const response = await fetchWithTimeout('/api/dashboard/recent-kafka-messages');
        const data = await response.json();
        
        const messagesContainer = document.getElementById('recent-messages');
        if (!messagesContainer) return;
        
        // Clear existing messages
        messagesContainer.innerHTML = '';
        
        // Add messages to the container
        data.forEach(message => {
            addRecentKafkaMessage(message);
        });
    } catch (error) {
        handleFetchError(error, 'fetch Kafka messages');
    }
}

// Add a recent Kafka message to the list
function addRecentKafkaMessage(message) {
    const messagesContainer = document.getElementById('recent-messages');
    if (!messagesContainer) return;
    
    const messageItem = document.createElement('li');
    messageItem.className = 'list-group-item d-flex justify-content-between align-items-center';
    
    const timeAgo = message.timestamp ? getTimeAgo(new Date(message.timestamp)) : 'Just now';
    
    messageItem.innerHTML = `
        <div>
            <strong>${escapeHtml(message.topic)}</strong>
            <div class="text-muted small">${escapeHtml(message.content)}</div>
        </div>
        <span class="badge bg-primary rounded-pill">${timeAgo}</span>
    `;
    
    // Add to the top of the list
    messagesContainer.insertBefore(messageItem, messagesContainer.firstChild);
    
    // Remove oldest message if more than 5
    if (messagesContainer.children.length > 5) {
        messagesContainer.removeChild(messagesContainer.lastChild);
    }
}

// Fetch pipeline status
async function fetchPipelineStatus() {
    try {
        const response = await fetchWithTimeout('/api/dashboard/pipeline-status');
        const data = await response.json();
        
        const pipelineContainer = document.getElementById('pipeline-status');
        if (!pipelineContainer) return;
        
        // Clear existing items
        pipelineContainer.innerHTML = '';
        
        // Add pipeline items
        // Direct use of returned jobs array
        data.forEach(pipeline => {
            updatePipelineStatus(pipeline);
        });
    } catch (error) {
        handleFetchError(error, 'fetch pipeline status');
    }
}

// Update pipeline status in the list
function updatePipelineStatus(pipeline) {
    const pipelineContainer = document.getElementById('pipeline-status');
    if (!pipelineContainer) return;
    
    // Check if pipeline already exists
    const existingPipeline = document.querySelector(`[data-pipeline-id="${pipeline.id}"]`);
    
    if (existingPipeline) {
        // Update existing pipeline
        const statusBadge = existingPipeline.querySelector('.badge');
        statusBadge.className = `badge ${getStatusBadgeClass(pipeline.status)} rounded-pill`;
        statusBadge.textContent = pipeline.status;
        
        const descriptionElement = existingPipeline.querySelector('.text-muted');
        descriptionElement.textContent = pipeline.description;
    } else {
        // Create new pipeline element
        const pipelineItem = document.createElement('li');
        pipelineItem.className = 'list-group-item d-flex justify-content-between align-items-center';
        pipelineItem.setAttribute('data-pipeline-id', pipeline.id);
        
        pipelineItem.innerHTML = `
            <div>
                <strong>${escapeHtml(pipeline.name)}</strong>
                <div class="text-muted small">${escapeHtml(pipeline.description)}</div>
            </div>
            <span class="badge ${getStatusBadgeClass(pipeline.status)} rounded-pill">${pipeline.status}</span>
        `;
        
        pipelineContainer.appendChild(pipelineItem);
        
        // Remove oldest pipeline if more than 5
        if (pipelineContainer.children.length > 5) {
            pipelineContainer.removeChild(pipelineContainer.firstChild);
        }
    }
}

// Fetch latest anomalies
async function fetchLatestAnomalies() {
    try {
        const response = await fetchWithTimeout('/api/dashboard/latest-anomalies');
        const data = await response.json();
        
        const anomaliesContainer = document.getElementById('latest-anomalies');
        if (!anomaliesContainer) return;
        
        // Clear existing anomalies
        anomaliesContainer.innerHTML = '';
        
        // Add anomalies to the container
        data.forEach(anomaly => {
            addLatestAnomaly(anomaly);
        });
    } catch (error) {
        handleFetchError(error, 'fetch latest anomalies');
    }
}

// Add a latest anomaly to the list
function addLatestAnomaly(anomaly) {
    const anomaliesContainer = document.getElementById('latest-anomalies');
    if (!anomaliesContainer) return;
    
    const anomalyItem = document.createElement('li');
    anomalyItem.className = 'list-group-item d-flex justify-content-between align-items-center';
    
    anomalyItem.innerHTML = `
        <div>
            <strong>${escapeHtml(anomaly.title)}</strong>
            <div class="text-muted small">${escapeHtml(anomaly.description)}</div>
        </div>
        <a href="/anomalies?id=${anomaly.id}" class="btn btn-sm btn-outline-primary">Details</a>
    `;
    
    // Add to the top of the list
    anomaliesContainer.insertBefore(anomalyItem, anomaliesContainer.firstChild);
    
    // Remove oldest anomaly if more than 5
    if (anomaliesContainer.children.length > 5) {
        anomaliesContainer.removeChild(anomaliesContainer.lastChild);
    }
}

// Helper function to get a human-readable time ago string
function getTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);
    
    let interval = seconds / 31536000;
    if (interval > 1) {
        return Math.floor(interval) + 'y ago';
    }
    
    interval = seconds / 2592000;
    if (interval > 1) {
        return Math.floor(interval) + 'mo ago';
    }
    
    interval = seconds / 86400;
    if (interval > 1) {
        return Math.floor(interval) + 'd ago';
    }
    
    interval = seconds / 3600;
    if (interval > 1) {
        return Math.floor(interval) + 'h ago';
    }
    
    interval = seconds / 60;
    if (interval > 1) {
        return Math.floor(interval) + 'm ago';
    }
    
    return Math.floor(seconds) + 's ago';
}

// Helper function to get the appropriate badge class based on status
function getStatusBadgeClass(status) {
    if (!status) return 'bg-secondary';
    
    status = status.toLowerCase();
    
    if (status === 'running' || status === 'success' || status === 'completed') {
        return 'bg-success';
    } else if (status === 'scheduled') {
        return 'bg-secondary';
    } else if (status === 'warning' || status === 'pending') {
        return 'bg-warning';
    } else if (status === 'error' || status === 'failed') {
        return 'bg-danger';
    } else {
        return 'bg-info';
    }
}

// Helper function to safely handle fetch errors
function handleFetchError(error, operation) {
    console.error(`Error ${operation}:`, error);
    // Could add user-facing error messages here if needed
}

// Helper function for fetch with timeout
async function fetchWithTimeout(url, options = {}, timeout = 5000) {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);
    
    try {
        const response = await fetch(url, {
            ...options,
            signal: controller.signal
        });
        clearTimeout(id);
        return response;
    } catch (error) {
        clearTimeout(id);
        throw error;
    }
}
