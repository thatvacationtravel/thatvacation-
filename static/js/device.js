document.addEventListener('DOMContentLoaded', function() {
        const menuToggle = document.getElementById('menu-toggle');
        const sidebarContent = document.getElementById('sidebarContent');
        const menuIcon = document.getElementById('menu-icon');

        const isMobile = () => {
            return /Mobi|Android|iPhone|iPad/i.test(navigator.userAgent);
        };

        if (menuToggle && sidebarContent && menuIcon) {  // Verifica que los elementos existan
            if (isMobile()) {
                // Ocultar el contenido del menú inicialmente en dispositivos móviles
                sidebarContent.style.display = 'none';

                menuToggle.addEventListener('click', function() {
                    const isOpen = sidebarContent.style.display === 'block';
                    sidebarContent.style.display = isOpen ? 'none' : 'block';
                    menuIcon.textContent = isOpen ? '▲' : '▼';
                });
            } else {
                // Mostrar el contenido del menú automáticamente en pantallas grandes
                sidebarContent.style.display = 'block';
            }

            // Ocultar el menú cuando se selecciona un botón o enlace en móviles
            const buttons = sidebarContent.querySelectorAll('button, a');
            buttons.forEach(button => {
                button.addEventListener('click', function() {
                    if (isMobile()) {
                        sidebarContent.style.display = 'none';
                        menuIcon.textContent = '▲';
                    }
                });
            });
        } else {

        }
    });