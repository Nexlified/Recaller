from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.organization import Organization
from app.models.social_group import SocialGroup
from app.schemas.organization import OrganizationCreate, OrganizationUpdate, SocialGroupCreate, SocialGroupUpdate

class CRUDOrganization(CRUDBase[Organization, OrganizationCreate, OrganizationUpdate]):
    def get_by_name(self, db: Session, *, name: str, tenant_id: int) -> Optional[Organization]:
        return db.query(Organization).filter(
            Organization.name == name,
            Organization.tenant_id == tenant_id
        ).first()

    def get_multi_by_tenant(
        self, db: Session, *, tenant_id: int, skip: int = 0, limit: int = 100
    ) -> List[Organization]:
        return db.query(Organization).filter(
            Organization.tenant_id == tenant_id
        ).offset(skip).limit(limit).all()

    def create_with_tenant(
        self, db: Session, *, obj_in: OrganizationCreate, tenant_id: int
    ) -> Organization:
        obj_in_data = obj_in.dict()
        db_obj = Organization(**obj_in_data, tenant_id=tenant_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

class CRUDSocialGroup(CRUDBase[SocialGroup, SocialGroupCreate, SocialGroupUpdate]):
    def get_by_name(self, db: Session, *, name: str, tenant_id: int) -> Optional[SocialGroup]:
        return db.query(SocialGroup).filter(
            SocialGroup.name == name,
            SocialGroup.tenant_id == tenant_id
        ).first()

    def get_multi_by_tenant(
        self, db: Session, *, tenant_id: int, skip: int = 0, limit: int = 100
    ) -> List[SocialGroup]:
        return db.query(SocialGroup).filter(
            SocialGroup.tenant_id == tenant_id
        ).offset(skip).limit(limit).all()

    def create_with_tenant(
        self, db: Session, *, obj_in: SocialGroupCreate, tenant_id: int
    ) -> SocialGroup:
        obj_in_data = obj_in.dict()
        db_obj = SocialGroup(**obj_in_data, tenant_id=tenant_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

organization = CRUDOrganization(Organization)
social_group = CRUDSocialGroup(SocialGroup)