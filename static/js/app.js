// Main Application JavaScript for AI Assistant Platform

// Removed Socket.IO initialization to resolve connection errors

// Dummy socket object to prevent errors in existing code
const socket = {
    on: function() {
        // Empty function to prevent errors
        return;
    },
    emit: function() {
        // Empty function to prevent errors
        return;
    }
};

// Global utility functions
function showToast(message, type = 'info') {
    // Create a bootstrap 3.4.1 compatible alert that will be shown at the top of the page
    
    // Create toast container if it doesn't exist
    if (!document.getElementById('toast-container')) {
        const toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'container';
        toastContainer.style.position = 'fixed';
        toastContainer.style.top = '10px';
        toastContainer.style.left = '50%';
        toastContainer.style.transform = 'translateX(-50%)';
        toastContainer.style.zIndex = '9999';
        toastContainer.style.width = '80%';
        toastContainer.style.maxWidth = '600px';
        document.body.appendChild(toastContainer);
    }
    
    const toastContainer = document.getElementById('toast-container');
    
    // Map to bootstrap 3 alert types
    const alertType = type === 'error' ? 'danger' : 
                     (type === 'success' ? 'success' : 
                     (type === 'warning' ? 'warning' : 'info'));
    
    // Create toast element
    const toastId = 'toast-' + Date.now();
    const toastHtml = `
        <div id="${toastId}" class="alert alert-${alertType} alert-dismissible fade in" role="alert">
            <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">&times;</span>
            </button>
            <strong>Notification</strong>: ${message}
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    // Automatically remove after 5 seconds
    setTimeout(() => {
        const toast = document.getElementById(toastId);
        if (toast) {
            // Fade out manually
            toast.style.opacity = '0';
            toast.style.transition = 'opacity 0.5s';
            
            // Remove after fade
            setTimeout(() => {
                if (toast && toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 500);
        }
    }, 5000);
}

// Update system status indicator
function updateSystemStatus(status) {
    const statusElement = document.getElementById('system-status');
    if (!statusElement) return;
    
    if (status.online) {
        statusElement.innerHTML = '<i class="fas fa-circle text-success"></i> System Online';
    } else {
        statusElement.innerHTML = '<i class="fas fa-circle text-danger"></i> System Offline';
    }
}

// Format date/time in a user-friendly way
function formatDateTime(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleString();
}

// Format file size in human-readable format
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Format API responses for display
function formatResponseText(text) {
    // Basic Markdown-like formatting
    
    // Code blocks
    text = text.replace(/```([\s\S]*?)```/g, '<pre class="bg-dark p-3 rounded"><code>$1</code></pre>');
    
    // Inline code
    text = text.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // Bold
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Italic
    text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // Line breaks
    text = text.replace(/\n/g, '<br>');
    
    return text;
}

// Initialize popovers and tooltips
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize all popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});

// Utility function to fetch data with error handling
async function fetchWithTimeout(resource, options = {}) {
    const { timeout = 8000 } = options;
    
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);
    
    try {
        const response = await fetch(resource, {
            ...options,
            signal: controller.signal
        });
        
        clearTimeout(id);
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        return response;
    } catch (error) {
        clearTimeout(id);
        if (error.name === 'AbortError') {
            throw new Error('Request timeout');
        }
        throw error;
    }
}

// Global error handler for fetch requests
window.handleFetchError = function(error, actionDescription) {
    console.error(`Error ${actionDescription}:`, error);
    showToast(`Failed to ${actionDescription}: ${error.message}`, 'danger');
};
