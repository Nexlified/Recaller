import api from './api';
import {
  ContactRelationship,
  ContactRelationshipCreate,
  ContactRelationshipUpdate,
  ContactRelationshipPair,
  RelationshipTypeOption,
  RelationshipSummary
} from '../types/ContactRelationship';

class ContactRelationshipService {
  private basePath = '/relationships';

  // Get all relationships for a specific contact
  async getContactRelationships(contactId: number, includeInactive: boolean = false): Promise<ContactRelationship[]> {
    const response = await api.get(`${this.basePath}/contact/${contactId}`, {
      params: { include_inactive: includeInactive }
    });
    return response.data;
  }

  // Get relationship summary for a contact grouped by category
  async getContactRelationshipSummary(contactId: number): Promise<RelationshipSummary> {
    const response = await api.get(`${this.basePath}/contact/${contactId}/summary`);
    return response.data;
  }

  // Create a new bidirectional relationship
  async createRelationship(relationshipData: ContactRelationshipCreate): Promise<ContactRelationshipPair> {
    const response = await api.post(this.basePath, relationshipData);
    return response.data;
  }

  // Update a specific relationship by ID
  async updateRelationship(relationshipId: number, updateData: ContactRelationshipUpdate): Promise<ContactRelationship> {
    const response = await api.put(`${this.basePath}/${relationshipId}`, updateData);
    return response.data;
  }

  // Update a bidirectional relationship between two contacts
  async updateBidirectionalRelationship(
    contactAId: number,
    contactBId: number,
    newRelationshipType: string,
    notes?: string,
    overrideGenderResolution: boolean = false
  ): Promise<ContactRelationshipPair> {
    const response = await api.put(`${this.basePath}/${contactAId}/${contactBId}`, null, {
      params: {
        new_relationship_type: newRelationshipType,
        notes,
        override_gender_resolution: overrideGenderResolution
      }
    });
    return response.data;
  }

  // Delete a bidirectional relationship
  async deleteRelationship(contactAId: number, contactBId: number): Promise<{ message: string }> {
    const response = await api.delete(`${this.basePath}/${contactAId}/${contactBId}`);
    return response.data;
  }

  // Get a specific relationship by ID
  async getRelationship(relationshipId: number): Promise<ContactRelationship> {
    const response = await api.get(`${this.basePath}/${relationshipId}`);
    return response.data;
  }

  // Get available relationship type options
  async getRelationshipOptions(includeBaseTypes: boolean = true): Promise<RelationshipTypeOption[]> {    
    try {
      const response = await api.get(`${this.basePath}/options`, {
        params: { include_base_types: includeBaseTypes }
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  // Get available relationship categories
  async getRelationshipCategories(): Promise<string[]> {
    const response = await api.get(`${this.basePath}/categories`);
    return response.data;
  }
}

const contactRelationshipService = new ContactRelationshipService();
export default contactRelationshipService;