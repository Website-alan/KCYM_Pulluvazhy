/**
 * KCYM Pulluvazhy - Client Side File Validation and Instant Preview
 */
document.addEventListener('DOMContentLoaded', function () {
    // Select all file inputs
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', function () {
            const file = this.files[0];
            if (!file) return;

            const allowedExtensions = /(\.jpg|\.jpeg|\.png|\.gif)$/i;
            const maxSize = 5 * 1024 * 1024; // 5MB limit
            const form = this.closest('form');
            const submitBtn = form ? form.querySelector('button[type="submit"]') : null;
            
            // Remove existing client-side errors
            const existingError = this.parentNode.querySelector('.js-upload-error');
            if (existingError) {
                existingError.remove();
            }
            this.classList.remove('is-invalid');
            if (submitBtn) submitBtn.disabled = false;

            // 1. Validate File Extension
            if (!allowedExtensions.exec(file.name)) {
                showError(this, 'Invalid file type. Only JPG, JPEG, PNG, and GIF posters/photos are allowed.');
                clearInput(this);
                if (submitBtn) submitBtn.disabled = true;
                return;
            }

            // 2. Validate File Size
            if (file.size > maxSize) {
                showError(this, 'File is too large. Maximum size allowed is 5MB.');
                clearInput(this);
                if (submitBtn) submitBtn.disabled = true;
                return;
            }

            // 3. Live Image Preview (for profile pictures or upload widgets)
            const profileCircle = form ? form.querySelector('.profile-circle img') : null;
            const profileCircleDiv = form ? form.querySelector('.profile-circle') : null;
            
            if (profileCircle || profileCircleDiv) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    if (profileCircle) {
                        profileCircle.src = e.target.result;
                    } else if (profileCircleDiv) {
                        // Replace initials text placeholder with preview image element
                        profileCircleDiv.innerHTML = `<img src="${e.target.result}" alt="Preview" style="width:100%; height:100%; object-fit:cover;">`;
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    });

    /**
     * Helper to show error labels using Bootstrap styles
     */
    function showError(inputElement, message) {
        inputElement.classList.add('is-invalid');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback js-upload-error d-block mt-1';
        errorDiv.innerText = message;
        inputElement.parentNode.appendChild(errorDiv);
    }

    /**
     * Helper to clear file inputs
     */
    function clearInput(inputElement) {
        inputElement.value = '';
    }
});
