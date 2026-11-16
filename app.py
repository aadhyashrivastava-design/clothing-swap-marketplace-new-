import os
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from database import get_db, init_db, calculate_barter_score
from models import haversine_distance_miles, evaluate_swap_fairness, get_eco_equivalencies

app = Flask(__name__)
app.secret_key = 'ecoswap-super-secret-sustainable-key-2024'

# Ensure DB is created on startup
with app.app_context():
    init_db()

def get_current_user_id():
    # Default to user 1 (Maya Lin) if not set in session
    return session.get('user_id', 1)

@app.route('/')
def index():
    return render_template('index.html')

# ----------------- User Endpoints -----------------

@app.route('/api/me', methods=['GET'])
def get_current_user():
    user_id = get_current_user_id()
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(dict(user))

@app.route('/api/switch-user', methods=['POST'])
def switch_user():
    data = request.json or {}
    new_user_id = data.get('user_id')
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (new_user_id,)).fetchone()
    conn.close()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    session['user_id'] = new_user_id
    return jsonify({'success': True, 'user': dict(user)})

@app.route('/api/users', methods=['GET'])
def list_users():
    conn = get_db()
    users = conn.execute('SELECT id, username, name, avatar_url, bio, address, rating, swaps_completed, eco_credits FROM users').fetchall()
    conn.close()
    return jsonify([dict(u) for u in users])

# ----------------- Items & Marketplace -----------------

@app.route('/api/items', methods=['GET'])
def get_marketplace_items():
    current_uid = get_current_user_id()
    conn = get_db()
    
    # Get current user coordinates
    current_user = conn.execute('SELECT latitude, longitude FROM users WHERE id = ?', (current_uid,)).fetchone()
    user_lat = current_user['latitude'] if current_user else 47.6150
    user_lon = current_user['longitude'] if current_user else -122.3200

    # Query params
    category = request.args.get('category')
    gender = request.args.get('gender')
    size = request.args.get('size')
    condition = request.args.get('condition')
    search = request.args.get('search')
    max_dist = request.args.get('max_distance', type=float)
    sort_by = request.args.get('sort', 'newest')
    include_own = request.args.get('include_own', 'false').lower() == 'true'

    query = '''
        SELECT items.*, users.name as owner_name, users.avatar_url as owner_avatar,
               users.rating as owner_rating, users.swaps_completed as owner_swaps
        FROM items
        JOIN users ON items.user_id = users.id
        WHERE items.status = 'available'
    '''
    params = []

    if not include_own:
        query += ' AND items.user_id != ?'
        params.append(current_uid)

    if category and category != 'All':
        query += ' AND items.category = ?'
        params.append(category)

    if gender and gender != 'All':
        query += ' AND items.gender = ?'
        params.append(gender)

    if size and size != 'All':
        query += ' AND items.size = ?'
        params.append(size)

    if condition and condition != 'All':
        query += ' AND items.condition = ?'
        params.append(condition)

    if search:
        search_like = f"%{search.strip()}%"
        query += ' AND (items.title LIKE ? OR items.brand LIKE ? OR items.description LIKE ? OR items.material LIKE ?)'
        params.extend([search_like, search_like, search_like, search_like])

    rows = conn.execute(query, params).fetchall()
    conn.close()

    items = []
    for r in rows:
        item = dict(r)
        # Compute distance to current user
        dist = haversine_distance_miles(user_lat, user_lon, item['latitude'], item['longitude'])
        item['distance_miles'] = dist
        
        # Distance filter if applied
        if max_dist and dist > max_dist:
            continue
        items.append(item)

    # Sorting
    if sort_by == 'nearest':
        items.sort(key=lambda x: x['distance_miles'])
    elif sort_by == 'value_high':
        items.sort(key=lambda x: x['barter_score'], reverse=True)
    elif sort_by == 'value_low':
        items.sort(key=lambda x: x['barter_score'])
    else:  # newest
        items.sort(key=lambda x: x['id'], reverse=True)

    return jsonify(items)

@app.route('/api/items/<int:item_id>', methods=['GET'])
def get_item_detail(item_id):
    current_uid = get_current_user_id()
    conn = get_db()
    current_user = conn.execute('SELECT latitude, longitude FROM users WHERE id = ?', (current_uid,)).fetchone()
    
    item_row = conn.execute('''
        SELECT items.*, users.name as owner_name, users.avatar_url as owner_avatar,
               users.rating as owner_rating, users.swaps_completed as owner_swaps,
               users.address as owner_address, users.bio as owner_bio
        FROM items
        JOIN users ON items.user_id = users.id
        WHERE items.id = ?
    ''', (item_id,)).fetchone()
    conn.close()

    if not item_row:
        return jsonify({'error': 'Item not found'}), 404

    item = dict(item_row)
    if current_user:
        item['distance_miles'] = haversine_distance_miles(
            current_user['latitude'], current_user['longitude'],
            item['latitude'], item['longitude']
        )
    return jsonify(item)

@app.route('/api/wardrobe', methods=['GET'])
def get_my_wardrobe():
    user_id = get_current_user_id()
    conn = get_db()
    rows = conn.execute('''
        SELECT * FROM items WHERE user_id = ? ORDER BY id DESC
    ''', (user_id,)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/items', methods=['POST'])
def add_new_item():
    user_id = get_current_user_id()
    data = request.json or {}

    title = data.get('title', '').strip()
    category = data.get('category', 'Tops & Shirts')
    gender = data.get('gender', 'Unisex')
    size = data.get('size', 'M')
    brand = data.get('brand', 'Independent')
    condition = data.get('condition', 'Gently Used')
    material = data.get('material', 'Cotton')
    estimated_value = float(data.get('estimated_value', 45.0) or 45.0)
    swap_preference = data.get('swap_preference', 'Open to fair trades')
    description = data.get('description', '')
    image_url = data.get('image_url') or 'https://images.unsplash.com/photo-1523381210434-271e8be1f52b?w=800&auto=format&fit=crop&q=80'

    if not title:
        return jsonify({'error': 'Title is required'}), 400

    conn = get_db()
    user = conn.execute('SELECT address, latitude, longitude FROM users WHERE id = ?', (user_id,)).fetchone()
    
    barter_score = calculate_barter_score(brand, condition, material, estimated_value)
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # Calculate eco savings based on category
    eco_metrics = {
        'Jackets & Coats': (4500, 15.0),
        'Pants & Jeans': (7500, 18.0),
        'Sweaters & Knits': (3200, 10.0),
        'Dresses & Jumpsuits': (3400, 8.5),
        'Shoes': (5000, 20.0),
        'Tops & Shirts': (2700, 7.5),
        'Accessories': (1200, 3.0)
    }
    water_l, co2_kg = eco_metrics.get(category, (2700, 8.0))

    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO items (
            user_id, title, description, category, gender, size, brand, condition, material,
            estimated_value, barter_score, swap_preference, image_url, status, address,
            latitude, longitude, water_saved_l, co2_saved_kg, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'available', ?, ?, ?, ?, ?, ?)
    ''', (
        user_id, title, description, category, gender, size, brand, condition, material,
        estimated_value, barter_score, swap_preference, image_url,
        user['address'] if user else 'Capitol Hill, Seattle, WA',
        user['latitude'] if user else 47.6150,
        user['longitude'] if user else -122.3200,
        water_l, co2_kg, now
    ))
    
    # Reward user with 15 Eco-Credits for listing an item!
    conn.execute('UPDATE users SET eco_credits = eco_credits + 15 WHERE id = ?', (user_id,))
    
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'item_id': new_id, 'barter_score': barter_score, 'earned_credits': 15}), 201

@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    user_id = get_current_user_id()
    conn = get_db()
    item = conn.execute('SELECT * FROM items WHERE id = ? AND user_id = ?', (item_id, user_id)).fetchone()
    if not item:
        conn.close()
        return jsonify({'error': 'Item not found or unauthorized'}), 404

    conn.execute('DELETE FROM items WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# ----------------- Value-Based Swap Recommendation Engine -----------------

@app.route('/api/fair-match/<int:target_item_id>', methods=['GET'])
def get_fair_swap_recommendations(target_item_id):
    user_id = get_current_user_id()
    conn = get_db()
    
    target_row = conn.execute('SELECT * FROM items WHERE id = ?', (target_item_id,)).fetchone()
    if not target_row:
        conn.close()
        return jsonify({'error': 'Target item not found'}), 404

    target_item = dict(target_row)
    
    # Get current user's available items
    user_items = conn.execute('''
        SELECT * FROM items WHERE user_id = ? AND status = 'available'
    ''', (user_id,)).fetchall()
    conn.close()

    matches = []
    for u_row in user_items:
        u_item = dict(u_row)
        fairness = evaluate_swap_fairness(u_item['barter_score'], target_item['barter_score'])
        matches.append({
            'my_item': u_item,
            'target_item': target_item,
            'fairness': fairness
        })

    # Sort best match first
    matches.sort(key=lambda m: m['fairness']['fairness_pct'], reverse=True)
    return jsonify({
        'target_item': target_item,
        'matches': matches
    })

# ----------------- Swap Proposals & Trade Lifecycle -----------------

@app.route('/api/swaps', methods=['GET'])
def get_user_swaps():
    user_id = get_current_user_id()
    conn = get_db()
    
    query = '''
        SELECT 
            sr.*,
            req.name as requester_name, req.avatar_url as requester_avatar,
            rec.name as receiver_name, rec.avatar_url as receiver_avatar,
            off_item.title as offered_title, off_item.image_url as offered_image, 
            off_item.barter_score as offered_score, off_item.size as offered_size,
            req_item.title as requested_title, req_item.image_url as requested_image,
            req_item.barter_score as requested_score, req_item.size as requested_size
        FROM swap_requests sr
        JOIN users req ON sr.requester_id = req.id
        JOIN users rec ON sr.receiver_id = rec.id
        JOIN items off_item ON sr.offered_item_id = off_item.id
        JOIN items req_item ON sr.requested_item_id = req_item.id
        WHERE sr.requester_id = ? OR sr.receiver_id = ?
        ORDER BY sr.id DESC
    '''
    rows = conn.execute(query, (user_id, user_id)).fetchall()
    conn.close()

    swaps = []
    for r in rows:
        swap = dict(r)
        swap['is_requester'] = (swap['requester_id'] == user_id)
        fairness = evaluate_swap_fairness(swap['offered_score'], swap['requested_score'])
        swap['fairness_pct'] = fairness['fairness_pct']
        swap['fairness_verdict'] = fairness['verdict']
        swaps.append(swap)

    return jsonify(swaps)

@app.route('/api/swaps/propose', methods=['POST'])
def propose_swap():
    user_id = get_current_user_id()
    data = request.json or {}

    requested_item_id = data.get('requested_item_id')
    offered_item_id = data.get('offered_item_id')
    additional_credits = int(data.get('additional_credits', 0) or 0)
    note = data.get('note', '')
    meet_location = data.get('meet_location', 'Community Eco Hub')
    meet_time = data.get('meet_time', 'Weekend Afternoon')

    if not requested_item_id or not offered_item_id:
        return jsonify({'error': 'Both offered and requested items are required'}), 400

    conn = get_db()
    # Validate requested item
    req_item = conn.execute('SELECT * FROM items WHERE id = ? AND status = "available"', (requested_item_id,)).fetchone()
    if not req_item:
        conn.close()
        return jsonify({'error': 'Requested item is no longer available'}), 400

    if req_item['user_id'] == user_id:
        conn.close()
        return jsonify({'error': 'You cannot swap with your own item'}), 400

    # Validate offered item belongs to user
    off_item = conn.execute('SELECT * FROM items WHERE id = ? AND user_id = ? AND status = "available"', (offered_item_id, user_id)).fetchone()
    if not off_item:
        conn.close()
        return jsonify({'error': 'Offered item is invalid or not in your wardrobe'}), 400

    receiver_id = req_item['user_id']
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    qr_token = f"SWAP-{uuid.uuid4().hex[:8].upper()}"

    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO swap_requests (
            requester_id, receiver_id, offered_item_id, requested_item_id,
            additional_credits, note, status, meet_location, meet_time, qr_code_token, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, 'pending', ?, ?, ?, ?, ?)
    ''', (
        user_id, receiver_id, offered_item_id, requested_item_id,
        additional_credits, note, meet_location, meet_time, qr_token, now, now
    ))
    new_swap_id = cursor.lastrowid

    # Add initial note as chat message
    if note:
        cursor.execute('''
            INSERT INTO swap_messages (swap_id, sender_id, message, created_at)
            VALUES (?, ?, ?, ?)
        ''', (new_swap_id, user_id, note, now))

    conn.commit()
    conn.close()

    return jsonify({'success': True, 'swap_id': new_swap_id, 'token': qr_token}), 201

@app.route('/api/swaps/<int:swap_id>/action', methods=['POST'])
def update_swap_action(swap_id):
    user_id = get_current_user_id()
    data = request.json or {}
    action = data.get('action') # 'accept', 'decline', 'complete', 'cancel'

    conn = get_db()
    swap = conn.execute('SELECT * FROM swap_requests WHERE id = ?', (swap_id,)).fetchone()
    if not swap:
        conn.close()
        return jsonify({'error': 'Swap request not found'}), 404

    now = datetime.now().strftime('%Y-%m-%d %H:%M')

    if action == 'accept':
        if swap['receiver_id'] != user_id:
            conn.close()
            return jsonify({'error': 'Only the receiver can accept this proposal'}), 403
        
        conn.execute('UPDATE swap_requests SET status = "accepted", updated_at = ? WHERE id = ?', (now, swap_id))
        # Mark both items as pending_swap
        conn.execute('UPDATE items SET status = "pending_swap" WHERE id IN (?, ?)', (swap['offered_item_id'], swap['requested_item_id']))
        conn.commit()

    elif action == 'decline':
        if swap['receiver_id'] != user_id:
            conn.close()
            return jsonify({'error': 'Only the receiver can decline this proposal'}), 403
        
        conn.execute('UPDATE swap_requests SET status = "declined", updated_at = ? WHERE id = ?', (now, swap_id))
        conn.commit()

    elif action == 'cancel':
        if swap['requester_id'] != user_id and swap['receiver_id'] != user_id:
            conn.close()
            return jsonify({'error': 'Unauthorized'}), 403
        
        conn.execute('UPDATE swap_requests SET status = "cancelled", updated_at = ? WHERE id = ?', (now, swap_id))
        # Revert items back to available
        conn.execute('UPDATE items SET status = "available" WHERE id IN (?, ?)', (swap['offered_item_id'], swap['requested_item_id']))
        conn.commit()

    elif action == 'complete':
        # Handshake / QR confirmation to complete barter!
        if swap['status'] not in ('accepted', 'pending'):
            conn.close()
            return jsonify({'error': 'Swap is not ready to complete'}), 400

        conn.execute('UPDATE swap_requests SET status = "completed", updated_at = ? WHERE id = ?', (now, swap_id))
        # Mark items as swapped
        conn.execute('UPDATE items SET status = "swapped" WHERE id IN (?, ?)', (swap['offered_item_id'], swap['requested_item_id']))
        # Swap ownership of items
        conn.execute('UPDATE items SET user_id = ? WHERE id = ?', (swap['receiver_id'], swap['offered_item_id']))
        conn.execute('UPDATE items SET user_id = ? WHERE id = ?', (swap['requester_id'], swap['requested_item_id']))
        
        # Increment completed swaps & award 25 Eco-Credits to each participant!
        conn.execute('UPDATE users SET swaps_completed = swaps_completed + 1, eco_credits = eco_credits + 25 WHERE id IN (?, ?)', (swap['requester_id'], swap['receiver_id']))
        conn.commit()

    conn.close()
    return jsonify({'success': True, 'action': action})

@app.route('/api/swaps/<int:swap_id>/messages', methods=['GET', 'POST'])
def handle_swap_messages(swap_id):
    user_id = get_current_user_id()
    conn = get_db()
    
    if request.method == 'POST':
        data = request.json or {}
        text = data.get('message', '').strip()
        if not text:
            conn.close()
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        now = datetime.now().strftime('%Y-%m-%d %H:%M')
        conn.execute('INSERT INTO swap_messages (swap_id, sender_id, message, created_at) VALUES (?, ?, ?, ?)', (swap_id, user_id, text, now))
        conn.commit()
        conn.close()
        return jsonify({'success': True})

    # GET messages
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
        m['is_me'] = (m['sender_id'] == user_id)
        msgs.append(m)
    return jsonify(msgs)

# ----------------- Eco Hubs & Platform Metrics -----------------

@app.route('/api/eco-hubs', methods=['GET'])
def get_eco_hubs():
    conn = get_db()
    rows = conn.execute('SELECT * FROM eco_hubs').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/eco-impact', methods=['GET'])
def get_eco_impact():
    user_id = get_current_user_id()
    conn = get_db()

    # Platform Totals
    platform_stats = conn.execute('''
        SELECT 
            COUNT(id) as total_items_listed,
            COALESCE(SUM(water_saved_l), 0) as total_water_saved,
            COALESCE(SUM(co2_saved_kg), 0.0) as total_co2_saved
        FROM items
    ''').fetchone()

    total_swaps = conn.execute('''
        SELECT COUNT(id) FROM swap_requests WHERE status = "completed"
    ''').fetchone()[0]

    # User Personal Impact
    user_stats = conn.execute('''
        SELECT 
            COUNT(id) as my_items,
            COALESCE(SUM(water_saved_l), 0) as my_water_saved,
            COALESCE(SUM(co2_saved_kg), 0.0) as my_co2_saved
        FROM items WHERE user_id = ?
    ''', (user_id,)).fetchone()

    user_info = conn.execute('SELECT swaps_completed, eco_credits FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()

    platform_equiv = get_eco_equivalencies(
        platform_stats['total_water_saved'],
        platform_stats['total_co2_saved'],
        platform_stats['total_items_listed']
    )
    user_equiv = get_eco_equivalencies(
        user_stats['my_water_saved'],
        user_stats['my_co2_saved'],
        user_stats['my_items']
    )

    return jsonify({
        'platform': {
            'items_listed': platform_stats['total_items_listed'],
            'completed_swaps': total_swaps + 18, # including historical community swaps
            'water_saved_l': platform_stats['total_water_saved'] + 54000,
            'co2_saved_kg': round(platform_stats['total_co2_saved'] + 175.0, 1),
            'equivalencies': platform_equiv
        },
        'personal': {
            'items_listed': user_stats['my_items'],
            'swaps_completed': user_info['swaps_completed'] if user_info else 0,
            'eco_credits': user_info['eco_credits'] if user_info else 0,
            'water_saved_l': user_stats['my_water_saved'],
            'co2_saved_kg': round(user_stats['my_co2_saved'], 1),
            'equivalencies': user_equiv
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting EcoSwap on http://127.0.0.1:{port} and http://localhost:{port} ...")
    app.run(host='0.0.0.0', port=port, debug=False)
