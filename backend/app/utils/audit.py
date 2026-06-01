import uuid

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def record_audit(
    db: Session,
    *,
    user_id: uuid.UUID | None,
    action: str,
    entity_type: str,
    entity_id,
    detail: str | None = None,
) -> None:
    """Append an audit-log entry. Does not commit (caller owns the transaction)."""
    db.add(
        AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=str(entity_id),
            detail=detail,
        )
    )
