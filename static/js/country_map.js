// Initialize the map
var map = L.map('map').setView([0, 0], 2);

// Define global variables to hold the data
var countriesData = [];
var visitedData = [];

// Define a variable outside of your function to hold the layer
var geoJsonLayer;

// Define the URLs for the API endpoints
const geoDataUrl = '/api/geodata';
const visitedDataUrl = '/api/visited';
// Fetch the GeoPandas data
function fetchAndUpdateGeoData() {
    fetch(geoDataUrl)
        .then(response => response.json())
        .then(data => {
            // Assign the data to the countriesData variable
            countriesData = JSON.parse(data);
            // Create a GeoJSON layer with the fetched data
            updateMap();

            // Call the function to fetch data and populate the dropdown
            populateCountryDropdown();
        })
        .catch(error => console.error('Error fetching GeoPandas data:', error));
}

// Fetch the visited countries data with retry on 500 status code
function fetchAndUpdateVisitedData(attempt = 1) {
    fetch(visitedDataUrl)
        .then(response => {
            if (!response.ok) {
                // If the response status code is 500, retry up to 5 times
                if (response.status === 500 && attempt < 5) {
                    console.log(`Attempt ${attempt}: Server error, retrying...`);
                    setTimeout(() => fetchAndUpdateVisitedData(attempt + 1), 2000); // Wait 2 seconds before retrying
                } else {
                    // If the response status code is not 500 or we've retried 5 times, throw an error
                    throw new Error(`Request failed with status ${response.status}`);
                }
            } else {
                // If the response is ok, proceed to process the data
                return response.json();
            }
        })
        .then(data => {
            // Assign the data to the visitedData variable
            visitedData = data;
            updateMap();

            // Function to update the list of visited countries
            updateVisitedList();
            console.log("Updated");
        })
        .catch(error => console.error('Error fetching visited countries data:', error));
}

function getCountryVisitStatus(countryName) {
    // Find the country in visitedData that matches the given name
    var country = visitedData.find(c => c.name === countryName);
    return country ? { john: country.john, marcia: country.marcia, todo: country.todo }
        : { john: false, marcia: false, todo: false };
}

// Function to create a list item
function createListItem(text) {
    const listItem = document.createElement('li');
    listItem.textContent = text;
    listItem.className = 'list-group-item'; // Bootstrap class for styling
    return listItem;
}

// Function to update the lists
function updateVisitedList() {
    // Find the list elements
    const bothVisitedList = document.getElementById('bothVisitedList');
    const marciaVisitedList = document.getElementById('marciaVisitedList');
    const johnVisitedList = document.getElementById('johnVisitedList');
    const todoList = document.getElementById('todoList');

    // Clear any existing list items
    bothVisitedList.innerHTML = '';
    marciaVisitedList.innerHTML = '';
    johnVisitedList.innerHTML = '';
    todoList.innerHTML = '';

    // Add countries to the respective lists
    visitedData.forEach(country => {
        if (country.john && country.marcia) {
        bothVisitedList.appendChild(createListItem(country.name));
        } else if (country.marcia) {
        marciaVisitedList.appendChild(createListItem(country.name));
        } else if (country.john) {
        johnVisitedList.appendChild(createListItem(country.name));
        }
        if (country.todo) {
        todoList.appendChild(createListItem(country.name));
        }
    });
}

function style(feature) {
    // Get the visit status for the country
    var visitStatus = getCountryVisitStatus(feature.properties.NAME_EN);

    // Determine the color based on the 'john' and 'marcia' properties
    var color;
    if (visitStatus.john && visitStatus.marcia) {
        color = 'purple'; // Both John and Marcia have visited
    } else if (visitStatus.marcia) {
        color = 'red'; // Only Marcia has visited
    } else if (visitStatus.john) {
        color = 'blue'; // Only John has visited
    } else if (visitStatus.todo) {
        color = 'black'; // To visit
    } else {
        color = 'grey'; // Neither has visited
    }

    // Return the style object with the determined color
    return {
        fillColor: color,
        weight: 2,
        opacity: 1,
        color: 'white',
        fillOpacity: 0.7
    };
}

document.getElementById('countryForm').addEventListener('submit', function(event) {
    event.preventDefault();

    // Get the form data
    const countryId = document.getElementById('countryId').value;
    const countryName = document.getElementById('countryName').value;
    const visitedJohn = document.getElementById('visitedJohn').checked;
    const visitedMarcia = document.getElementById('visitedMarcia').checked;
    const todo = document.getElementById('todo').checked;

    // Determine if this is an add or update operation based on the presence of an ID
    const method = countryId ? 'PUT' : 'POST';
    const endpoint = countryId ? `/api/visited/${countryId}` : '/api/visited';

    // Create the request body
    const requestBody = {
        name: countryName,
        john: visitedJohn,
        marcia: visitedMarcia,
        todo: todo
    };

    // If updating, include the ID in the request body
    if (method === 'PUT') {
        requestBody.id = parseInt(countryId);
    }

    // Send the data to the server
    fetch(endpoint, {
        method: method,
        headers: {
        'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
    })
    .then(response => response.json())
    .then(data => {
        // Clear the form
        document.getElementById('countryForm').reset();
        // Update the UI as needed
    })
    .then(fetchAndUpdateVisitedData())
    .catch((error) => {
        console.error('Error:', error);
    });
});

// Function to populate the dropdown with country names
function populateCountryDropdown() {
    const dropdown = document.getElementById('countryName');
    
    // Clear existing options
    dropdown.innerHTML = '';

    // Add a default option
    const defaultOption = document.createElement('option');
    defaultOption.textContent = 'Select a country';
    defaultOption.value = '';
    dropdown.appendChild(defaultOption);

    // Map the country names and sort them
    countries = countriesData.features.map(feature => feature.properties.NAME_EN).sort();
    // Add countries as options
    countries.forEach(country => {
        const option = document.createElement('option');
        option.textContent = country;
        option.value = country;
        dropdown.appendChild(option);
    });
}

function updateMap() {
    // If there's already a layer, remove it
    if (geoJsonLayer) {
        map.removeLayer(geoJsonLayer);
    }

    // Create a new GeoJSON layer and add it to the map
    geoJsonLayer = L.geoJSON(countriesData, {
        style: style,
        onEachFeature: function (feature, layer) {
            if (feature.properties && feature.properties.NAME_EN) {
                // Bind a tooltip to the layer that will show on hover
                layer.bindTooltip(feature.properties.NAME_EN, {
                    direction: 'center', // Center the tooltip on the feature
                    className: 'countryLabel' // Custom CSS class for styling
                });
            }
        }
    }).addTo(map);
}

fetchAndUpdateGeoData();
fetchAndUpdateVisitedData();