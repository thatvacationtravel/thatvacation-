function submitForm(buttonId) {
    document.getElementById(buttonId).click();
}

document.addEventListener("DOMContentLoaded", function() {
    const buttons = document.querySelectorAll('.interactive-button');

    if (sessionStorage.getItem('scrollPosition')) {
        window.scrollTo(0, parseInt(sessionStorage.getItem('scrollPosition'), 10));
        sessionStorage.removeItem('scrollPosition');
    }

    function setSelectedButton(button) {
        buttons.forEach(btn => {
            btn.classList.remove('selected');
            const selectedIcon = btn.querySelector('.selected-icon');
            if (selectedIcon) {
                selectedIcon.remove();
            }
            const spans = btn.querySelectorAll('span, i');
            spans.forEach(span => {
                span.style.removeProperty('color');
            });
        });

        button.classList.add('selected');
        let selectedIcon = button.querySelector('.selected-icon');
        if (!selectedIcon) {
            selectedIcon = document.createElement('i');
            selectedIcon.classList.add('selected-icon', 'fas', 'fa-check-circle');
            button.appendChild(selectedIcon);
        }

        const selectedContent = button.querySelectorAll('span, i');
        selectedContent.forEach(element => {
            element.style.setProperty('color', 'black', 'important');
        });
    }

    function updateSelection(button, param) {
        sessionStorage.setItem('scrollPosition', window.scrollY);

        setSelectedButton(button);
        const urlParams = new URLSearchParams(window.location.search);
        urlParams.set(param, 'true');
        const newUrl = window.location.pathname + '?' + urlParams.toString();
        console.log(`Navigating to URL: ${newUrl}`);
        history.pushState({ path: newUrl }, '', newUrl);
    }

    function restoreSelection() {
        const urlParams = new URLSearchParams(window.location.search);
        let button;
        if (urlParams.has('cruise_only')) {
            button = document.getElementById('btn_cruise_only');
        } else if (urlParams.has('drinks_and_obc_included')) {
            button = document.getElementById('btn_drinks_and_obc_included');
        } else if (urlParams.has('winter_sale')) {
            button = document.getElementById('btn_winter_sale');
        } else if (urlParams.has('cruise_with_drinks')) {
            button = document.getElementById('btn_cruise_with_drinks');
        } else if (urlParams.has('flash_sale_drinks')) {
            button = document.getElementById('btn_flash_sale_drinks');
        } else if (urlParams.has('flash_sale_cruise_only')) {
            button = document.getElementById('btn_flash_sale_cruise_only');
        } else {
            // Default to the button defined by fare_desc
            const fareDesc = document.getElementById('fareDescValue').textContent.trim();
            if (fareDesc === "ESCAPE TO SEA CRUISE ONLY") {
                button = document.getElementById('btn_cruise_only');
            } else if (fareDesc === "DRINKS AND OBC INCLUDED") {
                button = document.getElementById('btn_drinks_and_obc_included');
            } else if (fareDesc === "WINTER SALE") {
                button = document.getElementById('btn_winter_sale');
            } else if (fareDesc === "CRUISE WITH DRINKS INCLUDED") {
                button = document.getElementById('btn_cruise_with_drinks');
            } else if (fareDesc === "FLASH SALE DRINKS") {
                button = document.getElementById('btn_flash_sale_drinks');
            } else if (fareDesc === "FLASH SALE CRUISE ONLY") {
                button = document.getElementById('btn_flash_sale_cruise_only');
            }
        }
        if (button) {
            setSelectedButton(button);
        }
    }

    restoreSelection();

    window.addEventListener('popstate', function(event) {
        restoreSelection();
    });

    buttons.forEach(button => {
        button.addEventListener('click', function() {
            let param;
            if (button.id === 'btn_cruise_only') {
                param = 'cruise_only';
            } else if (button.id === 'btn_wifi_included') {
                param = 'wifi_included';
            } else if (button.id === 'btn_drinks_and_obc_included') {
                param = 'drinks_and_obc_included';
            } else if (button.id === 'btn_winter_sale') {
                param = 'winter_sale';
            } else if (button.id === 'btn_cruise_with_drinks') {
                param = 'cruise_with_drinks';
            } else if (button.id === 'btn_flash_sale_drinks') {
                param = 'flash_sale_drinks';
            } else if (button.id === 'btn_flash_sale_cruise_only') {
                param = 'flash_sale_cruise_only';
            }
            updateSelection(button, param);
        });
    });

    // Additional existing script logic
    const overlay = document.getElementById('overlay');

    document.querySelectorAll('form').forEach(function(form) {
        form.addEventListener('submit', function(event) {
            overlay.style.display = 'block';
        });
    });

    document.querySelectorAll('.interactive-button').forEach(button => {
        button.addEventListener('click', function() {
            overlay.style.display = 'block';
        });
    });

    // Ocultar el overlay si se navega hacia atrás en el historial
    window.addEventListener('popstate', function(event) {
        overlay.style.display = 'none';
    });

    // Manejar el evento pageshow para ocultar el overlay al navegar hacia atrás o adelante en el navegador
    window.addEventListener('pageshow', function(event) {
        if (event.persisted) {
            overlay.style.display = 'none';
        }
    });

    // Ensure the default button is selected when navigating away and back to the page
    window.addEventListener('beforeunload', function() {
        history.replaceState(null, '', window.location.pathname);
    });
});







