function updateValue(fieldId, increment) {
    const input = document.getElementById(fieldId);
    let value = parseInt(input.value, 10);
    value = isNaN(value) ? 0 : value;
    value += increment;
    if (value < 0) {
        value = 0;
    }
    input.value = value;
    input.dispatchEvent(new Event('change'));
    validateFormFields();
}

function validateFormFields() {
    const adultosField = document.getElementById('id_adultos');
    const ninosField = document.getElementById('id_ninos');
    const childrenContainer = document.getElementById('children-container');
    const incrementNinosButton = document.getElementById('increment-ninos');
    const decrementNinosButton = document.getElementById('decrement-ninos');
    const incrementAdultosButton = document.getElementById('increment-adultos');
    const decrementAdultosButton = document.getElementById('decrement-adultos');

    const adultos = parseInt(adultosField.value) || 0;
    const ninos = parseInt(ninosField.value) || 0;

    if (adultos === 1) {
        ninosField.max = 1;
        ninosField.disabled = false;
        childrenContainer.style.display = 'block';
    } else if (adultos === 2) {
        ninosField.max = 2;
        ninosField.disabled = false;
        childrenContainer.style.display = 'block';
    } else if (adultos === 3 || adultos === 4) {
        ninosField.value = 0;
        ninosField.max = 0;
        ninosField.disabled = true;
        childrenContainer.style.display = 'none';
    } else {
        ninosField.max = 0;
        ninosField.disabled = false;
        childrenContainer.style.display = 'block';
    }

    incrementNinosButton.disabled = (adultos === 1 && ninos >= 1) || (adultos === 2 && ninos >= 2);
    decrementNinosButton.disabled = (ninos <= 0);
    incrementAdultosButton.disabled = (adultos >= 4);
    decrementAdultosButton.disabled = (adultos <= 0);

    updateChildAgesVisibility();
}

function updateChildAgesVisibility() {
    const ninosField = document.getElementById('id_ninos');
    const childAges = document.getElementById('child-ages');
    const child1AgeField = document.getElementById('child1_age');
    const child2AgeContainer = document.getElementById('child2-age-container');
    const child2AgeField = document.getElementById('child2_age');

    const ninos = parseInt(ninosField.value) || 0;
    if (ninos > 0) {
        childAges.style.display = 'block';
        child1AgeField.required = true;
        if (ninos > 1) {
            child2AgeContainer.style.display = 'block';
            child2AgeField.required = true;
        } else {
            child2AgeContainer.style.display = 'none';
            child2AgeField.required = false;
            child2AgeField.value = '';
        }
    } else {
        childAges.style.display = 'none';
        child1AgeField.required = false;
        child1AgeField.value = '';
        child2AgeField.required = false;
        child2AgeField.value = '';
    }
}

function formatCruiseDates() {
    function formatDate(sailingDate, returnDate) {
        const sailing = new Date(sailingDate);
        let returning = new Date(returnDate);

        sailing.setDate(sailing.getDate() + 1);
        let sailingMonth = sailing.toLocaleString('default', { month: 'short' });
        let sailingDay = sailing.getDate();
        const maxDaysInMonth = {
            'Jan': 31, 'Feb': (sailing.getFullYear() % 4 === 0 && (sailing.getFullYear() % 100 !== 0 || sailing.getFullYear() % 400 === 0)) ? 29 : 28,
            'Mar': 31, 'Apr': 30, 'May': 31, 'Jun': 30,
            'Jul': 31, 'Aug': 31, 'Sep': 30, 'Oct': 31,
            'Nov': 30, 'Dec': 31
        };

        if (sailingDay > maxDaysInMonth[sailingMonth]) {
            sailing.setDate(1);
            sailing.setMonth(sailing.getMonth() + 1);
            sailingMonth = sailing.toLocaleString('default', { month: 'short' });
            sailingDay = sailing.getDate();
        }

        returning.setDate(returning.getDate() + 1);
        let returningMonth = returning.toLocaleString('default', { month: 'short' });
        let returningDay = returning.getDate();
        if (returningDay > maxDaysInMonth[returningMonth]) {
            returning.setDate(1);
            returning.setMonth(returning.getMonth() + 1);
            returningMonth = returning.toLocaleString('default', { month: 'short' });
            returningDay = returning.getDate();
        }

        const sailingYear = sailing.getFullYear();
        const returningYear = returning.getFullYear();

        if (sailingYear !== returningYear) {
            return `${sailingMonth} ${sailingDay} ${sailingYear} — ${returningMonth} ${returningDay} ${returningYear}`;
        } else {
            return `${sailingMonth} ${sailingDay} — ${returningMonth} ${returningDay} / ${sailingYear}`;
        }
    }

    const formattedTimes = document.querySelectorAll('.formatted-time');
    formattedTimes.forEach(function(element) {
        const departure = element.getAttribute('data-departure');
        const returning = element.getAttribute('data-return');

        if (departure && returning) {
            const formattedDate = formatDate(departure, returning);
            element.nextElementSibling.textContent = formattedDate;
        } else {
            console.error('Missing date attributes for element:', element);
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const adultosField = document.getElementById('id_adultos');
    const ninosField = document.getElementById('id_ninos');
    const incrementNinosButton = document.getElementById('increment-ninos');
    const decrementNinosButton = document.getElementById('decrement-ninos');
    const incrementAdultosButton = document.getElementById('increment-adultos');
    const decrementAdultosButton = document.getElementById('decrement-adultos');

    const loadingOverlay = document.getElementById('loading-overlay');
    const searchButton = document.querySelector('#search-button');

    function showOverlay() {
        loadingOverlay.style.display = 'flex';
    }

    function hideOverlay() {
        loadingOverlay.style.display = 'none';
    }

    adultosField.addEventListener('change', validateFormFields);
    ninosField.addEventListener('change', updateChildAgesVisibility);

    validateFormFields();
    updateChildAgesVisibility();

    const cruiseSearchForm = document.querySelector('#cruiseSearchForm1');
    const searchResultsCruceros = document.querySelector('#search-results-cruceros');
    const formErrorsContainer = document.querySelector('#form-errors');

    cruiseSearchForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const form = this;
        const url = form.getAttribute('action');

        const formData = new FormData(form);

        const dateRangeInput = document.getElementById('hidden-daterange');
        const dates = dateRangeInput.value.split(' - ');

        if (dates.length === 2) {
            formData.set('departure_date', dates[0].trim());
            formData.set('departure_end_date', dates[1].trim());
        } else {
            console.error('Please, Select Date range valid.');
        }


        if (!formData.has('ninos') || formData.get('ninos') === '') {
            formData.set('ninos', '0');
        }

        if (!formData.has('child1_age') || formData.get('child1_age') === '') {
            formData.set('child1_age', '0');
        }

        if (!formData.has('child2_age') || formData.get('child2_age') === '') {
            formData.set('child2_age', '0');
        }

        showOverlay();
        searchButton.textContent = 'Searching...';
        searchButton.classList.add('btn-clicked');

        fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(function(response) {
            if (!response.ok) {
                return response.text().then(text => {
                    console.error('Please select a valid date range and number of passengers to perform your cruise search.');
                    throw new Error('Please select a valid date range and number of passengers to perform your cruise search.');
                });
            }
            return response.json();
        })
        .then(function(data) {
            if (data.html && data.html.trim() !== '') {
                searchResultsCruceros.innerHTML = data.html;
                formErrorsContainer.style.display = 'none';
                formErrorsContainer.innerHTML = '';

                const shipElements = document.querySelectorAll('#search-results-cruceros > div > div > div.col-md-8 > div > div > h5');
                const shipNames = Array.from(shipElements).map(el => el.textContent.trim());

                const uniqueShipNames = [...new Set(shipNames)];

                const checkboxContainer = document.getElementById('ship-filter-container');

                if (checkboxContainer) {
                    checkboxContainer.innerHTML = '';

                    const hrElement = document.createElement('hr');
                    checkboxContainer.appendChild(hrElement);

                    const filterLink = document.createElement('a');
                    filterLink.href = "#";
                    filterLink.textContent = 'Filter By Name ▲';
                    filterLink.style.cursor = 'pointer';
                    filterLink.style.fontSize = '18px';
                    filterLink.style.borderColor = 'black';
                    checkboxContainer.appendChild(filterLink);

                    const filterContent = document.createElement('div');
                    filterContent.classList.add('filter-content');

                    if (window.innerWidth >= 769) {
                        filterContent.style.display = 'block';
                    } else {
                        filterContent.style.display = 'none';
                    }
                    checkboxContainer.appendChild(filterContent);

                    filterLink.onclick = function(e) {
                        e.preventDefault();
                        if (filterContent.style.display === 'none') {
                            filterContent.style.display = 'block';
                            filterLink.textContent = 'Filter By Name ▲';
                        } else {
                            filterContent.style.display = 'none';
                            filterLink.textContent = 'Filter By Name ▼';
                        }
                    };

                    uniqueShipNames.forEach(shipName => {
                        const checkbox = document.createElement('input');
                        checkbox.type = 'checkbox';
                        checkbox.value = shipName;
                        checkbox.id = `ship-${shipName}`;
                        checkbox.name = 'ship-filter';

                        const label = document.createElement('label');
                        label.htmlFor = `ship-${shipName}`;
                        label.textContent = shipName;

                        const div = document.createElement('div');
                        div.classList.add('form-check');
                        div.appendChild(checkbox);
                        div.appendChild(label);

                        filterContent.appendChild(div);

                        checkbox.addEventListener('change', filterResultsByShipName);
                    });

                } else {
                    console.error("El contenedor de los filtros de barcos (ship-filter-container) no existe.");
                }
            } else {
                searchResultsCruceros.innerHTML = `
                    <div class="card-body custom-card-body">
                        <h5>There are no cruise departures for this search.</h5>
                    </div>
                `;
                formErrorsContainer.style.display = 'none';
                formErrorsContainer.innerHTML = '';
            }

            formatCruiseDates();
        })



        .catch(function(error) {
            formErrorsContainer.innerHTML = error.message;
            formErrorsContainer.style.display = 'block';
            console.error('Error:', error);
        })
        .finally(() => {
            setTimeout(() => {
                hideOverlay();
                searchButton.textContent = 'Search';
                searchButton.classList.remove('btn-clicked');
                searchButton.blur();
            }, 200);
        });
    });

    function filterResultsByShipName() {
        const selectedShips = Array.from(document.querySelectorAll('input[name="ship-filter"]:checked')).map(checkbox => checkbox.value);

        const resultElements = document.querySelectorAll('#search-results-cruceros > div');
        resultElements.forEach(result => {
            const shipNameElement = result.querySelector('div.col-md-8 > div > div > h5');
            const shipName = shipNameElement ? shipNameElement.textContent.trim() : '';

            if (selectedShips.length === 0 || selectedShips.includes(shipName)) {

                result.classList.remove('hidden');
                result.style.display = 'block';
                setTimeout(() => {
                    result.style.opacity = '1';
                }, 600);
            } else {
                result.style.opacity = '.1';
                setTimeout(() => {
                    result.style.display = 'none';
                    result.classList.add('hidden');
                }, 800);
            }
        });
    }

    document.addEventListener('click', function(e) {
        const target = e.target.closest('.custom-card');

        if (target) {
            e.preventDefault();
            showOverlay();
        }
    });

    formatCruiseDates();

});