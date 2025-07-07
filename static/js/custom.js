// static/js/custom.js - MedTrack

document.addEventListener("DOMContentLoaded", function () {
    // ==== Dark Mode Toggle ====
    const toggleDarkMode = document.getElementById("toggleDarkMode");

    // Apply stored mode on load
    if (localStorage.getItem("darkMode") === "enabled") {
        document.body.classList.add("dark-mode");
    }

    // Toggle dark mode and save preference
    if (toggleDarkMode) {
        toggleDarkMode.addEventListener("click", () => {
            document.body.classList.toggle("dark-mode");
            localStorage.setItem("darkMode", document.body.classList.contains("dark-mode") ? "enabled" : "disabled");
        });
    }

    // ==== Smooth Scroll to Anchors ====
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener("click", function (e) {
            const target = document.querySelector(this.getAttribute("href"));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: "smooth" });
            }
        });
    });

    // ==== Auto-dismiss Alerts after 5s ====
    document.querySelectorAll('.alert').forEach(alert => {
        setTimeout(() => {
            alert.classList.add('fade');
            setTimeout(() => alert.remove(), 500); // Wait for fade-out transition
        }, 5000);
    });

    // ==== Fade-in Animation for Elements with .fade-in ====
    document.querySelectorAll('.fade-in').forEach(el => {
        el.classList.add('appear');
    });

    // ==== Initialize AOS Animations ====
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 800,   // ms
            once: true,      // Animate once on scroll
            easing: 'ease-in-out'
        });
    }

    // ==== Accessibility: Focus outline handling for keyboard navigation ====
    document.body.addEventListener('keydown', function (e) {
        if (e.key === 'Tab') {
            document.body.classList.add('user-is-tabbing');
        }
    });

    document.body.addEventListener('mousedown', function () {
        document.body.classList.remove('user-is-tabbing');
    });
});