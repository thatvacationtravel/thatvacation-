
            jQuery(document).ready(function($) {
                $('#daterange').daterangepicker({
                    locale: {
                        format: 'MM/DD/YYYY',
                    },
                    startDate: moment(),
                    endDate: moment().endOf('month'),
                    minDate: moment(),
                    autoUpdateInput: false
                }, function(start, end, label) {
                    $('#daterange').val(start.format('MMM D') + ' - ' + end.format('MMM D'));
                    $('#hidden-daterange').val(start.format('MM/DD/YYYY') + ' - ' + end.format('MM/DD/YYYY'));
                });
                var defaultStart = moment();
                var defaultEnd = moment().endOf('month');
                $('#daterange').val(defaultStart.format('MMM D') + ' - ' + defaultEnd.format('MMM D'));
                $('#hidden-daterange').val(defaultStart.format('MM/DD/YYYY') + ' - ' + defaultEnd.format('MM/DD/YYYY'));
            });
