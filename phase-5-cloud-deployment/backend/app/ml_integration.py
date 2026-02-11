"""
Machine Learning Integration

Integrate ML models for predictions and recommendations.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class TodoPriorityPredictor:
    """Predict todo priority based on content."""

    def __init__(self):
        """Initialize priority predictor."""
        self.keywords = {
            "high": ["urgent", "asap", "critical", "important", "emergency"],
            "medium": ["soon", "needed", "should", "consider"],
            "low": ["maybe", "someday", "optional", "nice to have"]
        }

    def predict_priority(self, title: str, description: Optional[str] = None) -> str:
        """Predict priority for todo."""
        text = (title + " " + (description or "")).lower()

        # Count keyword matches
        scores = {"high": 0, "medium": 0, "low": 0}

        for priority, keywords in self.keywords.items():
            for keyword in keywords:
                if keyword in text:
                    scores[priority] += 1

        # Return priority with highest score
        if scores["high"] > 0:
            return "high"
        elif scores["medium"] > 0:
            return "medium"
        else:
            return "low"


class DueDatePredictor:
    """Predict due date based on historical data."""

    def __init__(self):
        """Initialize due date predictor."""
        self.completion_times: Dict[str, List[float]] = defaultdict(list)

    def record_completion(self, priority: str, days_to_complete: float):
        """Record completion time."""
        self.completion_times[priority].append(days_to_complete)

    def predict_due_date(self, priority: str) -> Optional[datetime]:
        """Predict due date based on priority."""
        if priority not in self.completion_times or not self.completion_times[priority]:
            # Default predictions
            defaults = {"high": 1, "medium": 3, "low": 7}
            days = defaults.get(priority, 3)
        else:
            # Average completion time
            avg_days = sum(self.completion_times[priority]) / len(self.completion_times[priority])
            days = int(avg_days * 1.2)  # Add 20% buffer

        return datetime.utcnow() + timedelta(days=days)


class TodoRecommender:
    """Recommend todos based on user behavior."""

    def __init__(self):
        """Initialize todo recommender."""
        self.user_patterns: Dict[int, Dict[str, Any]] = {}

    def record_user_action(self, user_id: int, action: str, todo_data: Dict[str, Any]):
        """Record user action."""
        if user_id not in self.user_patterns:
            self.user_patterns[user_id] = {
                "priorities": defaultdict(int),
                "tags": defaultdict(int),
                "completion_times": []
            }

        patterns = self.user_patterns[user_id]

        if action == "create":
            patterns["priorities"][todo_data.get("priority", "medium")] += 1

            if "tags" in todo_data:
                for tag in todo_data["tags"]:
                    patterns["tags"][tag] += 1

        elif action == "complete":
            if "completion_time" in todo_data:
                patterns["completion_times"].append(todo_data["completion_time"])

    def get_recommended_priority(self, user_id: int) -> str:
        """Get recommended priority for user."""
        if user_id not in self.user_patterns:
            return "medium"

        priorities = self.user_patterns[user_id]["priorities"]
        if not priorities:
            return "medium"

        # Return most used priority
        return max(priorities.items(), key=lambda x: x[1])[0]

    def get_recommended_tags(self, user_id: int, limit: int = 5) -> List[str]:
        """Get recommended tags for user."""
        if user_id not in self.user_patterns:
            return []

        tags = self.user_patterns[user_id]["tags"]
        if not tags:
            return []

        # Return most used tags
        sorted_tags = sorted(tags.items(), key=lambda x: x[1], reverse=True)
        return [tag for tag, _ in sorted_tags[:limit]]

    def get_similar_todos(self, todo: Dict[str, Any], all_todos: List[Dict[str, Any]], limit: int = 5) -> List[Dict[str, Any]]:
        """Find similar todos."""
        # Simple similarity based on tags and priority
        similar = []

        todo_tags = set(todo.get("tags", []))
        todo_priority = todo.get("priority", "medium")

        for other_todo in all_todos:
            if other_todo.get("id") == todo.get("id"):
                continue

            other_tags = set(other_todo.get("tags", []))
            other_priority = other_todo.get("priority", "medium")

            # Calculate similarity score
            score = 0

            # Tag overlap
            if todo_tags and other_tags:
                overlap = len(todo_tags & other_tags)
                score += overlap * 2

            # Same priority
            if todo_priority == other_priority:
                score += 1

            if score > 0:
                similar.append((score, other_todo))

        # Sort by score and return top N
        similar.sort(key=lambda x: x[0], reverse=True)
        return [todo for _, todo in similar[:limit]]


class ProductivityAnalyzer:
    """Analyze user productivity patterns."""

    def __init__(self):
        """Initialize productivity analyzer."""
        self.user_stats: Dict[int, Dict[str, Any]] = {}

    def record_completion(self, user_id: int, todo: Dict[str, Any], completion_time: float):
        """Record todo completion."""
        if user_id not in self.user_stats:
            self.user_stats[user_id] = {
                "total_completed": 0,
                "total_time": 0,
                "by_priority": defaultdict(lambda: {"count": 0, "time": 0}),
                "by_hour": defaultdict(int)
            }

        stats = self.user_stats[user_id]
        stats["total_completed"] += 1
        stats["total_time"] += completion_time

        priority = todo.get("priority", "medium")
        stats["by_priority"][priority]["count"] += 1
        stats["by_priority"][priority]["time"] += completion_time

        # Record completion hour
        hour = datetime.utcnow().hour
        stats["by_hour"][hour] += 1

    def get_productivity_score(self, user_id: int) -> float:
        """Calculate productivity score (0-100)."""
        if user_id not in self.user_stats:
            return 0.0

        stats = self.user_stats[user_id]
        total = stats["total_completed"]

        if total == 0:
            return 0.0

        # Simple scoring based on completion count
        # In production, use more sophisticated metrics
        score = min(total * 2, 100)
        return score

    def get_best_time_to_work(self, user_id: int) -> Optional[int]:
        """Get best hour for user to work."""
        if user_id not in self.user_stats:
            return None

        by_hour = self.user_stats[user_id]["by_hour"]
        if not by_hour:
            return None

        # Return hour with most completions
        return max(by_hour.items(), key=lambda x: x[1])[0]

    def get_insights(self, user_id: int) -> Dict[str, Any]:
        """Get productivity insights."""
        if user_id not in self.user_stats:
            return {}

        stats = self.user_stats[user_id]

        insights = {
            "total_completed": stats["total_completed"],
            "productivity_score": self.get_productivity_score(user_id),
            "best_time": self.get_best_time_to_work(user_id)
        }

        # Average completion time
        if stats["total_completed"] > 0:
            insights["avg_completion_time"] = stats["total_time"] / stats["total_completed"]

        # Priority breakdown
        insights["by_priority"] = dict(stats["by_priority"])

        return insights


class SmartSuggestions:
    """Generate smart suggestions for users."""

    def __init__(
        self,
        priority_predictor: TodoPriorityPredictor,
        due_date_predictor: DueDatePredictor,
        recommender: TodoRecommender
    ):
        """Initialize smart suggestions."""
        self.priority_predictor = priority_predictor
        self.due_date_predictor = due_date_predictor
        self.recommender = recommender

    def suggest_todo_properties(
        self,
        user_id: int,
        title: str,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Suggest properties for new todo."""
        suggestions = {}

        # Predict priority
        suggestions["priority"] = self.priority_predictor.predict_priority(title, description)

        # Predict due date
        suggestions["due_date"] = self.due_date_predictor.predict_due_date(suggestions["priority"])

        # Recommend tags
        suggestions["tags"] = self.recommender.get_recommended_tags(user_id)

        return suggestions

    def suggest_next_actions(self, user_id: int, current_todos: List[Dict[str, Any]]) -> List[str]:
        """Suggest next actions for user."""
        suggestions = []

        # Check for overdue todos
        overdue = [t for t in current_todos if self._is_overdue(t)]
        if overdue:
            suggestions.append(f"You have {len(overdue)} overdue todos. Consider completing them first.")

        # Check for high priority todos
        high_priority = [t for t in current_todos if t.get("priority") == "high" and not t.get("completed")]
        if high_priority:
            suggestions.append(f"Focus on {len(high_priority)} high priority todos.")

        # Check for todos without due dates
        no_due_date = [t for t in current_todos if not t.get("due_date") and not t.get("completed")]
        if no_due_date:
            suggestions.append(f"Add due dates to {len(no_due_date)} todos for better planning.")

        return suggestions

    def _is_overdue(self, todo: Dict[str, Any]) -> bool:
        """Check if todo is overdue."""
        if todo.get("completed"):
            return False

        due_date = todo.get("due_date")
        if not due_date:
            return False

        if isinstance(due_date, str):
            due_date = datetime.fromisoformat(due_date)

        return datetime.utcnow() > due_date


# Global instances
priority_predictor = TodoPriorityPredictor()
due_date_predictor = DueDatePredictor()
todo_recommender = TodoRecommender()
productivity_analyzer = ProductivityAnalyzer()
smart_suggestions = SmartSuggestions(priority_predictor, due_date_predictor, todo_recommender)


# Helper functions
def predict_todo_priority(title: str, description: Optional[str] = None) -> str:
    """Predict todo priority."""
    return priority_predictor.predict_priority(title, description)


def get_smart_suggestions(user_id: int, title: str, description: Optional[str] = None) -> Dict[str, Any]:
    """Get smart suggestions for todo."""
    return smart_suggestions.suggest_todo_properties(user_id, title, description)


def analyze_productivity(user_id: int) -> Dict[str, Any]:
    """Analyze user productivity."""
    return productivity_analyzer.get_insights(user_id)
