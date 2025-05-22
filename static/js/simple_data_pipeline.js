// Simple Data Pipeline JavaScript for AI Assistant Platform

document.addEventListener('DOMContentLoaded', function() {
    console.log("Simple Data Pipeline JS loaded");
    populateNifiStats();
    populateNifiJobs();
    populateAirflowStats();
    populateAirflowDags();
    populateJobStatus();
    
    // Add click handlers for refresh buttons
    document.getElementById('refresh-nifi-btn')?.addEventListener('click', function() {
        populateNifiStats(true);
        populateNifiJobs(true);
    });
    
    document.getElementById('refresh-airflow-btn')?.addEventListener('click', function() {
        populateAirflowStats(true);
        populateAirflowDags(true);
    });
    
    document.getElementById('refresh-jobs-btn')?.addEventListener('click', function() {
        populateJobStatus(true);
    });
    
    // Initialize tabs if not already done
    const triggerTabList = document.querySelectorAll('#pipeline-tabs button');
    triggerTabList.forEach(triggerEl => {
        triggerEl.addEventListener('click', function(event) {
            event.preventDefault();
            const tab = new bootstrap.Tab(this);
            tab.show();
        });
    });
});

// Populate NiFi Statistics
function populateNifiStats(animate = false) {
    updateElement('active-processors', getRandomInt(35, 52), animate);
    updateElement('process-groups', getRandomInt(6, 12), animate);
    updateElement('connections', getRandomInt(58, 75), animate);
    updateElement('running-jobs', getRandomInt(3, 7), animate);
}

// Populate NiFi Jobs Table
function populateNifiJobs(animate = false) {
    const jobs = [
        {
            name: "Log Data Ingestion",
            type: "File Transfer",
            source: "/var/log/server01",
            destination: "Kafka: logs-topic",
            status: "Running",
            lastRun: "2025-05-22 04:30:15",
            actions: ["view", "pause", "stop"]
        },
        {
            name: "S3 Bucket Sync",
            type: "Cloud Storage",
            source: "AWS S3: data-bucket",
            destination: "MinIO: archived-data",
            status: "Running",
            lastRun: "2025-05-22 04:15:42",
            actions: ["view", "pause", "stop"]
        },
        {
            name: "Network PCAP Collection",
            type: "Network Data",
            source: "Network Interface",
            destination: "MinIO: pcap-storage",
            status: "Running",
            lastRun: "2025-05-22 04:45:20",
            actions: ["view", "pause", "stop"]
        },
        {
            name: "Database Backup",
            type: "Database",
            source: "PostgreSQL: main-db",
            destination: "MinIO: db-backups",
            status: "Idle",
            lastRun: "2025-05-22 02:00:00",
            actions: ["view", "start", "delete"]
        },
        {
            name: "API Data Collector",
            type: "REST API",
            source: "External API",
            destination: "Kafka: api-data",
            status: "Running",
            lastRun: "2025-05-22 04:55:12",
            actions: ["view", "pause", "stop"]
        }
    ];
    
    const tableBody = document.querySelector('#nifi-jobs-table tbody');
    if (tableBody) {
        let html = '';
        
        jobs.forEach(job => {
            const statusClass = job.status === 'Running' ? 'success' : 
                               job.status === 'Idle' ? 'secondary' : 
                               job.status === 'Failed' ? 'danger' : 'warning';
            
            let actionButtons = '';
            if (job.actions.includes('view')) {
                actionButtons += `<button class="btn btn-outline-primary" title="View"><i class="fas fa-eye"></i></button>`;
            }
            if (job.actions.includes('start')) {
                actionButtons += `<button class="btn btn-outline-success" title="Start"><i class="fas fa-play"></i></button>`;
            }
            if (job.actions.includes('pause')) {
                actionButtons += `<button class="btn btn-outline-warning" title="Pause"><i class="fas fa-pause"></i></button>`;
            }
            if (job.actions.includes('stop')) {
                actionButtons += `<button class="btn btn-outline-danger" title="Stop"><i class="fas fa-stop"></i></button>`;
            }
            if (job.actions.includes('delete')) {
                actionButtons += `<button class="btn btn-outline-danger" title="Delete"><i class="fas fa-trash"></i></button>`;
            }
            
            html += `
            <tr>
                <td>${job.name}</td>
                <td>${job.type}</td>
                <td>${job.source}</td>
                <td>${job.destination}</td>
                <td><span class="badge bg-${statusClass}">${job.status}</span></td>
                <td>${job.lastRun}</td>
                <td>
                    <div class="btn-group btn-group-sm">
                        ${actionButtons}
                    </div>
                </td>
            </tr>
            `;
        });
        
        tableBody.innerHTML = html;
    }
}

// Populate Airflow Statistics
function populateAirflowStats(animate = false) {
    updateElement('active-dags', getRandomInt(10, 15), animate);
    updateElement('paused-dags', getRandomInt(2, 5), animate);
    updateElement('success-rate', getRandomInt(94, 99) + '%', animate);
    updateElement('running-tasks', getRandomInt(2, 6), animate);
}

// Populate Airflow DAGs Table
function populateAirflowDags(animate = false) {
    const dags = [
        {
            id: "daily_data_processing",
            description: "Process daily incoming data",
            schedule: "0 0 * * *",
            lastRun: "2025-05-22 00:00:05",
            duration: "23m 45s",
            status: "Success",
            statusClass: "success",
            actions: ["view", "trigger", "schedule"]
        },
        {
            id: "hourly_metrics_collection",
            description: "Collect system metrics hourly",
            schedule: "0 * * * *",
            lastRun: "2025-05-22 05:00:00",
            duration: "4m 12s",
            status: "Running",
            statusClass: "primary",
            actions: ["view", "trigger", "schedule"]
        },
        {
            id: "weekly_data_aggregation",
            description: "Aggregate weekly data for reporting",
            schedule: "0 0 * * 0",
            lastRun: "2025-05-19 00:00:00",
            duration: "58m 32s",
            status: "Success",
            statusClass: "success",
            actions: ["view", "trigger", "schedule"]
        },
        {
            id: "ml_model_training",
            description: "Train ML models on new data",
            schedule: "0 4 * * *",
            lastRun: "2025-05-22 04:00:00",
            duration: "1h 15m 18s",
            status: "Running",
            statusClass: "primary",
            actions: ["view", "trigger", "schedule"]
        },
        {
            id: "database_maintenance",
            description: "Perform database maintenance tasks",
            schedule: "0 2 * * 6",
            lastRun: "2025-05-18 02:00:00",
            duration: "32m 45s",
            status: "Success",
            statusClass: "success",
            actions: ["view", "trigger", "schedule"]
        }
    ];
    
    const tableBody = document.querySelector('#airflow-dags-table tbody');
    if (tableBody) {
        let html = '';
        
        dags.forEach(dag => {
            let actionButtons = '';
            if (dag.actions.includes('view')) {
                actionButtons += `<button class="btn btn-outline-primary" title="View"><i class="fas fa-eye"></i></button>`;
            }
            if (dag.actions.includes('trigger')) {
                actionButtons += `<button class="btn btn-outline-success" title="Trigger"><i class="fas fa-play"></i></button>`;
            }
            if (dag.actions.includes('schedule')) {
                actionButtons += `<button class="btn btn-outline-secondary" title="Edit Schedule"><i class="fas fa-calendar-alt"></i></button>`;
            }
            
            html += `
            <tr>
                <td>${dag.id}</td>
                <td>${dag.description}</td>
                <td><code>${dag.schedule}</code></td>
                <td>${dag.lastRun}</td>
                <td>${dag.duration}</td>
                <td><span class="badge bg-${dag.statusClass}">${dag.status}</span></td>
                <td>
                    <div class="btn-group btn-group-sm">
                        ${actionButtons}
                    </div>
                </td>
            </tr>
            `;
        });
        
        tableBody.innerHTML = html;
    }
}

// Populate Job Status
function populateJobStatus(animate = false) {
    const jobs = [
        {
            id: "job-123",
            name: "Daily ETL Process",
            type: "Batch Processing",
            startTime: "2025-05-22 00:00:05",
            endTime: "2025-05-22 01:15:42",
            status: "Completed",
            statusClass: "success",
            duration: "1h 15m 37s",
            resources: { cpu: "45%", memory: "2.3 GB", disk: "128 MB" }
        },
        {
            id: "job-124",
            name: "User Activity Analysis",
            type: "Data Analysis",
            startTime: "2025-05-22 02:00:00",
            endTime: "2025-05-22 02:45:18",
            status: "Completed",
            statusClass: "success",
            duration: "45m 18s",
            resources: { cpu: "65%", memory: "4.1 GB", disk: "256 MB" }
        },
        {
            id: "job-125",
            name: "ML Model Training",
            type: "Machine Learning",
            startTime: "2025-05-22 04:00:00",
            endTime: null,
            status: "Running",
            statusClass: "primary",
            duration: "1h 42m (running)",
            resources: { cpu: "85%", memory: "7.8 GB", disk: "1.2 GB" }
        },
        {
            id: "job-126",
            name: "Log File Processing",
            type: "Stream Processing",
            startTime: "2025-05-22 00:00:00",
            endTime: null,
            status: "Running",
            statusClass: "primary",
            duration: "5h 42m (running)",
            resources: { cpu: "25%", memory: "1.2 GB", disk: "4.5 GB" }
        },
        {
            id: "job-127",
            name: "Database Backup",
            type: "Maintenance",
            startTime: "2025-05-21 23:00:00",
            endTime: "2025-05-21 23:45:36",
            status: "Completed",
            statusClass: "success",
            duration: "45m 36s",
            resources: { cpu: "35%", memory: "1.5 GB", disk: "75 GB" }
        }
    ];
    
    const tableBody = document.querySelector('#job-status-table tbody');
    if (tableBody) {
        let html = '';
        
        jobs.forEach(job => {
            html += `
            <tr>
                <td>${job.id}</td>
                <td>${job.name}</td>
                <td>${job.type}</td>
                <td>${job.startTime}</td>
                <td>${job.endTime || "-"}</td>
                <td><span class="badge bg-${job.statusClass}">${job.status}</span></td>
                <td>${job.duration}</td>
                <td>
                    <div class="resource-usage">
                        <div class="d-flex justify-content-between">
                            <span>CPU:</span>
                            <span>${job.resources.cpu}</span>
                        </div>
                        <div class="progress mb-1" style="height: 5px;">
                            <div class="progress-bar" role="progressbar" style="width: ${job.resources.cpu};" aria-valuenow="${parseInt(job.resources.cpu)}" aria-valuemin="0" aria-valuemax="100"></div>
                        </div>
                        <div class="d-flex justify-content-between">
                            <span>Memory:</span>
                            <span>${job.resources.memory}</span>
                        </div>
                        <div class="d-flex justify-content-between">
                            <span>Disk:</span>
                            <span>${job.resources.disk}</span>
                        </div>
                    </div>
                </td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" title="View Details"><i class="fas fa-eye"></i></button>
                        <button class="btn btn-outline-secondary" title="View Logs"><i class="fas fa-file-alt"></i></button>
                        ${job.status === "Running" ? 
                          `<button class="btn btn-outline-danger" title="Stop"><i class="fas fa-stop"></i></button>` : 
                          `<button class="btn btn-outline-success" title="Rerun"><i class="fas fa-redo"></i></button>`}
                    </div>
                </td>
            </tr>
            `;
        });
        
        tableBody.innerHTML = html;
    }
    
    // Create a simple timeline visualization
    const timelineContainer = document.getElementById('job-timeline');
    if (timelineContainer) {
        let html = '';
        
        jobs.forEach((job, index) => {
            html += `
            <div class="timeline-item">
                <div class="timeline-badge bg-${job.statusClass}">
                    <i class="fas fa-cog"></i>
                </div>
                <div class="timeline-panel">
                    <div class="timeline-heading">
                        <h6 class="timeline-title">${job.name}</h6>
                        <p><small class="text-muted"><i class="fas fa-clock"></i> ${job.startTime}</small></p>
                    </div>
                    <div class="timeline-body">
                        <p>Type: ${job.type}</p>
                        <p>Duration: ${job.duration}</p>
                        <p>Status: <span class="badge bg-${job.statusClass}">${job.status}</span></p>
                    </div>
                    <div class="timeline-footer">
                        <button class="btn btn-sm btn-outline-primary">View Details</button>
                    </div>
                </div>
            </div>
            `;
        });
        
        timelineContainer.innerHTML = html;
    }
}

// Helper function to update an element with optional animation
function updateElement(elementId, value, animate = false) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    if (animate) {
        element.classList.add('highlight-change');
        setTimeout(() => {
            element.classList.remove('highlight-change');
        }, 1500);
    }
    
    element.textContent = value;
}

// Helper function to get a random integer between min and max (inclusive)
function getRandomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}