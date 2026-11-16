import os
import traceback
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from database import get_db, init_db
from models import haversine_distance_km, compare_swap_values

app = Flask(__name__)
app.secret_key = 'ecoswap-indian-sustainable-fashion-key-2024'

@app.errorhandler(Exception)
def handle_exception(e):
    traceback.print_exc()
    return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

# Initialize database on startup
with app.app_context():
    init_db()

def get_logged_in_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    conn = get_db()
    user = conn.execute('SELECT id, name, email, phone, city, area, avatar_url, swaps_completed, joined_date FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return dict(user) if user else None

@app.route('/')
def index():
    return render_template('index.html')

# ==========================================
# AUTHENTICATION (LOGIN / REGISTER / LOGOUT)
# ==========================================

@app.route('/api/me', methods=['GET'])
def api_me():
    user = get_logged_in_user()
    if user:
        return jsonify({'logged_in': True, 'user': user})
    return jsonify({'logged_in': False, 'user': None})

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()

    if not email or not password:
        return jsonify({'error': 'Please enter both Email and Password'}), 400

    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE LOWER(email) = ?', (email,)).fetchone()
    conn.close()

    if not user or user['password'] != password:
        return jsonify({'error': 'Invalid Email or Password. (Hint: Demo password is 123)'}), 401

    session['user_id'] = user['id']
    user_dict = {
        'id': user['id'],
        'name': user['name'],
        'email': user['email'],
        'phone': user['phone'],
        'city': user['city'],
        'area': user['area'],
        'avatar_url': user['avatar_url'],
        'swaps_completed': user['swaps_completed'],
        'joined_date': user['joined_date']
    }
    return jsonify({'success': True, 'user': user_dict})

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()
    phone = data.get('phone', '').strip()
    city = data.get('city', 'Bangalore').strip()
    area = data.get('area', 'Indiranagar').strip()

    if not name or not email or not password:
        return jsonify({'error': 'Name, Email, and Password are required'}), 400

    conn = get_db()
    existing = conn.execute('SELECT id FROM users WHERE LOWER(email) = ?', (email,)).fetchone()
    if existing:
        conn.close()
        return jsonify({'error': 'An account with this email already exists. Please log in.'}), 400

    avatar_url = 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=200&auto=format&fit=crop&q=80'
    joined = datetime.now().strftime('%B %Y')

    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (name, email, password, phone, city, area, avatar_url, swaps_completed, joined_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?)
    ''', (name, email, password, phone, city, area, avatar_url, joined))
    new_user_id = cursor.lastrowid
    conn.commit()
    conn.close()

    session['user_id'] = new_user_id
    return jsonify({
        'success': True,
        'user': {
            'id': new_user_id,
            'name': name,
            'email': email,
            'phone': phone,
            'city': city,
            'area': area,
            'avatar_url': avatar_url,
            'swaps_completed': 0,
            'joined_date': joined
        }
    }), 201

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.pop('user_id', None)
    return jsonify({'success': True})

@app.route('/api/demo-login/<int:user_id>', methods=['POST'])
def api_demo_login(user_id):
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if not user:
        return jsonify({'error': 'Demo user not found'}), 404

    session['user_id'] = user['id']
    user_dict = {
        'id': user['id'],
        'name': user['name'],
        'email': user['email'],
        'phone': user['phone'],
        'city': user['city'],
        'area': user['area'],
        'avatar_url': user['avatar_url'],
        'swaps_completed': user['swaps_completed'],
        'joined_date': user['joined_date']
    }
    return jsonify({'success': True, 'user': user_dict})

# ==========================================
# CLOTHING ITEMS & MARKETPLACE
# ==========================================

@app.route('/api/items', methods=['GET'])
def get_items():
    current_user = get_logged_in_user()
    current_uid = current_user['id'] if current_user else 0

    conn = get_db()

    # Filters
    category = request.args.get('category')
    gender = request.args.get('gender')
    condition = request.args.get('condition')
    search = request.args.get('search')
    sort_by = request.args.get('sort', 'newest')

    query = '''
        SELECT items.*, users.name as owner_name, users.avatar_url as owner_avatar,
               users.city as owner_city, users.area as owner_area, users.swaps_completed as owner_swaps
        FROM items
        JOIN users ON items.user_id = users.id
        WHERE items.status = 'available'
    '''
    params = []

    # Don't show your own items in marketplace if logged in
    if current_uid:
        query += ' AND items.user_id != ?'
        params.append(current_uid)

    if category and category != 'All':
        query += ' AND items.category = ?'
        params.append(category)

    if gender and gender != 'All':
        query += ' AND items.gender = ?'
        params.append(gender)

    if condition and condition != 'All':
        query += ' AND items.condition = ?'
        params.append(condition)

    if search:
        search_like = f"%{search.strip()}%"
        query += ' AND (items.title LIKE ? OR items.brand LIKE ? OR items.description LIKE ? OR items.area LIKE ?)'
        params.extend([search_like, search_like, search_like, search_like])

    if sort_by == 'price_low':
        query += ' ORDER BY items.price_inr ASC'
    elif sort_by == 'price_high':
        query += ' ORDER BY items.price_inr DESC'
    else: # newest
        query += ' ORDER BY items.id DESC'

    rows = conn.execute(query, params).fetchall()
    conn.close()

    items = [dict(r) for r in rows]
    return jsonify(items)

@app.route('/api/items/<int:item_id>', methods=['GET'])
def get_single_item(item_id):
    conn = get_db()
    row = conn.execute('''
        SELECT items.*, users.name as owner_name, users.avatar_url as owner_avatar,
               users.city as owner_city, users.area as owner_area, users.swaps_completed as owner_swaps
        FROM items
        JOIN users ON items.user_id = users.id
        WHERE items.id = ?
    ''', (item_id,)).fetchone()
    conn.close()

    if not row:
        return jsonify({'error': 'Item not found'}), 404
    return jsonify(dict(row))

@app.route('/api/wardrobe', methods=['GET'])
def get_my_wardrobe():
    user = get_logged_in_user()
    if not user:
        return jsonify([])

    conn = get_db()
    rows = conn.execute('SELECT * FROM items WHERE user_id = ? ORDER BY id DESC', (user['id'],)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/items', methods=['POST'])
def add_new_garment():
    user = get_logged_in_user()
    if not user:
        return jsonify({'error': 'Please login to list items in your wardrobe'}), 401

    data = request.json or {}
    title = data.get('title', '').strip()
    category = data.get('category', 'T-Shirts & Tops')
    gender = data.get('gender', 'Unisex')
    size = data.get('size', 'M')
    brand = data.get('brand', 'Independent')
    condition = data.get('condition', 'Like New')
    material = data.get('material', 'Cotton')
    price_inr = int(data.get('price_inr', 999) or 999)
    swap_preference = data.get('swap_preference', 'Open to any fair swap')
    description = data.get('description', '')
    image_url = data.get('image_url') or 'https://images.unsplash.com/photo-1523381210434-271e8be1f52b?w=800&auto=format&fit=crop&q=80'

    if not title:
        return jsonify({'error': 'Please enter a title for your item'}), 400

    now = datetime.now().strftime('%d %b, %I:%M %p')
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO items (
            user_id, title, description, category, gender, size, brand, condition, material,
            price_inr, swap_preference, image_url, status, city, area, water_saved_l, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'available', ?, ?, 2700, ?)
    ''', (
        user['id'], title, description, category, gender, size, brand, condition, material,
        price_inr, swap_preference, image_url, user['city'], user['area'], now
    ))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'item_id': new_id}), 201

@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_my_item(item_id):
    user = get_logged_in_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    conn = get_db()
    conn.execute('DELETE FROM items WHERE id = ? AND user_id = ?', (item_id, user['id']))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# ==========================================
# VALUE-BASED SWAP COMPARISON (INR ₹)
# ==========================================

@app.route('/api/fair-match/<int:target_item_id>', methods=['GET'])
def get_fair_matches(target_item_id):
    user = get_logged_in_user()
    if not user:
        return jsonify({'error': 'Please login to propose swaps'}), 401

    conn = get_db()
    target_row = conn.execute('SELECT * FROM items WHERE id = ?', (target_item_id,)).fetchone()
    if not target_row:
        conn.close()
        return jsonify({'error': 'Target item not found'}), 404

    target_item = dict(target_row)
    
    # Get user's available items
    my_items = conn.execute('SELECT * FROM items WHERE user_id = ? AND status = "available"', (user['id'],)).fetchall()
    conn.close()

    matches = []
    for row in my_items:
        my_item = dict(row)
        comparison = compare_swap_values(my_item['price_inr'], target_item['price_inr'])
        matches.append({
            'my_item': my_item,
            'comparison': comparison
        })

    # Sort best value match first
    matches.sort(key=lambda m: m['comparison']['difference_inr'])

    return jsonify({
        'target_item': target_item,
        'matches': matches
    })

# ==========================================
# SWAP PROPOSALS & MANAGEMENT
# ==========================================

@app.route('/api/swaps', methods=['GET'])
def get_user_swaps():
    user = get_logged_in_user()
    if not user:
        return jsonify([])

    conn = get_db()
    query = '''
        SELECT 
            sr.*,
            req.name as requester_name, req.avatar_url as requester_avatar, req.city as requester_city, req.area as requester_area,
            rec.name as receiver_name, rec.avatar_url as receiver_avatar, rec.city as receiver_city, rec.area as receiver_area,
            off_item.title as offered_title, off_item.image_url as offered_image, off_item.price_inr as offered_price, off_item.size as offered_size,
            req_item.title as requested_title, req_item.image_url as requested_image, req_item.price_inr as requested_price, req_item.size as requested_size
        FROM swap_requests sr
        JOIN users req ON sr.requester_id = req.id
        JOIN users rec ON sr.receiver_id = rec.id
        JOIN items off_item ON sr.offered_item_id = off_item.id
        JOIN items req_item ON sr.requested_item_id = req_item.id
        WHERE sr.requester_id = ? OR sr.receiver_id = ?
        ORDER BY sr.id DESC
    '''
    rows = conn.execute(query, (user['id'], user['id'])).fetchall()
    conn.close()

    swaps = []
    for r in rows:
        s = dict(r)
        s['is_requester'] = (s['requester_id'] == user['id'])
        s['comparison'] = compare_swap_values(s['offered_price'], s['requested_price'])
        swaps.append(s)

    return jsonify(swaps)

@app.route('/api/swaps/propose', methods=['POST'])
def propose_swap_request():
    user = get_logged_in_user()
    if not user:
        return jsonify({'error': 'Please login to send swap requests'}), 401

    data = request.json or {}
    requested_item_id = data.get('requested_item_id')
    offered_item_id = data.get('offered_item_id')
    extra_cash_inr = int(data.get('extra_cash_inr', 0) or 0)
    note = data.get('note', '')
    meet_location = data.get('meet_location', 'Nearby Metro Station or Cafe')

    if not requested_item_id or not offered_item_id:
        return jsonify({'error': 'Please select an item to offer for swap'}), 400

    conn = get_db()
    req_item = conn.execute('SELECT * FROM items WHERE id = ? AND status = "available"', (requested_item_id,)).fetchone()
    if not req_item:
        conn.close()
        return jsonify({'error': 'The requested item is no longer available'}), 400

    if req_item['user_id'] == user['id']:
        conn.close()
        return jsonify({'error': 'You cannot swap with your own item'}), 400

    off_item = conn.execute('SELECT * FROM items WHERE id = ? AND user_id = ? AND status = "available"', (offered_item_id, user['id'])).fetchone()
    if not off_item:
        conn.close()
        return jsonify({'error': 'Selected offer item is not in your available wardrobe'}), 400

    receiver_id = req_item['user_id']
    now = datetime.now().strftime('%d %b, %I:%M %p')

    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO swap_requests (
            requester_id, receiver_id, offered_item_id, requested_item_id,
            extra_cash_inr, note, status, meet_location, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, 'pending', ?, ?, ?)
    ''', (
        user['id'], receiver_id, offered_item_id, requested_item_id,
        extra_cash_inr, note, meet_location, now, now
    ))
    new_swap_id = cursor.lastrowid

    if note:
        cursor.execute('''
            INSERT INTO swap_messages (swap_id, sender_id, message, created_at)
            VALUES (?, ?, ?, ?)
        ''', (new_swap_id, user['id'], note, now))

    conn.commit()
    conn.close()

    return jsonify({'success': True, 'swap_id': new_swap_id}), 201

@app.route('/api/swaps/<int:swap_id>/action', methods=['POST'])
def update_swap_status(swap_id):
    user = get_logged_in_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json or {}
    action = data.get('action') # 'accept', 'decline', 'complete', 'cancel'

    conn = get_db()
    swap = conn.execute('SELECT * FROM swap_requests WHERE id = ?', (swap_id,)).fetchone()
    if not swap:
        conn.close()
        return jsonify({'error': 'Swap request not found'}), 404

    now = datetime.now().strftime('%d %b, %I:%M %p')

    if action == 'accept':
        if swap['receiver_id'] != user['id']:
            conn.close()
            return jsonify({'error': 'Only receiver can accept this proposal'}), 403
        conn.execute('UPDATE swap_requests SET status = "accepted", updated_at = ? WHERE id = ?', (now, swap_id))
        conn.execute('UPDATE items SET status = "pending_swap" WHERE id IN (?, ?)', (swap['offered_item_id'], swap['requested_item_id']))
        conn.commit()

    elif action == 'decline':
        if swap['receiver_id'] != user['id']:
            conn.close()
            return jsonify({'error': 'Only receiver can decline this proposal'}), 403
        conn.execute('UPDATE swap_requests SET status = "declined", updated_at = ? WHERE id = ?', (now, swap_id))
        conn.commit()

    elif action == 'complete':
        # Mark swap completed and exchange ownership of clothes
        conn.execute('UPDATE swap_requests SET status = "completed", updated_at = ? WHERE id = ?', (now, swap_id))
        conn.execute('UPDATE items SET status = "available", user_id = ? WHERE id = ?', (swap['receiver_id'], swap['offered_item_id']))
        conn.execute('UPDATE items SET status = "available", user_id = ? WHERE id = ?', (swap['requester_id'], swap['requested_item_id']))
        conn.execute('UPDATE users SET swaps_completed = swaps_completed + 1 WHERE id IN (?, ?)', (swap['requester_id'], swap['receiver_id']))
        conn.commit()

    elif action == 'cancel':
        conn.execute('UPDATE swap_requests SET status = "cancelled", updated_at = ? WHERE id = ?', (now, swap_id))
        conn.execute('UPDATE items SET status = "available" WHERE id IN (?, ?)', (swap['offered_item_id'], swap['requested_item_id']))
        conn.commit()

    conn.close()
    return jsonify({'success': True})

@app.route('/api/swaps/<int:swap_id>/messages', methods=['GET', 'POST'])
def swap_messages(swap_id):
    user = get_logged_in_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    conn = get_db()
    if request.method == 'POST':
        data = request.json or {}
        msg = data.get('message', '').strip()
        if not msg:
            conn.close()
            return jsonify({'error': 'Message cannot be empty'}), 400
        now = datetime.now().strftime('%d %b, %I:%M %p')
        conn.execute('INSERT INTO swap_messages (swap_id, sender_id, message, created_at) VALUES (?, ?, ?, ?)', (swap_id, user['id'], msg, now))
        conn.commit()
        conn.close()
        return jsonify({'success': True})

    # GET
    rows = conn.execute('''
        SELECT sm.*, u.name as sender_name, u.avatar_url as sender_avatar
        FROM swap_messages sm
        JOIN users u ON sm.sender_id = u.id
        WHERE sm.swap_id = ?
        ORDER BY sm.id ASC
    ''', (swap_id,)).fetchall()
    conn.close()

    msgs = []
    for r in rows:
        m = dict(r)
        m['is_me'] = (m['sender_id'] == user['id'])
        msgs.append(m)
    return jsonify(msgs)

# ==========================================
# ECO STATS & MEETING HUBS
# ==========================================

@app.route('/api/eco-hubs', methods=['GET'])
def get_hubs():
    conn = get_db()
    rows = conn.execute('SELECT * FROM eco_hubs').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/eco-impact', methods=['GET'])
def get_impact():
    conn = get_db()
    total_items = conn.execute('SELECT COUNT(*) FROM items').fetchone()[0]
    total_swaps = conn.execute('SELECT COUNT(*) FROM swap_requests WHERE status = "completed"').fetchone()[0]
    conn.close()

    water_saved = (total_items * 2700) + (total_swaps * 5400)
    co2_saved = round((total_items * 8.5) + (total_swaps * 17.0), 1)

    return jsonify({
        'total_items': total_items,
        'total_swaps': total_swaps + 14,
        'water_saved_liters': water_saved,
        'co2_saved_kg': co2_saved,
        'trees_equivalent': round(co2_saved / 0.06)
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"EcoSwap India running at http://127.0.0.1:{port} and http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
