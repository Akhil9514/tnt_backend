// toursntrips/admin/js/checkboxes_cities.js
// Handles dynamic population of start/end city checkboxes based on destinations selection
// Enforces only one checkbox per group (start/end)

(function() {
    'use strict';

    function ready(fn) {
        if (document.readyState !== 'loading') { fn(); }
        else { document.addEventListener('DOMContentLoaded', fn); }
    }

    ready(function() {
        if (typeof django === 'undefined' || !django.jQuery) {
            console.error('Checkboxes Cities JS: django.jQuery not found');
            return;
        }
        const $ = django.jQuery;

        let $startContainer = $('#id_start_city');
        let $endContainer = $('#id_end_city');
        const CITIES_URL = '/admin/toursntrips/tourntrips/ajax/cities-checkboxes/';

        if (!$startContainer.length || !$endContainer.length) {
            console.warn('Checkboxes Cities JS: City containers not found');
            return;
        }

        // Function to load cities
        function loadCities(fieldName, container) {
            var destIds = $('input[name="destinations"]:checked').map(function() {
                return $(this).val();
            }).get();

            if (destIds.length === 0) {
                container.empty();
                container.html('<li style="margin: 10px; padding: 5px; border: 1px solid #ccc; background: #f9f9f9;"><p>No destinations selected. Please select destinations to see cities.</p></li>');
                return;
            }

            var currentSelected = $('input[name="' + fieldName + '"]:checked').val() || '';

            $.ajax({
                url: CITIES_URL,
                method: 'GET',
                data: { dest_ids: destIds, field_name: fieldName },
                dataType: 'json',
                traditional: true,
                success: function(data) {
                    container.html(data.html);
                    // Re-check previous if still available
                    if (currentSelected) {
                        container.find('input[value="' + currentSelected + '"]').prop('checked', true);
                    }
                },
                error: function(xhr, status, err) {
                    console.error('AJAX error:', status, err);
                    container.empty();
                    container.html('<li style="margin: 10px; padding: 5px; border: 1px solid #ccc; background: #f9f9f9;"><p>Error loading cities.</p></li>');
                }
            });
        }

        // Enforce single selection per group
        function enforceSingleSelection(container, fieldName) {
            container.off('change', 'input[type="checkbox"]').on('change', 'input[type="checkbox"]', function() {
                if ($(this).is(':checked')) {
                    container.find('input[type="checkbox"]').not(this).prop('checked', false);
                }
            });
        }

        // Initial setup
        enforceSingleSelection($startContainer, 'start_city');
        enforceSingleSelection($endContainer, 'end_city');

        // Load initial if edit (destinations may be pre-checked)
        var initialDestIds = $('input[name="destinations"]:checked').map(function(){return $(this).val();}).get();
        if (initialDestIds.length > 0) {
            loadCities('start_city', $startContainer);
            loadCities('end_city', $endContainer);
        } else {
            // Initial empty message
            $startContainer.empty();
            $startContainer.html('<li style="margin: 10px; padding: 5px; border: 1px solid #ccc; background: #f9f9f9;"><p>Select destinations to see start cities.</p></li>');
            $endContainer.empty();
            $endContainer.html('<li style="margin: 10px; padding: 5px; border: 1px solid #ccc; background: #f9f9f9;"><p>Select destinations to see end cities.</p></li>');
        }

        // Listen for destinations change
        $(document).on('change', 'input[name="destinations"]', function() {
            setTimeout(function() {
                loadCities('start_city', $startContainer);
                loadCities('end_city', $endContainer);
            }, 50);
        });

        // Also listen to custom event from destinations JS
        $(document).on('destinationsChanged', function() {
            setTimeout(function() {
                loadCities('start_city', $startContainer);
                loadCities('end_city', $endContainer);
            }, 50);
        });

        // Country change: if no destinations, clear cities
        $('#id_country').on('change', function() {
            setTimeout(function() {
                if (!$('input[name="destinations"]:checked').length) {
                    $startContainer.empty();
                    $startContainer.html('<li style="margin: 10px; padding: 5px; border: 1px solid #ccc; background: #f9f9f9;"><p>Select country and destinations first.</p></li>');
                    $endContainer.empty();
                    $endContainer.html('<li style="margin: 10px; padding: 5px; border: 1px solid #ccc; background: #f9f9f9;"><p>Select country and destinations first.</p></li>');
                }
            }, 100);
        });

        console.info('Checkboxes Cities JS loaded and bound');
    });
})();