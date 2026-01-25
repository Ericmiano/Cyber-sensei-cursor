"""Recommendation Engine: Provides explainable next-step recommendations."""
from typing import List, Dict, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.learning import UserConceptMastery, SpacedRepetitionSchedule, UserProgress
from app.models.topics import Concept, ContentItem
from datetime import datetime


class RecommendationEngine:
    """Generates explainable recommendations for next learning steps."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_recommendations(
        self,
        user_id: str,
        limit: int = 5,
    ) -> List[Dict]:
        """
        Generate personalized recommendations with explicit reasoning.
        
        Returns recommendations with:
        - Action type (review, learn, practice, etc.)
        - Target concept/content
        - Reasoning explanation
        - Priority score
        """
        recommendations = []
        
        # 1. Check for concepts needing review (spaced repetition due)
        due_reviews = await self._get_due_reviews(user_id)
        for review in due_reviews:
            recommendations.append({
                "type": "review",
                "concept_id": str(review["concept_id"]),
                "concept_name": review["concept_name"],
                "reasoning": f"Review '{review['concept_name']}' - spaced repetition due (last reviewed {review['days_since']} days ago)",
                "priority": 0.9,
                "action": "Start review session",
            })
        
        # 2. Check for low mastery concepts
        low_mastery = await self._get_low_mastery_concepts(user_id, threshold=0.7)
        for concept in low_mastery:
            recommendations.append({
                "type": "learn",
                "concept_id": str(concept["concept_id"]),
                "concept_name": concept["concept_name"],
                "reasoning": f"Mastery of '{concept['concept_name']}' is {concept['mastery']:.1%} (below 70% threshold). Focus on building foundational understanding.",
                "priority": 0.8 - concept["mastery"],  # Higher priority for lower mastery
                "action": "Study concept",
            })
        
        # 3. Check for incomplete content items
        incomplete = await self._get_incomplete_content(user_id)
        for item in incomplete:
            recommendations.append({
                "type": "continue",
                "content_item_id": str(item["content_item_id"]),
                "title": item["title"],
                "reasoning": f"Continue '{item['title']}' - {item['progress']:.0%} complete",
                "priority": 0.6,
                "action": "Resume learning",
            })
        
        # Sort by priority and return top N
        recommendations.sort(key=lambda x: x["priority"], reverse=True)
        return recommendations[:limit]
    
    async def _get_due_reviews(self, user_id: str) -> List[Dict]:
        """Get concepts that are due for spaced repetition review."""
        user_uuid = UUID(user_id)
        stmt = select(
            SpacedRepetitionSchedule,
            Concept,
        ).join(
            Concept, SpacedRepetitionSchedule.concept_id == Concept.id
        ).where(
            and_(
                SpacedRepetitionSchedule.user_id == user_uuid,
                SpacedRepetitionSchedule.next_review_date <= datetime.utcnow(),
            )
        )
        result = await self.db.execute(stmt)
        reviews = []
        for schedule, concept in result.all():
            days_since = (datetime.utcnow() - schedule.last_reviewed_at).days if schedule.last_reviewed_at else 0
            reviews.append({
                "concept_id": concept.id,
                "concept_name": concept.name,
                "days_since": days_since,
            })
        return reviews
    
    async def _get_low_mastery_concepts(
        self,
        user_id: str,
        threshold: float = 0.7,
    ) -> List[Dict]:
        """Get concepts with mastery below threshold."""
        user_uuid = UUID(user_id)
        stmt = select(
            UserConceptMastery,
            Concept,
        ).join(
            Concept, UserConceptMastery.concept_id == Concept.id
        ).where(
            and_(
                UserConceptMastery.user_id == user_uuid,
                UserConceptMastery.mastery_probability < threshold,
            )
        ).order_by(
            UserConceptMastery.mastery_probability.asc()
        )
        result = await self.db.execute(stmt)
        concepts = []
        for mastery, concept in result.all():
            concepts.append({
                "concept_id": concept.id,
                "concept_name": concept.name,
                "mastery": mastery.mastery_probability,
            })
        return concepts
    
    async def _get_incomplete_content(self, user_id: str) -> List[Dict]:
        """Get content items that are in progress but not completed."""
        user_uuid = UUID(user_id)
        stmt = select(
            UserProgress,
            ContentItem,
        ).join(
            ContentItem, UserProgress.content_item_id == ContentItem.id
        ).where(
            and_(
                UserProgress.user_id == user_uuid,
                UserProgress.is_completed == False,
                UserProgress.progress_percentage > 0,
            )
        ).order_by(
            UserProgress.last_accessed_at.desc()
        )
        result = await self.db.execute(stmt)
        items = []
        for progress, content in result.all():
            items.append({
                "content_item_id": content.id,
                "title": content.title,
                "progress": progress.progress_percentage / 100.0,
            })
        return items
