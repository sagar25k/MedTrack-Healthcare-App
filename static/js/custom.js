// static/js/custom.js - MedTrack

document.addEventListener("DOMContentLoaded", function () {
    // ==== Dark Mode Toggle ====
    const toggleDarkMode = document.getElementById("toggleDarkMode");

    // Apply stored mode on load
    if (localStorage.getItem("darkMode") === "enabled") {
        document.body.classList.add("dark-mode");
        if (toggleDarkMode) toggleDarkMode.textContent = "Light Mode";
    }

    // Toggle dark mode and save preference
    if (toggleDarkMode) {
        toggleDarkMode.addEventListener("click", () => {
            document.body.classList.toggle("dark-mode");
            localStorage.setItem("darkMode", document.body.classList.contains("dark-mode") ? "enabled" : "disabled");
            toggleDarkMode.textContent = document.body.classList.contains("dark-mode") ? "Light Mode" : "Dark Mode";
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

    // ==== Slider Interaction for How It Works ====
    const sliderTrack = document.querySelector('.slider-track');
    const slideCards = document.querySelectorAll('.slide-card');

    if (sliderTrack && slideCards.length > 0) {
        slideCards.forEach(card => {
            // Pause animation on focus or click
            card.addEventListener('focus', () => {
                sliderTrack.style.animationPlayState = 'paused';
            });
            card.addEventListener('click', () => {
                sliderTrack.style.animationPlayState = 'paused';
            });
            // Resume animation when focus or click leaves
            card.addEventListener('blur', () => {
                sliderTrack.style.animationPlayState = 'running';
            });
        });

        // Resume animation when mouse leaves the slider container
        const sliderContainer = document.querySelector('.slider-container');
        sliderContainer.addEventListener('mouseleave', () => {
            sliderTrack.style.animationPlayState = 'running';
        });
    }
});