# Import all models to ensure they are registered with SQLAlchemy
from .tenant import Tenant
from .user import User

# New person-based models
from .person import (
    PersonProfile, PersonContactInfo, PersonProfessionalInfo, PersonPersonalInfo, 
    PersonLifeEvent, PersonBelonging, PersonVisibility, ContactInfoType, 
    ContactInfoPrivacy, LifeEventType, BelongingType
)
from .person_relationship import PersonRelationship, RelationshipType, RelationshipStatus

# Legacy contact models (to be removed after migration)
from .contact import Contact, ContactInteraction
from .contact_work_experience import ContactWorkExperience
from .organization import Organization, OrganizationAlias, OrganizationLocation
from .social_group import SocialGroup, SocialGroupActivity, SocialGroupActivityAttendance, ContactSocialGroupMembership
from .analytics import (
    NetworkingInsight, 
    DailyNetworkMetric, 
    ContactAnalyticsSummary, 
    InteractionAnalytics, 
    OrganizationNetworkAnalytics, 
    SocialGroupAnalytics
)
from .event import Event, ContactEventAttendance, EventTag, EventFollowUp
from .task import Task, TaskContact, TaskRecurrence, TaskCategory, TaskCategoryAssignment
from .financial_account import FinancialAccount
from .transaction_category import TransactionCategory
from .transaction_subcategory import TransactionSubcategory
from .recurring_transaction import RecurringTransaction
from .transaction import Transaction
from .budget import Budget
from .journal import JournalEntry, JournalTag, JournalAttachment
from .personal_debt import PersonalDebt, DebtPayment
from .personal_reminder import PersonalReminder
from .gift import Gift, GiftIdea

__all__ = [
    "Tenant",
    "User", 
    # New person models
    "PersonProfile", "PersonContactInfo", "PersonProfessionalInfo", "PersonPersonalInfo", 
    "PersonLifeEvent", "PersonBelonging", "PersonVisibility", "ContactInfoType", 
    "ContactInfoPrivacy", "LifeEventType", "BelongingType",
    "PersonRelationship", "RelationshipType", "RelationshipStatus",
    # Legacy contact models
    "Contact",
    "ContactInteraction",
    "ContactWorkExperience",
    "Organization",
    "OrganizationAlias", 
    "OrganizationLocation",
    "SocialGroup",
    "SocialGroupActivity",
    "SocialGroupActivityAttendance", 
    "ContactSocialGroupMembership",
    "NetworkingInsight",
    "DailyNetworkMetric",
    "ContactAnalyticsSummary",
    "InteractionAnalytics",
    "OrganizationNetworkAnalytics",
    "SocialGroupAnalytics",
    "Event",
    "ContactEventAttendance",
    "EventTag", 
    "EventFollowUp",
    "Task",
    "TaskContact",
    "TaskRecurrence",
    "TaskCategory",
    "TaskCategoryAssignment",
    "FinancialAccount",
    "TransactionCategory",
    "TransactionSubcategory", 
    "RecurringTransaction",
    "Transaction",
    "Budget",
    "JournalEntry",
    "JournalTag",
    "JournalAttachment",
    "PersonalDebt",
    "DebtPayment",
    "PersonalReminder",
    "Gift",
    "GiftIdea"
]
