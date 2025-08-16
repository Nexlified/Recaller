import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Contact } from '../../services/contacts';
import contactRelationshipService from '../../services/contactRelationships';
import contactsService from '../../services/contacts';

interface NetworkNode {
  id: number;
  name: string;
  x: number;
  y: number;
  relationships: number;
  isCenter?: boolean;
}

interface NetworkEdge {
  from: number;
  to: number;
  relationshipType: string;
  strength?: number;
}

interface RelationshipNetworkProps {
  contactId: number;
  width?: number;
  height?: number;
}

export const RelationshipNetwork: React.FC<RelationshipNetworkProps> = ({
  contactId,
  width = 600,
  height = 400
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [nodes, setNodes] = useState<NetworkNode[]>([]);
  const [edges, setEdges] = useState<NetworkEdge[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState<NetworkNode | null>(null);

  useEffect(() => {
    loadNetworkData();
  }, [loadNetworkData]);

  const loadNetworkData = useCallback(async () => {
    try {
      setIsLoading(true);
      const [relationships, allContacts] = await Promise.all([
        contactRelationshipService.getContactRelationships(contactId),
        contactsService.getContacts()
      ]);

      // Build network from relationships
      const nodeMap = new Map<number, NetworkNode>();
      const edgeList: NetworkEdge[] = [];
      
      // Add center node (current contact)
      const centerContact = allContacts.find(c => c.id === contactId);
      if (centerContact) {
        nodeMap.set(contactId, {
          id: contactId,
          name: `${centerContact.first_name} ${centerContact.last_name || ''}`.trim(),
          x: width / 2,
          y: height / 2,
          relationships: relationships.length,
          isCenter: true
        });
      }

      // Add connected nodes and edges
      relationships.forEach((rel) => {
        const otherContactId = rel.contact_a_id === contactId ? rel.contact_b_id : rel.contact_a_id;
        const otherContact = allContacts.find(c => c.id === otherContactId);
        
        if (otherContact && !nodeMap.has(otherContactId)) {
          // Calculate position in circle around center
          const angle = (nodeMap.size - 1) * (2 * Math.PI) / Math.max(relationships.length, 1);
          const radius = Math.min(width, height) * 0.3;
          
          nodeMap.set(otherContactId, {
            id: otherContactId,
            name: `${otherContact.first_name} ${otherContact.last_name || ''}`.trim(),
            x: width / 2 + radius * Math.cos(angle),
            y: height / 2 + radius * Math.sin(angle),
            relationships: 1 // We only know about relationship to center
          });
        }

        edgeList.push({
          from: contactId,
          to: otherContactId,
          relationshipType: rel.relationship_type,
          strength: rel.relationship_strength
        });
      });

      setNodes(Array.from(nodeMap.values()));
      setEdges(edgeList);
    } catch (error) {
      console.error('Error loading network data:', error);
    } finally {
      setIsLoading(false);
    }
  }, [contactId, width, height]);

  const getNodeColor = (node: NetworkNode) => {
    if (node.isCenter) return '#3B82F6'; // Blue for center
    if (node.relationships >= 5) return '#10B981'; // Green for well-connected
    if (node.relationships >= 2) return '#F59E0B'; // Orange for moderately connected
    return '#6B7280'; // Gray for less connected
  };

  const getEdgeColor = (edge: NetworkEdge) => {
    if (!edge.strength) return '#9CA3AF';
    if (edge.strength >= 8) return '#10B981'; // Strong relationship
    if (edge.strength >= 6) return '#F59E0B'; // Medium relationship
    return '#EF4444'; // Weak relationship
  };

  const getEdgeWidth = (edge: NetworkEdge) => {
    if (!edge.strength) return 1;
    return Math.max(1, edge.strength / 3);
  };

  const handleNodeClick = (node: NetworkNode) => {
    setSelectedNode(node);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64 bg-gray-50 dark:bg-gray-800 rounded-lg">
        <div className="text-gray-600 dark:text-gray-400">Loading network...</div>
      </div>
    );
  }

  if (nodes.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 bg-gray-50 dark:bg-gray-800 rounded-lg">
        <div className="text-center">
          <div className="text-gray-600 dark:text-gray-400 mb-2">No relationships to visualize</div>
          <div className="text-sm text-gray-500 dark:text-gray-500">
            Add some relationships to see the network
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Relationship Network
        </h3>
        
        <div className="relative">
          <svg
            ref={svgRef}
            width={width}
            height={height}
            className="border border-gray-200 dark:border-gray-700 rounded bg-gray-50 dark:bg-gray-900"
          >
            {/* Render edges first (so they appear behind nodes) */}
            {edges.map((edge, index) => {
              const fromNode = nodes.find(n => n.id === edge.from);
              const toNode = nodes.find(n => n.id === edge.to);
              
              if (!fromNode || !toNode) return null;
              
              return (
                <line
                  key={index}
                  x1={fromNode.x}
                  y1={fromNode.y}
                  x2={toNode.x}
                  y2={toNode.y}
                  stroke={getEdgeColor(edge)}
                  strokeWidth={getEdgeWidth(edge)}
                  className="transition-all duration-200"
                />
              );
            })}
            
            {/* Render nodes */}
            {nodes.map((node) => (
              <g key={node.id}>
                <circle
                  cx={node.x}
                  cy={node.y}
                  r={node.isCenter ? 20 : 15}
                  fill={getNodeColor(node)}
                  stroke="#fff"
                  strokeWidth="2"
                  className="cursor-pointer transition-all duration-200 hover:stroke-4"
                  onClick={() => handleNodeClick(node)}
                />
                <text
                  x={node.x}
                  y={node.y + (node.isCenter ? 35 : 30)}
                  textAnchor="middle"
                  className="fill-current text-xs text-gray-700 dark:text-gray-300 pointer-events-none"
                  style={{ fontSize: '12px' }}
                >
                  {node.name.length > 15 ? `${node.name.substring(0, 12)}...` : node.name}
                </text>
              </g>
            ))}
          </svg>
          
          {/* Legend */}
          <div className="absolute bottom-2 left-2 bg-white dark:bg-gray-700 p-2 rounded shadow-sm border">
            <div className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                <span>Current Contact</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 rounded-full bg-green-500"></div>
                <span>Strong Relationship (8-10)</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                <span>Medium Relationship (6-7)</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 rounded-full bg-red-500"></div>
                <span>Weak Relationship (1-5)</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Selected node details */}
      {selectedNode && (
        <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border border-blue-200 dark:border-blue-700">
          <h4 className="font-medium text-blue-900 dark:text-blue-100">
            {selectedNode.name}
          </h4>
          <div className="mt-2 text-sm text-blue-700 dark:text-blue-300">
            <div>Relationships: {selectedNode.relationships}</div>
            {selectedNode.isCenter && <div>This is the center contact</div>}
            
            {/* Show relationships for this node */}
            <div className="mt-2">
              <div className="font-medium">Connected to:</div>
              {edges
                .filter(e => e.from === selectedNode.id || e.to === selectedNode.id)
                .map((edge, index) => {
                  const otherNodeId = edge.from === selectedNode.id ? edge.to : edge.from;
                  const otherNode = nodes.find(n => n.id === otherNodeId);
                  return (
                    <div key={index} className="text-xs">
                      {otherNode?.name} ({edge.relationshipType}
                      {edge.strength && ` - Strength: ${edge.strength}/10`})
                    </div>
                  );
                })}
            </div>
          </div>
        </div>
      )}
      
      {/* Network statistics */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white dark:bg-gray-800 p-3 rounded-lg border border-gray-200 dark:border-gray-700 text-center">
          <div className="text-2xl font-bold text-gray-900 dark:text-white">{nodes.length - 1}</div>
          <div className="text-sm text-gray-600 dark:text-gray-400">Connected People</div>
        </div>
        <div className="bg-white dark:bg-gray-800 p-3 rounded-lg border border-gray-200 dark:border-gray-700 text-center">
          <div className="text-2xl font-bold text-gray-900 dark:text-white">{edges.length}</div>
          <div className="text-sm text-gray-600 dark:text-gray-400">Total Relationships</div>
        </div>
        <div className="bg-white dark:bg-gray-800 p-3 rounded-lg border border-gray-200 dark:border-gray-700 text-center">
          <div className="text-2xl font-bold text-gray-900 dark:text-white">
            {edges.length > 0 ? Math.round(edges.reduce((sum, e) => sum + (e.strength || 0), 0) / edges.length) : 0}
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400">Avg. Strength</div>
        </div>
      </div>
    </div>
  );
};