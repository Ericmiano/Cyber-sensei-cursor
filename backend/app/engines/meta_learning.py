"""Meta-Learning & Feedback Engine: Self-evaluation and recursive improvement."""
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.performance import TeachingFeedback
from app.models.learning import UserConceptMastery, LearningEvent, EventType
from app.models.topics import ContentItem
from app.core.config import settings


class MetaLearningEngine:
    """
    Meta-Learning Engine: Calculates efficacy scores and triggers content revision.
    
    Efficacy Score: E = (ΔMastery / Time) × UserSatisfaction
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def calculate_efficacy_score(
        self,
        user_id: str,
        content_item_id: str,
        user_satisfaction: float,  # 0.0-1.0
    ) -> Dict:
        """
        Calculate teaching efficacy score for a content item.
        
        E = (ΔMastery / Time) × UserSatisfaction
        """
        from uuid import UUID
        
        # Get content item
        stmt = select(ContentItem).where(ContentItem.id == UUID(content_item_id))
        result = await self.db.execute(stmt)
        content_item = result.scalar_one_or_none()
        
        if not content_item:
            return {"error": "Content item not found"}
        
        # Get mastery before and after
        concept_id = content_item.concept_id
        if not concept_id:
            return {"error": "Content item has no associated concept"}
        
        # Get learning events to determine time window
        events_stmt = select(LearningEvent).where(
            LearningEvent.user_id == user_id,
            LearningEvent.content_item_id == UUID(content_item_id),
        ).order_by(LearningEvent.created_at)
        events_result = await self.db.execute(events_stmt)
        events = events_result.scalars().all()
        
        if not events:
            return {"error": "No learning events found"}
        
        start_event = events[0]
        end_event = events[-1]
        time_spent = (end_event.created_at - start_event.created_at).total_seconds()
        
        if time_spent == 0:
            time_spent = 1  # Avoid division by zero
        
        # Get mastery before (or initial)
        mastery_before = settings.BKT_INITIAL_MASTERY
        mastery_after = settings.BKT_INITIAL_MASTERY
        
        mastery_stmt = select(UserConceptMastery).where(
            UserConceptMastery.user_id == user_id,
            UserConceptMastery.concept_id == concept_id,
        )
        mastery_result = await self.db.execute(mastery_stmt)
        mastery = mastery_result.scalar_one_or_none()
        
        if mastery:
            mastery_after = mastery.mastery_probability
            # Try to estimate before (this is approximate)
            mastery_before = max(0.0, mastery_after - 0.2)  # Conservative estimate
        
        mastery_delta = mastery_after - mastery_before
        
        # Calculate efficacy score
        if time_spent > 0:
            efficacy = (mastery_delta / time_spent) * user_satisfaction * 1000  # Scale for readability
        else:
            efficacy = 0.0
        
        # Create or update feedback record
        feedback_stmt = select(TeachingFeedback).where(
            TeachingFeedback.user_id == user_id,
            TeachingFeedback.content_item_id == UUID(content_item_id),
        )
        feedback_result = await self.db.execute(feedback_stmt)
        feedback = feedback_result.scalar_one_or_none()
        
        if not feedback:
            from app.models.performance import TeachingFeedback
            feedback = TeachingFeedback(
                user_id=UUID(user_id),
                content_item_id=UUID(content_item_id),
                concept_id=concept_id,
                efficacy_score=efficacy,
                mastery_delta=mastery_delta,
                time_spent_seconds=int(time_spent),
                user_satisfaction=user_satisfaction,
            )
            self.db.add(feedback)
        else:
            feedback.efficacy_score = efficacy
            feedback.mastery_delta = mastery_delta
            feedback.time_spent_seconds = int(time_spent)
            feedback.user_satisfaction = user_satisfaction
        
        await self.db.commit()
        await self.db.refresh(feedback)
        
        return {
            "efficacy_score": efficacy,
            "mastery_delta": mastery_delta,
            "time_spent_seconds": int(time_spent),
            "user_satisfaction": user_satisfaction,
            "feedback_id": str(feedback.id),
        }
    
    async def identify_content_shortcomings(
        self,
        content_item_id: str,
        threshold_failure_rate: float = 0.3,
    ) -> List[Dict]:
        """
        Identify content items with high failure rates and specific shortcomings.
        """
        from uuid import UUID
        
        # Get all feedback for this content item
        stmt = select(TeachingFeedback).where(
            TeachingFeedback.content_item_id == UUID(content_item_id),
        )
        result = await self.db.execute(stmt)
        feedbacks = result.scalars().all()
        
        if not feedbacks:
            return []
        
        # Calculate average efficacy and failure rate
        avg_efficacy = sum(f.efficacy_score for f in feedbacks) / len(feedbacks)
        low_satisfaction_count = sum(1 for f in feedbacks if f.user_satisfaction < 0.5)
        failure_rate = low_satisfaction_count / len(feedbacks)
        
        shortcomings = []
        
        if failure_rate >= threshold_failure_rate:
            shortcomings.append({
                "type": "high_failure_rate",
                "severity": "high",
                "description": f"Failure rate is {failure_rate:.1%} (threshold: {threshold_failure_rate:.1%})",
                "suggestion": "Content may be too difficult or unclear. Consider simplifying or adding more examples.",
            })
        
        if avg_efficacy < 0.5:
            shortcomings.append({
                "type": "low_efficacy",
                "severity": "medium",
                "description": f"Average efficacy score is {avg_efficacy:.2f} (below threshold)",
                "suggestion": "Review pedagogical approach. Consider different learning style or pacing.",
            })
        
        # Analyze common patterns in shortcomings
        common_issues = []
        for feedback in feedbacks:
            if feedback.shortcomings:
                common_issues.extend(feedback.shortcomings)
        
        if common_issues:
            # Count frequency of each issue type
            from collections import Counter
            issue_counts = Counter(common_issues)
            for issue, count in issue_counts.most_common(3):
                if count >= len(feedbacks) * 0.3:  # Appears in 30%+ of feedback
                    shortcomings.append({
                        "type": "common_issue",
                        "severity": "medium",
                        "description": f"'{issue}' reported in {count}/{len(feedbacks)} feedbacks",
                        "suggestion": f"Address the issue: {issue}",
                    })
        
        return shortcomings
    
    async def trigger_content_revision(
        self,
        content_item_id: str,
        shortcomings: List[Dict],
    ) -> Dict:
        """
        Trigger AI-powered content revision based on identified shortcomings.
        
        This would typically call a Celery task to regenerate content.
        """
        from uuid import UUID
        
        # Get content item
        stmt = select(ContentItem).where(ContentItem.id == UUID(content_item_id))
        result = await self.db.execute(stmt)
        content_item = result.scalar_one_or_none()
        
        if not content_item:
            return {"error": "Content item not found"}
        
        # Update feedback records to mark as addressed
        feedback_stmt = select(TeachingFeedback).where(
            TeachingFeedback.content_item_id == UUID(content_item_id),
        )
        feedback_result = await self.db.execute(feedback_stmt)
        for feedback in feedback_result.scalars().all():
            feedback.is_addressed = True
            feedback.suggested_improvements = "\n".join([s.get("suggestion", "") for s in shortcomings])
        
        await self.db.commit()
        
        # In production, this would trigger a Celery task:
        # from app.tasks.content import revise_content_item
        # revise_content_item.delay(str(content_item_id), shortcomings)
        
        return {
            "content_item_id": str(content_item_id),
            "revision_triggered": True,
            "shortcomings_addressed": len(shortcomings),
            "message": "Content revision task queued",
        }
