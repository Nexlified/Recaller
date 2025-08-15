import api from './api';
import {
  ContactWorkExperience,
  ContactWorkExperienceCreate,
  ContactWorkExperienceUpdate,
  ProfessionalConnection,
  CompanyNetwork,
  CareerTimeline
} from '../types/ContactWorkExperience';

class ContactWorkExperienceService {
  // Contact Work Experience CRUD Operations
  async getContactWorkExperiences(
    contactId: number, 
    skip: number = 0, 
    limit: number = 100
  ): Promise<ContactWorkExperience[]> {
    const response = await api.get<ContactWorkExperience[]>(
      `/work-experience/contacts/${contactId}/work-experience?skip=${skip}&limit=${limit}`
    );
    return response.data;
  }

  async getCurrentWorkExperience(contactId: number): Promise<ContactWorkExperience | null> {
    const response = await api.get<ContactWorkExperience | null>(
      `/work-experience/contacts/${contactId}/work-experience/current`
    );
    return response.data;
  }

  async getWorkExperience(workExperienceId: number): Promise<ContactWorkExperience> {
    const response = await api.get<ContactWorkExperience>(
      `/work-experience/work-experience/${workExperienceId}`
    );
    return response.data;
  }

  async createWorkExperience(
    contactId: number, 
    workExperienceData: ContactWorkExperienceCreate
  ): Promise<ContactWorkExperience> {
    const response = await api.post<ContactWorkExperience>(
      `/work-experience/contacts/${contactId}/work-experience`,
      workExperienceData
    );
    return response.data;
  }

  async updateWorkExperience(
    workExperienceId: number,
    workExperienceData: ContactWorkExperienceUpdate
  ): Promise<ContactWorkExperience> {
    const response = await api.put<ContactWorkExperience>(
      `/work-experience/work-experience/${workExperienceId}`,
      workExperienceData
    );
    return response.data;
  }

  async deleteWorkExperience(workExperienceId: number): Promise<void> {
    await api.delete(`/work-experience/work-experience/${workExperienceId}`);
  }

  // Professional Network and Company Operations
  async getContactsByCompany(
    companyName: string,
    currentOnly: boolean = false,
    skip: number = 0,
    limit: number = 100
  ): Promise<ContactWorkExperience[]> {
    const response = await api.get<ContactWorkExperience[]>(
      `/work-experience/work-experience/by-company?company_name=${encodeURIComponent(companyName)}&current_only=${currentOnly}&skip=${skip}&limit=${limit}`
    );
    return response.data;
  }

  async getProfessionalNetwork(
    contactId: number,
    depth: number = 1
  ): Promise<ContactWorkExperience[]> {
    const response = await api.get<ContactWorkExperience[]>(
      `/work-experience/contacts/${contactId}/professional-network?depth=${depth}`
    );
    return response.data;
  }

  async getCareerTimeline(contactId: number): Promise<ContactWorkExperience[]> {
    const response = await api.get<ContactWorkExperience[]>(
      `/work-experience/contacts/${contactId}/career-timeline`
    );
    return response.data;
  }

  // Search and Filter Operations
  async searchWorkExperiences(
    query: string,
    skip: number = 0,
    limit: number = 100
  ): Promise<ContactWorkExperience[]> {
    const response = await api.get<ContactWorkExperience[]>(
      `/work-experience/work-experience/search?q=${encodeURIComponent(query)}&skip=${skip}&limit=${limit}`
    );
    return response.data;
  }

  async getContactsBySkills(
    skills: string[],
    skip: number = 0,
    limit: number = 100
  ): Promise<ContactWorkExperience[]> {
    const skillsParam = skills.join(',');
    const response = await api.get<ContactWorkExperience[]>(
      `/work-experience/work-experience/by-skills?skills=${encodeURIComponent(skillsParam)}&skip=${skip}&limit=${limit}`
    );
    return response.data;
  }

  async getPotentialReferences(
    skip: number = 0,
    limit: number = 100
  ): Promise<ContactWorkExperience[]> {
    const response = await api.get<ContactWorkExperience[]>(
      `/work-experience/work-experience/references?skip=${skip}&limit=${limit}`
    );
    return response.data;
  }

  // Utility Operations
  async getCompanies(): Promise<string[]> {
    const response = await api.get<string[]>('/work-experience/work-experience/companies');
    return response.data;
  }

  async getSkills(): Promise<string[]> {
    const response = await api.get<string[]>('/work-experience/work-experience/skills');
    return response.data;
  }

  // Helper methods for the frontend
  async getCompanyNetworkSummary(companyName: string): Promise<{
    current: ContactWorkExperience[];
    former: ContactWorkExperience[];
    total: number;
  }> {
    const [current, former] = await Promise.all([
      this.getContactsByCompany(companyName, true),
      this.getContactsByCompany(companyName, false)
    ]);

    // Filter out current employees from former to avoid duplicates
    const actualFormer = former.filter(exp => !exp.is_current);

    return {
      current,
      former: actualFormer,
      total: current.length + actualFormer.length
    };
  }

  async getContactWorkSummary(contactId: number): Promise<{
    current?: ContactWorkExperience;
    history: ContactWorkExperience[];
    totalExperience: number;
    companiesWorkedAt: string[];
    skillsUsed: string[];
  }> {
    const workExperiences = await this.getContactWorkExperiences(contactId);
    const current = workExperiences.find(exp => exp.is_current);
    const history = workExperiences.sort((a, b) => 
      new Date(b.start_date).getTime() - new Date(a.start_date).getTime()
    );

    const companiesWorkedAt = [...new Set(workExperiences.map(exp => exp.company_name))];
    const allSkills = workExperiences.flatMap(exp => exp.skills_used || []);
    const skillsUsed = [...new Set(allSkills)];

    // Calculate total experience in years (simplified calculation)
    const totalExperience = workExperiences.reduce((total, exp) => {
      const startDate = new Date(exp.start_date);
      const endDate = exp.end_date ? new Date(exp.end_date) : new Date();
      const years = (endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24 * 365);
      return total + Math.max(0, years);
    }, 0);

    return {
      current,
      history,
      totalExperience: Math.round(totalExperience * 10) / 10, // Round to 1 decimal
      companiesWorkedAt,
      skillsUsed
    };
  }

  // Validation helpers
  formatDate(date: Date): string {
    return date.toISOString().split('T')[0]; // YYYY-MM-DD format
  }

  parseDate(dateString: string): Date {
    return new Date(dateString);
  }

  validateDateRange(startDate: string, endDate?: string): boolean {
    if (!endDate) return true;
    return new Date(startDate) <= new Date(endDate);
  }

  validateCurrentPosition(isCurrent: boolean, endDate?: string): boolean {
    if (isCurrent && endDate) return false;
    return true;
  }
}

export const contactWorkExperienceService = new ContactWorkExperienceService();
export default contactWorkExperienceService;