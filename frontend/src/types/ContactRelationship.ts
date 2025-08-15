export enum RelationshipStatus {
  ACTIVE = 'active',
  DISTANT = 'distant',
  ENDED = 'ended'
}

export interface ContactRelationship {
  id: number;
  tenant_id: number;
  created_by_user_id: number;
  contact_a_id: number;
  contact_b_id: number;
  relationship_type: string;
  relationship_category: string;
  relationship_strength?: number;
  relationship_status: RelationshipStatus;
  start_date?: string;
  end_date?: string;
  is_mutual: boolean;
  notes?: string;
  context?: string;
  is_active: boolean;
  is_gender_resolved: boolean;
  original_relationship_type?: string;
  created_at: string;
  updated_at?: string;
}

export interface ContactRelationshipCreate {
  contact_a_id: number;
  contact_b_id: number;
  relationship_type: string;
  relationship_strength?: number;
  relationship_status?: RelationshipStatus;
  start_date?: string;
  end_date?: string;
  is_mutual?: boolean;
  notes?: string;
  context?: string;
  override_gender_resolution?: boolean;
}

export interface ContactRelationshipUpdate {
  relationship_type?: string;
  relationship_strength?: number;
  relationship_status?: RelationshipStatus;
  start_date?: string;
  end_date?: string;
  is_mutual?: boolean;
  notes?: string;
  context?: string;
  is_active?: boolean;
}

export interface ContactRelationshipPair {
  contact_a_id: number;
  contact_b_id: number;
  relationship_a_to_b: string;
  relationship_b_to_a: string;
  relationship_category: string;
  is_gender_resolved: boolean;
  original_relationship_type?: string;
}

export interface RelationshipTypeOption {
  key: string;
  display_name: string;
  category: string;
  is_gender_specific: boolean;
  description?: string;
}

export interface RelationshipSummary {
  [category: string]: Array<{
    relationship_id: number;
    relationship_type: string;
    other_contact_id: number;
    other_contact_name: string;
    is_gender_resolved: boolean;
    original_relationship_type?: string;
    notes?: string;
    created_at: string;
  }>;
}