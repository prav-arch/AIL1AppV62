// Bridge between kafka_browser.js and kafka_browser_data.js

// Override fetch functions to use our dummy data
function fetchKafkaTopics() {
    console.log("Fetching Kafka topics from dummy data");
    populateKafkaTopics();
}

function fetchKafkaMessages(topic) {
    console.log("Fetching Kafka messages from dummy data for topic:", topic);
    populateKafkaMessages(false, topic);
}

function fetchConsumerGroups() {
    console.log("Fetching consumer groups from dummy data");
    populateConsumerGroups();
}

// Initialize any additional functionality
function initializeKafkaDashboard() {
    console.log("Initializing Kafka dashboard with dummy data");
    // This is handled in the DOMContentLoaded event in kafka_browser_data.js
}