
            document.addEventListener('DOMContentLoaded', function() {
                const payBookingBtn = document.getElementById('pay-booking-btn');
                const commissionStatsBtn = document.getElementById('commission-stats-btn');
                const commissionDetailsBtn = document.getElementById('commission-details-btn');
                const commissionBeneffitsBtn = document.getElementById('commission-beneffits-btn');
                const payBookingSection = document.getElementById('pay-booking');
                const commissionStatsSection = document.getElementById('commission-stats');
                const commissionDetailsSection = document.getElementById('commission-details');
                const commissionBeneffitsSection = document.getElementById('commission-beneffits');

                const buttons = [payBookingBtn, commissionStatsBtn, commissionDetailsBtn, commissionBeneffitsBtn ];

                buttons.forEach(button => {
                    button.addEventListener('click', function() {
                        buttons.forEach(btn => btn.classList.remove('active'));
                        button.classList.add('active');

                        payBookingSection.style.display = (button === payBookingBtn) ? 'block' : 'none';
                        commissionStatsSection.style.display = (button === commissionStatsBtn) ? 'block' : 'none';
                        commissionDetailsSection.style.display = (button === commissionDetailsBtn) ? 'block' : 'none';
                        commissionBeneffitsSection.style.display = (button === commissionBeneffitsBtn) ? 'block' : 'none';
                    });
                });
            });
