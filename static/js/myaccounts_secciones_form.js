
            jQuery(document).ready(function($) {
                $('#btn-perfil').click(function() {
                    $('.contenido-seccion').hide();
                    $('#profile').show();

                    $('#btn-perfil').addClass('active');
                    $('#btn-history').removeClass('active');
                    $('#btn-buscar-cruceros-hoteles').removeClass('active');
                });

                $('#btn-history').click(function() {
                    $('.contenido-seccion').hide();
                    $('#history').show();

                    $('#btn-history').addClass('active');
                    $('#btn-perfil').removeClass('active');
                    $('#btn-buscar-cruceros-hoteles').removeClass('active');
                });

                $('#btn-buscar-cruceros-hoteles').click(function() {
                    $('.contenido-seccion').hide();
                    $('#formulario-busqueda').show();

                    $('#btn-buscar-cruceros-hoteles').addClass('active');
                    $('#btn-history').removeClass('active');
                    $('#btn-perfil').removeClass('active');
                });

                $('#formulario-busqueda').show();
                $('#btn-buscar-cruceros-hoteles').addClass('active');
            });
