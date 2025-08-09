// Base JavaScript functionality

// Auto-dismiss messages after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
  const messages = document.querySelectorAll('.alert');
  messages.forEach(function(message) {
    setTimeout(function() {
      message.classList.remove('show');
      setTimeout(function() {
        message.remove();
      }, 150);
    }, 5000);
  });
});

// Handle manual message dismissal
document.addEventListener('click', function(e) {
  if (e.target.classList.contains('btn-close')) {
    const alert = e.target.closest('.alert');
    if (alert) {
      alert.classList.remove('show');
      setTimeout(function() {
        alert.remove();
      }, 150);
    }
  }
});
