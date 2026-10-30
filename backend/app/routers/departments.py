from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Department
from app.schemas import DepartmentResponse

router = APIRouter(prefix="/api/departments", tags=["departments"])


@router.get("", response_model=list[DepartmentResponse])
def list_departments(db: Session = Depends(get_db)) -> list[Department]:
    return list(db.scalars(select(Department).order_by(Department.created_at, Department.id)))
