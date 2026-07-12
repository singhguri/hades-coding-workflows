"""
Hades Coding Workflows — Hermes plugin.

Auto-registers coding workflow skills so they're available as
skill_view("hades-coding-workflows:skill-name").
"""

from pathlib import Path


def register(ctx):
    skills_dir = Path(__file__).parent / "skills"
    for child in sorted(skills_dir.iterdir()):
        skill_md = child / "SKILL.md"
        if child.is_dir() and skill_md.exists():
            ctx.register_skill(child.name, skill_md)
