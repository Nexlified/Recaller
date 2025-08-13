import api from './api';

export interface Contact {
  id: number;
  tenant_id: number;
  created_by_user_id: number;
  first_name: string;
  last_name: string;
  full_name: string;
  email?: string;
  phone?: string;
  title?: string;
  company?: string;
  notes?: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface ContactCreate {
  first_name: string;
  last_name: string;
  full_name: string;
  email?: string;
  phone?: string;
  title?: string;
  company?: string;
  notes?: string;
  is_active?: boolean;
}

export interface ContactUpdate {
  first_name?: string;
  last_name?: string;
  full_name?: string;
  email?: string;
  phone?: string;
  title?: string;
  company?: string;
  notes?: string;
  is_active?: boolean;
}

export interface ValidationResponse {
  exists: boolean;
  email?: string;
  phone?: string;
}

class ContactsService {
  async getContacts(skip: number = 0, limit: number = 100): Promise<Contact[]> {
    const response = await api.get<Contact[]>(`/contacts/?skip=${skip}&limit=${limit}`);
    return response.data;
  }

  async getContact(contactId: number): Promise<Contact> {
    const response = await api.get<Contact>(`/contacts/${contactId}`);
    return response.data;
  }

  async createContact(contactData: ContactCreate): Promise<Contact> {
    const response = await api.post<Contact>('/contacts/', contactData);
    return response.data;
  }

  async updateContact(contactId: number, contactData: ContactUpdate): Promise<Contact> {
    const response = await api.put<Contact>(`/contacts/${contactId}`, contactData);
    return response.data;
  }

  async deleteContact(contactId: number): Promise<void> {
    await api.delete(`/contacts/${contactId}`);
  }

  async searchContacts(query: string, skip: number = 0, limit: number = 100): Promise<Contact[]> {
    const response = await api.get<Contact[]>(`/contacts/search/?q=${encodeURIComponent(query)}&skip=${skip}&limit=${limit}`);
    return response.data;
  }

  async validateEmail(email: string): Promise<ValidationResponse> {
    const response = await api.get<ValidationResponse>(`/contacts/validate/email/${encodeURIComponent(email)}`);
    return response.data;
  }

  async validatePhone(phone: string): Promise<ValidationResponse> {
    const response = await api.get<ValidationResponse>(`/contacts/validate/phone/${encodeURIComponent(phone)}`);
    return response.data;
  }
}

export const contactsService = new ContactsService();
export default contactsService;