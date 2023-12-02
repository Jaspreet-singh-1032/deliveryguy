
                  // scripts.js custom js file
         $(document).ready(function () {
            google.maps.event.addDomListener(window, 'load', initialize);
         });

         function initialize() {
            var input = document.getElementById('id_myaddress');
            var autocomplete = new google.maps.places.Autocomplete(input);
         }
      
        

            // This example displays an address form, using the autocomplete feature
            // of the Google Places API to help users fill in the information.
            var placeSearch, autocomplete, autocomplete2;
            var componentForm = {
              street_number: 'short_name',
              route: 'long_name',
              locality: 'long_name',
              administrative_area_level_1: 'short_name',
              country: 'long_name',
              postal_code: 'short_name'
            };
            
            function initAutocomplete() {
              // Create the autocomplete object, restricting the search to geographical
              // location types.
              autocomplete = new google.maps.places.Autocomplete(
                /** @type {!HTMLInputElement} */
                (document.getElementById('id_shipping_address')));
            
              // When the user selects an address from the dropdown, populate the address
              // fields in the form.
              autocomplete.addListener('place_changed', function() {
                fillInAddress(autocomplete, "");
              });
            
              autocomplete2 = new google.maps.places.Autocomplete(
                /** @type {!HTMLInputElement} */
                (document.getElementById('id_myaddress')));
              autocomplete2.addListener('place_changed', function() {
                fillInAddress(autocomplete2, "2");
              });
            
            }
            
            function fillInAddress(autocomplete, unique) {
              // Get the place details from the autocomplete object.
              var place = autocomplete.getPlace();

              if (!place.geometry) {
                var geocoder = new google.maps.Geocoder();
                geocoder.geocode({ 'address': place.name }, function(results, status) {
                    if (status !== 'OK') {
                        document.getElementById('error').style.display = 'inline';
                        setTimeout(function() {
                            document.getElementById('error').style.display = 'none';
                        }, 3000);
                    } else {
                        // The address is valid. Handle it accordingly.
                    }
                });
            }
            }
            
              for (var component in componentForm) {
                if (!!document.getElementById(component + unique)) {
                  document.getElementById(component + unique).value = '';
                  document.getElementById(component + unique).disabled = false;
                }
              }


            
              // Get each component of the address from the place details
              // and fill the corresponding field on the form.
              for (var i = 0; i < place.address_components.length; i++) {
                var addressType = place.address_components[i].types[0];
                if (componentForm[addressType] && document.getElementById(addressType + unique)) {
                  var val = place.address_components[i][componentForm[addressType]];
                  document.getElementById(addressType + unique).value = val;
                }
              }
              document.getElementById('id_latitude' + unique).value = place.geometry.location.lat();
              document.getElementById('id_longitude' + unique).value = place.geometry.location.lng();
            
            }
            google.maps.event.addDomListener(window, "load", initAutocomplete);
            
            function geolocate() {
                if (navigator.geolocation) {
                  navigator.geolocation.getCurrentPosition(function(position) {
                    var geolocation = {
                      lat: position.coords.latitude,
                      lng: position.coords.longitude
                    };
                    var circle = new google.maps.Circle({
                      center: geolocation,
                      radius: position.coords.accuracy
                    });
                    autocomplete.setBounds(circle.getBounds());
                  });
                }
              }
              // [END region_geolocation]