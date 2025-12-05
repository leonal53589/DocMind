"""Classification service for automatic content categorization."""

import re
from typing import Optional
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings, ClassificationRule as ConfigRule
from ..models import Category, ClassificationRule


class Classifier:
    """Hybrid classifier using rules and optional AI."""

    # Default classification rules
    DEFAULT_RULES = {
        "Mathematical Principles": {
            "keywords": [
                "theorem", "proof", "lemma", "corollary", "equation", "formula",
                "calculus", "algebra", "geometry", "topology", "matrix", "vector",
                "integral", "derivative", "function", "polynomial", "linear",
                "mathematical", "mathematics", "math", "数学", "定理", "证明",
            ],
            "file_types": [".tex", ".nb", ".m", ".maple"],
            "path_patterns": ["math", "Mathematics"],
        },
        "Ideas & Concepts": {
            "keywords": [
                "idea", "concept", "thought", "hypothesis", "theory", "proposal",
                "brainstorm", "innovation", "insight", "perspective", "想法",
                "creative", "design", "architecture", "strategy", "philosophy",
            ],
            "file_types": [],
            "path_patterns": ["ideas", "concepts", "notes"],
        },
        "Program Implementation": {
            "keywords": [
                "code", "function", "class", "method", "algorithm", "implementation",
                "software", "program", "api", "library", "framework", "module",
                "debug", "compile", "runtime", "database", "server", "client",
                "代码", "程序", "实现", "import", "export", "async", "await",
            ],
            "file_types": [
                ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".c", ".cpp",
                ".go", ".rs", ".rb", ".php", ".swift", ".kt", ".scala",
            ],
            "path_patterns": ["src", "code", "scripts", "lib"],
        },
        "Affairs & Tasks": {
            "keywords": [
                "todo", "task", "meeting", "schedule", "deadline", "agenda",
                "appointment", "reminder", "event", "calendar", "plan",
                "project", "milestone", "任务", "会议", "日程", "待办",
            ],
            "file_types": [],
            "path_patterns": ["tasks", "todos", "meetings"],
        },
    }

    def __init__(self):
        self.settings = get_settings()
        self._category_cache: dict[str, int] = {}

    async def classify(
        self,
        text: str,
        file_path: Optional[Path] = None,
        session: Optional[AsyncSession] = None,
    ) -> tuple[Optional[int], float]:
        """
        Classify content and return category_id and confidence.

        Args:
            text: Text content to classify
            file_path: Optional file path for additional hints
            session: Database session for looking up category IDs

        Returns:
            Tuple of (category_id, confidence)
        """
        scores: dict[str, float] = {}

        # Apply rule-based classification
        for category_name, rules in self.DEFAULT_RULES.items():
            score = self._calculate_rule_score(text, file_path, rules)
            if score > 0:
                scores[category_name] = score

        # Apply config-based rules
        for rule in self.settings.classification.rules:
            score = self._calculate_config_rule_score(text, file_path, rule)
            if score > 0:
                existing = scores.get(rule.category, 0)
                scores[rule.category] = max(existing, score)

        if not scores:
            return None, 0.0

        # Get best match
        best_category = max(scores, key=scores.get)
        best_score = scores[best_category]

        # Normalize confidence (0-1)
        confidence = min(best_score / 10.0, 1.0)

        # Look up category ID
        if session:
            category_id = await self._get_category_id(session, best_category)
            return category_id, confidence

        return None, confidence

    def _calculate_rule_score(
        self,
        text: str,
        file_path: Optional[Path],
        rules: dict,
    ) -> float:
        """Calculate classification score based on rules."""
        score = 0.0
        text_lower = text.lower()

        # Keyword matching
        keywords = rules.get("keywords", [])
        for keyword in keywords:
            if keyword.lower() in text_lower:
                score += 1.0

        # File type matching
        if file_path:
            file_types = rules.get("file_types", [])
            ext = file_path.suffix.lower()
            if ext in file_types:
                score += 3.0  # Strong signal

            # Path pattern matching
            path_patterns = rules.get("path_patterns", [])
            path_str = str(file_path).lower()
            for pattern in path_patterns:
                if pattern.lower() in path_str:
                    score += 2.0

        return score

    def _calculate_config_rule_score(
        self,
        text: str,
        file_path: Optional[Path],
        rule: ConfigRule,
    ) -> float:
        """Calculate score from configuration rule."""
        score = 0.0
        text_lower = text.lower()

        # Keywords
        for keyword in rule.keywords:
            if keyword.lower() in text_lower:
                score += 1.0

        # File types
        if file_path:
            ext = file_path.suffix.lower()
            if ext in rule.file_types:
                score += 3.0

            # Path patterns
            path_str = str(file_path).lower()
            for pattern in rule.path_patterns:
                if pattern.lower() in path_str:
                    score += 2.0

        return score

    async def _get_category_id(
        self,
        session: AsyncSession,
        category_name: str,
    ) -> Optional[int]:
        """Get category ID by name, with caching."""
        if category_name in self._category_cache:
            return self._category_cache[category_name]

        result = await session.execute(
            select(Category.id).where(Category.name == category_name)
        )
        category_id = result.scalar_one_or_none()

        if category_id:
            self._category_cache[category_name] = category_id

        return category_id

    async def classify_with_ai(
        self,
        text: str,
        categories: list[str],
    ) -> tuple[Optional[str], float]:
        """
        Classify using local LLM via Ollama.

        Falls back to rule-based if AI is unavailable.
        """
        if not self.settings.classification.use_ai:
            return None, 0.0

        try:
            import httpx

            prompt = f"""Classify the following text into one of these categories: {', '.join(categories)}

Text: {text[:2000]}

Respond with only the category name, nothing else."""

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.settings.classification.ollama_url}/api/generate",
                    json={
                        "model": self.settings.classification.ollama_model,
                        "prompt": prompt,
                        "stream": False,
                    },
                    timeout=30.0,
                )

                if response.status_code == 200:
                    result = response.json()
                    category = result.get("response", "").strip()

                    # Validate category
                    if category in categories:
                        return category, 0.85  # High confidence for AI

        except Exception as e:
            print(f"AI classification failed: {e}")

        return None, 0.0
