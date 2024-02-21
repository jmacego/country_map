var mymap = L.map('mapid').setView([0, 0], 2); // Center the map on the world

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
}).addTo(mymap);

var countriesVisitedByJohn;

fetch('/api/countries')
    .then(response => response.json())
    .then(data => {
        countriesVisitedByJohn = data;
        return fetch('https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json');
    })
    .then(response => response.json())
    .then(data => {
        L.geoJSON(data, {
            style: function(feature) {
                var country = countriesVisitedByJohn.find(function(c) {
                    return c.name === feature.properties.name;
                });
                return {color: country && country.john ? 'red' : 'blue'};
            }
        }).addTo(mymap);
    });