import api from './api';
import {
  SharedActivity,
  SharedActivityCreate,
  SharedActivityUpdate,
  ActivityInsights,
} from '../types/Activity';

export class ActivityService {
  /**
   * Get activities with optional filtering
   */
  async getActivities(params?: {
    skip?: number;
    limit?: number;
    contactId?: number;
  }): Promise<SharedActivity[]> {
    const queryParams = new URLSearchParams();
    
    if (params?.skip !== undefined) queryParams.append('skip', params.skip.toString());
    if (params?.limit !== undefined) queryParams.append('limit', params.limit.toString());
    if (params?.contactId !== undefined) queryParams.append('contact_id', params.contactId.toString());

    const response = await api.get(`/shared-activities?${queryParams.toString()}`);
    return response.data;
  }

  /**
   * Create new activity
   */
  async createActivity(activity: SharedActivityCreate): Promise<SharedActivity> {
    const response = await api.post('/shared-activities', activity);
    return response.data;
  }

  /**
   * Update existing activity
   */
  async updateActivity(id: number, activity: SharedActivityUpdate): Promise<SharedActivity> {
    const response = await api.put(`/shared-activities/${id}`, activity);
    return response.data;
  }

  /**
   * Delete activity
   */
  async deleteActivity(id: number): Promise<void> {
    await api.delete(`/shared-activities/${id}`);
  }

  /**
   * Get activity by ID
   */
  async getActivity(id: number): Promise<SharedActivity> {
    const response = await api.get(`/shared-activities/${id}`);
    return response.data;
  }

  /**
   * Get upcoming activities
   */
  async getUpcomingActivities(daysAhead: number = 30): Promise<SharedActivity[]> {
    const response = await api.get(`/shared-activities/upcoming?days_ahead=${daysAhead}`);
    return response.data;
  }

  /**
   * Get activity analytics and insights
   */
  async getActivityInsights(daysBack: number = 365): Promise<ActivityInsights> {
    const response = await api.get(`/shared-activities/insights?days_back=${daysBack}`);
    return response.data;
  }

  /**
   * Get activities with specific contact
   */
  async getActivitiesWithContact(contactId: number): Promise<SharedActivity[]> {
    const response = await api.get(`/shared-activities/with-contact/${contactId}`);
    return response.data;
  }

  /**
   * Get recent activities (last 30 days)
   */
  async getRecentActivities(limit: number = 10): Promise<SharedActivity[]> {
    const response = await api.get(`/shared-activities/recent?limit=${limit}`);
    return response.data;
  }

  /**
   * Update participant status
   */
  async updateParticipantStatus(
    activityId: number,
    participantId: number,
    status: string
  ): Promise<void> {
    await api.patch(`/shared-activities/${activityId}/participants/${participantId}`, {
      attendance_status: status,
    });
  }

  /**
   * Add participant to activity
   */
  async addParticipant(
    activityId: number,
    participant: {
      contact_id: number;
      participation_level: string;
      attendance_status: string;
    }
  ): Promise<void> {
    await api.post(`/shared-activities/${activityId}/participants`, participant);
  }

  /**
   * Remove participant from activity
   */
  async removeParticipant(activityId: number, participantId: number): Promise<void> {
    await api.delete(`/shared-activities/${activityId}/participants/${participantId}`);
  }

  /**
   * Upload activity photo
   */
  async uploadPhoto(activityId: number, file: File, caption?: string): Promise<void> {
    const formData = new FormData();
    formData.append('photo', file);
    if (caption) formData.append('caption', caption);

    await api.post(`/shared-activities/${activityId}/photos`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  }

  /**
   * Delete activity photo
   */
  async deletePhoto(activityId: number, photoId: string): Promise<void> {
    await api.delete(`/shared-activities/${activityId}/photos/${photoId}`);
  }

  /**
   * Search activities
   */
  async searchActivities(query: string): Promise<SharedActivity[]> {
    const response = await api.get(`/shared-activities/search?q=${encodeURIComponent(query)}`);
    return response.data;
  }
}

// Create and export a singleton instance
const activityService = new ActivityService();
export default activityService;