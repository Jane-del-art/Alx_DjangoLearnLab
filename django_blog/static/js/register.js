// static/js/register.js - Register page JavaScript
console.log('Register page JavaScript loaded');

document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            const password1 = document.getElementById('password1').value;
            const password2 = document.getElementById('password2').value;
            
            if (password1 !== password2) {
                e.preventDefault();
                alert('Passwords do not match!');
                return false;
            }
            
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating account...';
                submitBtn.disabled = true;
            }
        });
    }
});
