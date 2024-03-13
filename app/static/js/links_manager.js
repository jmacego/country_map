const apiURL = '/travel/api/links'

document.addEventListener('DOMContentLoaded', function() {
    const linksListElement = document.getElementById('links-list');
    const addLinkForm = document.getElementById('add-link-form');

    addLinkForm.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent the default form submission
        addLink();
    });


    function updateLink(id) {
        const nameInput = document.querySelector(`.link-name[data-id='${id}']`);
        const urlInput = document.querySelector(`.link-url[data-id='${id}']`);
        const notesInput = document.querySelector(`.link-notes[data-id='${id}']`);
    
        const updatedLink = {
            name: nameInput.value,
            url: urlInput.value,
            notes: notesInput.value
        };
    
        fetch(apiURL + "/" + id, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(updatedLink),
        })
        .then(response => response.json())
        .then(data => {
            console.log('Link updated:', data);
            fetchLinks(); // Refresh the list of links
        })
        .catch(error => console.error('Error updating link:', error));
    }
    

    // Function to delete a link
    function deleteLink(id) {
        if (confirm('Are you sure you want to delete this link?')) {
            fetch(apiURL + "/" + id, {
                method: 'DELETE'
            })
            .then(() => {
                console.log('Link deleted');
                fetchLinks(); // Refresh the list of links
            })
            .catch(error => console.error('Error deleting link:', error));
        }
    }
    // Fetch and display the links
    function fetchLinks() {
        fetch(apiURL)
            .then(response => response.json())
            .then(data => {
                displayLinks(data);
            })
            .catch(error => console.error('Error fetching links:', error));
    }
    // Function to add a new link
    function addLink() {
        const nameInput = document.getElementById('linkName');
        const urlInput = document.getElementById('linkUrl');
        const notesInput = document.getElementById('linkNotes'); // Ensure you have an input for notes

        // Validate and format the URL
        let url = urlInput.value;
        if (!url.match(/^(http:\/\/|https:\/\/|ftp:\/\/).*/i)) {
            url = 'https://' + url; // Default to https:// if no protocol is specified
        }

        const newLink = {
            name: nameInput.value,
            url: url,
            notes: notesInput.value
        };

        fetch(apiURL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(newLink),
        })
        .then(response => response.json())
        .then(data => {
            console.log('Link added:', data);
            fetchLinks(); // Call the fetchLinks function to refresh the table
        })
        .catch(error => console.error('Error adding link:', error));
    }


    function displayLinks(links) {
        linksListElement.innerHTML = '';
        links.forEach(link => {
            const row = linksListElement.insertRow();
            const viewModeHTML = `
                <td><a href="${link.url}" target="_blank">${link.name}</a></td>
                <td>${link.notes || ''}</td>
                <td>
                    <button class="btn btn-info btn-sm me-1 edit-button" data-id="${link.id}">Edit</button>
                    <button class="btn btn-danger btn-sm delete-button" data-id="${link.id}">Delete</button>
                </td>
            `;
            row.innerHTML = viewModeHTML;
    
            // Attach event listeners to buttons
            row.querySelector('.edit-button').addEventListener('click', function() {
                this.closest('tr').innerHTML = `
                    <td><input type="text" class="form-control link-name" value="${link.name}" data-id="${link.id}"></td>
                    <td><input type="text" class="form-control link-url" value="${link.url}" data-id="${link.id}"></td>
                    <td><textarea class="form-control link-notes" data-id="${link.id}">${link.notes || ''}</textarea></td>
                    <td>
                        <button class="btn btn-success btn-sm me-1 save-button" data-id="${link.id}">Save</button>
                        <button class="btn btn-danger btn-sm delete-button" data-id="${link.id}">Delete</button>
                    </td>
                `;
                // Attach event listener to the save button
                row.querySelector('.save-button').addEventListener('click', function() {
                    updateLink(this.dataset.id, true);
                });
                // Reattach event listener to the delete button
                row.querySelector('.delete-button').addEventListener('click', () => deleteLink(link.id));
            });
            row.querySelector('.delete-button').addEventListener('click', () => deleteLink(link.id));
        });
    }

    // Initial fetch of links
    fetchLinks();
});
