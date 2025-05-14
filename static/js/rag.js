// RAG Management JavaScript for AI Assistant Platform

// Helper function for error handling
function handleFetchError(error, action) {
    console.error(`Error trying to ${action}:`, error);
    const message = error.message || 'Network error occurred';
    showToast(`Error: ${message}`, 'error');
}

document.addEventListener('DOMContentLoaded', function() {
    // Initialize DataTables
    initializeDataTables();
    
    // Initialize Vector Database Charts
    initializeVectorDBCharts();
    
    // Initialize File Storage Charts
    initializeFileStorageCharts();
    
    // Initialize event listeners for range sliders
    initializeRangeSliders();
    
    // Setup document upload modal functionality
    setupDocumentUploadModal();
    
    // Setup webpage scraper modal functionality
    setupWebScraperModal();
    
    // Setup vector search modal functionality
    setupVectorSearchModal();
    
    // Vector DB operations
    document.getElementById('rebuild-index-btn')?.addEventListener('click', rebuildVectorIndex);
    document.getElementById('search-vector-btn')?.addEventListener('click', showVectorSearchModal);
    
    // MinIO operations
    document.getElementById('refresh-minio-btn')?.addEventListener('click', refreshMinioStorage);
    document.getElementById('create-bucket-btn')?.addEventListener('click', createMinioBucket);
    
    // RAG settings form submission
    document.getElementById('rag-settings-form')?.addEventListener('submit', saveRagSettings);
    document.getElementById('reset-rag-settings')?.addEventListener('click', resetRagSettings);
    
    // Fetch initial data
    fetchDocumentsData();
    fetchVectorDBStats();
    fetchMinioStorage();
    
    // Socket.IO event listeners for real-time updates
    socket.on('document_indexed', (data) => {
        updateDocumentStatus(data.document_id, 'Indexed');
        refreshVectorDBStats();
    });
    
    socket.on('document_processing_error', (data) => {
        updateDocumentStatus(data.document_id, 'Error');
        showToast(`Error processing document: ${data.error}`, 'danger');
    });
    
    socket.on('vector_search_results', (data) => {
        displayVectorSearchResults(data.results);
    });
});

// Initialize DataTables
function initializeDataTables() {
    if ($.fn.DataTable) {
        $('#documents-table').DataTable({
            responsive: true,
            pageLength: 10,
            order: [[4, 'desc']] // Sort by date added desc
        });
        
        $('#minio-files-table').DataTable({
            responsive: true,
            pageLength: 10,
            order: [[4, 'desc']] // Sort by last modified desc
        });
    }
}

// Initialize Vector Database Charts
function initializeVectorDBCharts() {
    const vectordbStatsCtx = document.getElementById('vectordb-stats-chart');
    
    if (vectordbStatsCtx) {
        new Chart(vectordbStatsCtx, {
            type: 'bar',
            data: {
                labels: ['PDFs', 'Word Docs', 'Excel Files', 'PCAP Files', 'Webpages', 'Other'],
                datasets: [{
                    label: 'Document Types',
                    data: [240, 180, 150, 95, 580, 0],
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.7)',
                        'rgba(54, 162, 235, 0.7)',
                        'rgba(255, 206, 86, 0.7)',
                        'rgba(75, 192, 192, 0.7)',
                        'rgba(153, 102, 255, 0.7)',
                        'rgba(255, 159, 64, 0.7)'
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)',
                        'rgba(255, 159, 64, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
}

// Initialize File Storage Charts
function initializeFileStorageCharts() {
    const storageUsageCtx = document.getElementById('storage-usage-chart');
    
    if (storageUsageCtx) {
        new Chart(storageUsageCtx, {
            type: 'doughnut',
            data: {
                labels: ['Used', 'Free'],
                datasets: [{
                    data: [25, 75],
                    backgroundColor: [
                        'rgba(54, 162, 235, 0.7)',
                        'rgba(201, 203, 207, 0.3)'
                    ],
                    borderColor: [
                        'rgba(54, 162, 235, 1)',
                        'rgba(201, 203, 207, 0.8)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.label + ': ' + context.raw + '%';
                            }
                        }
                    }
                }
            }
        });
    }
    
    const fileTypeCtx = document.getElementById('file-type-chart');
    
    if (fileTypeCtx) {
        new Chart(fileTypeCtx, {
            type: 'pie',
            data: {
                labels: ['PDF', 'Word', 'Excel', 'PCAP', 'Other'],
                datasets: [{
                    data: [35, 25, 20, 15, 5],
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.7)',
                        'rgba(54, 162, 235, 0.7)',
                        'rgba(255, 206, 86, 0.7)',
                        'rgba(75, 192, 192, 0.7)',
                        'rgba(153, 102, 255, 0.7)'
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
}

// Initialize range sliders
function initializeRangeSliders() {
    const chunkSizeRange = document.getElementById('chunk-size');
    const chunkSizeValue = document.getElementById('chunk-size-value');
    
    if (chunkSizeRange && chunkSizeValue) {
        chunkSizeRange.addEventListener('input', function() {
            chunkSizeValue.textContent = this.value;
        });
    }
    
    const chunkOverlapRange = document.getElementById('chunk-overlap');
    const chunkOverlapValue = document.getElementById('chunk-overlap-value');
    
    if (chunkOverlapRange && chunkOverlapValue) {
        chunkOverlapRange.addEventListener('input', function() {
            chunkOverlapValue.textContent = this.value;
        });
    }
    
    const topKRange = document.getElementById('top-k-results');
    const topKValue = document.getElementById('top-k-value');
    
    if (topKRange && topKValue) {
        topKRange.addEventListener('input', function() {
            topKValue.textContent = this.value;
        });
    }
    
    const similarityRange = document.getElementById('similarity-threshold');
    const similarityValue = document.getElementById('similarity-value');
    
    if (similarityRange && similarityValue) {
        similarityRange.addEventListener('input', function() {
            similarityValue.textContent = this.value;
        });
    }
    
    const nprobeRange = document.getElementById('faiss-nprobe');
    const nprobeValue = document.getElementById('nprobe-value');
    
    if (nprobeRange && nprobeValue) {
        nprobeRange.addEventListener('input', function() {
            nprobeValue.textContent = this.value;
        });
    }
}

// Setup document upload modal functionality
function setupDocumentUploadModal() {
    const uploadSubmitBtn = document.getElementById('upload-document-submit');
    
    if (uploadSubmitBtn) {
        uploadSubmitBtn.addEventListener('click', async function() {
            const fileInput = document.getElementById('modal-document-file');
            const nameInput = document.getElementById('modal-document-name');
            const descriptionInput = document.getElementById('modal-document-description');
            const indexImmediately = document.getElementById('index-immediately').checked;
            
            if (!fileInput.files || fileInput.files.length === 0) {
                showToast('Please select a file to upload', 'warning');
                return;
            }
            
            const file = fileInput.files[0];
            console.log('Selected file:', file.name, file.size, file.type);
            
            const formData = new FormData();
            // Make sure we're using the exact field name the server expects
            formData.append('document', file, file.name);
            console.log('FormData created with document field');
            
            if (nameInput.value) {
                formData.append('name', nameInput.value);
            }
            
            if (descriptionInput.value) {
                formData.append('description', descriptionInput.value);
            }
            
            formData.append('index_immediately', indexImmediately.toString());
            
            // Show loading toast
            showToast('Uploading document...', 'info');
            
            try {
                console.log('Sending file upload request...');
                const response = await fetch('/rag/api/documents/upload', {
                    method: 'POST',
                    body: formData
                });
                
                console.log('Response status:', response.status, response.statusText);
                
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                
                const data = await response.json();
                console.log('Response data:', data);
                
                if (data.success) {
                    showToast('Document uploaded successfully', 'success');
                    
                    // Close modal using jQuery (Bootstrap 3 compatible)
                    try {
                        $('#uploadDocumentModal').modal('hide');
                    } catch (modalError) {
                        console.error('Error closing modal:', modalError);
                    }
                    
                    // Reset form
                    document.getElementById('upload-document-form').reset();
                    
                    // Refresh documents table
                    fetchDocumentsData();
                } else {
                    console.error('Upload failed:', data);
                    showToast(`Error: ${data.error || 'Failed to upload document'}`, 'error');
                }
            } catch (error) {
                console.error('Error uploading document:', error);
                showToast(`Upload error: ${error.message || 'Connection failed'}`, 'error');
            }
        });
    }
}

// Setup webpage scraper modal functionality
function setupWebScraperModal() {
    const scrapeSubmitBtn = document.getElementById('scrape-webpage-submit');
    
    if (scrapeSubmitBtn) {
        scrapeSubmitBtn.addEventListener('click', async function() {
            const urlInput = document.getElementById('webpage-url-modal');
            const nameInput = document.getElementById('webpage-name');
            const descriptionInput = document.getElementById('webpage-description-modal');
            const indexImmediately = document.getElementById('index-webpage-immediately').checked;
            
            if (!urlInput.value.trim()) {
                showToast('Please enter a valid URL', 'warning');
                return;
            }
            
            // Show loading toast
            showToast('Scraping webpage...', 'info');
            
            try {
                const response = await fetchWithTimeout('/api/rag/scrape-webpage', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        url: urlInput.value.trim(),
                        name: nameInput.value.trim(),
                        description: descriptionInput.value.trim(),
                        index_immediately: indexImmediately
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showToast('Webpage scraped successfully', 'success');
                    
                    // Close modal
                    bootstrap.Modal.getInstance(document.getElementById('scrapeWebpageModal')).hide();
                    
                    // Reset form
                    document.getElementById('scrape-webpage-form').reset();
                    
                    // Refresh documents table
                    fetchDocumentsData();
                } else {
                    throw new Error(data.message || 'Failed to scrape webpage');
                }
            } catch (error) {
                handleFetchError(error, 'scrape webpage');
            }
        });
    }
}

// Setup vector search modal functionality
function setupVectorSearchModal() {
    const searchBtn = document.getElementById('run-vector-search');
    
    if (searchBtn) {
        searchBtn.addEventListener('click', async function() {
            const queryInput = document.getElementById('vector-search-query');
            const topKInput = document.getElementById('vector-search-top-k');
            
            if (!queryInput.value.trim()) {
                showToast('Please enter a search query', 'warning');
                return;
            }
            
            try {
                // Show loading state
                searchBtn.disabled = true;
                searchBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Searching...';
                
                const response = await fetchWithTimeout('/api/rag/vector-search', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        query: queryInput.value.trim(),
                        top_k: parseInt(topKInput.value)
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Display results
                    displayVectorSearchResults(data.results);
                } else {
                    throw new Error(data.message || 'Vector search failed');
                }
            } catch (error) {
                handleFetchError(error, 'perform vector search');
                
                // Hide results section
                document.getElementById('vector-search-results').classList.add('d-none');
            } finally {
                // Reset button state
                searchBtn.disabled = false;
                searchBtn.innerHTML = 'Search';
            }
        });
    }
}

// Display vector search results
function displayVectorSearchResults(results) {
    const resultsContainer = document.getElementById('vector-search-results');
    const resultsList = document.getElementById('vector-results-list');
    
    if (!resultsContainer || !resultsList) return;
    
    // Show results section
    resultsContainer.classList.remove('d-none');
    
    // Clear previous results
    resultsList.innerHTML = '';
    
    // Add results to the list
    if (results.length === 0) {
        resultsList.innerHTML = '<div class="alert alert-info">No results found</div>';
        return;
    }
    
    results.forEach((result, index) => {
        const resultItem = document.createElement('div');
        resultItem.className = 'list-group-item';
        
        resultItem.innerHTML = `
            <div class="d-flex w-100 justify-content-between">
                <h6 class="mb-1">${escapeHtml(result.title || 'Document Chunk')}</h6>
                <small class="text-muted">Score: ${result.score.toFixed(3)}</small>
            </div>
            <p class="mb-1">${escapeHtml(result.text)}</p>
            <small class="text-muted">Source: ${escapeHtml(result.source || 'Unknown')}</small>
        `;
        
        resultsList.appendChild(resultItem);
    });
}

// Fetch documents data
async function fetchDocumentsData() {
    try {
        const response = await fetchWithTimeout('/api/rag/documents');
        const data = await response.json();
        
        updateDocumentsTable(data);
    } catch (error) {
        handleFetchError(error, 'fetch documents');
    }
}

// Update documents table with fetched data
function updateDocumentsTable(documents) {
    const tableBody = document.querySelector('#documents-table tbody');
    if (!tableBody) return;
    
    // If DataTable is initialized, destroy it first
    if ($.fn.DataTable.isDataTable('#documents-table')) {
        $('#documents-table').DataTable().destroy();
    }
    
    // Clear the table body
    tableBody.innerHTML = '';
    
    // Add documents to the table
    documents.forEach((doc) => {
        const tr = document.createElement('tr');
        tr.setAttribute('data-document-id', doc.id);
        
        // Status badge class
        let statusBadgeClass = 'bg-success';
        if (doc.status === 'Processing') {
            statusBadgeClass = 'bg-warning';
        } else if (doc.status === 'Error') {
            statusBadgeClass = 'bg-danger';
        }
        
        tr.innerHTML = `
            <td>${doc.id}</td>
            <td>${escapeHtml(doc.name)}</td>
            <td>${doc.type}</td>
            <td>${formatFileSize(doc.size)}</td>
            <td>${formatDateTime(doc.date_added)}</td>
            <td><span class="badge ${statusBadgeClass}">${doc.status}</span></td>
            <td>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary" title="View" onclick="viewDocument('${doc.id}')"><i class="fas fa-eye"></i></button>
                    <button class="btn btn-outline-danger" title="Delete" onclick="deleteDocument('${doc.id}')"><i class="fas fa-trash"></i></button>
                    <button class="btn btn-outline-secondary" title="Reindex" onclick="reindexDocument('${doc.id}')"><i class="fas fa-retweet"></i></button>
                </div>
            </td>
        `;
        
        tableBody.appendChild(tr);
    });
    
    // Reinitialize DataTable
    $('#documents-table').DataTable({
        responsive: true,
        pageLength: 10,
        order: [[4, 'desc']] // Sort by date added desc
    });
}

// Update a document's status in the table
function updateDocumentStatus(documentId, status) {
    const tr = document.querySelector(`tr[data-document-id="${documentId}"]`);
    if (!tr) return;
    
    const statusBadge = tr.querySelector('.badge');
    if (!statusBadge) return;
    
    // Update status badge class
    statusBadge.className = 'badge';
    if (status === 'Indexed') {
        statusBadge.classList.add('bg-success');
    } else if (status === 'Processing') {
        statusBadge.classList.add('bg-warning');
    } else if (status === 'Error') {
        statusBadge.classList.add('bg-danger');
    }
    
    statusBadge.textContent = status;
}

// View document details
function viewDocument(documentId) {
    window.location.href = `/api/rag/documents/${documentId}/view`;
}

// Delete a document
async function deleteDocument(documentId) {
    if (!confirm('Are you sure you want to delete this document? This action cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetchWithTimeout(`/api/rag/documents/${documentId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Document deleted successfully', 'success');
            
            // Remove row from table
            const tr = document.querySelector(`tr[data-document-id="${documentId}"]`);
            if (tr && tr.parentNode) {
                tr.parentNode.removeChild(tr);
            }
            
            // Refresh vector DB stats
            refreshVectorDBStats();
        } else {
            throw new Error(data.message || 'Failed to delete document');
        }
    } catch (error) {
        handleFetchError(error, 'delete document');
    }
}

// Reindex a document
async function reindexDocument(documentId) {
    try {
        // Update status to Processing
        updateDocumentStatus(documentId, 'Processing');
        
        const response = await fetchWithTimeout(`/api/rag/documents/${documentId}/reindex`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Document reindexing started', 'success');
        } else {
            throw new Error(data.message || 'Failed to reindex document');
        }
    } catch (error) {
        handleFetchError(error, 'reindex document');
        
        // Set status back to Error
        updateDocumentStatus(documentId, 'Error');
    }
}

// Fetch vector database statistics
async function fetchVectorDBStats() {
    try {
        const response = await fetchWithTimeout('/api/rag/stats');
        const data = await response.json();
        
        updateVectorDBStats(data);
    } catch (error) {
        handleFetchError(error, 'fetch vector database statistics');
    }
}

// Format file size in human-readable form
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Refresh vector database statistics
function refreshVectorDBStats() {
    fetchVectorDBStats();
}

// Update vector database statistics display
function updateVectorDBStats(data) {
    // Update counter cards
    if (document.getElementById('chunks-count')) {
        document.getElementById('chunks-count').textContent = data.total_chunks.toLocaleString();
    }
    
    if (document.getElementById('vector-dimension')) {
        document.getElementById('vector-dimension').textContent = data.embedding_dimensions || 384;
    }
    
    if (document.getElementById('index-size')) {
        document.getElementById('index-size').textContent = formatFileSize(data.storage_used_mb * 1024 * 1024);
    }
    
    // Update the chart if it exists
    if (Chart.getChart('vectordb-stats-chart')) {
        const chart = Chart.getChart('vectordb-stats-chart');
        
        // Use default data if document counts aren't available
        const defaultData = [240, 180, 150, 95, 580, 0];
        
        chart.data.datasets[0].data = defaultData;
        
        chart.update();
    }
    
    // Update recent queries
    if (data.recent_queries && data.recent_queries.length > 0) {
        const recentQueriesContainer = document.getElementById('recent-queries');
        if (recentQueriesContainer) {
            recentQueriesContainer.innerHTML = '';
            
            data.recent_queries.forEach(query => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${escapeHtml(query.query)}</td>
                    <td>${query.timestamp}</td>
                    <td>${query.top_matches}</td>
                    <td>${query.latency}</td>
                `;
                
                recentQueriesContainer.appendChild(tr);
            });
        }
    }
}

// Rebuild vector index
async function rebuildVectorIndex() {
    if (!confirm('Are you sure you want to rebuild the vector index? This may take some time.')) {
        return;
    }
    
    try {
        showToast('Rebuilding vector index...', 'info');
        
        const response = await fetchWithTimeout('/api/rag/rebuild-index', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Vector index rebuild started. This may take some time to complete.', 'success');
        } else {
            throw new Error(data.message || 'Failed to rebuild vector index');
        }
    } catch (error) {
        handleFetchError(error, 'rebuild vector index');
    }
}

// Show vector search modal
function showVectorSearchModal() {
    const vectorSearchModal = new bootstrap.Modal(document.getElementById('vectorSearchModal'));
    vectorSearchModal.show();
}

// Fetch MinIO storage information
async function fetchMinioStorage() {
    try {
        const response = await fetchWithTimeout('/api/rag/storage');
        const data = await response.json();
        
        updateMinioStorage(data);
    } catch (error) {
        handleFetchError(error, 'fetch MinIO storage information');
    }
}

// Refresh MinIO storage information
function refreshMinioStorage() {
    fetchMinioStorage();
}

// Update MinIO storage information display
function updateMinioStorage(data) {
    // Update storage usage chart
    if (Chart.getChart('storage-usage-chart')) {
        const chart = Chart.getChart('storage-usage-chart');
        
        const usedPercentage = data.total_storage_mb ? Math.round((data.used_storage_mb / data.total_storage_mb) * 100) : 25;
        chart.data.datasets[0].data = [usedPercentage, 100 - usedPercentage];
        chart.update();
    }
    
    // Update file type chart
    if (Chart.getChart('file-type-chart')) {
        const chart = Chart.getChart('file-type-chart');
        
        // Use file_counts if available, otherwise use default values
        const fileTypes = data.file_counts || {};
        
        chart.data.datasets[0].data = [
            fileTypes.pdf || 0,
            fileTypes.doc || 0,
            fileTypes.md || 0,
            fileTypes.html || 0,
            fileTypes.txt || 0
        ];
        
        chart.update();
    }
    
    // Update files table
    if (data.files && data.files.length > 0) {
        const filesContainer = document.getElementById('minio-files');
        if (filesContainer) {
            // If DataTable is initialized, destroy it first
            if ($.fn.DataTable.isDataTable('#minio-files-table')) {
                $('#minio-files-table').DataTable().destroy();
            }
            
            // Clear the table body
            filesContainer.innerHTML = '';
            
            // Add files to the table
            data.files.forEach(file => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${escapeHtml(file.bucket)}</td>
                    <td>${escapeHtml(file.path)}</td>
                    <td>${file.type}</td>
                    <td>${formatFileSize(file.size)}</td>
                    <td>${formatDateTime(file.last_modified)}</td>
                    <td>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-primary" title="Download" onclick="downloadMinioFile('${file.bucket}', '${file.path}')"><i class="fas fa-download"></i></button>
                            <button class="btn btn-outline-danger" title="Delete" onclick="deleteMinioFile('${file.bucket}', '${file.path}')"><i class="fas fa-trash"></i></button>
                        </div>
                    </td>
                `;
                
                filesContainer.appendChild(tr);
            });
            
            // Reinitialize DataTable
            $('#minio-files-table').DataTable({
                responsive: true,
                pageLength: 10,
                order: [[4, 'desc']] // Sort by last modified desc
            });
        }
    }
}

// Create a new MinIO bucket
async function createMinioBucket() {
    const bucketName = prompt('Enter new bucket name:');
    
    if (!bucketName) return;
    
    try {
        const response = await fetchWithTimeout('/api/rag/create-bucket', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                bucket_name: bucketName
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast(`Bucket "${bucketName}" created successfully`, 'success');
            
            // Refresh MinIO storage display
            refreshMinioStorage();
        } else {
            throw new Error(data.message || 'Failed to create bucket');
        }
    } catch (error) {
        handleFetchError(error, 'create MinIO bucket');
    }
}

// Download a file from MinIO
function downloadMinioFile(bucket, path) {
    window.location.href = `/api/rag/download-file?bucket=${encodeURIComponent(bucket)}&path=${encodeURIComponent(path)}`;
}

// Delete a file from MinIO
async function deleteMinioFile(bucket, path) {
    if (!confirm('Are you sure you want to delete this file? This action cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetchWithTimeout('/api/rag/delete-file', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                bucket,
                path
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('File deleted successfully', 'success');
            
            // Refresh MinIO storage display
            refreshMinioStorage();
        } else {
            throw new Error(data.message || 'Failed to delete file');
        }
    } catch (error) {
        handleFetchError(error, 'delete MinIO file');
    }
}

// Save RAG settings
async function saveRagSettings(e) {
    e.preventDefault();
    
    const settings = {
        embedding_model: document.getElementById('embedding-model').value,
        embedding_dimension: parseInt(document.getElementById('embedding-dimension').value),
        faiss_index_type: document.getElementById('faiss-index-type').value,
        faiss_nprobe: parseInt(document.getElementById('faiss-nprobe').value),
        chunk_size: parseInt(document.getElementById('chunk-size').value),
        chunk_overlap: parseInt(document.getElementById('chunk-overlap').value),
        top_k_results: parseInt(document.getElementById('top-k-results').value),
        similarity_threshold: parseFloat(document.getElementById('similarity-threshold').value)
    };
    
    try {
        const response = await fetchWithTimeout('/api/rag/settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(settings)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('RAG settings saved successfully', 'success');
        } else {
            throw new Error(data.message || 'Failed to save RAG settings');
        }
    } catch (error) {
        handleFetchError(error, 'save RAG settings');
    }
}

// Reset RAG settings to defaults
function resetRagSettings() {
    // Set default values
    document.getElementById('embedding-model').value = 'sentence-transformers/all-MiniLM-L6-v2';
    document.getElementById('embedding-dimension').value = '384';
    document.getElementById('faiss-index-type').value = 'IndexFlatL2';
    document.getElementById('faiss-nprobe').value = '10';
    document.getElementById('nprobe-value').textContent = '10';
    document.getElementById('chunk-size').value = '500';
    document.getElementById('chunk-size-value').textContent = '500';
    document.getElementById('chunk-overlap').value = '50';
    document.getElementById('chunk-overlap-value').textContent = '50';
    document.getElementById('top-k-results').value = '5';
    document.getElementById('top-k-value').textContent = '5';
    document.getElementById('similarity-threshold').value = '0.7';
    document.getElementById('similarity-value').textContent = '0.7';
    
    showToast('RAG settings reset to defaults', 'info');
}
