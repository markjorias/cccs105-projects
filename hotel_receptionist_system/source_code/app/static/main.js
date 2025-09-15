// Search functionality for tables
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keyup', function() {
            const searchValue = this.value.toLowerCase();
            const rows = document.querySelectorAll('.data-table tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchValue) ? '' : 'none';
            });
        });
    }

    // Room filtering functionality
    const filterButtons = document.querySelectorAll('.filter-btn');
    const roomRows = document.querySelectorAll('.room-row');
    
    if (filterButtons.length > 0) {
        filterButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Remove active class from all buttons
                filterButtons.forEach(btn => btn.classList.remove('active'));
                // Add active class to clicked button
                this.classList.add('active');
                
                const filter = this.getAttribute('data-filter');
                roomRows.forEach(row => {
                    if (filter === 'all') {
                        row.style.display = '';
                    } else {
                        // Get the status from the status badge span
                        const statusBadge = row.querySelector('.status-badge');
                        const rowStatus = statusBadge ? statusBadge.textContent.trim().toLowerCase() : '';
                        row.style.display = rowStatus === filter.toLowerCase() ? '' : 'none';
                    }
                });
            });
        });
    }

    // Add fade effect when checking out
    document.querySelectorAll('form').forEach(form => {
        if (form.action.includes('checkout_booking') || form.action.includes('early_checkout_booking')) {
            form.addEventListener('submit', function(e) {
                const row = this.closest('.booking-row');
                row.style.opacity = '0.5';
                row.style.backgroundColor = '#f8f9fa';
                const button = this.querySelector('button');
                button.disabled = true;
                button.textContent = 'Processing...';
            });
        }
    });
});

// Login form handling
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            const button = document.querySelector('.login-button');
            if (button) {
                button.classList.add('loading');
                button.textContent = '';
            }
        });
    }
});

// Booking system functionality
document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const checkInInput = document.getElementById('check_in');
    const checkOutInput = document.getElementById('check_out');
    const roomSelect = document.getElementById('room_id');
    const roomHelp = document.getElementById('room-help');
    const totalInput = document.getElementById('total_amount');
    const guestSearch = document.getElementById('guestSearch');
    const filterButtons = document.querySelectorAll('.filter-btn');
    
    // Check room availability
    async function checkAvailability() {
        if (!checkInInput || !checkOutInput || !roomSelect || !roomHelp) return;

        const checkIn = checkInInput.value;
        const checkOut = checkOutInput.value;
        
        if (!checkIn || !checkOut) {
            roomSelect.disabled = true;
            roomSelect.innerHTML = '<option value="">Select dates first...</option>';
            roomHelp.textContent = 'Please select check-in and check-out dates to see available rooms.';
            return;
        }
        
        // Validate dates
        const checkInDate = new Date(checkIn);
        const checkOutDate = new Date(checkOut);
        
        if (checkOutDate <= checkInDate) {
            roomSelect.disabled = true;
            roomSelect.innerHTML = '<option value="">Invalid dates</option>';
            roomHelp.textContent = 'Check-out date must be after check-in date.';
            return;
        }
        
        try {
            const formData = new FormData();
            formData.append('check_in', checkIn);
            formData.append('check_out', checkOut);
            
            const response = await fetch('/check_room_availability', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                roomSelect.innerHTML = '<option value="">Select a room...</option>';
                
                if (data.available_rooms.length === 0) {
                    roomSelect.disabled = true;
                    roomHelp.textContent = 'No rooms available for selected dates.';
                } else {
                    roomSelect.disabled = false;
                    roomHelp.textContent = `${data.available_rooms.length} room(s) available for selected dates.`;
                    
                    data.available_rooms.forEach(room => {
                        const option = document.createElement('option');
                        option.value = room.room_id;
                        option.setAttribute('data-price', room.price);
                        option.textContent = `Room ${room.room_id} - ${room.room_type} (${room.price}/night)`;
                        roomSelect.appendChild(option);
                    });
                }
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            roomSelect.disabled = true;
            roomSelect.innerHTML = '<option value="">Error checking availability</option>';
            roomHelp.textContent = 'Error: ' + error.message;
        }
    }
    
    // Calculate total amount
    function calculateTotal() {
        if (!checkInInput || !checkOutInput || !roomSelect || !totalInput) return;

        const checkIn = new Date(checkInInput.value);
        const checkOut = new Date(checkOutInput.value);
        
        if (checkIn && checkOut && roomSelect.value && checkOut > checkIn) {
            const selectedOption = roomSelect.options[roomSelect.selectedIndex];
            const pricePerNight = parseFloat(selectedOption.getAttribute('data-price'));
            const nights = Math.ceil((checkOut - checkIn) / (1000 * 60 * 60 * 24));
            totalInput.value = (pricePerNight * nights).toFixed(2);
        } else {
            totalInput.value = '';
        }
    }

    // Search functionality
    function handleSearch() {
        if (!guestSearch) return;

        const searchTerm = guestSearch.value.toLowerCase();
        const bookingRows = document.querySelectorAll('.booking-row');
        const noBookingsRow = document.getElementById('no-bookings-row');
        let visibleRows = 0;

        bookingRows.forEach(row => {
            const guestName = row.getAttribute('data-guest-name');
            if (guestName.includes(searchTerm)) {
                row.style.display = '';
                visibleRows++;
            } else {
                row.style.display = 'none';
            }
        });

        if (noBookingsRow) {
            noBookingsRow.style.display = visibleRows === 0 ? '' : 'none';
        }
    }

    // Filter functionality
    function handleFilter(filterValue) {
        const bookingRows = document.querySelectorAll('.booking-row');
        bookingRows.forEach(row => {
            if (filterValue === 'all' || row.classList.contains(filterValue.toLowerCase().replace(' ', '-'))) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }

    // Event listeners
    if (checkInInput) {
        checkInInput.addEventListener('change', () => {
            checkAvailability();
            calculateTotal();
        });
    }
    
    if (checkOutInput) {
        checkOutInput.addEventListener('change', () => {
            checkAvailability();
            calculateTotal();
        });
    }
    
    if (roomSelect) {
        roomSelect.addEventListener('change', calculateTotal);
    }

    if (guestSearch) {
        guestSearch.addEventListener('input', handleSearch);
    }

    filterButtons.forEach(button => {
        button.addEventListener('click', () => {
            filterButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            handleFilter(button.getAttribute('data-filter'));
        });
    });
});

// Clear search function
function clearSearch() {
    const searchInput = document.getElementById('guestSearch');
    if (searchInput) {
        searchInput.value = '';
        searchInput.dispatchEvent(new Event('input'));
    }
} 

document.addEventListener('DOMContentLoaded', function() {
    const table = document.querySelector('.data-table');
    if (!table) return;
    
    // Format price to 2 decimal places
    function formatPrice(price) {
        return parseFloat(price).toFixed(2);
    }
    
    table.addEventListener('click', function(e) {
        if (e.target.classList.contains('edit-btn')) {
            const row = e.target.closest('tr');
            startEditing(row);
        } else if (e.target.classList.contains('save-btn')) {
            const row = e.target.closest('tr');
            saveChanges(row);
        } else if (e.target.classList.contains('cancel-btn')) {
            const row = e.target.closest('tr');
            cancelEditing(row);
        }
    });

    function startEditing(row) {
        // Hide display values and show input fields
        row.querySelectorAll('.display-value').forEach(span => span.style.display = 'none');
        row.querySelectorAll('.edit-input').forEach(input => {
            input.style.display = '';
            // Format price input to 2 decimal places
            if (input.closest('td').classList.contains('price-cell')) {
                input.value = formatPrice(input.value);
            }
        });
        
        // Show/hide buttons
        row.querySelector('.edit-btn').style.display = 'none';
        row.querySelector('.save-btn').style.display = '';
        row.querySelector('.cancel-btn').style.display = '';
    }

    function cancelEditing(row) {
        // Show display values and hide input fields
        row.querySelectorAll('.display-value').forEach(span => span.style.display = '');
        row.querySelectorAll('.edit-input').forEach(input => {
            input.style.display = 'none';
            // Reset input values to original and format price
            const originalValue = input.closest('td').querySelector('.display-value').textContent.trim();
            if (input.closest('td').classList.contains('price-cell')) {
                input.value = formatPrice(originalValue);
            } else {
                input.value = originalValue;
            }
        });
        
        // Show/hide buttons
        row.querySelector('.edit-btn').style.display = '';
        row.querySelector('.save-btn').style.display = 'none';
        row.querySelector('.cancel-btn').style.display = 'none';
    }

    function saveChanges(row) {
        const roomId = row.dataset.roomId;
        const roomType = row.querySelector('.room-type-cell .edit-input').value;
        const price = formatPrice(row.querySelector('.price-cell .edit-input').value);

        // Send AJAX request to update the room
        fetch('/admin/update_room', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                room_id: roomId,
                room_type: roomType,
                price: price
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update display values
                row.querySelector('.room-type-cell .display-value').textContent = roomType;
                row.querySelector('.price-cell .display-value').textContent = price;
                
                // Reset to display mode
                row.querySelectorAll('.display-value').forEach(span => span.style.display = '');
                row.querySelectorAll('.edit-input').forEach(input => input.style.display = 'none');
                
                // Show/hide buttons
                row.querySelector('.edit-btn').style.display = '';
                row.querySelector('.save-btn').style.display = 'none';
                row.querySelector('.cancel-btn').style.display = 'none';

                // Show success message
                alert('Room updated successfully!');
            } else {
                alert('Failed to update room: ' + (data.message || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to update room. Please try again.');
        });
    }

    // Add input event listener to format price as user types
    table.addEventListener('input', function(e) {
        if (e.target.classList.contains('edit-input') && e.target.closest('td').classList.contains('price-cell')) {
            const value = e.target.value;
            if (value) {
                // Only format if there's a value and it's a valid number
                const numValue = parseFloat(value);
                if (!isNaN(numValue)) {
                    // Keep cursor position
                    const cursorPos = e.target.selectionStart;
                    const oldLength = value.length;
                    e.target.value = formatPrice(value);
                    const newLength = e.target.value.length;
                    // Adjust cursor position if length changed
                    if (cursorPos !== undefined) {
                        e.target.setSelectionRange(cursorPos + (newLength - oldLength), cursorPos + (newLength - oldLength));
                    }
                }
            }
        }
    });
});