// Custom JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Example script to add interactivity
    const buttons = document.querySelectorAll('.btn-primary');
    buttons.forEach(button => {
        button.addEventListener('click', () => {
            alert('Button clicked!');
        });
    });
});