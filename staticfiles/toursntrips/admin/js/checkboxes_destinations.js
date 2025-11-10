// toursntrips/admin/js/checkboxes_destinations.js
// Handles dynamic population of destinations checkboxes based on country selection

(function() {
    'use strict';

    function ready(fn) {
        if (document.readyState !== 'loading') {
            fn();
        } else {
            document.addEventListener('DOMContentLoaded', fn);
        }
    }

    ready(function() {
        console.log('Checkboxes Destinations JS: DOM ready');

        if (typeof django === 'undefined' || !django.jQuery) {
            console.error('Checkboxes Destinations JS: django.jQuery is not available.');
            return;
        }

        var $ = django.jQuery;

        var countrySelect = $('#id_country');
        var destinationsContainer = $('#id_destinations');

        if (!countrySelect.length) {
            console.warn('Checkboxes Destinations JS: #id_country not found');
            return;
        }

        if (!destinationsContainer.length) {
            console.warn('Checkboxes Destinations JS: Destinations container not found');
            return;
        }

        console.log('Checkboxes Destinations JS: Setup starting');

        // Function to update destinations checkboxes
        function updateDestinationsCheckboxes() {
            var countryId = countrySelect.val();
            if (!countryId) {
                destinationsContainer.empty();
                destinationsContainer.html('<li style="margin: 10px; padding: 5px; border: 1px solid #ccc; background: #f9f9f9;"><p>No country selected. Please select a country to see destinations.</p></li>');
                // Clear hidden values? But form handles empty
                $(document).trigger('destinationsChanged');
                return;
            }

            // Get current checked values before update
            var currentChecked = $('input[name="destinations"]:checked').map(function() {
                return $(this).val();
            }).get();

            $.ajax({
                url: '/admin/toursntrips/tourntrips/ajax/destinations-checkboxes/',
                type: 'GET',
                data: {country_id: countryId},
                dataType: 'json',
                success: function(data) {
                    console.log('AJAX success: loaded destinations HTML');
                    destinationsContainer.html(data.html);
                    // Re-check valid previous selections
                    $('input[name="destinations"]').each(function() {
                        if (currentChecked.indexOf($(this).val()) !== -1) {
                            $(this).prop('checked', true);
                        }
                    });
                    // Trigger change for cities update
                    $(document).trigger('destinationsChanged');
                },
                error: function(xhr, status, error) {
                    console.error('AJAX Error:', status, error);
                    destinationsContainer.empty();
                    destinationsContainer.html('<li style="margin: 10px; padding: 5px; border: 1px solid #ccc; background: #f9f9f9;"><p>Error loading destinations.</p></li>');
                }
            });
        }

        // Bind to country change
        countrySelect.on('change', updateDestinationsCheckboxes);

        // Initial load if country pre-selected
        if (countrySelect.val()) {
            updateDestinationsCheckboxes();
        } else {
            // Initial empty message for add form
            destinationsContainer.html('<li style="margin: 10px; padding: 5px; border: 1px solid #ccc; background: #f9f9f9;"><p>Select a country to see destinations.</p></li>');
        }

        console.log('Checkboxes Destinations JS: Setup complete');
    });
})();