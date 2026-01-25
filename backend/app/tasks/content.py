"""Content generation and revision tasks."""
import asyncio
from uuid import UUID
from app.tasks.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.core.logging_config import logger
from app.models.topics import Concept, Topic, ContentItem, ContentType, BloomLevel
from app.models.sources import Chunk
from app.services.llm_service import llm_service
from app.services.vector_db_service import vector_db_service
from app.services.embedding_service import embedding_service
from sqlalchemy import select
from typing import List, Dict


@celery_app.task(name="generate_content", bind=True, max_retries=3)
def generate_content(
    self,
    topic_id: str,
    concept_id: str,
    content_type: str,
    bloom_level: int,
    user_id: str = None,
) -> Dict:
    """
    Generate AI content (study guide, lab, quiz, etc.).
    
    This is a Celery task that runs async operations.
    """
    async def _generate():
        async with AsyncSessionLocal() as db:
            try:
                # Get concept and topic
                concept = await db.get(Concept, UUID(concept_id))
                topic = await db.get(Topic, UUID(topic_id))
                
                if not concept or not topic:
                    raise ValueError("Concept or topic not found")
                
                # Build prompt based on content type and Bloom level
                bloom_names = {
                    1: "Remember",
                    2: "Understand",
                    3: "Apply",
                    4: "Analyze",
                    5: "Evaluate",
                    6: "Create",
                }
                
                content_type_names = {
                    "study_guide": "study guide",
                    "lab": "hands-on lab exercise",
                    "quiz": "quiz with questions",
                    "video_script": "video script",
                    "summary": "summary",
                    "practice_exercise": "practice exercise",
                }
                
                # Search for relevant chunks using vector search
                concept_embedding = await embedding_service.generate_embeddings([concept.description or concept.name])
                search_results = await vector_db_service.search(
                    query_embedding=concept_embedding[0],
                    top_k=5,
                )
                
                # Build context from search results
                context = "\n\n".join([
                    f"Source: {result[2].get('source_id', 'unknown')}\n{result[2].get('text', '')}"
                    for result in search_results
                ])
                
                # Generate prompt
                prompt = f"""Create a {content_type_names.get(content_type, content_type)} for the concept "{concept.name}".

Concept Description: {concept.description or 'N/A'}
Topic: {topic.name}
Bloom's Taxonomy Level: {bloom_level} ({bloom_names.get(bloom_level, 'Unknown')})

Relevant Context:
{context}

Requirements:
- Target Bloom's level {bloom_level} ({bloom_names.get(bloom_level, 'Unknown')})
- Be clear, accurate, and pedagogically sound
- Include examples where appropriate
- Cite sources when using information from context

Generate the {content_type_names.get(content_type, content_type)} now:"""
                
                # Generate content using LLM
                generated_content = await llm_service.generate_text(
                    prompt=prompt,
                    temperature=0.7,
                    max_tokens=2000,
                )
                
                # Extract citations from search results
                citations = [
                    {
                        "chunk_id": str(result[0]),
                        "source_id": result[2].get("source_id"),
                        "similarity": float(result[1]),
                    }
                    for result in search_results
                ]
                
                # Create content item
                content_item = ContentItem(
                    topic_id=UUID(topic_id),
                    concept_id=UUID(concept_id),
                    content_type=ContentType(content_type),
                    title=f"{concept.name} - {content_type_names.get(content_type, content_type).title()}",
                    content=generated_content,
                    bloom_level=bloom_level,
                    difficulty=concept.difficulty,
                    citations=citations,
                    is_published=False,
                    version=1,
                )
                db.add(content_item)
                await db.commit()
                await db.refresh(content_item)
                
                logger.info(f"Content generated: {content_item.id} for concept {concept_id}")
                
                return {
                    "status": "completed",
                    "content_item_id": str(content_item.id),
                    "title": content_item.title,
                }
            
            except Exception as e:
                await db.rollback()
                logger.error(f"Content generation failed: {e}", exc_info=True)
                raise
    
    # Run async function in sync context
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(_generate())


@celery_app.task(name="revise_content", bind=True, max_retries=3)
def revise_content(
    self,
    content_item_id: str,
    shortcomings: List[Dict],
) -> Dict:
    """
    Revise content based on identified shortcomings.
    
    Triggered by Meta-Learning Engine.
    """
    async def _revise():
        async with AsyncSessionLocal() as db:
            try:
                # Get content item
                content_item = await db.get(ContentItem, UUID(content_item_id))
                if not content_item:
                    raise ValueError(f"Content item {content_item_id} not found")
                
                # Get parent version
                parent_version_id = content_item.id
                
                # Build revision prompt
                shortcomings_text = "\n".join([
                    f"- {s.get('type', 'Unknown')}: {s.get('description', '')}"
                    for s in shortcomings
                ])
                
                suggestions = "\n".join([
                    f"- {s.get('suggestion', '')}"
                    for s in shortcomings
                ])
                
                prompt = f"""Revise the following educational content based on identified shortcomings.

Original Content:
{content_item.content}

Identified Shortcomings:
{shortcomings_text}

Suggested Improvements:
{suggestions}

Please revise the content to address these issues while maintaining:
- Accuracy and correctness
- Pedagogical soundness
- Appropriate Bloom's Taxonomy level ({content_item.bloom_level})
- Clear explanations

Revised Content:"""
                
                # Generate revised content
                revised_content = await llm_service.generate_text(
                    prompt=prompt,
                    temperature=0.7,
                    max_tokens=2000,
                )
                
                # Create new version
                new_version = ContentItem(
                    topic_id=content_item.topic_id,
                    concept_id=content_item.concept_id,
                    content_type=content_item.content_type,
                    title=content_item.title,
                    content=revised_content,
                    bloom_level=content_item.bloom_level,
                    difficulty=content_item.difficulty,
                    citations=content_item.citations,
                    is_published=False,
                    version=content_item.version + 1,
                    parent_version_id=parent_version_id,
                )
                db.add(new_version)
                await db.commit()
                await db.refresh(new_version)
                
                logger.info(f"Content revised: {new_version.id} (version {new_version.version})")
                
                return {
                    "status": "completed",
                    "content_item_id": str(new_version.id),
                    "version": new_version.version,
                }
            
            except Exception as e:
                await db.rollback()
                logger.error(f"Content revision failed: {e}", exc_info=True)
                raise
    
    # Run async function in sync context
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(_revise())
