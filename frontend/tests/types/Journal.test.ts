import { JournalEntryMood } from '../../src/types/Journal';

describe('Journal Types', () => {
  it('should have correct mood enum values', () => {
    expect(JournalEntryMood.VERY_HAPPY).toBe('very_happy');
    expect(JournalEntryMood.HAPPY).toBe('happy');
    expect(JournalEntryMood.CONTENT).toBe('content');
    expect(JournalEntryMood.NEUTRAL).toBe('neutral');
    expect(JournalEntryMood.ANXIOUS).toBe('anxious');
    expect(JournalEntryMood.SAD).toBe('sad');
    expect(JournalEntryMood.VERY_SAD).toBe('very_sad');
    expect(JournalEntryMood.ANGRY).toBe('angry');
    expect(JournalEntryMood.EXCITED).toBe('excited');
    expect(JournalEntryMood.GRATEFUL).toBe('grateful');
  });

  it('should have all expected mood options', () => {
    const moods = Object.values(JournalEntryMood);
    expect(moods).toHaveLength(10);
    expect(moods).toContain('very_happy');
    expect(moods).toContain('grateful');
  });
});