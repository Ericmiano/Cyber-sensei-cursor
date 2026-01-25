"""Quiz Engine: Implements CAT, BKT, and SM-2 algorithms."""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.learning import (
    UserConceptMastery,
    SpacedRepetitionSchedule,
    LearningEvent,
    EventType,
)
from app.models.topics import Concept
from app.core.config import settings


class QuizEngine:
    """Implements Computerized Adaptive Testing (CAT), BKT, and SM-2."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def select_next_question(
        self,
        user_id: str,
        concept_id: str,
        available_questions: List[Dict],
        previous_answers: List[Dict],
    ) -> Optional[Dict]:
        """
        Computerized Adaptive Testing (CAT): Select next question based on current ability estimate.
        
        Questions should have: {"id": "...", "difficulty": 0.0-1.0, "bloom_level": 1-6}
        """
        if not available_questions:
            return None
        
        # Get current mastery estimate
        mastery = await self.get_mastery(user_id, concept_id)
        
        # CAT: Select question with difficulty closest to current ability
        # If user is performing well, increase difficulty; if struggling, decrease
        if previous_answers:
            recent_correct = sum(1 for a in previous_answers[-5:] if a.get("correct", False))
            recent_total = len(previous_answers[-5:])
            if recent_total > 0:
                recent_accuracy = recent_correct / recent_total
                # Adjust target difficulty based on recent performance
                if recent_accuracy > 0.8:
                    target_difficulty = min(1.0, mastery + 0.2)
                elif recent_accuracy < 0.5:
                    target_difficulty = max(0.0, mastery - 0.2)
                else:
                    target_difficulty = mastery
            else:
                target_difficulty = mastery
        else:
            target_difficulty = mastery
        
        # Find question closest to target difficulty
        best_question = min(
            available_questions,
            key=lambda q: abs(q.get("difficulty", 0.5) - target_difficulty)
        )
        
        return best_question
    
    async def update_mastery_bkt(
        self,
        user_id: str,
        concept_id: str,
        is_correct: bool,
    ) -> float:
        """
        Update mastery using Bayesian Knowledge Tracing (BKT).
        
        BKT Parameters:
        - P(L0): Initial probability of knowing (mastery_probability)
        - P(T): Probability of learning (learn_rate)
        - P(G): Probability of guessing correctly (guess_rate)
        - P(S): Probability of slipping (slip_rate)
        """
        # Convert string IDs to UUIDs
        user_uuid = UUID(user_id)
        concept_uuid = UUID(concept_id)
        
        # Get or create mastery record
        stmt = select(UserConceptMastery).where(
            UserConceptMastery.user_id == user_uuid,
            UserConceptMastery.concept_id == concept_uuid,
        )
        result = await self.db.execute(stmt)
        mastery = result.scalar_one_or_none()
        
        if not mastery:
            # Create new mastery record
            mastery = UserConceptMastery(
                user_id=user_uuid,
                concept_id=concept_uuid,
                mastery_probability=settings.BKT_INITIAL_MASTERY,
                learn_rate=settings.BKT_LEARN_RATE,
                guess_rate=settings.BKT_GUESS_RATE,
                slip_rate=settings.BKT_SLIP_RATE,
            )
            self.db.add(mastery)
        
        # BKT update formula
        p_know = mastery.mastery_probability
        p_learn = mastery.learn_rate
        p_guess = mastery.guess_rate
        p_slip = mastery.slip_rate
        
        if is_correct:
            # P(know | correct) = P(know) * (1 - P(slip)) / P(correct)
            p_correct = p_know * (1 - p_slip) + (1 - p_know) * p_guess
            p_know_given_correct = (p_know * (1 - p_slip)) / p_correct if p_correct > 0 else p_know
            # Update: P(know) = P(know | correct) + (1 - P(know | correct)) * P(learn)
            new_mastery = p_know_given_correct + (1 - p_know_given_correct) * p_learn
            mastery.correct_attempts += 1
        else:
            # P(know | incorrect) = P(know) * P(slip) / P(incorrect)
            p_incorrect = p_know * p_slip + (1 - p_know) * (1 - p_guess)
            p_know_given_incorrect = (p_know * p_slip) / p_incorrect if p_incorrect > 0 else p_know
            # Update: P(know) = P(know | incorrect) (no learning on incorrect)
            new_mastery = p_know_given_incorrect
        
        mastery.mastery_probability = min(1.0, max(0.0, new_mastery))
        mastery.total_attempts += 1
        mastery.last_updated_at = datetime.utcnow()
        
        try:
            await self.db.commit()
            await self.db.refresh(mastery)
        except Exception as e:
            await self.db.rollback()
            raise
        
        return mastery.mastery_probability
    
    async def update_spaced_repetition_sm2(
        self,
        user_id: str,
        concept_id: str,
        quality: int,  # 0-5 (SM-2 quality rating)
    ) -> Dict:
        """
        Update spaced repetition schedule using SM-2 algorithm.
        
        Quality: 0 (complete blackout) to 5 (perfect recall)
        """
        # Convert string IDs to UUIDs
        user_uuid = UUID(user_id)
        concept_uuid = UUID(concept_id)
        
        stmt = select(SpacedRepetitionSchedule).where(
            SpacedRepetitionSchedule.user_id == user_uuid,
            SpacedRepetitionSchedule.concept_id == concept_uuid,
        )
        result = await self.db.execute(stmt)
        schedule = result.scalar_one_or_none()
        
        if not schedule:
            schedule = SpacedRepetitionSchedule(
                user_id=user_uuid,
                concept_id=concept_uuid,
                easiness_factor=settings.SM2_INITIAL_EASINESS,
                interval_days=1,
                repetitions=0,
                next_review_date=datetime.utcnow() + timedelta(days=1),
            )
            self.db.add(schedule)
        
        # SM-2 algorithm
        if quality < 3:  # Failed recall
            schedule.repetitions = 0
            schedule.interval_days = 1
        else:  # Successful recall
            schedule.repetitions += 1
            if schedule.repetitions == 1:
                schedule.interval_days = 1
            elif schedule.repetitions == 2:
                schedule.interval_days = 6
            else:
                schedule.interval_days = int(schedule.interval_days * schedule.easiness_factor)
        
        # Update easiness factor
        ef = schedule.easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        schedule.easiness_factor = max(settings.SM2_MIN_EASINESS, ef)
        
        schedule.next_review_date = datetime.utcnow() + timedelta(days=schedule.interval_days)
        schedule.last_reviewed_at = datetime.utcnow()
        
        try:
            await self.db.commit()
            await self.db.refresh(schedule)
        except Exception as e:
            await self.db.rollback()
            raise
        
        return {
            "easiness_factor": schedule.easiness_factor,
            "interval_days": schedule.interval_days,
            "repetitions": schedule.repetitions,
            "next_review_date": schedule.next_review_date.isoformat(),
        }
    
    async def get_mastery(self, user_id: str, concept_id: str) -> float:
        """Get current mastery probability for a user-concept pair."""
        user_uuid = UUID(user_id)
        concept_uuid = UUID(concept_id)
        stmt = select(UserConceptMastery).where(
            UserConceptMastery.user_id == user_uuid,
            UserConceptMastery.concept_id == concept_uuid,
        )
        result = await self.db.execute(stmt)
        mastery = result.scalar_one_or_none()
        return mastery.mastery_probability if mastery else settings.BKT_INITIAL_MASTERY
    
    def generate_actionable_critique(
        self,
        question: Dict,
        user_answer: str,
        correct_answer: str,
        concept: Concept,
    ) -> str:
        """
        Generate detailed feedback explaining why an answer was incorrect.
        """
        critique = f"Your answer: '{user_answer}'\n"
        critique += f"Correct answer: '{correct_answer}'\n\n"
        critique += f"Explanation:\n"
        critique += f"The concept '{concept.name}' requires understanding at Bloom's level {concept.bloom_level}. "
        critique += f"Consider reviewing the foundational principles and trying a different approach. "
        critique += f"Focus on: {concept.description or 'the core mechanics of this concept'}."
        return critique
