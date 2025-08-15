import { render, screen } from '@testing-library/react';
import { JournalEntryList } from '../../src/components/journal/JournalEntryList';
import { JournalEntrySummary, JournalEntryMood } from '../../src/types/Journal';

const mockEntries: JournalEntrySummary[] = [
  {
    id: 1,
    title: "Test Entry",
    entry_date: "2024-01-15",
    mood: JournalEntryMood.HAPPY,
    is_private: true,
    is_archived: false,
    created_at: "2024-01-15T10:30:00Z",
    tag_count: 1,
    attachment_count: 0,
  },
];

// Mock Next.js Link component
jest.mock('next/link', () => {
  return function MockLink({ children, href }: { children: React.ReactNode; href: string }) {
    return <a href={href}>{children}</a>;
  };
});

describe('JournalEntryList', () => {
  it('renders journal entries correctly', () => {
    render(<JournalEntryList entries={mockEntries} />);
    
    expect(screen.getByText('Test Entry')).toBeInTheDocument();
    expect(screen.getByText('Today')).toBeInTheDocument(); // Today's date formatting
    expect(screen.getByText('😊')).toBeInTheDocument(); // Mood emoji
    expect(screen.getByText('1 tag')).toBeInTheDocument();
    expect(screen.getByText('Private')).toBeInTheDocument();
  });

  it('shows empty state when no entries', () => {
    render(<JournalEntryList entries={[]} />);
    
    expect(screen.getByText('No journal entries yet')).toBeInTheDocument();
    expect(screen.getByText('Start documenting your thoughts and experiences.')).toBeInTheDocument();
  });

  it('shows loading state', () => {
    render(<JournalEntryList entries={[]} isLoading={true} />);
    
    expect(screen.getAllByText('')).toHaveLength(5); // 5 loading skeleton items
  });
});