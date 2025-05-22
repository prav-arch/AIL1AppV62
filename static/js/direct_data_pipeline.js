// Direct approach to populate the Data Pipeline tab
$(document).ready(function() {
    console.log("Direct Data Pipeline JS loaded");
    
    // NIFI STATS
    $('#active-processors').text('42');
    $('#process-groups').text('8');
    $('#connections').text('65');
    $('#running-jobs').text('5');
    
    // NIFI JOBS TABLE
    var nifiJobs = [
        {
            name: "Log Data Ingestion",
            type: "File Transfer",
            source: "/var/log/server01",
            destination: "Kafka: logs-topic",
            status: "Running",
            statusClass: "success",
            lastRun: "2025-05-22 04:30:15"
        },
        {
            name: "S3 Bucket Sync",
            type: "Cloud Storage",
            source: "AWS S3: data-bucket",
            destination: "MinIO: archived-data",
            status: "Running",
            statusClass: "success",
            lastRun: "2025-05-22 04:15:42"
        },
        {
            name: "Network PCAP Collection",
            type: "Network Data",
            source: "Network Interface",
            destination: "MinIO: pcap-storage",
            status: "Running",
            statusClass: "success",
            lastRun: "2025-05-22 04:45:20"
        },
        {
            name: "Database Backup",
            type: "Database",
            source: "PostgreSQL: main-db",
            destination: "MinIO: db-backups",
            status: "Idle",
            statusClass: "secondary",
            lastRun: "2025-05-22 02:00:00"
        },
        {
            name: "API Data Collector",
            type: "REST API", 
            source: "External API",
            destination: "Kafka: api-data",
            status: "Warning",
            statusClass: "warning",
            lastRun: "2025-05-22 04:55:12"
        }
    ];
    
    var nifiTableHtml = '';
    $.each(nifiJobs, function(i, job) {
        nifiTableHtml += '<tr>' +
            '<td>' + job.name + '</td>' +
            '<td>' + job.type + '</td>' +
            '<td>' + job.source + '</td>' +
            '<td>' + job.destination + '</td>' +
            '<td><span class="badge bg-' + job.statusClass + '">' + job.status + '</span></td>' +
            '<td>' + job.lastRun + '</td>' +
            '<td>' +
                '<div class="btn-group btn-group-sm">' +
                    '<button class="btn btn-outline-primary" title="View"><i class="fas fa-eye"></i></button>' +
                    '<button class="btn btn-outline-warning" title="Pause"><i class="fas fa-pause"></i></button>' +
                    '<button class="btn btn-outline-danger" title="Stop"><i class="fas fa-stop"></i></button>' +
                '</div>' +
            '</td>' +
        '</tr>';
    });
    $('#nifi-jobs-table tbody').html(nifiTableHtml);
    
    // AIRFLOW STATS
    $('#active-dags').text('12');
    $('#paused-dags').text('3');
    $('#success-rate').text('98%');
    $('#running-tasks').text('4');
    
    // AIRFLOW DAGS TABLE
    var airflowDags = [
        {
            id: "daily_data_processing",
            description: "Process daily incoming data",
            schedule: "0 0 * * *",
            lastRun: "2025-05-22 00:00:05",
            duration: "23m 45s",
            status: "Success",
            statusClass: "success"
        },
        {
            id: "hourly_metrics_collection",
            description: "Collect system metrics hourly",
            schedule: "0 * * * *",
            lastRun: "2025-05-22 05:00:00",
            duration: "4m 12s",
            status: "Running",
            statusClass: "primary"
        },
        {
            id: "weekly_data_aggregation",
            description: "Aggregate weekly data for reporting",
            schedule: "0 0 * * 0",
            lastRun: "2025-05-19 00:00:00",
            duration: "58m 32s",
            status: "Success",
            statusClass: "success"
        },
        {
            id: "ml_model_training",
            description: "Train ML models on new data",
            schedule: "0 4 * * *",
            lastRun: "2025-05-22 04:00:00",
            duration: "1h 15m 18s",
            status: "Failed",
            statusClass: "danger"
        },
        {
            id: "database_maintenance",
            description: "Perform database maintenance tasks",
            schedule: "0 2 * * 6",
            lastRun: "2025-05-18 02:00:00",
            duration: "32m 45s",
            status: "Success",
            statusClass: "success"
        }
    ];
    
    var airflowTableHtml = '';
    $.each(airflowDags, function(i, dag) {
        airflowTableHtml += '<tr>' +
            '<td>' + dag.id + '</td>' +
            '<td>' + dag.description + '</td>' +
            '<td><code>' + dag.schedule + '</code></td>' +
            '<td>' + dag.lastRun + '</td>' +
            '<td>' + dag.duration + '</td>' +
            '<td><span class="badge bg-' + dag.statusClass + '">' + dag.status + '</span></td>' +
            '<td>' +
                '<div class="btn-group btn-group-sm">' +
                    '<button class="btn btn-outline-primary" title="View"><i class="fas fa-eye"></i></button>' +
                    '<button class="btn btn-outline-success" title="Trigger"><i class="fas fa-play"></i></button>' +
                    '<button class="btn btn-outline-secondary" title="Edit Schedule"><i class="fas fa-calendar-alt"></i></button>' +
                '</div>' +
            '</td>' +
        '</tr>';
    });
    $('#airflow-dags-table tbody').html(airflowTableHtml);
    
    // JOB STATUS TABLE
    var jobStatus = [
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
        }
    ];
    
    var jobStatusHtml = '';
    $.each(jobStatus, function(i, job) {
        jobStatusHtml += '<tr>' +
            '<td>' + job.id + '</td>' +
            '<td>' + job.name + '</td>' +
            '<td>' + job.type + '</td>' +
            '<td>' + job.startTime + '</td>' +
            '<td>' + (job.endTime || "-") + '</td>' +
            '<td><span class="badge bg-' + job.statusClass + '">' + job.status + '</span></td>' +
            '<td>' + job.duration + '</td>' +
            '<td>' +
                '<div class="resource-usage">' +
                    '<div class="d-flex justify-content-between">' +
                        '<span>CPU:</span>' +
                        '<span>' + job.resources.cpu + '</span>' +
                    '</div>' +
                    '<div class="progress mb-1" style="height: 5px;">' +
                        '<div class="progress-bar" role="progressbar" style="width: ' + job.resources.cpu + ';" aria-valuenow="' + parseInt(job.resources.cpu) + '" aria-valuemin="0" aria-valuemax="100"></div>' +
                    '</div>' +
                    '<div class="d-flex justify-content-between">' +
                        '<span>Memory:</span>' +
                        '<span>' + job.resources.memory + '</span>' +
                    '</div>' +
                    '<div class="d-flex justify-content-between">' +
                        '<span>Disk:</span>' +
                        '<span>' + job.resources.disk + '</span>' +
                    '</div>' +
                '</div>' +
            '</td>' +
            '<td>' +
                '<div class="btn-group btn-group-sm">' +
                    '<button class="btn btn-outline-primary" title="View Details"><i class="fas fa-eye"></i></button>' +
                    '<button class="btn btn-outline-secondary" title="View Logs"><i class="fas fa-file-alt"></i></button>' +
                    (job.status === "Running" ? 
                        '<button class="btn btn-outline-danger" title="Stop"><i class="fas fa-stop"></i></button>' : 
                        '<button class="btn btn-outline-success" title="Rerun"><i class="fas fa-redo"></i></button>') +
                '</div>' +
            '</td>' +
        '</tr>';
    });
    $('#job-status-table tbody').html(jobStatusHtml);
    
    // Initialize tabs
    $('.nav-tabs a').on('click', function (e) {
        e.preventDefault();
        $(this).tab('show');
    });
});