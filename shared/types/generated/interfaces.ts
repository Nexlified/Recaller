// Auto-generated TypeScript interfaces from configuration files
// Do not edit manually - regenerate using npm run generate-types

export interface ConfigValue {
  id: number;
  key: string;
  display_name: string;
  description?: string;
  level: number;
  parent_id?: number;
  metadata?: Record<string, any>;
  tags?: string[];
  sort_order: number;
  is_system: boolean;
  category: string;
  type: string;
}

export interface ConfigCategory {
  id: number;
  category_key: string;
  name: string;
  description?: string;
  sort_order: number;
  is_active: boolean;
}

export interface ConfigType {
  id: number;
  category_id: number;
  type_key: string;
  name: string;
  description?: string;
  data_type: string;
  sort_order: number;
  is_active: boolean;
}

export interface HierarchicalConfigValue extends ConfigValue {
  children?: HierarchicalConfigValue[];
}

export interface SocialActivitiesConfig extends ConfigValue {
  metadata: {
    color?: any;
    icon?: any;
  };
}

export interface CoreGendersConfig extends ConfigValue {
  metadata: {
    color?: any;
    icon?: any;
  };
}

export interface CoreCountriesConfig extends ConfigValue {
  metadata: {
    continent?: any;
    flag?: any;
    iso3_code?: any;
    iso_code?: any;
  };
}

export interface ContactInteractionTypesConfig extends ConfigValue {
  metadata: {
    category?: any;
    color?: any;
    icon?: any;
  };
}

export interface ProfessionalIndustriesConfig extends ConfigValue {
  metadata: {
    color?: any;
    icon?: any;
  };
}
