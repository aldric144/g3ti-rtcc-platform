"""
API Connections Admin API Router
Tab 11: API Connections
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException

from ...admin.api_connections_admin import api_connection_admin, APIConnectionModel, APIConnectionCreate, APIConnectionUpdate, APIStatus
from ...admin.validation import ValidationEngine
from ...admin.audit_log import audit_logger
from .base_router import CurrentUser, get_current_user, require_supervisor, require_admin, get_pagination, PaginationParams

router = APIRouter()


@router.get("/", response_model=List[APIConnectionModel])
async def list_api_connections(
    pagination: PaginationParams = Depends(get_pagination),
    status: Optional[APIStatus] = None,
    current_user: CurrentUser = Depends(require_supervisor()),
):
    """List all API connections"""
    filters = {"status": status} if status else None
    return await api_connection_admin.get_all(skip=pagination.skip, limit=pagination.limit, filters=filters)


@router.get("/active", response_model=List[APIConnectionModel])
async def get_active_connections(current_user: CurrentUser = Depends(require_supervisor())):
    """Get all active API connections"""
    return await api_connection_admin.get_active()


@router.get("/{connection_id}", response_model=APIConnectionModel)
async def get_api_connection(connection_id: str, current_user: CurrentUser = Depends(require_supervisor())):
    """Get a specific API connection"""
    connection = await api_connection_admin.get_by_id(connection_id)
    if not connection:
        raise HTTPException(status_code=404, detail="API connection not found")
    return connection


@router.get("/{connection_id}/key")
async def get_decrypted_key(connection_id: str, current_user: CurrentUser = Depends(require_admin())):
    """Get decrypted API key (admin only)"""
    key = await api_connection_admin.get_decrypted_key(connection_id, current_user.user_id)
    if key is None:
        raise HTTPException(status_code=404, detail="API connection not found")
    
    audit_logger.log(
        user_id=current_user.user_id,
        action=audit_logger._logs[0].action if audit_logger._logs else None,
        table_name="api_connections",
        record_id=connection_id,
        metadata={"action": "decrypt_key"},
        username=current_user.username,
    )
    return {"api_key": key}


@router.post("/", response_model=APIConnectionModel)
async def create_api_connection(data: APIConnectionCreate, current_user: CurrentUser = Depends(require_admin())):
    """Create a new API connection"""
    validation = ValidationEngine.validate_api_connection(data.model_dump())
    if not validation.is_valid:
        raise HTTPException(status_code=400, detail={"errors": validation.errors})
    
    connection = await api_connection_admin.create(data, current_user.user_id)
    audit_logger.log_create(user_id=current_user.user_id, table_name="api_connections", record_id=connection.id, data=connection)
    return connection


@router.patch("/{connection_id}", response_model=APIConnectionModel)
async def update_api_connection(connection_id: str, data: APIConnectionUpdate, current_user: CurrentUser = Depends(require_admin())):
    """Update an API connection"""
    existing = await api_connection_admin.get_by_id(connection_id)
    if not existing:
        raise HTTPException(status_code=404, detail="API connection not found")
    
    connection = await api_connection_admin.update(connection_id, data, current_user.user_id)
    audit_logger.log_update(user_id=current_user.user_id, table_name="api_connections", record_id=connection_id, before=existing, after=connection)
    return connection


@router.delete("/{connection_id}")
async def delete_api_connection(connection_id: str, current_user: CurrentUser = Depends(require_admin())):
    """Delete an API connection"""
    existing = await api_connection_admin.get_by_id(connection_id)
    if not existing:
        raise HTTPException(status_code=404, detail="API connection not found")
    
    await api_connection_admin.delete(connection_id, current_user.user_id)
    audit_logger.log_delete(user_id=current_user.user_id, table_name="api_connections", record_id=connection_id, data=existing)
    return {"message": "API connection deleted successfully"}


@router.post("/{connection_id}/test")
async def test_connection(connection_id: str, current_user: CurrentUser = Depends(require_supervisor())):
    """Test an API connection"""
    result = await api_connection_admin.test_connection(connection_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result
