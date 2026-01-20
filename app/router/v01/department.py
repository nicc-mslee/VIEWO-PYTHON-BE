"""부서 관리 라우터"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.crud.department import (
    get_all_departments,
    get_department_by_id,
    create_department,
    update_department,
    delete_department,
    search_departments
)
from app.models.department import Department, DepartmentCreate, DepartmentUpdate

router = APIRouter(prefix="/department", tags=["Department Management"])

@router.get("/")
async def get_departments(
    search: Optional[str] = Query(None, description="검색어")
):
    """모든 부서 목록 조회 (검색 옵션 지원)"""
    try:
        if search:
            departments = search_departments(search)
        else:
            departments = get_all_departments()
        return {"code": 200, "data": departments}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"부서 목록 조회 실패: {str(e)}")

@router.get("/{department_id}")
async def get_department(department_id: int):
    """특정 부서 조회"""
    try:
        department = get_department_by_id(department_id)
        if department is None:
            raise HTTPException(status_code=404, detail="부서를 찾을 수 없습니다")
        return {"code": 200, "data": department}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"부서 조회 실패: {str(e)}")

@router.post("/")
async def create_department_endpoint(department: DepartmentCreate):
    """새 부서 생성"""
    try:
        department_data = department.dict(exclude_none=True)
        created = create_department(department_data)
        if not created:
             raise HTTPException(status_code=500, detail="부서 생성 실패")
        return {"code": 200, "data": created}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"부서 생성 실패: {str(e)}")

@router.patch("/{department_id}")
async def update_department_endpoint(department_id: int, department: DepartmentUpdate):
    """부서 업데이트"""
    try:
        department_data = department.dict(exclude_none=True)
        updated = update_department(department_id, department_data)
        if updated is None:
            raise HTTPException(status_code=404, detail="부서를 찾을 수 없습니다")
        return {"code": 200, "data": updated}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"부서 업데이트 실패: {str(e)}")

@router.delete("/{department_id}")
async def delete_department_endpoint(department_id: int):
    """부서 삭제"""
    try:
        success = delete_department(department_id)
        if not success:
            raise HTTPException(status_code=404, detail="부서를 찾을 수 없습니다")
        return {"code": 200, "message": "부서가 삭제되었습니다"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"부서 삭제 실패: {str(e)}")
