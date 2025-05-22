// Direct approach to populate the Kafka Browser tab
$(document).ready(function() {
    console.log("Direct Kafka Browser JS loaded");
    
    // KAFKA CLUSTER STATS
    $('#broker-count').text('3');
    $('#total-topics').text('15');
    $('#consumer-groups-count').text('12');
    $('#total-messages').text('1,862,473');
    
    // Set initial selected topic
    $('#selected-topic-name').text('logs-topic');
    $('#messages-topic-name').text('logs-topic');
    
    // KAFKA TOPICS TABLE
    var kafkaTopics = [
        {
            name: "logs-topic",
            partitions: 3,
            replication: 3,
            messageCount: 524892,
            throughput: "120 msg/sec",
            size: "750 MB",
            retention: "7 days",
            created: "2025-04-01 00:00:00"
        },
        {
            name: "metrics-topic",
            partitions: 5,
            replication: 3,
            messageCount: 328157,
            throughput: "250 msg/sec",
            size: "1.2 GB",
            retention: "14 days",
            created: "2025-04-01 00:00:00"
        },
        {
            name: "events-topic",
            partitions: 2,
            replication: 3,
            messageCount: 125628,
            throughput: "45 msg/sec",
            size: "380 MB",
            retention: "30 days",
            created: "2025-04-02 00:00:00"
        },
        {
            name: "alerts-topic",
            partitions: 1,
            replication: 3,
            messageCount: 8421,
            throughput: "5 msg/sec",
            size: "12 MB",
            retention: "90 days",
            created: "2025-04-02 00:00:00"
        },
        {
            name: "clickstream-topic",
            partitions: 8,
            replication: 3,
            messageCount: 1458276,
            throughput: "850 msg/sec",
            size: "3.5 GB",
            retention: "3 days",
            created: "2025-04-03 00:00:00"
        }
    ];
    
    var topicsTableHtml = '';
    $.each(kafkaTopics, function(i, topic) {
        var messagesClass = topic.messageCount > 500000 ? 'text-success' : (topic.messageCount < 50000 ? 'text-muted' : '');
        
        topicsTableHtml += '<tr data-topic="' + topic.name + '">' +
            '<td><strong>' + topic.name + '</strong></td>' +
            '<td>' + topic.partitions + '</td>' +
            '<td>' + topic.replication + '</td>' +
            '<td class="' + messagesClass + '">' + topic.messageCount.toLocaleString() + '</td>' +
            '<td>' + topic.throughput + '</td>' +
            '<td>' + topic.size + '</td>' +
            '<td>' + topic.retention + '</td>' +
            '<td>' + topic.created + '</td>' +
            '<td>' +
                '<div class="btn-group btn-group-sm">' +
                    '<button class="btn btn-outline-primary view-topic-btn" data-topic="' + topic.name + '" title="View Messages"><i class="fas fa-eye"></i></button>' +
                    '<button class="btn btn-outline-info" title="View Metrics"><i class="fas fa-chart-line"></i></button>' +
                    '<button class="btn btn-outline-secondary" title="Edit Configuration"><i class="fas fa-cog"></i></button>' +
                '</div>' +
            '</td>' +
        '</tr>';
    });
    $('#kafka-topics-table tbody').html(topicsTableHtml);
    
    // TOPIC MESSAGE STATS
    $('#topic-message-count').text('524,892');
    $('#topic-avg-size').text('1.4 KB');
    $('#topic-top-partition').text('1');
    $('#topic-message-rate').text('120 msg/sec');
    
    // KAFKA MESSAGES TABLE
    var kafkaMessages = [
        {
            offset: 1000050,
            partition: 1,
            key: "srv-web-01",
            value: {
                timestamp: "2025-05-22T04:55:12.000Z",
                level: "INFO",
                service: "api-gateway",
                message: "Request processed successfully",
                requestId: "abcd1234",
                duration: 125
            },
            timestamp: "2025-05-22 04:55:12"
        },
        {
            offset: 1000049,
            partition: 0,
            key: "srv-auth-02",
            value: {
                timestamp: "2025-05-22T04:55:10.000Z",
                level: "WARN",
                service: "auth-service",
                message: "Rate limit exceeded",
                requestId: "efgh5678",
                duration: 350
            },
            timestamp: "2025-05-22 04:55:10"
        },
        {
            offset: 1000048,
            partition: 2,
            key: "srv-db-01",
            value: {
                timestamp: "2025-05-22T04:55:08.000Z",
                level: "ERROR",
                service: "database",
                message: "Connection timeout",
                requestId: "ijkl9012",
                duration: 500
            },
            timestamp: "2025-05-22 04:55:08"
        },
        {
            offset: 1000047,
            partition: 1,
            key: "srv-web-02",
            value: {
                timestamp: "2025-05-22T04:55:05.000Z",
                level: "INFO",
                service: "user-service",
                message: "User login attempt",
                requestId: "mnop3456",
                duration: 75
            },
            timestamp: "2025-05-22 04:55:05"
        },
        {
            offset: 1000046,
            partition: 0,
            key: "srv-cache-01",
            value: {
                timestamp: "2025-05-22T04:55:01.000Z",
                level: "DEBUG",
                service: "cache-service",
                message: "Cache miss for key",
                requestId: "qrst7890",
                duration: 15
            },
            timestamp: "2025-05-22 04:55:01"
        }
    ];
    
    var messagesTableHtml = '';
    $.each(kafkaMessages, function(i, message) {
        messagesTableHtml += '<tr>' +
            '<td>' + message.offset + '</td>' +
            '<td>' + message.partition + '</td>' +
            '<td><code>' + (message.key || '<null>') + '</code></td>' +
            '<td class="text-truncate" style="max-width: 400px;"><code>' + 
                JSON.stringify(message.value).replace(/</g, '&lt;').replace(/>/g, '&gt;') + 
            '</code></td>' +
            '<td>' + message.timestamp + '</td>' +
            '<td>' +
                '<div class="btn-group btn-group-sm">' +
                    '<button class="btn btn-outline-primary view-message-btn" data-message-index="' + i + '" title="View Full Message"><i class="fas fa-eye"></i></button>' +
                    '<button class="btn btn-outline-secondary copy-message-btn" data-message-index="' + i + '" title="Copy Message"><i class="fas fa-copy"></i></button>' +
                '</div>' +
            '</td>' +
        '</tr>';
    });
    $('#kafka-messages-table tbody').html(messagesTableHtml);
    
    // Save messages for modal display
    window.currentKafkaMessages = kafkaMessages;
    
    // CONSUMER GROUPS TABLE
    var consumerGroups = [
        {
            id: "log-processor-group",
            members: 3,
            topics: ["logs-topic", "app-logs"],
            totalLag: 275,
            status: "Stable",
            statusClass: "success"
        },
        {
            id: "metrics-analyzer",
            members: 5,
            topics: ["metrics-topic", "system-metrics"],
            totalLag: 482,
            status: "Stable",
            statusClass: "success"
        },
        {
            id: "alert-manager",
            members: 2,
            topics: ["alerts-topic"],
            totalLag: 12,
            status: "Stable",
            statusClass: "success"
        },
        {
            id: "clickstream-processor",
            members: 8,
            topics: ["clickstream-topic"],
            totalLag: 8763,
            status: "Warning",
            statusClass: "warning"
        },
        {
            id: "user-activity-tracker",
            members: 4,
            topics: ["user-activity"],
            totalLag: 1254,
            status: "Stable",
            statusClass: "success"
        }
    ];
    
    var consumerGroupsHtml = '';
    $.each(consumerGroups, function(i, group) {
        consumerGroupsHtml += '<tr>' +
            '<td><strong>' + group.id + '</strong></td>' +
            '<td>' + group.members + '</td>' +
            '<td>' + group.topics.join(", ") + '</td>' +
            '<td>' + group.totalLag.toLocaleString() + '</td>' +
            '<td><span class="badge bg-' + group.statusClass + '">' + group.status + '</span></td>' +
            '<td>' +
                '<div class="btn-group btn-group-sm">' +
                    '<button class="btn btn-outline-primary" title="View Details"><i class="fas fa-eye"></i></button>' +
                    '<button class="btn btn-outline-secondary" title="View Offsets"><i class="fas fa-list-ol"></i></button>' +
                    '<button class="btn btn-outline-danger" title="Reset Offsets"><i class="fas fa-undo"></i></button>' +
                '</div>' +
            '</td>' +
        '</tr>';
    });
    $('#consumer-groups-table tbody').html(consumerGroupsHtml);
    
    // BIND EVENTS
    
    // Topic view button click
    $('.view-topic-btn').on('click', function() {
        var topicName = $(this).data('topic');
        selectTopic(topicName);
    });
    
    // Topic row click
    $('#kafka-topics-table tbody tr').on('click', function() {
        var topicName = $(this).data('topic');
        selectTopic(topicName);
    });
    
    // Message view button click
    $('.view-message-btn').on('click', function() {
        var messageIndex = $(this).data('message-index');
        viewMessageDetails(messageIndex);
    });
    
    // Initialize tabs
    $('.nav-tabs a').on('click', function (e) {
        e.preventDefault();
        $(this).tab('show');
    });
    
    // HELPER FUNCTIONS
    
    // Select a topic and show its messages
    function selectTopic(topicName) {
        $('#selected-topic-name').text(topicName);
        $('#messages-topic-name').text(topicName);
        
        // Highlight selected row
        $('#kafka-topics-table tbody tr').removeClass('table-primary');
        $('#kafka-topics-table tbody tr[data-topic="' + topicName + '"]').addClass('table-primary');
        
        // Switch to messages tab
        $('#kafka-tabs a[href="#messages"]').tab('show');
    }
    
    // View message details in modal
    function viewMessageDetails(messageIndex) {
        var message = window.currentKafkaMessages[messageIndex];
        if (!message) return;
        
        $('#message-modal-offset').text(message.offset);
        $('#message-modal-partition').text(message.partition);
        $('#message-modal-key').text(message.key || '<null>');
        $('#message-modal-timestamp').text(message.timestamp);
        
        // Format JSON
        $('#message-modal-value').text(JSON.stringify(message.value, null, 2));
        
        // Show modal
        $('#messageDetailsModal').modal('show');
    }
});