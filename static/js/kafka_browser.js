// Kafka Browser JavaScript for AI Assistant Platform

document.addEventListener('DOMContentLoaded', function() {
    // Initialize DataTables
    initializeDataTables();
    
    // Setup tab behavior
    setupTabBehavior();
    
    // Setup event listeners
    setupEventListeners();
    
    // Fetch initial data
    fetchKafkaTopics();
});

// Initialize DataTables
function initializeDataTables() {
    if ($.fn.DataTable) {
        $('#kafka-topics-table').DataTable({
            responsive: true,
            pageLength: 10
        });
        
        $('#kafka-messages-table').DataTable({
            responsive: true,
            pageLength: 10,
            order: [[0, 'desc']] // Sort by offset desc
        });
    }
}

// Setup Tab Behavior
function setupTabBehavior() {
    const triggerTabList = document.querySelectorAll('#kafka-tabs button');
    triggerTabList.forEach(triggerEl => {
        triggerEl.addEventListener('click', function(event) {
            event.preventDefault();
            const tab = new bootstrap.Tab(this);
            tab.show();
        });
    });
}

// Setup Event Listeners
function setupEventListeners() {
    // Refresh buttons
    document.getElementById('refresh-topics-btn')?.addEventListener('click', fetchKafkaTopics);
    document.getElementById('refresh-messages-btn')?.addEventListener('click', function() {
        const selectedTopic = document.getElementById('topic-selector').value;
        if (selectedTopic) {
            fetchKafkaMessages(selectedTopic);
        }
    });
    
    // Topic selector
    document.getElementById('topic-selector')?.addEventListener('change', function() {
        const selectedTopic = this.value;
        if (selectedTopic) {
            fetchKafkaMessages(selectedTopic);
            document.getElementById('selected-topic-title').textContent = selectedTopic;
            document.getElementById('message-tab').classList.remove('d-none');
        }
    });
    
    // Send message form
    document.getElementById('send-message-form')?.addEventListener('submit', function(e) {
        e.preventDefault();
        sendMessage();
    });
    
    // Create topic form
    document.getElementById('create-topic-form')?.addEventListener('submit', function(e) {
        e.preventDefault();
        createTopic();
    });
    
    // View message details
    document.addEventListener('click', function(e) {
        if (e.target && e.target.matches('.view-message-btn')) {
            const messageId = e.target.getAttribute('data-message-id');
            const messageOffset = e.target.getAttribute('data-message-offset');
            viewMessageDetails(messageId, messageOffset);
        }
    });
    
    // Delete message buttons
    document.addEventListener('click', function(e) {
        if (e.target && e.target.matches('.delete-message-btn')) {
            const messageId = e.target.getAttribute('data-message-id');
            const messageOffset = e.target.getAttribute('data-message-offset');
            const topic = document.getElementById('topic-selector').value;
            deleteMessage(topic, messageOffset, messageId);
        }
    });
    
    // Delete topic buttons
    document.addEventListener('click', function(e) {
        if (e.target && e.target.matches('.delete-topic-btn')) {
            const topic = e.target.getAttribute('data-topic');
            deleteTopic(topic);
        }
    });
    
    // Auto-refresh toggle
    document.getElementById('auto-refresh-toggle')?.addEventListener('change', function() {
        toggleAutoRefresh(this.checked);
    });
    
    // Consumer group selector
    document.getElementById('consumer-group-selector')?.addEventListener('change', function() {
        const selectedTopic = document.getElementById('topic-selector').value;
        const selectedGroup = this.value;
        
        if (selectedTopic && selectedGroup) {
            fetchConsumerGroupOffset(selectedTopic, selectedGroup);
        }
    });
}

// Fetch Kafka Topics
async function fetchKafkaTopics() {
    try {
        const response = await fetchWithTimeout('/api/kafka/topics');
        const data = await response.json();
        
        if (data.success) {
            updateKafkaTopics(data.topics);
            updateTopicSelector(data.topics);
            updateConsumerGroups(data.consumer_groups);
            updateClusterInfo(data.cluster_info);
        } else {
            throw new Error(data.message || 'Failed to fetch Kafka topics');
        }
    } catch (error) {
        handleFetchError(error, 'fetch Kafka topics');
    }
}

// Update Kafka Topics Table
function updateKafkaTopics(topics) {
    const tableBody = document.querySelector('#kafka-topics-table tbody');
    if (!tableBody) return;
    
    // If DataTable is initialized, destroy it first
    if ($.fn.DataTable.isDataTable('#kafka-topics-table')) {
        $('#kafka-topics-table').DataTable().destroy();
    }
    
    // Clear the table body
    tableBody.innerHTML = '';
    
    // Add topics to the table
    topics.forEach((topic) => {
        const tr = document.createElement('tr');
        
        tr.innerHTML = `
            <td>${escapeHtml(topic.name)}</td>
            <td>${topic.partitions}</td>
            <td>${topic.replication_factor}</td>
            <td>${formatNumber(topic.message_count)}</td>
            <td>${formatDateTime(topic.created_at)}</td>
            <td>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary view-topic-btn" data-topic="${escapeHtml(topic.name)}">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-outline-danger delete-topic-btn" data-topic="${escapeHtml(topic.name)}">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        `;
        
        tableBody.appendChild(tr);
    });
    
    // Reinitialize DataTable
    $('#kafka-topics-table').DataTable({
        responsive: true,
        pageLength: 10
    });
    
    // Update topic count cards
    if (document.getElementById('topic-count')) {
        document.getElementById('topic-count').textContent = topics.length;
    }
}

// Update Topic Selector Dropdown
function updateTopicSelector(topics) {
    const topicSelector = document.getElementById('topic-selector');
    if (!topicSelector) return;
    
    // Save current selection
    const currentSelection = topicSelector.value;
    
    // Clear options
    topicSelector.innerHTML = '<option value="">Select a topic</option>';
    
    // Add topics to the selector
    topics.forEach((topic) => {
        const option = document.createElement('option');
        option.value = topic.name;
        option.textContent = topic.name;
        topicSelector.appendChild(option);
    });
    
    // Restore selection if it exists
    if (currentSelection && topics.some(topic => topic.name === currentSelection)) {
        topicSelector.value = currentSelection;
    }
}

// Update Consumer Groups Selector
function updateConsumerGroups(consumerGroups) {
    const groupSelector = document.getElementById('consumer-group-selector');
    if (!groupSelector) return;
    
    // Save current selection
    const currentSelection = groupSelector.value;
    
    // Clear options
    groupSelector.innerHTML = '<option value="">Select a consumer group</option>';
    
    // Add consumer groups to the selector
    consumerGroups.forEach((group) => {
        const option = document.createElement('option');
        option.value = group.id;
        option.textContent = group.id;
        groupSelector.appendChild(option);
    });
    
    // Restore selection if it exists
    if (currentSelection && consumerGroups.some(group => group.id === currentSelection)) {
        groupSelector.value = currentSelection;
    }
}

// Update Cluster Info
function updateClusterInfo(clusterInfo) {
    if (document.getElementById('broker-count')) {
        document.getElementById('broker-count').textContent = clusterInfo.broker_count || '0';
    }
    
    if (document.getElementById('total-topics')) {
        document.getElementById('total-topics').textContent = clusterInfo.topic_count || '0';
    }
    
    if (document.getElementById('consumer-groups-count')) {
        document.getElementById('consumer-groups-count').textContent = clusterInfo.consumer_group_count || '0';
    }
    
    if (document.getElementById('total-messages')) {
        document.getElementById('total-messages').textContent = formatNumber(clusterInfo.total_messages || 0);
    }
}

// Fetch Kafka Messages for a Topic
async function fetchKafkaMessages(topic) {
    try {
        const response = await fetchWithTimeout(`/api/kafka/topics/${encodeURIComponent(topic)}/messages`);
        const data = await response.json();
        
        if (data.success) {
            updateKafkaMessages(data.messages);
            updateMessageStats(data.stats);
        } else {
            throw new Error(data.message || 'Failed to fetch Kafka messages');
        }
    } catch (error) {
        handleFetchError(error, 'fetch Kafka messages');
    }
}

// Update Kafka Messages Table
function updateKafkaMessages(messages) {
    const tableBody = document.querySelector('#kafka-messages-table tbody');
    if (!tableBody) return;
    
    // If DataTable is initialized, destroy it first
    if ($.fn.DataTable.isDataTable('#kafka-messages-table')) {
        $('#kafka-messages-table').DataTable().destroy();
    }
    
    // Clear the table body
    tableBody.innerHTML = '';
    
    // Add messages to the table
    messages.forEach((message) => {
        const tr = document.createElement('tr');
        
        // Truncate message value if too long
        let messageValue = message.value;
        if (messageValue && messageValue.length > 100) {
            messageValue = messageValue.substring(0, 100) + '...';
        }
        
        tr.innerHTML = `
            <td>${message.offset}</td>
            <td>${message.partition}</td>
            <td>${message.key || '<null>'}</td>
            <td>${escapeHtml(messageValue)}</td>
            <td>${formatDateTime(message.timestamp)}</td>
            <td>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary view-message-btn" data-message-id="${message.id}" data-message-offset="${message.offset}">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-outline-danger delete-message-btn" data-message-id="${message.id}" data-message-offset="${message.offset}">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        `;
        
        tableBody.appendChild(tr);
    });
    
    // Reinitialize DataTable
    $('#kafka-messages-table').DataTable({
        responsive: true,
        pageLength: 10,
        order: [[0, 'desc']] // Sort by offset desc
    });
    
    // Update message count
    if (document.getElementById('message-count')) {
        document.getElementById('message-count').textContent = messages.length;
    }
}

// Update Message Stats
function updateMessageStats(stats) {
    // Update message rate chart if available
    if (stats.message_rate && Chart.getChart('message-rate-chart')) {
        const chart = Chart.getChart('message-rate-chart');
        
        chart.data.labels = stats.message_rate.labels;
        chart.data.datasets[0].data = stats.message_rate.values;
        
        chart.update();
    }
    
    // Update message size chart if available
    if (stats.message_size && Chart.getChart('message-size-chart')) {
        const chart = Chart.getChart('message-size-chart');
        
        chart.data.labels = stats.message_size.labels;
        chart.data.datasets[0].data = stats.message_size.values;
        
        chart.update();
    }
    
    // Update partition distribution chart if available
    if (stats.partition_distribution && Chart.getChart('partition-distribution-chart')) {
        const chart = Chart.getChart('partition-distribution-chart');
        
        chart.data.labels = Object.keys(stats.partition_distribution);
        chart.data.datasets[0].data = Object.values(stats.partition_distribution);
        
        chart.update();
    }
}

// Fetch Consumer Group Offset
async function fetchConsumerGroupOffset(topic, group) {
    try {
        const response = await fetchWithTimeout(`/api/kafka/consumer-groups/${encodeURIComponent(group)}/topics/${encodeURIComponent(topic)}`);
        const data = await response.json();
        
        if (data.success) {
            updateConsumerGroupOffset(data.offsets);
        } else {
            throw new Error(data.message || 'Failed to fetch consumer group offsets');
        }
    } catch (error) {
        handleFetchError(error, 'fetch consumer group offsets');
    }
}

// Update Consumer Group Offset
function updateConsumerGroupOffset(offsets) {
    const offsetTable = document.getElementById('consumer-offset-table');
    if (!offsetTable) return;
    
    // Clear the table body
    const tableBody = offsetTable.querySelector('tbody');
    tableBody.innerHTML = '';
    
    // Add offsets to the table
    offsets.forEach((offset) => {
        const tr = document.createElement('tr');
        
        // Calculate lag
        const lag = offset.log_end_offset - offset.offset;
        
        tr.innerHTML = `
            <td>${offset.partition}</td>
            <td>${offset.offset}</td>
            <td>${offset.log_end_offset}</td>
            <td>${lag}</td>
        `;
        
        tableBody.appendChild(tr);
    });
}

// Send Message
async function sendMessage() {
    const topic = document.getElementById('topic-selector').value;
    const messageKey = document.getElementById('message-key').value;
    const messageValue = document.getElementById('message-value').value;
    const partition = document.getElementById('message-partition').value;
    
    if (!topic) {
        showToast('Please select a topic', 'warning');
        return;
    }
    
    if (!messageValue) {
        showToast('Please enter a message value', 'warning');
        return;
    }
    
    try {
        const response = await fetchWithTimeout('/api/kafka/messages', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                topic: topic,
                key: messageKey || null,
                value: messageValue,
                partition: partition ? parseInt(partition) : null
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Message sent successfully', 'success');
            
            // Clear form
            document.getElementById('message-key').value = '';
            document.getElementById('message-value').value = '';
            document.getElementById('message-partition').value = '';
            
            // Refresh messages
            fetchKafkaMessages(topic);
        } else {
            throw new Error(data.message || 'Failed to send message');
        }
    } catch (error) {
        handleFetchError(error, 'send message');
    }
}

// Create Topic
async function createTopic() {
    const topicName = document.getElementById('new-topic-name').value;
    const partitions = document.getElementById('new-topic-partitions').value;
    const replicationFactor = document.getElementById('new-topic-replication').value;
    
    if (!topicName) {
        showToast('Please enter a topic name', 'warning');
        return;
    }
    
    try {
        const response = await fetchWithTimeout('/api/kafka/topics', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: topicName,
                partitions: parseInt(partitions),
                replication_factor: parseInt(replicationFactor)
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Topic created successfully', 'success');
            
            // Clear form
            document.getElementById('new-topic-name').value = '';
            
            // Close modal
            bootstrap.Modal.getInstance(document.getElementById('createTopicModal')).hide();
            
            // Refresh topics
            fetchKafkaTopics();
        } else {
            throw new Error(data.message || 'Failed to create topic');
        }
    } catch (error) {
        handleFetchError(error, 'create topic');
    }
}

// View Message Details
function viewMessageDetails(messageId, offset) {
    const topic = document.getElementById('topic-selector').value;
    
    // Open modal with loading state
    const modal = new bootstrap.Modal(document.getElementById('messageDetailsModal'));
    
    // Set loading state
    document.getElementById('message-details-content').innerHTML = `
        <div class="d-flex justify-content-center py-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>
    `;
    
    // Update modal title
    document.getElementById('messageDetailsModalLabel').textContent = `Message Details (Offset: ${offset})`;
    
    // Show modal
    modal.show();
    
    // Fetch message details
    fetchMessageDetails(topic, offset, messageId);
}

// Fetch Message Details
async function fetchMessageDetails(topic, offset, messageId) {
    try {
        const response = await fetchWithTimeout(`/api/kafka/topics/${encodeURIComponent(topic)}/messages/${offset}`);
        const data = await response.json();
        
        if (data.success) {
            displayMessageDetails(data.message);
        } else {
            throw new Error(data.message || 'Failed to fetch message details');
        }
    } catch (error) {
        handleFetchError(error, 'fetch message details');
        
        // Update modal content with error
        document.getElementById('message-details-content').innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Failed to fetch message details: ${error.message}
            </div>
        `;
    }
}

// Display Message Details
function displayMessageDetails(message) {
    const detailsContent = document.getElementById('message-details-content');
    if (!detailsContent) return;
    
    // Format the message value if it's JSON
    let formattedValue = message.value;
    try {
        if (message.value && message.value.trim().startsWith('{')) {
            const parsedJson = JSON.parse(message.value);
            formattedValue = JSON.stringify(parsedJson, null, 2);
        }
    } catch (e) {
        // Not valid JSON, use the raw value
        formattedValue = message.value;
    }
    
    detailsContent.innerHTML = `
        <div class="row mb-3">
            <div class="col-md-6">
                <h6>Topic</h6>
                <p>${escapeHtml(message.topic)}</p>
            </div>
            <div class="col-md-6">
                <h6>Partition</h6>
                <p>${message.partition}</p>
            </div>
        </div>
        
        <div class="row mb-3">
            <div class="col-md-6">
                <h6>Offset</h6>
                <p>${message.offset}</p>
            </div>
            <div class="col-md-6">
                <h6>Timestamp</h6>
                <p>${formatDateTime(message.timestamp)}</p>
            </div>
        </div>
        
        <div class="mb-3">
            <h6>Key</h6>
            <p>${message.key || '<null>'}</p>
        </div>
        
        <div class="mb-3">
            <h6>Value</h6>
            <pre class="bg-dark text-light p-3 rounded"><code>${escapeHtml(formattedValue)}</code></pre>
        </div>
        
        <div class="mb-3">
            <h6>Headers</h6>
            <pre class="bg-dark text-light p-3 rounded"><code>${JSON.stringify(message.headers || {}, null, 2)}</code></pre>
        </div>
    `;
}

// Delete Message
async function deleteMessage(topic, offset, messageId) {
    if (!confirm('Are you sure you want to delete this message? This action cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetchWithTimeout(`/api/kafka/topics/${encodeURIComponent(topic)}/messages/${offset}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Message deleted successfully', 'success');
            
            // Refresh messages
            fetchKafkaMessages(topic);
        } else {
            throw new Error(data.message || 'Failed to delete message');
        }
    } catch (error) {
        handleFetchError(error, 'delete message');
    }
}

// Delete Topic
async function deleteTopic(topic) {
    if (!confirm(`Are you sure you want to delete the topic "${topic}"? This action cannot be undone.`)) {
        return;
    }
    
    try {
        const response = await fetchWithTimeout(`/api/kafka/topics/${encodeURIComponent(topic)}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Topic deleted successfully', 'success');
            
            // Refresh topics
            fetchKafkaTopics();
            
            // If the deleted topic was selected, clear the messages table
            if (document.getElementById('topic-selector').value === topic) {
                document.getElementById('topic-selector').value = '';
                const tableBody = document.querySelector('#kafka-messages-table tbody');
                if (tableBody) {
                    tableBody.innerHTML = '';
                }
                
                // Hide message tab
                document.getElementById('message-tab').classList.add('d-none');
            }
        } else {
            throw new Error(data.message || 'Failed to delete topic');
        }
    } catch (error) {
        handleFetchError(error, 'delete topic');
    }
}

// Toggle Auto-Refresh
let autoRefreshInterval;
function toggleAutoRefresh(enabled) {
    if (enabled) {
        // Start auto-refresh (every 10 seconds)
        autoRefreshInterval = setInterval(() => {
            const selectedTopic = document.getElementById('topic-selector').value;
            if (selectedTopic) {
                fetchKafkaMessages(selectedTopic);
            }
        }, 10000);
        
        showToast('Auto-refresh enabled (10s interval)', 'info');
    } else {
        // Stop auto-refresh
        if (autoRefreshInterval) {
            clearInterval(autoRefreshInterval);
            autoRefreshInterval = null;
        }
        
        showToast('Auto-refresh disabled', 'info');
    }
}

// Helper function to format numbers with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}
