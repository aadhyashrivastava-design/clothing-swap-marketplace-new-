# 🌿 EcoSwap — Sustainable Clothing Exchange & Barter Marketplace

> **Countering Fast Fashion & Textile Waste through a Hyperlocal Circular Barter Economy**

EcoSwap is a full-featured web platform that allows individuals to directly exchange pre-loved, wearable clothes with nearby swappers without spending money. By replacing traditional disposable fashion consumption with a peer-to-peer barter model, EcoSwap keeps quality garments in rotation, reduces landfill waste, and saves thousands of liters of clean water and kilograms of carbon emissions.

---

## 🌟 Key Features

### 1. 🛍️ Clothing Marketplace & Deep Filtering
- Browse pre-loved fashion items with high-resolution photography, size, category, condition grade, and barter scores.
- Filter dynamically by:
  - **Category**: Jackets & Coats, Sweaters & Knits, Tops & Shirts, Pants & Jeans, Dresses & Jumpsuits, Shoes, Accessories.
  - **Gender / Style**: Unisex, Women, Men.
  - **Size**: XS, S, M, L, XL, 30/30, 32/32, US 9.5, etc.
  - **Condition**: Brand New with Tags, Like New, Gently Used, Vintage / Well Loved.
  - **Radius Distance Slider**: 1 to 50 miles with live distance calculations.
  - **Sorting**: Nearest to me, Recently Listed, Highest Barter Score, Lowest Barter Score.

### 2. ⚖️ Value-Based Swap Recommendation Engine
- **Fairness Scoring Algorithm**: Evaluates item retail value, brand tier, condition grade, and sustainable material weighting (e.g. wool, organic cotton, raw denim, linen).
- **Live Equivalence Meter**: When proposing a swap, the algorithm matches the target item against all items in your wardrobe, calculating a **Fair Match Percentage (0–100%)**, verdict classification (e.g. *Perfect Fair Barter*, *Balanced Match*, *Tier Gap*), and suggests compensatory Eco-Credits if an adjustment is recommended.

### 3. 🗺️ Location-Based Matching & Community Map
- Built with **Leaflet.js** and the **Haversine formula** to calculate exact distances to nearby items and swappers.
- Shows safe **Verified Community Eco Hubs & Partner Cafes** (e.g. local eco-friendly coffee shops and textile libraries) providing secure, zero-carbon meetup spots.

### 4. 🤝 Trade Negotiation Hub & Handshake Lifecycle
- **Incoming & Outgoing Request Management**: Accept, Decline, or Cancel barter proposals.
- **In-App Coordination Chat**: Direct messaging between traders to arrange meetup details.
- **Physical Handshake / QR Verification**: Simulates in-person verification when members meet, automatically swapping item ownership, awarding +25 Eco-Credits, and updating completed swap records.

### 5. 🧥 Wardrobe Management ("List an Item")
- Add garments to your closet with real-time Barter Score calculation as you type brand, condition, and material.
- Earn **+15 Eco-Credits** immediately upon listing wearable clothes.

### 6. 🌱 Tangible Eco-Impact Dashboard
- Live tracking of:
  - **Clean Water Saved (Liters)** (e.g. 2,700L per shirt, 7,500L per pair of jeans)
  - **CO₂ Emissions Diverted (kg)**
  - **Clothing Diverted from Landfills (kg)**
  - Real-world equivalencies: 8-minute showers saved, car exhaust miles offset, and tree absorption days.

---

## 🏗️ Tech Stack

- **Backend**: Python 3.12, Flask, SQLite3, Werkzeug, Jinja2
- **Frontend**: HTML5, Tailwind CSS, Lucide Icons, Leaflet.js Interactive Maps
- **Algorithms**: Barter Score Equivalence Engine, Haversine Distance Calculator, Environmental Textile Impact Estimator
- **Architecture**: REST API endpoints with SQLite database and persistent state

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+ installed on your machine.

### 2. Installation
Open PowerShell or Terminal in the project root:

```bash
# Install dependencies
python -m pip install -r requirements.txt
```

### 3. Run the Application
```bash
python app.py
```

Open your browser and visit:
👉 **`http://127.0.0.1:5000`**

---

## 🧪 Testing Swaps Between Multiple Users (Built-in Persona Switcher)

To test the entire barter loop without creating fake accounts:
1. Click the **Profile Dropdown** in the top right corner.
2. Switch between **Maya Lin (You)**, **Liam Chen**, **Elena Rostova**, **Marcus King**, or **Zoe Thorne**.
3. As Maya, browse the marketplace, pick an item from Liam (e.g., *Carhartt WIP Chore Coat*), and click **Swap**.
4. Switch your persona to **Liam Chen** and navigate to the **Trade Hub** tab: you will see the incoming request, can chat, accept the trade, and complete the physical swap handshake!

---

## 📦 Pushing this Project to GitHub

To push this repository to your GitHub account:

### Step 1: Initialize Git and Commit
```bash
git init
git add .
git commit -m "Initial commit: EcoSwap clothing exchange & barter marketplace"
```

### Step 2: Create a Repository on GitHub
1. Go to [github.com/new](https://github.com/new).
2. Name your repository (e.g., `clothing-swap-marketplace` or `ecoswap`).
3. Leave it empty (without initializing README/license).
4. Copy the repository URL (e.g., `https://github.com/YOUR_USERNAME/ecoswap.git`).

### Step 3: Link Remote and Push
```bash
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ecoswap.git
git push -u origin main
```

---

## 🌍 The Fast Fashion Problem & Circular Solution

- **The Problem**: Over **100 billion garments** are produced annually, with **85% ending up in landfills or incinerated**. Synthetic textiles take up to 200 years to decompose.
- **The EcoSwap Solution**: By facilitating zero-cash peer barter, we lengthen garment lifespans, preserve natural resources, and empower local communities to dress sustainably.
