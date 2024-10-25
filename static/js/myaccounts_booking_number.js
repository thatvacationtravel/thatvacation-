
        $(document).ready(function() {
            var currentPage = 1;
            var hasNextPage = false;

            function loadResults(page) {
                $.ajax({
                    url: $('#search-form').attr('action'),
                    type: 'GET',
                    data: $('#search-form').serialize() + '&page=' + page,
                    success: function(data) {
                        var results = data.results;
                        var html = '<ul class="list-group">';
                        if (results.length > 0) {
                            results.forEach(function(booking) {
                                var createdDate = new Date(booking.created_at);
                                var year = createdDate.getFullYear();
                                var month = ("0" + (createdDate.getMonth() + 1)).slice(-2);
                                var day = ("0" + createdDate.getDate()).slice(-2);
                                var formattedDate = year + month + day;
                                html += '<li class="list-group-item">';
                                html += '<div class="card-body">';
                                html += '<strong>Booking Number:</strong> ' + booking.booking_number + '<br>';
                                html += '<strong>Ship ID:</strong> ' + booking.ship + '<br>';
                                html += '<strong>Departure Date:</strong> ' + booking.departure_day + '<br>';
                                html += '<strong>Name:</strong> ' + booking.first_name + ' ' + booking.last_name + '<br>';
                                html += '<strong>Email:</strong> ' + booking.email + '<br>';
                                html += '<strong>Phone:</strong> ' + booking.phone + '<br>';
                                html += '<strong>Created at:</strong> ' + booking.created_at + '<br>';
                                html += '<strong>Balance:</strong>' + booking.balance + '<br>';
                                html += '<div class="make-payment-btn" style="margin-top: 20px; width: 25%;">';
                                html += '<a href="/record_payment/' + booking.booking_number + '/" class="btn btn-primary btn-md">Make Payment</a>';
                                var invoiceUrl = '/media/invoices/TVT_' + formattedDate + '_' + booking.booking_number + '.pdf';
                                html += '<a href="' + invoiceUrl + '" class="btn btn-success download-btn" download="TVT_' + formattedDate + '_' + booking.booking_number + '.pdf">';
                                html += '<i class="fas fa-download"></i>';
                                html += '</a>';
                                html += '</div>';
                                html += '</li>';
                            });

                            hasNextPage = data.has_next;
                        } else {
                            html += '<li class="list-group-item">No results found.</li>';
                        }

                        html += '</ul>';
                        $('#search-results').html(html);

                        if (hasNextPage) {
                            $('#load-more').show();
                        } else {
                            $('#load-more').hide();
                        }
                    },
                    error: function(xhr, status, error) {
                        $('#search-results').html('<p class="text-danger">An error occurred: ' + error + '</p>');
                    }
                });
            }

            $('#search-form').on('submit', function(event) {
                event.preventDefault();
                currentPage = 1;
                loadResults(currentPage);
            });

            $('#load-more').on('click', function() {
                if (hasNextPage) {
                    currentPage++;
                    $(this).css('animation', 'contract 0.5s forwards').on('animationend', function() {
                        $(this).hide();
                        loadResults(currentPage);
                        $(this).css('animation', 'expand 0.5s forwards').show();
                    });
                }
            });

            $('#load-more').hide();
        });


