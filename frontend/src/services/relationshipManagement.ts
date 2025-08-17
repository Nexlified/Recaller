import api from './api';
import {
  PersonProfile,
  PersonProfileCreate,
  PersonProfileUpdate,
  PersonProfileSummary,
  PersonContactInfo,
  PersonContactInfoCreate,
  PersonContactInfoUpdate,
  PersonProfessionalInfo,
  PersonProfessionalInfoCreate,
  PersonProfessionalInfoUpdate,
  PersonPersonalInfo,
  PersonPersonalInfoCreate,
  PersonPersonalInfoUpdate,
  PersonLifeEvent,
  PersonLifeEventCreate,
  PersonLifeEventUpdate,
  PersonBelonging,
  PersonBelongingCreate,
  PersonBelongingUpdate,
  PersonRelationship,
  PersonRelationshipCreate,
  PersonRelationshipUpdate,
  ApiResponse,
  PaginatedResponse
} from '../types/PersonProfile';

class RelationshipManagementService {
  private basePath = '/relationship-management';

  // Person Profile Operations
  async getPersonProfiles(skip: number = 0, limit: number = 100): Promise<PersonProfileSummary[]> {
    const response = await api.get(`${this.basePath}/profiles/`, {
      params: { skip, limit }
    });
    return response.data;
  }

  async searchPersonProfiles(query: string, skip: number = 0, limit: number = 100): Promise<PersonProfileSummary[]> {
    const response = await api.get(`${this.basePath}/profiles/search/`, {
      params: { q: query, skip, limit }
    });
    return response.data;
  }

  async getPersonProfile(profileId: number): Promise<PersonProfile> {
    const response = await api.get(`${this.basePath}/profiles/${profileId}`);
    return response.data;
  }

  async createPersonProfile(profileData: PersonProfileCreate): Promise<PersonProfile> {
    const response = await api.post(`${this.basePath}/profiles/`, profileData);
    return response.data;
  }

  async updatePersonProfile(profileId: number, profileData: PersonProfileUpdate): Promise<PersonProfile> {
    const response = await api.put(`${this.basePath}/profiles/${profileId}`, profileData);
    return response.data;
  }

  async deletePersonProfile(profileId: number): Promise<void> {
    await api.delete(`${this.basePath}/profiles/${profileId}`);
  }

  // Contact Information Operations
  async getPersonContactInfo(profileId: number): Promise<PersonContactInfo[]> {
    const response = await api.get(`${this.basePath}/profiles/${profileId}/contact-info/`);
    return response.data;
  }

  async createPersonContactInfo(profileId: number, contactInfoData: Omit<PersonContactInfoCreate, 'person_id'>): Promise<PersonContactInfo> {
    const dataWithPersonId = { ...contactInfoData, person_id: profileId };
    const response = await api.post(`${this.basePath}/profiles/${profileId}/contact-info/`, dataWithPersonId);
    return response.data;
  }

  async updatePersonContactInfo(profileId: number, contactInfoId: number, contactInfoData: PersonContactInfoUpdate): Promise<PersonContactInfo> {
    const response = await api.put(`${this.basePath}/profiles/${profileId}/contact-info/${contactInfoId}`, contactInfoData);
    return response.data;
  }

  // Professional Information Operations
  async getPersonProfessionalInfo(profileId: number): Promise<PersonProfessionalInfo[]> {
    const response = await api.get(`${this.basePath}/profiles/${profileId}/professional-info/`);
    return response.data;
  }

  async createPersonProfessionalInfo(profileId: number, professionalInfoData: Omit<PersonProfessionalInfoCreate, 'person_id'>): Promise<PersonProfessionalInfo> {
    const dataWithPersonId = { ...professionalInfoData, person_id: profileId };
    const response = await api.post(`${this.basePath}/profiles/${profileId}/professional-info/`, dataWithPersonId);
    return response.data;
  }

  // Personal Information Operations
  async getPersonPersonalInfo(profileId: number): Promise<PersonPersonalInfo[]> {
    const response = await api.get(`${this.basePath}/profiles/${profileId}/personal-info/`);
    return response.data;
  }

  async createPersonPersonalInfo(profileId: number, personalInfoData: Omit<PersonPersonalInfoCreate, 'person_id'>): Promise<PersonPersonalInfo> {
    const dataWithPersonId = { ...personalInfoData, person_id: profileId };
    const response = await api.post(`${this.basePath}/profiles/${profileId}/personal-info/`, dataWithPersonId);
    return response.data;
  }

  // Life Events Operations
  async getPersonLifeEvents(profileId: number, skip: number = 0, limit: number = 100): Promise<PersonLifeEvent[]> {
    const response = await api.get(`${this.basePath}/profiles/${profileId}/life-events/`, {
      params: { skip, limit }
    });
    return response.data;
  }

  async createPersonLifeEvent(profileId: number, lifeEventData: Omit<PersonLifeEventCreate, 'person_id'>): Promise<PersonLifeEvent> {
    const dataWithPersonId = { ...lifeEventData, person_id: profileId };
    const response = await api.post(`${this.basePath}/profiles/${profileId}/life-events/`, dataWithPersonId);
    return response.data;
  }

  // Belongings Operations
  async getPersonBelongings(profileId: number, skip: number = 0, limit: number = 100, activeOnly: boolean = true): Promise<PersonBelonging[]> {
    const response = await api.get(`${this.basePath}/profiles/${profileId}/belongings/`, {
      params: { skip, limit, active_only: activeOnly }
    });
    return response.data;
  }

  async createPersonBelonging(profileId: number, belongingData: Omit<PersonBelongingCreate, 'person_id'>): Promise<PersonBelonging> {
    const dataWithPersonId = { ...belongingData, person_id: profileId };
    const response = await api.post(`${this.basePath}/profiles/${profileId}/belongings/`, dataWithPersonId);
    return response.data;
  }

  // Relationships Operations
  async getPersonRelationships(profileId: number, includeInactive: boolean = false): Promise<PersonRelationship[]> {
    const response = await api.get(`${this.basePath}/profiles/${profileId}/relationships/`, {
      params: { include_inactive: includeInactive }
    });
    return response.data;
  }

  async createPersonRelationship(relationshipData: PersonRelationshipCreate): Promise<PersonRelationship> {
    const response = await api.post(`${this.basePath}/relationships/`, relationshipData);
    return response.data;
  }

  // Utility methods
  async getFullPersonProfile(profileId: number): Promise<PersonProfile> {
    const [
      profile,
      contactInfo,
      professionalInfo,
      personalInfo,
      lifeEvents,
      belongings
    ] = await Promise.all([
      this.getPersonProfile(profileId),
      this.getPersonContactInfo(profileId),
      this.getPersonProfessionalInfo(profileId),
      this.getPersonPersonalInfo(profileId),
      this.getPersonLifeEvents(profileId),
      this.getPersonBelongings(profileId)
    ]);

    return {
      ...profile,
      contact_info: contactInfo,
      professional_info: professionalInfo,
      personal_info: personalInfo,
      life_events: lifeEvents,
      belongings: belongings
    };
  }

  async createMinimalProfile(firstName: string, lastName?: string): Promise<PersonProfile> {
    return this.createPersonProfile({
      first_name: firstName,
      last_name: lastName
    });
  }

  async searchProfiles(query: string): Promise<PersonProfileSummary[]> {
    if (query.trim().length === 0) {
      return [];
    }
    return this.searchPersonProfiles(query, 0, 50);
  }

  // Privacy control helpers
  async shareProfileWithTenant(profileId: number): Promise<PersonProfile> {
    return this.updatePersonProfile(profileId, {
      visibility: 'tenant_shared' as any
    });
  }

  async makeProfilePrivate(profileId: number): Promise<PersonProfile> {
    return this.updatePersonProfile(profileId, {
      visibility: 'private' as any
    });
  }

  // Relationship helper methods
  async createFamilyRelationship(
    personAId: number, 
    personBId: number, 
    relationshipType: string,
    context?: string
  ): Promise<PersonRelationship> {
    return this.createPersonRelationship({
      person_a_id: personAId,
      person_b_id: personBId,
      relationship_type: relationshipType,
      relationship_category: 'family',
      context: context,
      is_mutual: true
    });
  }

  async createProfessionalRelationship(
    personAId: number, 
    personBId: number, 
    relationshipType: string,
    context?: string
  ): Promise<PersonRelationship> {
    return this.createPersonRelationship({
      person_a_id: personAId,
      person_b_id: personBId,
      relationship_type: relationshipType,
      relationship_category: 'professional',
      context: context,
      is_mutual: true
    });
  }

  async createSocialRelationship(
    personAId: number, 
    personBId: number, 
    relationshipType: string,
    howWeMet?: string
  ): Promise<PersonRelationship> {
    return this.createPersonRelationship({
      person_a_id: personAId,
      person_b_id: personBId,
      relationship_type: relationshipType,
      relationship_category: 'social',
      how_we_met: howWeMet,
      is_mutual: true
    });
  }
}

export default new RelationshipManagementService();