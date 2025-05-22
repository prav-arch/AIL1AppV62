// Simple Bootstrap 3 Kafka Browser script
$(document).ready(function() {
    console.log("Simple Bootstrap 3 Kafka Browser loaded");
    
    // KAFKA TOPICS
    var topicsHtml = '';
    topicsHtml += '<tr data-topic="logs-topic"><td><strong>logs-topic</strong></td><td>3</td><td>3</td>';
    topicsHtml += '<td class="text-success">524,892</td><td>120 msg/sec</td><td>750 MB</td>';
    topicsHtml += '<td>7 days</td><td>2025-04-01 00:00:00</td>';
    topicsHtml += '<td><div class="btn-group"><button class="btn btn-default btn-xs view-topic-btn" data-topic="logs-topic"><i class="fa fa-eye"></i></button>';
    topicsHtml += '<button class="btn btn-default btn-xs"><i class="fa fa-line-chart"></i></button>';
    topicsHtml += '<button class="btn btn-default btn-xs"><i class="fa fa-cog"></i></button></div></td></tr>';
    
    topicsHtml += '<tr data-topic="metrics-topic"><td><strong>metrics-topic</strong></td><td>5</td><td>3</td>';
    topicsHtml += '<td>328,157</td><td>250 msg/sec</td><td>1.2 GB</td>';
    topicsHtml += '<td>14 days</td><td>2025-04-01 00:00:00</td>';
    topicsHtml += '<td><div class="btn-group"><button class="btn btn-default btn-xs view-topic-btn" data-topic="metrics-topic"><i class="fa fa-eye"></i></button>';
    topicsHtml += '<button class="btn btn-default btn-xs"><i class="fa fa-line-chart"></i></button>';
    topicsHtml += '<button class="btn btn-default btn-xs"><i class="fa fa-cog"></i></button></div></td></tr>';
    
    topicsHtml += '<tr data-topic="events-topic"><td><strong>events-topic</strong></td><td>2</td><td>3</td>';
    topicsHtml += '<td>125,628</td><td>45 msg/sec</td><td>380 MB</td>';
    topicsHtml += '<td>30 days</td><td>2025-04-02 00:00:00</td>';
    topicsHtml += '<td><div class="btn-group"><button class="btn btn-default btn-xs view-topic-btn" data-topic="events-topic"><i class="fa fa-eye"></i></button>';
    topicsHtml += '<button class="btn btn-default btn-xs"><i class="fa fa-line-chart"></i></button>';
    topicsHtml += '<button class="btn btn-default btn-xs"><i class="fa fa-cog"></i></button></div></td></tr>';
    
    topicsHtml += '<tr data-topic="alerts-topic"><td><strong>alerts-topic</strong></td><td>1</td><td>3</td>';
    topicsHtml += '<td class="text-muted">8,421</td><td>5 msg/sec</td><td>12 MB</td>';
    topicsHtml += '<td>90 days</td><td>2025-04-02 00:00:00</td>';
    topicsHtml += '<td><div class="btn-group"><button class="btn btn-default btn-xs view-topic-btn" data-topic="alerts-topic"><i class="fa fa-eye"></i></button>';
    topicsHtml += '<button class="btn btn-default btn-xs"><i class="fa fa-line-chart"></i></button>';
    topicsHtml += '<button class="btn btn-default btn-xs"><i class="fa fa-cog"></i></button></div></td></tr>';
    
    topicsHtml += '<tr data-topic="clickstream-topic"><td><strong>clickstream-topic</strong></td><td>8</td><td>3</td>';
    topicsHtml += '<td class="text-success">1,458,276</td><td>850 msg/sec</td><td>3.5 GB</td>';
    topicsHtml += '<td>3 days</td><td>2025-04-03 00:00:00</td>';
    topicsHtml += '<td><div class="btn-group"><button class="btn btn-default btn-xs view-topic-btn" data-topic="clickstream-topic"><i class="fa fa-eye"></i></button>';
    topicsHtml += '<button class="btn btn-default btn-xs"><i class="fa fa-line-chart"></i></button>';
    topicsHtml += '<button class="btn btn-default btn-xs"><i class="fa fa-cog"></i></button></div></td></tr>';
    
    $('#kafka-topics-table tbody').html(topicsHtml);
    
    // KAFKA MESSAGES
    var messagesHtml = '';
    messagesHtml += '<tr><td>1000050</td><td>1</td><td><code>srv-web-01</code></td>';
    messagesHtml += '<td class="text-truncate" style="max-width:400px;"><code>{"timestamp":"2025-05-22T04:55:12.000Z","level":"INFO","service":"api-gateway","message":"Request processed successfully","requestId":"abcd1234","duration":125}</code></td>';
    messagesHtml += '<td>2025-05-22 04:55:12</td>';
    messagesHtml += '<td><div class="btn-group"><button class="btn btn-default btn-xs view-message-btn" data-message-index="0"><i class="fa fa-eye"></i></button>';
    messagesHtml += '<button class="btn btn-default btn-xs"><i class="fa fa-copy"></i></button></div></td></tr>';
    
    messagesHtml += '<tr><td>1000049</td><td>0</td><td><code>srv-auth-02</code></td>';
    messagesHtml += '<td class="text-truncate" style="max-width:400px;"><code>{"timestamp":"2025-05-22T04:55:10.000Z","level":"WARN","service":"auth-service","message":"Rate limit exceeded","requestId":"efgh5678","duration":350}</code></td>';
    messagesHtml += '<td>2025-05-22 04:55:10</td>';
    messagesHtml += '<td><div class="btn-group"><button class="btn btn-default btn-xs view-message-btn" data-message-index="1"><i class="fa fa-eye"></i></button>';
    messagesHtml += '<button class="btn btn-default btn-xs"><i class="fa fa-copy"></i></button></div></td></tr>';
    
    messagesHtml += '<tr><td>1000048</td><td>2</td><td><code>srv-db-01</code></td>';
    messagesHtml += '<td class="text-truncate" style="max-width:400px;"><code>{"timestamp":"2025-05-22T04:55:08.000Z","level":"ERROR","service":"database","message":"Connection timeout","requestId":"ijkl9012","duration":500}</code></td>';
    messagesHtml += '<td>2025-05-22 04:55:08</td>';
    messagesHtml += '<td><div class="btn-group"><button class="btn btn-default btn-xs view-message-btn" data-message-index="2"><i class="fa fa-eye"></i></button>';
    messagesHtml += '<button class="btn btn-default btn-xs"><i class="fa fa-copy"></i></button></div></td></tr>';
    
    $('#kafka-messages-table tbody').html(messagesHtml);
    
    // CONSUMER GROUPS
    var groupsHtml = '';
    groupsHtml += '<tr><td><strong>log-processor-group</strong></td><td>3</td><td>logs-topic, app-logs</td>';
    groupsHtml += '<td>275</td><td><span class="label label-success">Stable</span></td>';
    groupsHtml += '<td><div class="btn-group"><button class="btn btn-default btn-xs"><i class="fa fa-eye"></i></button>';
    groupsHtml += '<button class="btn btn-default btn-xs"><i class="fa fa-list-ol"></i></button>';
    groupsHtml += '<button class="btn btn-default btn-xs"><i class="fa fa-undo"></i></button></div></td></tr>';
    
    groupsHtml += '<tr><td><strong>metrics-analyzer</strong></td><td>5</td><td>metrics-topic, system-metrics</td>';
    groupsHtml += '<td>482</td><td><span class="label label-success">Stable</span></td>';
    groupsHtml += '<td><div class="btn-group"><button class="btn btn-default btn-xs"><i class="fa fa-eye"></i></button>';
    groupsHtml += '<button class="btn btn-default btn-xs"><i class="fa fa-list-ol"></i></button>';
    groupsHtml += '<button class="btn btn-default btn-xs"><i class="fa fa-undo"></i></button></div></td></tr>';
    
    groupsHtml += '<tr><td><strong>clickstream-processor</strong></td><td>8</td><td>clickstream-topic</td>';
    groupsHtml += '<td>8,763</td><td><span class="label label-warning">Warning</span></td>';
    groupsHtml += '<td><div class="btn-group"><button class="btn btn-default btn-xs"><i class="fa fa-eye"></i></button>';
    groupsHtml += '<button class="btn btn-default btn-xs"><i class="fa fa-list-ol"></i></button>';
    groupsHtml += '<button class="btn btn-default btn-xs"><i class="fa fa-undo"></i></button></div></td></tr>';
    
    $('#consumer-groups-table tbody').html(groupsHtml);
    
    // Set stats
    $('#broker-count').text('3');
    $('#total-topics').text('15');
    $('#consumer-groups-count').text('12');
    $('#total-messages').text('1,862,473');
    
    $('#selected-topic-name').text('logs-topic');
    $('#messages-topic-name').text('logs-topic');
    
    $('#topic-message-count').text('524,892');
    $('#topic-avg-size').text('1.4 KB');
    $('#topic-top-partition').text('1');
    $('#topic-message-rate').text('120 msg/sec');
    
    // Ensure tabs work with Bootstrap 3
    $('#kafka-tabs a').click(function(e) {
        e.preventDefault();
        $(this).tab('show');
    });
    
    // Handle topic selection
    $('.view-topic-btn').click(function() {
        var topicName = $(this).data('topic');
        $('#selected-topic-name').text(topicName);
        $('#messages-topic-name').text(topicName);
        $('#kafka-tabs a[href="#messages"]').tab('show');
    });
});