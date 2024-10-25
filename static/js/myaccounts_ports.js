document.addEventListener('DOMContentLoaded', function() {
    $('#id_destination').select2({
        placeholder: "Select a destination",
        allowClear: true
    }).on('change', function() {
        const destinationId = $(this).val();
        const portSelect = $('#id_port');

        if (destinationId) {
            $.ajax({
                url: '/ajax/load-ports/',
                data: {
                    destino_id: destinationId
                },
                success: function(data) {
                    portSelect.empty();
                    portSelect.append(new Option("Any Port", "Any Port")); 
                    $.each(data, function(index, port) {
                        portSelect.append(new Option(port.port_name, port.port_code));
                    });
                    portSelect.select2(); 
                }
            });
        } else {
            portSelect.empty(); 
            portSelect.select2();
        }
    });

    $('#id_port').select2({
        placeholder: "Select a port",
        allowClear: true
    });
});
