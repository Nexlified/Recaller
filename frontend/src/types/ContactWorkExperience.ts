export enum EmploymentType {
  FULL_TIME = "full-time",
  PART_TIME = "part-time",
  CONTRACT = "contract",
  INTERNSHIP = "internship",
  FREELANCE = "freelance",
  VOLUNTEER = "volunteer"
}

export enum WorkLocation {
  REMOTE = "remote",
  HYBRID = "hybrid",
  ON_SITE = "on-site",
  TRAVEL = "travel"
}

export enum WorkExperienceVisibility {
  PRIVATE = "private",
  TEAM = "team",
  PUBLIC = "public"
}

export interface ContactWorkExperience {
  id: number;
  contact_id: number;
  tenant_id: number;
  company_name: string;
  company_id?: number;
  job_title: string;
  department?: string;
  employment_type?: EmploymentType;
  work_location?: string;
  start_date: string; // ISO date string
  end_date?: string; // ISO date string
  is_current: boolean;
  work_phone?: string;
  work_email?: string;
  work_address?: string;
  job_description?: string;
  key_achievements?: string[];
  skills_used?: string[];
  salary_range?: string;
  currency: string;
  linkedin_profile?: string;
  other_profiles?: Record<string, any>;
  manager_contact_id?: number;
  reporting_structure?: string;
  can_be_reference: boolean;
  reference_notes?: string;
  visibility: WorkExperienceVisibility;
  created_at: string;
  updated_at?: string;
}

export interface ContactWorkExperienceCreate {
  company_name: string;
  company_id?: number;
  job_title: string;
  department?: string;
  employment_type?: EmploymentType;
  work_location?: string;
  start_date: string; // ISO date string
  end_date?: string; // ISO date string
  is_current?: boolean;
  work_phone?: string;
  work_email?: string;
  work_address?: string;
  job_description?: string;
  key_achievements?: string[];
  skills_used?: string[];
  salary_range?: string;
  currency?: string;
  linkedin_profile?: string;
  other_profiles?: Record<string, any>;
  manager_contact_id?: number;
  reporting_structure?: string;
  can_be_reference?: boolean;
  reference_notes?: string;
  visibility?: WorkExperienceVisibility;
}

export interface ContactWorkExperienceUpdate {
  company_name?: string;
  company_id?: number;
  job_title?: string;
  department?: string;
  employment_type?: EmploymentType;
  work_location?: string;
  start_date?: string; // ISO date string
  end_date?: string; // ISO date string
  is_current?: boolean;
  work_phone?: string;
  work_email?: string;
  work_address?: string;
  job_description?: string;
  key_achievements?: string[];
  skills_used?: string[];
  salary_range?: string;
  currency?: string;
  linkedin_profile?: string;
  other_profiles?: Record<string, any>;
  manager_contact_id?: number;
  reporting_structure?: string;
  can_be_reference?: boolean;
  reference_notes?: string;
  visibility?: WorkExperienceVisibility;
}

export interface ProfessionalConnection {
  contact_id: number;
  contact_name: string;
  connection_type: string; // "current_colleague", "former_colleague", "manager", "report"
  company_name: string;
  shared_companies: string[];
  mutual_connections: number;
}

export interface CompanyNetwork {
  company_name: string;
  current_employees: ContactWorkExperience[];
  former_employees: ContactWorkExperience[];
  total_connections: number;
}

export interface CareerTimeline {
  contact_id: number;
  work_experiences: ContactWorkExperience[];
  career_progression: string[];
  total_experience_years: number;
  skills_evolution: Record<string, string[]>; // skill -> companies where used
}