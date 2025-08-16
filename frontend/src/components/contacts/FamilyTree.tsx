import React, { useEffect, useRef, useState } from 'react';
import { ContactRelationship } from '../../types/ContactRelationship';
import { Contact } from '../../services/contacts';
import relationshipService, { NetworkData, NetworkNode, NetworkEdge } from '../../services/relationships';

interface FamilyTreeProps {
  contactId: number;
  relationships: ContactRelationship[];
  contacts: Contact[];
  onContactClick?: (contactId: number) => void;
}

interface FamilyTreeNode extends NetworkNode {
  x?: number;
  y?: number;
  level?: number;
  generation?: number;
  isRoot?: boolean;
  children?: FamilyTreeNode[];
  parents?: FamilyTreeNode[];
}

export const FamilyTree: React.FC<FamilyTreeProps> = ({
  contactId,
  relationships,
  contacts,
  onContactClick
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [familyData, setFamilyData] = useState<FamilyTreeNode[]>([]);
  const [selectedNode, setSelectedNode] = useState<number | null>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });

  useEffect(() => {
    buildFamilyTree();
  }, [contactId, relationships, contacts]);

  useEffect(() => {
    if (familyData.length > 0) {
      renderTree();
    }
  }, [familyData, dimensions]);

  const buildFamilyTree = () => {
    // Filter family relationships only
    const familyRelationships = relationships.filter(rel => 
      rel.relationship_category === 'family'
    );

    if (familyRelationships.length === 0) {
      setFamilyData([]);
      return;
    }

    // Create nodes map
    const nodesMap = new Map<number, FamilyTreeNode>();
    
    // Add root contact
    const rootContact = contacts.find(c => c.id === contactId);
    if (rootContact) {
      nodesMap.set(contactId, {
        id: contactId,
        name: `${rootContact.first_name} ${rootContact.last_name || ''}`.trim(),
        category: 'family',
        isRoot: true,
        generation: 0,
        children: [],
        parents: []
      });
    }

    // Add related contacts
    familyRelationships.forEach(rel => {
      const relatedId = rel.contact_a_id === contactId ? rel.contact_b_id : rel.contact_a_id;
      const relatedContact = contacts.find(c => c.id === relatedId);
      
      if (relatedContact && !nodesMap.has(relatedId)) {
        const generation = getGeneration(rel.relationship_type);
        nodesMap.set(relatedId, {
          id: relatedId,
          name: `${relatedContact.first_name} ${relatedContact.last_name || ''}`.trim(),
          category: 'family',
          generation,
          children: [],
          parents: []
        });
      }
    });

    // Build family relationships
    familyRelationships.forEach(rel => {
      const nodeA = nodesMap.get(rel.contact_a_id);
      const nodeB = nodesMap.get(rel.contact_b_id);
      
      if (nodeA && nodeB) {
        // Determine parent-child relationships
        if (isParentRelationship(rel.relationship_type)) {
          const parent = rel.contact_a_id === contactId ? nodeA : nodeB;
          const child = rel.contact_a_id === contactId ? nodeB : nodeA;
          
          parent.children?.push(child);
          child.parents?.push(parent);
        }
      }
    });

    // Calculate positions
    const nodes = Array.from(nodesMap.values());
    layoutNodes(nodes);
    setFamilyData(nodes);
  };

  const getGeneration = (relationshipType: string): number => {
    // Map relationship types to generation levels relative to root (0)
    const generationMap: Record<string, number> = {
      'grandparent': -2,
      'parent': -1,
      'sibling': 0,
      'brother': 0,
      'sister': 0,
      'child': 1,
      'grandchild': 2,
      'uncle': -1,
      'aunt': -1,
      'cousin': 0,
      'nephew': 1,
      'niece': 1
    };
    
    return generationMap[relationshipType] || 0;
  };

  const isParentRelationship = (relationshipType: string): boolean => {
    return ['parent', 'child', 'grandparent', 'grandchild'].includes(relationshipType);
  };

  const layoutNodes = (nodes: FamilyTreeNode[]) => {
    const generations = new Map<number, FamilyTreeNode[]>();
    
    // Group by generation
    nodes.forEach(node => {
      const gen = node.generation || 0;
      if (!generations.has(gen)) {
        generations.set(gen, []);
      }
      generations.get(gen)?.push(node);
    });

    // Calculate positions
    const levelHeight = 120;
    const nodeWidth = 140;
    const centerY = dimensions.height / 2;
    
    generations.forEach((nodesInGen, generation) => {
      const y = centerY + (generation * levelHeight);
      const totalWidth = nodesInGen.length * nodeWidth;
      const startX = (dimensions.width - totalWidth) / 2;
      
      nodesInGen.forEach((node, index) => {
        node.x = startX + (index * nodeWidth) + nodeWidth / 2;
        node.y = y;
      });
    });
  };

  const renderTree = () => {
    if (!svgRef.current || familyData.length === 0) return;

    const svg = svgRef.current;
    
    // Clear existing content
    while (svg.firstChild) {
      svg.removeChild(svg.firstChild);
    }

    // Create group for zoom/pan
    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    svg.appendChild(g);

    // Draw connections
    familyData.forEach(node => {
      node.children?.forEach(child => {
        if (node.x && node.y && child.x && child.y) {
          const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
          line.setAttribute('x1', node.x.toString());
          line.setAttribute('y1', (node.y + 30).toString()); // Offset for node height
          line.setAttribute('x2', child.x.toString());
          line.setAttribute('y2', (child.y - 30).toString());
          line.setAttribute('stroke', '#6B7280');
          line.setAttribute('stroke-width', '2');
          g.appendChild(line);
        }
      });
    });

    // Draw nodes
    familyData.forEach(node => {
      if (!node.x || !node.y) return;

      // Node group
      const nodeGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      nodeGroup.setAttribute('transform', `translate(${node.x},${node.y})`);
      nodeGroup.style.cursor = 'pointer';
      
      // Node background
      const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
      rect.setAttribute('x', '-60');
      rect.setAttribute('y', '-25');
      rect.setAttribute('width', '120');
      rect.setAttribute('height', '50');
      rect.setAttribute('rx', '8');
      rect.setAttribute('fill', node.isRoot ? '#3B82F6' : '#E5E7EB');
      rect.setAttribute('stroke', selectedNode === node.id ? '#F59E0B' : '#9CA3AF');
      rect.setAttribute('stroke-width', selectedNode === node.id ? '3' : '1');
      nodeGroup.appendChild(rect);

      // Node text
      const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      text.setAttribute('text-anchor', 'middle');
      text.setAttribute('dominant-baseline', 'middle');
      text.setAttribute('fill', node.isRoot ? 'white' : '#374151');
      text.setAttribute('font-size', '12');
      text.setAttribute('font-weight', node.isRoot ? 'bold' : 'normal');
      text.textContent = node.name.length > 15 ? node.name.substring(0, 15) + '...' : node.name;
      nodeGroup.appendChild(text);

      // Click handler
      nodeGroup.addEventListener('click', () => {
        setSelectedNode(node.id);
        onContactClick?.(node.id);
      });

      g.appendChild(nodeGroup);
    });
  };

  const handleResize = () => {
    if (svgRef.current) {
      const container = svgRef.current.parentElement;
      if (container) {
        setDimensions({
          width: container.clientWidth,
          height: Math.max(400, container.clientHeight)
        });
      }
    }
  };

  useEffect(() => {
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  if (familyData.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 bg-gray-50 dark:bg-gray-800 rounded-lg">
        <div className="text-center">
          <div className="text-4xl mb-2">👨‍👩‍👧‍👦</div>
          <p className="text-gray-600 dark:text-gray-400">No family relationships found</p>
          <p className="text-sm text-gray-500 dark:text-gray-500 mt-1">
            Add family members to see the family tree
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
            <span className="mr-2">🌳</span>
            Family Tree
          </h3>
          <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
            <div className="flex items-center">
              <div className="w-3 h-3 bg-blue-500 rounded mr-1"></div>
              <span>Current Contact</span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 bg-gray-300 rounded mr-1"></div>
              <span>Family Member</span>
            </div>
          </div>
        </div>
      </div>
      
      <div className="p-4" style={{ height: '500px', overflow: 'auto' }}>
        <svg
          ref={svgRef}
          width={dimensions.width}
          height={dimensions.height}
          className="border border-gray-100 dark:border-gray-800 rounded"
        />
      </div>
      
      {selectedNode && (
        <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border-t border-gray-200 dark:border-gray-700">
          <p className="text-sm text-blue-800 dark:text-blue-200">
            <strong>Selected:</strong> {familyData.find(n => n.id === selectedNode)?.name}
          </p>
          <p className="text-xs text-blue-600 dark:text-blue-300 mt-1">
            Click to view detailed contact information
          </p>
        </div>
      )}
    </div>
  );
};

export default FamilyTree;