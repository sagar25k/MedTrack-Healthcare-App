// Custom JS for MedTrack Project

// Example: Display a confirmation popup on appointment booking
document.addEventListener('DOMContentLoaded', () => {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            const button = form.querySelector('button[type=submit]');
            if (button && button.innerText.includes('Book Appointment')) {
                if (!confirm('Are you sure you want to book this appointment?')) {
                    e.preventDefault();
                }
            }
        });
    });
});
