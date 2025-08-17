/**
 * TypeScript types for Person Profile (Relationship Management system)
 */

export enum PersonProfileVisibility {
  PRIVATE = "private",
  TENANT_SHARED = "tenant_shared"
}

// Base interfaces
export interface PersonProfileBase {
  first_name: string;
  last_name?: string;
  display_name?: string;
  notes?: string;
  gender?: string;
  is_active?: boolean;
  visibility?: PersonProfileVisibility;
}

export interface PersonContactInfoBase {
  email?: string;
  phone?: string;
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  country?: string;
  contact_type?: string;
  is_primary?: boolean;
  is_emergency_contact?: boolean;
  notes?: string;
  visibility?: PersonProfileVisibility;
}

export interface PersonProfessionalInfoBase {
  job_title?: string;
  organization_id?: number;
  organization_name?: string;
  department?: string;
  start_date?: string; // ISO date string
  end_date?: string; // ISO date string
  salary_range?: string;
  work_location?: string;
  employment_type?: string;
  notes?: string;
  is_current?: boolean;
  visibility?: PersonProfileVisibility;
}

export interface PersonPersonalInfoBase {
  date_of_birth?: string; // ISO date string
  anniversary_date?: string; // ISO date string
  maiden_name?: string;
  family_nickname?: string;
  preferred_name?: string;
  favorite_color?: string;
  favorite_food?: string;
  dietary_restrictions?: string;
  allergies?: string;
  personality_notes?: string;
  interests_hobbies?: string;
  notes?: string;
  visibility?: PersonProfileVisibility;
}

export interface PersonLifeEventBase {
  event_type: string;
  title: string;
  description?: string;
  event_date: string; // ISO date string
  location?: string;
  my_role?: string;
  significance?: number;
  is_recurring?: boolean;
  notes?: string;
  visibility?: PersonProfileVisibility;
}

export interface PersonBelongingBase {
  name: string;
  category?: string;
  description?: string;
  brand?: string;
  model?: string;
  estimated_value?: string;
  acquisition_date?: string; // ISO date string
  acquisition_method?: string;
  relationship_context?: string;
  notes?: string;
  visibility?: PersonProfileVisibility;
  is_active?: boolean;
}

export interface PersonRelationshipBase {
  person_a_id: number;
  person_b_id: number;
  relationship_type: string;
  relationship_category: string;
  relationship_strength?: number;
  start_date?: string; // ISO date string
  end_date?: string; // ISO date string
  how_we_met?: string;
  context?: string;
  notes?: string;
  is_mutual?: boolean;
  is_active?: boolean;
  visibility?: PersonProfileVisibility;
}

// Create interfaces
export interface PersonProfileCreate extends PersonProfileBase {}

export interface PersonContactInfoCreate extends PersonContactInfoBase {
  person_id: number;
}

export interface PersonProfessionalInfoCreate extends PersonProfessionalInfoBase {
  person_id: number;
}

export interface PersonPersonalInfoCreate extends PersonPersonalInfoBase {
  person_id: number;
}

export interface PersonLifeEventCreate extends PersonLifeEventBase {
  person_id: number;
}

export interface PersonBelongingCreate extends PersonBelongingBase {
  person_id: number;
}

export interface PersonRelationshipCreate extends PersonRelationshipBase {}

// Update interfaces (all fields optional)
export interface PersonProfileUpdate {
  first_name?: string;
  last_name?: string;
  display_name?: string;
  notes?: string;
  gender?: string;
  is_active?: boolean;
  visibility?: PersonProfileVisibility;
}

export interface PersonContactInfoUpdate {
  email?: string;
  phone?: string;
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  country?: string;
  contact_type?: string;
  is_primary?: boolean;
  is_emergency_contact?: boolean;
  notes?: string;
  visibility?: PersonProfileVisibility;
}

export interface PersonProfessionalInfoUpdate {
  job_title?: string;
  organization_id?: number;
  organization_name?: string;
  department?: string;
  start_date?: string;
  end_date?: string;
  salary_range?: string;
  work_location?: string;
  employment_type?: string;
  notes?: string;
  is_current?: boolean;
  visibility?: PersonProfileVisibility;
}

export interface PersonPersonalInfoUpdate {
  date_of_birth?: string;
  anniversary_date?: string;
  maiden_name?: string;
  family_nickname?: string;
  preferred_name?: string;
  favorite_color?: string;
  favorite_food?: string;
  dietary_restrictions?: string;
  allergies?: string;
  personality_notes?: string;
  interests_hobbies?: string;
  notes?: string;
  visibility?: PersonProfileVisibility;
}

export interface PersonLifeEventUpdate {
  event_type?: string;
  title?: string;
  description?: string;
  event_date?: string;
  location?: string;
  my_role?: string;
  significance?: number;
  is_recurring?: boolean;
  notes?: string;
  visibility?: PersonProfileVisibility;
}

export interface PersonBelongingUpdate {
  name?: string;
  category?: string;
  description?: string;
  brand?: string;
  model?: string;
  estimated_value?: string;
  acquisition_date?: string;
  acquisition_method?: string;
  relationship_context?: string;
  notes?: string;
  visibility?: PersonProfileVisibility;
  is_active?: boolean;
}

export interface PersonRelationshipUpdate {
  relationship_type?: string;
  relationship_category?: string;
  relationship_strength?: number;
  start_date?: string;
  end_date?: string;
  how_we_met?: string;
  context?: string;
  notes?: string;
  is_mutual?: boolean;
  is_active?: boolean;
  visibility?: PersonProfileVisibility;
}

// Response interfaces (with database fields)
export interface PersonContactInfo extends PersonContactInfoBase {
  id: number;
  person_id: number;
  tenant_id: number;
  created_at: string;
  updated_at?: string;
}

export interface PersonProfessionalInfo extends PersonProfessionalInfoBase {
  id: number;
  person_id: number;
  tenant_id: number;
  created_at: string;
  updated_at?: string;
}

export interface PersonPersonalInfo extends PersonPersonalInfoBase {
  id: number;
  person_id: number;
  tenant_id: number;
  created_at: string;
  updated_at?: string;
}

export interface PersonLifeEvent extends PersonLifeEventBase {
  id: number;
  person_id: number;
  tenant_id: number;
  created_at: string;
  updated_at?: string;
}

export interface PersonBelonging extends PersonBelongingBase {
  id: number;
  person_id: number;
  tenant_id: number;
  created_at: string;
  updated_at?: string;
}

export interface PersonRelationship extends PersonRelationshipBase {
  id: number;
  tenant_id: number;
  created_by_user_id: number;
  created_at: string;
  updated_at?: string;
}

export interface PersonProfile extends PersonProfileBase {
  id: number;
  tenant_id: number;
  created_by_user_id: number;
  created_at: string;
  updated_at?: string;
  
  // Optional related information
  contact_info?: PersonContactInfo[];
  professional_info?: PersonProfessionalInfo[];
  personal_info?: PersonPersonalInfo[];
  life_events?: PersonLifeEvent[];
  belongings?: PersonBelonging[];
}

// Simplified response for lists
export interface PersonProfileSummary {
  id: number;
  first_name: string;
  last_name?: string;
  display_name?: string;
  visibility: PersonProfileVisibility;
  created_at: string;
}

// API Response types
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
}

// Utility types for forms
export interface PersonProfileFormData extends PersonProfileCreate {
  // Additional form-specific fields can go here
}

export interface PersonContactInfoFormData extends PersonContactInfoCreate {
  // Additional form-specific fields can go here
}

// Error types
export interface ValidationError {
  field: string;
  message: string;
}

export interface ApiError {
  detail: string;
  validation_errors?: ValidationError[];
}