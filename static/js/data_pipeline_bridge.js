// Bridge between data_pipeline.js and data_pipeline_data.js

// Override fetch functions to use our dummy data
function fetchNifiJobs() {
    console.log("Fetching NiFi jobs from dummy data");
    populateNifiJobs();
}

function fetchAirflowDags() {
    console.log("Fetching Airflow DAGs from dummy data");
    populateAirflowDags();
}

function fetchJobStatus() {
    console.log("Fetching job status from dummy data");
    populateJobStatus();
}

// Initialize job timeline visualization if needed
function initializeJobTimeline() {
    // This is already handled in populateJobStatus() in data_pipeline_data.js
    console.log("Job timeline initialization via dummy data");
}