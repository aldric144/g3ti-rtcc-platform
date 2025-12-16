"""
Schools Admin API Router
Tab 8: Schools
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException

from ...admin.schools_admin import school_admin, SchoolModel, SchoolCreate, SchoolUpdate, GradeLevel
from ...admin.validation import ValidationEngine
from ...admin.audit_log import audit_logger
from .base_router import CurrentUser, get_current_user, require_supervisor, get_pagination, PaginationParams

router = APIRouter()


@router.get("/", response_model=List[SchoolModel])
async def list_schools(
    pagination: PaginationParams = Depends(get_pagination),
    grade_level: Optional[GradeLevel] = None,
    current_user: CurrentUser = Depends(get_current_user),
):
    """List all schools"""
    filters = {"grade_level": grade_level} if grade_level else None
    return await school_admin.get_all(skip=pagination.skip, limit=pagination.limit, filters=filters)


@router.get("/with-sro", response_model=List[SchoolModel])
async def get_schools_with_sro(current_user: CurrentUser = Depends(get_current_user)):
    """Get schools with assigned SRO"""
    return await school_admin.get_schools_with_sro()


@router.get("/grade/{grade_level}", response_model=List[SchoolModel])
async def get_by_grade_level(grade_level: GradeLevel, current_user: CurrentUser = Depends(get_current_user)):
    """Get schools by grade level"""
    return await school_admin.get_by_grade_level(grade_level)


@router.get("/{school_id}", response_model=SchoolModel)
async def get_school(school_id: str, current_user: CurrentUser = Depends(get_current_user)):
    """Get a specific school"""
    school = await school_admin.get_by_id(school_id)
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    return school


@router.post("/", response_model=SchoolModel)
async def create_school(data: SchoolCreate, current_user: CurrentUser = Depends(require_supervisor())):
    """Create a new school"""
    validation = ValidationEngine.validate_school(data.model_dump())
    if not validation.is_valid:
        raise HTTPException(status_code=400, detail={"errors": validation.errors})
    
    school = await school_admin.create(data, current_user.user_id)
    audit_logger.log_create(user_id=current_user.user_id, table_name="schools", record_id=school.id, data=school)
    return school


@router.patch("/{school_id}", response_model=SchoolModel)
async def update_school(school_id: str, data: SchoolUpdate, current_user: CurrentUser = Depends(require_supervisor())):
    """Update a school"""
    existing = await school_admin.get_by_id(school_id)
    if not existing:
        raise HTTPException(status_code=404, detail="School not found")
    
    school = await school_admin.update(school_id, data, current_user.user_id)
    audit_logger.log_update(user_id=current_user.user_id, table_name="schools", record_id=school_id, before=existing, after=school)
    return school


@router.delete("/{school_id}")
async def delete_school(school_id: str, current_user: CurrentUser = Depends(require_supervisor())):
    """Delete a school"""
    existing = await school_admin.get_by_id(school_id)
    if not existing:
        raise HTTPException(status_code=404, detail="School not found")
    
    await school_admin.delete(school_id, current_user.user_id)
    audit_logger.log_delete(user_id=current_user.user_id, table_name="schools", record_id=school_id, data=existing)
    return {"message": "School deleted successfully"}
