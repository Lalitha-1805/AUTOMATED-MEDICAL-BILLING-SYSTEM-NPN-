// Medical Billing Validation System - JavaScript

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    // Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Form validation for bill validation form
const validationForm = document.getElementById('validationForm');
if (validationForm) {
    validationForm.addEventListener('submit', function(e) {
        // Client-side validation
        const patientId = document.getElementById('patient_id').value;
        const diagnosis = document.getElementById('diagnosis').value;
        const procedure = document.getElementById('procedure').value;
        const cost = parseFloat(document.getElementById('cost').value);
        
        if (!patientId || !diagnosis || !procedure || isNaN(cost) || cost <= 0) {
            e.preventDefault();
            alert('Please fill in all required fields with valid values');
            return false;
        }
    });
}

// Load statistics
function loadStatistics() {
    fetch('/api/statistics')
        .then(response => response.json())
        .then(data => {
            // Update stats elements if they exist
            const statsElements = document.querySelectorAll('[data-stat]');
            statsElements.forEach(el => {
                const statKey = el.dataset.stat;
                if (data[statKey] !== undefined) {
                    el.textContent = data[statKey].toFixed(1);
                }
            });
        })
        .catch(error => console.log('Statistics not available:', error));
}

// Load and display claims
async function loadClaims(page = 1) {
    try {
        const response = await fetch(`/api/claims?page=${page}`);
        const data = await response.json();
        
        const tbody = document.getElementById('claimsBody');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        if (data.claims.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">No claims found</td></tr>';
            return;
        }
        
        data.claims.forEach(claim => {
            const statusClass = claim.status === 'Approved' ? 'success' : 
                               claim.status === 'Rejected' ? 'danger' : 'warning';
            const fraudClass = claim.fraud_probability > 0.7 ? 'danger' : 
                              claim.fraud_probability > 0.4 ? 'warning' : 'success';
            
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><code>${claim.claim_id}</code></td>
                <td>${claim.patient_id}</td>
                <td>${claim.diagnosis}</td>
                <td>$${claim.cost.toFixed(2)}</td>
                <td><span class="badge bg-${statusClass}">${claim.status}</span></td>
                <td><span class="badge bg-${fraudClass}">${(claim.fraud_probability * 100).toFixed(1)}%</span></td>
                <td>${claim.date}</td>
            `;
            tbody.appendChild(row);
        });
        
        // Update pagination
        updatePagination(data.pages, page);
        
    } catch (error) {
        console.error('Error loading claims:', error);
    }
}

// Update pagination
function updatePagination(pages, currentPage) {
    const pagination = document.getElementById('pagination');
    if (!pagination) return;
    
    pagination.innerHTML = '';
    
    if (currentPage > 1) {
        const prevBtn = document.createElement('li');
        prevBtn.className = 'page-item';
        prevBtn.innerHTML = `<a class="page-link" href="#" onclick="loadClaims(${currentPage - 1}); return false;">Previous</a>`;
        pagination.appendChild(prevBtn);
    }
    
    for (let i = 1; i <= pages; i++) {
        const pageItem = document.createElement('li');
        pageItem.className = `page-item ${i === currentPage ? 'active' : ''}`;
        pageItem.innerHTML = `<a class="page-link" href="#" onclick="loadClaims(${i}); return false;">${i}</a>`;
        pagination.appendChild(pageItem);
    }
    
    if (currentPage < pages) {
        const nextBtn = document.createElement('li');
        nextBtn.className = 'page-item';
        nextBtn.innerHTML = `<a class="page-link" href="#" onclick="loadClaims(${currentPage + 1}); return false;">Next</a>`;
        pagination.appendChild(nextBtn);
    }
}

// Format currency
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(value);
}

// Format date
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

// Create toast notification
function showToast(message, type = 'info') {
    const toastHtml = `
        <div class="toast align-items-center text-white bg-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'info'}" 
             role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.style.position = 'fixed';
        container.style.top = '20px';
        container.style.right = '20px';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
    
    const toastElement = document.createElement('div');
    toastElement.innerHTML = toastHtml;
    document.getElementById('toastContainer').appendChild(toastElement);
    
    const toast = new bootstrap.Toast(toastElement.querySelector('.toast'));
    toast.show();
}

// Validate form inputs
function validateForm(formElement) {
    let isValid = true;
    const inputs = formElement.querySelectorAll('input[required], select[required], textarea[required]');
    
    inputs.forEach(input => {
        if (!input.value || (input.type === 'number' && parseFloat(input.value) <= 0)) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Export data to CSV
function exportToCSV(data, filename = 'export.csv') {
    const csv = convertToCSV(data);
    const link = document.createElement('a');
    link.href = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv);
    link.download = filename;
    link.click();
}

// Convert array of objects to CSV
function convertToCSV(data) {
    if (!data || data.length === 0) return '';
    
    const headers = Object.keys(data[0]);
    const csv = [headers.join(',')];
    
    data.forEach(row => {
        const values = headers.map(header => {
            const value = row[header];
            return typeof value === 'string' && value.includes(',') ? `"${value}"` : value;
        });
        csv.push(values.join(','));
    });
    
    return csv.join('\n');
}

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// API helper
const api = {
    async get(url) {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return await response.json();
    },
    
    async post(url, data) {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return await response.json();
    }
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadStatistics();
    
    // Refresh statistics every 30 seconds
    setInterval(loadStatistics, 30000);
    
    // Initialize PDF upload handler
    initializePDFUpload();
});

// ============================================================================
// PDF BILL UPLOAD FUNCTIONALITY
// ============================================================================

function initializePDFUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const billFileInput = document.getElementById('billFileInput');
    const extractedForm = document.getElementById('extractedForm');
    
    if (!uploadArea || !billFileInput) return;
    
    // Click to upload
    uploadArea.addEventListener('click', function() {
        billFileInput.click();
    });
    
    // Drag and drop
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadArea.style.borderColor = '#0d6efd';
        uploadArea.style.backgroundColor = '#e7f1ff';
    });
    
    uploadArea.addEventListener('dragleave', function() {
        uploadArea.style.borderColor = '#dee2e6';
        uploadArea.style.backgroundColor = '#f8f9fa';
    });
    
    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadArea.style.borderColor = '#dee2e6';
        uploadArea.style.backgroundColor = '#f8f9fa';
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            billFileInput.files = files;
            handleFileUpload(files[0]);
        }
    });
    
    // File input change
    billFileInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });
    
    // Handle extracted form submission
    if (extractedForm) {
        extractedForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Validate extracted form
            if (!validateForm(extractedForm)) {
                showToast('Please fill in all required fields', 'error');
                return;
            }
            
            // Submit the form
            extractedForm.submit();
        });
    }
}

function handleFileUpload(file) {
    // Validate file
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        showToast('Only PDF files are allowed', 'error');
        return;
    }
    
    if (file.size > 16 * 1024 * 1024) {
        showToast('File size exceeds 16MB limit', 'error');
        return;
    }
    
    // Show loading state
    const uploadArea = document.getElementById('uploadArea');
    const uploadLoading = document.getElementById('uploadLoading');
    const uploadStatus = document.getElementById('uploadStatus');
    
    uploadArea.style.display = 'none';
    uploadLoading.style.display = 'block';
    uploadStatus.innerHTML = '';
    
    // Create form data
    const formData = new FormData();
    formData.append('bill_file', file);
    
    // Upload file
    fetch('/api/upload-bill', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        uploadLoading.style.display = 'none';
        
        if (!data.success) {
            uploadArea.style.display = 'block';
            const errorHtml = `
                <div class="alert alert-danger alert-dismissible fade show" role="alert">
                    <i class="bi bi-exclamation-circle"></i> <strong>Upload Failed:</strong> ${data.error}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `;
            uploadStatus.innerHTML = errorHtml;
            showToast('Failed to extract PDF: ' + data.error, 'error');
            return;
        }
        
        // Success - fill form with extracted data
        const fields = data.extracted_fields;
        const extractedForm = document.getElementById('extractedForm');
        
        if (extractedForm) {
            // Fill in fields
            if (fields.patient_id) document.getElementById('ex_patient_id').value = fields.patient_id;
            if (fields.age) document.getElementById('ex_age').value = fields.age;
            if (fields.gender) document.getElementById('ex_gender').value = fields.gender;
            if (fields.diagnosis_code) document.getElementById('ex_diagnosis').value = fields.diagnosis_code;
            if (fields.procedure_code) document.getElementById('ex_procedure').value = fields.procedure_code;
            if (fields.treatment_cost) document.getElementById('ex_cost').value = fields.treatment_cost.toFixed(2);
            if (fields.insurance_coverage_limit) document.getElementById('ex_coverage_limit').value = fields.insurance_coverage_limit.toFixed(2);
            if (fields.hospital_id) document.getElementById('ex_hospital_id').value = fields.hospital_id || 'H0001';
            
            // Show success message
            const successHtml = `
                <div class="alert alert-success alert-dismissible fade show" role="alert">
                    <i class="bi bi-check-circle"></i> <strong>Success!</strong> ${data.message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `;
            uploadStatus.innerHTML = successHtml;
            
            // Show extracted form
            extractedForm.style.display = 'block';
            
            // Scroll to form
            setTimeout(() => {
                extractedForm.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 300);
        }
    })
    .catch(error => {
        uploadLoading.style.display = 'none';
        uploadArea.style.display = 'block';
        
        const errorHtml = `
            <div class="alert alert-danger alert-dismissible fade show" role="alert">
                <i class="bi bi-exclamation-circle"></i> <strong>Error:</strong> ${error.message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        uploadStatus.innerHTML = errorHtml;
        
        showToast('Error uploading file: ' + error.message, 'error');
    });
}

function resetUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const uploadLoading = document.getElementById('uploadLoading');
    const uploadStatus = document.getElementById('uploadStatus');
    const extractedForm = document.getElementById('extractedForm');
    const billFileInput = document.getElementById('billFileInput');
    
    // Reset states
    uploadArea.style.display = 'block';
    uploadLoading.style.display = 'none';
    uploadStatus.innerHTML = '';
    if (extractedForm) extractedForm.style.display = 'none';
    if (billFileInput) billFileInput.value = '';
    
    // Reset form fields
    if (extractedForm) {
        extractedForm.reset();
    }
}

// ============================================================================
// REAL-TIME DASHBOARD CHARTS
// ============================================================================

let statusChartInstance = null;
let distributionChartInstance = null;

function initializeDashboardCharts() {
    // Check if charts are needed (only on dashboard)
    const statusChartCanvas = document.getElementById('statusChart');
    const distributionChartCanvas = document.getElementById('distributionChart');
    
    if (!statusChartCanvas || !distributionChartCanvas) return;
    
    // Load initial statistics and render charts
    loadAndRenderCharts();
    
    // Refresh charts every 5 seconds
    setInterval(loadAndRenderCharts, 5000);
}

function loadAndRenderCharts() {
    fetch('/api/statistics')
        .then(response => response.json())
        .then(data => {
            renderStatusChart(data);
            renderDistributionChart(data);
        })
        .catch(error => console.error('Error loading statistics:', error));
}

function renderStatusChart(data) {
    const ctx = document.getElementById('statusChart');
    if (!ctx) return;
    
    const chartData = {
        labels: ['Approved', 'Rejected', 'Manual Review'],
        datasets: [{
            label: 'Claims by Status',
            data: [data.approved, data.rejected, data.manual_review],
            backgroundColor: [
                '#28a745', // green
                '#dc3545', // red
                '#ffc107'  // yellow
            ],
            borderColor: [
                '#1e7e34',
                '#bd2130',
                '#e0a800'
            ],
            borderWidth: 2,
            tension: 0.4
        }]
    };
    
    if (statusChartInstance) {
        statusChartInstance.data = chartData;
        statusChartInstance.update();
    } else {
        statusChartInstance = new Chart(ctx, {
            type: 'line',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'bottom'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    }
}

function renderDistributionChart(data) {
    const ctx = document.getElementById('distributionChart');
    if (!ctx) return;
    
    const total = data.total || 1;
    const approvalRate = data.approval_rate || 0;
    const rejectionRate = ((data.rejected / total) * 100) || 0;
    const manualRate = ((data.manual_review / total) * 100) || 0;
    
    const chartData = {
        labels: [
            `Approved\n${data.approved}`,
            `Rejected\n${data.rejected}`,
            `Manual Review\n${data.manual_review}`
        ],
        datasets: [{
            data: [approvalRate, rejectionRate, manualRate],
            backgroundColor: [
                '#28a745',
                '#dc3545',
                '#ffc107'
            ],
            borderColor: [
                '#1e7e34',
                '#bd2130',
                '#e0a800'
            ],
            borderWidth: 2
        }]
    };
    
    if (distributionChartInstance) {
        distributionChartInstance.data = chartData;
        distributionChartInstance.update();
    } else {
        distributionChartInstance = new Chart(ctx, {
            type: 'doughnut',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.label + ': ' + context.parsed + '%';
                            }
                        }
                    }
                }
            }
        });
    }
}

// Initialize charts when page loads
document.addEventListener('DOMContentLoaded', initializeDashboardCharts);

