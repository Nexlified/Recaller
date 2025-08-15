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
    is_mutual: true,
    notes: '',
    context: ''
  });

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

      await contactRelationshipService.createRelationship(newRelationship);
      await loadData();
      setShowAddForm(false);
      setNewRelationship({
        contact_a_id: contactId,
        contact_b_id: 0,
        relationship_type: '',
        relationship_strength: 5,
        relationship_status: RelationshipStatus.ACTIVE,
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
                onChange={(e) => setNewRelationship({
                  ...newRelationship,
                  relationship_type: e.target.value
                })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              >
                <option value="">Select relationship type...</option>
                {relationshipOptions.map(option => (
                  <option key={option.key} value={option.key}>
                    {option.display_name} ({option.category})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Strength (1-10)
              </label>
              <input
                type="number"
                min="1"
                max="10"
                value={newRelationship.relationship_strength}
                onChange={(e) => setNewRelationship({
                  ...newRelationship,
                  relationship_strength: parseInt(e.target.value)
                })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
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
          </div>

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