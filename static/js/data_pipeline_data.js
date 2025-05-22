// Data Pipeline Dummy Data Generator

document.addEventListener('DOMContentLoaded', function() {
    // Populate NiFi Jobs
    populateNifiJobs();
    
    // Populate Airflow DAGs
    populateAirflowDags();
    
    // Populate Job Status
    populateJobStatus();
    
    // Setup refresh buttons
    document.getElementById('refresh-nifi-btn').addEventListener('click', function() {
        populateNifiJobs(true);
    });
    
    document.getElementById('refresh-airflow-btn').addEventListener('click', function() {
        populateAirflowDags(true);
    });
    
    document.getElementById('refresh-jobs-btn').addEventListener('click', function() {
        populateJobStatus(true);
    });
});

// Populate NiFi Jobs with dummy data
function populateNifiJobs(animate = false) {
    // NiFi statistics
    updateWithAnimation('active-processors', getRandomInt(35, 52), animate);
    updateWithAnimation('process-groups', getRandomInt(6, 12), animate);
    updateWithAnimation('connections', getRandomInt(58, 75), animate);
    updateWithAnimation('running-jobs', getRandomInt(3, 7), animate);
    
    // Create dummy data for NiFi jobs
    const nifiJobs = [
        {
            name: "Log Data Ingestion",
            type: "File Transfer",
            source: "/var/log/server01",
            destination: "Kafka: logs-topic",
            status: getRandomStatus(0.8, 0.1, 0.05, 0.05),
            lastRun: getRandomTimestamp(60),
            actions: ["view", "pause", "stop"]
        },
        {
            name: "S3 Bucket Sync",
            type: "Cloud Storage",
            source: "AWS S3: data-bucket",
            destination: "MinIO: archived-data",
            status: getRandomStatus(0.7, 0.2, 0.05, 0.05),
            lastRun: getRandomTimestamp(120),
            actions: ["view", "pause", "stop"]
        },
        {
            name: "Network PCAP Collection",
            type: "Network Data",
            source: "Network Interface",
            destination: "MinIO: pcap-storage",
            status: getRandomStatus(0.9, 0.05, 0.05, 0),
            lastRun: getRandomTimestamp(30),
            actions: ["view", "pause", "stop"]
        },
        {
            name: "Database Backup",
            type: "Database",
            source: "PostgreSQL: main-db",
            destination: "MinIO: db-backups",
            status: getRandomStatus(0.2, 0.6, 0.1, 0.1),
            lastRun: getRandomTimestamp(720),
            actions: ["view", "start", "delete"]
        },
        {
            name: "API Data Collector",
            type: "REST API",
            source: "External API",
            destination: "Kafka: api-data",
            status: getRandomStatus(0.85, 0.05, 0.05, 0.05),
            lastRun: getRandomTimestamp(45),
            actions: ["view", "pause", "stop"]
        },
        {
            name: "Event Stream Processor",
            type: "Stream Processing",
            source: "Kafka: events-topic",
            destination: "ClickHouse: events-table",
            status: getRandomStatus(0.9, 0.05, 0.05, 0),
            lastRun: getRandomTimestamp(15),
            actions: ["view", "pause", "stop"]
        },
        {
            name: "Machine Learning Data Prep",
            type: "Data Transformation",
            source: "MinIO: raw-data",
            destination: "MinIO: ml-ready-data",
            status: getRandomStatus(0.7, 0.1, 0.1, 0.1),
            lastRun: getRandomTimestamp(180),
            actions: ["view", "start", "delete"]
        },
        {
            name: "Clickstream Processing",
            type: "Stream Processing",
            source: "Kafka: clickstream",
            destination: "TimescaleDB: user_actions",
            status: getRandomStatus(0.8, 0.1, 0.05, 0.05),
            lastRun: getRandomTimestamp(25),
            actions: ["view", "pause", "stop"]
        }
    ];
    
    // Populate the NiFi jobs table
    const nifiJobsTableBody = document.querySelector('#nifi-jobs-table tbody');
    if (nifiJobsTableBody) {
        let html = '';
        
        nifiJobs.forEach(job => {
            let statusClass, statusText;
            switch(job.status) {
                case 'running':
                    statusClass = 'success';
                    statusText = 'Running';
                    break;
                case 'idle':
                    statusClass = 'secondary';
                    statusText = 'Idle';
                    break;
                case 'failed':
                    statusClass = 'danger';
                    statusText = 'Failed';
                    break;
                case 'warning':
                    statusClass = 'warning';
                    statusText = 'Warning';
                    break;
            }
            
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
                <td><span class="badge bg-${statusClass}">${statusText}</span></td>
                <td>${job.lastRun}</td>
                <td>
                    <div class="btn-group btn-group-sm">
                        ${actionButtons}
                    </div>
                </td>
            </tr>
            `;
        });
        
        nifiJobsTableBody.innerHTML = html;
    }
}

// Populate Airflow DAGs with dummy data
function populateAirflowDags(animate = false) {
    // Airflow statistics
    updateWithAnimation('active-dags', getRandomInt(10, 15), animate);
    updateWithAnimation('paused-dags', getRandomInt(2, 5), animate);
    updateWithAnimation('success-rate', getRandomInt(94, 99) + '%', animate);
    updateWithAnimation('running-tasks', getRandomInt(2, 6), animate);
    
    // Create dummy data for Airflow DAGs
    const airflowDags = [
        {
            id: "daily_data_processing",
            description: "Process daily incoming data",
            schedule: "0 0 * * *",
            lastRun: getRandomTimestamp(24 * 60),
            duration: getRandomDuration(10, 30),
            status: getRandomStatus(0.9, 0.05, 0.05, 0),
            actions: ["view", "trigger", "schedule"]
        },
        {
            id: "hourly_metrics_collection",
            description: "Collect system metrics hourly",
            schedule: "0 * * * *",
            lastRun: getRandomTimestamp(60),
            duration: getRandomDuration(2, 8),
            status: getRandomStatus(0.95, 0.0, 0.05, 0),
            actions: ["view", "trigger", "schedule"]
        },
        {
            id: "weekly_data_aggregation",
            description: "Aggregate weekly data for reporting",
            schedule: "0 0 * * 0",
            lastRun: getRandomTimestamp(7 * 24 * 60),
            duration: getRandomDuration(40, 90),
            status: getRandomStatus(0.85, 0.05, 0.1, 0),
            actions: ["view", "trigger", "schedule"]
        },
        {
            id: "ml_model_training",
            description: "Train ML models on new data",
            schedule: "0 4 * * *",
            lastRun: getRandomTimestamp(24 * 60),
            duration: getRandomDuration(60, 120),
            status: getRandomStatus(0.8, 0.1, 0.1, 0),
            actions: ["view", "trigger", "schedule"]
        },
        {
            id: "database_maintenance",
            description: "Perform database maintenance tasks",
            schedule: "0 2 * * 6",
            lastRun: getRandomTimestamp(7 * 24 * 60),
            duration: getRandomDuration(15, 45),
            status: getRandomStatus(0.9, 0.0, 0.1, 0),
            actions: ["view", "trigger", "schedule"]
        },
        {
            id: "log_rotation",
            description: "Rotate and archive log files",
            schedule: "0 3 * * *",
            lastRun: getRandomTimestamp(24 * 60),
            duration: getRandomDuration(5, 15),
            status: getRandomStatus(0.95, 0.05, 0.0, 0),
            actions: ["view", "trigger", "schedule"]
        },
        {
            id: "data_quality_checks",
            description: "Run data quality checks",
            schedule: "0 6 * * *",
            lastRun: getRandomTimestamp(24 * 60),
            duration: getRandomDuration(10, 20),
            status: getRandomStatus(0.75, 0.15, 0.1, 0),
            actions: ["view", "trigger", "schedule"]
        },
        {
            id: "monthly_reports",
            description: "Generate monthly business reports",
            schedule: "0 1 1 * *",
            lastRun: getRandomTimestamp(30 * 24 * 60),
            duration: getRandomDuration(30, 60),
            status: getRandomStatus(0.9, 0.05, 0.05, 0),
            actions: ["view", "trigger", "schedule"]
        }
    ];
    
    // Populate the Airflow DAGs table
    const airflowDagsTableBody = document.querySelector('#airflow-dags-table tbody');
    if (airflowDagsTableBody) {
        let html = '';
        
        airflowDags.forEach(dag => {
            let statusClass, statusText;
            switch(dag.status) {
                case 'running':
                    statusClass = 'primary';
                    statusText = 'Running';
                    break;
                case 'idle':
                    statusClass = 'secondary';
                    statusText = 'Idle';
                    break;
                case 'failed':
                    statusClass = 'danger';
                    statusText = 'Failed';
                    break;
                case 'warning':
                    statusClass = 'warning';
                    statusText = 'Warning';
                    break;
                default:
                    statusClass = 'success';
                    statusText = 'Success';
            }
            
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
                <td><span class="badge bg-${statusClass}">${statusText}</span></td>
                <td>
                    <div class="btn-group btn-group-sm">
                        ${actionButtons}
                    </div>
                </td>
            </tr>
            `;
        });
        
        airflowDagsTableBody.innerHTML = html;
    }
}

// Populate Job Status with dummy data
function populateJobStatus(animate = false) {
    // Create dummy data for job status
    const jobStatuses = [
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
        },
        {
            id: "job-128",
            name: "Report Generation",
            type: "Data Visualization",
            startTime: "2025-05-21 22:30:00",
            endTime: "2025-05-21 22:35:12",
            status: "Failed",
            statusClass: "danger",
            duration: "5m 12s",
            resources: { cpu: "40%", memory: "1.8 GB", disk: "120 MB" }
        },
        {
            id: "job-129",
            name: "Data Ingestion Pipeline",
            type: "Stream Processing",
            startTime: "2025-05-22 05:00:00",
            endTime: null,
            status: "Warning",
            statusClass: "warning",
            duration: "42m (running)",
            resources: { cpu: "55%", memory: "3.2 GB", disk: "890 MB" }
        }
    ];
    
    // Populate the job status table
    const jobStatusTableBody = document.querySelector('#job-status-table tbody');
    if (jobStatusTableBody) {
        let html = '';
        
        jobStatuses.forEach(job => {
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
        
        jobStatusTableBody.innerHTML = html;
    }
    
    // Update the timeline visualization
    updateJobTimeline(jobStatuses);
}

// Update job timeline visualization
function updateJobTimeline(jobStatuses) {
    const timelineContainer = document.getElementById('job-timeline');
    if (!timelineContainer) return;
    
    let html = '';
    
    jobStatuses.forEach((job, index) => {
        // Create a timeline item for each job
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
                    <button class="btn btn-sm btn-outline-primary">Details</button>
                </div>
            </div>
        </div>
        `;
    });
    
    timelineContainer.innerHTML = html;
}

// Helper function to get a random integer between min and max (inclusive)
function getRandomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

// Helper function to get a random timestamp within the last n minutes
function getRandomTimestamp(maxMinutesAgo) {
    const now = new Date();
    const minutesAgo = getRandomInt(1, maxMinutesAgo);
    const timestamp = new Date(now.getTime() - (minutesAgo * 60000));
    
    return timestamp.toISOString().replace('T', ' ').substring(0, 19);
}

// Helper function to get a random duration string
function getRandomDuration(minMinutes, maxMinutes) {
    const minutes = getRandomInt(minMinutes, maxMinutes);
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    const seconds = getRandomInt(0, 59);
    
    if (hours > 0) {
        return `${hours}h ${remainingMinutes}m ${seconds}s`;
    } else {
        return `${minutes}m ${seconds}s`;
    }
}

// Helper function to get a random status based on probabilities
function getRandomStatus(runningProb, idleProb, failedProb, warningProb) {
    const rand = Math.random();
    let cumulativeProb = 0;
    
    cumulativeProb += runningProb;
    if (rand < cumulativeProb) return 'running';
    
    cumulativeProb += idleProb;
    if (rand < cumulativeProb) return 'idle';
    
    cumulativeProb += failedProb;
    if (rand < cumulativeProb) return 'failed';
    
    return 'warning';
}

// Helper function to update element with animation
function updateWithAnimation(elementId, value, animate) {
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