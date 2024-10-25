document.addEventListener('DOMContentLoaded', function() {
    const slideInContainerPrueba = document.getElementById('slide-in-container-prueba');
    const closeBtnPrueba = slideInContainerPrueba.querySelector('.close-btn');
    const modal = document.getElementById("cabinModal");
    const span = document.getElementsByClassName("close")[0];

    closeBtnPrueba.addEventListener('click', function() {
        slideInContainerPrueba.classList.remove('slide-in-open');
    });

    window.mostrarCategoriaPrueba = function(event, categoria) {
        event.preventDefault();
        const elementos = document.querySelectorAll('.prueba-cabinas .elemento-cabina');
        const slideInBodyPrueba = document.getElementById('slide-in-body-prueba');
        slideInBodyPrueba.innerHTML = '';

        const slideInContentInner = document.createElement('div');
        slideInContentInner.className = 'slide-in-content-inner';

        elementos.forEach(function(elemento) {
            if (elemento.id === categoria) {
                const clonedElement = elemento.cloneNode(true);
                clonedElement.querySelectorAll('.btn-choice-room').forEach(button => {
                    button.addEventListener('click', function() {
                        const cruiseId = this.getAttribute('data-cruise-id');
                        const cardElement = this.closest('.elemento-cabina');
                        let availableCabins;
                        try {
                            const jsonDataElement = document.getElementById(`available-cabins-${cruiseId}`);
                            if (!jsonDataElement) {
                                throw new Error(`Element with ID available-cabins-${cruiseId} not found`);
                            }
                            const jsonData = jsonDataElement.textContent;
                            availableCabins = JSON.parse(jsonData);
                        } catch (e) {
                            console.error("Error parsing JSON: ", e);
                            return;
                        }

                        const cabinsList = document.getElementById("available-cabins-list");
                        cabinsList.innerHTML = '';

                        const uniqueCabins = Array.from(new Set(availableCabins.map(cabin => cabin.cabin_number)))
                            .map(cabin_number => {
                                return availableCabins.find(cabin => cabin.cabin_number === cabin_number);
                            });

                        const cabinsByDeck = {};
                        uniqueCabins.forEach(cabin => {
                            const deckNumber = getDeckNumber(cabin.cabin_number); // Cambiado a la nueva función
                            if (!cabinsByDeck[deckNumber]) {
                                cabinsByDeck[deckNumber] = [];
                            }
                            cabinsByDeck[deckNumber].push(cabin);
                        });

                        for (const [deck, cabins] of Object.entries(cabinsByDeck)) {
                            const deckContainer = document.createElement('div');
                            deckContainer.className = 'deck-container';
                            const deckTitle = document.createElement('h3');
                            deckTitle.innerText = `Deck ${deck}`;
                            deckContainer.appendChild(deckTitle);

                            cabins.forEach(cabin => {
                                const cabinButton = document.createElement('button');
                                cabinButton.className = 'cabin-button';
                                cabinButton.innerText = `Cabin ${cabin.cabin_number}`;
                                cabinButton.addEventListener('click', function() {
                                    cardElement.querySelector('.selected-cabin-number').innerText = cabin.cabin_number;

                                    const bookingButton = cardElement.querySelector('.btn-booking');
                                    const originalUrl = bookingButton.getAttribute('href');

                                    const updatedUrl = originalUrl.replace(/\/\d+\//, `/${cabin.cabin_number}/`);
                                    bookingButton.setAttribute('href', updatedUrl);

                                    modal.style.display = "none";
                                });
                                deckContainer.appendChild(cabinButton);
                            });

                            cabinsList.appendChild(deckContainer);
                        }

                        modal.style.display = "block";
                    });
                });
                slideInContentInner.appendChild(clonedElement);
            }
        });

        slideInBodyPrueba.appendChild(slideInContentInner);
        slideInContainerPrueba.classList.add('slide-in-open');
    };

    span.onclick = function() {
        modal.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }

    document.querySelectorAll('.btn-choice-room').forEach(button => {
        button.addEventListener('click', function() {
            const cruiseId = this.getAttribute('data-cruise-id');
            const cardElement = this.closest('.elemento-cabina');
            let availableCabins;
            try {
                const jsonDataElement = document.getElementById(`available-cabins-${cruiseId}`);
                if (!jsonDataElement) {
                    throw new Error(`Element with ID available-cabins-${cruiseId} not found`);
                }
                const jsonData = jsonDataElement.textContent;
                availableCabins = JSON.parse(jsonData);
            } catch (e) {
                console.error("Error parsing JSON: ", e);
                return;
            }

            const cabinsList = document.getElementById("available-cabins-list");
            cabinsList.innerHTML = '';

            const uniqueCabins = Array.from(new Set(availableCabins.map(cabin => cabin.cabin_number)))
                .map(cabin_number => {
                    return availableCabins.find(cabin => cabin.cabin_number === cabin_number);
                });

            const cabinsByDeck = {};
            uniqueCabins.forEach(cabin => {
                const deckNumber = getDeckNumber(cabin.cabin_number); // Cambiado a la nueva función
                if (!cabinsByDeck[deckNumber]) {
                    cabinsByDeck[deckNumber] = [];
                }
                cabinsByDeck[deckNumber].push(cabin);
            });

            for (const [deck, cabins] of Object.entries(cabinsByDeck)) {
                const deckContainer = document.createElement('div');
                deckContainer.className = 'deck-container';
                const deckTitle = document.createElement('h3');
                deckTitle.innerText = `Deck ${deck}`;
                deckContainer.appendChild(deckTitle);

                cabins.forEach(cabin => {
                    const cabinButton = document.createElement('button');
                    cabinButton.className = 'cabin-button';
                    cabinButton.innerText = `Cabin ${cabin.cabin_number}`;
                    cabinButton.addEventListener('click', function() {
                        cardElement.querySelector('.selected-cabin-number').innerText = cabin.cabin_number;

                        const bookingButton = cardElement.querySelector('.btn-booking');
                        const originalUrl = bookingButton.getAttribute('href');

                        const updatedUrl = originalUrl.replace(/\/\d+\//, `/${cabin.cabin_number}/`);
                        bookingButton.setAttribute('href', updatedUrl);

                        modal.style.display = "none";
                    });
                    deckContainer.appendChild(cabinButton);
                });

                cabinsList.appendChild(deckContainer);
            }

            modal.style.display = "block";
        });
    });

    function getDeckNumber(cabinNumber) {
        const cabinStr = cabinNumber.toString(); 
        let deckNumber;

        if (cabinStr.startsWith('G')) {
            return 'Guaranty'; 
        }
        
        if (cabinStr.length > 4) {
            deckNumber = cabinStr.substring(0, 2);
        } else {
            deckNumber = cabinStr.charAt(0);
        }

        return deckNumber;
    }
});
