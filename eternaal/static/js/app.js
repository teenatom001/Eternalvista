// Initialize the app when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    // Determine which page we are on and load relevant data
    if (document.getElementById('admin-dest-list')) {
        // Admin Page
        loadAdminDestinations();
        setupAdminForms();
        loadAdminVenues();
        loadAdminBookings();
    } else if (document.getElementById('destinations-list')) {
        // Index Page
        loadDestinations();
        setupBookingForm();
    }
});

// Helper function to perform API calls (GET, POST, PUT, DELETE)
// --- API HELPER ---
async function apiCall(url, method = 'GET', body = null) {
    const options = { method };
    if (body instanceof FormData) {
        options.body = body;
    } else if (body) {
        options.headers = { 'Content-Type': 'application/json' };
        options.body = JSON.stringify(body);
    }
    const res = await fetch(url, options);
    return await res.json();
}

// --- BASIC ALERT ---
// Simple wrapper for alert messages (can be replaced with a nicer UI later)
function showAlert(msg) {
    // Simple alert for beginner level
    alert(msg);
}


// Functions that power the admin dashboard (loading data, handling forms, etc.)
// --- ADMIN FUNCTIONS ---

// Load all bookings for the admin view, separating pending and historical bookings
async function loadAdminBookings() {
    const pendingBody = document.getElementById('bookings-pending-body');
    const historyBody = document.getElementById('bookings-history-body');
    if (!pendingBody) return;

    pendingBody.innerHTML = '<tr><td colspan="5">Loading...</td></tr>';

    const bookings = await apiCall('/api/bookings');
    pendingBody.innerHTML = '';
    historyBody.innerHTML = '';

    bookings.forEach(b => {
        if (b.status === 'pending') {
            pendingBody.innerHTML += `
                <tr>
                    <td>${b.id}</td>
                    <td>${b.customer_name} (${b.customer_email})</td>
                    <td>${b.venue_name}</td>
                    <td>${b.booking_date}</td>
                    <td>
                        <button onclick="updateBooking(${b.id}, 'confirmed')">Confirm</button>
                        <button onclick="updateBooking(${b.id}, 'cancelled')" class="btn-danger">Cancel</button>
                    </td>
                </tr>
            `;
        } else {
            historyBody.innerHTML += `
                <tr>
                    <td>${b.id}</td>
                    <td>${b.customer_name}</td>
                    <td>${b.venue_name}</td>
                    <td>${b.booking_date}</td>
                    <td>${b.status}</td>
                    <td><button onclick="deleteBooking(${b.id})" class="btn-danger">Delete</button></td>
                </tr>
            `;
        }
    });
}

// Update a booking's status (e.g., confirm or cancel) and refresh the list
async function updateBooking(id, status) {
    await apiCall(`/api/bookings/${id}`, 'PUT', { status });
    loadAdminBookings();
}

// Delete a booking after user confirmation and refresh the list
async function deleteBooking(id) {
    if (confirm('Delete this booking?')) {
        await apiCall(`/api/bookings/${id}`, 'DELETE');
        loadAdminBookings();
    }
}

// Load all destinations for the admin page and populate edit/delete controls
async function loadAdminDestinations() {
    const list = document.getElementById('admin-dest-list');
    const dests = await apiCall('/api/destinations');
    list.innerHTML = ''; // clear

    dests.forEach(d => {
        const div = document.createElement('div');
        div.className = 'admin-card'; // New class

        div.innerHTML = `
            <div class="admin-card-content">
                <h3 style="margin-top:0;">${d.name} <small style="font-weight:normal; font-size:0.8em; color:#7f8c8d;">- ${d.availability ? 'Available' : 'Unavailable'}</small></h3>
                <p style="margin-bottom:0; color:#555;">${d.description}</p>
            </div>
            <div class="admin-card-actions">
                <button onclick="openEditDest(${d.id}, '${d.name}', '${d.description.replace(/'/g, "\\'")}', ${d.availability})" class="btn-edit" title="Edit">
                    <i class="fas fa-edit"></i>
                </button>
                <button onclick="deleteDest(${d.id})" class="btn-delete" title="Delete">
                    <i class="fas fa-trash-alt"></i>
                </button>
            </div>
        `;
        list.appendChild(div);
    });

    // Also populate dropdowns
    populateDestDropdowns(dests);
}

// Fill destination <select> elements in the admin forms (add venue, filter venues)
function populateDestDropdowns(dests) {
    const selects = [document.getElementById('new-venue-dest-select'), document.getElementById('admin-venue-filter-dest')];
    selects.forEach(sel => {
        if (!sel) return;
        const current = sel.value;
        // Keep first option if it exists
        const first = sel.options.length > 0 ? sel.options[0] : null;
        sel.innerHTML = '';

        if (first) {
            sel.appendChild(first);
        } else {
            // Create a default option if none existed
            const defaultOpt = document.createElement('option');
            defaultOpt.value = "";
            defaultOpt.innerText = "Select Destination";
            sel.appendChild(defaultOpt);
        }

        dests.forEach(d => {
            const opt = document.createElement('option');
            opt.value = d.id;
            opt.innerText = d.name;
            sel.appendChild(opt);
        });

        if (current) sel.value = current;
    });
}

// Open the edit‑destination modal and pre‑fill fields with the selected destination's data
function openEditDest(id, name, desc, avail) {
    document.getElementById('edit-dest-id').value = id;
    document.getElementById('edit-dest-name').value = name;
    document.getElementById('edit-dest-desc').value = desc;
    document.getElementById('edit-dest-avail').checked = avail;
    document.getElementById('edit-dest-container').style.display = 'block';
    document.getElementById('edit-dest-container').scrollIntoView();
}

// Prompt for confirmation and delete a destination, then refresh the list
async function deleteDest(id) {
    if (confirm('Delete destination?')) {
        await apiCall(`/api/destinations/${id}`, 'DELETE');
        loadAdminDestinations();
    }
}

// Load venues for the admin page, optionally filtered by destination, and render edit/delete controls
async function loadAdminVenues() {
    const list = document.getElementById('admin-venue-list');
    const filter = document.getElementById('admin-venue-filter-dest').value;
    let url = '/api/venues';
    if (filter) url += `?destination_id=${filter}`;

    const venues = await apiCall(url);
    list.innerHTML = '';

    venues.forEach(v => {
        const div = document.createElement('div');
        div.className = 'admin-card'; // New class

        div.innerHTML = `
            <div class="admin-card-content">
                <h3 style="margin-top:0;">${v.name}</h3>
                <p style="margin:0; color:#7f8c8d;">${v.destination_name}</p>
                <p style="margin:0;">Capacity: <strong>${v.capacity}</strong> | Price: <strong>$${v.price}</strong></p>
            </div>
            <div class="admin-card-actions">
                <button onclick="openEditVenue(${v.id}, '${v.name}', ${v.capacity}, ${v.price}, ${v.availability}, ${v.destination_id})" class="btn-edit" title="Edit">
                    <i class="fas fa-edit"></i>
                </button>
                <button onclick="deleteVenue(${v.id})" class="btn-delete" title="Delete">
                    <i class="fas fa-trash-alt"></i>
                </button>
            </div>
        `;
        list.appendChild(div);
    });
}

// Open the edit‑venue modal and fill it with the selected venue's details
function openEditVenue(id, name, cap, price, avail, destId) {
    document.getElementById('edit-venue-id').value = id;
    document.getElementById('edit-venue-dest-id').value = destId;
    document.getElementById('edit-venue-name').value = name;
    document.getElementById('edit-venue-capacity').value = cap;
    document.getElementById('edit-venue-price').value = price;
    document.getElementById('edit-venue-avail').checked = avail;
    document.getElementById('edit-venue-container').style.display = 'block';
    document.getElementById('edit-venue-container').scrollIntoView();
}

// Confirm and delete a venue, then reload the venue list
async function deleteVenue(id) {
    if (confirm('Delete venue?')) {
        await apiCall(`/api/venues/${id}`, 'DELETE');
        loadAdminVenues();
    }
}

// Attach event listeners to all admin forms (add/edit destination, add/edit venue)
function setupAdminForms() {
    // Add Destination
    document.getElementById('add-destination-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const data = {
            name: document.getElementById('new-dest-name').value,
            description: document.getElementById('new-dest-desc').value,
            availability: document.getElementById('new-dest-avail').checked
            // image upload skipped for simple JSON API
        };

        await apiCall('/api/destinations', 'POST', data);
        loadAdminDestinations();
        e.target.reset();
        alert('Destination Added');
    });

    // Edit Destination
    document.getElementById('edit-dest-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const id = document.getElementById('edit-dest-id').value;
        const data = {
            name: document.getElementById('edit-dest-name').value,
            description: document.getElementById('edit-dest-desc').value,
            availability: document.getElementById('edit-dest-avail').checked
        };

        await apiCall(`/api/destinations/${id}`, 'PUT', data);
        document.getElementById('edit-dest-container').style.display = 'none';
        loadAdminDestinations();
        alert('Destination Updated');
    });

    // Add Venue
    document.getElementById('add-venue-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const data = {
            destination_id: document.getElementById('new-venue-dest-select').value,
            name: document.getElementById('new-venue-name').value,
            capacity: parseInt(document.getElementById('new-venue-capacity').value),
            price: parseFloat(document.getElementById('new-venue-price').value)
        };

        await apiCall('/api/venues', 'POST', data);
        loadAdminVenues();
        e.target.reset();
        alert('Venue Added');
    });

    document.getElementById('edit-venue-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const id = document.getElementById('edit-venue-id').value;
        const data = {
            destination_id: document.getElementById('edit-venue-dest-id').value,
            name: document.getElementById('edit-venue-name').value,
            capacity: parseInt(document.getElementById('edit-venue-capacity').value),
            price: parseFloat(document.getElementById('edit-venue-price').value),
            availability: document.getElementById('edit-venue-avail').checked
        };

        await apiCall(`/api/venues/${id}`, 'PUT', data);
        document.getElementById('edit-venue-container').style.display = 'none';
        loadAdminVenues();
        alert('Venue Updated');
    });
}
