import React, { useEffect, useRef, useState, useCallback } from 'react';
import { ContactRelationship } from '../../types/ContactRelationship';
import { Contact } from '../../services/contacts';
import { NetworkNode, NetworkEdge } from '../../services/relationships';

interface SocialNetworkProps {
  contactId: number;
  relationships: ContactRelationship[];
  contacts: Contact[];
  onContactClick?: (contactId: number) => void;
}

interface NetworkGraphNode extends NetworkNode {
  x: number;
  y: number;
  vx?: number;
  vy?: number;
  radius: number;
  isSelected?: boolean;
  isHovered?: boolean;
}

interface NetworkGraphEdge extends NetworkEdge {
  sourceNode?: NetworkGraphNode;
  targetNode?: NetworkGraphNode;
}

export const SocialNetwork: React.FC<SocialNetworkProps> = ({
  contactId,
  relationships,
  contacts,
  onContactClick
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [networkData, setNetworkData] = useState<{
    nodes: NetworkGraphNode[];
    edges: NetworkGraphEdge[];
  }>({ nodes: [], edges: [] });
  const [selectedNode, setSelectedNode] = useState<number | null>(contactId);
  const [hoveredNode, setHoveredNode] = useState<number | null>(null);
  const [filterCategory, setFilterCategory] = useState<string>('all');
  const [animationId, setAnimationId] = useState<number | null>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragNode, setDragNode] = useState<NetworkGraphNode | null>(null);

  useEffect(() => {
    buildNetworkGraph();
  }, [contactId, relationships, contacts, filterCategory]);

  useEffect(() => {
    if (networkData.nodes.length > 0) {
      startSimulation();
    }
    return () => {
      if (animationId) {
        cancelAnimationFrame(animationId);
      }
    };
  }, [networkData]);

  const buildNetworkGraph = useCallback(() => {
    // Filter relationships by category if needed
    const filteredRelationships = filterCategory === 'all' 
      ? relationships 
      : relationships.filter(rel => rel.relationship_category === filterCategory);

    if (filteredRelationships.length === 0) {
      setNetworkData({ nodes: [], edges: [] });
      return;
    }

    const nodeMap = new Map<number, NetworkGraphNode>();
    const edges: NetworkGraphEdge[] = [];

    // Add root contact
    const rootContact = contacts.find(c => c.id === contactId);
    if (rootContact) {
      nodeMap.set(contactId, {
        id: contactId,
        name: `${rootContact.first_name} ${rootContact.last_name || ''}`.trim(),
        category: 'root',
        x: dimensions.width / 2,
        y: dimensions.height / 2,
        radius: 25,
        isSelected: selectedNode === contactId
      });
    }

    // Add related contacts
    filteredRelationships.forEach(rel => {
      const relatedId = rel.contact_a_id === contactId ? rel.contact_b_id : rel.contact_a_id;
      const relatedContact = contacts.find(c => c.id === relatedId);
      
      if (relatedContact && !nodeMap.has(relatedId)) {
        const radius = Math.max(8, Math.min(20, (rel.relationship_strength || 5) * 2));
        nodeMap.set(relatedId, {
          id: relatedId,
          name: `${relatedContact.first_name} ${relatedContact.last_name || ''}`.trim(),
          category: rel.relationship_category,
          strength: rel.relationship_strength,
          x: Math.random() * dimensions.width,
          y: Math.random() * dimensions.height,
          radius,
          isSelected: selectedNode === relatedId,
          isHovered: hoveredNode === relatedId
        });
      }

      // Add edge
      const sourceNode = nodeMap.get(rel.contact_a_id);
      const targetNode = nodeMap.get(rel.contact_b_id);
      
      if (sourceNode && targetNode) {
        edges.push({
          source: rel.contact_a_id,
          target: rel.contact_b_id,
          relationship: rel.relationship_type,
          strength: rel.relationship_strength || 5,
          category: rel.relationship_category,
          status: rel.relationship_status,
          mutual: rel.is_mutual,
          sourceNode,
          targetNode
        });
      }
    });

    setNetworkData({
      nodes: Array.from(nodeMap.values()),
      edges
    });
  }, [contactId, relationships, contacts, filterCategory, selectedNode, hoveredNode, dimensions]);

  const startSimulation = () => {
    if (!canvasRef.current || networkData.nodes.length === 0) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Simple force simulation
    const simulate = () => {
      // Apply forces
      networkData.nodes.forEach(node => {
        // Initialize velocities
        if (node.vx === undefined) node.vx = 0;
        if (node.vy === undefined) node.vy = 0;

        // Center force (attract to center)
        const centerX = dimensions.width / 2;
        const centerY = dimensions.height / 2;
        const centerForce = 0.01;
        node.vx += (centerX - node.x) * centerForce;
        node.vy += (centerY - node.y) * centerForce;

        // Repulsion between nodes
        networkData.nodes.forEach(otherNode => {
          if (node !== otherNode) {
            const dx = node.x - otherNode.x;
            const dy = node.y - otherNode.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            if (distance < 100 && distance > 0) {
              const force = 500 / (distance * distance);
              node.vx += (dx / distance) * force;
              node.vy += (dy / distance) * force;
            }
          }
        });

        // Link forces
        networkData.edges.forEach(edge => {
          if (edge.source === node.id || edge.target === node.id) {
            const otherNodeId = edge.source === node.id ? edge.target : edge.source;
            const otherNode = networkData.nodes.find(n => n.id === otherNodeId);
            if (otherNode) {
              const dx = otherNode.x - node.x;
              const dy = otherNode.y - node.y;
              const distance = Math.sqrt(dx * dx + dy * dy);
              const targetDistance = 80;
              const force = (distance - targetDistance) * 0.1;
              if (distance > 0) {
                node.vx += (dx / distance) * force;
                node.vy += (dy / distance) * force;
              }
            }
          }
        });

        // Apply velocities with damping
        node.vx *= 0.9;
        node.vy *= 0.9;
        
        if (!dragNode || dragNode.id !== node.id) {
          node.x += node.vx;
          node.y += node.vy;

          // Keep nodes within bounds
          node.x = Math.max(node.radius, Math.min(dimensions.width - node.radius, node.x));
          node.y = Math.max(node.radius, Math.min(dimensions.height - node.radius, node.y));
        }
      });

      // Render
      renderNetwork(ctx);

      // Continue simulation
      const id = requestAnimationFrame(simulate);
      setAnimationId(id);
    };

    simulate();
  };

  const renderNetwork = (ctx: CanvasRenderingContext2D) => {
    // Clear canvas
    ctx.clearRect(0, 0, dimensions.width, dimensions.height);

    // Apply zoom and pan
    ctx.save();
    ctx.translate(pan.x, pan.y);
    ctx.scale(zoom, zoom);

    // Draw edges
    networkData.edges.forEach(edge => {
      if (edge.sourceNode && edge.targetNode) {
        ctx.beginPath();
        ctx.moveTo(edge.sourceNode.x, edge.sourceNode.y);
        ctx.lineTo(edge.targetNode.x, edge.targetNode.y);
        
        // Style based on relationship strength
        const alpha = Math.max(0.2, (edge.strength / 10));
        ctx.strokeStyle = getCategoryColor(edge.category, alpha);
        ctx.lineWidth = Math.max(1, edge.strength / 3);
        ctx.stroke();
      }
    });

    // Draw nodes
    networkData.nodes.forEach(node => {
      ctx.beginPath();
      ctx.arc(node.x, node.y, node.radius, 0, 2 * Math.PI);
      
      // Fill color based on category
      if (node.id === contactId) {
        ctx.fillStyle = '#3B82F6'; // Blue for root
      } else {
        ctx.fillStyle = getCategoryColor(node.category);
      }
      
      ctx.fill();

      // Outline
      ctx.lineWidth = node.isSelected ? 4 : node.isHovered ? 2 : 1;
      ctx.strokeStyle = node.isSelected ? '#F59E0B' : node.isHovered ? '#6B7280' : '#374151';
      ctx.stroke();

      // Label
      if (node.radius > 12 || node.isHovered || node.isSelected) {
        ctx.fillStyle = '#374151';
        ctx.font = '12px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(
          node.name.length > 15 ? node.name.substring(0, 15) + '...' : node.name,
          node.x,
          node.y - node.radius - 5
        );
      }
    });

    ctx.restore();
  };

  const getCategoryColor = (category: string, alpha = 1) => {
    const colors = {
      family: `rgba(59, 130, 246, ${alpha})`, // Blue
      professional: `rgba(16, 185, 129, ${alpha})`, // Green
      social: `rgba(245, 158, 11, ${alpha})`, // Orange
      romantic: `rgba(239, 68, 68, ${alpha})`, // Red
      root: `rgba(59, 130, 246, ${alpha})` // Blue
    };
    return colors[category as keyof typeof colors] || `rgba(156, 163, 175, ${alpha})`;
  };

  const getNodeAtPosition = (x: number, y: number): NetworkGraphNode | null => {
    // Adjust for zoom and pan
    const adjustedX = (x - pan.x) / zoom;
    const adjustedY = (y - pan.y) / zoom;
    
    return networkData.nodes.find(node => {
      const dx = adjustedX - node.x;
      const dy = adjustedY - node.y;
      const distance = Math.sqrt(dx * dx + dy * dy);
      return distance <= node.radius;
    }) || null;
  };

  const handleMouseMove = (event: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    if (isDragging && dragNode) {
      const adjustedX = (x - pan.x) / zoom;
      const adjustedY = (y - pan.y) / zoom;
      dragNode.x = adjustedX;
      dragNode.y = adjustedY;
      dragNode.vx = 0;
      dragNode.vy = 0;
      return;
    }

    const node = getNodeAtPosition(x, y);
    setHoveredNode(node?.id || null);
    
    // Update cursor
    canvas.style.cursor = node ? 'pointer' : 'default';
  };

  const handleMouseDown = (event: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    const node = getNodeAtPosition(x, y);
    if (node) {
      setDragNode(node);
      setIsDragging(true);
      setSelectedNode(node.id);
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
    setDragNode(null);
  };

  const handleClick = (event: React.MouseEvent<HTMLCanvasElement>) => {
    if (isDragging) return;
    
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    const node = getNodeAtPosition(x, y);
    if (node && node.id !== contactId) {
      onContactClick?.(node.id);
    }
  };

  const handleResize = useCallback(() => {
    if (canvasRef.current) {
      const container = canvasRef.current.parentElement;
      if (container) {
        const newDimensions = {
          width: container.clientWidth,
          height: Math.max(400, container.clientHeight)
        };
        setDimensions(newDimensions);
        
        // Update canvas size
        canvasRef.current.width = newDimensions.width;
        canvasRef.current.height = newDimensions.height;
      }
    }
  }, []);

  useEffect(() => {
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [handleResize]);

  const categories = ['all', 'family', 'professional', 'social', 'romantic'];

  if (networkData.nodes.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 bg-gray-50 dark:bg-gray-800 rounded-lg">
        <div className="text-center">
          <div className="text-4xl mb-2">🕸️</div>
          <p className="text-gray-600 dark:text-gray-400">
            {filterCategory === 'all' 
              ? 'No relationships found' 
              : `No ${filterCategory} relationships found`}
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-500 mt-1">
            {filterCategory !== 'all' ? 'Try changing the filter' : 'Add relationships to see the social network'}
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
            <span className="mr-2">🕸️</span>
            Social Network
          </h3>
          
          <div className="flex items-center space-x-4">
            {/* Category filter */}
            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="text-sm border border-gray-300 dark:border-gray-600 rounded-md px-2 py-1 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              {categories.map(category => (
                <option key={category} value={category}>
                  {category === 'all' ? 'All Categories' : category.charAt(0).toUpperCase() + category.slice(1)}
                </option>
              ))}
            </select>

            {/* Zoom controls */}
            <div className="flex items-center space-x-1">
              <button
                onClick={() => setZoom(Math.max(0.5, zoom - 0.1))}
                className="px-2 py-1 text-sm bg-gray-100 dark:bg-gray-700 rounded hover:bg-gray-200 dark:hover:bg-gray-600"
              >
                −
              </button>
              <span className="text-sm text-gray-600 dark:text-gray-400 min-w-[3rem] text-center">
                {Math.round(zoom * 100)}%
              </span>
              <button
                onClick={() => setZoom(Math.min(2, zoom + 0.1))}
                className="px-2 py-1 text-sm bg-gray-100 dark:bg-gray-700 rounded hover:bg-gray-200 dark:hover:bg-gray-600"
              >
                +
              </button>
            </div>
          </div>
        </div>
        
        {/* Legend */}
        <div className="flex items-center space-x-4 mt-2 text-sm text-gray-600 dark:text-gray-400">
          <div className="flex items-center">
            <div className="w-3 h-3 bg-blue-500 rounded-full mr-1"></div>
            <span>You</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-blue-400 rounded-full mr-1"></div>
            <span>Family</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-green-400 rounded-full mr-1"></div>
            <span>Professional</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-orange-400 rounded-full mr-1"></div>
            <span>Social</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-red-400 rounded-full mr-1"></div>
            <span>Romantic</span>
          </div>
        </div>
      </div>
      
      <div className="p-4" style={{ height: '500px', overflow: 'hidden' }}>
        <canvas
          ref={canvasRef}
          width={dimensions.width}
          height={dimensions.height}
          className="border border-gray-100 dark:border-gray-800 rounded cursor-default"
          onMouseMove={handleMouseMove}
          onMouseDown={handleMouseDown}
          onMouseUp={handleMouseUp}
          onClick={handleClick}
        />
      </div>
      
      {selectedNode && (
        <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border-t border-gray-200 dark:border-gray-700">
          <p className="text-sm text-blue-800 dark:text-blue-200">
            <strong>Selected:</strong> {networkData.nodes.find(n => n.id === selectedNode)?.name}
          </p>
          <p className="text-xs text-blue-600 dark:text-blue-300 mt-1">
            Drag to move • Click to view details • Use zoom controls to navigate
          </p>
        </div>
      )}
    </div>
  );
};

export default SocialNetwork;