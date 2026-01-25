"""Lab Orchestrator: Manages lab environments (Docker support removed for local execution)."""
from typing import Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.performance import LabSession, LabStatus
from app.core.config import settings
from app.core.logging_config import logger


class LabOrchestrator:
    """Orchestrates lab environments for hands-on exercises.
    
    Note: Docker support has been removed for local execution.
    Lab functionality is disabled and will return appropriate error messages.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.docker_client = None  # Docker removed for local execution
        logger.warning("Lab Orchestrator initialized without Docker support. Lab features are disabled.")
    
    async def provision_lab(
        self,
        user_id: str,
        content_item_id: str,
        docker_image: str,
        port_mappings: Dict[str, str],
        environment_variables: Dict[str, str],
    ) -> LabSession:
        """
        Provision a new lab environment.
        
        Returns LabSession with container_id and status.
        """
        from uuid import UUID
        
        # Create lab session record
        lab_session = LabSession(
            user_id=UUID(user_id),
            content_item_id=UUID(content_item_id),
            docker_image=docker_image,
            port_mappings=port_mappings,
            environment_variables=environment_variables,
            status=LabStatus.PENDING,
            timeout_at=datetime.utcnow() + timedelta(seconds=settings.LAB_TIMEOUT_SECONDS),
        )
        self.db.add(lab_session)
        await self.db.commit()
        await self.db.refresh(lab_session)
        
        if not self.docker_client:
            lab_session.status = LabStatus.FAILED
            lab_session.error_message = "Lab features are disabled. Docker support has been removed for local execution."
            await self.db.commit()
            logger.warning(f"Lab provisioning attempted but Docker is not available. Lab session {lab_session.id} marked as failed.")
            return lab_session
        
        try:
            # Start container
            lab_session.status = LabStatus.PROVISIONING
            await self.db.commit()
            
            container = self.docker_client.containers.run(
                image=docker_image,
                detach=True,
                ports=port_mappings,
                environment=environment_variables,
                network=settings.DOCKER_NETWORK,
                remove=False,  # Keep container for inspection
            )
            
            lab_session.docker_container_id = container.id
            lab_session.status = LabStatus.RUNNING
            lab_session.started_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(lab_session)
            
        except Exception as e:
            lab_session.status = LabStatus.FAILED
            lab_session.error_message = str(e)
            await self.db.commit()
        
        return lab_session
    
    async def grade_lab(
        self,
        lab_session_id: str,
        rubric_id: str,
    ) -> Dict:
        """
        Grade a lab session against a grading rubric.
        
        Validates:
        - File existence
        - Port listening
        - Command outputs
        - Service states
        """
        from app.models.performance import GradingRubric
        from uuid import UUID
        
        # Get lab session
        stmt = select(LabSession).where(LabSession.id == UUID(lab_session_id))
        result = await self.db.execute(stmt)
        lab_session = result.scalar_one_or_none()
        
        if not lab_session or not lab_session.docker_container_id:
            return {"error": "Lab session not found or not running"}
        
        # Get rubric
        rubric_stmt = select(GradingRubric).where(GradingRubric.id == UUID(rubric_id))
        rubric_result = await self.db.execute(rubric_stmt)
        rubric = rubric_result.scalar_one_or_none()
        
        if not rubric:
            return {"error": "Grading rubric not found"}
        
        if not self.docker_client:
            return {"error": "Docker client not available"}
        
        try:
            container = self.docker_client.containers.get(lab_session.docker_container_id)
        except Exception as e:
            return {"error": f"Container not found: {e}"}
        
        # Evaluate each criterion
        results = []
        total_score = 0.0
        
        for criterion in rubric.criteria:
            criterion_type = criterion.get("type")
            weight = criterion.get("weight", 0.0)
            score = 0.0
            passed = False
            
            if criterion_type == "file_exists":
                path = criterion.get("path")
                exit_code, output = container.exec_run(f"test -f {path}")
                passed = exit_code == 0
                score = weight if passed else 0.0
            
            elif criterion_type == "port_listening":
                port = criterion.get("port")
                exit_code, output = container.exec_run(f"netstat -tuln | grep :{port}")
                passed = exit_code == 0
                score = weight if passed else 0.0
            
            elif criterion_type == "command_output":
                command = criterion.get("command")
                expected = criterion.get("expected", "")
                exit_code, output = container.exec_run(command)
                output_str = output.decode("utf-8") if output else ""
                passed = expected.lower() in output_str.lower()
                score = weight if passed else 0.0
            
            elif criterion_type == "service_running":
                service = criterion.get("service")
                exit_code, output = container.exec_run(f"systemctl is-active {service}")
                passed = exit_code == 0
                score = weight if passed else 0.0
            
            results.append({
                "criterion": criterion.get("description", ""),
                "type": criterion_type,
                "weight": weight,
                "score": score,
                "passed": passed,
            })
            total_score += score
        
        # Determine if passed
        passed = total_score >= rubric.passing_threshold
        
        return {
            "lab_session_id": str(lab_session.id),
            "total_score": total_score,
            "max_score": rubric.total_weight,
            "percentage": (total_score / rubric.total_weight * 100) if rubric.total_weight > 0 else 0,
            "passed": passed,
            "passing_threshold": rubric.passing_threshold,
            "criteria_results": results,
        }
    
    async def terminate_lab(self, lab_session_id: str) -> bool:
        """Terminate a lab session and clean up container."""
        from uuid import UUID
        
        stmt = select(LabSession).where(LabSession.id == UUID(lab_session_id))
        result = await self.db.execute(stmt)
        lab_session = result.scalar_one_or_none()
        
        if not lab_session:
            return False
        
        if lab_session.docker_container_id and self.docker_client:
            try:
                container = self.docker_client.containers.get(lab_session.docker_container_id)
                container.stop()
                container.remove()
            except Exception:
                pass
        
        lab_session.status = LabStatus.TERMINATED
        lab_session.completed_at = datetime.utcnow()
        await self.db.commit()
        
        return True
