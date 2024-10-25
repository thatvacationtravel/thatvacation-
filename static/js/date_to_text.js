document.addEventListener("DOMContentLoaded", function() {
    function formatDate(dateStr) {
        if (!dateStr) return '';

        var date = new Date(dateStr);
        var options = { year: 'numeric', month: 'long', day: 'numeric' };

        return date.toLocaleDateString('en-US', options);
    }

    document.querySelectorAll('.formatted-date').forEach(function(span) {
        var date = span.getAttribute('data-date');
        if (date) {
            span.textContent = formatDate(date);
        }
    });
});
