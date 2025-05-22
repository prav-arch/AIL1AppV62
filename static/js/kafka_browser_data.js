// Kafka Browser Dummy Data Generator

document.addEventListener('DOMContentLoaded', function() {
    // Populate Kafka Topics
    populateKafkaTopics();
    
    // Populate Kafka Messages
    populateKafkaMessages();
    
    // Populate Consumer Groups
    populateConsumerGroups();
    
    // Setup refresh buttons
    document.getElementById('refresh-topics-btn').addEventListener('click', function() {
        populateKafkaTopics(true);
    });
    
    document.getElementById('refresh-messages-btn').addEventListener('click', function() {
        populateKafkaMessages(true);
    });
    
    document.getElementById('refresh-consumers-btn').addEventListener('click', function() {
        populateConsumerGroups(true);
    });
    
    // Setup topic selection
    setupTopicSelection();
});

// Populate Kafka Topics with dummy data
function populateKafkaTopics(animate = false) {
    // Kafka cluster statistics
    updateWithAnimation('broker-count', getRandomInt(3, 5), animate);
    updateWithAnimation('total-topics', getRandomInt(12, 18), animate);
    updateWithAnimation('consumer-groups-count', getRandomInt(8, 15), animate);
    updateWithAnimation('total-messages', formatNumber(getRandomInt(500000, 3000000)), animate);
    
    // Create dummy data for Kafka topics
    const kafkaTopics = [
        {
            name: "logs-topic",
            partitions: 3,
            replication: 3,
            messageCount: getRandomInt(100000, 500000),
            created: "2025-04-01 00:00:00",
            throughput: getRandomInt(50, 200) + " msg/sec",
            size: formatSize(getRandomInt(1024 * 1024 * 500, 1024 * 1024 * 2000)),
            retention: "7 days"
        },
        {
            name: "metrics-topic",
            partitions: 5,
            replication: 3,
            messageCount: getRandomInt(200000, 800000),
            created: "2025-04-01 00:00:00",
            throughput: getRandomInt(100, 400) + " msg/sec",
            size: formatSize(getRandomInt(1024 * 1024 * 800, 1024 * 1024 * 3000)),
            retention: "14 days"
        },
        {
            name: "events-topic",
            partitions: 2,
            replication: 3,
            messageCount: getRandomInt(50000, 200000),
            created: "2025-04-02 00:00:00",
            throughput: getRandomInt(20, 80) + " msg/sec",
            size: formatSize(getRandomInt(1024 * 1024 * 200, 1024 * 1024 * 800)),
            retention: "30 days"
        },
        {
            name: "alerts-topic",
            partitions: 1,
            replication: 3,
            messageCount: getRandomInt(1000, 5000),
            created: "2025-04-02 00:00:00",
            throughput: getRandomInt(1, 10) + " msg/sec",
            size: formatSize(getRandomInt(1024 * 1024 * 5, 1024 * 1024 * 20)),
            retention: "90 days"
        },
        {
            name: "clickstream-topic",
            partitions: 8,
            replication: 3,
            messageCount: getRandomInt(1000000, 2000000),
            created: "2025-04-03 00:00:00",
            throughput: getRandomInt(500, 1200) + " msg/sec",
            size: formatSize(getRandomInt(1024 * 1024 * 2000, 1024 * 1024 * 5000)),
            retention: "3 days"
        },
        {
            name: "user-activity",
            partitions: 6,
            replication: 3,
            messageCount: getRandomInt(300000, 900000),
            created: "2025-04-10 00:00:00",
            throughput: getRandomInt(200, 600) + " msg/sec",
            size: formatSize(getRandomInt(1024 * 1024 * 1000, 1024 * 1024 * 3000)),
            retention: "7 days"
        },
        {
            name: "api-requests",
            partitions: 4,
            replication: 3,
            messageCount: getRandomInt(400000, 1000000),
            created: "2025-04-15 00:00:00",
            throughput: getRandomInt(300, 800) + " msg/sec",
            size: formatSize(getRandomInt(1024 * 1024 * 1500, 1024 * 1024 * 4000)),
            retention: "5 days"
        },
        {
            name: "system-metrics",
            partitions: 2,
            replication: 3,
            messageCount: getRandomInt(100000, 400000),
            created: "2025-04-20 00:00:00",
            throughput: getRandomInt(50, 150) + " msg/sec",
            size: formatSize(getRandomInt(1024 * 1024 * 400, 1024 * 1024 * 1200)),
            retention: "14 days"
        },
        {
            name: "app-logs",
            partitions: 3,
            replication: 3,
            messageCount: getRandomInt(500000, 1500000),
            created: "2025-04-25 00:00:00",
            throughput: getRandomInt(250, 700) + " msg/sec",
            size: formatSize(getRandomInt(1024 * 1024 * 1800, 1024 * 1024 * 4500)),
            retention: "10 days"
        },
        {
            name: "transaction-events",
            partitions: 5,
            replication: 3,
            messageCount: getRandomInt(200000, 700000),
            created: "2025-05-01 00:00:00",
            throughput: getRandomInt(100, 300) + " msg/sec",
            size: formatSize(getRandomInt(1024 * 1024 * 800, 1024 * 1024 * 2500)),
            retention: "30 days"
        },
        {
            name: "ml-predictions",
            partitions: 2,
            replication: 3,
            messageCount: getRandomInt(50000, 250000),
            created: "2025-05-10 00:00:00",
            throughput: getRandomInt(25, 100) + " msg/sec",
            size: formatSize(getRandomInt(1024 * 1024 * 300, 1024 * 1024 * 900)),
            retention: "7 days"
        },
        {
            name: "audit-trail",
            partitions: 1,
            replication: 3,
            messageCount: getRandomInt(10000, 50000),
            created: "2025-05-15 00:00:00",
            throughput: getRandomInt(5, 25) + " msg/sec",
            size: formatSize(getRandomInt(1024 * 1024 * 50, 1024 * 1024 * 200)),
            retention: "365 days"
        }
    ];
    
    // Populate the Kafka topics table
    const kafkaTopicsTableBody = document.querySelector('#kafka-topics-table tbody');
    if (kafkaTopicsTableBody) {
        let html = '';
        
        kafkaTopics.forEach(topic => {
            const messagesClass = topic.messageCount > 500000 ? 'text-success' : (topic.messageCount < 50000 ? 'text-muted' : '');
            
            html += `
            <tr data-topic="${topic.name}">
                <td><strong>${topic.name}</strong></td>
                <td>${topic.partitions}</td>
                <td>${topic.replication}</td>
                <td class="${messagesClass}">${formatNumber(topic.messageCount)}</td>
                <td>${topic.throughput}</td>
                <td>${topic.size}</td>
                <td>${topic.retention}</td>
                <td>${topic.created}</td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary view-topic-btn" title="View Messages" data-topic="${topic.name}">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-outline-info" title="View Metrics">
                            <i class="fas fa-chart-line"></i>
                        </button>
                        <button class="btn btn-outline-secondary" title="Edit Configuration">
                            <i class="fas fa-cog"></i>
                        </button>
                    </div>
                </td>
            </tr>
            `;
        });
        
        kafkaTopicsTableBody.innerHTML = html;
        
        // Add event listeners to view topic buttons
        document.querySelectorAll('.view-topic-btn').forEach(button => {
            button.addEventListener('click', function() {
                const topicName = this.getAttribute('data-topic');
                selectTopic(topicName);
            });
        });
        
        // Add event listeners to table rows for selection
        document.querySelectorAll('#kafka-topics-table tbody tr').forEach(row => {
            row.addEventListener('click', function() {
                const topicName = this.getAttribute('data-topic');
                selectTopic(topicName);
            });
        });
    }
}

// Populate Kafka Messages with dummy data
function populateKafkaMessages(animate = false, topic = null) {
    // If no specific topic is provided, use the currently selected topic
    const selectedTopic = topic || document.getElementById('selected-topic-name').textContent;
    
    // Show topic name in messages tab
    document.getElementById('messages-topic-name').textContent = selectedTopic;
    
    // Create dummy data for Kafka messages based on topic
    const kafkaMessages = generateMessagesForTopic(selectedTopic, 50);
    
    // Populate the Kafka messages table
    const kafkaMessagesTableBody = document.querySelector('#kafka-messages-table tbody');
    if (kafkaMessagesTableBody) {
        let html = '';
        
        kafkaMessages.forEach((message, index) => {
            html += `
            <tr>
                <td>${message.offset}</td>
                <td>${message.partition}</td>
                <td><code>${message.key || '<null>'}</code></td>
                <td class="text-truncate" style="max-width: 400px;">
                    <code>${escapeHtml(JSON.stringify(message.value))}</code>
                </td>
                <td>${formatDateTime(message.timestamp)}</td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary view-message-btn" data-message-index="${index}" title="View Full Message">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-outline-secondary copy-message-btn" data-message-index="${index}" title="Copy Message">
                            <i class="fas fa-copy"></i>
                        </button>
                    </div>
                </td>
            </tr>
            `;
        });
        
        kafkaMessagesTableBody.innerHTML = html;
        
        // Store messages in a global variable for viewing details
        window.currentKafkaMessages = kafkaMessages;
        
        // Add event listeners to view message buttons
        document.querySelectorAll('.view-message-btn').forEach(button => {
            button.addEventListener('click', function() {
                const messageIndex = parseInt(this.getAttribute('data-message-index'));
                viewMessageDetails(messageIndex);
            });
        });
    }
    
    // Update message stats
    updateMessageStats(selectedTopic, kafkaMessages);
}

// Populate Consumer Groups with dummy data
function populateConsumerGroups(animate = false) {
    // Create dummy data for consumer groups
    const consumerGroups = [
        {
            id: "log-processor-group",
            members: 3,
            topics: ["logs-topic", "app-logs"],
            totalLag: getRandomInt(50, 500),
            status: "Stable"
        },
        {
            id: "metrics-analyzer",
            members: 5,
            topics: ["metrics-topic", "system-metrics"],
            totalLag: getRandomInt(100, 1000),
            status: "Stable"
        },
        {
            id: "alert-manager",
            members: 2,
            topics: ["alerts-topic"],
            totalLag: getRandomInt(0, 20),
            status: "Stable"
        },
        {
            id: "clickstream-processor",
            members: 8,
            topics: ["clickstream-topic"],
            totalLag: getRandomInt(2000, 10000),
            status: "Warning"
        },
        {
            id: "user-activity-tracker",
            members: 4,
            topics: ["user-activity"],
            totalLag: getRandomInt(500, 3000),
            status: "Stable"
        },
        {
            id: "api-monitor",
            members: 3,
            topics: ["api-requests"],
            totalLag: getRandomInt(200, 1500),
            status: "Stable"
        },
        {
            id: "transaction-handler",
            members: 5,
            topics: ["transaction-events"],
            totalLag: getRandomInt(50, 200),
            status: "Stable"
        },
        {
            id: "ml-service",
            members: 2,
            topics: ["ml-predictions"],
            totalLag: getRandomInt(10, 100),
            status: "Stable"
        },
        {
            id: "compliance-auditor",
            members: 1,
            topics: ["audit-trail"],
            totalLag: getRandomInt(5, 50),
            status: "Stable"
        }
    ];
    
    // Populate the consumer groups table
    const consumerGroupsTableBody = document.querySelector('#consumer-groups-table tbody');
    if (consumerGroupsTableBody) {
        let html = '';
        
        consumerGroups.forEach(group => {
            const statusClass = group.status === "Stable" ? "success" : 
                              (group.status === "Warning" ? "warning" : "danger");
            
            html += `
            <tr>
                <td><strong>${group.id}</strong></td>
                <td>${group.members}</td>
                <td>${group.topics.join(", ")}</td>
                <td>${formatNumber(group.totalLag)}</td>
                <td><span class="badge bg-${statusClass}">${group.status}</span></td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" title="View Details">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-outline-secondary" title="View Offsets">
                            <i class="fas fa-list-ol"></i>
                        </button>
                        <button class="btn btn-outline-danger" title="Reset Offsets">
                            <i class="fas fa-undo"></i>
                        </button>
                    </div>
                </td>
            </tr>
            `;
        });
        
        consumerGroupsTableBody.innerHTML = html;
    }
}

// Helper function to generate messages for a specific topic
function generateMessagesForTopic(topic, count) {
    const messages = [];
    const now = new Date();
    
    // Define message templates based on topic type
    const messageTypes = {
        "logs-topic": () => ({
            timestamp: new Date(now - getRandomInt(0, 3600000)),
            level: getRandomItem(["INFO", "WARN", "ERROR", "DEBUG"]),
            service: getRandomItem(["api-gateway", "auth-service", "user-service", "payment-service"]),
            message: getRandomItem([
                "Request processed successfully",
                "Database connection established",
                "User login attempt",
                "Cache miss for key",
                "Rate limit exceeded",
                "Slow query detected",
                "API request timeout"
            ]),
            requestId: generateId(8),
            duration: getRandomInt(5, 500)
        }),
        "metrics-topic": () => ({
            timestamp: new Date(now - getRandomInt(0, 3600000)),
            service: getRandomItem(["api-gateway", "auth-service", "user-service", "payment-service"]),
            metrics: {
                cpu: getRandomFloat(0.1, 95.0).toFixed(1),
                memory: getRandomFloat(10.0, 85.0).toFixed(1),
                requestCount: getRandomInt(10, 5000),
                responseTime: getRandomInt(5, 500),
                errorRate: getRandomFloat(0.0, 5.0).toFixed(2)
            }
        }),
        "events-topic": () => ({
            timestamp: new Date(now - getRandomInt(0, 3600000)),
            eventType: getRandomItem(["USER_CREATED", "USER_UPDATED", "ITEM_ADDED", "ITEM_REMOVED", "CHECKOUT_COMPLETED"]),
            userId: generateId(6),
            data: {
                id: generateId(8),
                source: getRandomItem(["web", "mobile", "api"]),
                ipAddress: `192.168.${getRandomInt(1, 255)}.${getRandomInt(1, 255)}`
            }
        }),
        "alerts-topic": () => ({
            timestamp: new Date(now - getRandomInt(0, 3600000)),
            alertId: generateId(10),
            severity: getRandomItem(["CRITICAL", "HIGH", "MEDIUM", "LOW"]),
            source: getRandomItem(["monitoring", "security", "system"]),
            message: getRandomItem([
                "High CPU usage detected",
                "Disk space below threshold",
                "Multiple failed login attempts",
                "API endpoint unreachable",
                "Database connection timeout"
            ]),
            affectedService: getRandomItem(["api-gateway", "auth-service", "user-service", "database"])
        }),
        "clickstream-topic": () => ({
            timestamp: new Date(now - getRandomInt(0, 3600000)),
            sessionId: generateId(12),
            userId: getRandomItem([null, generateId(8)]),
            action: getRandomItem(["PAGE_VIEW", "CLICK", "SCROLL", "FORM_SUBMIT", "VIDEO_PLAY"]),
            page: getRandomItem(["/home", "/products", "/about", "/contact", "/checkout", "/profile"]),
            referrer: getRandomItem(["https://google.com", "https://facebook.com", "https://twitter.com", "https://linkedin.com", null]),
            device: getRandomItem(["desktop", "mobile", "tablet"]),
            browser: getRandomItem(["Chrome", "Firefox", "Safari", "Edge"])
        }),
        "default": () => ({
            timestamp: new Date(now - getRandomInt(0, 3600000)),
            key: generateId(10),
            value: `Sample message for ${topic}`,
            metadata: {
                source: "kafka-generator",
                version: "1.0"
            }
        })
    };
    
    // Create messages
    for (let i = 0; i < count; i++) {
        const offset = 1000000 + i;
        const partition = getRandomInt(0, getPartitionsForTopic(topic) - 1);
        const key = Math.random() > 0.3 ? generateId(8) : null;
        
        // Generate message value based on topic type
        const valueGenerator = messageTypes[topic] || messageTypes.default;
        const value = valueGenerator();
        
        messages.push({
            offset: offset,
            partition: partition,
            key: key,
            value: value,
            timestamp: value.timestamp || new Date(now - getRandomInt(0, 3600000))
        });
    }
    
    // Sort by offset (descending)
    return messages.sort((a, b) => b.offset - a.offset);
}

// Helper function to get number of partitions for a topic
function getPartitionsForTopic(topic) {
    const partitionsMap = {
        "logs-topic": 3,
        "metrics-topic": 5,
        "events-topic": 2,
        "alerts-topic": 1,
        "clickstream-topic": 8,
        "user-activity": 6,
        "api-requests": 4,
        "system-metrics": 2,
        "app-logs": 3,
        "transaction-events": 5,
        "ml-predictions": 2,
        "audit-trail": 1
    };
    
    return partitionsMap[topic] || 3; // Default to 3 partitions
}

// Update message stats based on topic and messages
function updateMessageStats(topic, messages) {
    const messageStats = {
        totalMessages: messages.length,
        avgMessageSize: getRandomInt(500, 2000) + " bytes",
        topPartition: getRandomInt(0, getPartitionsForTopic(topic) - 1),
        messageRate: getRandomInt(10, 500) + " msg/sec"
    };
    
    document.getElementById('topic-message-count').textContent = formatNumber(messageStats.totalMessages);
    document.getElementById('topic-avg-size').textContent = messageStats.avgMessageSize;
    document.getElementById('topic-top-partition').textContent = messageStats.topPartition;
    document.getElementById('topic-message-rate').textContent = messageStats.messageRate;
}

// Setup topic selection functionality
function setupTopicSelection() {
    // Initial topic selection
    selectTopic('logs-topic');
    
    // Topic search functionality
    const topicSearchInput = document.getElementById('topic-search');
    if (topicSearchInput) {
        topicSearchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const rows = document.querySelectorAll('#kafka-topics-table tbody tr');
            
            rows.forEach(row => {
                const topicName = row.querySelector('td:first-child').textContent.toLowerCase();
                if (topicName.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }
}

// Select a topic and show its messages
function selectTopic(topicName) {
    // Update selected topic name
    document.getElementById('selected-topic-name').textContent = topicName;
    
    // Highlight the selected row
    const rows = document.querySelectorAll('#kafka-topics-table tbody tr');
    rows.forEach(row => {
        if (row.getAttribute('data-topic') === topicName) {
            row.classList.add('table-primary');
        } else {
            row.classList.remove('table-primary');
        }
    });
    
    // Switch to messages tab
    const tabEl = document.querySelector('#kafka-tabs button[data-bs-target="#messages"]');
    const tab = new bootstrap.Tab(tabEl);
    tab.show();
    
    // Load messages for the topic
    populateKafkaMessages(false, topicName);
}

// View full message details in a modal
function viewMessageDetails(messageIndex) {
    const message = window.currentKafkaMessages[messageIndex];
    if (!message) return;
    
    // Populate modal fields
    document.getElementById('message-modal-offset').textContent = message.offset;
    document.getElementById('message-modal-partition').textContent = message.partition;
    document.getElementById('message-modal-key').textContent = message.key || '<null>';
    document.getElementById('message-modal-timestamp').textContent = formatDateTime(message.timestamp);
    
    // Format JSON value
    const jsonValue = JSON.stringify(message.value, null, 2);
    document.getElementById('message-modal-value').textContent = jsonValue;
    
    // Show the modal
    const messageModal = new bootstrap.Modal(document.getElementById('messageDetailsModal'));
    messageModal.show();
}

// Helper function to get a random integer between min and max (inclusive)
function getRandomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

// Helper function to get a random float between min and max
function getRandomFloat(min, max) {
    return min + Math.random() * (max - min);
}

// Helper function to get a random item from an array
function getRandomItem(array) {
    return array[Math.floor(Math.random() * array.length)];
}

// Helper function to generate a random ID
function generateId(length) {
    const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
    let id = '';
    for (let i = 0; i < length; i++) {
        id += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return id;
}

// Helper function to format a number with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Helper function to format file size
function formatSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Helper function to format a date time
function formatDateTime(date) {
    if (typeof date === 'string') {
        date = new Date(date);
    }
    
    return date.toISOString().replace('T', ' ').substring(0, 19);
}

// Helper function to escape HTML
function escapeHtml(unsafe) {
    if (typeof unsafe !== 'string') {
        unsafe = JSON.stringify(unsafe);
    }
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
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