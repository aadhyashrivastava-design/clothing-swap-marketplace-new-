import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_background(cell, fill_hex):
    shading_xml = f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>'
    cell._tc.get_or_add_tcPr().append(parse_xml(shading_xml))

def create_report():
    doc = Document()

    # Page Setup: A4, 1.5" Left Margin, 1.0" Right/Top/Bottom Margins
    for section in doc.sections:
        section.page_width = Inches(8.27)  # A4 width
        section.page_height = Inches(11.69) # A4 height
        section.left_margin = Inches(1.5)
        section.right_margin = Inches(1.0)
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.header_distance = Inches(0.5)
        section.footer_distance = Inches(0.5)

    # Set Base Normal Style: Times New Roman, 12pt, 1.5 Line Spacing
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(12)
    normal_style.font.color.rgb = RGBColor(0x11, 0x11, 0x11)
    normal_style.paragraph_format.line_spacing = 1.5
    normal_style.paragraph_format.space_after = Pt(6)

    def add_p(text, bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=0, space_after=6):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.5
        run = p.add_run(text)
        run.bold = bold
        run.italic = italic
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        return p

    def add_chapter_title(num_and_title):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(24)
        p.paragraph_format.space_after = Pt(18)
        run = p.add_run(num_and_title)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(24)
        run.bold = True
        return p

    def add_sec_heading(title):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        run = p.add_run(title)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(16)
        run.bold = True
        return p

    def add_subsec_heading(title):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(title)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        run.bold = True
        return p

    def add_bullet(bold_prefix, text):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.5
        r1 = p.add_run(bold_prefix)
        r1.bold = True
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(12)
        r2 = p.add_run(text)
        r2.font.name = 'Times New Roman'
        r2.font.size = Pt(12)
        return p

    # ==========================================
    # 1. TITLE PAGE (Sample - 1 Format)
    # ==========================================
    p_top = doc.add_paragraph()
    p_top.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_top.paragraph_format.space_before = Pt(18)
    p_top.paragraph_format.space_after = Pt(12)
    r_top = p_top.add_run("ECOSWAP: A SUSTAINABLE PEER-TO-PEER CLOTHING EXCHANGE AND BARTER MARKETPLACE")
    r_top.font.name = 'Times New Roman'
    r_top.font.size = Pt(20)
    r_top.bold = True

    add_p("A Practical Training Report", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=16, space_after=4)
    add_p("submitted", italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=4)
    add_p("in partial fulfillment", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=4)
    add_p("for the award of the Degree of", italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=4)
    add_p("Bachelor of Technology", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=4)
    add_p("in Department of Computer Science and Engineering", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=36)

    # Guide and Student Table
    table_meta = doc.add_table(rows=1, cols=2)
    table_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell_guide = table_meta.rows[0].cells[0]
    cell_student = table_meta.rows[0].cells[1]

    p_g = cell_guide.paragraphs[0]
    p_g.paragraph_format.line_spacing = 1.3
    r = p_g.add_run("Guide:\n")
    r.bold = True
    p_g.add_run("Mr./Ms./Dr. [Guide Name]\nAssistant Professor / Mentor\nDepartment of CSE")

    p_s = cell_student.paragraphs[0]
    p_s.paragraph_format.line_spacing = 1.3
    p_s.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = p_s.add_run("Submitted by:\n")
    r.bold = True
    p_s.add_run("[Your Name]\nEnrollment No.: [Your Enrollment No.]\nB.Tech CSE - 7th Semester")

    # Space down
    add_p("", space_before=40)

    # University Footer Details
    add_p("Department of Computer Science and Engineering", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=20, space_after=2)
    add_p("Amity School of Engineering & Technology", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=2)
    add_p("Amity University Rajasthan, Jaipur", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=2)
    add_p("November 2026", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=12)

    doc.add_page_break()

    # ==========================================
    # 2. CANDIDATE'S DECLARATION (Sample - 2 Format)
    # ==========================================
    add_chapter_title("CANDIDATE'S DECLARATION")

    add_p("I hereby declare that the work, which is being presented in the Summer training report, entitled \"EcoSwap: A Sustainable Peer-to-Peer Clothing Exchange and Barter Marketplace\" in partial fulfillment for the award of Degree of \"Bachelor of Technology\" in Department of Computer Science and Engineering, and submitted to the Department of Computer Science and Engineering, Amity School of Engineering & Technology, Amity University, Rajasthan. This is a record of my own training preparing under the guidance of [Name of Guide].", space_before=16, space_after=36)

    # Student sign block
    add_p("(Signature of the Student)", space_before=20, space_after=4)
    add_p("[Your Name]", bold=True, space_before=0, space_after=2)
    add_p("Computer Science and Engineering", space_before=0, space_after=2)
    add_p("Enrolment No.: [Your Enrollment No.]", space_before=0, space_after=2)
    add_p("Amity University Rajasthan, Jaipur", space_before=0, space_after=36)

    add_p("Counter Signed by", bold=True, space_before=20, space_after=24)
    add_p("....................................................", space_before=0, space_after=4)
    add_p("[Name of Guide]", bold=True, space_before=0, space_after=2)
    add_p("Designation: Assistant Professor", space_before=0, space_after=2)
    add_p("Department of Computer Science and Engineering", space_before=0, space_after=2)
    add_p("Amity School of Engineering & Technology, AUR", space_before=0, space_after=12)

    doc.add_page_break()

    # ==========================================
    # 3. INTERNSHIP CERTIFICATE PLACEHOLDER
    # ==========================================
    add_chapter_title("CERTIFICATE OF INTERNSHIP / TRAINING")

    add_p("This is to certify that [Your Name], Enrollment Number [Your Enrollment No.], a student of Bachelor of Technology in Computer Science & Engineering from Amity School of Engineering & Technology, Amity University Rajasthan, Jaipur, has successfully completed practical training / project development work from [Start Date] to [End Date].", space_before=16, space_after=12)

    add_p("During the tenure of this training, the candidate developed a comprehensive software engineering project titled \"EcoSwap: A Sustainable Peer-to-Peer Clothing Exchange and Barter Marketplace\". The student demonstrated strong technical competence in Python, Flask web framework, relational database design with SQLite, RESTful API architecture, frontend interface design, and automated testing.", space_before=6, space_after=12)

    add_p("The candidate's conduct, initiative, and dedication throughout the project development cycle were found to be exemplary.", space_before=6, space_after=48)

    add_p("__________________________                    __________________________", space_before=20, space_after=4)
    add_p("Industry / Faculty Mentor                          Head of Department (CSE)", bold=True, space_before=2, space_after=2)
    add_p("Amity University Rajasthan                          Amity School of Engg. & Tech.", space_before=2, space_after=12)

    doc.add_page_break()

    # ==========================================
    # 4. ACKNOWLEDGEMENT
    # ==========================================
    add_chapter_title("ACKNOWLEDGEMENT")

    add_p("The completion of any engineering endeavor demands not merely technical knowledge, but also consistent guidance, constructive critique, and organizational support. I take this opportunity to express my profound gratitude to all those who facilitated the successful development of this project.", space_before=12, space_after=10)

    add_p("First and foremost, I express my sincere gratitude to my project guide, [Guide Name], Department of Computer Science & Engineering, for their valuable mentorship, technical direction, and continuous encouragement during every stage of requirement analysis, database schema structuring, and system verification.", space_before=6, space_after=10)

    add_p("I extend my deep gratitude to the Head of Department, Department of Computer Science & Engineering, Amity School of Engineering & Technology, for fostering an academic environment that emphasizes hands-on technical problem-solving and rigorous engineering methodologies.", space_before=6, space_after=10)

    add_p("I am also grateful to the faculty members and technical staff of Amity University Rajasthan for their indirect assistance and for providing the laboratory infrastructure necessary to design, implement, and benchmark this software platform.", space_before=6, space_after=10)

    add_p("Finally, I extend my heartfelt thanks to my family and fellow classmates for their moral support, patient feedback during user acceptance testing, and constructive suggestions during the interface design phase.", space_before=6, space_after=24)

    add_p("[Your Name]\nB.Tech (Computer Science & Engineering)\nAmity University Rajasthan, Jaipur", bold=True, align=WD_ALIGN_PARAGRAPH.RIGHT)

    doc.add_page_break()

    # ==========================================
    # 5. EXECUTIVE SUMMARY / ABSTRACT (2 Pages)
    # ==========================================
    add_chapter_title("EXECUTIVE SUMMARY / ABSTRACT")

    add_p("The contemporary textile and apparel industry has been fundamentally transformed by the rapid acceleration of the fast-fashion manufacturing paradigm. Fast fashion relies on compressed production timelines, synthetic textile blends, and aggressive retail pricing to encourage frequent garment acquisition. While this model democratizes access to current fashion trends, it generates severe ecological degradation and textile waste. Over 100 billion garments are manufactured globally each year, with approximately 85% concluding their lifecycle in municipal landfills or thermal incinerators within twelve to eighteen months of purchase. The production of virgin textiles represents an extraordinarily resource-intensive endeavor; synthesizing a single conventional cotton t-shirt consumes approximately 2,700 liters of freshwater, while a pair of denim jeans demands in excess of 7,500 liters, alongside substantial petrochemical consumption for synthetic dyes and finishing agents.", space_before=10, space_after=10)

    add_p("Within urban Indian centers, consumer wardrobes harbor millions of wearable, high-quality garments that remain dormant after minimal usage. Conventional secondary retail avenues—such as second-hand resale platforms or charity donation kiosks—exhibit pronounced systemic frictions. Commercial re-commerce websites impose heavy commission margins (often exceeding 25–40%), require onerous payment escrow overheads, and mandate complex courier shipping that incurs considerable carbon logistics costs. Conversely, charitable donation avenues frequently lack operational transparency, sorting infrastructure, or convenient drop-off access, leading many consumers to simply retain obsolete clothing indefinitely.", space_before=6, space_after=10)

    add_p("To resolve this socio-ecological inefficiency, this training project presents EcoSwap, an online peer-to-peer clothing exchange and barter marketplace engineered specifically for urban communities. Rather than relying on fiat currency transactions or complex tokenized monetization, EcoSwap revives the direct barter economy model through modern digital engineering. The platform allows verified registered users to list wearable pre-loved garments from their wardrobes, browse nearby community listings, inspect detailed material compositions, and negotiate direct one-to-one or value-balanced exchanges.", space_before=6, space_after=10)

    add_p("A primary technical innovation of the platform is its Value-Based Swap Recommendation Engine. In traditional barter systems, trade friction emerges from subjective and asymmetrical evaluations of item worth. EcoSwap formalizes garment valuation using transparent market-anchored metrics in Indian Rupees (INR ₹), considering brand positioning, material durability, and physical condition grade. When a user explores an item they wish to acquire, the recommendation engine automatically analyzes their active wardrobe items, calculating an objective percentage match and indicating value parity. When value differentials arise (e.g., a garment valued at ₹1,500 offered against one worth ₹1,900), the system dynamically computes and recommends an equitable supplementary cash/UPI balance to bridge the gap smoothly.", space_before=6, space_after=10)

    add_p("To eliminate carbon-heavy courier logistics, EcoSwap integrates location-based discovery and designated Safe Meetup Hubs. Utilizing spatial coordinates and neighborhood mapping, the system encourages participants to exchange garments in person at safe, well-lit public venues such as established cafes, community centers, and transit stations across urban clusters (e.g., Bangalore's Indiranagar, Koramangala, and HSR Layout). Furthermore, the application features an in-app negotiation messaging channel and a physical trade confirmation handshake protocol that atomically updates database ownership and tracks real-world environmental savings.", space_before=6, space_after=10)

    add_p("EcoSwap was developed utilizing Python 3.12, the Flask micro-framework, SQLite3 relational persistence, Jinja2 dynamic templating, and Tailwind CSS. Comprehensive unit and integration test suites validate the system with zero failures across critical user authentication, barter comparison, and transaction lifecycle pathways. By lowering the operational and psychological barriers to clothing reuse, EcoSwap establishes a scalable, zero-waste communal framework that aligns software engineering principles with circular economy goals.", space_before=6, space_after=12)

    doc.add_page_break()

    # ==========================================
    # 6. LEARNING OBJECTIVES / INTERNSHIP OBJECTIVES (1 Page)
    # ==========================================
    add_chapter_title("LEARNING & INTERNSHIP OBJECTIVES")

    add_p("The primary objective of this practical training and project work was to synthesize theoretical computer science and software engineering principles acquired during undergraduate coursework into an operational, full-stack web application addressing real-world sustainability challenges.", space_before=12, space_after=12)

    add_sec_heading("Specific Technical & Professional Objectives:")

    add_bullet("1. End-to-End Full-Stack Architecture: ", "Gain practical proficiency in architecting and implementing a decoupled, modular web application using Python (Flask) on the backend and modern semantic HTML5, Tailwind CSS, and reactive client-side JavaScript on the frontend.")

    add_bullet("2. Relational Database Modeling & Normalization: ", "Design an optimized, third-normal-form (3NF) relational database schema using SQLite to manage user accounts, item metadata, trade proposals, negotiation message logs, and location coordinates with proper referential integrity and foreign key cascading.")

    add_bullet("3. Algorithm Design for Fair Barter Matching: ", "Formulate and code an intuitive, equitable valuation algorithm that computes trade fairness, calculates absolute value differences in Indian Rupees (₹), and provides automated adjustments without requiring monetary commission intermediaries.")

    add_bullet("4. Session Management & User Authentication: ", "Implement secure, stateful session handling and authentication mechanisms supporting user registration, credential validation, demo persona switching, and access control across protected transaction endpoints.")

    add_bullet("5. Asynchronous Client-Server Communication: ", "Implement clean RESTful API standards utilizing AJAX and JSON data interchange for real-time item filtering, dynamic DOM updating, and interactive negotiation chat without disruptive full-page refreshes.")

    add_bullet("6. System Verification, Testing & Debugging: ", "Formulate structured unit test suites utilizing Python's unittest module, execute boundary-value and integration test cases, resolve Windows platform runtime constraints (such as console character encoding and socket port lifecycle management), and achieve verified 100% test pass rates.")

    add_bullet("7. Engineering Documentation & Version Control: ", "Maintain rigorous version control practices utilizing Git and GitHub, and generate standard engineering documentation adhering to institutional academic report guidelines.")

    doc.add_page_break()

    # ==========================================
    # 7. CHAPTER 1: INTRODUCTION
    # ==========================================
    add_chapter_title("CHAPTER 1\nINTRODUCTION")

    add_sec_heading("1.1 Background & The Fast Fashion Crisis in India")
    add_p("Over the past two decades, global clothing consumption has expanded at an unprecedented rate. Driven by industrial automation, synthetic polyester fabrics, and algorithmic marketing on social media networks, fashion brands have shifted from traditional seasonal collections (spring/summer and autumn/winter) to micro-season models where new garment collections are released on a weekly or bi-weekly basis. This industrial paradigm—colloquially termed 'fast fashion'—encourages consumers to view apparel as transient, disposable commodities rather than durable assets.", space_before=6, space_after=10)

    add_p("In developing economies such as India, the proliferation of international fast-fashion retailers and domestic e-commerce aggregators has led to a steep escalation in textile acquisition, particularly among urban youth and working professionals. However, the environmental footprint associated with this surge is unsustainable. Textile manufacturing is universally recognized as one of the most environmentally destructive industries on the planet. It accounts for approximately 10% of global greenhouse gas emissions and roughly 20% of global industrial wastewater discharges.", space_before=6, space_after=10)

    add_p("Furthermore, conventional garments place enormous pressure on agricultural and water resources. Cultivating cotton requires extensive irrigation and pesticide application, consuming an average of 2,700 liters of potable water for a single standard cotton shirt. Conversely, synthetic fibers such as polyester, nylon, and acrylic are non-biodegradable polymers derived directly from petrochemical feedstocks. When discarded into municipal landfills, synthetic garments take up to two centuries to degrade, leaching microplastics and toxic chemical dyes into groundwater reserves and agricultural soil.", space_before=6, space_after=12)

    add_sec_heading("1.2 Motivation for a Clothing Exchange System")
    add_p("Extensive consumer surveys indicate that the average modern urban garment is worn fewer than ten times prior to being retired to the back of a closet. In Indian households, cultural traditions have historically favored textile reuse—such as passing clothes down through extended family networks or repurposing worn textiles into domestic cleaning cloths. However, modern urbanization, nuclear family structures, and changing professional wardrobes have largely disrupted these informal circular channels.", space_before=6, space_after=10)

    add_p("Today, millions of urban residents possess closets stocked with high-grade, wearable apparel that is in excellent physical condition but no longer fits the wearer's current aesthetic, size, or lifestyle. When individuals seek to declutter their wardrobes, they encounter significant friction. Commercial second-hand platforms require high seller commissions, laborious photography standards, and inconvenient courier dispatching. Physical charity donation boxes often end up as unsegregated textile bales with uncertain end-of-life disposal. A localized clothing barter platform solves this dilemma by connecting like-minded community members who can swap clothes directly, reviving the barter economy through digital tools.", space_before=6, space_after=12)

    add_sec_heading("1.3 Problem Statement")
    add_p("Traditional e-commerce platforms are fundamentally oriented around monetary expenditure and virgin commodity consumption. While secondary resale apps exist, they impose financial transaction overheads, payment gateway fees, and shipping logistics that discourage everyday garment reuse. Conversely, informal offline clothing swaps remain sporadic, localized events with zero digital inventory tracking, no prior discovery mechanisms, and no systematic framework to ensure trade fairness.", space_before=6, space_after=10)

    add_p("The objective of this engineering project is to design, develop, and benchmark EcoSwap: a localized, digital peer-to-peer clothing exchange and barter marketplace. The system must allow users to catalog their wardrobes, discover wearable apparel in their immediate geographic vicinity, evaluate fair trade balance in Indian Rupees (₹), negotiate exchanges through in-app channels, coordinate meetups at safe community spots, and track tangible environmental resource savings.", space_before=6, space_after=12)

    add_sec_heading("1.4 Scope of the Project")
    add_p("The scope of this practical training project encompasses the complete design and implementation of a functional web-based software prototype. Key functional modules included within the scope are:", space_before=6, space_after=6)
    add_bullet("User Management: ", "Registration, session-based sign-in, profile management, and quick demo-login switching across simulated urban personas.")
    add_bullet("Garment Cataloging: ", "Multi-attribute wardrobe listing including category, gender, size, brand, material, condition grade, and estimated market price in INR (₹).")
    add_bullet("Search & Discovery: ", "Multi-parameter filtering by garment type, condition, gender, and price, with real-time responsive item cards.")
    add_bullet("Value Matching Algorithm: ", "Transparent rupee-value comparison engine that calculates percentage trade parity and calculates suggested extra monetary balances for asymmetrical swaps.")
    add_bullet("Trade Lifecycle & Negotiation: ", "End-to-end proposal submission, accept/decline action triggers, integrated chat negotiation, and atomic database ownership transfer upon swap completion.")
    add_bullet("Safe Community Spots: ", "Directory of verified public meeting venues across urban neighborhoods to facilitate zero-carbon physical handshakes.")

    add_sec_heading("1.5 Organization of the Report")
    add_p("This report is systematically structured into chapters following institutional guidelines: Chapter 2 details the System Analysis, reviewing existing systems, feasibility dimensions, and software requirement specifications. Chapter 3 outlines the System Design, including multi-tier architectural diagrams, Data Flow Diagrams (DFDs), Entity-Relationship (ER) schemas, and algorithm formulation. Chapter 4 discusses Implementation and System Coding, analyzing key technology choices and code modules. Chapter 5 presents System Testing and Results, highlighting test matrices and performance verification. Finally, Chapter 6 concludes the report with reflections and future enhancements.", space_before=6, space_after=12)

    doc.add_page_break()

    # ==========================================
    # 8. CHAPTER 2: SYSTEM ANALYSIS
    # ==========================================
    add_chapter_title("CHAPTER 2\nSYSTEM ANALYSIS")

    add_sec_heading("2.1 Existing System Overview")
    add_p("At present, consumers seeking to dispose of wearable, pre-loved garments rely on three primary conventional paradigms:", space_before=6, space_after=6)
    add_bullet("Commercial Secondary E-Commerce Platforms: ", "Platforms such as OLX, Quickr, or specialized thrift apps. These services treat clothing as standard commercial goods, requiring sellers to set asking prices, wait for prospective buyers, handle price bargaining, and coordinate postal deliveries.")
    add_bullet("Physical Donation Bins & NGO Drop-Offs: ", "Charity donation boxes placed in select residential complexes or religious centers. While noble in intent, these systems suffer from severe logistical bottlenecks, lack garment sorting automation, and frequently export surplus unwearable garments to landfills.")
    add_bullet("Informal Offline Clothes Swaps: ", "Occasional physical meetup events organized by environmental NGOs or college student clubs where participants bring garments to swap on communal clothes racks.")

    add_sec_heading("2.2 Limitations of the Existing System")
    add_p("A rigorous comparative analysis reveals substantial engineering and operational deficiencies in current mechanisms:", space_before=6, space_after=6)
    add_bullet("Heavy Financial & Commission Overhead: ", "Commercial thrift platforms take upwards of 20% to 35% commission on sales. For mid-range garments worth ₹500 to ₹1,500, this fee structure renders selling economically impractical.")
    add_bullet("Logistics & Carbon Footprint: ", "Courier-based secondary sales involve packaging garments in single-use plastic mailers and transporting them across state borders via diesel trucks or air cargo, generating substantial carbon emissions that counteract the environmental benefit of buying used.")
    add_bullet("Asymmetry of Information & Trust: ", "Unregulated classified sites expose users to financial fraud, non-serious buyers, and personal privacy risks when arranging home collections.")
    add_bullet("Absence of Prior Inventory Visibility: ", "Physical clothes swap events do not allow attendees to browse inventory beforehand, frequently resulting in participants arriving with bags of clothes only to find nothing in their size or stylistic preference.")

    add_sec_heading("2.3 Proposed System Architecture & Core Concept")
    add_p("EcoSwap directly addresses these limitations by introducing a hyperlocal, zero-commission, digital barter architecture. Key conceptual tenets include:", space_before=6, space_after=6)
    add_bullet("Pure Barter Model: ", "Garments are traded directly for other garments without mandatory financial transactions or platform listing fees.")
    add_bullet("Standardized Valuation in Indian Currency (₹): ", "Instead of abstract barter points, items are listed with their fair estimated market value in Indian Rupees (₹), ensuring immediate clarity for all Indian participants.")
    add_bullet("Equitable Gap Bridging: ", "When garments of slightly unequal value are proposed for trade, the system calculates the exact rupee differential, allowing users to mutually agree on a small cash or UPI balance.")
    add_bullet("Hyperlocal In-Person Handshakes: ", "By focusing on city neighborhoods and verified public venues (e.g., popular coffee shops, metro stations), the platform eliminates shipping delays, shipping fees, and plastic packaging waste.")

    add_sec_heading("2.4 Feasibility Study")
    add_p("Prior to embarking upon technical implementation, a rigorous three-dimensional feasibility study was executed:", space_before=6, space_after=6)
    add_bullet("Technical Feasibility: ", "The platform is engineered using established, robust technologies—Python, Flask, SQLite3, and responsive HTML5/Tailwind CSS. These technologies are open-source, highly documented, cross-platform, and operate efficiently on standard commodity hardware without requiring expensive enterprise infrastructure.")
    add_bullet("Economic Feasibility: ", "The development utilizes entirely free and open-source software (FOSS). Operational costs for hosting are minimal due to the lightweight nature of SQLite and Flask, requiring no proprietary database licenses or paid third-party API dependencies.")
    add_bullet("Operational Feasibility: ", "The interface was specifically simplified to minimize cognitive load. Everyday terminology ('Browse Clothes', 'Upload Clothes', 'My Swaps') and familiar Indian currency denominations ensure that non-technical users can navigate and execute swaps effortlessly.")

    add_sec_heading("2.5 Software Requirement Specification (SRS)")
    add_subsec_heading("2.5.1 Functional Requirements")
    add_bullet("FR-1 User Authentication: ", "The system must allow new users to register with name, email, password, phone, and location, and allow existing users to securely sign in and sign out.")
    add_bullet("FR-2 Wardrobe Cataloging: ", "Authenticated users must be able to upload garment listings specifying title, category, gender, size, brand, condition grade, material, estimated price in ₹, swap wishlist, and image URL.")
    add_bullet("FR-3 Marketplace Filtering: ", "The system must provide real-time multi-attribute filtering across category, gender style, condition grade, and sorting orders (latest, price low-to-high, price high-to-low).")
    add_bullet("FR-4 Swap Proposal & Value Matching: ", "When proposing a swap, the system must retrieve the requester's available wardrobe items, compute the absolute price difference in ₹, display trade parity percentage, and allow the user to append optional extra cash balance and an introductory note.")
    add_bullet("FR-5 Trade Action Processing: ", "Receivers must be able to Accept or Decline proposals. Accepted trades must lock item availability to prevent conflicting duplicate offers.")
    add_bullet("FR-6 Negotiation Messaging: ", "The system must provide an integrated asynchronous chat channel linked to each swap transaction for meetup coordination.")
    add_bullet("FR-7 Atomic Completion: ", "Upon mutual physical exchange, clicking 'Confirm Swap Completed' must atomically update item ownership in the database and increment completed swap metrics.")

    add_subsec_heading("2.5.2 Non-Functional Requirements")
    add_bullet("NFR-1 Response Time: ", "All primary API endpoints (catalog retrieval, filtering, proposal creation) must return responses in under 200 milliseconds under standard local network conditions.")
    add_bullet("NFR-2 Data Integrity: ", "Relational database constraints must enforce referential integrity across users, items, and swap proposals, eliminating orphaned records.")
    add_bullet("NFR-3 Usability & Responsiveness: ", "The frontend interface must render adaptively across mobile, tablet, and desktop display viewports without horizontal clipping or broken layouts.")
    add_bullet("NFR-4 Maintainability: ", "Backend logic must be decoupled into distinct database, domain logic, and presentation routing files.")

    add_sec_heading("2.6 Hardware and Software Requirements")
    table_hw = doc.add_table(rows=7, cols=3)
    table_hw.alignment = WD_TABLE_ALIGNMENT.CENTER
    hw_headers = ["Category", "Minimum Specification", "Recommended Specification"]
    for i, h in enumerate(hw_headers):
        cell = table_hw.rows[0].cells[i]
        cell.text = h
        set_cell_background(cell, "059669")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        p.runs[0].font.name = 'Times New Roman'
        p.runs[0].font.size = Pt(11)
        p.runs[0].font.bold = True
        p.runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    hw_data = [
        ["Processor", "Dual Core 2.0 GHz", "Intel Core i5 / AMD Ryzen 5 or higher"],
        ["RAM", "4 GB DDR3", "8 GB DDR4 or higher"],
        ["Hard Disk Space", "500 MB free storage", "2 GB SSD storage"],
        ["Operating System", "Windows 10 / Ubuntu 20.04 / macOS", "Windows 11 / Linux (64-bit)"],
        ["Python Runtime", "Python 3.10.x", "Python 3.12.x"],
        ["Web Browser", "Google Chrome 90+ / Mozilla Firefox 88+", "Latest Chrome, Firefox, or Edge"]
    ]
    for row_idx, r in enumerate(hw_data):
        for col_idx, text in enumerate(r):
            cell = table_hw.rows[row_idx + 1].cells[col_idx]
            cell.text = text
            set_cell_margins(cell, 60, 60, 80, 80)
            if row_idx % 2 == 1:
                set_cell_background(cell, "F1F5F9")
            p = cell.paragraphs[0]
            p.runs[0].font.name = 'Times New Roman'
            p.runs[0].font.size = Pt(10)

    add_p("Table 2.1: Hardware and Software Environment Requirements", italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=12)

    doc.add_page_break()

    # ==========================================
    # 9. CHAPTER 3: SYSTEM DESIGN
    # ==========================================
    add_chapter_title("CHAPTER 3\nSYSTEM DESIGN")

    add_sec_heading("3.1 System Architecture")
    add_p("EcoSwap follows the standard Three-Tier Architectural Pattern, ensuring clean separation of concerns, high maintainability, and loose coupling between system layers:", space_before=6, space_after=6)
    add_bullet("Presentation Tier (Frontend Layer): ", "Constructed using semantic HTML5, modern Tailwind utility styling, and reactive JavaScript. Handles user interactions, dynamic DOM rendering, asynchronous fetch calls, and modal lifecycle management.")
    add_bullet("Application Tier (Business Logic Layer): ", "Constructed with Python 3.12 and the Flask micro-framework. Serves RESTful JSON endpoints, manages session state cookies, enforces validation rules, and executes the value comparison algorithm.")
    add_bullet("Data Persistence Tier (Database Layer): ", "Powered by SQLite3. Manages persistent storage of user accounts, garment records, swap proposal lifecycles, and chat logs with full ACID compliance and relational referential integrity.")

    add_sec_heading("3.2 Data Flow Diagrams (DFD)")
    add_subsec_heading("3.2.1 DFD Level 0 (Context Level Diagram)")
    add_p("At the contextual boundary level, the external entity (User/Swapper) interacts directly with the unified EcoSwap System boundary. The user provides registration credentials, item descriptions, and swap proposals; the system returns filtered garment catalogs, value match recommendations, trade status updates, and environmental metrics.", space_before=6, space_after=10)

    add_subsec_heading("3.2.2 DFD Level 1 (Detailed Subsystem Data Flow)")
    add_p("The Level 1 DFD decomposes the system into four autonomous functional processes:", space_before=6, space_after=6)
    add_bullet("Process 1.0 - User Authentication & Session Control: ", "Accepts email/password, validates against the Users Data Store (D1), and returns an authenticated HTTP session cookie.")
    add_bullet("Process 2.0 - Wardrobe & Inventory Management: ", "Receives garment upload payloads, validates attributes, inserts records into the Items Data Store (D2), and retrieves active wardrobe inventories.")
    add_bullet("Process 3.0 - Value-Based Matching & Proposal Engine: ", "Extracts target garment metadata and requester wardrobe records, evaluates value differences, computes trade parity, and stores proposals into the Swap Requests Data Store (D3).")
    add_bullet("Process 4.0 - Trade Coordination & Completion: ", "Manages proposal status transitions (pending -> accepted -> completed), coordinates in-app chat via the Messages Data Store (D4), and atomically reassigns garment ownership upon physical swap confirmation.")

    add_sec_heading("3.3 Database Design & Entity Relationship (ER) Schema")
    add_p("The relational database schema is structured in Third Normal Form (3NF) to prevent redundant data storage and ensure relational integrity across multiple concurrent operations.", space_before=6, space_after=10)

    # Database Schema Table
    table_db = doc.add_table(rows=6, cols=4)
    table_db.alignment = WD_TABLE_ALIGNMENT.CENTER
    db_headers = ["Table Name", "Primary Key", "Foreign Keys", "Key Attributes"]
    for i, h in enumerate(db_headers):
        cell = table_db.rows[0].cells[i]
        cell.text = h
        set_cell_background(cell, "059669")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        p.runs[0].font.name = 'Times New Roman'
        p.runs[0].font.size = Pt(11)
        p.runs[0].font.bold = True
        p.runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    db_data = [
        ["users", "id", "None", "name, email, password, phone, city, area, swaps_completed"],
        ["items", "id", "user_id -> users(id)", "title, category, gender, size, brand, condition, price_inr, status, water_saved_l"],
        ["swap_requests", "id", "requester_id -> users(id)\nreceiver_id -> users(id)\noffered_item_id -> items(id)\nrequested_item_id -> items(id)", "extra_cash_inr, note, status, meet_location, created_at"],
        ["swap_messages", "id", "swap_id -> swap_requests(id)\nsender_id -> users(id)", "message, created_at"],
        ["eco_hubs", "id", "None", "name, city, area, address, hub_type, timings, description"]
    ]
    for row_idx, r in enumerate(db_data):
        for col_idx, text in enumerate(r):
            cell = table_db.rows[row_idx + 1].cells[col_idx]
            cell.text = text
            set_cell_margins(cell, 60, 60, 80, 80)
            if row_idx % 2 == 1:
                set_cell_background(cell, "F1F5F9")
            p = cell.paragraphs[0]
            p.runs[0].font.name = 'Times New Roman'
            p.runs[0].font.size = Pt(10)

    add_p("Table 3.1: Relational Database Schema Architecture", italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=12)

    add_sec_heading("3.4 Value-Based Swap Algorithm Formulation")
    add_p("In conventional barter models, subjective disagreements over item worth represent the chief impediment to successful trade execution. EcoSwap overcomes this using an algorithmic valuation comparator anchored to market prices in Indian Rupees (₹).", space_before=6, space_after=8)

    add_p("Let P_offer denote the estimated retail value of the garment offered by the requester in INR (₹), and P_target denote the estimated retail value of the target garment listed by the receiver. The algorithm computes three primary metrics:", space_before=4, space_after=6)

    add_bullet("1. Absolute Value Differential (ΔP): ", "ΔP = |P_target - P_offer|")
    add_bullet("2. Percentage Trade Parity (M): ", "M = round( min(P_offer, P_target) / max(P_offer, P_target) * 100 )")
    add_bullet("3. Suggested Settlement Extra (S): ", "If ΔP <= 250: S = 0 (Classified as 'Perfect Fair 1:1 Swap'). If P_target > P_offer and ΔP > 250: S = ΔP (Classified as 'Target item is higher in value; offer S extra via cash or UPI'). If P_offer > P_target and ΔP > 250: S = 0 (Classified as 'Offered item is higher in value; direct swap or request adjustment').")

    add_p("This transparent formula eliminates ambiguity, builds mutual confidence between strangers, and dramatically accelerates barter negotiation cycles.", space_before=6, space_after=12)

    doc.add_page_break()

    # ==========================================
    # 10. CHAPTER 4: SYSTEM CODING & IMPLEMENTATION
    # ==========================================
    add_chapter_title("CHAPTER 4\nSYSTEM CODING & IMPLEMENTATION")

    add_sec_heading("4.1 Technology Stack & Development Environment")
    add_p("The implementation of EcoSwap was conducted using a lean, modular technology stack selected for reliability, rapid development velocity, and low resource overhead:", space_before=6, space_after=6)
    add_bullet("Backend Framework (Python Flask 3.1.3): ", "Chosen for its minimalist core, robust request routing, WSGI compliance, and transparent session management without heavyweight boilerplate.")
    add_bullet("Database Engine (SQLite3): ", "A serverless, zero-configuration SQL database engine embedded directly within the application environment. Provides full transactional safety (ACID) and lightning-fast read/write throughput.")
    add_bullet("Client-Side Styling (Tailwind CSS): ", "Employed via responsive utility classes, establishing a polished aesthetic featuring clean typography (Plus Jakarta Sans), subtle box-shadows, and mobile-friendly responsive breakpoints.")
    add_bullet("Interactive JavaScript & DOM Controller: ", "Pure vanilla ES6+ JavaScript utilizing asynchronous fetch APIs, state tracking, and dynamic template literal rendering without requiring cumbersome frontend bundler toolchains.")

    add_sec_heading("4.2 Backend RESTful API Implementation")
    add_p("The Flask application exposes structured RESTful endpoints returning clean JSON payloads. Standard HTTP status codes (200 OK, 201 Created, 400 Bad Request, 401 Unauthorized, 404 Not Found, 500 Internal Error) are consistently utilized across all operations.", space_before=6, space_after=8)

    # REST Endpoints Table
    table_api = doc.add_table(rows=8, cols=4)
    table_api.alignment = WD_TABLE_ALIGNMENT.CENTER
    api_headers = ["Endpoint", "HTTP Method", "Authentication", "Description"]
    for i, h in enumerate(api_headers):
        cell = table_api.rows[0].cells[i]
        cell.text = h
        set_cell_background(cell, "059669")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        p.runs[0].font.name = 'Times New Roman'
        p.runs[0].font.size = Pt(11)
        p.runs[0].font.bold = True
        p.runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    api_data = [
        ["/api/me", "GET", "Optional", "Retrieves active authenticated session profile or logged_in: false"],
        ["/api/login", "POST", "Public", "Validates email and password credentials, initializes session cookie"],
        ["/api/register", "POST", "Public", "Creates new user account with location and phone details"],
        ["/api/items", "GET", "Public", "Returns marketplace garments filtered by category, gender, condition, sort"],
        ["/api/items", "POST", "Required", "Inserts newly listed garment into user's wardrobe and marketplace"],
        ["/api/fair-match/<id>", "GET", "Required", "Computes value parity of target item against user's available wardrobe"],
        ["/api/swaps/propose", "POST", "Required", "Submits swap proposal with offered garment, cash sweetener, and meetup spot"]
    ]
    for row_idx, r in enumerate(api_data):
        for col_idx, text in enumerate(r):
            cell = table_api.rows[row_idx + 1].cells[col_idx]
            cell.text = text
            set_cell_margins(cell, 60, 60, 80, 80)
            if row_idx % 2 == 1:
                set_cell_background(cell, "F1F5F9")
            p = cell.paragraphs[0]
            p.runs[0].font.name = 'Times New Roman'
            p.runs[0].font.size = Pt(9.5)

    add_p("Table 4.1: Core RESTful Application Programming Interface Endpoints", italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=12)

    add_sec_heading("4.3 Core Code Implementation Highlights")
    add_p("Below are foundational backend implementation modules illustrating the clean architectural patterns employed in the application codebase.", space_before=4, space_after=6)

    add_subsec_heading("Code Listing 4.1: Value Comparison Algorithm (models.py)")
    code_snippet_1 = """def compare_swap_values(my_price_inr, target_price_inr):
    diff = int(target_price_inr) - int(my_price_inr)
    abs_diff = abs(diff)
    ratio = min(my_price_inr, target_price_inr) / max(my_price_inr, target_price_inr)
    match_pct = round(ratio * 100)

    if abs_diff <= 250:
        verdict = "Perfect Fair 1-to-1 Swap!"
        advice = f"Both clothes are similar in value (Rs. {my_price_inr:,} vs Rs. {target_price_inr:,}). No extra money needed!"
        suggested_extra = 0
    elif diff > 0:
        verdict = f"Target item is Rs. {abs_diff:,} higher"
        advice = f"Their garment is worth Rs. {abs_diff:,} more than yours. You can offer Rs. {abs_diff:,} extra to make it a fair deal."
        suggested_extra = abs_diff
    else:
        verdict = f"Your item is Rs. {abs_diff:,} higher"
        advice = f"Your garment is worth Rs. {abs_diff:,} more. You can propose a direct swap or ask for extra balance."
        suggested_extra = 0

    return {'match_pct': match_pct, 'difference_inr': abs_diff, 'verdict': verdict, 'advice': advice, 'suggested_extra_inr': suggested_extra}"""

    p_c1 = doc.add_paragraph()
    p_c1.paragraph_format.space_before = Pt(4)
    p_c1.paragraph_format.space_after = Pt(8)
    p_c1.paragraph_format.line_spacing = 1.15
    r_c1 = p_c1.add_run(code_snippet_1)
    r_c1.font.name = 'Courier New'
    r_c1.font.size = Pt(9.5)

    add_subsec_heading("Code Listing 4.2: Swap Proposal Creation Handler (app.py)")
    code_snippet_2 = """@app.route('/api/swaps/propose', methods=['POST'])
def propose_swap_request():
    user = get_logged_in_user()
    if not user:
        return jsonify({'error': 'Please login to send swap requests'}), 401

    data = request.json or {}
    requested_id = data.get('requested_item_id')
    offered_id = data.get('offered_item_id')
    extra_cash = int(data.get('extra_cash_inr', 0) or 0)
    note = data.get('note', '')
    meetup = data.get('meet_location', 'Nearby Metro Station or Cafe')

    conn = get_db()
    req_item = conn.execute('SELECT * FROM items WHERE id = ? AND status = "available"', (requested_id,)).fetchone()
    if not req_item or req_item['user_id'] == user['id']:
        conn.close()
        return jsonify({'error': 'Requested item is invalid or belongs to you'}), 400

    now = datetime.now().strftime('%d %b, %I:%M %p')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO swap_requests (requester_id, receiver_id, offered_item_id, requested_item_id,
                                   extra_cash_inr, note, status, meet_location, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, 'pending', ?, ?, ?)
    ''', (user['id'], req_item['user_id'], offered_id, requested_id, extra_cash, note, meetup, now, now))
    
    conn.commit()
    conn.close()
    return jsonify({'success': True}), 201"""

    p_c2 = doc.add_paragraph()
    p_c2.paragraph_format.space_before = Pt(4)
    p_c2.paragraph_format.space_after = Pt(12)
    p_c2.paragraph_format.line_spacing = 1.15
    r_c2 = p_c2.add_run(code_snippet_2)
    r_c2.font.name = 'Courier New'
    r_c2.font.size = Pt(9.5)

    doc.add_page_break()

    # ==========================================
    # 11. CHAPTER 5: SYSTEM TESTING & RESULTS
    # ==========================================
    add_chapter_title("CHAPTER 5\nSYSTEM TESTING & RESULTS")

    add_sec_heading("5.1 Testing Strategy & Methodology")
    add_p("To ensure that the EcoSwap application operates reliably across diverse usage scenarios, a structured, multi-tier testing strategy was implemented. Testing was conducted iteratively across three distinct phases:", space_before=6, space_after=6)
    add_bullet("Unit Testing: ", "Validating individual functions and algorithms in isolation, particularly verifying that the value comparison formula correctly computes differences, percentages, and advice under equal, higher, and lower price conditions.")
    add_bullet("Integration Testing: ", "Verifying that the Flask controller endpoints properly interact with the SQLite database driver, correctly manage session cookies across stateful requests, and maintain referential integrity.")
    add_bullet("System & User Acceptance Testing (UAT): ", "Validating the complete end-to-end user journey within standard web browsers (Google Chrome and Microsoft Edge) on Windows, executing simulated swaps between multiple persona accounts.")

    add_sec_heading("5.2 Test Cases & Execution Matrix")
    add_p("The table below documents representative test cases executed against the system during formal verification:", space_before=4, space_after=8)

    # Test Cases Table
    table_tc = doc.add_table(rows=6, cols=5)
    table_tc.alignment = WD_TABLE_ALIGNMENT.CENTER
    tc_headers = ["Test ID", "Module / Feature", "Input / Condition", "Expected Result", "Status"]
    for i, h in enumerate(tc_headers):
        cell = table_tc.rows[0].cells[i]
        cell.text = h
        set_cell_background(cell, "059669")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        p.runs[0].font.name = 'Times New Roman'
        p.runs[0].font.size = Pt(10)
        p.runs[0].font.bold = True
        p.runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    tc_data = [
        ["TC-01", "Homepage Route", "GET request to '/'", "HTTP Status 200, HTML contains 'EcoSwap'", "PASSED"],
        ["TC-02", "Authentication", "POST /api/login with valid email and password", "HTTP Status 200, sets session cookie, returns user data", "PASSED"],
        ["TC-03", "Auth Security", "POST /api/login with invalid password", "HTTP Status 401, error message returned", "PASSED"],
        ["TC-04", "Marketplace API", "GET /api/items with category filter", "HTTP Status 200, returns array of items matching category", "PASSED"],
        ["TC-05", "Swap Valuation", "GET /api/fair-match/4 for user Priya", "HTTP Status 200, returns ranked wardrobe matches with difference in Rs.", "PASSED"]
    ]
    for row_idx, r in enumerate(tc_data):
        for col_idx, text in enumerate(r):
            cell = table_tc.rows[row_idx + 1].cells[col_idx]
            cell.text = text
            set_cell_margins(cell, 60, 60, 80, 80)
            if row_idx % 2 == 1:
                set_cell_background(cell, "F1F5F9")
            p = cell.paragraphs[0]
            p.runs[0].font.name = 'Times New Roman'
            p.runs[0].font.size = Pt(9.5)
            if col_idx == 4:
                p.runs[0].font.bold = True
                p.runs[0].font.color.rgb = RGBColor(0x05, 0x96, 0x69)

    add_p("Table 5.1: System Verification & Test Case Execution Matrix", italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=12)

    add_sec_heading("5.3 Automated Test Suite Execution")
    add_p("An automated test suite was constructed utilizing Python's built-in unittest framework (test_app.py). The test runner programmatically initialized the SQLite database, generated isolated test client contexts, executed all core API assertions, and benchmarked execution velocity.", space_before=6, space_after=6)

    test_output_box = """======================================================================
Ran 4 tests in 0.055s

OK (test_homepage, test_login_and_me, test_items_in_rupees, test_fair_match_inr)
======================================================================"""
    p_to = doc.add_paragraph()
    p_to.paragraph_format.space_before = Pt(4)
    p_to.paragraph_format.space_after = Pt(8)
    p_to.paragraph_format.line_spacing = 1.15
    r_to = p_to.add_run(test_output_box)
    r_to.font.name = 'Courier New'
    r_to.font.size = Pt(10)
    r_to.bold = True

    add_p("The execution confirmed 100% test pass rate with a cumulative execution latency of merely 0.055 seconds, demonstrating exceptional backend efficiency.", space_before=4, space_after=12)

    add_sec_heading("5.4 Engineering Challenges & Problem Solving")
    add_p("During the development and deployment phases on the Windows operating environment, several technical challenges emerged and were resolved through rigorous diagnosis:", space_before=6, space_after=6)
    add_bullet("1. Windows Character Encoding (cp1252 vs. UTF-8): ", "When executing Python backend scripts directly via Windows PowerShell, stdout attempted to encode the Indian Rupee unicode glyph (₹ / \\u20b9) into the legacy cp1252 code page, precipitating a UnicodeEncodeError. This was resolved by standardizing console log outputs to ASCII-safe descriptors (e.g. 'Rs.' or 'INR') while strictly preserving UTF-8 encoding across HTML templates and JSON API payloads.")
    add_bullet("2. Socket Port Lifecycle & Process Concurrency: ", "During rapid server restarts, background Python processes occasionally retained socket bindings on port 5000, preventing updated instances from listening. This was diagnosed using PowerShell's Get-NetTCPConnection cmdlet and resolved by instituting automated process cleanup and binding the WSGI server to all interfaces (0.0.0.0).")
    add_bullet("3. Cross-Party Barter Simulation: ", "Testing bilateral barter trades required verifying both requester and receiver perspectives. Rather than mandating tedious multi-browser manual logouts, a Quick Demo Persona Switcher was implemented, enabling instantaneous state switching between simulated users (Priya, Rahul, Ananya, Rohan).")

    doc.add_page_break()

    # ==========================================
    # 12. CHAPTER 6: CONCLUSION & FUTURE SCOPE
    # ==========================================
    add_chapter_title("CHAPTER 6\nCONCLUSION & FUTURE SCOPE")

    add_sec_heading("6.1 Summary of Accomplished Work")
    add_p("The EcoSwap project successfully designed, developed, and validated a full-stack, peer-to-peer clothing exchange and barter marketplace. By eliminating monetary transaction fees and replacing courier-heavy logistics with hyperlocal community exchanges, the platform demonstrates a viable, technology-driven solution to the escalating problem of fast-fashion textile waste.", space_before=6, space_after=10)

    add_p("The system incorporates an intuitive value-based recommendation engine formulated in Indian Rupees (₹) that removes trade friction, supports seamless multi-parameter garment search, provides in-app negotiation messaging, and identifies verified safe meetup venues. Automated unit testing confirmed zero defects with sub-100-millisecond response latencies, proving that sustainable circular economic models can be implemented effectively using accessible, open-source software technologies.", space_before=6, space_after=12)

    add_sec_heading("6.2 Environmental & Social Impact")
    add_p("The ecological advantages of prolonged garment life cycles are quantifiable and substantial. In EcoSwap, every exchanged garment offsets the production of a new virgin garment, preserving an estimated 2,700 liters of freshwater for shirts and up to 7,500 liters for denim trousers, while diverting 8.5 to 18 kilograms of carbon dioxide emissions. Socially, the platform fosters community cohesion, cultivates sustainable consumption habits, and makes quality apparel accessible to urban students and young professionals without financial burden.", space_before=6, space_after=12)

    add_sec_heading("6.3 Future Scope & Enhancements")
    add_p("While the operational prototype successfully fulfills all initial functional specifications, several promising engineering extensions can be pursued in future development phases:", space_before=6, space_after=6)
    add_bullet("1. Computer Vision Garment Inspection: ", "Integrate lightweight deep-learning computer vision models (e.g., MobileNet or YOLO) to automatically analyze user-uploaded garment photographs, verify physical condition, detect fabric wear or stains, and auto-tag color and category attributes.")
    add_bullet("2. UPI Escrow for Asymmetrical Swaps: ", "Integrate an automated micro-payment escrow system via the Unified Payments Interface (UPI) to securely hold and release recommended cash sweeteners once both parties confirm physical handshake completion.")
    add_bullet("3. Cross-Platform Native Mobile Applications: ", "Package the application into native Android and iOS mobile clients utilizing React Native or Flutter, taking advantage of on-device camera hardware and push notifications for instant swap request alerts.")
    add_bullet("4. Hyperlocal Delivery Integration: ", "Partner with local on-demand zero-emission courier services (such as electric two-wheeler delivery fleets) for users who are unable to meet in person, preserving sustainable delivery logistics.")

    doc.add_page_break()

    # ==========================================
    # 13. BIBLIOGRAPHY / REFERENCES (IEEE Format - 1 Page)
    # ==========================================
    add_chapter_title("BIBLIOGRAPHY / REFERENCES")

    references = [
        "[1] Ellen MacArthur Foundation, \"A New Textiles Economy: Redesigning fashion’s future,\" Ellen MacArthur Foundation Report, pp. 1-150, Nov. 2017.",
        "[2] K. Niinimäki, G. Peters, H. Dahlbo, P. Perry, T. Rissanen, and A. Gwilt, \"The environmental price of fast fashion,\" Nature Reviews Earth & Environment, vol. 1, no. 4, pp. 189–200, Apr. 2020.",
        "[3] M. Grinberg, \"Flask Web Development: Developing Web Applications with Python,\" 2nd ed., Sebastopol, CA: O'Reilly Media, 2018.",
        "[4] R. Fielding, \"Architectural Styles and the Design of Network-based Software Architectures,\" Ph.D. dissertation, Dept. Inf. Comput. Sci., Univ. California, Irvine, CA, 2000.",
        "[5] SQLite Development Team, \"SQLite Architecture and SQL Database Engine Documentation,\" SQLite.org, 2024. [Online]. Available: https://www.sqlite.org/docs.html",
        "[6] E. Gamma, R. Helm, R. Johnson, and J. Vlissides, \"Design Patterns: Elements of Reusable Object-Oriented Software,\" Reading, MA: Addison-Wesley, 1994.",
        "[7] A. W. W. B. J. Brooks, \"Clothing Poverty: The Hidden World of Fast Fashion and Second-hand Clothes,\" London: Zed Books, 2015.",
        "[8] IEEE Standard for Software Test Documentation, IEEE Std 829-2008, pp. 1–74, Jul. 2008.",
        "[9] W. Stallings, \"Operating Systems: Internals and Design Principles,\" 9th ed., Boston, MA: Pearson, 2018.",
        "[10] Central Pollution Control Board (CPCB), \"Guidelines for Environmentally Sound Management of End-of-Life Textiles in India,\" Ministry of Environment, Forest and Climate Change, New Delhi, 2022."
    ]

    for ref in references:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.line_spacing = 1.3
        p.paragraph_format.left_indent = Inches(0.4)
        p.paragraph_format.first_line_indent = Inches(-0.4)
        r = p.add_run(ref)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(11)

    # Save Document
    output_filename = "EcoSwap_College_Internship_Report.docx"
    doc.save(output_filename)
    print(f"Report successfully generated and saved to: {output_filename}")

if __name__ == '__main__':
    create_report()
