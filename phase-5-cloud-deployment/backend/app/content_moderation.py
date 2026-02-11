"""
Content Moderation System

Detect and filter inappropriate content, spam, and profanity.
"""

import logging
import re
from typing import Dict, Any, Optional, List, Set
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ModerationAction(str, Enum):
    """Moderation action types."""
    ALLOW = "allow"
    FLAG = "flag"
    BLOCK = "block"
    QUARANTINE = "quarantine"


class ModerationCategory(str, Enum):
    """Content moderation categories."""
    PROFANITY = "profanity"
    SPAM = "spam"
    HATE_SPEECH = "hate_speech"
    VIOLENCE = "violence"
    SEXUAL = "sexual"
    PERSONAL_INFO = "personal_info"
    MALICIOUS_LINK = "malicious_link"


class ModerationResult:
    """Content moderation result."""

    def __init__(
        self,
        action: ModerationAction,
        score: float,
        categories: List[ModerationCategory],
        reasons: List[str],
        flagged_content: Optional[List[str]] = None
    ):
        """Initialize moderation result."""
        self.action = action
        self.score = score
        self.categories = categories
        self.reasons = reasons
        self.flagged_content = flagged_content or []
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "action": self.action.value,
            "score": self.score,
            "categories": [c.value for c in self.categories],
            "reasons": self.reasons,
            "flagged_content": self.flagged_content,
            "timestamp": self.timestamp.isoformat()
        }

    def is_allowed(self) -> bool:
        """Check if content is allowed."""
        return self.action == ModerationAction.ALLOW

    def is_blocked(self) -> bool:
        """Check if content is blocked."""
        return self.action == ModerationAction.BLOCK


class ProfanityFilter:
    """Filter profanity and offensive language."""

    def __init__(self):
        """Initialize profanity filter."""
        # In production, load from comprehensive word list
        self.profanity_words: Set[str] = {
            "badword1", "badword2", "offensive1", "offensive2"
        }
        self.profanity_patterns = [
            re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
            for word in self.profanity_words
        ]

    def contains_profanity(self, text: str) -> bool:
        """Check if text contains profanity."""
        for pattern in self.profanity_patterns:
            if pattern.search(text):
                return True
        return False

    def find_profanity(self, text: str) -> List[str]:
        """Find all profanity in text."""
        found = []
        for pattern in self.profanity_patterns:
            matches = pattern.findall(text)
            found.extend(matches)
        return found

    def censor(self, text: str, replacement: str = "***") -> str:
        """Censor profanity in text."""
        result = text
        for pattern in self.profanity_patterns:
            result = pattern.sub(replacement, result)
        return result


class SpamDetector:
    """Detect spam content."""

    def __init__(self):
        """Initialize spam detector."""
        self.spam_patterns = [
            re.compile(r'(buy now|click here|limited time|act now)', re.IGNORECASE),
            re.compile(r'(viagra|cialis|pharmacy)', re.IGNORECASE),
            re.compile(r'(winner|congratulations|prize)', re.IGNORECASE),
            re.compile(r'(\$\$\$|!!!+|FREE)', re.IGNORECASE)
        ]

    def calculate_spam_score(self, text: str) -> float:
        """Calculate spam score (0-1)."""
        score = 0.0
        text_lower = text.lower()

        # Check spam patterns
        pattern_matches = sum(1 for p in self.spam_patterns if p.search(text))
        score += pattern_matches * 0.2

        # Check excessive capitalization
        if len(text) > 10:
            caps_ratio = sum(1 for c in text if c.isupper()) / len(text)
            if caps_ratio > 0.5:
                score += 0.3

        # Check excessive punctuation
        punct_count = sum(1 for c in text if c in '!?.')
        if punct_count > len(text) * 0.1:
            score += 0.2

        # Check repeated characters
        if re.search(r'(.)\1{3,}', text):
            score += 0.2

        # Check URL count
        url_count = len(re.findall(r'https?://\S+', text))
        if url_count > 2:
            score += 0.3

        return min(score, 1.0)

    def is_spam(self, text: str, threshold: float = 0.6) -> bool:
        """Check if text is spam."""
        return self.calculate_spam_score(text) >= threshold


class PersonalInfoDetector:
    """Detect personal information."""

    def __init__(self):
        """Initialize PII detector."""
        self.patterns = {
            "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            "phone": re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'),
            "ssn": re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
            "credit_card": re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b')
        }

    def find_pii(self, text: str) -> Dict[str, List[str]]:
        """Find personal information in text."""
        found = {}

        for pii_type, pattern in self.patterns.items():
            matches = pattern.findall(text)
            if matches:
                found[pii_type] = matches

        return found

    def contains_pii(self, text: str) -> bool:
        """Check if text contains PII."""
        return bool(self.find_pii(text))

    def redact_pii(self, text: str) -> str:
        """Redact personal information."""
        result = text

        for pii_type, pattern in self.patterns.items():
            result = pattern.sub(f"[REDACTED_{pii_type.upper()}]", result)

        return result


class LinkAnalyzer:
    """Analyze and validate links."""

    def __init__(self):
        """Initialize link analyzer."""
        self.suspicious_tlds = {".tk", ".ml", ".ga", ".cf", ".gq"}
        self.url_pattern = re.compile(r'https?://[^\s]+')

    def extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text."""
        return self.url_pattern.findall(text)

    def is_suspicious_url(self, url: str) -> bool:
        """Check if URL is suspicious."""
        url_lower = url.lower()

        # Check suspicious TLDs
        if any(url_lower.endswith(tld) for tld in self.suspicious_tlds):
            return True

        # Check for IP addresses
        if re.search(r'https?://\d+\.\d+\.\d+\.\d+', url):
            return True

        # Check for excessive subdomains
        domain_part = url.split("//")[1].split("/")[0] if "//" in url else url
        if domain_part.count(".") > 3:
            return True

        return False

    def analyze_links(self, text: str) -> Dict[str, Any]:
        """Analyze all links in text."""
        urls = self.extract_urls(text)
        suspicious = [url for url in urls if self.is_suspicious_url(url)]

        return {
            "total_urls": len(urls),
            "suspicious_urls": suspicious,
            "has_suspicious": len(suspicious) > 0
        }


class ContentModerator:
    """Main content moderation system."""

    def __init__(
        self,
        profanity_threshold: float = 0.0,
        spam_threshold: float = 0.6,
        block_pii: bool = True
    ):
        """Initialize content moderator."""
        self.profanity_filter = ProfanityFilter()
        self.spam_detector = SpamDetector()
        self.pii_detector = PersonalInfoDetector()
        self.link_analyzer = LinkAnalyzer()

        self.profanity_threshold = profanity_threshold
        self.spam_threshold = spam_threshold
        self.block_pii = block_pii

    def moderate(self, text: str) -> ModerationResult:
        """Moderate content."""
        score = 0.0
        categories = []
        reasons = []
        flagged_content = []

        # Check profanity
        if self.profanity_filter.contains_profanity(text):
            score += 0.8
            categories.append(ModerationCategory.PROFANITY)
            reasons.append("Contains profanity")
            flagged_content.extend(self.profanity_filter.find_profanity(text))

        # Check spam
        spam_score = self.spam_detector.calculate_spam_score(text)
        if spam_score >= self.spam_threshold:
            score += spam_score
            categories.append(ModerationCategory.SPAM)
            reasons.append(f"Spam score: {spam_score:.2f}")

        # Check PII
        pii_found = self.pii_detector.find_pii(text)
        if pii_found and self.block_pii:
            score += 0.5
            categories.append(ModerationCategory.PERSONAL_INFO)
            reasons.append(f"Contains PII: {', '.join(pii_found.keys())}")

        # Check links
        link_analysis = self.link_analyzer.analyze_links(text)
        if link_analysis["has_suspicious"]:
            score += 0.6
            categories.append(ModerationCategory.MALICIOUS_LINK)
            reasons.append(f"Suspicious links: {len(link_analysis['suspicious_urls'])}")
            flagged_content.extend(link_analysis["suspicious_urls"])

        # Determine action
        if score >= 0.8:
            action = ModerationAction.BLOCK
        elif score >= 0.5:
            action = ModerationAction.FLAG
        elif score >= 0.3:
            action = ModerationAction.QUARANTINE
        else:
            action = ModerationAction.ALLOW

        result = ModerationResult(
            action=action,
            score=min(score, 1.0),
            categories=categories,
            reasons=reasons,
            flagged_content=flagged_content
        )

        if not result.is_allowed():
            logger.warning(
                f"Content moderated: {action.value}",
                extra={
                    "action": action.value,
                    "score": result.score,
                    "categories": [c.value for c in categories]
                }
            )

        return result

    def sanitize(self, text: str) -> str:
        """Sanitize content by removing/censoring violations."""
        # Censor profanity
        result = self.profanity_filter.censor(text)

        # Redact PII
        if self.block_pii:
            result = self.pii_detector.redact_pii(result)

        return result


# Global moderator
content_moderator = ContentModerator()


# Helper functions
def moderate_content(text: str) -> ModerationResult:
    """Moderate content."""
    return content_moderator.moderate(text)


def sanitize_content(text: str) -> str:
    """Sanitize content."""
    return content_moderator.sanitize(text)


def is_content_safe(text: str) -> bool:
    """Check if content is safe."""
    result = content_moderator.moderate(text)
    return result.is_allowed()
