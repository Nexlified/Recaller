from typing import List, Optional
from pydantic import BaseModel
from datetime import date
from app.schemas.contact import Contact


class FamilyMemberInfo(BaseModel):
    """Enhanced contact information with family-specific details"""
    contact: Contact
    relationship_type: Optional[str] = None
    relationship_category: Optional[str] = None
    age: Optional[int] = None  # Calculated from date_of_birth
    days_until_birthday: Optional[int] = None  # Days until next birthday


class BirthdayReminder(BaseModel):
    """Birthday and anniversary reminder information"""
    contact_id: int
    contact_name: str
    family_nickname: Optional[str] = None
    event_type: str  # 'birthday' or 'anniversary'
    event_date: date
    days_until: int
    age_turning: Optional[int] = None  # For birthdays only


class EmergencyContact(BaseModel):
    """Emergency contact information"""
    contact: Contact
    relationship_type: Optional[str] = None
    primary_phone: Optional[str] = None
    alternative_contact: Optional[str] = None


class FamilyTreeNode(BaseModel):
    """Family tree structure node"""
    contact_id: int
    contact_name: str
    family_nickname: Optional[str] = None
    relationship_to_user: Optional[str] = None
    generation: int  # Relative generation (0 = user, 1 = children/siblings, -1 = parents, etc.)
    children: List['FamilyTreeNode'] = []


class FamilySummary(BaseModel):
    """Family information summary"""
    total_family_members: int
    family_tree: List[FamilyTreeNode]
    upcoming_birthdays: List[BirthdayReminder]
    upcoming_anniversaries: List[BirthdayReminder]
    emergency_contacts: List[EmergencyContact]


class FamilyInformationFilter(BaseModel):
    """Filter parameters for family information queries"""
    include_extended_family: bool = True
    include_in_laws: bool = True
    days_ahead_for_reminders: int = 30
    generation_depth: int = 3  # How many generations up/down to include in tree


# Update forward references
FamilyTreeNode.model_rebuild()