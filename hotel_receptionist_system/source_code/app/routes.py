from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app import db
from app.models import Admin, Receptionist, Guest, Room, Booking, Payment
from app.auth import auth  # Import auth blueprint
from functools import wraps
from sqlalchemy import text, and_, not_, or_
from datetime import datetime, date, timedelta


# Create blueprints
main = Blueprint('main', __name__)
admin = Blueprint('admin', __name__, url_prefix='/admin')

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_type' not in session or session['user_type'] != 'admin':
            flash('Admin access required', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def get_dashboard_stats():
    today = date.today()
    
    # Get rooms occupied (rooms with active bookings)
    rooms_occupied = Booking.query.filter(
        Booking.status == 'Checked In'
    ).count()
    
    # Get check-ins for today
    checkins_today = Booking.query.filter(
        Booking.check_in == today,
        Booking.status.in_(['Confirmed', 'Checked In'])
    ).count()
    
    # Get check-outs for today
    checkouts_today = Booking.query.filter(
        Booking.check_out == today,
        Booking.status == 'Checked In'
    ).count()
    
    # Get pending arrivals (confirmed bookings with future check-in dates)
    pending_arrivals = Booking.query.filter(
        Booking.check_in > today,
        Booking.status == 'Confirmed'
    ).count()
    
    return {
        'rooms_occupied': rooms_occupied,
        'checkins_today': checkins_today,
        'checkouts_today': checkouts_today,
        'pending_arrivals': pending_arrivals
    }

@main.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if session.get('user_type') == 'admin':
        return redirect(url_for('admin.dashboard'))
    
    stats = get_dashboard_stats()
    return render_template('home.html', stats=stats)

@main.route('/receptionist/dashboard')
@login_required
def receptionist_dashboard():
    stats = get_dashboard_stats()
    return render_template('home.html', stats=stats)

@main.route('/guests')
@login_required
def guests():
    # Get all guests ordered by name alphabetically
    all_guests = Guest.query.order_by(Guest.name.asc()).all()
    return render_template('manage_guest.html', guests=all_guests)

@main.route('/edit_guest/<int:guest_id>')
@login_required
def edit_guest(guest_id):
    guest = Guest.query.get_or_404(guest_id)
    
    # Get all active bookings (Confirmed or Checked In)
    active_bookings = Booking.query.filter(
        Booking.guest_id == guest_id,
        Booking.status.in_(['Confirmed', 'Checked In'])
    ).all()
    
    available_rooms = Room.query.filter_by(status='vacant').all()
    
    # Add currently booked rooms to available rooms list
    for booking in active_bookings:
        if booking.room not in available_rooms:
            available_rooms.append(booking.room)
    
    return render_template('edit_guest.html', 
                         guest=guest, 
                         active_bookings=active_bookings,
                         available_rooms=available_rooms)

@main.route('/update_guest/<int:guest_id>', methods=['POST'])
@login_required
def update_guest(guest_id):
    guest = Guest.query.get_or_404(guest_id)
    
    try:
        guest.name = request.form.get('name')
        guest.email = request.form.get('email')
        guest.phone = request.form.get('phone')
        guest.id_document = request.form.get('id_document')
        
        db.session.commit()
        flash('Guest information updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating guest information: {str(e)}', 'danger')
    
    return redirect(url_for('main.guests'))

@main.route('/update_booking/<int:booking_id>', methods=['POST'])
@login_required
def update_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    try:
        # Update booking details
        booking.check_in = datetime.strptime(request.form.get('check_in'), '%Y-%m-%d').date()
        booking.check_out = datetime.strptime(request.form.get('check_out'), '%Y-%m-%d').date()
        
        # Update room if changed
        new_room_id = int(request.form.get('room_id'))
        if new_room_id != booking.room_id:
            old_room = Room.query.get(booking.room_id)
            new_room = Room.query.get(new_room_id)
            
            old_room.status = 'vacant'
            new_room.status = 'occupied'
            booking.room_id = new_room_id
        
        # Update payment if it exists
        if booking.payments:
            payment = booking.payments[0]
            payment.method = request.form.get('payment_method')
            payment.amount = float(request.form.get('amount'))
        
        db.session.commit()
        flash('Booking updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating booking: {str(e)}', 'danger')
    
    return redirect(url_for('main.edit_guest', guest_id=booking.guest_id))

@main.route('/checkin')
@login_required
def checkin():
    today = date.today()
    
    # Get today's pending check-ins
    todays_checkins = Booking.query.filter(
        Booking.check_in == today,
        Booking.status == 'Confirmed'
    ).all()
    
    # Get upcoming check-ins
    upcoming_checkins = Booking.query.filter(
        Booking.check_in > today,
        Booking.status == 'Confirmed'
    ).order_by(Booking.check_in.asc()).all()
    
    # Get check-in history (checked-in and checked-out bookings)
    checkin_history = Booking.query.filter(
        Booking.status.in_(['Checked In', 'Checked Out'])
    ).order_by(Booking.check_in.desc()).all()
    
    return render_template('check_in.html', 
                         todays_checkins=todays_checkins,
                         upcoming_checkins=upcoming_checkins,
                         checkin_history=checkin_history)

@main.route('/checkout')
@login_required
def checkout():
    today = date.today()
    
    # Get today's expected check-outs
    todays_checkouts = Booking.query.filter(
        Booking.check_out == today,
        Booking.status == 'Checked In'
    ).all()
    
    # Get upcoming check-outs (guests currently checked in)
    upcoming_checkouts = Booking.query.filter(
        Booking.check_out > today,
        Booking.status == 'Checked In'
    ).order_by(Booking.check_out.asc()).all()
    
    # Get check-out history
    checkout_history = Booking.query.filter(
        Booking.status == 'Checked Out'
    ).order_by(Booking.check_out.desc()).all()
    
    return render_template('check_out.html', 
                         todays_checkouts=todays_checkouts,
                         upcoming_checkouts=upcoming_checkouts,
                         checkout_history=checkout_history)

@main.route('/bookings')
@login_required
def bookings():
    # Get all vacant rooms for the dropdown
    vacant_rooms = Room.query.filter_by(status='vacant').all()
    
    # Get all bookings with related data
    bookings = Booking.query.all()
    
    # Get today's date for the date input min attribute
    today = date.today().strftime('%Y-%m-%d')
    
    return render_template('bookings.html', 
                          vacant_rooms=vacant_rooms, 
                          bookings=bookings, 
                          today=today)

@main.route('/create_booking', methods=['POST'])
@login_required
def create_booking():
    if request.method == 'POST':
        try:
            # Get guest information
            name = request.form.get('name')
            phone = request.form.get('phone')
            email = request.form.get('email')
            id_document = request.form.get('id_document')
            
            # Get booking dates
            check_in_date = datetime.strptime(request.form.get('check_in'), '%Y-%m-%d').date()
            check_out_date = datetime.strptime(request.form.get('check_out'), '%Y-%m-%d').date()
            
            # Check if guest already exists
            existing_guest = Guest.query.filter(
                (Guest.email == email) | (Guest.id_document == id_document)
            ).first()
            
            if existing_guest:
                # Check for date conflicts with active bookings
                active_bookings = Booking.query.filter(
                    Booking.guest_id == existing_guest.guest_id,
                    Booking.status.in_(['Confirmed', 'Checked In'])
                ).all()
                
                for booking in active_bookings:
                    # Check if there's any overlap in dates
                    if (check_in_date <= booking.check_out and 
                        check_out_date >= booking.check_in):
                        flash('This guest already has a booking during these dates. '
                              f'Existing booking: {booking.check_in.strftime("%Y-%m-%d")} '
                              f'to {booking.check_out.strftime("%Y-%m-%d")}', 'warning')
                        return redirect(url_for('main.bookings'))
                
                # If we get here, either no active bookings or no date conflicts
                guest = existing_guest
                # Update guest information
                guest.name = name
                guest.phone = phone
            else:
                # Create new guest
                guest = Guest(
                    name=name,
                    phone=phone,
                    email=email,
                    id_document=id_document
                )
                db.session.add(guest)
            
            # Get booking details
            room_id = request.form.get('room_id')
            total_amount = float(request.form.get('total_amount'))
            payment_method = request.form.get('payment_method')
            
            # Validate data
            if check_out_date <= check_in_date:
                flash('Check-out date must be after check-in date', 'danger')
                return redirect(url_for('main.bookings'))
            
            # Check if room is still available
            room = Room.query.get(room_id)
            if not room:
                flash('Selected room does not exist', 'danger')
                return redirect(url_for('main.bookings'))
                
            # Check if room is already booked for these dates
            existing_booking = Booking.query.filter(
                Booking.room_id == room_id,
                Booking.status.in_(['Confirmed', 'Checked In']),
                ~(
                    (Booking.check_out <= check_in_date) |  # Ends before new check-in
                    (Booking.check_in >= check_out_date)    # Starts after new check-out
                )
            ).first()
            
            if existing_booking:
                flash('This room is no longer available for the selected dates', 'danger')
                return redirect(url_for('main.bookings'))
            
            # Create booking
            booking = Booking(
                guest_id=guest.guest_id,
                room_id=room_id,
                check_in=check_in_date,
                check_out=check_out_date,
                status='Confirmed'
            )
            db.session.add(booking)
            
            # Update room status
            room.status = 'occupied'
            
            # First commit to get the booking_id
            db.session.commit()
            
            # Now create payment record with the committed booking_id
            payment = Payment(
                booking_id=booking.booking_id,
                amount=total_amount,
                payment_date=date.today(),
                method=payment_method
            )
            db.session.add(payment)
            
            # Commit the payment
            db.session.commit()
            
            flash('Booking created successfully!', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating booking: {str(e)}', 'danger')
        
        return redirect(url_for('main.bookings'))

@main.route('/cancel_booking/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    try:
        booking = Booking.query.get_or_404(booking_id)
        
        # Only allow cancellation if booking is in 'Confirmed' status
        if booking.status != 'Confirmed':
            flash('Only confirmed bookings can be cancelled', 'danger')
            return redirect(url_for('main.bookings'))
        
        # Update booking status
        booking.status = 'Cancelled'
        db.session.commit()
        
        flash('Booking cancelled successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error cancelling booking: {str(e)}', 'danger')
    
    return redirect(url_for('main.bookings'))

@main.route('/checkin_booking/<int:booking_id>', methods=['POST'])
@login_required
def checkin_booking(booking_id):
    try:
        booking = Booking.query.get_or_404(booking_id)
        
        # Only allow check-in if booking is in 'Confirmed' status
        if booking.status != 'Confirmed':
            flash('Only confirmed bookings can be checked in', 'danger')
            return redirect(url_for('main.checkin'))
        
        # Update booking status
        booking.status = 'Checked In'
        
        # Update room status
        room = Room.query.get(booking.room_id)
        room.status = 'occupied'
        
        db.session.commit()
        
        flash('Guest checked in successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error checking in: {str(e)}', 'danger')
    
    # Redirect back to check-in page instead of bookings
    if session.get('user_type') == 'admin':
        return redirect(url_for('admin.checkin'))
    return redirect(url_for('main.checkin'))

@main.route('/checkout_booking/<int:booking_id>', methods=['POST'])
@login_required
def checkout_booking(booking_id):
    try:
        booking = Booking.query.get_or_404(booking_id)
        
        # Only allow check-out if booking is in 'Checked In' status
        if booking.status != 'Checked In':
            flash('Only checked-in bookings can be checked out', 'danger')
            return redirect(url_for('main.checkout'))
        
        # Update booking status
        booking.status = 'Checked Out'
        
        # Update room status
        room = Room.query.get(booking.room_id)
        room.status = 'vacant'
        
        db.session.commit()
        
        flash('Guest checked out successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error checking out: {str(e)}', 'danger')
    
    # Redirect back to check-out page instead of bookings
    if session.get('user_type') == 'admin':
        return redirect(url_for('admin.checkout'))
    return redirect(url_for('main.checkout'))

@main.route('/check_room_availability', methods=['POST'])
@login_required
def check_room_availability():
    try:
        check_in = datetime.strptime(request.form.get('check_in'), '%Y-%m-%d').date()
        check_out = datetime.strptime(request.form.get('check_out'), '%Y-%m-%d').date()
        current_booking_id = request.form.get('current_booking_id')
        
        # Get all rooms
        all_rooms = Room.query.all()
        
        # Find rooms that are already booked for the selected dates
        query = Booking.query.filter(
            and_(
                Booking.status.in_(['Confirmed', 'Checked In']),
                not_(
                    or_(
                        Booking.check_out <= check_in,  # Booking ends before check-in
                        Booking.check_in >= check_out   # Booking starts after check-out
                    )
                )
            )
        )
        
        # Exclude current booking from the conflict check if editing
        if current_booking_id:
            query = query.filter(Booking.booking_id != int(current_booking_id))
        
        booked_room_ids = [room_id for (room_id,) in query.with_entities(Booking.room_id).all()]
        
        # Create list of available rooms
        available_rooms = []
        for room in all_rooms:
            if room.room_id not in booked_room_ids:
                available_rooms.append({
                    'room_id': room.room_id,
                    'room_type': room.room_type,
                    'price': float(room.price)
                })
        
        return jsonify({
            'success': True,
            'available_rooms': available_rooms
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    stats = get_dashboard_stats()
    return render_template('admin/dashboard.html', stats=stats)

@admin.route('/receptionists')
@login_required
@admin_required
def receptionists():
    all_receptionists = Receptionist.query.all()
    return render_template('admin/add_receptionist.html', receptionists=all_receptionists)

@admin.route('/add_receptionist', methods=['POST'])
@login_required
@admin_required
def add_receptionist():
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check if username already exists
        existing_user = Receptionist.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose another one.', 'danger')
            return redirect(url_for('admin.receptionists'))
        
        # Create new receptionist
        new_receptionist = Receptionist(name=name, username=username)
        new_receptionist.set_password(password)
        
        # Add to database
        db.session.add(new_receptionist)
        db.session.commit()
        
        flash('Receptionist added successfully!', 'success')
        return redirect(url_for('admin.receptionists'))

@admin.route('/delete_receptionist/<int:receptionist_id>', methods=['POST'])
@login_required
@admin_required
def delete_receptionist(receptionist_id):
    receptionist = Receptionist.query.get_or_404(receptionist_id)
    
    # Delete from database
    db.session.delete(receptionist)
    db.session.commit()
    
    flash('Receptionist deleted successfully!', 'success')
    return redirect(url_for('admin.receptionists'))

@admin.route('/rooms')
@login_required
@admin_required
def rooms():
    # Get all rooms with their current bookings and booking history
    all_rooms = Room.query.all()
    today = date.today()
    
    for room in all_rooms:
        # Get all bookings for this room (including history)
        room.bookings = Booking.query.filter(
            Booking.room_id == room.room_id
        ).all()
        
        # Check for active bookings (Confirmed or Checked In)
        active_booking = Booking.query.filter(
            Booking.room_id == room.room_id,
            Booking.status.in_(['Confirmed', 'Checked In']),
            Booking.check_out >= today
        ).first()
        
        if active_booking:
            if active_booking.status == 'Checked In':
                room.status = 'OCCUPIED'
            else:  # status is 'Confirmed'
                room.status = 'RESERVED'
        else:
            room.status = 'VACANT'
    
    return render_template('admin/add_rooms.html', rooms=all_rooms)

@admin.route('/add_room', methods=['POST'])
@login_required
@admin_required
def add_room():
    if request.method == 'POST':
        room_type = request.form.get('room_type')
        price = request.form.get('price')
        
        # Validate inputs
        if not room_type or not price:
            flash('Room type and price are required', 'danger')
            return redirect(url_for('admin.rooms'))
        
        try:
            # Create new room with status "VACANT"
            new_room = Room(
                room_type=room_type,
                price=price,
                status='VACANT'
            )
            
            # Add to database
            db.session.add(new_room)
            db.session.commit()
            
            flash('Room added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding room: {str(e)}', 'danger')
        
        return redirect(url_for('admin.rooms'))

@admin.route('/delete_room/<int:room_id>', methods=['POST'])
@login_required
@admin_required
def delete_room(room_id):
    try:
        room = Room.query.get_or_404(room_id)
        
        # Check for any active (non-cancelled) bookings
        active_bookings = Booking.query.filter(
            Booking.room_id == room_id,
            Booking.status.in_(['Confirmed', 'Checked In'])
        ).first()
        
        if active_bookings:
            flash('Cannot delete room with active bookings', 'danger')
            return redirect(url_for('admin.rooms'))
        
        # Delete the room's bookings that are cancelled or checked out
        Booking.query.filter(
            Booking.room_id == room_id,
            Booking.status.in_(['Cancelled', 'Checked Out'])
        ).delete()
        
        # Now delete the room
        db.session.delete(room)
        db.session.commit()
        flash('Room deleted successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting room: {str(e)}', 'danger')
    
    return redirect(url_for('admin.rooms'))

@admin.route('/bookings')
@login_required
@admin_required
def bookings():
    # Get all vacant rooms for the dropdown
    vacant_rooms = Room.query.filter_by(status='vacant').all()
    
    # Get all bookings with related data
    bookings = Booking.query.all()
    
    # Get today's date for the date input min attribute
    today = date.today().strftime('%Y-%m-%d')
    
    return render_template('bookings.html', 
                          vacant_rooms=vacant_rooms, 
                          bookings=bookings, 
                          today=today)

@admin.route('/guests')
@login_required
@admin_required
def guests():
    # Get all guests ordered by name alphabetically
    all_guests = Guest.query.order_by(Guest.name.asc()).all()
    return render_template('manage_guest.html', guests=all_guests)

@admin.route('/edit_guest/<int:guest_id>')
@login_required
@admin_required
def edit_guest(guest_id):
    guest = Guest.query.get_or_404(guest_id)
    
    # Get all active bookings (Confirmed or Checked In)
    active_bookings = Booking.query.filter(
        Booking.guest_id == guest_id,
        Booking.status.in_(['Confirmed', 'Checked In'])
    ).all()
    
    available_rooms = Room.query.filter_by(status='vacant').all()
    
    # Add currently booked rooms to available rooms list
    for booking in active_bookings:
        if booking.room not in available_rooms:
            available_rooms.append(booking.room)
    
    return render_template('edit_guest.html', 
                         guest=guest, 
                         active_bookings=active_bookings,
                         available_rooms=available_rooms)

@admin.route('/checkin')
@login_required
@admin_required
def checkin():
    today = date.today()
    
    # Get today's pending check-ins
    todays_checkins = Booking.query.filter(
        Booking.check_in == today,
        Booking.status == 'Confirmed'
    ).all()
    
    # Get upcoming check-ins
    upcoming_checkins = Booking.query.filter(
        Booking.check_in > today,
        Booking.status == 'Confirmed'
    ).order_by(Booking.check_in.asc()).all()
    
    # Get check-in history (checked-in and checked-out bookings)
    checkin_history = Booking.query.filter(
        Booking.status.in_(['Checked In', 'Checked Out'])
    ).order_by(Booking.check_in.desc()).all()
    
    return render_template('check_in.html', 
                         todays_checkins=todays_checkins,
                         upcoming_checkins=upcoming_checkins,
                         checkin_history=checkin_history)

@admin.route('/checkout')
@login_required
@admin_required
def checkout():
    today = date.today()
    
    # Get today's expected check-outs
    todays_checkouts = Booking.query.filter(
        Booking.check_out == today,
        Booking.status == 'Checked In'
    ).all()
    
    # Get upcoming check-outs (guests currently checked in)
    upcoming_checkouts = Booking.query.filter(
        Booking.check_out > today,
        Booking.status == 'Checked In'
    ).order_by(Booking.check_out.asc()).all()
    
    # Get check-out history
    checkout_history = Booking.query.filter(
        Booking.status == 'Checked Out'
    ).order_by(Booking.check_out.desc()).all()
    
    return render_template('check_out.html', 
                         todays_checkouts=todays_checkouts,
                         upcoming_checkouts=upcoming_checkouts,
                         checkout_history=checkout_history)

@main.route('/early_checkout_booking/<int:booking_id>', methods=['POST'])
@login_required
def early_checkout_booking(booking_id):
    try:
        booking = Booking.query.get_or_404(booking_id)
        today = date.today()
        
        # Only allow early check-out if booking is in 'Checked In' status
        if booking.status != 'Checked In':
            flash('Only checked-in bookings can be checked out', 'danger')
            return redirect(url_for('main.checkout'))
        
        # Update booking status and check-out date
        booking.status = 'Checked Out'
        booking.check_out = today
        
        # Update room status
        room = Room.query.get(booking.room_id)
        room.status = 'vacant'
        
        db.session.commit()
        
        flash('Guest checked out successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error checking out: {str(e)}', 'danger')
    
    # Redirect back to check-out page
    if session.get('user_type') == 'admin':
        return redirect(url_for('admin.checkout'))
    return redirect(url_for('main.checkout'))

@main.route('/delete_booking/<int:booking_id>', methods=['POST'])
@login_required
def delete_booking(booking_id):
    try:
        booking = Booking.query.get_or_404(booking_id)
        
        # Only allow deletion of cancelled bookings
        if booking.status != 'Cancelled':
            flash('Only cancelled bookings can be deleted', 'danger')
            return redirect(url_for('main.bookings'))
        
        # Delete associated payments first
        Payment.query.filter_by(booking_id=booking_id).delete()
        
        # Now delete the booking
        db.session.delete(booking)
        db.session.commit()
        
        flash('Booking deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting booking: {str(e)}', 'danger')
    
    return redirect(url_for('main.bookings'))

# Add the same route for admin
@admin.route('/delete_booking/<int:booking_id>', methods=['POST'])
@login_required
@admin_required
def delete_booking(booking_id):
    try:
        booking = Booking.query.get_or_404(booking_id)
        
        # Only allow deletion of cancelled bookings
        if booking.status != 'Cancelled':
            flash('Only cancelled bookings can be deleted', 'danger')
            return redirect(url_for('admin.bookings'))
        
        # Delete associated payments first
        Payment.query.filter_by(booking_id=booking_id).delete()
        
        # Now delete the booking
        db.session.delete(booking)
        db.session.commit()
        
        flash('Booking deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting booking: {str(e)}', 'danger')
    
    return redirect(url_for('admin.bookings'))

@admin.route('/update_room', methods=['POST'])
@login_required
@admin_required
def update_room():
    try:
        data = request.get_json()
        room_id = data.get('room_id')
        room_type = data.get('room_type')
        price = data.get('price')
        
        room = Room.query.get_or_404(room_id)
        room.room_type = room_type
        room.price = price
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Room updated successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400