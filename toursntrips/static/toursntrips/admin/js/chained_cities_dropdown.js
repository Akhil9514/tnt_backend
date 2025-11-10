window.addEventListener('load', function() {
    (function($) {
        var destinationsSelect = $('#id_destinations');
        var startCitySelect = $('#id_start_city');
        var endCitySelect = $('#id_end_city');
        // Function to update city dropdowns based on selected destinations
        function updateCityDropdowns() {
            var selectedDestIds = destinationsSelect.val() || [];
            if (selectedDestIds.length === 0) {
                // Clear and add placeholder
                startCitySelect.empty().append(new Option('--- Select Destinations First ---', ''));
                endCitySelect.empty().append(new Option('--- Select Destinations First ---', ''));
                return;
            }
            // Preserve current selections before clearing
            var currentStart = startCitySelect.val() || '';
            var currentEnd = endCitySelect.val() || '';
            // Clear existing
            startCitySelect.empty();
            endCitySelect.empty();
            // AJAX to get unique cities
            $.ajax({
                url: '/admin/toursntrips/tourntrips/ajax/possible-cities/',
                type: 'GET',
                traditional: true,  // For array params: dest_ids=1&dest_ids=2
                data: {dest_ids: selectedDestIds},
                dataType: 'json',
                success: function(data) {
                    if (data.length === 0) {
                        var placeholder = new Option('No cities in selected destinations', '');
                        startCitySelect.append(placeholder.cloneNode(true));
                        endCitySelect.append(placeholder.cloneNode(true));
                        return;
                    }
                    // Add options to both dropdowns
                    $.each(data, function(index, item) {
                        var opt = $('<option></option>').val(item.id).text(item.name);  // value=id (city string), text=name (city string)
                        startCitySelect.append(opt.clone(true));
                        endCitySelect.append(opt.clone(true));
                    });
                    // Restore selections if they match (for edits/initial or changes)
                    if (currentStart) {
                        startCitySelect.val(currentStart);
                        // Fallback: If not selected (e.g., old value not in new data), add it as option
                        if (startCitySelect[0].selectedIndex === -1) {
                            var fallbackOpt = $('<option></option>').val(currentStart).text(currentStart).prop('selected', true);
                            startCitySelect.prepend(fallbackOpt);
                        }
                    }
                    if (currentEnd) {
                        endCitySelect.val(currentEnd);
                        // Fallback for end
                        if (endCitySelect[0].selectedIndex === -1) {
                            var fallbackOptEnd = $('<option></option>').val(currentEnd).text(currentEnd).prop('selected', true);
                            endCitySelect.prepend(fallbackOptEnd);
                        }
                    }
                },
                error: function(xhr, status, error) {
                    console.error('AJAX Error:', status, error, xhr.responseText);
                    alert('Error loading cities. Please try again.');
                }
            });
        }
        // Bind to destinations change
        destinationsSelect.off('change').on('change', updateCityDropdowns);
        // No initial call needed: For edits, choices pre-populated in form; for adds, triggered on user change
    })(django.jQuery);
});