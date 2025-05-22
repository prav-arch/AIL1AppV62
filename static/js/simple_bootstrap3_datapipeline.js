// Simple Bootstrap 3 Data Pipeline script
$(document).ready(function() {
    console.log("Simple Bootstrap 3 Data Pipeline loaded");
    
    // Hard-code data directly into the tables
    
    // NIFI JOBS
    var nifiHtml = '';
    nifiHtml += '<tr><td>Log Data Ingestion</td><td>File Transfer</td><td>/var/log/server01</td><td>Kafka: logs-topic</td>';
    nifiHtml += '<td><span class="label label-success">Running</span></td><td>2025-05-22 04:30:15</td>';
    nifiHtml += '<td><div class="btn-group"><button class="btn btn-default btn-xs"><i class="fa fa-eye"></i></button>';
    nifiHtml += '<button class="btn btn-default btn-xs"><i class="fa fa-pause"></i></button>';
    nifiHtml += '<button class="btn btn-default btn-xs"><i class="fa fa-stop"></i></button></div></td></tr>';
    
    nifiHtml += '<tr><td>S3 Bucket Sync</td><td>Cloud Storage</td><td>AWS S3: data-bucket</td><td>MinIO: archived-data</td>';
    nifiHtml += '<td><span class="label label-success">Running</span></td><td>2025-05-22 04:15:42</td>';
    nifiHtml += '<td><div class="btn-group"><button class="btn btn-default btn-xs"><i class="fa fa-eye"></i></button>';
    nifiHtml += '<button class="btn btn-default btn-xs"><i class="fa fa-pause"></i></button>';
    nifiHtml += '<button class="btn btn-default btn-xs"><i class="fa fa-stop"></i></button></div></td></tr>';
    
    nifiHtml += '<tr><td>Database Backup</td><td>Database</td><td>PostgreSQL: main-db</td><td>MinIO: db-backups</td>';
    nifiHtml += '<td><span class="label label-default">Idle</span></td><td>2025-05-22 02:00:00</td>';
    nifiHtml += '<td><div class="btn-group"><button class="btn btn-default btn-xs"><i class="fa fa-eye"></i></button>';
    nifiHtml += '<button class="btn btn-default btn-xs"><i class="fa fa-play"></i></button>';
    nifiHtml += '<button class="btn btn-default btn-xs"><i class="fa fa-stop"></i></button></div></td></tr>';
    
    nifiHtml += '<tr><td>API Data Collector</td><td>REST API</td><td>External API</td><td>Kafka: api-data</td>';
    nifiHtml += '<td><span class="label label-success">Running</span></td><td>2025-05-22 04:55:12</td>';
    nifiHtml += '<td><div class="btn-group"><button class="btn btn-default btn-xs"><i class="fa fa-eye"></i></button>';
    nifiHtml += '<button class="btn btn-default btn-xs"><i class="fa fa-pause"></i></button>';
    nifiHtml += '<button class="btn btn-default btn-xs"><i class="fa fa-stop"></i></button></div></td></tr>';
    
    $('#nifi-jobs-table tbody').html(nifiHtml);
    
    // AIRFLOW DAGS
    var airflowHtml = '';
    airflowHtml += '<tr><td>daily_data_processing</td><td>Process daily incoming data</td><td><code>0 0 * * *</code></td>';
    airflowHtml += '<td>2025-05-22 00:00:05</td><td>23m 45s</td><td><span class="label label-success">Success</span></td>';
    airflowHtml += '<td><div class="btn-group"><button class="btn btn-default btn-xs"><i class="fa fa-eye"></i></button>';
    airflowHtml += '<button class="btn btn-default btn-xs"><i class="fa fa-play"></i></button>';
    airflowHtml += '<button class="btn btn-default btn-xs"><i class="fa fa-calendar"></i></button></div></td></tr>';
    
    airflowHtml += '<tr><td>hourly_metrics_collection</td><td>Collect system metrics hourly</td><td><code>0 * * * *</code></td>';
    airflowHtml += '<td>2025-05-22 05:00:00</td><td>4m 12s</td><td><span class="label label-primary">Running</span></td>';
    airflowHtml += '<td><div class="btn-group"><button class="btn btn-default btn-xs"><i class="fa fa-eye"></i></button>';
    airflowHtml += '<button class="btn btn-default btn-xs"><i class="fa fa-play"></i></button>';
    airflowHtml += '<button class="btn btn-default btn-xs"><i class="fa fa-calendar"></i></button></div></td></tr>';
    
    airflowHtml += '<tr><td>ml_model_training</td><td>Train ML models on new data</td><td><code>0 4 * * *</code></td>';
    airflowHtml += '<td>2025-05-22 04:00:00</td><td>1h 15m 18s</td><td><span class="label label-danger">Failed</span></td>';
    airflowHtml += '<td><div class="btn-group"><button class="btn btn-default btn-xs"><i class="fa fa-eye"></i></button>';
    airflowHtml += '<button class="btn btn-default btn-xs"><i class="fa fa-play"></i></button>';
    airflowHtml += '<button class="btn btn-default btn-xs"><i class="fa fa-calendar"></i></button></div></td></tr>';
    
    $('#airflow-dags-table tbody').html(airflowHtml);
    
    // JOB STATUS
    var jobStatusHtml = '';
    jobStatusHtml += '<tr><td>job-123</td><td>Daily ETL Process</td><td>Batch Processing</td><td>2025-05-22 00:00:05</td>';
    jobStatusHtml += '<td>2025-05-22 01:15:42</td><td><span class="label label-success">Completed</span></td><td>1h 15m 37s</td>';
    jobStatusHtml += '<td><div>CPU: 45%<div class="progress" style="margin-bottom:5px;"><div class="progress-bar" style="width:45%"></div></div>';
    jobStatusHtml += 'Memory: 2.3 GB<br>Disk: 128 MB</div></td>';
    jobStatusHtml += '<td><div class="btn-group"><button class="btn btn-default btn-xs"><i class="fa fa-eye"></i></button>';
    jobStatusHtml += '<button class="btn btn-default btn-xs"><i class="fa fa-file-text-o"></i></button>';
    jobStatusHtml += '<button class="btn btn-default btn-xs"><i class="fa fa-repeat"></i></button></div></td></tr>';
    
    jobStatusHtml += '<tr><td>job-125</td><td>ML Model Training</td><td>Machine Learning</td><td>2025-05-22 04:00:00</td>';
    jobStatusHtml += '<td>-</td><td><span class="label label-primary">Running</span></td><td>1h 42m (running)</td>';
    jobStatusHtml += '<td><div>CPU: 85%<div class="progress" style="margin-bottom:5px;"><div class="progress-bar" style="width:85%"></div></div>';
    jobStatusHtml += 'Memory: 7.8 GB<br>Disk: 1.2 GB</div></td>';
    jobStatusHtml += '<td><div class="btn-group"><button class="btn btn-default btn-xs"><i class="fa fa-eye"></i></button>';
    jobStatusHtml += '<button class="btn btn-default btn-xs"><i class="fa fa-file-text-o"></i></button>';
    jobStatusHtml += '<button class="btn btn-default btn-xs"><i class="fa fa-stop"></i></button></div></td></tr>';
    
    $('#job-status-table tbody').html(jobStatusHtml);
    
    // Set stats
    $('#active-processors').text('42');
    $('#process-groups').text('8');
    $('#connections').text('65');
    $('#running-jobs').text('5');
    
    $('#active-dags').text('12');
    $('#paused-dags').text('3');
    $('#success-rate').text('98%');
    $('#running-tasks').text('4');
    
    // Ensure tabs work with Bootstrap 3
    $('#pipeline-tabs a').click(function(e) {
        e.preventDefault();
        $(this).tab('show');
    });
});