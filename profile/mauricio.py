"""
SOURCE OF TRUTH — Mauricio Mena's profile.
The scraper reads this file at the start of every session before searching.
Do NOT search or match jobs without loading CANDIDATE_PROFILE first.
Update this file whenever your resume changes.
"""

CANDIDATE_PROFILE = {
    "name": "Mauricio Mena",
    "email": "mena47831@gmail.com",
    "phone": "437-661-4530",
    "location": "Toronto, ON",
    "relocation_note": "Open to relocate to Montréal, QC | Toronto, ON",
    "linkedin": "linkedin.com/in/mauriciomena-design",
    "portfolio_behance": "behance.net/gallery/217417729/Portfolio",
    "website": "mauricio-mena.com",

    "summary": (
        "Industrial and Product Designer graduating from Centennial College (April 2026) "
        "with hands-on experience in the full product development cycle — from concept "
        "sketching and SolidWorks modeling to functional prototyping, DFM review, and BOM "
        "documentation. Currently Lead Designer on a patent-pending wearable device at "
        "WIMTACH, with demonstrated experience coordinating cross-functional teams and "
        "managing iterative design-to-production workflows."
    ),

    "education": [
        {
            "degree": "Advanced Diploma — Industrial and Product Design",
            "school": "Centennial College",
            "location": "Toronto, ON",
            "graduation": "Expected April 2026",
            "courses": "Manufacturing Processes, Material Science, Technical Drawing, UX/UI Design",
        }
    ],

    "experience": [
        {
            "title": "Lead Industrial Designer",
            "company": "WIMTACH / Centennial College",
            "location": "Toronto, ON",
            "dates": "Sept 2024 – Present",
            "bullets": [
                "Lead designer for BuddhaCalm, a patent-pending wearable stress-relief device — managed full product cycle from concept sketching and enclosure geometry to production-ready prototypes",
                "Created SolidWorks assemblies with complex pogo pin charging architecture; produced iterative functional prototypes using high-fidelity 3D printing (Bambu Lab P1S)",
                "Produced high-quality KeyShot renders and Adobe Suite presentations for stakeholder and client-facing design reviews",
                "Conducted user research and ergonomic analysis to ground design decisions in real human experience; created mood boards and benchmarked competitor products",
                "Consistently met project schedule timelines across multiple concurrent design deliverables in a fast-paced, multidisciplinary environment",
            ],
        },
        {
            "title": "Product & Technical Designer",
            "company": "VIV66",
            "location": "Toronto, ON",
            "dates": "2023 – 2024",
            "bullets": [
                "Developed technical construction specifications for multiple seasonal styles, ensuring manufacturing feasibility within tolerance constraints",
                "Collaborated with production teams to manage material tolerances and fit refinement across a 5-month product cycle",
            ],
        },
    ],

    "key_project": {
        "name": "BuddhaCalm Wearable Device | WIMTACH, 2026 (Patent Pending)",
        "description": "Consumer wearable stress-relief device — full design cycle from concept to production-ready prototype",
        "portfolio_url": "mauricio-mena.com | behance.net/gallery/217417729/Portfolio",
    },

    "skills": {
        "CAD": ["SolidWorks (Expert) — assemblies, parts, drawings, DFM-compliant design"],
        "Prototyping": ["3D Printing: Bambu Lab P1S, Prusa XL — FDM, material selection, functional validation"],
        "Engineering": ["Design for Manufacturing (DFM) — production-aware design from first sketch"],
        "Rendering": ["KeyShot — photorealistic product renders, lifestyle visuals, client presentations"],
        "3D_Modelling": ["Rhino 3D — surface modelling, concept geometry, organic forms"],
        "Concept_Design": ["Hand sketching, digital illustration, concept ideation, mood boards, CMF exploration"],
        "Documentation": ["BOM preparation, technical drawings, shop drawings, assembly drawings, production packages"],
        "Software": ["Adobe Creative Suite — Photoshop, Illustrator, InDesign (presentations, mood boards, marketing)"],
        "Research": ["User research, competitive benchmarking, trend monitoring, mood board creation"],
    },

    "languages": [
        "English (Fluent)",
        "Spanish (Native)",
        "French (Basic — actively developing)",
    ],

    # --- Matching configuration ---

    "target_roles": [
        "Junior Industrial Designer",
        "Junior Product Designer",
        "Product Designer",
        "Industrial Designer",
        "Medical Device Designer",
        "Wearable Device Designer",
        "Consumer Product Designer",
        "Design Engineer",
        "CAD Designer",
        "Product Development Designer",
    ],

    "target_locations": [
        "Toronto, ON",
        "Montréal, QC",
        "Ontario",
        "Remote",
        "Canada",
    ],
    "preferred_location": "Toronto, ON",

    "preferred_sectors": [
        "medical devices",
        "wearables",
        "consumer electronics",
        "consumer products",
        "sporting goods",
        "furniture",
        "hardware startups",
        "health tech",
    ],

    # Keywords that BOOST match score
    "boost_keywords": [
        "solidworks", "keyshot", "3d printing", "fdm", "dfm", "design for manufacturing",
        "wearable", "medical device", "consumer electronics", "product design",
        "industrial design", "prototyping", "bom", "cad", "rhino", "sketch",
        "junior", "new grad", "entry level", "associate designer",
        "ergonomics", "user research", "enclosure", "injection molding",
        "pogo pin", "rapid prototyping", "concept design", "cmf",
    ],

    # Keywords that PENALIZE / lower match score
    "penalize_keywords": [
        "catia", "nx", "creo", "autocad civil", "structural engineering",
        "senior", "5+ years", "7+ years", "10+ years", "manager", "director",
        "graphic design only", "fashion design only", "interior design only",
        "software engineer", "developer", "programmer",
        "p.eng required", "professional engineer required",
        "10 years", "8 years", "7 years",
    ],

    # Minimum match score to surface in results.
    # 50 is realistic for the current Job Bank market — very few listings score 70+.
    # Override per-run with: python main.py scrape --min-score 70
    "min_match_score": 50,
}
