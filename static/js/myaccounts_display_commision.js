
            document.addEventListener('DOMContentLoaded', function() {
                const payBookingBtn = document.getElementById('pay-booking-btn');
                const commissionStatsBtn = document.getElementById('commission-stats-btn');
                const commissionDetailsBtn = document.getElementById('commission-details-btn');
                const payBookingSection = document.getElementById('pay-booking');
                const commissionStatsSection = document.getElementById('commission-stats');
                const commissionDetailsSection = document.getElementById('commission-details');

                if (payBookingBtn && commissionStatsBtn && commissionDetailsBtn && payBookingSection && commissionStatsSection && commissionDetailsSection) {
                    payBookingBtn.addEventListener('click', function() {
                        payBookingSection.style.display = 'block';
                        commissionStatsSection.style.display = 'none';
                        commissionDetailsSection.style.display = 'none';
                    });

                    commissionStatsBtn.addEventListener('click', function() {
                        payBookingSection.style.display = 'none';
                        commissionStatsSection.style.display = 'block';
                        commissionDetailsSection.style.display = 'none';
                    });

                    commissionDetailsBtn.addEventListener('click', function() {
                        payBookingSection.style.display = 'none';
                        commissionStatsSection.style.display = 'none';
                        commissionDetailsSection.style.display = 'block';
                    });
                }
            });
