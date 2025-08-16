import React, { useEffect, useState } from 'react';
import { ContactRelationship } from '../../types/ContactRelationship';
import { Contact } from '../../services/contacts';

interface ProfessionalNetworkProps {
  contactId: number;
  relationships: ContactRelationship[];
  contacts: Contact[];
  onContactClick?: (contactId: number) => void;
}

interface ProfessionalNode {
  id: number;
  name: string;
  company?: string;
  position?: string;
  relationship: string;
  level: number; // 0 = current user, -1 = manager, 1 = subordinate, 2 = colleague
  strength: number;
  isRoot?: boolean;
}

interface CompanyGroup {
  company: string;
  nodes: ProfessionalNode[];
}

export const ProfessionalNetwork: React.FC<ProfessionalNetworkProps> = ({
  contactId,
  relationships,
  contacts,
  onContactClick
}) => {
  const [professionalData, setProfessionalData] = useState<CompanyGroup[]>([]);
  const [selectedNode, setSelectedNode] = useState<number | null>(null);
  const [viewMode, setViewMode] = useState<'hierarchy' | 'company'>('hierarchy');

  useEffect(() => {
    buildProfessionalNetwork();
  }, [contactId, relationships, contacts]);

  const buildProfessionalNetwork = () => {
    // Filter professional relationships only
    const professionalRelationships = relationships.filter(rel => 
      rel.relationship_category === 'professional'
    );

    if (professionalRelationships.length === 0) {
      setProfessionalData([]);
      return;
    }

    const nodes: ProfessionalNode[] = [];
    
    // Add root contact
    const rootContact = contacts.find(c => c.id === contactId);
    if (rootContact) {
      nodes.push({
        id: contactId,
        name: `${rootContact.first_name} ${rootContact.last_name || ''}`.trim(),
        company: (rootContact as any).company || 'Current Company',
        position: (rootContact as any).position || 'Your Position',
        relationship: 'self',
        level: 0,
        strength: 10,
        isRoot: true
      });
    }

    // Add professional contacts
    professionalRelationships.forEach(rel => {
      const relatedId = rel.contact_a_id === contactId ? rel.contact_b_id : rel.contact_a_id;
      const relatedContact = contacts.find(c => c.id === relatedId);
      
      if (relatedContact) {
        const level = getProfessionalLevel(rel.relationship_type);
        nodes.push({
          id: relatedId,
          name: `${relatedContact.first_name} ${relatedContact.last_name || ''}`.trim(),
          company: (relatedContact as any).company || 'Unknown Company',
          position: (relatedContact as any).position || 'Unknown Position',
          relationship: rel.relationship_type,
          level,
          strength: rel.relationship_strength || 5,
          isRoot: false
        });
      }
    });

    // Group by company
    const companyGroups = groupByCompany(nodes);
    setProfessionalData(companyGroups);
  };

  const getProfessionalLevel = (relationshipType: string): number => {
    const levelMap: Record<string, number> = {
      'manager': -1,
      'employee': 1,
      'colleague': 2,
      'client': 3,
      'service_provider': 3
    };
    
    return levelMap[relationshipType] || 2;
  };

  const groupByCompany = (nodes: ProfessionalNode[]): CompanyGroup[] => {
    const groups = new Map<string, ProfessionalNode[]>();
    
    nodes.forEach(node => {
      const company = node.company || 'Unknown Company';
      if (!groups.has(company)) {
        groups.set(company, []);
      }
      groups.get(company)?.push(node);
    });

    return Array.from(groups.entries()).map(([company, nodes]) => ({
      company,
      nodes: nodes.sort((a, b) => a.level - b.level)
    }));
  };

  const getRelationshipIcon = (relationship: string) => {
    const iconMap: Record<string, string> = {
      'manager': '👔',
      'employee': '👨‍💼',
      'colleague': '🤝',
      'client': '🤝',
      'service_provider': '⚙️',
      'self': '🎯'
    };
    
    return iconMap[relationship] || '👤';
  };

  const getRelationshipColor = (relationship: string) => {
    const colorMap: Record<string, string> = {
      'manager': 'bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-400',
      'employee': 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400',
      'colleague': 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400',
      'client': 'bg-orange-100 text-orange-800 dark:bg-orange-900/20 dark:text-orange-400',
      'service_provider': 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400',
      'self': 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900/20 dark:text-indigo-400'
    };
    
    return colorMap[relationship] || 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400';
  };

  const renderHierarchyView = () => {
    // Group nodes by level for hierarchy view
    const levels = new Map<number, ProfessionalNode[]>();
    
    professionalData.forEach(group => {
      group.nodes.forEach(node => {
        if (!levels.has(node.level)) {
          levels.set(node.level, []);
        }
        levels.get(node.level)?.push(node);
      });
    });

    const sortedLevels = Array.from(levels.entries()).sort(([a], [b]) => a - b);

    return (
      <div className="space-y-6">
        {sortedLevels.map(([level, nodes]) => (
          <div key={level} className="space-y-2">
            <h4 className="text-sm font-medium text-gray-600 dark:text-gray-400">
              {level === 0 ? 'You' :
               level === -1 ? 'Management' :
               level === 1 ? 'Direct Reports' :
               level === 2 ? 'Colleagues' :
               'External Contacts'}
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {nodes.map(node => renderProfessionalCard(node))}
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderCompanyView = () => {
    return (
      <div className="space-y-6">
        {professionalData.map(group => (
          <div key={group.company} className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
            <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
              <span className="mr-2">🏢</span>
              {group.company}
              <span className="ml-2 text-sm font-normal text-gray-500">
                ({group.nodes.length} contacts)
              </span>
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {group.nodes.map(node => renderProfessionalCard(node))}
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderProfessionalCard = (node: ProfessionalNode) => {
    return (
      <div
        key={node.id}
        className={`p-4 rounded-lg border-2 cursor-pointer transition-all duration-200 ${
          node.isRoot 
            ? 'bg-indigo-50 border-indigo-200 dark:bg-indigo-900/20 dark:border-indigo-800' 
            : 'bg-white border-gray-200 dark:bg-gray-700 dark:border-gray-600'
        } ${
          selectedNode === node.id 
            ? 'ring-2 ring-blue-500 border-blue-500' 
            : 'hover:border-gray-300 dark:hover:border-gray-500'
        }`}
        onClick={() => {
          setSelectedNode(node.id);
          if (!node.isRoot) {
            onContactClick?.(node.id);
          }
        }}
      >
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              <span className="text-lg">{getRelationshipIcon(node.relationship)}</span>
              <h5 className="font-medium text-gray-900 dark:text-white truncate">
                {node.name}
              </h5>
            </div>
            
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
              {node.position}
            </p>
            
            <p className="text-xs text-gray-500 dark:text-gray-500 mb-2">
              {node.company}
            </p>
            
            <div className="flex items-center justify-between">
              <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getRelationshipColor(node.relationship)}`}>
                {node.relationship.replace('_', ' ')}
              </span>
              
              {!node.isRoot && (
                <div className="flex items-center space-x-1">
                  <div className="w-12 h-1.5 bg-gray-200 rounded-full">
                    <div
                      className={`h-1.5 rounded-full ${
                        node.strength >= 8 ? 'bg-green-500' :
                        node.strength >= 6 ? 'bg-yellow-500' :
                        node.strength >= 4 ? 'bg-orange-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${(node.strength / 10) * 100}%` }}
                    />
                  </div>
                  <span className="text-xs text-gray-500">
                    {node.strength}/10
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  };

  if (professionalData.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 bg-gray-50 dark:bg-gray-800 rounded-lg">
        <div className="text-center">
          <div className="text-4xl mb-2">💼</div>
          <p className="text-gray-600 dark:text-gray-400">No professional relationships found</p>
          <p className="text-sm text-gray-500 dark:text-gray-500 mt-1">
            Add colleagues, managers, or clients to see the professional network
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
            <span className="mr-2">🏢</span>
            Professional Network
          </h3>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setViewMode('hierarchy')}
              className={`px-3 py-1 text-sm font-medium rounded-md ${
                viewMode === 'hierarchy'
                  ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400'
                  : 'text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-200'
              }`}
            >
              Hierarchy
            </button>
            <button
              onClick={() => setViewMode('company')}
              className={`px-3 py-1 text-sm font-medium rounded-md ${
                viewMode === 'company'
                  ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400'
                  : 'text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-200'
              }`}
            >
              By Company
            </button>
          </div>
        </div>
      </div>
      
      <div className="p-4">
        {viewMode === 'hierarchy' ? renderHierarchyView() : renderCompanyView()}
      </div>
      
      {selectedNode && (
        <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border-t border-gray-200 dark:border-gray-700">
          <p className="text-sm text-blue-800 dark:text-blue-200">
            <strong>Selected:</strong> {professionalData.flatMap(g => g.nodes).find(n => n.id === selectedNode)?.name}
          </p>
          <p className="text-xs text-blue-600 dark:text-blue-300 mt-1">
            Click to view detailed contact information
          </p>
        </div>
      )}
    </div>
  );
};

export default ProfessionalNetwork;