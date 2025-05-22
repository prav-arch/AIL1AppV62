// Bootstrap 3 compatible Kafka Browser JavaScript
$(document).ready(function() {
    console.log("Bootstrap 3 Kafka Browser JS loaded");
    
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
    
    // Clear and populate the Kafka Topics table
    var $topicsTableBody = $('#kafka-topics-table tbody');
    $topicsTableBody.empty();
    
    $.each(kafkaTopics, function(i, topic) {
        var $tr = $('<tr>')
            .attr('data-topic', topic.name)
            .appendTo($topicsTableBody);
        
        $('<td>').append($('<strong>').text(topic.name)).appendTo($tr);
        $('<td>').text(topic.partitions).appendTo($tr);
        $('<td>').text(topic.replication).appendTo($tr);
        
        // Message count with color for visibility
        var messagesClass = topic.messageCount > 500000 ? 'text-success' : 
                            (topic.messageCount < 50000 ? 'text-muted' : '');
        $('<td>').addClass(messagesClass)
            .text(topic.messageCount.toLocaleString())
            .appendTo($tr);
        
        $('<td>').text(topic.throughput).appendTo($tr);
        $('<td>').text(topic.size).appendTo($tr);
        $('<td>').text(topic.retention).appendTo($tr);
        $('<td>').text(topic.created).appendTo($tr);
        
        // Actions column
        var $actionsTd = $('<td>').appendTo($tr);
        var $btnGroup = $('<div>').addClass('btn-group btn-group-xs').appendTo($actionsTd);
        
        var $viewBtn = $('<button>')
            .addClass('btn btn-default view-topic-btn')
            .attr({
                'title': 'View Messages',
                'data-topic': topic.name
            })
            .append($('<i>').addClass('fa fa-eye'))
            .appendTo($btnGroup);
            
        $('<button>')
            .addClass('btn btn-default')
            .attr('title', 'View Metrics')
            .append($('<i>').addClass('fa fa-line-chart'))
            .appendTo($btnGroup);
            
        $('<button>')
            .addClass('btn btn-default')
            .attr('title', 'Edit Configuration')
            .append($('<i>').addClass('fa fa-cog'))
            .appendTo($btnGroup);
    });
    
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
            key: null,
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
    
    // Clear and populate the Kafka Messages table
    var $messagesTableBody = $('#kafka-messages-table tbody');
    $messagesTableBody.empty();
    
    $.each(kafkaMessages, function(i, message) {
        var $tr = $('<tr>').appendTo($messagesTableBody);
        
        $('<td>').text(message.offset).appendTo($tr);
        $('<td>').text(message.partition).appendTo($tr);
        
        // Key with null handling
        $('<td>').append(
            $('<code>').text(message.key || '<null>')
        ).appendTo($tr);
        
        // Value as truncated JSON
        var valueStr = JSON.stringify(message.value);
        $('<td>').addClass('text-truncate').css('max-width', '400px')
            .append($('<code>').text(valueStr))
            .appendTo($tr);
        
        $('<td>').text(message.timestamp).appendTo($tr);
        
        // Actions column
        var $actionsTd = $('<td>').appendTo($tr);
        var $btnGroup = $('<div>').addClass('btn-group btn-group-xs').appendTo($actionsTd);
        
        $('<button>')
            .addClass('btn btn-default view-message-btn')
            .attr({
                'title': 'View Full Message',
                'data-message-index': i
            })
            .append($('<i>').addClass('fa fa-eye'))
            .appendTo($btnGroup);
            
        $('<button>')
            .addClass('btn btn-default copy-message-btn')
            .attr({
                'title': 'Copy Message',
                'data-message-index': i
            })
            .append($('<i>').addClass('fa fa-copy'))
            .appendTo($btnGroup);
    });
    
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
    
    // Clear and populate the Consumer Groups table
    var $consumerGroupsTableBody = $('#consumer-groups-table tbody');
    $consumerGroupsTableBody.empty();
    
    $.each(consumerGroups, function(i, group) {
        var $tr = $('<tr>').appendTo($consumerGroupsTableBody);
        
        $('<td>').append($('<strong>').text(group.id)).appendTo($tr);
        $('<td>').text(group.members).appendTo($tr);
        $('<td>').text(group.topics.join(", ")).appendTo($tr);
        $('<td>').text(group.totalLag.toLocaleString()).appendTo($tr);
        
        // Status with label
        var $statusTd = $('<td>').appendTo($tr);
        $('<span>')
            .addClass('label label-' + group.statusClass)
            .text(group.status)
            .appendTo($statusTd);
        
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
            .attr('title', 'View Offsets')
            .append($('<i>').addClass('fa fa-list-ol'))
            .appendTo($btnGroup);
            
        $('<button>')
            .addClass('btn btn-default')
            .attr('title', 'Reset Offsets')
            .append($('<i>').addClass('fa fa-undo'))
            .appendTo($btnGroup);
    });
    
    // BIND EVENTS
    
    // Fix tab navigation for Bootstrap 3
    $('#kafka-tabs a').click(function (e) {
        e.preventDefault();
        $(this).tab('show');
    });
    
    // Topic view button click
    $('.view-topic-btn').click(function() {
        var topicName = $(this).data('topic');
        selectTopic(topicName);
    });
    
    // Topic row click
    $('#kafka-topics-table tbody tr').click(function() {
        var topicName = $(this).data('topic');
        selectTopic(topicName);
    });
    
    // Message view button click
    $('.view-message-btn').click(function() {
        var messageIndex = $(this).data('message-index');
        viewMessageDetails(messageIndex);
    });
    
    // HELPER FUNCTIONS
    
    // Select a topic and show its messages
    function selectTopic(topicName) {
        $('#selected-topic-name').text(topicName);
        $('#messages-topic-name').text(topicName);
        
        // Highlight selected row
        $('#kafka-topics-table tbody tr').removeClass('active');
        $('#kafka-topics-table tbody tr[data-topic="' + topicName + '"]').addClass('active');
        
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