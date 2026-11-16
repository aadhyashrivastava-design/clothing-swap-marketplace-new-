import sqlite3
import os
import math
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'ecoswap.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def calculate_barter_score(brand, condition, material, estimated_value):
    """
    Computes a standardized barter score (10 - 100) based on:
    - Estimated retail value
    - Item condition grade
    - Sustainable/durable material weighting
    """
    condition_multipliers = {
        'Brand New with Tags': 1.0,
        'Like New': 0.88,
        'Gently Used': 0.75,
        'Vintage / Well Loved': 0.65
    }
    
    sustainable_materials = ['100% Wool', 'Organic Cotton', 'Linen', 'Raw Denim', 'Recycled Cashmere', 'Silk', 'Upcycled Canvas']
    material_bonus = 1.15 if any(mat.lower() in (material or '').lower() for mat in sustainable_materials) else 1.0
    
    cond_mult = condition_multipliers.get(condition, 0.75)
    base = min(max(float(estimated_value or 30), 10), 300)
    
    # Scale from 15 to 100
    score = (base * 0.35 + 10) * cond_mult * material_bonus
    return round(min(max(score, 10), 100), 1)

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            avatar_url TEXT,
            bio TEXT,
            address TEXT,
            latitude REAL,
            longitude REAL,
            rating REAL DEFAULT 5.0,
            swaps_completed INTEGER DEFAULT 0,
            eco_credits INTEGER DEFAULT 50,
            joined_date TEXT
        )
    ''')

    # Clothing Items Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT NOT NULL,
            gender TEXT DEFAULT 'Unisex',
            size TEXT NOT NULL,
            brand TEXT,
            condition TEXT NOT NULL,
            material TEXT,
            estimated_value REAL DEFAULT 40.0,
            barter_score REAL DEFAULT 50.0,
            swap_preference TEXT,
            image_url TEXT,
            status TEXT DEFAULT 'available',
            address TEXT,
            latitude REAL,
            longitude REAL,
            water_saved_l INTEGER DEFAULT 2700,
            co2_saved_kg REAL DEFAULT 8.5,
            created_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Swap Requests Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS swap_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            requester_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            offered_item_id INTEGER NOT NULL,
            requested_item_id INTEGER NOT NULL,
            additional_credits INTEGER DEFAULT 0,
            note TEXT,
            status TEXT DEFAULT 'pending',
            meet_location TEXT,
            meet_time TEXT,
            qr_code_token TEXT,
            created_at TEXT,
            updated_at TEXT,
            FOREIGN KEY (requester_id) REFERENCES users (id),
            FOREIGN KEY (receiver_id) REFERENCES users (id),
            FOREIGN KEY (offered_item_id) REFERENCES items (id),
            FOREIGN KEY (requested_item_id) REFERENCES items (id)
        )
    ''')

    # Swap Messages Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS swap_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            swap_id INTEGER NOT NULL,
            sender_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT,
            FOREIGN KEY (swap_id) REFERENCES swap_requests (id),
            FOREIGN KEY (sender_id) REFERENCES users (id)
        )
    ''')

    # Eco Community Swap Hubs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS eco_hubs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            hub_type TEXT NOT NULL,
            address TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            hours TEXT,
            description TEXT
        )
    ''')

    conn.commit()
    seed_data(conn)
    conn.close()

def seed_data(conn):
    cursor = conn.cursor()
    
    # Check if already seeded
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] > 0:
        return

    # Seed Users (Current active user is user #1 "Maya Lin")
    users = [
        (1, 'mayalin', 'Maya Lin (You)', 'maya@ecoswap.org',
         'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200&auto=format&fit=crop&q=80',
         'Slow fashion enthusiast & textile circularity advocate. Downsizing my closet sustainably!',
         'Capitol Hill, Seattle, WA', 47.6150, -122.3200, 4.95, 8, 120, '2024-01-15'),
        (2, 'liam_swaps', 'Liam Chen', 'liam@ecoswap.org',
         'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&auto=format&fit=crop&q=80',
         'Vintage collector & denim head. Looking for heavyweight flannel or chore coats.',
         'Fremont, Seattle, WA', 47.6505, -122.3493, 4.88, 14, 85, '2023-11-20'),
        (3, 'elena_vintage', 'Elena Rostova', 'elena@ecoswap.org',
         'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=200&auto=format&fit=crop&q=80',
         'Upcycler and knitwear lover. Prefer meeting at local community cafes or swap stations.',
         'Ballard, Seattle, WA', 47.6685, -122.3845, 5.0, 22, 210, '2023-09-10'),
        (4, 'marcus_k', 'Marcus King', 'marcus@ecoswap.org',
         'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=200&auto=format&fit=crop&q=80',
         'Minimalist capsule wardrobe convert. Swapping outdoor apparel and quality shoes.',
         'Queen Anne, Seattle, WA', 47.6323, -122.3564, 4.79, 6, 60, '2024-02-01'),
        (5, 'zoe_green', 'Zoe Thorne', 'zoe@ecoswap.org',
         'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&auto=format&fit=crop&q=80',
         'Student stylist. Love layering pieces, streetwear, and vintage 90s aesthetic.',
         'University District, Seattle, WA', 47.6599, -122.3134, 4.92, 11, 140, '2024-03-05')
    ]
    cursor.executemany('''
        INSERT INTO users (id, username, name, email, avatar_url, bio, address, latitude, longitude, rating, swaps_completed, eco_credits, joined_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', users)

    # Seed Items (User 1 has 3 items in her active wardrobe, others have items in the marketplace)
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    items = [
        # Maya's Items (User 1)
        (1, 1, 'Everlane Oversized Alpaca Crew Sweater',
         'Super soft cloudy alpaca knit in warm oat. Only worn twice, dry cleaned and in immaculate condition. Looking for a structured blazer or denim jacket in Size S/M.',
         'Sweaters & Knits', 'Women', 'M', 'Everlane', 'Like New', 'Alpaca / Wool blend', 110.0, 72.0,
         'Looking for oversized workwear jackets or chore coats',
         'https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=800&auto=format&fit=crop&q=80',
         'available', 'Capitol Hill, Seattle, WA', 47.6150, -122.3200, 3200, 9.4, now),
        (2, 1, 'Vintage Levi’s 501 Straight Leg Jeans',
         'Classic 90s made in USA wash with authentic gentle fading. Hemmed to 30 inseam. Sturdy 100% cotton denim with no fraying.',
         'Pants & Jeans', 'Unisex', '30/30', 'Levi’s', 'Gently Used', '100% Raw Denim', 85.0, 68.0,
         'Open to wool skirts, boots, or chunky knits',
         'https://images.unsplash.com/photo-1542272604-780c96856592?w=800&auto=format&fit=crop&q=80',
         'available', 'Capitol Hill, Seattle, WA', 47.6150, -122.3200, 7500, 18.2, now),
        (3, 1, 'Patagonia Lightweight Synchilla Snap-T Fleece',
         'Cozy geometric pattern fleece pullover. Excellent condition, non-smoking home. Keeps you warm for fall and spring hikes.',
         'Jackets & Coats', 'Unisex', 'S', 'Patagonia', 'Like New', '100% Recycled Polyester', 98.0, 69.0,
         'Swap for rain shell or canvas tote',
         'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=800&auto=format&fit=crop&q=80',
         'available', 'Capitol Hill, Seattle, WA', 47.6150, -122.3200, 2400, 7.8, now),

        # Marketplace Items from Liam, Elena, Marcus, Zoe
        (4, 2, 'Carhartt WIP Michigan Chore Coat',
         'Heavy organic cotton canvas chore coat in Tobacco Brown with corduroy collar. Unlined, perfect everyday outerwear.',
         'Jackets & Coats', 'Men', 'M', 'Carhartt WIP', 'Gently Used', '100% Organic Cotton', 145.0, 78.0,
         'Looking for high-neck wool sweaters, trench coats, or selvedge denim',
         'https://images.unsplash.com/photo-1544441893-675973e31985?w=800&auto=format&fit=crop&q=80',
         'available', 'Fremont, Seattle, WA', 47.6505, -122.3493, 4200, 14.5, now),
        (5, 2, 'L.L.Bean Heritage Wool Cable Fisherman Sweater',
         'Authentic Irish knit aesthetic with thick cable weave. Incredibly warm and durable heirloom quality.',
         'Sweaters & Knits', 'Unisex', 'L', 'L.L.Bean', 'Like New', '100% Wool', 120.0, 74.0,
         'Interested in utility cargo trousers or rain slicker',
         'https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=800&auto=format&fit=crop&q=80',
         'available', 'Fremont, Seattle, WA', 47.6505, -122.3493, 3100, 11.0, now),
        (6, 3, 'Sézane Gaspard Cardigan in Sage Green',
         'Iconic Parisian knit with mother-of-pearl buttons. Can be worn with buttons front or back. Flawless condition, delicate hand wash only.',
         'Sweaters & Knits', 'Women', 'S', 'Sézane', 'Like New', 'Kid Mohair / Alpaca blend', 130.0, 76.0,
         'Will swap for alpaca sweaters, trench coat, or midi wrap dresses',
         'https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=800&auto=format&fit=crop&q=80',
         'available', 'Ballard, Seattle, WA', 47.6685, -122.3845, 2800, 8.2, now),
        (7, 3, 'Reformation Linen A-Line Wrap Midi Dress',
         'Effortless summer linen dress in terracotta floral. Ties at the waist with flutter sleeves. Zero signs of wear.',
         'Dresses & Jumpsuits', 'Women', 'M', 'Reformation', 'Brand New with Tags', '100% Linen', 178.0, 86.0,
         'Seeking vintage leather bomber or designer boots',
         'https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=800&auto=format&fit=crop&q=80',
         'available', 'Ballard, Seattle, WA', 47.6685, -122.3845, 3400, 6.9, now),
        (8, 4, 'Red Wing Heritage Iron Ranger Boots (Amber Harness)',
         'Famous handcrafted Goodyear welted boots. Broken in nicely with rich patina. Freshly conditioned with mink oil, soles in great shape.',
         'Shoes', 'Men', 'US 9.5', 'Red Wing', 'Gently Used', 'Full Grain Leather', 220.0, 88.0,
         'Seeking technical down jackets (Arc’teryx, Patagonia) or Barbour coats',
         'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&auto=format&fit=crop&q=80',
         'available', 'Queen Anne, Seattle, WA', 47.6323, -122.3564, 5200, 19.8, now),
        (9, 4, 'Arc’teryx Atom LT Hoody - Black',
         'Lightweight, breathable Coreloft insulated hoody. Ideal standalone or midlayer for PNW wet weather. Clean cuffs and zipper.',
         'Jackets & Coats', 'Unisex', 'M', 'Arc’teryx', 'Like New', 'Tyono 20 Nylon', 190.0, 84.0,
         'Trade for wool overcoat or sturdy leather footwear',
         'https://images.unsplash.com/photo-1548883354-7622d03aca27?w=800&auto=format&fit=crop&q=80',
         'available', 'Queen Anne, Seattle, WA', 47.6323, -122.3564, 3800, 12.3, now),
        (10, 5, 'Vintage 90s Stüssy Boxy Embroidered Hoodie',
         'True vintage heavyweight fleece hoodie with retro chainstitch embroidery on chest. Washed charcoal grey with oversized 90s fit.',
         'Tops & Shirts', 'Unisex', 'L', 'Stüssy Vintage', 'Vintage / Well Loved', '100% Heavyweight Cotton', 95.0, 65.0,
         'Looking for carpenter pants, vintage Levi’s 501s, or beanies',
         'https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=800&auto=format&fit=crop&q=80',
         'available', 'University District, Seattle, WA', 47.6599, -122.3134, 3600, 10.5, now),
        (11, 5, 'Dickies 874 Work Pants (Forest Green)',
         'Iconic twill skater work trousers. Wrinkle and stain resistant, crisp crease intact.',
         'Pants & Jeans', 'Unisex', '32/32', 'Dickies', 'Like New', 'Poly-Cotton Twill', 45.0, 48.0,
         'Open to graphic tees, hats, or tote bags',
         'https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=800&auto=format&fit=crop&q=80',
         'available', 'University District, Seattle, WA', 47.6599, -122.3134, 4100, 11.2, now),
        (12, 2, 'COS Minimalist Wool Blend Tailored Overshirt',
         'Clean architectural silhouette from COS in deep navy. Hidden placket and sharp point collar. Great for smart casual layering.',
         'Tops & Shirts', 'Men', 'M', 'COS', 'Like New', 'Wool blend', 90.0, 66.0,
         'Open to casual knitwear or casual leather accessories',
         'https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=800&auto=format&fit=crop&q=80',
         'available', 'Fremont, Seattle, WA', 47.6505, -122.3493, 2600, 7.5, now)
    ]
    cursor.executemany('''
        INSERT INTO items (
            id, user_id, title, description, category, gender, size, brand, condition, material,
            estimated_value, barter_score, swap_preference, image_url, status, address, latitude,
            longitude, water_saved_l, co2_saved_kg, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', items)

    # Seed Sample Community Eco Swap Hubs
    hubs = [
        (1, 'Green District Textile Library & Hub', 'Official Swap Station',
         '1520 11th Ave, Capitol Hill, Seattle, WA', 47.6145, -122.3188,
         'Mon-Sat 10:00 AM - 7:00 PM', 'Public swap rack, digital verification kiosk, and mending supplies available.'),
        (2, 'Fremont Sustainable Coffee & Trade Bar', 'Eco Cafe Partner',
         '3401 Evanston Ave N, Fremont, WA', 47.6500, -122.3510,
         'Daily 7:00 AM - 6:00 PM', 'Safe indoor swap meeting place. Swappers get 15% off oat milk lattes!'),
        (3, 'Ballard Community Center Circular Room', 'Community Hub',
         '6020 28th Ave NW, Ballard, WA', 47.6720, -122.3920,
         'Tue-Sun 9:00 AM - 8:00 PM', 'Hosts bi-weekly sustainable clothing barter events and drop boxes.'),
        (4, 'Queen Anne Eco-Loft', 'Partner Studio',
         '2121 Queen Anne Ave N, Seattle, WA', 47.6380, -122.3570,
         'Mon-Fri 11:00 AM - 6:00 PM', 'Upcycling workspace and verified swap meetup zone.')
    ]
    cursor.executemany('''
        INSERT INTO eco_hubs (id, name, hub_type, address, latitude, longitude, hours, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', hubs)

    # Seed an initial swap request to demonstrate the trade hub right away!
    cursor.execute('''
        INSERT INTO swap_requests (
            id, requester_id, receiver_id, offered_item_id, requested_item_id,
            additional_credits, note, status, meet_location, meet_time, qr_code_token, created_at, updated_at
        ) VALUES (
            1, 2, 1, 4, 1,
            10, 'Hi Maya! I love your Everlane Alpaca sweater. Would you be open to swapping for my Carhartt WIP Chore coat? Adding 10 Eco-Credits to make it even!',
            'pending', 'Fremont Sustainable Coffee & Trade Bar', 'Saturday 2:00 PM', 'SWAP-TOKEN-MAYALEN-001',
            ?, ?
        )
    ''', (now, now))

    cursor.execute('''
        INSERT INTO swap_messages (swap_id, sender_id, message, created_at)
        VALUES (1, 2, 'Hey! I can meet at the Fremont Eco Cafe anytime this weekend if this trade looks good to you :)', ?)
    ''', (now,))

    conn.commit()

if __name__ == '__main__':
    init_db()
    print("EcoSwap Database initialized successfully with rich seed data!")
