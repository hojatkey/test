// JavaScript اصلی پایسیب

document.addEventListener("DOMContentLoaded", function() {
    // انیمیشن‌های ورودی
    const cards = document.querySelectorAll(".card");
    cards.forEach((card, index) => {
        card.style.opacity = "0";
        card.style.transform = "translateY(20px)";
        
        setTimeout(() => {
            card.style.transition = "all 0.5s ease";
            card.style.opacity = "1";
            card.style.transform = "translateY(0)";
        }, index * 100);
    });
    
    // مدیریت فرم‌ها
    const forms = document.querySelectorAll("form");
    forms.forEach(form => {
        form.addEventListener("submit", function(e) {
            const submitBtn = form.querySelector("button[type=\"submit\"]");
            if (submitBtn) {
                submitBtn.innerHTML = "<span class=\"loading\"></span> در حال پردازش...";
                submitBtn.disabled = true;
            }
        });
    });
    
    // مدیریت انتخاب فایل
    const fileInputs = document.querySelectorAll("input[type=\"file\"]");
    fileInputs.forEach(input => {
        input.addEventListener("change", function(e) {
            const file = e.target.files[0];
            if (file) {
                const preview = document.getElementById("file-preview");
                if (preview) {
                    preview.innerHTML = `
                        <div class="file-preview">
                            <i class="fas fa-file-upload fa-3x text-primary mb-3"></i>
                            <p class="mb-0">${file.name}</p>
                            <small class="text-muted">${formatFileSize(file.size)}</small>
                        </div>
                    `;
                }
            }
        });
    });
    
    // مدیریت مچینگ کارت‌ها
    const matchCards = document.querySelectorAll(".match-card");
    matchCards.forEach(card => {
        card.addEventListener("click", function() {
            // حذف انتخاب قبلی
            matchCards.forEach(c => c.classList.remove("selected"));
            
            // انتخاب کارت فعلی
            this.classList.add("selected");
            
            // نمایش جزئیات
            const studentId = this.dataset.studentId;
            if (studentId) {
                showStudentDetails(studentId);
            }
        });
    });
    
    // مدیریت فیلترها
    const filterInputs = document.querySelectorAll(".filter-input");
    filterInputs.forEach(input => {
        input.addEventListener("input", debounce(function() {
            filterResults();
        }, 300));
    });
    
    // مدیریت نوتیفیکیشن‌ها
    const notificationBell = document.querySelector(".notification-bell");
    if (notificationBell) {
        notificationBell.addEventListener("click", function() {
            markAllNotificationsAsRead();
        });
    }
    
    // مدیریت مدال‌ها
    const modals = document.querySelectorAll(".modal");
    modals.forEach(modal => {
        modal.addEventListener("show.bs.modal", function() {
            // انیمیشن ورود مدال
            this.querySelector(".modal-dialog").style.transform = "scale(0.8)";
            this.querySelector(".modal-dialog").style.transition = "transform 0.3s ease";
            
            setTimeout(() => {
                this.querySelector(".modal-dialog").style.transform = "scale(1)";
            }, 10);
        });
    });
    
    // مدیریت اسکرول نرم
    const smoothScrollLinks = document.querySelectorAll("a[href^=\"#\"]");
    smoothScrollLinks.forEach(link => {
        link.addEventListener("click", function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute("href"));
            if (target) {
                target.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });
            }
        });
    });
    
    // مدیریت تایپ کردن در جستجو
    const searchInputs = document.querySelectorAll(".search-input");
    searchInputs.forEach(input => {
        input.addEventListener("input", debounce(function() {
            performSearch(this.value);
        }, 500));
    });
    
    // مدیریت انتخاب چندگانه
    const checkboxes = document.querySelectorAll(".select-item");
    const selectAllCheckbox = document.querySelector(".select-all");
    
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener("change", function() {
            checkboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
            updateSelectionCount();
        });
    }
    
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener("change", function() {
            updateSelectionCount();
        });
    });
    
    // مدیریت آپلود فایل با پیش‌نمایش
    const dropZones = document.querySelectorAll(".drop-zone");
    dropZones.forEach(zone => {
        zone.addEventListener("dragover", function(e) {
            e.preventDefault();
            this.classList.add("drag-over");
        });
        
        zone.addEventListener("dragleave", function(e) {
            e.preventDefault();
            this.classList.remove("drag-over");
        });
        
        zone.addEventListener("drop", function(e) {
            e.preventDefault();
            this.classList.remove("drag-over");
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFileUpload(files[0]);
            }
        });
    });
});

// توابع کمکی

function formatFileSize(bytes) {
    if (bytes === 0) return "0 Bytes";
    
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
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

function showStudentDetails(studentId) {
    // نمایش جزئیات دانشجو در مدال یا صفحه جدید
    fetch(`/students/${studentId}/details/`)
        .then(response => response.json())
        .then(data => {
            // نمایش جزئیات
            console.log("Student details:", data);
        })
        .catch(error => {
            console.error("Error:", error);
        });
}

function filterResults() {
    const searchTerm = document.querySelector(".search-input")?.value.toLowerCase() || "";
    const filterType = document.querySelector(".filter-type")?.value || "";
    const filterStatus = document.querySelector(".filter-status")?.value || "";
    
    const items = document.querySelectorAll(".filterable-item");
    
    items.forEach(item => {
        const text = item.textContent.toLowerCase();
        const type = item.dataset.type || "";
        const status = item.dataset.status || "";
        
        const matchesSearch = text.includes(searchTerm);
        const matchesType = !filterType || type === filterType;
        const matchesStatus = !filterStatus || status === filterStatus;
        
        if (matchesSearch && matchesType && matchesStatus) {
            item.style.display = "block";
        } else {
            item.style.display = "none";
        }
    });
}

function performSearch(query) {
    if (query.length < 2) return;
    
    // نمایش انیمیشن بارگذاری
    const resultsContainer = document.querySelector(".search-results");
    if (resultsContainer) {
        resultsContainer.innerHTML = "<div class=\"text-center\"><div class=\"loading\"></div></div>";
    }
    
    // درخواست جستجو
    fetch(`/api/search/?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            displaySearchResults(data);
        })
        .catch(error => {
            console.error("Search error:", error);
        });
}

function displaySearchResults(results) {
    const container = document.querySelector(".search-results");
    if (!container) return;
    
    if (results.length === 0) {
        container.innerHTML = "<div class=\"text-center text-muted\">نتیجه‌ای یافت نشد</div>";
        return;
    }
    
    let html = "";
    results.forEach(result => {
        html += `
            <div class="card mb-3">
                <div class="card-body">
                    <h5 class="card-title">${result.title}</h5>
                    <p class="card-text">${result.description}</p>
                    <a href="${result.url}" class="btn btn-primary">مشاهده جزئیات</a>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

function markAllNotificationsAsRead() {
    fetch("/notifications/mark-all-read/", {
        method: "POST",
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "Content-Type": "application/json",
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // حذف نشان نوتیفیکیشن
            const badge = document.querySelector(".notification-badge");
            if (badge) {
                badge.style.display = "none";
            }
        }
    })
    .catch(error => {
        console.error("Error:", error);
    });
}

function updateSelectionCount() {
    const checkedItems = document.querySelectorAll(".select-item:checked");
    const count = checkedItems.length;
    
    const counter = document.querySelector(".selection-counter");
    if (counter) {
        counter.textContent = `${count} مورد انتخاب شده`;
    }
    
    const selectAllCheckbox = document.querySelector(".select-all");
    if (selectAllCheckbox) {
        const totalItems = document.querySelectorAll(".select-item").length;
        selectAllCheckbox.checked = count === totalItems;
        selectAllCheckbox.indeterminate = count > 0 && count < totalItems;
    }
}

function handleFileUpload(file) {
    const formData = new FormData();
    formData.append("file", file);
    
    // نمایش پیش‌نمایش فایل
    const preview = document.getElementById("file-preview");
    if (preview) {
        preview.innerHTML = `
            <div class="file-preview">
                <i class="fas fa-file-upload fa-3x text-primary mb-3"></i>
                <p class="mb-0">${file.name}</p>
                <small class="text-muted">${formatFileSize(file.size)}</small>
                <div class="progress mt-2">
                    <div class="progress-bar" role="progressbar" style="width: 0%"></div>
                </div>
            </div>
        `;
    }
    
    // آپلود فایل
    fetch("/api/upload/", {
        method: "POST",
        body: formData,
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // موفقیت
            console.log("File uploaded successfully");
        } else {
            // خطا
            console.error("Upload error:", data.error);
        }
    })
    .catch(error => {
        console.error("Upload error:", error);
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// توابع مچینگ
function selectCandidate(studentId, jobRequestId) {
    fetch("/matching/select-candidate/", {
        method: "POST",
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            student_id: studentId,
            job_request_id: jobRequestId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification("کاندیدا انتخاب شد!", "success");
        } else {
            showNotification("خطا در انتخاب کاندیدا", "error");
        }
    })
    .catch(error => {
        console.error("Error:", error);
        showNotification("خطا در انتخاب کاندیدا", "error");
    });
}

function showNotification(message, type = "info") {
    const alertClass = {
        "success": "alert-success",
        "error": "alert-danger",
        "warning": "alert-warning",
        "info": "alert-info"
    }[type] || "alert-info";
    
    const notification = document.createElement("div");
    notification.className = `alert ${alertClass} alert-dismissible fade show position-fixed`;
    notification.style.cssText = "top: 20px; right: 20px; z-index: 9999; min-width: 300px;";
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // حذف خودکار بعد از 5 ثانیه
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}
