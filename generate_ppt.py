import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5) # Standard 4:3 academic slide

    # Color Palette (Amity Navy Blue & Gold)
    COLOR_NAVY = RGBColor(0x1A, 0x36, 0x5D)
    COLOR_DARK = RGBColor(0x1F, 0x29, 0x37)
    COLOR_MUTED = RGBColor(0x4B, 0x55, 0x63)
    COLOR_EMERALD = RGBColor(0x05, 0x96, 0x69)
    COLOR_GOLD = RGBColor(0xE6, 0x95, 0x00) # Amity Gold
    COLOR_BORDER = RGBColor(0xDC, 0xDE, 0xE2)

    blank_layout = prs.slide_layouts[6]

    def add_header_footer(slide, title_text="", slide_num=None):
        # Top Header Line
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(1.1), Inches(8.8), Inches(0.02))
        line.fill.solid()
        line.fill.fore_color.rgb = COLOR_BORDER
        line.line.color.rgb = COLOR_BORDER

        # Amity Logo Text Block (Top Left)
        tb_amity = slide.shapes.add_textbox(Inches(0.6), Inches(0.35), Inches(3.5), Inches(0.7))
        p = tb_amity.text_frame.paragraphs[0]
        r1 = p.add_run()
        r1.text = "AMITY "
        r1.font.bold = True
        r1.font.size = Pt(20)
        r1.font.color.rgb = COLOR_NAVY
        
        r2 = p.add_run()
        r2.text = "UNIVERSITY"
        r2.font.size = Pt(17)
        r2.font.bold = True
        r2.font.color.rgb = COLOR_NAVY

        p2 = tb_amity.text_frame.add_paragraph()
        r3 = p2.add_run()
        r3.text = "RAJASTHAN, JAIPUR"
        r3.font.size = Pt(8)
        r3.font.color.rgb = COLOR_GOLD
        r3.font.bold = True

        # Department / Institution Text Block (Top Right)
        tb_inst = slide.shapes.add_textbox(Inches(4.5), Inches(0.4), Inches(4.9), Inches(0.6))
        p_inst = tb_inst.text_frame.paragraphs[0]
        p_inst.alignment = PP_ALIGN.RIGHT
        r_inst = p_inst.add_run()
        r_inst.text = "Department of Computer Science & Engineering\nAmity School of Engineering & Technology"
        r_inst.font.size = Pt(9.5)
        r_inst.font.bold = True
        r_inst.font.color.rgb = COLOR_NAVY

        # Slide Title (Below header line)
        if title_text:
            tb_title = slide.shapes.add_textbox(Inches(0.6), Inches(1.2), Inches(8.8), Inches(0.6))
            p_t = tb_title.text_frame.paragraphs[0]
            r_t = p_t.add_run()
            r_t.text = title_text
            r_t.font.bold = True
            r_t.font.size = Pt(19)
            r_t.font.color.rgb = COLOR_NAVY

        # Bottom Gold Accent Bar (Amity Style on Bottom Left)
        gold_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(2.5), Inches(7.28), Inches(7.5), Inches(0.22))
        gold_bar.fill.solid()
        gold_bar.fill.fore_color.rgb = COLOR_GOLD
        gold_bar.line.fill.background()

        # Slide Number (Bottom Right)
        if slide_num is not None:
            tb_num = slide.shapes.add_textbox(Inches(9.2), Inches(6.9), Inches(0.6), Inches(0.3))
            p_n = tb_num.text_frame.paragraphs[0]
            p_n.alignment = PP_ALIGN.RIGHT
            r_n = p_n.add_run()
            r_n.text = str(slide_num)
            r_n.font.size = Pt(10)
            r_n.font.color.rgb = COLOR_MUTED

    # -------------------------------------------------------------
    # SLIDE 1: TITLE SLIDE (Matches Amity Template)
    # -------------------------------------------------------------
    slide1 = prs.slides.add_slide(blank_layout)
    add_header_footer(slide1, slide_num=1)

    tb1 = slide1.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(8.4), Inches(4.8))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p = tf1.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "EcoSwap: A Sustainable Peer-to-Peer\nClothing Exchange & Barter Marketplace"
    r.font.bold = True
    r.font.size = Pt(26)
    r.font.color.rgb = COLOR_NAVY

    p2 = tf1.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    p2.space_before = Pt(14)
    r = p2.add_run()
    r.text = "A Practical Training & Engineering Project Presentation"
    r.font.size = Pt(13)
    r.font.italic = True
    r.font.color.rgb = COLOR_MUTED

    p3 = tf1.add_paragraph()
    p3.alignment = PP_ALIGN.CENTER
    p3.space_before = Pt(8)
    r = p3.add_run()
    r.text = "Bachelor of Technology (Computer Science & Engineering) • 7th Semester\nCourse: Practical Training (B.Tech CSE)"
    r.font.size = Pt(11)
    r.font.bold = True
    r.font.color.rgb = COLOR_DARK

    p4 = tf1.add_paragraph()
    p4.alignment = PP_ALIGN.CENTER
    p4.space_before = Pt(28)
    r = p4.add_run()
    r.text = "Submitted by: [Your Name] (Enrollment No: [Your Enrollment No.])\nUnder the Guidance of: Mr./Ms./Dr. [Guide Name], Assistant Professor\nDepartment of Computer Science & Engineering, ASET, AUR"
    r.font.size = Pt(11.5)
    r.font.color.rgb = COLOR_DARK

    # Helper function for adding bullet points
    def add_bullets(tf, bullet_list, title_color=COLOR_NAVY):
        for i, (b_title, b_desc) in enumerate(bullet_list):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.space_before = Pt(10)
            p.space_after = Pt(4)
            
            r1 = p.add_run()
            r1.text = "•  " + b_title
            r1.font.bold = True
            r1.font.size = Pt(13)
            r1.font.color.rgb = title_color
            
            r2 = p.add_run()
            r2.text = b_desc
            r2.font.size = Pt(12)
            r2.font.color.rgb = COLOR_DARK

    # -------------------------------------------------------------
    # SLIDE 2: BACKGROUND & CRISIS
    # -------------------------------------------------------------
    slide2 = prs.slides.add_slide(blank_layout)
    add_header_footer(slide2, "Background: The Fast Fashion & Textile Crisis", 2)
    tb2 = slide2.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(8.4), Inches(5.0))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    add_bullets(tf2, [
        ("Explosion of Fast Fashion: ", "Rapid retail micro-seasons produce 100+ billion garments globally every year, designed for short-term consumption."),
        ("Catastrophic Textile Waste: ", "Approximately 85% of manufactured clothes end up in municipal landfills or incinerators within 12–18 months."),
        ("Excessive Natural Resource Depletion: ", "A single cotton shirt requires ~2,700 Liters of water; denim jeans require over 7,500 Liters alongside chemical dye effluents."),
        ("Urban Indian Household Dilemma: ", "Urban closets hold wearable, high-quality clothes worn only 2–5 times, but users find it inconvenient to sell or donate."),
        ("Limitations of Existing Options: ", "Second-hand platforms impose 20–35% commission fees, complex courier packaging, and high carbon delivery logistics.")
    ])

    # -------------------------------------------------------------
    # SLIDE 3: PROJECT VISION & OBJECTIVES
    # -------------------------------------------------------------
    slide3 = prs.slides.add_slide(blank_layout)
    add_header_footer(slide3, "Project Vision & Core Objectives", 3)
    tb3 = slide3.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(8.4), Inches(5.0))
    tf3 = tb3.text_frame
    tf3.word_wrap = True
    add_bullets(tf3, [
        ("Reviving the Barter Economy Model: ", "Eliminate cash commissions and platform listing fees by allowing direct peer-to-peer clothing exchanges."),
        ("Standardized Valuation in Indian Rupees (₹): ", "Avoid confusing token systems. Price items in familiar INR (₹) and use an algorithmic comparator to evaluate fair swaps."),
        ("Bridge Asymmetrical Value Swaps: ", "When garments of slightly different values are traded, automatically calculate the fair rupee difference (e.g. +₹400 balance)."),
        ("Hyperlocal Community Meetups: ", "Promote in-person exchanges at verified safe spots (cafes, metro stations) to eliminate shipping emissions and plastic mailers."),
        ("Quantifiable Environmental Accounting: ", "Track real-world liters of water saved and kilograms of CO₂ offset with every completed swap.")
    ], COLOR_EMERALD)

    # -------------------------------------------------------------
    # SLIDE 4: COMPARATIVE ANALYSIS TABLE
    # -------------------------------------------------------------
    slide4 = prs.slides.add_slide(blank_layout)
    add_header_footer(slide4, "Comparative Analysis: Existing Systems vs. EcoSwap", 4)
    table4 = slide4.shapes.add_table(5, 3, Inches(0.8), Inches(2.0), Inches(8.4), Inches(4.5)).table
    table4.columns[0].width = Inches(2.2)
    table4.columns[1].width = Inches(3.1)
    table4.columns[2].width = Inches(3.1)

    headers4 = ["Parameter", "Conventional Secondary Platforms", "EcoSwap Solution"]
    for j, h in enumerate(headers4):
        cell = table4.cell(0, j)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_NAVY
        p = cell.text_frame.paragraphs[0]
        p.runs[0].font.bold = True
        p.runs[0].font.size = Pt(11)
        p.runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    data4 = [
        ["Transaction Model", "Monetary buying & selling with 25-35% platform commission fees", "Direct peer-to-peer barter with 0% platform commission overhead"],
        ["Valuation Clarity", "Subjective price bargaining and buyer lowballing", "Transparent market price in INR (₹) + automated fair trade parity engine"],
        ["Logistics & Carbon", "Courier air/road shipping in single-use plastic mailers", "Hyperlocal in-person exchange at public safe hubs (zero packaging/emissions)"],
        ["Inventory Visibility", "Search focused on commercial retail sale", "Pre-browse local wardrobes, filter by size/condition, and propose 1:1 swaps"]
    ]
    for i, row in enumerate(data4):
        for j, val in enumerate(row):
            cell = table4.cell(i+1, j)
            cell.text = val
            p = cell.text_frame.paragraphs[0]
            p.runs[0].font.size = Pt(10)
            if j == 2:
                p.runs[0].font.bold = True
                p.runs[0].font.color.rgb = COLOR_EMERALD

    # -------------------------------------------------------------
    # SLIDE 5: SYSTEM ARCHITECTURE
    # -------------------------------------------------------------
    slide5 = prs.slides.add_slide(blank_layout)
    add_header_footer(slide5, "System Architecture & Technology Stack", 5)
    tb5 = slide5.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(8.4), Inches(5.0))
    tf5 = tb5.text_frame
    tf5.word_wrap = True
    add_bullets(tf5, [
        ("Layer 1 - Presentation Tier: ", "Modern responsive UI built with semantic HTML5, Tailwind CSS, Plus Jakarta Sans typography, and responsive grid breakpoints."),
        ("Layer 2 - Application Logic Tier: ", "Python 3.12 + Flask Framework. Lightweight WSGI controller handling RESTful JSON endpoints, session cookies, and route dispatching."),
        ("Layer 3 - Data Persistence Tier: ", "Embedded SQLite3 database engine enforcing relational constraints, foreign keys, and atomic transactions."),
        ("Decoupled REST API Architecture: ", "Clean separation between server data endpoints and asynchronous client fetch calls, eliminating disruptive full-page reloads."),
        ("Session Security & Protection: ", "Protected endpoints require valid session cookies; unauthenticated actions trigger friendly login / demo persona modals.")
    ])

    # -------------------------------------------------------------
    # SLIDE 6: VALUE MATCHING ALGORITHM
    # -------------------------------------------------------------
    slide6 = prs.slides.add_slide(blank_layout)
    add_header_footer(slide6, "Value-Based Swap Recommendation Engine (INR ₹)", 6)
    tb6 = slide6.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(8.4), Inches(5.0))
    tf6 = tb6.text_frame
    tf6.word_wrap = True
    add_bullets(tf6, [
        ("Absolute Differential (ΔP): ", "ΔP = |P_target - P_offer| in Indian Rupees (₹)."),
        ("Trade Parity Percentage (M): ", "M = round( min(P_offer, P_target) / max(P_offer, P_target) * 100 )."),
        ("Case 1 - Balanced Trade (ΔP ≤ ₹250): ", "Classified as '⭐️ Perfect Fair 1-to-1 Swap'. No monetary adjustment required."),
        ("Case 2 - Target Item Higher (P_target > P_offer, ΔP > ₹250): ", "System suggests offering ΔP as extra cash or UPI sweetener (e.g. +₹400)."),
        ("Case 3 - Offered Item Higher (P_offer > P_target, ΔP > ₹250): ", "System advises requester they hold higher value, allowing direct swap or counter-request.")
    ], COLOR_EMERALD)

    # -------------------------------------------------------------
    # SLIDE 7: DATABASE DESIGN
    # -------------------------------------------------------------
    slide7 = prs.slides.add_slide(blank_layout)
    add_header_footer(slide7, "Relational Database Schema (3NF SQLite)", 7)
    table7 = slide7.shapes.add_table(6, 4, Inches(0.8), Inches(1.9), Inches(8.4), Inches(4.7)).table
    table7.columns[0].width = Inches(1.6)
    table7.columns[1].width = Inches(1.1)
    table7.columns[2].width = Inches(1.8)
    table7.columns[3].width = Inches(3.9)

    headers7 = ["Table", "Primary Key", "Foreign Key", "Key Attributes & Purpose"]
    for j, h in enumerate(headers7):
        cell = table7.cell(0, j)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_NAVY
        p = cell.text_frame.paragraphs[0]
        p.runs[0].font.bold = True
        p.runs[0].font.size = Pt(10.5)
        p.runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    data7 = [
        ["users", "id", "None", "name, email, password, phone, city, area, swaps_completed"],
        ["items", "id", "user_id -> users(id)", "title, category, gender, size, brand, condition, price_inr, status, water_saved_l"],
        ["swap_requests", "id", "requester_id, receiver_id\noffered_id, requested_id", "extra_cash_inr, note, status (pending/accepted/completed), meet_location"],
        ["swap_messages", "id", "swap_id, sender_id", "message string, created_at timestamp for trade coordination"],
        ["eco_hubs", "id", "None", "name, city, area, address, hub_type, timings, safe meetup info"]
    ]
    for i, row in enumerate(data7):
        for j, val in enumerate(row):
            cell = table7.cell(i+1, j)
            cell.text = val
            p = cell.text_frame.paragraphs[0]
            p.runs[0].font.size = Pt(9.5)

    # -------------------------------------------------------------
    # SLIDE 8: MARKETPLACE & WARDROBE
    # -------------------------------------------------------------
    slide8 = prs.slides.add_slide(blank_layout)
    add_header_footer(slide8, "Core Module: Marketplace & Wardrobe Cataloging", 8)
    tb8 = slide8.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(8.4), Inches(5.0))
    tf8 = tb8.text_frame
    tf8.word_wrap = True
    add_bullets(tf8, [
        ("Multi-Attribute Search & Filter: ", "Filter dynamically by Category (Ethnic, Tops, Shirts, Jeans, Jackets, Shoes, Bags), Gender, Condition, and Price Sort."),
        ("Rich Garment Cards in INR: ", "Displays realistic market valuation (e.g. FabIndia Kurta ₹1,499, Levi's Jeans ₹1,299), condition grade, size tag, and owner locality."),
        ("Wardrobe Management ('Upload Clothes'): ", "Users can list dormant garments from their closet, specifying condition, material, asking wishlist, and photos."),
        ("Own-Item Filter Optimization: ", "When logged in, the marketplace automatically excludes the user's own clothes to prevent self-swaps while prioritizing local listings."),
        ("Resource Savings Tag: ", "Every listed garment displays its clean water conservation metric (e.g., 💧 2,700L Water Saved).")
    ])

    # -------------------------------------------------------------
    # SLIDE 9: SWAP PROPOSAL & TRADE HUB
    # -------------------------------------------------------------
    slide9 = prs.slides.add_slide(blank_layout)
    add_header_footer(slide9, "Core Module: Swap Proposal & Trade Lifecycle", 9)
    tb9 = slide9.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(8.4), Inches(5.0))
    tf9 = tb9.text_frame
    tf9.word_wrap = True
    add_bullets(tf9, [
        ("Interactive 'Propose Swap' Flow: ", "Clicking 'Swap' on any item opens a modal displaying the user's wardrobe items ranked by value compatibility."),
        ("Live Equivalence Feedback: ", "Instantly informs user: '⭐️ Perfect Fair 1-to-1 Swap!' or 'Their garment is worth ₹400 more; offer ₹400 cash/UPI balance'."),
        ("Trade Lifecycle States: ", "Structured workflow: PENDING -> ACCEPTED / DECLINED -> COMPLETED / CANCELLED."),
        ("Item Lock on Acceptance: ", "When a proposal is accepted, both garments shift to 'pending_swap' status to prevent double-booking with other users."),
        ("Atomic Ownership Transfer: ", "Confirming completed swap automatically reassigns garment user IDs in SQLite and increments completed swap counters.")
    ], COLOR_EMERALD)

    # -------------------------------------------------------------
    # SLIDE 10: IN-APP CHAT & SAFE HUBS
    # -------------------------------------------------------------
    slide10 = prs.slides.add_slide(blank_layout)
    add_header_footer(slide10, "In-App Negotiation Chat & Safe Meetup Hubs", 10)
    tb10 = slide10.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(8.4), Inches(5.0))
    tf10 = tb10.text_frame
    tf10.word_wrap = True
    add_bullets(tf10, [
        ("Integrated Swap Coordination Chat: ", "Linked directly to the swap transaction ID. Allows traders to arrange meetup schedules without exchanging private contact numbers."),
        ("Verified Public Safe Spots: ", "Pre-configured directory of safe public meetup locations across Bangalore (Third Wave Coffee Indiranagar, Blue Tokai Koramangala, Metro Stations)."),
        ("Eliminating Domestic Privacy Risks: ", "Encourages daylight meetings in well-monitored commercial hubs rather than home visits."),
        ("Zero Courier Delivery Overhead: ", "Physical in-person exchange entirely bypasses postal delays, courier transit costs, and cardboard packaging waste."),
        ("Demo Multi-Persona Switcher: ", "Enables examiners to test swaps seamlessly by switching between Priya, Rahul, Ananya, and Rohan in 1 click.")
    ])

    # -------------------------------------------------------------
    # SLIDE 11: TESTING METHODOLOGY
    # -------------------------------------------------------------
    slide11 = prs.slides.add_slide(blank_layout)
    add_header_footer(slide11, "Testing Methodology & Verification Results", 11)
    tb11 = slide11.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(8.4), Inches(5.0))
    tf11 = tb11.text_frame
    tf11.word_wrap = True
    add_bullets(tf11, [
        ("Automated Test Suite (test_app.py): ", "Utilizes Python's standard unittest framework to execute programmatically isolated test clients."),
        ("TC-01 Homepage Route Verification: ", "Validates HTTP 200 status code and template DOM integrity."),
        ("TC-02 Authentication & Session State: ", "Verifies credential validation, session cookie generation, and user profile retrieval on /api/me."),
        ("TC-03 Rupee Valuation Constraints: ", "Validates that all catalog items possess valid price_inr integers (price_inr >= 100)."),
        ("TC-04 Barter Parity Comparison: ", "Asserts correct difference_inr calculation and equitable settlement advice."),
        ("High Execution Velocity: ", "All 4 core test suites ran and passed in 0.055 seconds with 100% test pass rate.")
    ], COLOR_EMERALD)

    # -------------------------------------------------------------
    # SLIDE 12: ENVIRONMENTAL IMPACT
    # -------------------------------------------------------------
    slide12 = prs.slides.add_slide(blank_layout)
    add_header_footer(slide12, "Environmental Accounting & Circular Impact", 12)
    tb12 = slide12.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(8.4), Inches(5.0))
    tf12 = tb12.text_frame
    tf12.word_wrap = True
    add_bullets(tf12, [
        ("Every Garment Kept in Rotation Saves: ", "Approximately 2,700 Liters of water for shirts and 7,500 Liters for heavy denim trousers."),
        ("Carbon Emission Offsetting: ", "Diverts 8.5 kg to 18 kg of CO₂ emissions per garment that would otherwise be expended in industrial production."),
        ("Textile Landfill Diversion: ", "Prevents synthetic polyester blends from languishing in landfills for centuries where they release microplastics."),
        ("Tangible Everyday Metrics: ", "Calculates intuitive equivalencies: equivalent 8-minute showers preserved and car travel miles offset."),
        ("Aligning Tech with SDG 12: ", "Directly supports United Nations Sustainable Development Goal 12: Responsible Consumption and Production.")
    ])

    # -------------------------------------------------------------
    # SLIDE 13: CHALLENGES OVERCOME
    # -------------------------------------------------------------
    slide13 = prs.slides.add_slide(blank_layout)
    add_header_footer(slide13, "Key Engineering Challenges & Solutions", 13)
    tb13 = slide13.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(8.4), Inches(5.0))
    tf13 = tb13.text_frame
    tf13.word_wrap = True
    add_bullets(tf13, [
        ("Windows Console Character Encoding (cp1252): ", "Resolved UnicodeEncodeError when printing the Rupee glyph (₹) to Windows PowerShell stdout by standardizing console outputs to ASCII descriptors ('Rs.') while keeping full UTF-8 for web clients."),
        ("Socket Lifecycle & Port Binding: ", "Handled lingering background process socket locks on port 5000 using PowerShell process inspection and binding to 0.0.0.0."),
        ("State Synchronization & Responsive Rendering: ", "Implemented defensive checks in frontend controllers to prevent delayed third-party script loading from interrupting UI initialization."),
        ("Multi-User Barter Simulation: ", "Built seamless 1-click demo persona logins to allow testing both proposal sender and receiver interactions without browser incognito toggling.")
    ], COLOR_GOLD)

    # -------------------------------------------------------------
    # SLIDE 14: FUTURE SCOPE & CONCLUSION
    # -------------------------------------------------------------
    slide14 = prs.slides.add_slide(blank_layout)
    add_header_footer(slide14, "Future Scope & Conclusion", 14)
    tb14 = slide14.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(8.4), Inches(5.0))
    tf14 = tb14.text_frame
    tf14.word_wrap = True
    add_bullets(tf14, [
        ("Computer Vision Quality Grading: ", "Integrate lightweight on-device CNN models (e.g. MobileNet) to auto-detect garment stains, fabric wear, and verify brand tags."),
        ("Automated UPI Micro-Escrow: ", "Integrate UPI payment gateway for holding recommended balance sweeteners until in-person QR handshake completion."),
        ("Cross-Platform Mobile Apps: ", "Build native React Native / Flutter apps taking advantage of push notifications and camera upload."),
        ("Conclusion: ", "EcoSwap demonstrates that digital engineering can revive sustainable community barter, reducing textile waste and promoting a conscious circular fashion economy.")
    ])

    # -------------------------------------------------------------
    # SLIDE 15: THANK YOU / Q&A
    # -------------------------------------------------------------
    slide15 = prs.slides.add_slide(blank_layout)
    add_header_footer(slide15, slide_num=15)
    tb15 = slide15.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(8.0), Inches(4.0))
    tf15 = tb15.text_frame

    p = tf15.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "THANK YOU!"
    r.font.bold = True
    r.font.size = Pt(36)
    r.font.color.rgb = COLOR_NAVY

    p2 = tf15.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    p2.space_before = Pt(14)
    r = p2.add_run()
    r.text = "Questions & Discussion\n\nEcoSwap — Sustainable Clothing Exchange & Barter Platform\nReady for GitHub Deployment & Live Demonstration"
    r.font.size = Pt(14)
    r.font.color.rgb = COLOR_DARK

    output_ppt = "EcoSwap_College_Presentation.pptx"
    prs.save(output_ppt)
    print(f"Presentation successfully generated and saved to: {output_ppt}")

if __name__ == '__main__':
    create_presentation()
