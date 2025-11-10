// toursntrips/admin/js/chained_destinations.js
// Handles dynamic population of destinations dual listbox based on country selection
// Updated: Fix duplicate options in sort, unbind old click handlers before reinit, delegated debug clicks

(function() {
    'use strict';

    // Wait for DOM ready using vanilla JS
    function ready(fn) {
        if (document.readyState !== 'loading') {
            fn();
        } else {
            document.addEventListener('DOMContentLoaded', fn);
        }
    }

    ready(function() {
        console.log('Chained Destinations JS: DOM ready');

        // Check if django.jQuery is available
        if (typeof django === 'undefined' || !django.jQuery || typeof django.jQuery !== 'function') {
            console.error('Chained Destinations JS: django.jQuery is not available. Cannot proceed.');
            return;
        }

        var $ = django.jQuery;  // Now safe to alias
        console.log('Chained Destinations JS: Using django.jQuery version', $.fn.jquery);

        var countrySelect = $('#id_country');
        var hiddenField = $('#id_destinations');           // Hidden input for form submission

        // Confirm country select exists
        if (!countrySelect.length) {
            console.warn('Chained Destinations JS: #id_country not found');
            return;
        }
        console.log('Chained Destinations JS: #id_country found');

        // Function to wait for filter_horizontal selects and setup
        function waitForFilterHorizontal(callback, maxAttempts = 50, interval = 100) {
            var attempts = 0;
            var intervalId = setInterval(function() {
                attempts++;
                var availableSelect = $('#id_destinations_from');  // filter_horizontal available box
                var chosenSelect = $('#id_destinations_to');      // filter_horizontal chosen box
                var chooserLinks = $('.selector-add, .selector-chooseall, .selector-remove, .selector-removeall');  // Arrow links

                if (availableSelect.length && chosenSelect.length && chooserLinks.length) {
                    clearInterval(intervalId);
                    console.log('Chained Destinations JS: filter_horizontal selects and links found after', attempts, 'attempts');
                    callback(availableSelect, chosenSelect, chooserLinks);
                } else if (attempts >= maxAttempts) {
                    clearInterval(intervalId);
                    console.error('Chained Destinations JS: filter_horizontal elements not found after', maxAttempts, 'attempts. Check if filter_horizontal is enabled.');
                    // Fallback: Log actual select and link elements
                    console.log('Available selects:', $('select').map(function() { return this.id; }).get());
                    console.log('Available chooser links:', $('.selector-add, .selector-chooseall, .selector-remove, .selector-removeall').map(function() { return $(this).text(); }).get());
                }
            }, interval);
        }

        // Setup once elements are ready
        waitForFilterHorizontal(function(availableSelect, chosenSelect, chooserLinks) {
            console.log('Chained Destinations JS: Setup starting with elements');

            // DEBUG: Log changes on selects to track moves
            availableSelect.on('change', function() {
                console.log('DEBUG: Available select changed - selected options:', $(this).find('option:selected').length, 'total options:', $(this).find('option').length);
                console.log('DEBUG: Selected option values:', $(this).find('option:selected').map(function() { return $(this).val(); }).get());
            });

            chosenSelect.on('change', function() {
                console.log('DEBUG: Chosen select changed - selected options:', $(this).find('option:selected').length, 'total options:', $(this).find('option').length);
                console.log('DEBUG: Chosen option texts:', chosenSelect.find('option').map(function() { return $(this).text(); }).get());
                console.log('DEBUG: Chosen option values:', chosenSelect.find('option').map(function() { return $(this).val(); }).get());
            });

            // DEBUG: Log clicks on chooser links (arrows) - using delegated event for reliability
            $(document).on('click', '.selector-add, .selector-chooseall, .selector-remove, .selector-removeall', function(e) {
                console.log('DEBUG: Chooser link clicked - class:', $(this).attr('class'), 'text:', $(this).text());
                // Log selected before move (for add/remove)
                if ($(this).hasClass('selector-add') || $(this).hasClass('selector-chooseall')) {
                    console.log('DEBUG: Before add - available selected:', availableSelect.find('option:selected').map(function() { return $(this).text(); }).get());
                } else if ($(this).hasClass('selector-remove') || $(this).hasClass('selector-removeall')) {
                    console.log('DEBUG: Before remove - chosen selected:', chosenSelect.find('option:selected').map(function() { return $(this).text(); }).get());
                }
                // Don't prevent default - let Django's handler run
            });

            // Function to update available destinations
            function updateAvailableDestinations() {
                console.log('Updating destinations for country:', countrySelect.val());
                var countryId = countrySelect.val();
                if (!countryId) {
                    console.log('No country selected, clearing available');
                    availableSelect.empty();
                    updateHiddenField();
                    // reInitSelectFilter();


                    reInitSelectFilter();

                    // NEW: let the city-dropdown script know that the chosen set changed
                    if (typeof window.dispatchEvent === 'function') {
                        window.dispatchEvent(new Event('destinationsChanged'));
                    }

                    console.log('Available repopulated with', availableData.length, 'options');

                    return;
                }

                // Get current chosen before any changes
                var currentChosen = chosenSelect.val() || [];

                $.ajax({
                    url: '/admin/toursntrips/tourntrips/ajax/destinations/',
                    type: 'GET',
                    data: {country_id: countryId},
                    dataType: 'json',
                    success: function(data) {
                        console.log('AJAX success: loaded', data.length, 'destinations');
                        if (!data || data.length === 0) {
                            availableSelect.empty().append(new Option('No destinations for this country', ''));
                            updateHiddenField();
                            reInitSelectFilter();
                            return;
                        }

                        // Get all new possible IDs as strings
                        var newAvailableIds = data.map(function(item) { return item.id.toString(); });

                        // Remove invalid options from chosen (those not in new country)
                        var removedCount = 0;
                        chosenSelect.find('option').each(function() {
                            if (newAvailableIds.indexOf(this.value) === -1) {
                                $(this).remove();
                                removedCount++;
                            }
                        });
                        if (removedCount > 0) {
                            console.log('Removed', removedCount, 'invalid destinations from chosen');
                        }

                        // Calculate kept chosen IDs (intersection of current and new)
                        var keptChosenIds = currentChosen.filter(function(id) {
                            return newAvailableIds.indexOf(id) !== -1;
                        });

                        // Filter data for available: only those not in kept chosen
                        var availableData = data.filter(function(item) {
                            return keptChosenIds.indexOf(item.id.toString()) === -1;
                        });

                        // Clear and repopulate available with filtered data
                        availableSelect.empty();
                        $.each(availableData, function(index, item) {
                            var opt = $('<option></option>').val(item.id.toString()).text(item.name);  // Ensure string value
                            availableSelect.append(opt);
                        });

                        // Sort the options alphabetically: detach, sort, re-append (prevents duplicates)
                        var options = availableSelect.find('option').detach().sort(function(a, b) {
                            var aText = $(a).text().toLowerCase();
                            var bText = $(b).text().toLowerCase();
                            return aText.localeCompare(bText);
                        });
                        availableSelect.append(options);

                        // If no available after filtering, add placeholder
                        if (availableData.length === 0) {
                            availableSelect.append(new Option('All destinations already selected', ''));
                        }

                        // Update hidden field with current (updated) chosen values
                        updateHiddenField();

                        // Re-initialize SelectFilter2 to ensure move handlers are properly bound after DOM changes
                        reInitSelectFilter();

                        console.log('Available repopulated with', availableData.length, 'options');
                    },
                    error: function(xhr, status, error) {
                        console.error('AJAX Error:', status, error, xhr.responseText);
                        availableSelect.empty().append(new Option('Error loading destinations', ''));
                        updateHiddenField();
                        reInitSelectFilter();
                    }
                });
            }

            // Helper to re-initialize Django's SelectFilter2 (unbind old handlers first, then re-bind)
            function reInitSelectFilter() {
                console.log('Attempting reinit SelectFilter2');
                // Unbind existing click handlers to prevent multiples/duplicates
                chooserLinks.off('click');
                console.log('Off click handlers before reinit');
                if (typeof SelectFilter2 !== 'undefined') {
                    try {
                        SelectFilter2.init('id_destinations_from', 'id_destinations_to', '', '');
                        console.log('Re-initialized SelectFilter2 successfully');
                    } catch (e) {
                        console.error('Failed to re-init SelectFilter2:', e);
                    }
                } else {
                    console.warn('SelectFilter2 not available - moves may not work');
                }
            }

            // Helper to update hidden field (comma-separated IDs)
            function updateHiddenField() {
                var chosenVals = chosenSelect.val() || [];
                hiddenField.val(chosenVals.join(','));
                console.log('Hidden field updated to:', hiddenField.val());
            }

            // Bind to country change
            countrySelect.off('change').on('change', function() {
                console.log('Country changed to:', $(this).val());
                updateAvailableDestinations();
            });

            // Initial load: If country pre-selected (edit or prefilled add), populate
            if (countrySelect.val()) {
                console.log('Initial country pre-selected, populating destinations');
                updateAvailableDestinations();
            } else {
                console.log('No initial country, available will populate on change');
            }

            // Optional: Backup listener for hidden sync (Django handles primarily)
            chosenSelect.on('change', updateHiddenField);

            console.log('Chained Destinations JS: Setup complete');
        });

        console.log('Chained Destinations JS: Waiting for filter_horizontal...');
    });
})();