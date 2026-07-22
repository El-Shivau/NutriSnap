/**
 * NutriSnap – Global JavaScript
 * ================================
 * Shared JS utilities used across all pages.
 * Page-specific logic is kept in separate inline scripts or
 * additional JS files per template.
 *
 * Current responsibilities:
 *  - Auto-dismiss flash messages after a timeout.
 *  - Add 'fade-in-up' animation to main content on page load.
 *  - Upload zone drag-and-drop styling.
 */

"use strict";

// ============================================================
// Auto-dismiss Flash Messages
// ============================================================

/**
 * Automatically dismiss Bootstrap alert messages after a delay.
 * @param {number} delayMs - Milliseconds before dismissal (default: 5000)
 */
function autoDismissAlerts(delayMs = 5000) {
    const alertContainer = document.getElementById("flash-messages");
    if (!alertContainer) return;

    const alerts = alertContainer.querySelectorAll(".alert");
    alerts.forEach((alert) => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, delayMs);
    });
}

// ============================================================
// Page Load Animation
// ============================================================

/**
 * Add fade-in animation to the main content area on page load.
 */
function initPageAnimation() {
    const main = document.querySelector("main");
    if (main) {
        main.classList.add("fade-in-up");
    }
}

// ============================================================
// Upload Zone — Drag and Drop
// ============================================================

/**
 * Enhance the upload zone with drag-and-drop visual feedback.
 * The actual file input is still used for the form submission.
 */
function initUploadZone() {
    const zone = document.getElementById("upload-zone");
    if (!zone) return;

    const fileInput = document.getElementById("food-image-input");

    // Open file picker when clicking the zone
    zone.addEventListener("click", () => {
        if (fileInput) fileInput.click();
    });

    // Prevent default browser drag behaviours
    ["dragenter", "dragover", "dragleave", "drop"].forEach((event) => {
        zone.addEventListener(event, (e) => e.preventDefault());
    });

    // Visual feedback on drag enter/over
    zone.addEventListener("dragenter", () => zone.classList.add("drag-over"));
    zone.addEventListener("dragover", () => zone.classList.add("drag-over"));

    // Remove visual feedback on drag leave/drop
    zone.addEventListener("dragleave", () => zone.classList.remove("drag-over"));
    zone.addEventListener("drop", (e) => {
        zone.classList.remove("drag-over");
        const files = e.dataTransfer?.files;
        if (files && files.length > 0 && fileInput) {
            // Assign dropped files to the hidden file input
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(files[0]);
            fileInput.files = dataTransfer.files;

            // Show selected filename
            showSelectedFileName(files[0].name);
        }
    });

    // Show filename when selected via the file picker
    if (fileInput) {
        fileInput.addEventListener("change", () => {
            if (fileInput.files.length > 0) {
                showSelectedFileName(fileInput.files[0].name);
            }
        });
    }
}

/**
 * Update the upload zone text to show the selected file name.
 * @param {string} filename
 */
function showSelectedFileName(filename) {
    const label = document.getElementById("upload-zone-label");
    if (label) {
        label.textContent = `Selected: ${filename}`;
    }
}

// ============================================================
// Initialise on DOM Ready
// ============================================================
document.addEventListener("DOMContentLoaded", () => {
    autoDismissAlerts(5000);
    initPageAnimation();
    initUploadZone();
});
