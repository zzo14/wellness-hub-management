document.addEventListener("DOMContentLoaded", function () {
    dropdown_image();
});

// Toggle password visibility
function toggle_password_visibility(password_id) {
    var passwordInput = document.getElementById(password_id);
    var isVisibility = passwordInput.type === 'text';
    passwordInput.type = isVisibility ? 'password' : 'text';
    var toggle_icon = passwordInput.nextElementSibling.querySelector('i');
    toggle_icon.className = isVisibility ? 'fa-regular fa-eye' : 'fa-regular fa-eye-slash';

    // Update aria-label or title for screen readers
    var actionText = isVisibility ? 'Show Password' : 'Hide Password';
    passwordInput.nextElementSibling.setAttribute('aria-label', actionText);
    passwordInput.nextElementSibling.setAttribute('title', actionText);
};

// change password input border color based on password complexity and enable/disable submit button
function validate_password(password_id, tooltip_id) {
    var passwordInput = document.getElementById(password_id);
    var tooltip = document.getElementById(tooltip_id)
    var submitButton = passwordInput.form.querySelector('button[type=submit]')
    var pattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^a-zA-Z\d]).{8,}$/;

    if (passwordInput.value === '') {
        passwordInput.style.borderColor = '';
        tooltip.style.display = 'none';
        submitButton.disabled = false;
    }
    else if (pattern.test(passwordInput.value)) {
        passwordInput.style.borderColor = 'green';
        tooltip.style.display = 'none';
        submitButton.disabled = false;
    } else {
        passwordInput.style.borderColor = 'red';
        tooltip.style.display = 'block';
        submitButton.disabled = true;
    }
}

// set max datepicker date to today
function max_date_today() {
    var today = new Date() // get today's date
    today.setFullYear(today.getFullYear() - 18); // subtract 18 years
    var max_date = today.toISOString().split('T')[0]; // format date
    document.getElementById('date_of_birth').max = max_date;
}


function dropdown_image() {
    var dropArea = document.getElementById('dropArea');
    var fileElem = document.getElementById('profile_image');
    var gallery = document.getElementById('gallery');

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false);
    });

    dropArea.addEventListener('drop', handleDrop, false);

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function highlight(e) {
        dropArea.classList.add('highlight');
    }

    function unhighlight(e) {
        dropArea.classList.remove('highlight');
    }

    function handleDrop(e) {
        let dt = e.dataTransfer;
        let files = dt.files;
        handleFiles(files);
    }

    dropArea.addEventListener('click', () => {
        fileElem.click();
    });

    fileElem.addEventListener('change', function (e) {
        handleFiles(this.files);
    });

    function handleFiles(files) {
        if (files.length > 0) {
            gallery.innerHTML = '';
            previewFile(files[0])
        }
    }

    function previewFile(file) {
        let reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onloadend = function (theFile) {
            var imgDiv = document.createElement('div');
            imgDiv.classList.add('d-flex', 'justify-content-center', 'align-items-center', 'my-2');
            var img = document.createElement('img');
            img.classList.add('img-thumbnail', 'rounded', 'border', 'shadow-sm');
            img.style.maxHeight = '200px';
            img.style.maxWidth = '200px';
            img.src = reader.result;
            img.alt = theFile.name;
            imgDiv.appendChild(img);
            gallery.appendChild(imgDiv);
        }
    }
}

document.querySelectorAll('.select-month-btn').forEach(button => {
    button.addEventListener('click', function() {
        const planId = this.getAttribute('data-plan-id');
        document.getElementById('selectedPlanId').value = planId;
    });
})