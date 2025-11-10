window.addEventListener('load', function() {
    (function($) {
        var destinationsSelect = $('#id_destinations');
        var startCityInput = $('#id_start_city');
        var endCityInput = $('#id_end_city');

        // Create shared datalist for autocomplete suggestions
        var datalist = $('<datalist id="possible_cities"></datalist>');
        $('body').append(datalist);

        // Function to update possible cities suggestions
        function updatePossibleCities() {
            var selectedDestIds = destinationsSelect.val() || [];
            if (selectedDestIds.length === 0) {
                datalist.empty();
                startCityInput.attr('placeholder', 'Select destinations first to see suggestions');
                endCityInput.attr('placeholder', 'Select destinations first to see suggestions');
                return;
            }

            $.ajax({
                url: '/admin/toursntrips/tourntrips/ajax/possible-cities/',
                type: 'GET',
                traditional: true,  // For array params
                data: {dest_ids: selectedDestIds},
                dataType: 'json',
                success: function(data) {
                    datalist.empty();
                    $.each(data, function(index, item) {
                        datalist.append($('<option>').attr('value', item.city));
                    });
                    if (data.length === 0) {
                        startCityInput.attr('placeholder', 'No cities in selected destinations');
                        endCityInput.attr('placeholder', 'No cities in selected destinations');
                    } else {
                        startCityInput.removeAttr('placeholder');
                        endCityInput.removeAttr('placeholder');
                    }
                },
                error: function(xhr, status, error) {
                    console.error('AJAX Error:', status, error);
                    alert('Error loading possible cities.');
                }
            });
        }

        // Bind to destinations change
        destinationsSelect.off('change').on('change', updatePossibleCities);

        // Optional: Real-time validation on blur (client-side check)
        startCityInput.off('blur').on('blur', function() {
            var value = $(this).val().trim();
            if (value) {
                var options = datalist.find('option[value="' + value + '"]');
                if (options.length === 0) {
                    alert('Start city must match a selected destination\'s city. Suggestions: ' + datalist.find('option').map(function() { return $(this).val(); }).get().join(', '));
                    $(this).focus();
                }
            }
        });

        endCityInput.off('blur').on('blur', function() {
            var value = $(this).val().trim();
            if (value) {
                var options = datalist.find('option[value="' + value + '"]');
                if (options.length === 0) {
                    alert('End city must match a selected destination\'s city. Suggestions: ' + datalist.find('option').map(function() { return $(this).val(); }).get().join(', '));
                    $(this).focus();
                }
            }
        });

        // Initial load if pre-selected
        if (destinationsSelect.val()) {
            updatePossibleCities();
        }
    })(django.jQuery);
});