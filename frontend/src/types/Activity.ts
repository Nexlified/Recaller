export interface SharedActivity {
  id: number;
  tenant_id: number;
  created_by_user_id: number;
  activity_type: string;
  title: string;
  description?: string;
  location?: string;
  activity_date: string;
  start_time?: string;
  end_time?: string;
  duration_minutes?: number;
  cost_per_person?: number;
  total_cost?: number;
  currency: string;
  quality_rating?: number;
  photos?: ActivityPhoto[];
  notes?: string;
  memorable_moments?: string;
  status: 'planned' | 'completed' | 'cancelled' | 'postponed';
  is_private: boolean;
  created_at: string;
  updated_at?: string;
  participants: SharedActivityParticipant[];
}

export interface SharedActivityParticipant {
  id: number;
  activity_id: number;
  contact_id: number;
  tenant_id: number;
  participation_level: 'organizer' | 'participant' | 'invitee';
  attendance_status: 'confirmed' | 'maybe' | 'declined' | 'no_show' | 'attended';
  participant_notes?: string;
  satisfaction_rating?: number;
  created_at: string;
  updated_at?: string;
  contact?: {
    id: number;
    first_name: string;
    last_name?: string;
    email?: string;
  };
}

export interface SharedActivityCreate {
  activity_type: string;
  title: string;
  description?: string;
  location?: string;
  activity_date: string;
  start_time?: string;
  end_time?: string;
  duration_minutes?: number;
  cost_per_person?: number;
  total_cost?: number;
  currency?: string;
  quality_rating?: number;
  photos?: ActivityPhoto[];
  notes?: string;
  memorable_moments?: string;
  status?: 'planned' | 'completed' | 'cancelled' | 'postponed';
  is_private?: boolean;
  participants: SharedActivityParticipantCreate[];
}

export interface SharedActivityUpdate {
  activity_type?: string;
  title?: string;
  description?: string;
  location?: string;
  activity_date?: string;
  start_time?: string;
  end_time?: string;
  duration_minutes?: number;
  cost_per_person?: number;
  total_cost?: number;
  currency?: string;
  quality_rating?: number;
  photos?: ActivityPhoto[];
  notes?: string;
  memorable_moments?: string;
  status?: 'planned' | 'completed' | 'cancelled' | 'postponed';
  is_private?: boolean;
}

export interface SharedActivityParticipantCreate {
  contact_id: number;
  participation_level: 'organizer' | 'participant' | 'invitee';
  attendance_status: 'confirmed' | 'maybe' | 'declined' | 'no_show' | 'attended';
  participant_notes?: string;
  satisfaction_rating?: number;
}

export interface SharedActivityParticipantUpdate {
  participation_level?: 'organizer' | 'participant' | 'invitee';
  attendance_status?: 'confirmed' | 'maybe' | 'declined' | 'no_show' | 'attended';
  participant_notes?: string;
  satisfaction_rating?: number;
}

export interface ActivityInsights {
  total_activities: number;
  activities_this_month: number;
  favorite_activity_type?: string;
  average_quality_rating?: number;
  total_spent?: number;
  most_active_contacts: ContactActivitySummary[];
  activity_frequency: Record<string, number>;
}

export interface ContactActivitySummary {
  contact_id: number;
  contact_name: string;
  activity_count: number;
  last_activity_date?: string;
  favorite_activity_type?: string;
  average_quality_rating?: number;
}

export interface ActivityPhoto {
  id: string;
  url: string;
  thumbnail_url: string;
  caption?: string;
  taken_at?: string;
  uploaded_at: string;
}

// Activity Type Constants
export const ACTIVITY_TYPES = [
  { value: 'dinner', label: 'Dinner', icon: '🍽️' },
  { value: 'movie', label: 'Movie', icon: '🎬' },
  { value: 'sports', label: 'Sports', icon: '⚽' },
  { value: 'travel', label: 'Travel', icon: '✈️' },
  { value: 'work_meeting', label: 'Work Meeting', icon: '💼' },
  { value: 'coffee', label: 'Coffee', icon: '☕' },
  { value: 'party', label: 'Party', icon: '🎉' },
  { value: 'conference', label: 'Conference', icon: '👥' },
  { value: 'workshop', label: 'Workshop', icon: '🛠️' },
  { value: 'hobby', label: 'Hobby', icon: '🎨' },
  { value: 'shopping', label: 'Shopping', icon: '🛒' },
  { value: 'cultural', label: 'Cultural', icon: '🎭' },
  { value: 'outdoor', label: 'Outdoor', icon: '🌳' },
  { value: 'game_night', label: 'Game Night', icon: '🎲' },
  { value: 'other', label: 'Other', icon: '📝' },
] as const;

export const PARTICIPATION_LEVELS = [
  { value: 'organizer', label: 'Organizer' },
  { value: 'participant', label: 'Participant' },
  { value: 'invitee', label: 'Invitee' },
] as const;

export const ATTENDANCE_STATUS = [
  { value: 'confirmed', label: 'Confirmed' },
  { value: 'maybe', label: 'Maybe' },
  { value: 'declined', label: 'Declined' },
  { value: 'no_show', label: 'No Show' },
  { value: 'attended', label: 'Attended' },
] as const;

export const ACTIVITY_STATUS = [
  { value: 'planned', label: 'Planned' },
  { value: 'completed', label: 'Completed' },
  { value: 'cancelled', label: 'Cancelled' },
  { value: 'postponed', label: 'Postponed' },
] as const;