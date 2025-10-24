// Main JavaScript for PYSIB Platform

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initNotifications();
    initFileUpload();
    initMatching();
    initForms();
    initAnimations();
});

// Notification System
function initNotifications() {
    // Mark notification as read when clicked
    document.querySelectorAll('.notification-item').forEach(item => {
        item.addEventListener('click', function() {
            const notificationId = this.dataset.notificationId;
            markNotificationAsRead(notificationId);
        });
    });

    // Real-time notification updates
    if (typeof(EventSource) !== "undefined") {
        const eventSource = new EventSource('/notifications/stream/');
        eventSource.onmessage = function(event) {
            const data = JSON.parse(event.data);
            showNotification(data);
            updateNotificationBadge();
        };
    }
}

function markNotificationAsRead(notificationId) {
    fetch(`/notifications/mark-read/${notificationId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateNotificationUI(notificationId);
        }
    })
    .catch(error => console.error('Error:', error));
}

function showNotification(data) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = 'alert alert-info alert-dismissible fade show position-fixed';
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        <i class="fas fa-bell me-2"></i>
        ${data.message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

function updateNotificationBadge() {
    fetch('/notifications/unread-count/')
        .then(response => response.json())
        .then(data => {
            const badge = document.querySelector('.notification-badge');
            if (badge) {
                badge.textContent = data.count;
                badge.style.display = data.count > 0 ? 'flex' : 'none';
            }
        });
}

// File Upload System
function initFileUpload() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                validateFile(file, this);
                showFilePreview(file, this);
            }
        });
    });

    // Drag and drop functionality
    const dropZones = document.querySelectorAll('.file-upload');
    dropZones.forEach(zone => {
        zone.addEventListener('dragover', handleDragOver);
        zone.addEventListener('dragleave', handleDragLeave);
        zone.addEventListener('drop', handleDrop);
    });
}

function validateFile(file, input) {
    const maxSize = 5 * 1024 * 1024; // 5MB
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf'];
    
    if (file.size > maxSize) {
        showAlert('حجم فایل نباید بیشتر از 5 مگابایت باشد', 'danger');
        input.value = '';
        return false;
    }
    
    if (!allowedTypes.includes(file.type)) {
        showAlert('فرمت فایل مجاز نیست. فقط JPG، PNG، GIF و PDF مجاز است', 'danger');
        input.value = '';
        return false;
    }
    
    return true;
}

function showFilePreview(file, input) {
    const preview = document.createElement('div');
    preview.className = 'file-preview mt-2';
    
    if (file.type.startsWith('image/')) {
        const img = document.createElement('img');
        img.src = URL.createObjectURL(file);
        img.className = 'img-thumbnail';
        img.style.maxWidth = '200px';
        preview.appendChild(img);
    } else {
        const icon = document.createElement('i');
        icon.className = 'fas fa-file-pdf text-danger fs-1';
        preview.appendChild(icon);
    }
    
    const fileName = document.createElement('p');
    fileName.textContent = file.name;
    fileName.className = 'small text-muted mt-2';
    preview.appendChild(fileName);
    
    input.parentNode.appendChild(preview);
}

function handleDragOver(e) {
    e.preventDefault();
    e.currentTarget.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    const input = e.currentTarget.querySelector('input[type="file"]');
    
    if (files.length > 0) {
        input.files = files;
        input.dispatchEvent(new Event('change'));
    }
}

// Matching System
function initMatching() {
    // Filter candidates
    const filterForm = document.querySelector('#candidate-filter');
    if (filterForm) {
        filterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            filterCandidates();
        });
    }

    // Select candidate
    document.querySelectorAll('.select-candidate-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const candidateId = this.dataset.candidateId;
            selectCandidate(candidateId);
        });
    });
}

function filterCandidates() {
    const formData = new FormData(document.querySelector('#candidate-filter'));
    const params = new URLSearchParams(formData);
    
    fetch(`/companies/matching/?${params}`)
        .then(response => response.text())
        .then(html => {
            document.querySelector('#candidates-container').innerHTML = html;
        });
}

function selectCandidate(candidateId) {
    if (confirm('آیا مطمئن هستید که می‌خواهید این کاندیدا را انتخاب کنید؟')) {
        fetch(`/companies/select-candidate/${candidateId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert('کاندیدا با موفقیت انتخاب شد!', 'success');
                location.reload();
            } else {
                showAlert('خطا در انتخاب کاندیدا: ' + data.message, 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('خطا در انتخاب کاندیدا', 'danger');
        });
    }
}

// Form Enhancements
function initForms() {
    // Auto-save forms
    const autoSaveForms = document.querySelectorAll('.auto-save');
    autoSaveForms.forEach(form => {
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('change', function() {
                autoSaveForm(form);
            });
        });
    });

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

function autoSaveForm(form) {
    const formData = new FormData(form);
    const url = form.dataset.saveUrl;
    
    if (url) {
        fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCSRFToken(),
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAutoSaveIndicator();
            }
        });
    }
}

function showAutoSaveIndicator() {
    const indicator = document.createElement('div');
    indicator.className = 'auto-save-indicator';
    indicator.innerHTML = '<i class="fas fa-check text-success me-1"></i>ذخیره شد';
    indicator.style.cssText = 'position: fixed; top: 20px; left: 20px; z-index: 9999; background: white; padding: 10px; border-radius: 5px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);';
    
    document.body.appendChild(indicator);
    
    setTimeout(() => {
        indicator.remove();
    }, 2000);
}

// Animations
function initAnimations() {
    // Fade in animation for cards
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
            }
        });
    });

    document.querySelectorAll('.card').forEach(card => {
        observer.observe(card);
    });

    // Counter animation for stats
    const counters = document.querySelectorAll('.counter');
    counters.forEach(counter => {
        const target = parseInt(counter.dataset.target);
        const duration = 2000;
        const increment = target / (duration / 16);
        let current = 0;
        
        const timer = setInterval(() => {
            current += increment;
            counter.textContent = Math.floor(current);
            
            if (current >= target) {
                counter.textContent = target;
                clearInterval(timer);
            }
        }, 16);
    });
}

// Utility Functions
function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

function showAlert(message, type = 'info') {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alert.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alert);
    
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('fa-IR');
}

// Test System
function startTest(testId) {
    if (confirm('آیا آماده شروع آزمون هستید؟')) {
        window.location.href = `/students/take-test/${testId}/`;
    }
}

function submitTestAnswer(questionId, answer) {
    fetch('/students/submit-answer/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            question_id: questionId,
            answer: answer
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateProgress(data.progress);
        }
    });
}

function updateProgress(progress) {
    const progressBar = document.querySelector('.test-progress .progress-bar');
    if (progressBar) {
        progressBar.style.width = progress + '%';
        progressBar.textContent = progress + '%';
    }
}

// Profile Completion
function calculateProfileCompletion() {
    const fields = document.querySelectorAll('.profile-field');
    let completed = 0;
    
    fields.forEach(field => {
        if (field.value.trim() !== '') {
            completed++;
        }
    });
    
    const percentage = Math.round((completed / fields.length) * 100);
    const progressBar = document.querySelector('.profile-completion .progress-bar');
    
    if (progressBar) {
        progressBar.style.width = percentage + '%';
        progressBar.textContent = percentage + '%';
    }
    
    return percentage;
}

// Search and Filter
function initSearch() {
    const searchInput = document.querySelector('#search-input');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(performSearch, 300));
    }
}

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

function performSearch() {
    const query = document.querySelector('#search-input').value;
    const url = new URL(window.location);
    url.searchParams.set('search', query);
    
    fetch(url)
        .then(response => response.text())
        .then(html => {
            document.querySelector('#search-results').innerHTML = html;
        });
}

// Export functions for global use
window.PYSIB = {
    showAlert,
    formatNumber,
    formatDate,
    startTest,
    selectCandidate,
    calculateProfileCompletion
};
