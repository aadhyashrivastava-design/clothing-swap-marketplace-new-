import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'ecoswap.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Users Table (Supports Login and Registration)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            phone TEXT,
            city TEXT DEFAULT 'Bangalore',
            area TEXT DEFAULT 'Indiranagar',
            avatar_url TEXT,
            swaps_completed INTEGER DEFAULT 0,
            joined_date TEXT
        )
    ''')

    # Clothing Items Table (Value in Indian Rupees ₹)
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
            price_inr INTEGER NOT NULL DEFAULT 999,
            swap_preference TEXT,
            image_url TEXT,
            status TEXT DEFAULT 'available',
            city TEXT DEFAULT 'Bangalore',
            area TEXT DEFAULT 'Indiranagar',
            latitude REAL,
            longitude REAL,
            water_saved_l INTEGER DEFAULT 2700,
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
            extra_cash_inr INTEGER DEFAULT 0,
            note TEXT,
            status TEXT DEFAULT 'pending',
            meet_location TEXT,
            created_at TEXT,
            updated_at TEXT,
            FOREIGN KEY (requester_id) REFERENCES users (id),
            FOREIGN KEY (receiver_id) REFERENCES users (id),
            FOREIGN KEY (offered_item_id) REFERENCES items (id),
            FOREIGN KEY (requested_item_id) REFERENCES items (id)
        )
    ''')

    # Swap Chat Messages Table
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

    # Safe Local Swap Points
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS eco_hubs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            city TEXT NOT NULL,
            area TEXT NOT NULL,
            address TEXT NOT NULL,
            hub_type TEXT NOT NULL,
            timings TEXT,
            description TEXT
        )
    ''')

    conn.commit()
    seed_indian_data(conn)
    conn.close()

def seed_indian_data(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] > 0:
        return

    # Seed Indian Users (Default password: 123 for easy login!)
    users = [
        (1, 'Priya Sharma', 'priya@gmail.com', '123', '9876543210',
         'Bangalore', 'Indiranagar',
         'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200&auto=format&fit=crop&q=80',
         5, 'January 2024'),
        (2, 'Rahul Verma', 'rahul@gmail.com', '123', '9876543211',
         'Bangalore', 'Koramangala',
         'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&auto=format&fit=crop&q=80',
         8, 'November 2023'),
        (3, 'Ananya Iyer', 'ananya@gmail.com', '123', '9876543212',
         'Bangalore', 'HSR Layout',
         'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=200&auto=format&fit=crop&q=80',
         12, 'October 2023'),
        (4, 'Rohan Mehta', 'rohan@gmail.com', '123', '9876543213',
         'Bangalore', 'Whitefield',
         'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=200&auto=format&fit=crop&q=80',
         4, 'February 2024')
    ]
    cursor.executemany('''
        INSERT INTO users (id, name, email, password, phone, city, area, avatar_url, swaps_completed, joined_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', users)

    # Seed Indian Clothing Items (in ₹ Rupees)
    now = datetime.now().strftime('%d %b, %I:%M %p')
    items = [
        # Priya's Wardrobe (User 1)
        (1, 1, 'FabIndia Handwoven Pure Cotton Kurta',
         'Beautiful pastel green handblock printed cotton kurta with wooden buttons. Worn only once during Diwali.',
         'Ethnic & Traditional', 'Women', 'M', 'FabIndia', 'Like New', '100% Cotton',
         1499, 'Looking for denim jacket or linen pants',
         'https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=800&auto=format&fit=crop&q=80',
         'available', 'Bangalore', 'Indiranagar', 12.9784, 77.6408, 2700, now),
        (2, 1, 'Zara Oversized Knitted Cardigan',
         'Warm beige button-down knit cardigan. Very soft and cozy for Bangalore evenings.',
         'Jackets & Hoodies', 'Women', 'Free Size', 'Zara', 'Like New', 'Wool Blend',
         1899, 'Want to swap for Zara trousers or boots',
         'https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=800&auto=format&fit=crop&q=80',
         'available', 'Bangalore', 'Indiranagar', 12.9784, 77.6408, 3200, now),
        (3, 1, 'Levi’s 711 Skinny Fit Denim Jeans',
         'Dark indigo blue washed jeans with high stretch. Waist size 28. Very good condition.',
         'Jeans & Trousers', 'Women', '28/30', 'Levi’s', 'Gently Used', 'Cotton Stretch Denim',
         1299, 'Open to any ethnic kurti or hoodie',
         'https://images.unsplash.com/photo-1542272604-780c96856592?w=800&auto=format&fit=crop&q=80',
         'available', 'Bangalore', 'Indiranagar', 12.9784, 77.6408, 7500, now),

        # Rahul's Items (User 2)
        (4, 2, 'H&M Relaxed Fit Denim Chore Jacket',
         'Classic light blue denim trucker jacket. Sturdy and in clean condition. Fits Size L comfortably.',
         'Jackets & Hoodies', 'Men', 'L', 'H&M', 'Like New', '100% Cotton Denim',
         1999, 'Looking for oversized graphic tees or cargo pants',
         'https://images.unsplash.com/photo-1544441893-675973e31985?w=800&auto=format&fit=crop&q=80',
         'available', 'Bangalore', 'Koramangala', 12.9352, 77.6245, 4500, now),
        (5, 2, 'Uniqlo Supima Cotton Crew Neck T-Shirt (Navy)',
         'Premium soft Supima cotton t-shirt. Never lost color or shape, worn 3-4 times only.',
         'T-Shirts & Tops', 'Men', 'M', 'Uniqlo', 'Like New', 'Supima Cotton',
         799, 'Open to cap, beanie, or casual t-shirts',
         'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=800&auto=format&fit=crop&q=80',
         'available', 'Bangalore', 'Koramangala', 12.9352, 77.6245, 2500, now),
        (6, 2, 'Woodland Tan Leather Hiking Shoes',
         'Original Woodland high-grip leather boots. Soles are completely intact with clean finish.',
         'Footwear & Shoes', 'Men', 'UK 8', 'Woodland', 'Gently Used', 'Genuine Leather',
         2499, 'Interested in Nike sneakers or leather jacket',
         'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&auto=format&fit=crop&q=80',
         'available', 'Bangalore', 'Koramangala', 12.9352, 77.6245, 5000, now),

        # Ananya's Items (User 3)
        (7, 3, 'W for Woman Gold Embroidered Anarkali Kurti',
         'Deep maroon festive anarkali with delicate zari work around collar. Ideal for celebrations and family functions.',
         'Ethnic & Traditional', 'Women', 'M', 'W for Woman', 'Brand New with Tags', 'Chanderi Silk',
         2199, 'Want FabIndia kurta or raw silk dupatta',
         'https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=800&auto=format&fit=crop&q=80',
         'available', 'Bangalore', 'HSR Layout', 12.9121, 77.6446, 3500, now),
        (8, 3, 'Marks & Spencer Linen Casual Shirt',
         'Breezy white 100% pure linen button-up shirt. Elegant summer essential.',
         'Shirts & Kurtas', 'Women', 'S', 'Marks & Spencer', 'Like New', '100% Pure Linen',
         1599, 'Swap for linen trousers or jacket',
         'https://images.unsplash.com/photo-1598033129183-c4f50c736f10?w=800&auto=format&fit=crop&q=80',
         'available', 'Bangalore', 'HSR Layout', 12.9121, 77.6446, 3000, now),

        # Rohan's Items (User 4)
        (9, 4, 'Decathlon Quechua Waterproof Hiking Jacket',
         'Breathable, windproof rain jacket in dark graphite grey. Lightweight with zippered pockets.',
         'Jackets & Hoodies', 'Unisex', 'M', 'Decathlon Quechua', 'Like New', 'Waterproof Polyester',
         1399, 'Swap for gym hoodies or sports shoes',
         'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=800&auto=format&fit=crop&q=80',
         'available', 'Bangalore', 'Whitefield', 12.9698, 77.7500, 3800, now),
        (10, 4, 'Levi’s 511 Slim Fit Selvedge Denim',
         'Authentic heavyweight raw denim jeans with red line selvedge detail. Clean hem.',
         'Jeans & Trousers', 'Men', '32/32', 'Levi’s', 'Like New', '100% Selvedge Denim',
         2299, 'Looking for winter knit sweater or boots',
         'https://images.unsplash.com/photo-1582552938357-32b906df40cb?w=800&auto=format&fit=crop&q=80',
         'available', 'Bangalore', 'Whitefield', 12.9698, 77.7500, 7500, now)
    ]
    cursor.executemany('''
        INSERT INTO items (
            id, user_id, title, description, category, gender, size, brand, condition, material,
            price_inr, swap_preference, image_url, status, city, area, latitude, longitude,
            water_saved_l, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', items)

    # Safe Meeting Locations in Bangalore
    hubs = [
        (1, 'Third Wave Coffee - 12th Main', 'Bangalore', 'Indiranagar',
         '12th Main Rd, HAL 2nd Stage, Indiranagar', 'Safe Cafe Spot', '8:00 AM - 11:00 PM',
         'Popular safe cafe with good seating and friendly staff. Perfect for meeting other swappers.'),
        (2, 'Blue Tokai Coffee Roasters', 'Bangalore', 'Koramangala',
         '5th Block, Koramangala, Bangalore', 'Safe Cafe Spot', '8:30 AM - 10:30 PM',
         'Quiet cafe with outdoor seating. Verified safe meetup point.'),
        (3, 'HSR Club & Public Park Spot', 'Bangalore', 'HSR Layout',
         'Sector 2, HSR Layout, Bangalore', 'Public Meeting Spot', '9:00 AM - 8:00 PM',
         'Open public park area with plenty of parking and safe daytime atmosphere.'),
        (4, 'Phoenix Marketcity Swap Zone', 'Bangalore', 'Whitefield',
         'Whitefield Main Road, Mahadevapura', 'Mall Pickup Point', '10:00 AM - 9:30 PM',
         'Central mall lobby area with AC and security.')
    ]
    cursor.executemany('''
        INSERT INTO eco_hubs (id, name, city, area, address, hub_type, timings, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', hubs)

    # Seed one sample pending swap request for demonstration
    cursor.execute('''
        INSERT INTO swap_requests (
            id, requester_id, receiver_id, offered_item_id, requested_item_id,
            extra_cash_inr, note, status, meet_location, created_at, updated_at
        ) VALUES (
            1, 2, 1, 4, 1,
            500, 'Hi Priya! I love your FabIndia kurta. Open to swapping for my H&M denim jacket? Adding ₹500 extra to make it a great deal!',
            'pending', 'Third Wave Coffee, Indiranagar', ?, ?
        )
    ''', (now, now))

    cursor.execute('''
        INSERT INTO swap_messages (swap_id, sender_id, message, created_at)
        VALUES (1, 2, 'Hi Priya, can meet this Saturday afternoon at Indiranagar if this works for you!', ?)
    ''', (now,))

    conn.commit()

if __name__ == '__main__':
    init_db()
    print("EcoSwap Database re-initialized with Indian Currency (INR) and Login system!")
