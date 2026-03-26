from __future__ import annotations


class CroatianLocalizer:
    """Placeholder Croatian localization interface."""

    def localize_summary(self, english_summary: str) -> str:
        return f"[HR Lokalizacija] {english_summary}"
