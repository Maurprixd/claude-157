"""
PDF resume builder using ReportLab.
Replicates Mauricio's current resume style: clean, sans-serif, two-column skills.
"""
import pathlib
import time
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# --- Styles ---
NAME_STYLE = ParagraphStyle(
    "Name",
    fontName="Helvetica-Bold",
    fontSize=18,
    leading=22,
    alignment=TA_CENTER,
    spaceAfter=2,
)
CONTACT_STYLE = ParagraphStyle(
    "Contact",
    fontName="Helvetica",
    fontSize=8.5,
    leading=12,
    alignment=TA_CENTER,
    spaceAfter=4,
)
SECTION_STYLE = ParagraphStyle(
    "Section",
    fontName="Helvetica-Bold",
    fontSize=10.5,
    leading=14,
    spaceBefore=8,
    spaceAfter=2,
)
ROLE_TITLE_STYLE = ParagraphStyle(
    "RoleTitle",
    fontName="Helvetica-Bold",
    fontSize=10,
    leading=13,
    spaceAfter=0,
)
ROLE_META_STYLE = ParagraphStyle(
    "RoleMeta",
    fontName="Helvetica-Oblique",
    fontSize=9,
    leading=12,
    textColor=colors.HexColor("#444444"),
    spaceAfter=2,
)
BULLET_STYLE = ParagraphStyle(
    "Bullet",
    fontName="Helvetica",
    fontSize=9,
    leading=12,
    leftIndent=12,
    spaceAfter=1,
)
BODY_STYLE = ParagraphStyle(
    "Body",
    fontName="Helvetica",
    fontSize=9,
    leading=13,
    spaceAfter=4,
)
SKILL_KEY_STYLE = ParagraphStyle(
    "SkillKey",
    fontName="Helvetica-Bold",
    fontSize=8.5,
    leading=12,
)
SKILL_VAL_STYLE = ParagraphStyle(
    "SkillVal",
    fontName="Helvetica",
    fontSize=8.5,
    leading=12,
)

RULE_COLOR = colors.HexColor("#333333")


def _rule():
    return HRFlowable(width="100%", thickness=0.75, color=RULE_COLOR, spaceAfter=4)


def _section_header(title: str) -> list:
    return [
        Spacer(1, 4),
        Paragraph(title.upper(), SECTION_STYLE),
        _rule(),
    ]


def _header_section(profile: dict) -> list:
    name = profile["name"]
    contact_parts = [
        profile.get("relocation_note", profile.get("location", "")),
        profile.get("phone", ""),
        profile.get("email", ""),
        profile.get("portfolio_behance", ""),
        profile.get("linkedin", ""),
        profile.get("website", ""),
    ]
    contact_line = " | ".join(p for p in contact_parts if p)
    return [
        Paragraph(name, NAME_STYLE),
        Paragraph(contact_line, CONTACT_STYLE),
    ]


def _summary_section(summary: str) -> list:
    items = _section_header("Summary")
    items.append(Paragraph(summary, BODY_STYLE))
    return items


def _experience_section(experience: list) -> list:
    items = _section_header("Experience")
    for exp in experience:
        items.append(Paragraph(f"{exp['title']} — {exp['company']}", ROLE_TITLE_STYLE))
        items.append(Paragraph(f"{exp['location']} | {exp['dates']}", ROLE_META_STYLE))
        for bullet in exp["bullets"]:
            items.append(Paragraph(f"• {bullet}", BULLET_STYLE))
        items.append(Spacer(1, 4))
    return items


def _skills_section(skills: dict, emphasis: Optional[list] = None) -> list:
    items = _section_header("Skills")

    skill_items = list(skills.items())
    if emphasis:
        def _sort_key(kv):
            k, v = kv
            val_str = " ".join(v).lower()
            return -sum(1 for e in emphasis if e.lower() in val_str or e.lower() in k.lower())
        skill_items = sorted(skill_items, key=_sort_key)

    rows = []
    for i in range(0, len(skill_items), 2):
        left_k, left_v = skill_items[i]
        row_left_key = Paragraph(f"{left_k.replace('_', ' ')}:", SKILL_KEY_STYLE)
        row_left_val = Paragraph(", ".join(left_v), SKILL_VAL_STYLE)

        if i + 1 < len(skill_items):
            right_k, right_v = skill_items[i + 1]
            row_right_key = Paragraph(f"{right_k.replace('_', ' ')}:", SKILL_KEY_STYLE)
            row_right_val = Paragraph(", ".join(right_v), SKILL_VAL_STYLE)
        else:
            row_right_key = Paragraph("", SKILL_KEY_STYLE)
            row_right_val = Paragraph("", SKILL_VAL_STYLE)

        rows.append([
            Table([[row_left_key], [row_left_val]], colWidths=[2.8 * inch]),
            Table([[row_right_key], [row_right_val]], colWidths=[2.8 * inch]),
        ])

    tbl = Table(rows, colWidths=[3.3 * inch, 3.3 * inch])
    tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    items.append(tbl)
    return items


def _education_section(education: list) -> list:
    items = _section_header("Education")
    for edu in education:
        items.append(Paragraph(
            f"<b>{edu['degree']}</b> — {edu['school']}, {edu['location']}",
            BODY_STYLE,
        ))
        items.append(Paragraph(f"{edu['graduation']}", ROLE_META_STYLE))
        if edu.get("courses"):
            items.append(Paragraph(
                f"Relevant courses: {edu['courses']}", BODY_STYLE
            ))
    return items


def _key_project_section(project: dict) -> list:
    items = _section_header("Key Project")
    items.append(Paragraph(f"<b>{project['name']}</b>", BODY_STYLE))
    items.append(Paragraph(f"• {project['description']}", BULLET_STYLE))
    items.append(Paragraph(f"• Portfolio: {project['portfolio_url']}", BULLET_STYLE))
    return items


def _languages_section(languages: list) -> list:
    items = _section_header("Languages")
    items.append(Paragraph(" | ".join(languages), BODY_STYLE))
    return items


def build_resume(profile: dict, output_path: str) -> str:
    """Build a PDF resume from a profile dict. Returns the output path."""
    pathlib.Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.55 * inch,
    )

    emphasis = profile.get("_skills_emphasis")
    story = []
    story.extend(_header_section(profile))
    story.extend(_summary_section(profile.get("summary", "")))
    story.extend(_experience_section(profile.get("experience", [])))
    if profile.get("key_project"):
        story.extend(_key_project_section(profile["key_project"]))
    story.extend(_skills_section(profile.get("skills", {}), emphasis))
    story.extend(_education_section(profile.get("education", [])))
    story.extend(_languages_section(profile.get("languages", [])))

    doc.build(story)
    print(f"  [pdf] Resume saved: {output_path}")
    return output_path
