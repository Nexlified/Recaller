export enum JournalEntryMood {
  VERY_HAPPY = 'very_happy',
  HAPPY = 'happy',
  CONTENT = 'content',
  NEUTRAL = 'neutral',
  ANXIOUS = 'anxious',
  SAD = 'sad',
  VERY_SAD = 'very_sad',
  ANGRY = 'angry',
  EXCITED = 'excited',
  GRATEFUL = 'grateful',
}

export enum WeatherImpact {
  POSITIVE = 'positive',
  NEUTRAL = 'neutral',
  NEGATIVE = 'negative',
}

export interface JournalTag {
  id: number;
  journal_entry_id: number;
  tag_name: string;
  tag_color?: string;
  created_at: string;
}

export interface JournalTagCreate {
  tag_name: string;
  tag_color?: string;
}

export interface JournalAttachment {
  id: number;
  journal_entry_id: number;
  original_filename: string;
  filename: string;
  file_path: string;
  file_size: number;
  file_type: string;
  description?: string;
  is_encrypted: boolean;
  created_at: string;
}

export interface JournalEntry {
  id: number;
  tenant_id: number;
  user_id: number;
  title?: string;
  content: string;
  entry_date: string; // ISO date string
  mood?: JournalEntryMood;
  location?: string;
  weather?: string;
  is_private: boolean;
  is_archived: boolean;
  entry_version: number;
  parent_entry_id?: number;
  is_encrypted: boolean;
  created_at: string;
  updated_at?: string;
  tags: JournalTag[];
  attachments: JournalAttachment[];
  
  // Day quality and life metrics
  day_quality_rating?: number; // 1-10 scale
  energy_level?: number; // 1-10 scale
  stress_level?: number; // 1-10 scale
  productivity_level?: number; // 1-10 scale
  social_interactions_count?: number;
  exercise_minutes?: number;
  sleep_quality?: number; // 1-10 scale
  weather_impact?: WeatherImpact;
  significant_events?: string[] | Record<string, unknown>[]; // JSON array of events
}

export interface JournalEntryCreate {
  title?: string;
  content: string;
  entry_date: string; // ISO date string
  mood?: JournalEntryMood;
  location?: string;
  weather?: string;
  is_private?: boolean;
  tags?: JournalTagCreate[];
  
  // Day quality and life metrics
  day_quality_rating?: number; // 1-10 scale
  energy_level?: number; // 1-10 scale
  stress_level?: number; // 1-10 scale
  productivity_level?: number; // 1-10 scale
  social_interactions_count?: number;
  exercise_minutes?: number;
  sleep_quality?: number; // 1-10 scale
  weather_impact?: WeatherImpact;
  significant_events?: string[] | Record<string, unknown>[]; // JSON array of events
}

export interface JournalEntryUpdate {
  title?: string;
  content?: string;
  entry_date?: string;
  mood?: JournalEntryMood;
  location?: string;
  weather?: string;
  is_private?: boolean;
  is_archived?: boolean;
  
  // Day quality and life metrics
  day_quality_rating?: number; // 1-10 scale
  energy_level?: number; // 1-10 scale
  stress_level?: number; // 1-10 scale
  productivity_level?: number; // 1-10 scale
  social_interactions_count?: number;
  exercise_minutes?: number;
  sleep_quality?: number; // 1-10 scale
  weather_impact?: WeatherImpact;
  significant_events?: string[] | Record<string, unknown>[]; // JSON array of events
}

export interface JournalEntrySummary {
  id: number;
  title?: string;
  entry_date: string;
  mood?: JournalEntryMood;
  is_private: boolean;
  is_archived: boolean;
  created_at: string;
  tag_count: number;
  attachment_count: number;
}

export interface PaginationMeta {
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

export interface JournalEntryListResponse {
  items: JournalEntrySummary[];
  pagination: PaginationMeta;
}

export interface JournalEntryStats {
  total_entries: number;
  entries_this_month: number;
  entries_this_week: number;
  average_words_per_entry: number;
  most_common_mood?: JournalEntryMood;
  most_used_tags: string[];
  longest_streak_days: number;
  current_streak_days: number;
}