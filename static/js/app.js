// Main application JavaScript for AI Assistant Platform

document.addEventListener('DOMContentLoaded', function() {
    console.log('AI Assistant Platform initialized');
    
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize Bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Settings modal functionality
    const settingsForm = document.getElementById('settingsForm');
    if (settingsForm) {
        const saveSettingsBtn = document.querySelector('#settingsModal .btn-primary');
        saveSettingsBtn.addEventListener('click', function() {
            // Get form values
            const modelSelection = document.getElementById('modelSelection').value;
            const streamingEnable = document.getElementById('streamingEnable').checked;
            
            // Save settings (using localStorage for demo purposes)
            const settings = {
                model: modelSelection,
                streaming: streamingEnable
            };
            
            localStorage.setItem('aiAssistantSettings', JSON.stringify(settings));
            
            // Show success message
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert alert-success mt-3';
            alertDiv.textContent = 'Settings saved successfully!';
            settingsForm.appendChild(alertDiv);
            
            // Remove alert after 3 seconds
            setTimeout(function() {
                alertDiv.remove();
            }, 3000);
        });
    }
    
    // Load saved settings (if any)
    const loadSavedSettings = function() {
        const savedSettings = localStorage.getItem('aiAssistantSettings');
        if (savedSettings) {
            const settings = JSON.parse(savedSettings);
            
            // Apply settings to form
            if (document.getElementById('modelSelection')) {
                document.getElementById('modelSelection').value = settings.model || 'local';
            }
            
            if (document.getElementById('streamingEnable')) {
                document.getElementById('streamingEnable').checked = settings.streaming !== undefined ? settings.streaming : true;
            }
        }
    };
    
    loadSavedSettings();
    
    // Global error handler for fetch requests
    window.handleFetchError = function(error, elementId) {
        console.error('Fetch error:', error);
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = `
                <div class="alert alert-danger">
                    <h4 class="alert-heading">Error</h4>
                    <p>An error occurred while fetching data: ${error.message}</p>
                    <hr>
                    <p class="mb-0">Please try again later or contact support if the problem persists.</p>
                </div>
            `;
        }
    };
    
    // Helper function to format timestamps
    window.formatTimestamp = function(timestamp) {
        if (!timestamp) return 'N/A';
        
        const date = new Date(timestamp);
        return date.toLocaleString();
    };
    
    // Helper function to truncate text
    window.truncateText = function(text, maxLength) {
        if (!text) return '';
        if (text.length <= maxLength) return text;
        
        return text.substring(0, maxLength) + '...';
    };
});