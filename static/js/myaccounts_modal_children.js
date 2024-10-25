
    function openModal() {
        document.getElementById("modal").style.display = "block";
        updatePlaceholder();
        document.getElementById("error-message").style.display = "none";
    }

    function closeModal() {
    const ninos = parseInt(document.getElementById('id_ninos').value) || 0;

    let valid = true;
    let ageValid = true;
    if (ninos > 0) {
        for (let i = 1; i <= ninos; i++) {
            const childAgeField = document.getElementById(`child${i}_age`);
            if (childAgeField && childAgeField.value === "") {
                valid = false;
                break;
            }
            if (childAgeField && parseInt(childAgeField.value) === 0) {
                ageValid = false;
            }
        }
    }

    if (!valid) {
        const errorMessage = "Please select the age of all children before closing.";
        document.getElementById("error-message").textContent = errorMessage;
        document.getElementById("error-message").style.display = "block";
    } else if (!ageValid) {
        const ageErrorMessage = "Children must be at least 1 year old.";
        document.getElementById("error-message").textContent = ageErrorMessage;
        document.getElementById("error-message").style.display = "block";
    } else {
        document.getElementById("modal").style.display = "none";
        updatePlaceholder();
        document.getElementById("error-message").style.display = "none";
    }
}

    function updateValue(fieldId, increment) {
        const input = document.getElementById(fieldId);
        let value = parseInt(input.value, 10);
        value = isNaN(value) ? 0 : value;
        value += increment;

        if (fieldId === 'id_adultos' && value < 0) {
            value = 0;
        }

        input.value = value;
        input.dispatchEvent(new Event('change'));
        validateFormFields();
        updatePlaceholder();
    }

    function updatePlaceholder() {
        const adultos = parseInt(document.getElementById('id_adultos').value) || 0;
        const ninos = parseInt(document.getElementById('id_ninos').value) || 0;

        const total = adultos + ninos;
        const placeholderText = `${total} Travelers, 1 Room`;
        document.getElementById('adults-children-input').placeholder = placeholderText;
    }

    window.onclick = function(event) {
        const modal = document.getElementById("modal");
        if (event.target === modal) {
            closeModal();
        }
    }
