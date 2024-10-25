
        function capitalizeFirstLetter(str) {
            return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
        }

        document.addEventListener("DOMContentLoaded", function() {
            const listItems = document.querySelectorAll("#item-list li");
            listItems.forEach(item => {
                item.textContent = capitalizeFirstLetter(item.textContent);
            });
        });