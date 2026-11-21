import json
from datetime import datetime
from sqlalchemy.orm import Session

def log_audit_event(
    db: Session,
    user_id: str,
    action: str,
    entity_type: str,
    entity_id: str = None,
    details: dict = None
):
    """Record an audit trail event in the database."""
    from backend.app.db.models import AuditLog
    
    details_str = json.dumps(details or {}, default=str)
    log_entry = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id else None,
        details=details_str,
        timestamp=datetime.utcnow()
    )
    db.add(log_entry)
    try:
        db.commit()
    except Exception:
        db.rollback()
