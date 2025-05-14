// Data Pipeline JavaScript for AI Assistant Platform

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tabs
    const triggerTabList = document.querySelectorAll('#pipeline-tabs button');
    triggerTabList.forEach(triggerEl => {
        triggerEl.addEventListener('click', function(event) {
            event.preventDefault();
            const tab = new bootstrap.Tab(this);
            tab.show();
        });
    });
    
    // Initialize DataTables
    initializeDataTables();
    
    // Initialize Charts
    initializeCharts();
    
    // Setup Timeline for jobs
    initializeJobTimeline();
    
    // Setup Event Listeners
    setupEventListeners();
    
    // Fetch initial data
    fetchNifiJobs();
    fetchAirflowDags();
    fetchJobStatus();
});

// Initialize DataTables
function initializeDataTables() {
    if ($.fn.DataTable) {
        $('#nifi-jobs-table').DataTable({
            responsive: true,
            pageLength: 10
        });
        
        $('#airflow-dags-table').DataTable({
            responsive: true,
            pageLength: 10
        });
    }
}

// Initialize Charts for Job Statistics
function initializeCharts() {
    // Job Success Rate Chart
    const jobSuccessCtx = document.getElementById('job-success-chart');
    if (jobSuccessCtx) {
        new Chart(jobSuccessCtx, {
            type: 'bar',
            data: {
                labels: ['7 Days Ago', '6 Days Ago', '5 Days Ago', '4 Days Ago', '3 Days Ago', '2 Days Ago', 'Yesterday', 'Today'],
                datasets: [
                    {
                        label: 'Success',
                        data: [42, 38, 45, 40, 43, 41, 44, 46],
                        backgroundColor: 'rgba(40, 167, 69, 0.7)',
                        borderColor: 'rgba(40, 167, 69, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Failed',
                        data: [3, 5, 2, 4, 1, 2, 1, 0],
                        backgroundColor: 'rgba(220, 53, 69, 0.7)',
                        borderColor: 'rgba(220, 53, 69, 1)',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        stacked: true
                    },
                    y: {
                        stacked: true,
                        beginAtZero: true
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Job Execution Results (Last 7 Days)'
                    }
                }
            }
        });
    }

    // Job Execution Time Chart
    const jobExecutionCtx = document.getElementById('job-execution-chart');
    if (jobExecutionCtx) {
        new Chart(jobExecutionCtx, {
            type: 'bar',
            data: {
                labels: ['Data Ingestion', 'ETL Process', 'PCAP Analysis', 'API Collection', 'Database Backup'],
                datasets: [{
                    label: 'Average Execution Time (minutes)',
                    data: [8, 15, 22, 5, 45],
                    backgroundColor: 'rgba(54, 162, 235, 0.7)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Minutes'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Average Job Execution Time'
                    }
                }
            }
        });
    }
}

// Initialize Job Timeline
function initializeJobTimeline() {
    const timelineContainer = document.getElementById('job-timeline');
    if (!timelineContainer) return;
    
    // Sample timeline data
    const jobs = [
        { id: 1, name: 'Daily Data Processing', start: '2023-05-20 00:00:00', end: '2023-05-20 00:23:45', status: 'completed' },
        { id: 2, name: 'Hourly Metrics Collection', start: '2023-05-20 14:00:00', end: '2023-05-20 14:02:12', status: 'completed' },
        { id: 3, name: 'Network PCAP Collection', start: '2023-05-20 00:00:00', end: '2023-05-21 00:00:00', status: 'running' },
        { id: 4, name: 'API Data Collector', start: '2023-05-20 10:00:00', end: '2023-05-20 10:05:30', status: 'completed' },
        { id: 5, name: 'Model Training', start: '2023-05-20 22:00:00', end: '2023-05-21 00:30:00', status: 'scheduled' }
    ];
    
    // Draw simple timeline
    timelineContainer.innerHTML = '';
    
    // Create a container for the timeline
    const svgContainer = document.createElement('div');
    svgContainer.style.width = '100%';
    svgContainer.style.height = '300px';
    svgContainer.style.position = 'relative';
    timelineContainer.appendChild(svgContainer);
    
    // Create SVG using D3
    const width = svgContainer.clientWidth;
    const height = svgContainer.clientHeight;
    const margin = { top: 20, right: 20, bottom: 30, left: 100 };
    
    const svg = d3.select(svgContainer)
        .append('svg')
        .attr('width', width)
        .attr('height', height);
    
    // Time scale
    const now = new Date();
    const timeStart = d3.timeDay.offset(now, -1); // 1 day ago
    const timeEnd = d3.timeDay.offset(now, 1); // 1 day ahead
    
    const x = d3.scaleTime()
        .domain([timeStart, timeEnd])
        .range([margin.left, width - margin.right]);
    
    // Job scale (vertical)
    const y = d3.scaleBand()
        .domain(jobs.map(d => d.name))
        .range([margin.top, height - margin.bottom])
        .padding(0.1);
    
    // Add axes
    svg.append('g')
        .attr('transform', `translate(0,${height - margin.bottom})`)
        .call(d3.axisBottom(x));
    
    svg.append('g')
        .attr('transform', `translate(${margin.left},0)`)
        .call(d3.axisLeft(y));
    
    // Helper function to parse dates
    const parseTime = d3.timeParse('%Y-%m-%d %H:%M:%S');
    
    // Color based on status
    const statusColor = (status) => {
        switch(status) {
            case 'completed': return '#28a745';
            case 'running': return '#007bff';
            case 'failed': return '#dc3545';
            case 'scheduled': return '#6c757d';
            default: return '#ffc107';
        }
    };
    
    // Add bars for jobs
    svg.selectAll('.job-bar')
        .data(jobs)
        .enter()
        .append('rect')
        .attr('class', 'job-bar')
        .attr('x', d => x(parseTime(d.start)))
        .attr('y', d => y(d.name))
        .attr('width', d => {
            const startTime = parseTime(d.start);
            const endTime = parseTime(d.end);
            return x(endTime) - x(startTime);
        })
        .attr('height', y.bandwidth())
        .attr('fill', d => statusColor(d.status))
        .attr('rx', 4)
        .attr('ry', 4)
        .on('mouseover', function(event, d) {
            d3.select(this).attr('opacity', 0.8);
            
            // Show tooltip
            const tooltip = d3.select('body')
                .append('div')
                .attr('class', 'tooltip')
                .style('position', 'absolute')
                .style('background', 'rgba(0, 0, 0, 0.8)')
                .style('color', 'white')
                .style('padding', '5px')
                .style('border-radius', '5px')
                .style('pointer-events', 'none')
                .style('z-index', 1000)
                .style('left', (event.pageX + 10) + 'px')
                .style('top', (event.pageY - 15) + 'px');
            
            tooltip.html(`
                <div><strong>${d.name}</strong></div>
                <div>Start: ${d.start}</div>
                <div>End: ${d.end}</div>
                <div>Status: ${d.status}</div>
            `);
        })
        .on('mouseout', function() {
            d3.select(this).attr('opacity', 1);
            d3.select('.tooltip').remove();
        });
}

// Setup Event Listeners
function setupEventListeners() {
    // Refresh buttons
    document.getElementById('refresh-nifi-btn')?.addEventListener('click', fetchNifiJobs);
    document.getElementById('refresh-airflow-btn')?.addEventListener('click', fetchAirflowDags);
    document.getElementById('refresh-jobs-btn')?.addEventListener('click', fetchJobStatus);
    
    // Create NiFi Job Modal Submit
    document.getElementById('create-nifi-job-submit')?.addEventListener('click', createNifiJob);
    
    // Create Schedule Modal Submit
    document.getElementById('create-schedule-submit')?.addEventListener('click', createSchedule);
    
    // Schedule type toggle
    document.getElementById('schedule-cron')?.addEventListener('change', toggleScheduleType);
    document.getElementById('schedule-simple')?.addEventListener('change', toggleScheduleType);
    
    // Cron presets
    document.querySelectorAll('.cron-preset').forEach(button => {
        button.addEventListener('click', function() {
            const cronExpression = this.getAttribute('data-cron');
            document.getElementById('cron-expression').value = cronExpression;
        });
    });
}

// Toggle between cron and simple schedule
function toggleScheduleType() {
    const cronOptions = document.getElementById('cron-schedule-options');
    const simpleOptions = document.getElementById('simple-schedule-options');
    
    if (document.getElementById('schedule-cron').checked) {
        cronOptions.classList.remove('d-none');
        simpleOptions.classList.add('d-none');
    } else {
        cronOptions.classList.add('d-none');
        simpleOptions.classList.remove('d-none');
    }
}

// Fetch NiFi Jobs
async function fetchNifiJobs() {
    try {
        const response = await fetchWithTimeout('/api/pipeline/nifi/jobs');
        const data = await response.json();
        
        if (data.success) {
            updateNifiJobs(data.jobs);
            updateNifiStats(data.stats);
        } else {
            throw new Error(data.message || 'Failed to fetch NiFi jobs');
        }
    } catch (error) {
        handleFetchError(error, 'fetch NiFi jobs');
    }
}

// Update NiFi Jobs Table
function updateNifiJobs(jobs) {
    const tableBody = document.querySelector('#nifi-jobs-table tbody');
    if (!tableBody) return;
    
    // If DataTable is initialized, destroy it first
    if ($.fn.DataTable.isDataTable('#nifi-jobs-table')) {
        $('#nifi-jobs-table').DataTable().destroy();
    }
    
    // Clear the table body
    tableBody.innerHTML = '';
    
    // Add jobs to the table
    jobs.forEach((job) => {
        const tr = document.createElement('tr');
        
        // Status badge class
        let statusBadgeClass = 'bg-success';
        if (job.status === 'Idle') {
            statusBadgeClass = 'bg-secondary';
        } else if (job.status === 'Failed') {
            statusBadgeClass = 'bg-danger';
        } else if (job.status === 'Warning') {
            statusBadgeClass = 'bg-warning';
        }
        
        // Action buttons
        let actionButtons = `
            <div class="btn-group btn-group-sm">
                <button class="btn btn-outline-primary" title="View" onclick="viewNifiJob('${job.id}')"><i class="fas fa-eye"></i></button>
        `;
        
        if (job.status === 'Running') {
            actionButtons += `
                <button class="btn btn-outline-warning" title="Pause" onclick="pauseNifiJob('${job.id}')"><i class="fas fa-pause"></i></button>
                <button class="btn btn-outline-danger" title="Stop" onclick="stopNifiJob('${job.id}')"><i class="fas fa-stop"></i></button>
            `;
        } else if (job.status === 'Idle') {
            actionButtons += `
                <button class="btn btn-outline-success" title="Start" onclick="startNifiJob('${job.id}')"><i class="fas fa-play"></i></button>
                <button class="btn btn-outline-danger" title="Delete" onclick="deleteNifiJob('${job.id}')"><i class="fas fa-trash"></i></button>
            `;
        } else {
            actionButtons += `
                <button class="btn btn-outline-success" title="Restart" onclick="restartNifiJob('${job.id}')"><i class="fas fa-redo"></i></button>
                <button class="btn btn-outline-danger" title="Delete" onclick="deleteNifiJob('${job.id}')"><i class="fas fa-trash"></i></button>
            `;
        }
        
        actionButtons += `</div>`;
        
        tr.innerHTML = `
            <td>${escapeHtml(job.name)}</td>
            <td>${escapeHtml(job.type)}</td>
            <td>${escapeHtml(job.source)}</td>
            <td>${escapeHtml(job.destination)}</td>
            <td><span class="badge ${statusBadgeClass}">${job.status}</span></td>
            <td>${job.last_run}</td>
            <td>${actionButtons}</td>
        `;
        
        tableBody.appendChild(tr);
    });
    
    // Reinitialize DataTable
    $('#nifi-jobs-table').DataTable({
        responsive: true,
        pageLength: 10
    });
}

// Update NiFi Stats
function updateNifiStats(stats) {
    if (document.getElementById('active-processors')) {
        document.getElementById('active-processors').textContent = stats.active_processors || '0';
    }
    
    if (document.getElementById('process-groups')) {
        document.getElementById('process-groups').textContent = stats.process_groups || '0';
    }
    
    if (document.getElementById('connections')) {
        document.getElementById('connections').textContent = stats.connections || '0';
    }
    
    if (document.getElementById('running-jobs')) {
        document.getElementById('running-jobs').textContent = stats.running_jobs || '0';
    }
}

// Fetch Airflow DAGs
async function fetchAirflowDags() {
    try {
        const response = await fetchWithTimeout('/api/pipeline/airflow/dags');
        const data = await response.json();
        
        if (data.success) {
            updateAirflowDags(data.dags);
            updateAirflowStats(data.stats);
        } else {
            throw new Error(data.message || 'Failed to fetch Airflow DAGs');
        }
    } catch (error) {
        handleFetchError(error, 'fetch Airflow DAGs');
    }
}

// Update Airflow DAGs Table
function updateAirflowDags(dags) {
    const tableBody = document.querySelector('#airflow-dags-table tbody');
    if (!tableBody) return;
    
    // If DataTable is initialized, destroy it first
    if ($.fn.DataTable.isDataTable('#airflow-dags-table')) {
        $('#airflow-dags-table').DataTable().destroy();
    }
    
    // Clear the table body
    tableBody.innerHTML = '';
    
    // Add DAGs to the table
    dags.forEach((dag) => {
        const tr = document.createElement('tr');
        
        // Status badge class
        let statusBadgeClass = 'bg-success';
        if (dag.status === 'Failed') {
            statusBadgeClass = 'bg-danger';
        } else if (dag.status === 'Running') {
            statusBadgeClass = 'bg-primary';
        }
        
        tr.innerHTML = `
            <td>${escapeHtml(dag.id)}</td>
            <td>${escapeHtml(dag.description)}</td>
            <td>${escapeHtml(dag.schedule)}</td>
            <td>${dag.last_run}</td>
            <td>${dag.duration}</td>
            <td><span class="badge ${statusBadgeClass}">${dag.status}</span></td>
            <td>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary" title="View" onclick="viewDag('${dag.id}')"><i class="fas fa-eye"></i></button>
                    <button class="btn btn-outline-success" title="Trigger" onclick="triggerDag('${dag.id}')"><i class="fas fa-play"></i></button>
                    <button class="btn btn-outline-secondary" title="Edit Schedule" onclick="editDagSchedule('${dag.id}')"><i class="fas fa-calendar-alt"></i></button>
                </div>
            </td>
        `;
        
        tableBody.appendChild(tr);
    });
    
    // Reinitialize DataTable
    $('#airflow-dags-table').DataTable({
        responsive: true,
        pageLength: 10
    });
}

// Update Airflow Stats
function updateAirflowStats(stats) {
    if (document.getElementById('active-dags')) {
        document.getElementById('active-dags').textContent = stats.active_dags || '0';
    }
    
    if (document.getElementById('paused-dags')) {
        document.getElementById('paused-dags').textContent = stats.paused_dags || '0';
    }
    
    if (document.getElementById('success-rate')) {
        document.getElementById('success-rate').textContent = stats.success_rate || '0%';
    }
    
    if (document.getElementById('running-tasks')) {
        document.getElementById('running-tasks').textContent = stats.running_tasks || '0';
    }
}

// Fetch Job Status
async function fetchJobStatus() {
    try {
        const response = await fetchWithTimeout('/api/pipeline/jobs/status');
        const data = await response.json();
        
        if (data.success) {
            updateJobCharts(data.stats);
            updateJobTimeline(data.jobs);
        } else {
            throw new Error(data.message || 'Failed to fetch job status');
        }
    } catch (error) {
        handleFetchError(error, 'fetch job status');
    }
}

// Update Job Charts
function updateJobCharts(stats) {
    // Update Success Rate Chart
    if (stats.success_rate && Chart.getChart('job-success-chart')) {
        const chart = Chart.getChart('job-success-chart');
        
        chart.data.datasets[0].data = stats.success_rate.success || Array(8).fill(0);
        chart.data.datasets[1].data = stats.success_rate.failed || Array(8).fill(0);
        
        chart.update();
    }
    
    // Update Execution Time Chart
    if (stats.execution_time && Chart.getChart('job-execution-chart')) {
        const chart = Chart.getChart('job-execution-chart');
        
        chart.data.labels = Object.keys(stats.execution_time) || [];
        chart.data.datasets[0].data = Object.values(stats.execution_time) || [];
        
        chart.update();
    }
}

// Update Job Timeline
function updateJobTimeline(jobs) {
    // Re-initialize the timeline with new data
    const timelineContainer = document.getElementById('job-timeline');
    if (!timelineContainer) return;
    
    timelineContainer.innerHTML = '';
    
    // Create a container for the timeline
    const svgContainer = document.createElement('div');
    svgContainer.style.width = '100%';
    svgContainer.style.height = '300px';
    svgContainer.style.position = 'relative';
    timelineContainer.appendChild(svgContainer);
    
    // Create SVG using D3
    const width = svgContainer.clientWidth;
    const height = svgContainer.clientHeight;
    const margin = { top: 20, right: 20, bottom: 30, left: 100 };
    
    const svg = d3.select(svgContainer)
        .append('svg')
        .attr('width', width)
        .attr('height', height);
    
    // Time scale
    const now = new Date();
    const timeStart = d3.timeDay.offset(now, -1); // 1 day ago
    const timeEnd = d3.timeDay.offset(now, 1); // 1 day ahead
    
    const x = d3.scaleTime()
        .domain([timeStart, timeEnd])
        .range([margin.left, width - margin.right]);
    
    // Job scale (vertical)
    const y = d3.scaleBand()
        .domain(jobs.map(d => d.name))
        .range([margin.top, height - margin.bottom])
        .padding(0.1);
    
    // Add axes
    svg.append('g')
        .attr('transform', `translate(0,${height - margin.bottom})`)
        .call(d3.axisBottom(x));
    
    svg.append('g')
        .attr('transform', `translate(${margin.left},0)`)
        .call(d3.axisLeft(y));
    
    // Helper function to parse dates
    const parseTime = d3.timeParse('%Y-%m-%d %H:%M:%S');
    
    // Color based on status
    const statusColor = (status) => {
        switch(status) {
            case 'completed': return '#28a745';
            case 'running': return '#007bff';
            case 'failed': return '#dc3545';
            case 'scheduled': return '#6c757d';
            default: return '#ffc107';
        }
    };
    
    // Add bars for jobs
    svg.selectAll('.job-bar')
        .data(jobs)
        .enter()
        .append('rect')
        .attr('class', 'job-bar')
        .attr('x', d => x(parseTime(d.start)))
        .attr('y', d => y(d.name))
        .attr('width', d => {
            const startTime = parseTime(d.start);
            const endTime = parseTime(d.end);
            return x(endTime) - x(startTime);
        })
        .attr('height', y.bandwidth())
        .attr('fill', d => statusColor(d.status))
        .attr('rx', 4)
        .attr('ry', 4);
}

// Create a new NiFi job
async function createNifiJob() {
    const jobName = document.getElementById('job-name').value;
    const jobType = document.getElementById('job-type').value;
    const jobPriority = document.getElementById('job-priority').value;
    const sourceType = document.getElementById('source-type').value;
    const sourcePath = document.getElementById('source-path').value;
    const sourceCredentials = document.getElementById('source-credentials').value;
    const sourceFormat = document.getElementById('source-format').value;
    const destinationType = document.getElementById('destination-type').value;
    const destinationPath = document.getElementById('destination-path').value;
    const destinationCredentials = document.getElementById('destination-credentials').value;
    const destinationFormat = document.getElementById('destination-format').value;
    const jobDescription = document.getElementById('job-description').value;
    
    if (!jobName || !sourcePath || !destinationPath) {
        showToast('Please fill in all required fields', 'warning');
        return;
    }
    
    try {
        const response = await fetchWithTimeout('/api/pipeline/nifi/jobs', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: jobName,
                type: jobType,
                priority: jobPriority,
                source: {
                    type: sourceType,
                    path: sourcePath,
                    credentials: sourceCredentials,
                    format: sourceFormat
                },
                destination: {
                    type: destinationType,
                    path: destinationPath,
                    credentials: destinationCredentials,
                    format: destinationFormat
                },
                description: jobDescription
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('NiFi job created successfully', 'success');
            
            // Close modal
            bootstrap.Modal.getInstance(document.getElementById('createNifiJobModal')).hide();
            
            // Reset form
            document.getElementById('create-nifi-job-form').reset();
            
            // Refresh NiFi jobs list
            fetchNifiJobs();
        } else {
            throw new Error(data.message || 'Failed to create NiFi job');
        }
    } catch (error) {
        handleFetchError(error, 'create NiFi job');
    }
}

// Create a new schedule
async function createSchedule() {
    const scheduleName = document.getElementById('schedule-name').value;
    const associatedJob = document.getElementById('associated-job').value;
    const scheduleType = document.getElementById('schedule-cron').checked ? 'cron' : 'simple';
    
    let scheduleValue;
    if (scheduleType === 'cron') {
        scheduleValue = document.getElementById('cron-expression').value;
    } else {
        const frequencyValue = document.getElementById('frequency-value').value;
        const frequencyUnit = document.getElementById('frequency-unit').value;
        scheduleValue = `${frequencyValue} ${frequencyUnit}`;
    }
    
    const timezone = document.getElementById('schedule-timezone').value;
    const description = document.getElementById('schedule-description').value;
    
    if (!scheduleName || !scheduleValue) {
        showToast('Please fill in all required fields', 'warning');
        return;
    }
    
    try {
        const response = await fetchWithTimeout('/api/pipeline/airflow/schedule', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: scheduleName,
                job_id: associatedJob,
                schedule_type: scheduleType,
                schedule_value: scheduleValue,
                timezone: timezone,
                description: description
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Schedule created successfully', 'success');
            
            // Close modal
            bootstrap.Modal.getInstance(document.getElementById('createScheduleModal')).hide();
            
            // Reset form
            document.getElementById('create-schedule-form').reset();
            
            // Refresh Airflow DAGs list
            fetchAirflowDags();
        } else {
            throw new Error(data.message || 'Failed to create schedule');
        }
    } catch (error) {
        handleFetchError(error, 'create schedule');
    }
}

// View NiFi job
function viewNifiJob(jobId) {
    window.location.href = `/pipeline/nifi/jobs/${jobId}`;
}

// Start a NiFi job
async function startNifiJob(jobId) {
    try {
        const response = await fetchWithTimeout(`/api/pipeline/nifi/jobs/${jobId}/start`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Job started successfully', 'success');
            fetchNifiJobs();
        } else {
            throw new Error(data.message || 'Failed to start job');
        }
    } catch (error) {
        handleFetchError(error, 'start job');
    }
}

// Pause a NiFi job
async function pauseNifiJob(jobId) {
    try {
        const response = await fetchWithTimeout(`/api/pipeline/nifi/jobs/${jobId}/pause`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Job paused successfully', 'success');
            fetchNifiJobs();
        } else {
            throw new Error(data.message || 'Failed to pause job');
        }
    } catch (error) {
        handleFetchError(error, 'pause job');
    }
}

// Stop a NiFi job
async function stopNifiJob(jobId) {
    try {
        const response = await fetchWithTimeout(`/api/pipeline/nifi/jobs/${jobId}/stop`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Job stopped successfully', 'success');
            fetchNifiJobs();
        } else {
            throw new Error(data.message || 'Failed to stop job');
        }
    } catch (error) {
        handleFetchError(error, 'stop job');
    }
}

// Restart a NiFi job
async function restartNifiJob(jobId) {
    try {
        const response = await fetchWithTimeout(`/api/pipeline/nifi/jobs/${jobId}/restart`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Job restarted successfully', 'success');
            fetchNifiJobs();
        } else {
            throw new Error(data.message || 'Failed to restart job');
        }
    } catch (error) {
        handleFetchError(error, 'restart job');
    }
}

// Delete a NiFi job
async function deleteNifiJob(jobId) {
    if (!confirm('Are you sure you want to delete this job? This action cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetchWithTimeout(`/api/pipeline/nifi/jobs/${jobId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Job deleted successfully', 'success');
            fetchNifiJobs();
        } else {
            throw new Error(data.message || 'Failed to delete job');
        }
    } catch (error) {
        handleFetchError(error, 'delete job');
    }
}

// View Airflow DAG
function viewDag(dagId) {
    window.location.href = `/pipeline/airflow/dags/${dagId}`;
}

// Trigger Airflow DAG
async function triggerDag(dagId) {
    try {
        const response = await fetchWithTimeout(`/api/pipeline/airflow/dags/${dagId}/trigger`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('DAG triggered successfully', 'success');
            fetchAirflowDags();
        } else {
            throw new Error(data.message || 'Failed to trigger DAG');
        }
    } catch (error) {
        handleFetchError(error, 'trigger DAG');
    }
}

// Edit Airflow DAG schedule
function editDagSchedule(dagId) {
    // Open the schedule modal with pre-filled data
    // In a real implementation, we would fetch the current schedule first
    document.getElementById('schedule-name').value = `Schedule for ${dagId}`;
    document.getElementById('associated-job').value = dagId;
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('createScheduleModal'));
    modal.show();
}
