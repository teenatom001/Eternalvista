// API Base URL
const API_URL = 'http://localhost:5000/api/vendors';

// Global variable for edit modal
let editModal;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function () {
    // Initialize Bootstrap modal
    editModal = new bootstrap.Modal(document.getElementById('editModal'));

    // Load vendors on page load
    getVendors();

    // Add form submit event listener
    document.getElementById('vendorForm').addEventListener('submit', function (e) {
        e.preventDefault();
        addVendor();
    });

    // Edit form submit
    document.getElementById('editVendorForm').addEventListener('submit', function (e) {
        e.preventDefault();
        saveVendorUpdate();
    });
});

/**
 * Show alert message to user
 */
function showAlert(message, type = 'success') {
    const alertContainer = document.getElementById('alertContainer');
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    alertContainer.appendChild(alertDiv);

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

/**
 * GET - Fetch and display all vendors
 */
async function getVendors() {
    try {
        const response = await fetch(API_URL);

        if (!response.ok) {
            throw new Error('Failed to fetch vendors');
        }

        const vendors = await response.json();
        displayVendors(vendors);
    } catch (error) {
        console.error('Error fetching vendors:', error);
        showAlert('Error loading vendors: ' + error.message, 'danger');
        document.getElementById('vendorTableBody').innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-danger">
                    <i class="bi bi-exclamation-triangle"></i> Error loading vendors
                </td>
            </tr>
        `;
    }
}

/**
 * Display vendors in the table
 */
function displayVendors(vendors) {
    const tableBody = document.getElementById('vendorTableBody');

    if (vendors.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-muted">
                    <i class="bi bi-inbox"></i> No vendors found. Add your first vendor above!
                </td>
            </tr>
        `;
        return;
    }

    tableBody.innerHTML = vendors.map(vendor => `
        <tr>
            <td>${vendor.vendor_id}</td>
            <td>${escapeHtml(vendor.name)}</td>
            <td><span class="badge bg-info">${escapeHtml(vendor.service_type)}</span></td>
            <td>${escapeHtml(vendor.price_range)}</td>
            <td>${escapeHtml(vendor.contact)}</td>
            <td>
                <button class="btn btn-sm btn-warning" onclick="editVendor(${vendor.vendor_id})" title="Edit">
                    <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-danger" onclick="deleteVendor(${vendor.vendor_id})" title="Delete">
                    <i class="bi bi-trash"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

/**
 * POST - Add a new vendor
 */
async function addVendor() {
    const name = document.getElementById('vendorName').value.trim();
    const serviceType = document.getElementById('serviceType').value;
    const priceRange = document.getElementById('priceRange').value.trim();
    const contact = document.getElementById('contact').value.trim();

    // Client-side validation
    if (!name || !serviceType || !priceRange || !contact) {
        showAlert('Please fill in all required fields', 'warning');
        return;
    }

    const vendorData = {
        name: name,
        service_type: serviceType,
        price_range: priceRange,
        contact: contact
    };

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(vendorData)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to add vendor');
        }

        showAlert('Vendor added successfully!', 'success');
        document.getElementById('vendorForm').reset();
        getVendors(); // Refresh the vendor list
    } catch (error) {
        console.error('Error adding vendor:', error);
        showAlert('Error adding vendor: ' + error.message, 'danger');
    }
}

/**
 * Prepare vendor for editing
 */
async function editVendor(vendorId) {
    try {
        const response = await fetch(API_URL);
        const vendors = await response.json();
        const vendor = vendors.find(v => v.vendor_id === vendorId);

        if (!vendor) {
            showAlert('Vendor not found', 'danger');
            return;
        }

        // Populate edit form
        document.getElementById('editVendorId').value = vendor.vendor_id;
        document.getElementById('editVendorName').value = vendor.name;
        document.getElementById('editServiceType').value = vendor.service_type;
        document.getElementById('editPriceRange').value = vendor.price_range;
        document.getElementById('editContact').value = vendor.contact;

        // Show modal
        editModal.show();
    } catch (error) {
        console.error('Error loading vendor for edit:', error);
        showAlert('Error loading vendor details', 'danger');
    }
}

/**
 * PUT - Update vendor
 */
async function updateVendor(vendorId) {
    const name = document.getElementById('editVendorName').value.trim();
    const serviceType = document.getElementById('editServiceType').value;
    const priceRange = document.getElementById('editPriceRange').value.trim();
    const contact = document.getElementById('editContact').value.trim();

    if (!name || !serviceType || !priceRange || !contact) {
        showAlert('Please fill in all required fields', 'warning');
        return;
    }

    const vendorData = {
        name: name,
        service_type: serviceType,
        price_range: priceRange,
        contact: contact
    };

    try {
        const response = await fetch(`${API_URL}/${vendorId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(vendorData)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to update vendor');
        }

        showAlert('Vendor updated successfully!', 'success');
        editModal.hide();
        getVendors(); // Refresh the vendor list
    } catch (error) {
        console.error('Error updating vendor:', error);
        showAlert('Error updating vendor: ' + error.message, 'danger');
    }
}

/**
 * Save vendor update (called from modal button)
 */
function saveVendorUpdate() {
    const vendorId = document.getElementById('editVendorId').value;
    updateVendor(vendorId);
}

/**
 * DELETE - Delete vendor
 */
async function deleteVendor(vendorId) {
    // Confirm deletion
    if (!confirm('Are you sure you want to delete this vendor?')) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/${vendorId}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to delete vendor');
        }

        showAlert('Vendor deleted successfully!', 'success');
        getVendors(); // Refresh the vendor list
    } catch (error) {
        console.error('Error deleting vendor:', error);
        showAlert('Error deleting vendor: ' + error.message, 'danger');
    }
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}
