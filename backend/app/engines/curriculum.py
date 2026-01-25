"""Curriculum Engine: Generates personalized learning sequences using topological sort and Bloom weighting."""
from typing import List, Dict, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
import logging
from app.models.topics import Concept, ConceptEdge, Topic
from app.models.learning import UserConceptMastery
from app.core.config import settings
from app.core.error_handlers import DatabaseError, NotFoundError

logger = logging.getLogger(__name__)


class CurriculumEngine:
    """Generates personalized curriculum using prerequisite graphs and Bloom's Taxonomy."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def generate_curriculum(
        self,
        user_id: str,
        topic_id: str,
        target_bloom_level: int = 3,
    ) -> List[Dict]:
        """
        Generate a personalized curriculum sequence.
        
        Uses:
        - Topological sort for prerequisite ordering
        - Bloom weighting for difficulty progression
        - User mastery data to skip known concepts
        """
        try:
            # Validate inputs
            if not 1 <= target_bloom_level <= 6:
                raise ValueError("Target Bloom level must be between 1 and 6")
            
            # Convert string IDs to UUIDs
            try:
                topic_uuid = UUID(topic_id)
                user_uuid = UUID(user_id)
            except ValueError as e:
                raise ValueError(f"Invalid UUID format: {e}")
            
            # Get all concepts for the topic
            stmt = select(Concept).where(Concept.topic_id == topic_uuid)
            result = await self.db.execute(stmt)
            concepts = result.scalars().all()
            
            if not concepts:
                logger.warning(f"No concepts found for topic {topic_id}")
                return []
            
            # Get user mastery for these concepts
            mastery_stmt = select(UserConceptMastery).where(
                UserConceptMastery.user_id == user_uuid,
                UserConceptMastery.concept_id.in_([c.id for c in concepts])
            )
            mastery_result = await self.db.execute(mastery_stmt)
            mastery_dict = {m.concept_id: m.mastery_probability for m in mastery_result.scalars().all()}
            
            # Get prerequisite edges
            edges_stmt = select(ConceptEdge).where(
                ConceptEdge.concept_id.in_([c.id for c in concepts])
            )
            edges_result = await self.db.execute(edges_stmt)
            edges = edges_result.scalars().all()
            
            # Build prerequisite graph
            graph: Dict[str, List[str]] = {str(c.id): [] for c in concepts}
            in_degree: Dict[str, int] = {str(c.id): 0 for c in concepts}
            
            for edge in edges:
                concept_id = str(edge.concept_id)
                prereq_id = str(edge.prerequisite_id)
                if prereq_id in graph:
                    graph[prereq_id].append(concept_id)
                    in_degree[concept_id] += 1
            
            # Topological sort (Kahn's algorithm)
            queue = []
            for concept in concepts:
                concept_id = str(concept.id)
                mastery = mastery_dict.get(concept.id, 0.0)
                # Skip concepts with high mastery (>0.8) or add to queue if no prerequisites
                if in_degree[concept_id] == 0 and mastery < 0.8:
                    queue.append(concept)
            
            curriculum = []
            processed = set()
            
            while queue:
                # Sort by Bloom level and difficulty (ascending)
                queue.sort(key=lambda c: (c.bloom_level, c.difficulty))
                current = queue.pop(0)
                current_id = str(current.id)
                
                if current_id in processed:
                    continue
                
                processed.add(current_id)
                mastery = mastery_dict.get(current.id, 0.0)
                
                # Only include if mastery is below threshold and Bloom level is appropriate
                if mastery < 0.8 and current.bloom_level <= target_bloom_level:
                    curriculum.append({
                        "concept_id": str(current.id),
                        "concept_name": current.name,
                        "bloom_level": current.bloom_level,
                        "difficulty": current.difficulty,
                        "estimated_time_minutes": current.estimated_time_minutes,
                        "current_mastery": mastery,
                        "order": len(curriculum) + 1,
                    })
                
                # Add dependent concepts to queue
                for dependent_id in graph.get(current_id, []):
                    in_degree[dependent_id] -= 1
                    if in_degree[dependent_id] == 0:
                        dependent = next((c for c in concepts if str(c.id) == dependent_id), None)
                        if dependent and str(dependent.id) not in processed:
                            queue.append(dependent)
            
            logger.info(
                f"Curriculum generated: {len(curriculum)} concepts for topic {topic_id}, "
                f"user {user_id}, target Bloom level {target_bloom_level}"
            )
            
            return curriculum
        except ValueError as e:
            logger.error(f"Validation error in generate_curriculum: {e}")
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error in generate_curriculum: {e}", exc_info=True)
            raise DatabaseError("Failed to generate curriculum", e)
        except Exception as e:
            logger.error(f"Unexpected error in generate_curriculum: {e}", exc_info=True)
            raise
    
    def calculate_reliability_score(
        self,
        domain_authority: float,
        age_bonus: float,
        peer_reviewed: bool,
    ) -> float:
        """
        Calculate source reliability score.
        
        Formula: (domain_authority * weight + age_bonus * weight + peer_review * weight)
        Weights sum to 1.0, so no division needed.
        """
        peer_review_score = 1.0 if peer_reviewed else 0.0
        score = (
            domain_authority * settings.DOMAIN_AUTHORITY_WEIGHT +
            age_bonus * settings.AGE_BONUS_WEIGHT +
            peer_review_score * settings.PEER_REVIEW_WEIGHT
        )
        return min(1.0, max(0.0, score))
