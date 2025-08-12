"""Generate TypeScript types from configuration files."""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Set


class TypeScriptGenerator:
    """Generate TypeScript types from YAML configuration files."""
    
    def __init__(self, config_path: Path, output_path: Path):
        self.config_path = config_path
        self.output_path = output_path
        self.types: Dict[str, Any] = {}
        self.enums: Dict[str, List[str]] = {}
        
    def generate_all_types(self):
        """Generate all TypeScript types from configuration files."""
        # Process all YAML files
        for yaml_file in self.config_path.rglob("*.yml"):
            self._process_config_file(yaml_file)
        
        # Generate TypeScript files
        self._generate_enums_file()
        self._generate_interfaces_file()
        self._generate_config_client_file()
        
        print(f"✅ TypeScript types generated in {self.output_path}")
    
    def _process_config_file(self, file_path: Path):
        """Process a single YAML configuration file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            category = config_data.get('category')
            type_key = config_data.get('type')
            values = config_data.get('values', [])
            
            if not category or not type_key:
                return
            
            # Generate enum for simple values
            enum_name = self._get_enum_name(category, type_key)
            enum_values = []
            
            for value in values:
                if 'key' in value:
                    enum_values.append(value['key'])
                    # Also add children if they exist
                    if 'children' in value:
                        for child in value['children']:
                            if 'key' in child:
                                enum_values.append(child['key'])
            
            if enum_values:
                self.enums[enum_name] = enum_values
            
            # Store type info for interfaces
            self.types[f"{category}_{type_key}"] = {
                'category': category,
                'type': type_key,
                'values': values,
                'has_hierarchy': any('children' in v for v in values),
                'has_metadata': any('extra_metadata' in v for v in values)
            }
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    def _generate_enums_file(self):
        """Generate TypeScript enums file."""
        content = [
            "// Auto-generated TypeScript enums from configuration files",
            "// Do not edit manually - regenerate using npm run generate-types",
            "",
        ]
        
        for enum_name, values in self.enums.items():
            content.append(f"export enum {enum_name} {{")
            for value in values:
                # Convert snake_case to PascalCase for enum member
                member_name = self._to_pascal_case(value)
                content.append(f"  {member_name} = '{value}',")
            content.append("}")
            content.append("")
        
        # Write to file
        output_file = self.output_path / "enums.ts"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))
    
    def _generate_interfaces_file(self):
        """Generate TypeScript interfaces file."""
        content = [
            "// Auto-generated TypeScript interfaces from configuration files",
            "// Do not edit manually - regenerate using npm run generate-types",
            "",
            "export interface ConfigValue {",
            "  id: number;",
            "  key: string;",
            "  display_name: string;",
            "  description?: string;",
            "  level: number;",
            "  parent_id?: number;",
            "  metadata?: Record<string, any>;",
            "  tags?: string[];",
            "  sort_order: number;",
            "  is_system: boolean;",
            "  category: string;",
            "  type: string;",
            "}",
            "",
            "export interface ConfigCategory {",
            "  id: number;",
            "  category_key: string;",
            "  name: string;",
            "  description?: string;",
            "  sort_order: number;",
            "  is_active: boolean;",
            "}",
            "",
            "export interface ConfigType {",
            "  id: number;",
            "  category_id: number;",
            "  type_key: string;",
            "  name: string;",
            "  description?: string;",
            "  data_type: string;",
            "  sort_order: number;",
            "  is_active: boolean;",
            "}",
            "",
            "export interface HierarchicalConfigValue extends ConfigValue {",
            "  children?: HierarchicalConfigValue[];",
            "}",
            "",
        ]
        
        # Generate specific interfaces for each configuration type
        for type_info in self.types.values():
            category = type_info['category']
            type_key = type_info['type']
            interface_name = f"{self._to_pascal_case(category)}{self._to_pascal_case(type_key)}Config"
            
            content.append(f"export interface {interface_name} extends ConfigValue {{")
            
            # Add specific properties based on the configuration
            if type_info['has_metadata']:
                content.append("  metadata: {")
                # Analyze metadata structure from sample values
                metadata_props = set()
                for value in type_info['values']:
                    if 'extra_metadata' in value and value['extra_metadata']:
                        metadata_props.update(value['extra_metadata'].keys())
                
                for prop in sorted(metadata_props):
                    content.append(f"    {prop}?: any;")
                content.append("  };")
            
            content.append("}")
            content.append("")
        
        # Write to file
        output_file = self.output_path / "interfaces.ts"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))
    
    def _generate_config_client_file(self):
        """Generate configuration client service file."""
        content = [
            "// Auto-generated configuration client",
            "// Do not edit manually - regenerate using npm run generate-types",
            "",
            "import { ConfigValue, ConfigCategory, ConfigType, HierarchicalConfigValue } from './interfaces';",
            "",
            "export class ConfigurationClient {",
            "  private baseUrl: string;",
            "",
            "  constructor(baseUrl: string = '/api/v1/config') {",
            "    this.baseUrl = baseUrl;",
            "  }",
            "",
            "  async getCategories(): Promise<ConfigCategory[]> {",
            "    const response = await fetch(`${this.baseUrl}/categories`);",
            "    return response.json();",
            "  }",
            "",
            "  async getTypes(categoryKey?: string): Promise<ConfigType[]> {",
            "    const params = categoryKey ? `?category_key=${categoryKey}` : '';",
            "    const response = await fetch(`${this.baseUrl}/types${params}`);",
            "    return response.json();",
            "  }",
            "",
            "  async getValues(categoryKey?: string, typeKey?: string): Promise<ConfigValue[]> {",
            "    const params = new URLSearchParams();",
            "    if (categoryKey) params.append('category_key', categoryKey);",
            "    if (typeKey) params.append('type_key', typeKey);",
            "    const queryString = params.toString() ? `?${params.toString()}` : '';",
            "    const response = await fetch(`${this.baseUrl}/values${queryString}`);",
            "    return response.json();",
            "  }",
            "",
            "  async getValuesByType(categoryKey: string, typeKey: string): Promise<ConfigValue[]> {",
            "    const response = await fetch(`${this.baseUrl}/values/${categoryKey}/${typeKey}`);",
            "    return response.json();",
            "  }",
            "",
            "  async getHierarchicalValues(categoryKey: string, typeKey: string): Promise<HierarchicalConfigValue[]> {",
            "    const response = await fetch(`${this.baseUrl}/values/${categoryKey}/${typeKey}/hierarchy`);",
            "    return response.json();",
            "  }",
            "",
        ]
        
        # Generate specific getter methods for each configuration type
        for type_info in self.types.values():
            category = type_info['category']
            type_key = type_info['type']
            method_name = f"get{self._to_pascal_case(category)}{self._to_pascal_case(type_key)}"
            
            content.append(f"  async {method_name}(): Promise<ConfigValue[]> {{")
            content.append(f"    return this.getValuesByType('{category}', '{type_key}');")
            content.append("  }")
            content.append("")
        
        content.append("}")
        content.append("")
        content.append("export const configClient = new ConfigurationClient();")
        
        # Write to file
        output_file = self.output_path / "config-client.ts"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))
    
    def _get_enum_name(self, category: str, type_key: str) -> str:
        """Generate enum name from category and type."""
        return f"{self._to_pascal_case(category)}{self._to_pascal_case(type_key)}"
    
    def _to_pascal_case(self, text: str) -> str:
        """Convert snake_case to PascalCase."""
        return ''.join(word.capitalize() for word in text.split('_'))


def main():
    """Main function to generate TypeScript types."""
    base_path = Path(__file__).parent.parent.parent.parent
    config_path = base_path / "shared" / "config" / "reference-data"
    output_path = base_path / "shared" / "types" / "generated"
    
    if not config_path.exists():
        print(f"❌ Configuration path not found: {config_path}")
        return
    
    generator = TypeScriptGenerator(config_path, output_path)
    generator.generate_all_types()


if __name__ == '__main__':
    main()