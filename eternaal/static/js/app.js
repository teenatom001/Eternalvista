document.addEventListener('DOMContentLoaded', () => {
    // Determine which page we are on and load relevant data
    if (document.getElementById('admin-dest-list')) {
        // Admin Page
        loadAdminDestinations();
        setupAdminForms();
        loadAdminVenues();
        loadAdminBookings();
        loadAdminUsers(); // Add this line
    } else if (document.getElementById('destinations-list')) {
        // Index Page
        loadDestinations();
        setupBookingForm();
        loadUserBookings(); // Add this
    }
});

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
function showAlert(msg) {
    // Simple alert for beginner level
    alert(msg);
}

// --- CUSTOMER FUNCTIONS ---

async function loadDestinations() {
    const list = document.getElementById('destinations-list');
    try {
        const dests = await apiCall('/api/destinations');
        list.innerHTML = '';
        dests.forEach(d => {
            const div = document.createElement('div');
            div.className = 'item-card';
            div.innerHTML = `
                <h3>${d.name}</h3>
                ${d.image_url ? `<img src="${d.image_url}" alt="Dest Image">` : ''}
                <p>${d.description}</p>
                <p>Status: <strong>${d.availability ? 'Available' : 'Unavailable'}</strong></p>
                <button onclick="selectDestination(${d.id}, '${d.name}')" ${!d.availability ? 'disabled' : ''}>
                    ${d.availability ? 'View Venues' : 'Unavailable'}
                </button>
            `;
            list.appendChild(div);
        });
    } catch (e) { list.innerHTML = 'Error loading destinations'; }
}

async function selectDestination(id, name) {
    document.getElementById('selected-destination-name').innerText = name;
    document.getElementById('venues-section').style.display = 'block';
    document.getElementById('venues-section').scrollIntoView();

    const list = document.getElementById('venues-list');
    list.innerHTML = 'Loading...';

    try {
        const venues = await apiCall(`/api/venues?destination_id=${id}`);
        list.innerHTML = '';
        if (venues.length === 0) list.innerHTML = '<p>No venues found.</p>';

        venues.forEach(v => {
            const div = document.createElement('div');
            div.className = 'item-card';
            div.innerHTML = `
                <h4>${v.name}</h4>
                ${v.image_url ? `<img src="${v.image_url}" alt="Venue Image">` : ''}
                <p>Capacity: ${v.capacity}, Price: $${v.price}</p>
                <button onclick="showBookingForm(${id}, ${v.id}, '${v.name}', ${v.price})" ${!v.availability ? 'disabled' : ''}>
                    ${v.availability ? 'Book This Venue' : 'Fully Booked'}
                </button>
            `;
            list.appendChild(div);
        });
    } catch (e) { list.innerHTML = 'Error loading venues'; }
}

function showBookingForm(destId, venueId, venueName, price) {
    document.getElementById('book-dest-id').value = destId;
    document.getElementById('book-venue-id').value = venueId;
    document.getElementById('book-venue-name-display').innerText = venueName;
    document.getElementById('book-venue-price-display').innerText = '$' + price;

    document.getElementById('booking-section').style.display = 'block';
    document.getElementById('booking-section').scrollIntoView();
}

function setupBookingForm() {
    const form = document.getElementById('booking-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const data = {
            destination_id: document.getElementById('book-dest-id').value,
            venue_id: document.getElementById('book-venue-id').value,
            customer_name: document.getElementById('book-customer-name').value,
            customer_email: document.getElementById('book-customer-email').value,
            booking_date: document.getElementById('book-date').value
        };

        const res = await apiCall('/api/bookings', 'POST', data);
        if (res.message) {
            showAlert('Booking Successful!');
            document.getElementById('booking-section').style.display = 'none';
        } else {
            showAlert('Error: ' + res.error);
        }
    });
}

// --- USER BOOKINGS ---
async function loadUserBookings() {
    const container = document.getElementById('user-bookings-container');
    if (!container) return; // Only exists if user is logged in

    try {
        const bookings = await apiCall('/api/bookings');
        const list = document.getElementById('user-bookings-list');
        list.innerHTML = '';

        if (bookings.length === 0) {
            list.innerHTML = '<p class="text-muted">You have no bookings yet.</p>';
            return;
        }

        bookings.forEach(b => {
            const div = document.createElement('div');
            div.className = 'card mb-3';
            div.innerHTML = `
                <div class="card-body">
                    <h5 class="card-title">${b.dest_name} - ${b.venue_name}</h5>
                    <p class="card-text">
                        <strong>Date:</strong> ${b.booking_date}<br>
                        <strong>Status:</strong> <span class="badge ${getStatusBadge(b.status)}">${b.status.toUpperCase()}</span>
                    </p>
                </div>
             `;
            list.appendChild(div);
        });
    } catch (e) {
        console.error('Error loading bookings', e);
    }
}

function getStatusBadge(status) {
    if (status === 'confirmed' || status === 'accepted') return 'bg-success';
    if (status === 'pending') return 'bg-warning text-dark';
    if (status === 'cancelled' || status === 'rejected') return 'bg-danger';
    return 'bg-secondary';
}

// --- ADMIN FUNCTIONS ---

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

async function updateBooking(id, status) {
    await apiCall(`/api/bookings/${id}`, 'PUT', { status });
    loadAdminBookings();
}

async function deleteBooking(id) {
    if (confirm('Delete this booking?')) {
        await apiCall(`/api/bookings/${id}`, 'DELETE');
        loadAdminBookings();
    }
}

// --- USER MANAGEMENT ---
async function loadAdminUsers() {
    const tableBody = document.getElementById('users-table-body');
    if (!tableBody) return;

    tableBody.innerHTML = '<tr><td colspan="4">Loading...</td></tr>';

    try {
        const users = await apiCall('/api/users');
        tableBody.innerHTML = '';

        users.forEach(u => {
            tableBody.innerHTML += `
                <tr>
                    <td>${u.id}</td>
                    <td>${u.username}</td>
                    <td>${u.role}</td>
                    <td>
                        <button onclick="deleteUser(${u.id}, '${u.username}')" class="btn-delete" ${u.role === 'admin' ? 'disabled title="Cannot delete admin"' : ''}>
                            <i class="fas fa-trash-alt"></i> Delete
                        </button>
                    </td>
                </tr>
            `;
        });
    } catch (e) {
        tableBody.innerHTML = '<tr><td colspan="4">Error loading users</td></tr>';
    }
}

async function deleteUser(id, username) {
    if (confirm(`Are you sure you want to delete user "${username}"? This cannot be undone.`)) {
        const res = await apiCall(`/api/users/${id}`, 'DELETE');
        if (res.message) {
            alert(res.message);
            loadAdminUsers();
        } else {
            alert('Error: ' + (res.error || 'Unknown error'));
        }
    }
}

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

function openEditDest(id, name, desc, avail) {
    document.getElementById('edit-dest-id').value = id;
    document.getElementById('edit-dest-name').value = name;
    document.getElementById('edit-dest-desc').value = desc;
    document.getElementById('edit-dest-avail').checked = avail;
    document.getElementById('edit-dest-container').style.display = 'block';
    document.getElementById('edit-dest-container').scrollIntoView();
}

async function deleteDest(id) {
    if (confirm('Delete destination?')) {
        await apiCall(`/api/destinations/${id}`, 'DELETE');
        loadAdminDestinations();
    }
}

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

async function deleteVenue(id) {
    if (confirm('Delete venue?')) {
        await apiCall(`/api/venues/${id}`, 'DELETE');
        loadAdminVenues();
    }
}

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
