// Bootstrap 3 compatible Data Pipeline JavaScript
$(document).ready(function() {
    console.log("Bootstrap 3 Data Pipeline JS loaded");
    
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
            statusClass: "success"
        },
        {
            name: "S3 Bucket Sync",
            type: "Cloud Storage",
            source: "AWS S3: data-bucket",
            destination: "MinIO: archived-data",
            status: "Running", 
            statusClass: "success"
        },
        {
            name: "Network PCAP Collection",
            type: "Network Data",
            source: "Network Interface",
            destination: "MinIO: pcap-storage",
            status: "Running",
            statusClass: "success"
        },
        {
            name: "Database Backup",
            type: "Database",
            source: "PostgreSQL: main-db",
            destination: "MinIO: db-backups",
            status: "Idle",
            statusClass: "default"
        },
        {
            name: "API Data Collector",
            type: "REST API",
            source: "External API",
            destination: "Kafka: api-data",
            status: "Running",
            statusClass: "success"
        }
    ];
    
    // Clear and populate the NiFi jobs table
    var $nifiTableBody = $('#nifi-jobs-table tbody');
    $nifiTableBody.empty();
    
    $.each(nifiJobs, function(i, job) {
        var $tr = $('<tr>').appendTo($nifiTableBody);
        
        $('<td>').text(job.name).appendTo($tr);
        $('<td>').text(job.type).appendTo($tr);
        $('<td>').text(job.source).appendTo($tr);
        $('<td>').text(job.destination).appendTo($tr);
        
        // Status column with label
        var $statusTd = $('<td>').appendTo($tr);
        $('<span>')
            .addClass('label label-' + job.statusClass)
            .text(job.status)
            .appendTo($statusTd);
        
        // Last run column
        $('<td>').text('2025-05-22 ' + (7 - i) + ':00:00').appendTo($tr);
        
        // Actions column
        var $actionsTd = $('<td>').appendTo($tr);
        var $btnGroup = $('<div>').addClass('btn-group btn-group-xs').appendTo($actionsTd);
        
        $('<button>')
            .addClass('btn btn-default')
            .attr('title', 'View')
            .append($('<i>').addClass('fa fa-eye'))
            .appendTo($btnGroup);
            
        $('<button>')
            .addClass('btn btn-default')
            .attr('title', job.status === 'Running' ? 'Pause' : 'Start')
            .append($('<i>').addClass(job.status === 'Running' ? 'fa fa-pause' : 'fa fa-play'))
            .appendTo($btnGroup);
            
        $('<button>')
            .addClass('btn btn-default')
            .attr('title', 'Stop')
            .append($('<i>').addClass('fa fa-stop'))
            .appendTo($btnGroup);
    });
    
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
            lastRun: "2025-05-22 00:00:00",
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
    
    // Clear and populate the Airflow DAGs table
    var $airflowTableBody = $('#airflow-dags-table tbody');
    $airflowTableBody.empty();
    
    $.each(airflowDags, function(i, dag) {
        var $tr = $('<tr>').appendTo($airflowTableBody);
        
        $('<td>').text(dag.id).appendTo($tr);
        $('<td>').text(dag.description).appendTo($tr);
        $('<td>').append($('<code>').text(dag.schedule)).appendTo($tr);
        $('<td>').text(dag.lastRun).appendTo($tr);
        $('<td>').text(dag.duration).appendTo($tr);
        
        // Status column with label
        var $statusTd = $('<td>').appendTo($tr);
        $('<span>')
            .addClass('label label-' + dag.statusClass)
            .text(dag.status)
            .appendTo($statusTd);
        
        // Actions column
        var $actionsTd = $('<td>').appendTo($tr);
        var $btnGroup = $('<div>').addClass('btn-group btn-group-xs').appendTo($actionsTd);
        
        $('<button>')
            .addClass('btn btn-default')
            .attr('title', 'View')
            .append($('<i>').addClass('fa fa-eye'))
            .appendTo($btnGroup);
            
        $('<button>')
            .addClass('btn btn-default')
            .attr('title', 'Trigger')
            .append($('<i>').addClass('fa fa-play'))
            .appendTo($btnGroup);
            
        $('<button>')
            .addClass('btn btn-default')
            .attr('title', 'Edit Schedule')
            .append($('<i>').addClass('fa fa-calendar'))
            .appendTo($btnGroup);
    });
    
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
    
    // Clear and populate the Job Status table
    var $jobStatusTableBody = $('#job-status-table tbody');
    $jobStatusTableBody.empty();
    
    $.each(jobStatus, function(i, job) {
        var $tr = $('<tr>').appendTo($jobStatusTableBody);
        
        $('<td>').text(job.id).appendTo($tr);
        $('<td>').text(job.name).appendTo($tr);
        $('<td>').text(job.type).appendTo($tr);
        $('<td>').text(job.startTime).appendTo($tr);
        $('<td>').text(job.endTime || "-").appendTo($tr);
        
        // Status column with label
        var $statusTd = $('<td>').appendTo($tr);
        $('<span>')
            .addClass('label label-' + job.statusClass)
            .text(job.status)
            .appendTo($statusTd);
        
        $('<td>').text(job.duration).appendTo($tr);
        
        // Resources column
        var $resourcesTd = $('<td>').appendTo($tr);
        var $resourceDiv = $('<div>').addClass('resource-usage').appendTo($resourcesTd);
        
        // CPU
        $('<div>').addClass('row').appendTo($resourceDiv)
            .append($('<div>').addClass('col-xs-6').text('CPU:'))
            .append($('<div>').addClass('col-xs-6 text-right').text(job.resources.cpu));
        
        // Progress bar for CPU
        var $progressDiv = $('<div>').addClass('progress').css('margin-bottom', '5px').appendTo($resourceDiv);
        $('<div>').addClass('progress-bar')
            .attr({
                'role': 'progressbar',
                'aria-valuenow': parseInt(job.resources.cpu),
                'aria-valuemin': '0',
                'aria-valuemax': '100'
            })
            .css('width', job.resources.cpu)
            .appendTo($progressDiv);
        
        // Memory and Disk
        $('<div>').addClass('row').appendTo($resourceDiv)
            .append($('<div>').addClass('col-xs-6').text('Memory:'))
            .append($('<div>').addClass('col-xs-6 text-right').text(job.resources.memory));
        
        $('<div>').addClass('row').appendTo($resourceDiv)
            .append($('<div>').addClass('col-xs-6').text('Disk:'))
            .append($('<div>').addClass('col-xs-6 text-right').text(job.resources.disk));
        
        // Actions column
        var $actionsTd = $('<td>').appendTo($tr);
        var $btnGroup = $('<div>').addClass('btn-group btn-group-xs').appendTo($actionsTd);
        
        $('<button>')
            .addClass('btn btn-default')
            .attr('title', 'View Details')
            .append($('<i>').addClass('fa fa-eye'))
            .appendTo($btnGroup);
            
        $('<button>')
            .addClass('btn btn-default')
            .attr('title', 'View Logs')
            .append($('<i>').addClass('fa fa-file-text-o'))
            .appendTo($btnGroup);
            
        if (job.status === "Running") {
            $('<button>')
                .addClass('btn btn-default')
                .attr('title', 'Stop')
                .append($('<i>').addClass('fa fa-stop'))
                .appendTo($btnGroup);
        } else {
            $('<button>')
                .addClass('btn btn-default')
                .attr('title', 'Rerun')
                .append($('<i>').addClass('fa fa-repeat'))
                .appendTo($btnGroup);
        }
    });
    
    // Fix tab navigation for Bootstrap 3
    $('#pipeline-tabs a').click(function (e) {
        e.preventDefault();
        $(this).tab('show');
    });
});