import React, { useState, useEffect, useCallback } from 'react';
import { 
  ContactRelationship, 
  ContactRelationshipCreate, 
  RelationshipTypeOption, 
  RelationshipStatus 
} from '../../types/ContactRelationship';
import { Contact } from '../../services/contacts';
import contactRelationshipService from '../../services/contactRelationships';
import contactsService from '../../services/contacts';
import relationshipService from '../../services/relationships';

interface RelationshipManagerProps {
  contactId: number;
  onRelationshipChange?: () => void;
}

export const RelationshipManager: React.FC<RelationshipManagerProps> = ({
  contactId,
  onRelationshipChange
}) => {
  const [relationships, setRelationships] = useState<ContactRelationship[]>([]);
  const [relationshipOptions, setRelationshipOptions] = useState<RelationshipTypeOption[]>([]);
  const [availableContacts, setAvailableContacts] = useState<Contact[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newRelationship, setNewRelationship] = useState<ContactRelationshipCreate>({
    contact_a_id: contactId,
    contact_b_id: 0,
    relationship_type: '',
    relationship_strength: 5,
    relationship_status: RelationshipStatus.ACTIVE,
    start_date: new Date().toISOString().split('T')[0],
    end_date: undefined,
    is_mutual: true,
    notes: '',
    context: ''
  });
  const [showBidirectionalPreview, setShowBidirectionalPreview] = useState(false);
  const [relationshipCategories, setRelationshipCategories] = useState<Record<string, RelationshipTypeOption[]>>({});

  useEffect(() => {
    loadData();
  }, [loadData]);

  const loadData = useCallback(async () => {
    try {
      setIsLoading(true);
      const [relationshipsData, optionsData, contactsData] = await Promise.all([
        contactRelationshipService.getContactRelationships(contactId),
        contactRelationshipService.getRelationshipOptions(),
        contactsService.getContacts()
      ]);

      setRelationships(relationshipsData);
      setRelationshipOptions(optionsData);
      // Filter out the current contact from available contacts
      setAvailableContacts(contactsData.filter(c => c.id !== contactId));
      
      // Group relationship options by category
      const grouped = optionsData.reduce((acc, option) => {
        if (!acc[option.category]) {
          acc[option.category] = [];
        }
        acc[option.category].push(option);
        return acc;
      }, {} as Record<string, RelationshipTypeOption[]>);
      setRelationshipCategories(grouped);
    } catch (error) {
      console.error('Error loading relationship data:', error);
    } finally {
      setIsLoading(false);
    }
  }, [contactId]);

  const handleCreateRelationship = async () => {
    try {
      if (!newRelationship.contact_b_id || !newRelationship.relationship_type) {
        alert('Please select a contact and relationship type');
        return;
      }
      
      const validationResult = relationshipService.validateBidirectionalRelationship(
        newRelationship.contact_a_id,
        newRelationship.contact_b_id,
        newRelationship.relationship_type
      );
      
      if (!validationResult.valid) {
        alert(`Validation failed: ${validationResult.errors.join(', ')}`);
        return;
      }

      await contactRelationshipService.createRelationship(newRelationship);
      await loadData();
      setShowAddForm(false);
      setShowBidirectionalPreview(false);
      setNewRelationship({
        contact_a_id: contactId,
        contact_b_id: 0,
        relationship_type: '',
        relationship_strength: 5,
        relationship_status: RelationshipStatus.ACTIVE,
        start_date: new Date().toISOString().split('T')[0],
        end_date: undefined,
        is_mutual: true,
        notes: '',
        context: ''
      });
      
      onRelationshipChange?.();
      alert('Relationship created successfully!');
    } catch (error) {
      console.error('Error creating relationship:', error);
      alert('Failed to create relationship. Please try again.');
    }
  };

  const getSelectedContactName = () => {
    const contact = availableContacts.find(c => c.id === newRelationship.contact_b_id);
    return contact ? `${contact.first_name} ${contact.last_name || ''}`.trim() : '';
  };

  const getCurrentContactName = () => {
    // This would ideally come from a contact context or prop
    return 'Current Contact';
  };

  const getBidirectionalPreview = () => {
    if (!newRelationship.relationship_type || !newRelationship.contact_b_id) {
      return null;
    }
    
    const selectedOption = relationshipOptions.find(opt => opt.key === newRelationship.relationship_type);
    if (!selectedOption) return null;
    
    const currentName = getCurrentContactName();
    const selectedName = getSelectedContactName();
    
    // For simplicity, show the basic relationship preview
    // In a full implementation, this would use the gender resolution logic
    return {
      aToB: `${currentName} → ${selectedName}: ${selectedOption.display_name}`,
      bToA: `${selectedName} → ${currentName}: ${selectedOption.display_name}` // This would be the reverse type
    };
  };

  const handleDeleteRelationship = async (relationship: ContactRelationship) => {
    if (!confirm(`Are you sure you want to delete this relationship?`)) {
      return;
    }

    try {
      await contactRelationshipService.deleteRelationship(
        relationship.contact_a_id,
        relationship.contact_b_id
      );
      await loadData();
      onRelationshipChange?.();
      alert('Relationship deleted successfully!');
    } catch (error) {
      console.error('Error deleting relationship:', error);
      alert('Failed to delete relationship. Please try again.');
    }
  };

  const getRelatedContactName = (relationship: ContactRelationship) => {
    const relatedContactId = relationship.contact_a_id === contactId 
      ? relationship.contact_b_id 
      : relationship.contact_a_id;
    
    const contact = availableContacts.find(c => c.id === relatedContactId);
    return contact ? `${contact.first_name} ${contact.last_name || ''}`.trim() : 'Unknown Contact';
  };

  const getStrengthColor = (strength?: number) => {
    if (!strength) return 'bg-gray-200';
    if (strength >= 8) return 'bg-green-500';
    if (strength >= 6) return 'bg-yellow-500';
    if (strength >= 4) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const getStatusColor = (status: RelationshipStatus) => {
    switch (status) {
      case RelationshipStatus.ACTIVE:
        return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400';
      case RelationshipStatus.DISTANT:
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400';
      case RelationshipStatus.ENDED:
        return 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400';
    }
  };

  if (isLoading) {
    return (
      <div className="p-4">
        <div className="text-center text-gray-600 dark:text-gray-400">
          Loading relationships...
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Relationships ({relationships.length})
        </h3>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          {showAddForm ? 'Cancel' : 'Add Relationship'}
        </button>
      </div>

      {showAddForm && (
        <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg space-y-4">
          <h4 className="font-medium text-gray-900 dark:text-white">Add New Relationship</h4>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Contact
              </label>
              <select
                value={newRelationship.contact_b_id}
                onChange={(e) => setNewRelationship({
                  ...newRelationship,
                  contact_b_id: parseInt(e.target.value)
                })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              >
                <option value={0}>Select a contact...</option>
                {availableContacts.map(contact => (
                  <option key={contact.id} value={contact.id}>
                    {contact.first_name} {contact.last_name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Relationship Type
              </label>
              <select
                value={newRelationship.relationship_type}
                onChange={(e) => {
                  setNewRelationship({
                    ...newRelationship,
                    relationship_type: e.target.value
                  });
                  // Show preview when type is selected
                  if (e.target.value && newRelationship.contact_b_id) {
                    setShowBidirectionalPreview(true);
                  }
                }}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              >
                <option value="">Select relationship type...</option>
                {Object.entries(relationshipCategories).map(([category, options]) => (
                  <optgroup key={category} label={category.charAt(0).toUpperCase() + category.slice(1)}>
                    {options.map(option => (
                      <option key={option.key} value={option.key}>
                        {option.display_name}
                        {option.description && ` - ${option.description}`}
                      </option>
                    ))}
                  </optgroup>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Relationship Strength: {newRelationship.relationship_strength}/10
              </label>
              <div className="mt-2 space-y-2">
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={newRelationship.relationship_strength}
                  onChange={(e) => setNewRelationship({
                    ...newRelationship,
                    relationship_strength: parseInt(e.target.value)
                  })}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
                />
                <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400">
                  <span>Weak</span>
                  <span>Moderate</span>
                  <span>Strong</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-full h-2 bg-gray-200 rounded-full">
                    <div
                      className={`h-2 rounded-full transition-all duration-200 ${getStrengthColor(newRelationship.relationship_strength)}`}
                      style={{ width: `${(newRelationship.relationship_strength / 10) * 100}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300 min-w-[3rem]">
                    {newRelationship.relationship_strength}/10
                  </span>
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Status
              </label>
              <select
                value={newRelationship.relationship_status}
                onChange={(e) => setNewRelationship({
                  ...newRelationship,
                  relationship_status: e.target.value as RelationshipStatus
                })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              >
                <option value={RelationshipStatus.ACTIVE}>Active</option>
                <option value={RelationshipStatus.DISTANT}>Distant</option>
                <option value={RelationshipStatus.ENDED}>Ended</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Start Date
              </label>
              <input
                type="date"
                value={newRelationship.start_date || ''}
                onChange={(e) => setNewRelationship({
                  ...newRelationship,
                  start_date: e.target.value
                })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                End Date (Optional)
              </label>
              <input
                type="date"
                value={newRelationship.end_date || ''}
                onChange={(e) => setNewRelationship({
                  ...newRelationship,
                  end_date: e.target.value || undefined
                })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                disabled={newRelationship.relationship_status === RelationshipStatus.ACTIVE}
              />
              {newRelationship.relationship_status === RelationshipStatus.ACTIVE && (
                <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                  End date disabled for active relationships
                </p>
              )}
            </div>
          </div>

          {/* Bidirectional Preview */}
          {showBidirectionalPreview && getBidirectionalPreview() && (
            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
              <h5 className="font-medium text-blue-900 dark:text-blue-100 mb-2">
                📝 Bidirectional Relationship Preview
              </h5>
              <div className="space-y-1 text-sm">
                <div className="text-blue-800 dark:text-blue-200">
                  {getBidirectionalPreview()?.aToB}
                </div>
                <div className="text-blue-800 dark:text-blue-200">
                  {getBidirectionalPreview()?.bToA}
                </div>
              </div>
              <p className="mt-2 text-xs text-blue-700 dark:text-blue-300">
                Both relationship directions will be created automatically
              </p>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Notes
              </label>
              <textarea
                value={newRelationship.notes}
                onChange={(e) => setNewRelationship({
                  ...newRelationship,
                  notes: e.target.value
                })}
                rows={2}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                placeholder="Optional notes about the relationship..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Context
              </label>
              <textarea
                value={newRelationship.context}
                onChange={(e) => setNewRelationship({
                  ...newRelationship,
                  context: e.target.value
                })}
                rows={2}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                placeholder="Where did you meet, how do you know each other..."
              />
            </div>
          </div>

          <div className="flex justify-end space-x-2">
            <button
              onClick={() => setShowAddForm(false)}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-600"
            >
              Cancel
            </button>
            <button
              onClick={handleCreateRelationship}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Create Relationship
            </button>
          </div>
        </div>
      )}

      {relationships.length === 0 ? (
        <div className="text-center py-8 text-gray-500 dark:text-gray-400">
          No relationships found. Add one to get started.
        </div>
      ) : (
        <div className="space-y-3">
          {relationships.map((relationship) => (
            <div
              key={relationship.id}
              className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm"
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center space-x-3">
                    <span className="font-medium text-gray-900 dark:text-white">
                      {getRelatedContactName(relationship)}
                    </span>
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      {relationship.relationship_type}
                    </span>
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(relationship.relationship_status)}`}>
                      {relationship.relationship_status}
                    </span>
                  </div>
                  
                  {relationship.relationship_strength && (
                    <div className="flex items-center mt-2 space-x-2">
                      <span className="text-sm text-gray-600 dark:text-gray-400">Strength:</span>
                      <div className="flex items-center space-x-1">
                        <div className="w-16 h-2 bg-gray-200 rounded-full">
                          <div
                            className={`h-2 rounded-full ${getStrengthColor(relationship.relationship_strength)}`}
                            style={{ width: `${(relationship.relationship_strength / 10) * 100}%` }}
                          />
                        </div>
                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                          {relationship.relationship_strength}/10
                        </span>
                      </div>
                    </div>
                  )}

                  {relationship.notes && (
                    <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                      {relationship.notes}
                    </p>
                  )}

                  {relationship.is_gender_resolved && relationship.original_relationship_type && (
                    <p className="mt-1 text-xs text-blue-600 dark:text-blue-400">
                      Auto-resolved from: {relationship.original_relationship_type}
                    </p>
                  )}
                </div>

                <button
                  onClick={() => handleDeleteRelationship(relationship)}
                  className="ml-4 text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300 text-sm"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};