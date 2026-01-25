"""Document ingestion and processing tasks."""
import asyncio
from uuid import UUID
from app.tasks.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.core.logging_config import logger
from app.models.sources import Document, DocumentStatus, Chunk, Source
from app.services.document_processor import document_processor
from app.services.embedding_service import embedding_service
from app.services.vector_db_service import vector_db_service
from sqlalchemy import select
from typing import Dict


@celery_app.task(name="process_document", bind=True, max_retries=3)
def process_document(self, document_id: str) -> Dict:
    """
    Process uploaded document: extract text, chunk, generate embeddings.
    
    This is a Celery task that runs async operations.
    """
    async def _process():
        async with AsyncSessionLocal() as db:
            try:
                # Get document
                stmt = select(Document).where(Document.id == UUID(document_id))
                result = await db.execute(stmt)
                document = result.scalar_one_or_none()
                
                if not document:
                    raise ValueError(f"Document {document_id} not found")
                
                # Update status
                document.status = DocumentStatus.PROCESSING
                await db.commit()
                
                # Extract text based on source type
                text = ""
                source = await db.get(Source, document.source_id)
                
                if source.source_type.value == "pdf":
                    text = await document_processor.extract_text_from_pdf(document.file_path)
                elif source.source_type.value == "url":
                    text = await document_processor.extract_text_from_url(source.url)
                elif source.source_type.value in ["book", "paper", "manual"]:
                    if document.file_path:
                        if document.file_path.endswith(".pdf"):
                            text = await document_processor.extract_text_from_pdf(document.file_path)
                        elif document.file_path.endswith(".docx"):
                            text = await document_processor.extract_text_from_docx(document.file_path)
                
                if not text:
                    raise ValueError("No text extracted from document")
                
                # Chunk text
                chunks_data = document_processor.chunk_text(text)
                
                # Generate embeddings
                chunk_texts = [chunk["content"] for chunk in chunks_data]
                embeddings = await embedding_service.generate_embeddings(chunk_texts)
                
                # Create chunk records and store in vector DB
                chunk_ids = []
                vector_db_ids = []
                vector_db_embeddings = []
                vector_db_documents = []
                vector_db_metadatas = []
                
                for idx, (chunk_data, embedding) in enumerate(zip(chunks_data, embeddings)):
                    chunk_id = UUID()
                    chunk_ids.append(str(chunk_id))
                    
                    # Create chunk record
                    chunk = Chunk(
                        id=chunk_id,
                        document_id=document.id,
                        content=chunk_data["content"],
                        chunk_index=idx,
                        start_char=chunk_data["start_char"],
                        end_char=chunk_data["end_char"],
                        embedding=embedding,
                        citation={
                            "source_id": str(source.id),
                            "document_id": str(document.id),
                            "chunk_index": idx,
                        },
                    )
                    db.add(chunk)
                    
                    # Prepare for vector DB
                    vector_db_ids.append(str(chunk_id))
                    vector_db_embeddings.append(embedding)
                    vector_db_documents.append(chunk_data["content"])
                    vector_db_metadatas.append({
                        "document_id": str(document.id),
                        "source_id": str(source.id),
                        "chunk_index": idx,
                    })
                
                # Store in vector DB
                await vector_db_service.add_documents(
                    ids=vector_db_ids,
                    embeddings=vector_db_embeddings,
                    documents=vector_db_documents,
                    metadatas=vector_db_metadatas,
                )
                
                # Update document status
                document.status = DocumentStatus.COMPLETED
                document.meta_data = {
                    "chunk_count": len(chunks_data),
                    "total_chars": len(text),
                }
                await db.commit()
                
                logger.info(f"Document {document_id} processed successfully: {len(chunks_data)} chunks")
                
                return {
                    "status": "completed",
                    "document_id": document_id,
                    "chunks_created": len(chunks_data),
                }
            
            except Exception as e:
                await db.rollback()
                logger.error(f"Document processing failed: {e}", exc_info=True)
                
                # Update document status
                stmt = select(Document).where(Document.id == UUID(document_id))
                result = await db.execute(stmt)
                document = result.scalar_one_or_none()
                if document:
                    document.status = DocumentStatus.FAILED
                    document.processing_error = str(e)
                    await db.commit()
                
                raise
    
    # Run async function in sync context
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(_process())
