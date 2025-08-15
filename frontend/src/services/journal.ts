import api from './api';
import {
  JournalEntry,
  JournalEntryCreate,
  JournalEntryUpdate,
  JournalEntryListResponse,
  JournalEntryStats,
  JournalEntryMood,
} from '../types/Journal';

export interface JournalEntryFilters {
  page?: number;
  per_page?: number;
  include_archived?: boolean;
  mood?: JournalEntryMood;
  start_date?: string;
  end_date?: string;
  search?: string;
}

class JournalService {
  private readonly basePath = '/journal';

  async getJournalEntries(filters: JournalEntryFilters = {}): Promise<JournalEntryListResponse> {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        params.append(key, value.toString());
      }
    });

    const response = await api.get(`${this.basePath}?${params.toString()}`);
    return response.data;
  }

  async getJournalEntry(id: number): Promise<JournalEntry> {
    const response = await api.get(`${this.basePath}/${id}`);
    return response.data;
  }

  async createJournalEntry(entry: JournalEntryCreate): Promise<JournalEntry> {
    const response = await api.post(this.basePath, entry);
    return response.data;
  }

  async updateJournalEntry(id: number, entry: JournalEntryUpdate): Promise<JournalEntry> {
    const response = await api.put(`${this.basePath}/${id}`, entry);
    return response.data;
  }

  async deleteJournalEntry(id: number): Promise<void> {
    await api.delete(`${this.basePath}/${id}`);
  }

  async archiveJournalEntry(id: number): Promise<JournalEntry> {
    const response = await api.post(`${this.basePath}/${id}/archive`);
    return response.data;
  }

  async unarchiveJournalEntry(id: number): Promise<JournalEntry> {
    const response = await api.post(`${this.basePath}/${id}/unarchive`);
    return response.data;
  }

  async getJournalStats(): Promise<JournalEntryStats> {
    const response = await api.get(`${this.basePath}/stats`);
    return response.data;
  }

  async searchJournalEntries(query: string, filters: JournalEntryFilters = {}): Promise<JournalEntryListResponse> {
    const params = new URLSearchParams({ search: query });
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && key !== 'search') {
        params.append(key, value.toString());
      }
    });

    const response = await api.get(`${this.basePath}?${params.toString()}`);
    return response.data;
  }
}

const journalService = new JournalService();
export default journalService;