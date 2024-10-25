document.addEventListener("DOMContentLoaded", function() {
    const buttons = document.querySelectorAll('.hidden-submit');

    // Función para manejar la solicitud AJAX y actualizar la página sin recargar
    function updateSelection(param) {
        const url = window.location.pathname;  // Mantener la misma URL

        console.log(`Iniciando solicitud AJAX con el parámetro: ${param}`);

        // Realizar la solicitud AJAX
        fetch(url + `?${param}=true`, {  // Enviamos el parámetro seleccionado en la URL
            method: 'GET',  // La solicitud es de tipo GET
            headers: {
                'X-Requested-With': 'XMLHttpRequest',  // Esto indica que es una solicitud AJAX
            }
        })
        .then(response => {
            console.log('Respuesta recibida del servidor:', response);
            if (!response.ok) {
                throw new Error('Error en la solicitud');
            }
            return response.json();  // Esperamos una respuesta en formato JSON
        })
        .then(data => {
            // Mostrar en consola la respuesta completa del servidor
            console.log("Respuesta completa de la solicitud AJAX:", data);

            // Actualizar la descripción de la tarifa seleccionada
            if (data.fare_desc) {
                document.getElementById('selected_fare_text').textContent = data.fare_desc;
            }

            // Actualizar precios por categoría
            if (data.fare_prices) {
                Object.keys(data.fare_prices).forEach(fareKey => {
                    const farePriceElement = document.getElementById(fareKey + '_price');
                    if (farePriceElement) {
                        farePriceElement.textContent = `$${data.fare_prices[fareKey]}`;
                    }
                });
            }

            // Si necesitas actualizar cabinas:
            // const cabinContainer = document.getElementById('cabin-container');
            // if (data.cabinas) {
            //     cabinContainer.innerHTML = '';  // Limpiar el contenido actual
            //     data.cabinas.forEach(cabin => {
            //         const cabinElement = document.createElement('div');
            //         cabinElement.textContent = `Cabina: ${cabin.cabin_number} - ${cabin.category_desc}`;
            //         cabinContainer.appendChild(cabinElement);
            //     });
            // }
        })
        .catch(error => console.error('Error en la solicitud AJAX:', error));
    }

    // Asignar eventos a cada botón
    buttons.forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();  // Prevenir el comportamiento predeterminado del botón
            const param = button.getAttribute('data-param');  // Obtener el parámetro correspondiente
            console.log(`Botón clicado: ${button.id}, parámetro: ${param}`);  // Mostrar qué botón fue clicado
            updateSelection(param);  // Ejecutar la función AJAX
        });
    });
});
