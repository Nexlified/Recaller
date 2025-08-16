import api from './api';
import { 
  RelationshipTypeOption,
  ContactRelationship,
  ContactRelationshipCreate,
  ContactRelationshipUpdate,
  ContactRelationshipPair,
  RelationshipSummary
} from '../types/ContactRelationship';

// Network data interfaces for visualizations
export interface NetworkNode {
  id: number;
  name: string;
  category: string;
  strength?: number;
  avatar?: string;
  gender?: string;
}

export interface NetworkEdge {
  source: number;
  target: number;
  relationship: string;
  strength: number;
  category: string;
  status: string;
  mutual: boolean;
}

export interface NetworkData {
  nodes: NetworkNode[];
  edges: NetworkEdge[];
}

export interface RelationshipAnalytics {
  totalRelationships: number;
  categoryDistribution: {
    family: number;
    professional: number;
    social: number;
    romantic: number;
  };
  strengthDistribution: {
    weak: number; // 1-3
    moderate: number; // 4-6
    strong: number; // 7-10
  };
  statusDistribution: {
    active: number;
    distant: number;
    ended: number;
  };
  topCategories: Array<{
    category: string;
    count: number;
    percentage: number;
  }>;
  networkInsights: {
    averageStrength: number;
    mostConnectedCategory: string;
    oldestRelationship?: ContactRelationship;
    newestRelationship?: ContactRelationship;
  };
}

export interface RelationshipTypes {
  version: string;
  categories: Array<{
    key: string;
    display_name: string;
    description: string;
  }>;
  relationship_types: RelationshipTypeOption[];
  gender_specific_relationships: Record<string, {
    description: string;
    mappings: Record<string, [string, string]>;
    fallback: [string, string];
  }>;
}

class RelationshipService {
  private basePath = '/relationships';
  private configPath = '/config/relationship-types';
  private relationshipTypesCache: RelationshipTypes | null = null;

  // Get relationship types from YAML config via API
  async getRelationshipTypes(): Promise<RelationshipTypes> {
    if (this.relationshipTypesCache) {
      return this.relationshipTypesCache;
    }

    try {
      const response = await api.get(this.configPath);
      this.relationshipTypesCache = response.data;
      return response.data;
    } catch (error) {
      console.error('Failed to load relationship types:', error);
      // Return minimal fallback configuration
      return {
        version: '1.0.0',
        categories: [
          { key: 'family', display_name: 'Family', description: 'Family relations' },
          { key: 'professional', display_name: 'Professional', description: 'Work relationships' },
          { key: 'social', display_name: 'Social', description: 'Friends and social connections' },
          { key: 'romantic', display_name: 'Romantic', description: 'Romantic relationships' }
        ],
        relationship_types: [],
        gender_specific_relationships: {}
      };
    }
  }

  // Clear cache to force reload
  clearCache(): void {
    this.relationshipTypesCache = null;
  }

  // CRUD operations (delegate to existing service)
  async createRelationship(contactId: number, relationship: ContactRelationshipCreate): Promise<ContactRelationshipPair> {
    const response = await api.post(this.basePath, relationship);
    return response.data;
  }

  async getContactRelationships(contactId: number): Promise<ContactRelationship[]> {
    const response = await api.get(`${this.basePath}/contact/${contactId}`);
    return response.data;
  }

  async updateRelationship(relationshipId: number, updates: ContactRelationshipUpdate): Promise<ContactRelationship> {
    const response = await api.put(`${this.basePath}/${relationshipId}`, updates);
    return response.data;
  }

  async deleteRelationship(contactAId: number, contactBId: number): Promise<{ message: string }> {
    const response = await api.delete(`${this.basePath}/${contactAId}/${contactBId}`);
    return response.data;
  }

  async getRelationshipOptions(includeBaseTypes: boolean = true): Promise<RelationshipTypeOption[]> {
    const response = await api.get(`${this.basePath}/options`, {
      params: { include_base_types: includeBaseTypes }
    });
    return response.data;
  }

  async getRelationshipCategories(): Promise<string[]> {
    const response = await api.get(`${this.basePath}/categories`);
    return response.data;
  }

  // Analytics
  async getRelationshipAnalytics(contactId?: number): Promise<RelationshipAnalytics> {
    const params = contactId ? { contact_id: contactId } : {};
    const response = await api.get(`${this.basePath}/analytics`, { params });
    return response.data;
  }

  async getNetworkData(contactId?: number): Promise<NetworkData> {
    const params = contactId ? { contact_id: contactId } : {};
    const response = await api.get(`${this.basePath}/network`, { params });
    return response.data;
  }

  // Validation functions
  validateRelationshipType(relationshipType: string): boolean {
    // This would check against the loaded YAML config
    return relationshipType.length > 0;
  }

  validateRelationshipStrength(strength: number): boolean {
    return strength >= 1 && strength <= 10;
  }

  validateBidirectionalRelationship(
    contactAId: number, 
    contactBId: number, 
    relationshipType: string
  ): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (contactAId === contactBId) {
      errors.push('Cannot create relationship with self');
    }

    if (!this.validateRelationshipType(relationshipType)) {
      errors.push('Invalid relationship type');
    }

    return {
      valid: errors.length === 0,
      errors
    };
  }

  // Relationship suggestions based on contact data
  async suggestRelationships(contactId: number): Promise<Array<{
    contactId: number;
    contactName: string;
    suggestedType: string;
    reason: string;
    confidence: number;
  }>> {
    try {
      const response = await api.get(`${this.basePath}/suggestions/${contactId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to get relationship suggestions:', error);
      return [];
    }
  }

  // Bulk operations
  async createBulkRelationships(relationships: ContactRelationshipCreate[]): Promise<ContactRelationshipPair[]> {
    const response = await api.post(`${this.basePath}/bulk`, { relationships });
    return response.data;
  }

  async deleteBulkRelationships(relationshipPairs: Array<{ contactAId: number; contactBId: number }>): Promise<{ deleted: number }> {
    const response = await api.delete(`${this.basePath}/bulk`, { data: { pairs: relationshipPairs } });
    return response.data;
  }
}

const relationshipService = new RelationshipService();
export default relationshipService;