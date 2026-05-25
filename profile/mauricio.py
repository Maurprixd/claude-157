"""
SOURCE OF TRUTH — Mauricio Mena's profile.

This file is read at the start of every search session.
Do NOT score, search, or generate resumes without loading CANDIDATE_PROFILE first.
Update this file whenever your resume, experience, or job search strategy changes.
"""

CANDIDATE_PROFILE = {
    # ── Personal info ──────────────────────────────────────────────────────────
    "name": "Mauricio Mena",
    "email": "mena47831@gmail.com",
    "phone": "437-661-4530",
    "location": "Toronto, ON",
    "relocation_note": "Open to relocate to Montréal, QC | Toronto, ON",
    "linkedin": "linkedin.com/in/mauriciomena-design",
    "portfolio_behance": "behance.net/gallery/217417729/Portfolio",
    "website": "mauricio-mena.com",

    # ── Summary ────────────────────────────────────────────────────────────────
    "summary": (
        "Industrial and Product Designer graduating from Centennial College (April 2026) "
        "with hands-on experience in the full product development cycle — from concept "
        "generation and SolidWorks modeling to multi-material prototyping, DFM review, and "
        "BOM documentation. Lead Designer on BuddhaCalm, a patent-pending wearable health "
        "device (patent application filed Feb 2026; selected for WIMTACH industry showcase). "
        "Soft goods experience from VIV66 (apparel): multi-material construction specs, "
        "fabric/hardware callouts, fit refinement. Bilingual: English + Spanish; French in progress."
    ),

    # ── Education ──────────────────────────────────────────────────────────────
    "education": [
        {
            "degree": "Advanced Diploma — Industrial and Product Design",
            "school": "Centennial College",
            "location": "Toronto, ON",
            "graduation": "Expected April 2026",
            "courses": "Manufacturing Processes, Material Science, Technical Drawing, UX/UI Design",
        }
    ],

    # ── Experience ─────────────────────────────────────────────────────────────
    # IMPORTANT: keep these bullets accurate. They feed both resume generation
    # and AI job scoring. Do not exaggerate — but be specific and concrete.
    "experience": [
        {
            "title": "Lead Industrial Designer",
            "company": "WIMTACH / Centennial College",
            "location": "Toronto, ON",
            "dates": "Sept 2024 – Present",
            "bullets": [
                # Patent context — establishes this is real funded R&D, not a class project
                "Lead designer for BuddhaCalm, a patent-pending wearable stress-relief device "
                "(patent application filed Feb 2026; device selected for WIMTACH industry showcase) — "
                "full ownership from first sketch to production-ready prototype",

                # Concept volume — mirrors what top industrial design roles ask for
                "Generated 15–20+ distinct product concepts per design sprint, iterating across "
                "mechanism variations, enclosure geometry, CMF options, and ergonomic form factors "
                "before converging on a direction",

                # Multi-material prototyping — hard + soft, FDM + foam
                "Built multi-fidelity prototypes at every stage: foam and cardboard mockups for "
                "early ergonomic validation, iterative FDM prints (Bambu Lab P1S) for mechanism "
                "testing, final assemblies integrating rigid housing, flexible contact surfaces, "
                "and pogo-pin charging hardware",

                # CAD + DFM
                "Created SolidWorks assemblies with complex pogo-pin charging architecture; "
                "produced DFM-ready parts and technical drawings for external manufacturing partners",

                # User research / validation — equivalent to focus-group facilitation
                "Led user research sessions and ergonomic testing with target users; synthesized "
                "feedback into documented design changes across 4 prototype iterations",

                # Presentation / visual communication
                "Produced KeyShot photorealistic renders and Adobe Suite stakeholder decks for "
                "client-facing design reviews; visible portfolio at mauricio-mena.com",
            ],
        },
        {
            "title": "Product & Technical Designer",
            "company": "VIV66",
            "location": "Toronto, ON",
            "dates": "2023 – 2024",
            # NOTE: VIV66 is an apparel company — this is real soft goods experience.
            # Fabric, stitch types, hardware trim, fit refinement = flexible materials design.
            # Mention this when applying to roles that list foam/fabric/soft goods.
            "bullets": [
                "Developed multi-material technical construction specifications for soft goods "
                "(apparel) product lines — documenting stitch types, fabric callouts, hardware "
                "assembly sequences, and tolerance requirements for flexible material constructions",

                "Collaborated with production teams on fit refinement and material tolerance "
                "validation across a 5-month development cycle; iterated samples to meet comfort, "
                "durability, and manufacturability targets",

                "Produced BOM documentation and production packages for manufacturing handoff",
            ],
        },
    ],

    # ── Key project (for resume PDF) ───────────────────────────────────────────
    "key_project": {
        "name": "BuddhaCalm Wearable Health Device | WIMTACH, 2026 (Patent Pending)",
        "description": (
            "Consumer wearable stress-relief device — full design cycle from concept generation "
            "to production-ready prototype. Patent application filed Feb 2026. Integrated rigid "
            "housing, flexible contact surfaces, and embedded electronics; validated through "
            "repeated user research and ergonomic testing sessions."
        ),
        "portfolio_url": "mauricio-mena.com | behance.net/gallery/217417729/Portfolio",
    },

    # ── Skills ─────────────────────────────────────────────────────────────────
    "skills": {
        "CAD": ["SolidWorks (Expert) — assemblies, parts, drawings, DFM-compliant design"],
        "Prototyping": [
            "FDM 3D printing (Bambu Lab P1S, Prusa XL), foam & cardboard mockups, "
            "multi-material functional assemblies (rigid + flexible + hardware)"
        ],
        "Engineering": ["Design for Manufacturing (DFM) — production-aware design from first sketch"],
        "Rendering": ["KeyShot — photorealistic product renders, lifestyle visuals, client presentations"],
        "3D_Modelling": ["Rhino 3D — surface modelling, concept geometry, organic forms"],
        "Concept_Design": [
            "High-volume ideation (15–20+ concepts per brief), hand sketching, "
            "digital illustration, CMF exploration, mood boards"
        ],
        "Soft_Goods": [
            "Technical construction specs (apparel/flexible materials), fabric & hardware callouts, "
            "stitch specifications, fit refinement, material tolerance validation"
        ],
        "Documentation": [
            "BOM preparation, technical drawings, assembly drawings, "
            "construction specs, production packages"
        ],
        "Software": ["Adobe Creative Suite — Photoshop, Illustrator, InDesign"],
        "Research": ["User research, focus-group facilitation, ergonomic analysis, competitive benchmarking"],
    },

    # ── Languages ──────────────────────────────────────────────────────────────
    "languages": [
        "English (Fluent)",
        "Spanish (Native)",
        "French (Basic — actively studying; asset for Quebec or bilingual roles)",
    ],

    # ══════════════════════════════════════════════════════════════════════════
    # JOB SEARCH STRATEGY
    # ══════════════════════════════════════════════════════════════════════════
    # This section drives both the scraper search queries and the AI scoring.
    # Update it as your targets evolve.

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
        "Associate Product Designer",
        "Junior Design Engineer",
    ],

    "target_locations": [
        "Toronto, ON",
        "Montréal, QC",
        "Ontario",
        "Remote",
        "Canada",
    ],
    "preferred_location": "Toronto, ON",

    # Sectors ranked by fit — top tier gets the biggest score boost
    "preferred_sectors": [
        # Tier 1 — best fit (wearable/health device experience is directly transferable)
        "medical devices",
        "wearables",
        "rehab / orthotics / prosthetics",
        "health tech",
        # Tier 2 — strong fit (consumer product + DFM skills apply)
        "consumer electronics",
        "consumer products",
        "sporting goods",
        "hardware startups",
        # Tier 3 — workable (some transferability)
        "furniture",
        "packaging",
        "defense / aerospace (CAD-heavy roles)",
    ],

    # What to ACTIVELY AVOID showing — these waste time
    "avoid_sectors": [
        "graphic design only",
        "interior design only",
        "fashion design only",
        "software / SaaS",
        "civil / structural engineering",
        "HVAC / MEP",
        "retail sales",
    ],

    # Keywords that BOOST match score when found in a job posting
    "boost_keywords": [
        # Tools Mauricio has
        "solidworks", "keyshot", "3d printing", "fdm", "dfm", "design for manufacturing",
        "rhino", "cad", "bom", "prototyping", "rapid prototyping",
        # Role type signals
        "wearable", "medical device", "consumer electronics", "product design",
        "industrial design", "enclosure", "injection molding", "pogo pin",
        "concept design", "cmf", "ergonomics", "user research", "sketch",
        "foam", "fabric", "soft goods", "flexible materials",
        # Seniority signals (good — lowers the experience bar)
        "junior", "new grad", "entry level", "associate designer",
        "no experience requirement", "recent graduate",
        # Language bonus
        "bilingual", "french", "spanish", "english and french",
    ],

    # Keywords that PENALIZE — lower score when found
    "penalize_keywords": [
        # Tools Mauricio does NOT have
        "catia", "nx", "creo", "autocad civil", "ansys", "matlab",
        # Wrong role type
        "graphic design only", "fashion design only", "interior design only",
        "software engineer", "developer", "programmer", "devops",
        # Seniority too high
        "senior", "5+ years", "7+ years", "10+ years",
        "10 years", "8 years", "7 years", "6 years",
        "manager", "director", "vice president",
        # License / credentials Mauricio doesn't have yet
        "p.eng required", "professional engineer required",
        "licensed engineer", "p.eng license",
    ],

    # ── Score threshold ────────────────────────────────────────────────────────
    # Minimum AI match score to surface a job in the report.
    # 50 is realistic for the current Job Bank market — very few listings hit 70+.
    # Override per-run: python main.py scrape --min-score 70
    "min_match_score": 50,

    # ── Experience context for AI scoring ─────────────────────────────────────
    # Plain-text notes that get injected into the scoring prompt so Claude
    # understands things that aren't obvious from the bullets alone.
    "experience_notes": (
        "Total experience: ~1.5 years professional + 3 years active design practice. "
        "WIMTACH is a real funded industry R&D program at Centennial College — not a "
        "class project. The patent was filed in Feb 2026 and the device was shown at an "
        "industry showcase. VIV66 is an apparel/soft goods company — the 'construction "
        "specs' work there is real soft goods design experience (fabric, flexible materials, "
        "fit refinement). Portfolio is live and visible: mauricio-mena.com."
    ),
}
