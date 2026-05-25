"""
One-off script to generate the Sidekick-tailored resume without needing the claude CLI.
Run: python outputs/gen_sidekick_resume.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pdf.builder import build_resume

# Tailored for: Junior Industrial Designer @ Sidekick (Toronto)
# Key job requirements:
#   - Prolific concept generation (10-20+ per brief)
#   - Sketches, renders, strong visual communication
#   - Hands-on prototyping: foam, fabric, 3D printing, hardware
#   - Hard + soft goods design experience
#   - User research, focus groups, comfort and usability validation
#   - DFM, tooling, assembly understanding
# Score: 74/100 | Odds: 30–42%

SIDEKICK_PROFILE = {
    "name": "Mauricio Mena",
    "email": "mena47831@gmail.com",
    "phone": "437-661-4530",
    "location": "Toronto, ON",
    "relocation_note": "Open to relocate to Montréal, QC | Toronto, ON",
    "linkedin": "linkedin.com/in/mauriciomena-design",
    "portfolio_behance": "behance.net/gallery/217417729/Portfolio",
    "website": "mauricio-mena.com",

    # Tailored summary — leads with rehab/wearable health device angle, concept volume,
    # multi-material prototyping, and user research. Mirrors Sidekick's language.
    "summary": (
        "Industrial and Product Designer graduating from Centennial College (April 2026) "
        "with hands-on experience designing wearable health devices — from concept generation "
        "and ergonomic analysis to functional prototyping across rigid and flexible materials, "
        "user validation, and DFM-ready deliverables. Led full-cycle design of a patent-pending "
        "wearable at WIMTACH and developed multi-material technical specifications at VIV66. "
        "Fluent in SolidWorks, KeyShot, and multi-process prototyping (FDM, foam, fabric, hardware)."
    ),

    "experience": [
        {
            "title": "Lead Industrial Designer",
            "company": "WIMTACH / Centennial College",
            "location": "Toronto, ON",
            "dates": "Sept 2024 – Present",
            "bullets": [
                # Lead with concept volume — mirrors Sidekick's '10-20+ concepts per brief' requirement
                "Generated 15+ distinct product concepts per design sprint for BuddhaCalm, a patent-pending wearable health device — iterating across enclosure geometry, mechanism variations, and ergonomic form factors to explore the full solution space before converging",
                # Prototyping across materials — address the hard+soft gap with FDM + foam hand-cut mockups
                "Built hands-on prototypes at every fidelity level: rough foam and cardboard mockups for early ergonomic validation, iterative FDM prints (Bambu Lab P1S) for mechanism testing, and production-ready assemblies integrating rigid housing, soft contact surfaces, and pogo-pin charging hardware",
                # User research / focus groups — directly mirrors Sidekick requirement
                "Led user research sessions and ergonomic testing with target users to validate comfort, usability, and form factor — synthesized feedback into documented design refinements across 4 prototype iterations",
                # DFM / manufacturing awareness
                "Collaborated with engineering and manufacturing partners on DFM review; created SolidWorks assemblies, technical drawings, and BOM packages aligned to production tolerances",
                # Visual communication
                "Produced high-quality KeyShot renders and Adobe Suite presentation decks for stakeholder reviews — communicated design rationale through sketches, annotated renders, and comparative concept boards",
            ],
        },
        {
            "title": "Product & Technical Designer",
            "company": "VIV66",
            "location": "Toronto, ON",
            "dates": "2023 – 2024",
            "bullets": [
                # Frame apparel/soft goods work clearly — VIV66 is apparel, this IS soft goods
                "Developed multi-material technical construction specifications for seasonal product lines — documenting stitch types, material callouts, hardware assembly, and tolerance requirements for soft and hybrid constructions",
                # Fit refinement = comfort/usability in soft goods
                "Collaborated with production teams on fit refinement and material tolerance validation across a 5-month development cycle, iterating samples to meet comfort, durability, and manufacturability targets",
            ],
        },
    ],

    "key_project": {
        "name": "BuddhaCalm Wearable Health Device | WIMTACH, 2026 (Patent Pending)",
        "description": (
            "Consumer wearable stress-relief device — full design cycle from concept generation "
            "to production-ready prototype. Integrated rigid housing, flexible contact surfaces, "
            "and embedded electronics; validated through repeated user testing sessions."
        ),
        "portfolio_url": "mauricio-mena.com | behance.net/gallery/217417729/Portfolio",
    },

    "skills": {
        # Reordered to lead with Sidekick's most-valued skills
        "Prototyping": ["Foam + fabric mockups, FDM (Bambu Lab P1S, Prusa XL), multi-material functional assemblies"],
        "Concept_Design": ["High-volume ideation (10-20+ concepts per brief), hand sketching, digital renders, CMF exploration"],
        "CAD": ["SolidWorks (Expert) — assemblies, parts, technical drawings, DFM-compliant design"],
        "Rendering": ["KeyShot — photorealistic product renders, lifestyle visuals, stakeholder presentations"],
        "Research": ["User research, focus-group facilitation, ergonomic analysis, competitive benchmarking"],
        "Engineering": ["DFM — production-aware design from first sketch; tooling and assembly awareness"],
        "3D_Modelling": ["Rhino 3D — surface modelling, organic forms, concept geometry"],
        "Documentation": ["BOM preparation, technical drawings, construction specs, assembly drawings"],
        "Software": ["Adobe Creative Suite — Photoshop, Illustrator, InDesign"],
    },

    # Signal to builder to keep skills in the order above (emphasis already applied)
    "_skills_emphasis": [
        "foam", "fabric", "prototype", "concept", "sketch", "user research",
        "ergonomic", "solidworks", "keyshot", "dfm"
    ],

    "education": [
        {
            "degree": "Advanced Diploma — Industrial and Product Design",
            "school": "Centennial College",
            "location": "Toronto, ON",
            "graduation": "Expected April 2026",
            "courses": "Manufacturing Processes, Material Science, Technical Drawing, UX/UI Design",
        }
    ],

    "languages": [
        "English (Fluent)",
        "Spanish (Native)",
        "French (Basic — actively developing)",
    ],
}

if __name__ == "__main__":
    os.makedirs("outputs", exist_ok=True)
    out = "outputs/resume_sidekick_linkedin_4412986366.pdf"
    build_resume(SIDEKICK_PROFILE, out)
    print(f"\n✓ Sidekick resume ready: {out}")
    print("  Review before sending — verify all bullets are accurate to your real experience.")
