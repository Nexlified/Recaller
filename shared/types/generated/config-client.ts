// Auto-generated configuration client
// Do not edit manually - regenerate using npm run generate-types

import { ConfigValue, ConfigCategory, ConfigType, HierarchicalConfigValue } from './interfaces';

export class ConfigurationClient {
  private baseUrl: string;

  constructor(baseUrl: string = '/api/v1/config') {
    this.baseUrl = baseUrl;
  }

  async getCategories(): Promise<ConfigCategory[]> {
    const response = await fetch(`${this.baseUrl}/categories`);
    return response.json();
  }

  async getTypes(categoryKey?: string): Promise<ConfigType[]> {
    const params = categoryKey ? `?category_key=${categoryKey}` : '';
    const response = await fetch(`${this.baseUrl}/types${params}`);
    return response.json();
  }

  async getValues(categoryKey?: string, typeKey?: string): Promise<ConfigValue[]> {
    const params = new URLSearchParams();
    if (categoryKey) params.append('category_key', categoryKey);
    if (typeKey) params.append('type_key', typeKey);
    const queryString = params.toString() ? `?${params.toString()}` : '';
    const response = await fetch(`${this.baseUrl}/values${queryString}`);
    return response.json();
  }

  async getValuesByType(categoryKey: string, typeKey: string): Promise<ConfigValue[]> {
    const response = await fetch(`${this.baseUrl}/values/${categoryKey}/${typeKey}`);
    return response.json();
  }

  async getHierarchicalValues(categoryKey: string, typeKey: string): Promise<HierarchicalConfigValue[]> {
    const response = await fetch(`${this.baseUrl}/values/${categoryKey}/${typeKey}/hierarchy`);
    return response.json();
  }

  async getSocialActivities(): Promise<ConfigValue[]> {
    return this.getValuesByType('social', 'activities');
  }

  async getCoreGenders(): Promise<ConfigValue[]> {
    return this.getValuesByType('core', 'genders');
  }

  async getCoreCountries(): Promise<ConfigValue[]> {
    return this.getValuesByType('core', 'countries');
  }

  async getContactInteractionTypes(): Promise<ConfigValue[]> {
    return this.getValuesByType('contact', 'interaction_types');
  }

  async getProfessionalIndustries(): Promise<ConfigValue[]> {
    return this.getValuesByType('professional', 'industries');
  }

}

export const configClient = new ConfigurationClient();