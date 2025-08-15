from typing import List, Optional
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.contact import Contact
from app.models.contact_relationship import ContactRelationship
from app.schemas.family_information import (
    FamilyMemberInfo, BirthdayReminder, EmergencyContact, 
    FamilyTreeNode, FamilySummary, FamilyInformationFilter
)


class FamilyInformationService:
    """Service for managing family information tracking"""
    
    def __init__(self, db: Session):
        self.db = db

    def get_family_members(
        self, 
        user_id: int, 
        tenant_id: int, 
        include_extended: bool = True
    ) -> List[FamilyMemberInfo]:
        """Get all family members with relationship information"""
        
        # Base query for family relationships
        family_relationships_query = self.db.query(ContactRelationship).filter(
            and_(
                ContactRelationship.tenant_id == tenant_id,
                ContactRelationship.relationship_category == 'family',
                ContactRelationship.is_active == True,
                or_(
                    ContactRelationship.contact_a_id.in_(
                        self.db.query(Contact.id).filter(
                            and_(
                                Contact.tenant_id == tenant_id,
                                Contact.created_by_user_id == user_id
                            )
                        )
                    ),
                    ContactRelationship.contact_b_id.in_(
                        self.db.query(Contact.id).filter(
                            and_(
                                Contact.tenant_id == tenant_id,
                                Contact.created_by_user_id == user_id
                            )
                        )
                    )
                )
            )
        )
        
        if not include_extended:
            # Only immediate family (parent, child, sibling, spouse)
            immediate_family_types = ['parent', 'child', 'sibling', 'brother', 'sister', 'spouse', 'partner']
            family_relationships_query = family_relationships_query.filter(
                ContactRelationship.relationship_type.in_(immediate_family_types)
            )
        
        family_relationships = family_relationships_query.all()
        
        # Collect all family contact IDs
        family_contact_ids = set()
        for rel in family_relationships:
            family_contact_ids.add(rel.contact_a_id)
            family_contact_ids.add(rel.contact_b_id)
        
        # Get all family contacts
        family_contacts = self.db.query(Contact).filter(
            and_(
                Contact.id.in_(family_contact_ids),
                Contact.tenant_id == tenant_id,
                Contact.is_active == True
            )
        ).all()
        
        # Build family member info list
        family_members = []
        for contact in family_contacts:
            # Find the relationship for this contact
            relationship = None
            for rel in family_relationships:
                if rel.contact_a_id == contact.id or rel.contact_b_id == contact.id:
                    relationship = rel
                    break
            
            # Calculate age if birth date is available
            age = None
            days_until_birthday = None
            if contact.date_of_birth:
                today = date.today()
                age = today.year - contact.date_of_birth.year
                if today.month < contact.date_of_birth.month or \
                   (today.month == contact.date_of_birth.month and today.day < contact.date_of_birth.day):
                    age -= 1
                
                # Calculate days until next birthday
                next_birthday = contact.date_of_birth.replace(year=today.year)
                if next_birthday < today:
                    next_birthday = next_birthday.replace(year=today.year + 1)
                days_until_birthday = (next_birthday - today).days
            
            family_member = FamilyMemberInfo(
                contact=contact,
                relationship_type=relationship.relationship_type if relationship else None,
                relationship_category=relationship.relationship_category if relationship else None,
                age=age,
                days_until_birthday=days_until_birthday
            )
            family_members.append(family_member)
        
        return family_members

    def get_upcoming_birthdays(
        self, 
        user_id: int, 
        tenant_id: int, 
        days_ahead: int = 30
    ) -> List[BirthdayReminder]:
        """Get upcoming birthdays within the specified number of days"""
        
        # Get all contacts with birthdays
        contacts_with_birthdays = self.db.query(Contact).filter(
            and_(
                Contact.tenant_id == tenant_id,
                Contact.created_by_user_id == user_id,
                Contact.date_of_birth.isnot(None),
                Contact.is_active == True
            )
        ).all()
        
        upcoming_birthdays = []
        today = date.today()
        
        for contact in contacts_with_birthdays:
            if contact.date_of_birth:
                # Calculate next birthday
                next_birthday = contact.date_of_birth.replace(year=today.year)
                if next_birthday < today:
                    next_birthday = next_birthday.replace(year=today.year + 1)
                
                days_until = (next_birthday - today).days
                
                if days_until <= days_ahead:
                    # Calculate age turning
                    age_turning = next_birthday.year - contact.date_of_birth.year
                    
                    birthday_reminder = BirthdayReminder(
                        contact_id=contact.id,
                        contact_name=f"{contact.first_name} {contact.last_name or ''}".strip(),
                        family_nickname=contact.family_nickname,
                        event_type='birthday',
                        event_date=contact.date_of_birth,
                        days_until=days_until,
                        age_turning=age_turning
                    )
                    upcoming_birthdays.append(birthday_reminder)
        
        # Sort by days until birthday
        upcoming_birthdays.sort(key=lambda x: x.days_until)
        return upcoming_birthdays

    def get_upcoming_anniversaries(
        self, 
        user_id: int, 
        tenant_id: int, 
        days_ahead: int = 30
    ) -> List[BirthdayReminder]:
        """Get upcoming anniversaries within the specified number of days"""
        
        # Get all contacts with anniversary dates
        contacts_with_anniversaries = self.db.query(Contact).filter(
            and_(
                Contact.tenant_id == tenant_id,
                Contact.created_by_user_id == user_id,
                Contact.anniversary_date.isnot(None),
                Contact.is_active == True
            )
        ).all()
        
        upcoming_anniversaries = []
        today = date.today()
        
        for contact in contacts_with_anniversaries:
            if contact.anniversary_date:
                # Calculate next anniversary
                next_anniversary = contact.anniversary_date.replace(year=today.year)
                if next_anniversary < today:
                    next_anniversary = next_anniversary.replace(year=today.year + 1)
                
                days_until = (next_anniversary - today).days
                
                if days_until <= days_ahead:
                    anniversary_reminder = BirthdayReminder(
                        contact_id=contact.id,
                        contact_name=f"{contact.first_name} {contact.last_name or ''}".strip(),
                        family_nickname=contact.family_nickname,
                        event_type='anniversary',
                        event_date=contact.anniversary_date,
                        days_until=days_until,
                        age_turning=None  # Not applicable for anniversaries
                    )
                    upcoming_anniversaries.append(anniversary_reminder)
        
        # Sort by days until anniversary
        upcoming_anniversaries.sort(key=lambda x: x.days_until)
        return upcoming_anniversaries

    def get_emergency_contacts(
        self, 
        user_id: int, 
        tenant_id: int
    ) -> List[EmergencyContact]:
        """Get all contacts marked as emergency contacts"""
        
        emergency_contacts = self.db.query(Contact).filter(
            and_(
                Contact.tenant_id == tenant_id,
                Contact.created_by_user_id == user_id,
                Contact.is_emergency_contact == True,
                Contact.is_active == True
            )
        ).all()
        
        result = []
        for contact in emergency_contacts:
            # Try to find relationship type if it exists
            relationship = self.db.query(ContactRelationship).filter(
                and_(
                    ContactRelationship.tenant_id == tenant_id,
                    or_(
                        ContactRelationship.contact_a_id == contact.id,
                        ContactRelationship.contact_b_id == contact.id
                    ),
                    ContactRelationship.is_active == True
                )
            ).first()
            
            emergency_contact = EmergencyContact(
                contact=contact,
                relationship_type=relationship.relationship_type if relationship else None,
                primary_phone=contact.phone,
                alternative_contact=contact.email
            )
            result.append(emergency_contact)
        
        return result

    def get_family_summary(
        self, 
        user_id: int, 
        tenant_id: int, 
        filter_params: Optional[FamilyInformationFilter] = None
    ) -> FamilySummary:
        """Get comprehensive family information summary"""
        
        if not filter_params:
            filter_params = FamilyInformationFilter()
        
        family_members = self.get_family_members(
            user_id, 
            tenant_id, 
            include_extended=filter_params.include_extended_family
        )
        
        upcoming_birthdays = self.get_upcoming_birthdays(
            user_id, 
            tenant_id, 
            days_ahead=filter_params.days_ahead_for_reminders
        )
        
        upcoming_anniversaries = self.get_upcoming_anniversaries(
            user_id, 
            tenant_id, 
            days_ahead=filter_params.days_ahead_for_reminders
        )
        
        emergency_contacts = self.get_emergency_contacts(user_id, tenant_id)
        
        # Build a simple family tree (could be enhanced further)
        family_tree = self._build_family_tree(family_members, filter_params.generation_depth)
        
        return FamilySummary(
            total_family_members=len(family_members),
            family_tree=family_tree,
            upcoming_birthdays=upcoming_birthdays,
            upcoming_anniversaries=upcoming_anniversaries,
            emergency_contacts=emergency_contacts
        )

    def _build_family_tree(
        self, 
        family_members: List[FamilyMemberInfo], 
        depth: int
    ) -> List[FamilyTreeNode]:
        """Build a basic family tree structure"""
        
        tree_nodes = []
        
        # Group by relationship types to determine generation
        generation_map = {
            'grandparent': -2,
            'parent': -1,
            'sibling': 0,
            'brother': 0,
            'sister': 0,
            'spouse': 0,
            'partner': 0,
            'child': 1,
            'grandchild': 2,
            'uncle': -1,
            'aunt': -1,
            'nephew': 1,
            'niece': 1,
            'cousin': 0
        }
        
        for family_member in family_members:
            generation = generation_map.get(family_member.relationship_type, 0)
            
            if abs(generation) <= depth:
                node = FamilyTreeNode(
                    contact_id=family_member.contact.id,
                    contact_name=f"{family_member.contact.first_name} {family_member.contact.last_name or ''}".strip(),
                    family_nickname=family_member.contact.family_nickname,
                    relationship_to_user=family_member.relationship_type,
                    generation=generation,
                    children=[]  # Simplified - not building actual parent-child hierarchy
                )
                tree_nodes.append(node)
        
        # Sort by generation for display
        tree_nodes.sort(key=lambda x: x.generation)
        return tree_nodes