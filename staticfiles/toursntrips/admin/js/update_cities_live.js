/*  update_cities_live.js
    -------------------------------------------------
    Keeps the Start-City and End-City selects in sync
    with the currently chosen destinations.
    -------------------------------------------------
    Works together with:
      - chained_destinations.js  (populates the dual listbox)
      - chained_cities_dropdown.js (optional – can be removed)
    ------------------------------------------------- */
(function () {
    'use strict';

    // -----------------------------------------------------------------
    // Helper: wait until django.jQuery is ready
    // -----------------------------------------------------------------
    function ready(fn) {
        if (document.readyState !== 'loading') { fn(); }
        else { document.addEventListener('DOMContentLoaded', fn); }
    }

    ready(function () {
        if (typeof django === 'undefined' || !django.jQuery) {
            console.error('update_cities_live.js: django.jQuery not found');
            return;
        }
        const $ = django.jQuery;

        // -----------------------------------------------------------------
        // Elements we care about
        // -----------------------------------------------------------------
        const $chosenSelect   = $('#id_destinations_to');      // filter_horizontal "chosen"
        const $startSelect    = $('#id_start_city');
        const $endSelect      = $('#id_end_city');
        const $countrySelect  = $('#id_country');             // needed for edit-mode pre-population

        if (!$chosenSelect.length || !$startSelect.length || !$endSelect.length) {
            console.warn('update_cities_live.js: required elements not found');
            return;
        }

        // -----------------------------------------------------------------
        // AJAX endpoint (same as in admin.py)
        // -----------------------------------------------------------------
        const CITIES_URL = '/admin/toursntrips/tourntrips/ajax/possible-cities/';

        // -----------------------------------------------------------------
        // Build <option> elements from the server response
        // -----------------------------------------------------------------
        function buildOptions(cities) {
            const $opts = $('<option></option>').val('').text('---------');
            cities.forEach(function (city) {
                $opts = $opts.add(
                    $('<option></option>').val(city).text(city)
                );
            });
            return $opts;
        }

        // -----------------------------------------------------------------
        // Refresh both dropdowns
        // -----------------------------------------------------------------
        function refreshCityDropdowns(cities) {
            const $newOpts = buildOptions(cities);

            // Preserve currently selected values (if they still exist)
            const curStart = $startSelect.val();
            const curEnd   = $endSelect.val();

            $startSelect.empty().append($newOpts);
            $endSelect.empty().append($newOpts.clone());

            // Re-select the values the user had chosen before the refresh
            if (curStart && cities.indexOf(curStart) !== -1) $startSelect.val(curStart);
            if (curEnd   && cities.indexOf(curEnd)   !== -1) $endSelect.val(curEnd);

            // Enable / disable according to availability
            const enabled = cities.length > 0;
            $startSelect.prop('disabled', !enabled);
            $endSelect.prop('disabled',   !enabled);
        }

        // -----------------------------------------------------------------
        // Load cities from the server
        // -----------------------------------------------------------------
        function loadCities() {
            const chosenIds = $chosenSelect.val() || [];   // array of strings
            if (chosenIds.length === 0) {
                refreshCityDropdowns([]);
                return;
            }

            $.ajax({
                url: CITIES_URL,
                method: 'GET',
                data: { dest_ids: chosenIds },   // getlist works automatically
                dataType: 'json',
                traditional: true,
                success: function (data) {
                    // data = [{id: "Paris", name: "Paris"}, ...]
                    const cities = data.map(function (o) { return o.name; }).filter(Boolean);
                    refreshCityDropdowns(cities);
                },
                error: function (xhr, status, err) {
                    console.error('update_cities_live.js AJAX error:', status, err);
                    refreshCityDropdowns([]);
                }
            });
        }

        // -----------------------------------------------------------------
        // 1. Initial population (edit form – destinations already chosen)
        // -----------------------------------------------------------------
        if ($chosenSelect.find('option').length) {
            loadCities();
        } else {
            refreshCityDropdowns([]);
        }

        // -----------------------------------------------------------------
        // 2. React to every move in the dual listbox
        // -----------------------------------------------------------------
        // Django's SelectFilter2 fires a *change* on the hidden <select>
        // but also manipulates the DOM directly.  Listening to the
        // arrow buttons (delegated) + the hidden select covers all cases.
        $(document).on('click', '.selector-add, .selector-chooseall, .selector-remove, .selector-removeall', function () {
            // tiny debounce – the DOM needs a tick to settle
            setTimeout(loadCities, 50);
        });

        $chosenSelect.on('change', function () {
            setTimeout(loadCities, 50);
        });

        // -----------------------------------------------------------------
        // 3. Country change (only needed for the *add* form where the
        //     destinations list is rebuilt – the destinations script already
        //     calls reInitSelectFilter, which triggers the listeners above)
        // -----------------------------------------------------------------
        $countrySelect.on('change', function () {
            // When country changes the destinations list is cleared → cities must be cleared
            setTimeout(function () {
                if (!$chosenSelect.find('option').length) {
                    refreshCityDropdowns([]);
                }
            }, 100);
        });

        console.info('update_cities_live.js loaded and bound');
    });
})();