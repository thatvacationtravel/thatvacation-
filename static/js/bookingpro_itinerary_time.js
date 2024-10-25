document.addEventListener("DOMContentLoaded", function() {
    function formatTime(timeStr) {
        if (timeStr.length === 4) {
            return timeStr.slice(0, 2) + ':' + timeStr.slice(2);
        }
        return timeStr;
    }

    document.querySelectorAll('.formatted-time').forEach(function(span) {
        var departure = span.getAttribute('data-departure');
        var arrival = span.getAttribute('data-arrival');
        if (departure && arrival) {
            span.textContent = formatTime(departure) + ' to ' + formatTime(arrival);
        } else {
            var time = span.getAttribute('data-time');
            span.textContent = formatTime(time);
        }
    });

    document.getElementById("ver-mas").addEventListener("click", function(event) {
        event.preventDefault();
        var button = document.getElementById("ver-mas");
        var expanded = button.getAttribute("data-expanded") === "true";
        var allItems = document.querySelectorAll(".detalle");

        if (expanded) {
            // Ocultar los elementos y cambiar el texto a "Show more"
            allItems.forEach(function(item, index) {
                if (index >= 0) {
                    item.style.display = "none";
                }
            });
            button.innerHTML = 'Itinerary<span id="flecha-abajo">&#9660;</span>';
            button.setAttribute("data-expanded", "false");
        } else {
            // Mostrar los elementos y cambiar el texto a "Show less"
            allItems.forEach(function(item) {
                item.style.display = "block";
            });
            button.innerHTML = 'Show less<span id="flecha-arriba">&#9650;</span>';
            button.setAttribute("data-expanded", "true");
        }
    });
});