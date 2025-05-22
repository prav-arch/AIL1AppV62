// Simple Kafka Browser JavaScript for AI Assistant Platform

document.addEventListener('DOMContentLoaded', function() {
    console.log("Simple Kafka Browser JS loaded");
    populateKafkaStats();
    populateKafkaTopics();
    populateConsumerGroups();
    
    // Set initial selected topic
    document.getElementById('selected-topic-name').textContent = "logs-topic";
    document.getElementById('messages-topic-name').textContent = "logs-topic";
    
    // Populate messages for the initial topic
    populateKafkaMessages("logs-topic");
    
    // Add click handlers for refresh buttons
    document.getElementById('refresh-topics-btn')?.addEventListener('click', function() {
        populateKafkaStats(true);
        populateKafkaTopics(true);
    });
    
    document.getElementById('refresh-messages-btn')?.addEventListener('click', function() {
        const topicName = document.getElementById('selected-topic-name').textContent;
        populateKafkaMessages(topicName, true);
    });
    
    document.getElementById('refresh-consumers-btn')?.addEventListener('click', function() {
        populateConsumerGroups(true);
    });
    
    // Initialize tabs if not already done
    const triggerTabList = document.querySelectorAll('#kafka-tabs button');
    triggerTabList.forEach(triggerEl => {
        triggerEl.addEventListener('click', function(event) {
            event.preventDefault();
            const tab = new bootstrap.Tab(this);
            tab.show();
        });
    });
});

// Populate Kafka Statistics
function populateKafkaStats(animate = false) {
    updateElement('broker-count', getRandomInt(3, 5), animate);
    updateElement('total-topics', getRandomInt(12, 18), animate);
    updateElement('consumer-groups-count', getRandomInt(8, 15), animate);
    updateElement('total-messages', formatNumber(getRandomInt(500000, 3000000)), animate);
}

// Populate Kafka Topics Table
function populateKafkaTopics(animate = false) {
    const topics = [
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
    
    const tableBody = document.querySelector('#kafka-topics-table tbody');
    if (tableBody) {
        let html = '';
        
        topics.forEach(topic => {
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
        
        tableBody.innerHTML = html;
        
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
    
    // Update topic stats
    document.getElementById('topic-message-count').textContent = "Loading...";
    document.getElementById('topic-avg-size').textContent = "Loading...";
    document.getElementById('topic-top-partition').textContent = "Loading...";
    document.getElementById('topic-message-rate').textContent = "Loading...";
}

// Populate Kafka Messages
function populateKafkaMessages(topicName, animate = false) {
    // Update the selected topic name in the UI
    document.getElementById('selected-topic-name').textContent = topicName;
    document.getElementById('messages-topic-name').textContent = topicName;
    
    // Generate mock messages based on topic type
    const messages = generateMessagesForTopic(topicName, 10);
    
    // Update the messages table
    const tableBody = document.querySelector('#kafka-messages-table tbody');
    if (tableBody) {
        let html = '';
        
        messages.forEach((message, index) => {
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
        
        tableBody.innerHTML = html;
        
        // Store messages in a global variable for viewing details
        window.currentKafkaMessages = messages;
        
        // Add event listeners to view message buttons
        document.querySelectorAll('.view-message-btn').forEach(button => {
            button.addEventListener('click', function() {
                const messageIndex = parseInt(this.getAttribute('data-message-index'));
                viewMessageDetails(messageIndex);
            });
        });
    }
    
    // Update topic statistics
    updateTopicStats(topicName);
}

// Populate Consumer Groups
function populateConsumerGroups(animate = false) {
    const groups = [
        {
            id: "log-processor-group",
            members: 3,
            topics: ["logs-topic", "app-logs"],
            totalLag: 275,
            status: "Stable"
        },
        {
            id: "metrics-analyzer",
            members: 5,
            topics: ["metrics-topic", "system-metrics"],
            totalLag: 482,
            status: "Stable"
        },
        {
            id: "alert-manager",
            members: 2,
            topics: ["alerts-topic"],
            totalLag: 12,
            status: "Stable"
        },
        {
            id: "clickstream-processor",
            members: 8,
            topics: ["clickstream-topic"],
            totalLag: 8763,
            status: "Warning"
        },
        {
            id: "user-activity-tracker",
            members: 4,
            topics: ["user-activity"],
            totalLag: 1254,
            status: "Stable"
        }
    ];
    
    const tableBody = document.querySelector('#consumer-groups-table tbody');
    if (tableBody) {
        let html = '';
        
        groups.forEach(group => {
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
        
        tableBody.innerHTML = html;
    }
}

// Update topic statistics
function updateTopicStats(topicName) {
    // Generate realistic stats based on topic
    const stats = {
        logs: {
            count: formatNumber(524892),
            avgSize: "1.4 KB",
            topPartition: 1,
            messageRate: "120 msg/sec"
        },
        metrics: {
            count: formatNumber(328157),
            avgSize: "3.8 KB",
            topPartition: 2,
            messageRate: "250 msg/sec"
        },
        events: {
            count: formatNumber(125628),
            avgSize: "2.2 KB",
            topPartition: 0,
            messageRate: "45 msg/sec"
        },
        alerts: {
            count: formatNumber(8421),
            avgSize: "1.5 KB",
            topPartition: 0,
            messageRate: "5 msg/sec"
        },
        clickstream: {
            count: formatNumber(1458276),
            avgSize: "2.5 KB",
            topPartition: 3,
            messageRate: "850 msg/sec"
        }
    };
    
    // Set default stats if topic not found
    const topicType = topicName.split('-')[0];
    const topicStats = stats[topicType] || {
        count: formatNumber(getRandomInt(10000, 500000)),
        avgSize: "2.0 KB",
        topPartition: 0,
        messageRate: "50 msg/sec"
    };
    
    // Update stats in UI
    document.getElementById('topic-message-count').textContent = topicStats.count;
    document.getElementById('topic-avg-size').textContent = topicStats.avgSize;
    document.getElementById('topic-top-partition').textContent = topicStats.topPartition;
    document.getElementById('topic-message-rate').textContent = topicStats.messageRate;
}

// Helper function to select a topic
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
    populateKafkaMessages(topicName);
}

// Helper function to generate messages for a specific topic
function generateMessagesForTopic(topicName, count) {
    const messages = [];
    const now = new Date();
    const baseOffset = 1000000;
    
    // Get the number of partitions for this topic
    const partitionsMap = {
        "logs-topic": 3,
        "metrics-topic": 5,
        "events-topic": 2,
        "alerts-topic": 1,
        "clickstream-topic": 8,
        "user-activity": 6,
        "api-requests": 4
    };
    const partitions = partitionsMap[topicName] || 3;
    
    // Generate messages based on topic type
    for (let i = 0; i < count; i++) {
        const offset = baseOffset + i;
        const partition = getRandomInt(0, partitions - 1);
        const timestamp = new Date(now.getTime() - getRandomInt(0, 3600000));
        const key = Math.random() > 0.3 ? generateId(8) : null;
        let value;
        
        // Generate appropriate value for each topic type
        if (topicName === "logs-topic") {
            value = {
                timestamp: timestamp,
                level: getRandomItem(["INFO", "WARN", "ERROR", "DEBUG"]),
                service: getRandomItem(["api-gateway", "auth-service", "user-service", "payment-service"]),
                message: getRandomItem([
                    "Request processed successfully",
                    "Database connection established",
                    "User login attempt",
                    "Cache miss for key",
                    "Rate limit exceeded"
                ]),
                requestId: generateId(8),
                duration: getRandomInt(5, 500)
            };
        } else if (topicName === "metrics-topic") {
            value = {
                timestamp: timestamp,
                service: getRandomItem(["api-gateway", "auth-service", "user-service", "payment-service"]),
                metrics: {
                    cpu: getRandomFloat(0.1, 95.0).toFixed(1),
                    memory: getRandomFloat(10.0, 85.0).toFixed(1),
                    requestCount: getRandomInt(10, 5000),
                    responseTime: getRandomInt(5, 500),
                    errorRate: getRandomFloat(0.0, 5.0).toFixed(2)
                }
            };
        } else if (topicName === "events-topic") {
            value = {
                timestamp: timestamp,
                eventType: getRandomItem(["USER_CREATED", "USER_UPDATED", "ITEM_ADDED", "ITEM_REMOVED", "CHECKOUT_COMPLETED"]),
                userId: generateId(6),
                data: {
                    id: generateId(8),
                    source: getRandomItem(["web", "mobile", "api"]),
                    ipAddress: `192.168.${getRandomInt(1, 255)}.${getRandomInt(1, 255)}`
                }
            };
        } else if (topicName === "alerts-topic") {
            value = {
                timestamp: timestamp,
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
            };
        } else if (topicName === "clickstream-topic") {
            value = {
                timestamp: timestamp,
                sessionId: generateId(12),
                userId: getRandomItem([null, generateId(8)]),
                action: getRandomItem(["PAGE_VIEW", "CLICK", "SCROLL", "FORM_SUBMIT", "VIDEO_PLAY"]),
                page: getRandomItem(["/home", "/products", "/about", "/contact", "/checkout", "/profile"]),
                referrer: getRandomItem(["https://google.com", "https://facebook.com", "https://twitter.com", null]),
                device: getRandomItem(["desktop", "mobile", "tablet"]),
                browser: getRandomItem(["Chrome", "Firefox", "Safari", "Edge"])
            };
        } else {
            value = {
                timestamp: timestamp,
                key: generateId(10),
                value: `Sample message for ${topicName}`,
                metadata: {
                    source: "kafka-generator",
                    version: "1.0"
                }
            };
        }
        
        messages.push({
            offset: offset,
            partition: partition,
            key: key,
            value: value,
            timestamp: timestamp
        });
    }
    
    // Sort by offset (descending)
    return messages.sort((a, b) => b.offset - a.offset);
}

// View message details
function viewMessageDetails(messageIndex) {
    const message = window.currentKafkaMessages?.[messageIndex];
    if (!message) return;
    
    // Use Bootstrap modal if available
    const modalEl = document.getElementById('messageDetailsModal');
    if (modalEl) {
        document.getElementById('message-modal-offset').textContent = message.offset;
        document.getElementById('message-modal-partition').textContent = message.partition;
        document.getElementById('message-modal-key').textContent = message.key || '<null>';
        document.getElementById('message-modal-timestamp').textContent = formatDateTime(message.timestamp);
        
        // Format the JSON for display
        const jsonValue = JSON.stringify(message.value, null, 2);
        const valueEl = document.getElementById('message-modal-value');
        if (valueEl) {
            valueEl.textContent = jsonValue;
        }
        
        // Show the modal
        const modal = new bootstrap.Modal(modalEl);
        modal.show();
    } else {
        // Fallback if no modal is available
        alert(`Message ${message.offset}: ${JSON.stringify(message.value)}`);
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

// Helper function to format a date time
function formatDateTime(date) {
    if (typeof date === 'string') {
        date = new Date(date);
    }
    
    return date.toISOString().replace('T', ' ').substring(0, 19);
}

// Helper function to escape HTML entities
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