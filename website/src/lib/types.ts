export type Status = 'observed' | 'modelled' | 'estimated' | 'illustrative';

export interface Prov {
  status: string;
  confidence_level: string;
  source: string;
  source_url?: string | null;
  methodology: string;
  note?: string;
}

export interface HeadlineYear {
  year: number;
  gdp: number;
  domestic_value_retention: number;
  foreign_value_leakage: number;
  foreign_value_leakage_eur_m: number;
  foreign_ownership_capture: number;
  foreign_creditor_income_share_of_nos?: number | null;
  foreign_labour_income_share: number;
  foreign_input_exposure: number | null;
  official_primary_income_outflow_to_gdp: number;
  official_gni: number;
  ofc_investment_income_paid: number;
  fdi_income_paid_non_spe: number | null;
  fdi_income_paid_total: number | null;
  dvr_consistent_scope: number;
  fats_scope: string;
  theta: number;
  tau: number;
}

export interface Headline {
  country: string;
  name: string;
  years: number[];
  io_years: number[];
  series: HeadlineYear[];
}

export interface FlowRow extends Prov {
  industry: string;
  industry_name: string;
  recipient: string;
  recipient_name: string;
  mechanism: string;
  value: number;
}

export interface Flows {
  year: number;
  gdp: number;
  rows: FlowRow[];
}

export interface Industry {
  industry: string;
  name: string;
  gva: number;
  compensation: number;
  gross_operating_surplus: number;
  foreign_outflow: number;
  foreign_capital_income: number;
  foreign_ownership_capture: number | null;
  domestic_retention: number | null;
  direct_foreign_input_exposure: number | null;
  total_import_content: number | null;
  main_recipients: { recipient: string; name: string; value: number }[];
}

export interface PerEuroProduct {
  name: string;
  channels: Record<string, number>;
  domestic_va_retained: number;
  recipients: Record<string, number>;
}

export interface IoNetwork {
  year: number;
  nodes: { id: string; name: string; output: number; imported_inputs: number }[];
  edges: { from: string; to: string; value: number }[];
  source: string;
  unit: string;
}

export interface Firm {
  entity_id: string;
  legal_name: string;
  sector: string;
  nace_code: number | null;
  domestic: number;
  foreign: number;
  unresolved: number;
  uci_entity: string;
  uci_country: string;
  uci_status: string;
  first_foreign_parent_country: string | null;
  unpriced_parent_edges: number;
  confidence: string;
}

export interface OwnNode {
  id: string;
  name: string;
  country: string;
  sector: string | null;
  source_url: string | null;
  revenue_eur_m: number | null;
  operating_profit_eur_m: number | null;
  employees: number | null;
  fiscal_year: number | null;
  notes: string | null;
  source: string | null;
  source_tier: number | null;
  confidence: string | null;
}

export interface OwnEdge {
  from: string;
  to: string;
  share_pct: number;
  share_type: string;
  as_of_date: string;
  source: string;
  source_url: string;
  source_tier: number;
  confidence: string;
  presumption: string;
}

export interface Ownership {
  firms: Firm[];
  nodes: OwnNode[];
  edges: OwnEdge[];
  unpriced_edges: { parent_entity_id: string; child_entity_id: string; share_type: string; source_url: string; notes: string }[];
  theta_calibration: { entity_id: string; group: string; theta: number; group_theta: number }[];
  note: string;
}

export interface SensRow {
  year: number;
  domestic_value_retention: number;
  foreign_value_leakage: number;
  foreign_capital_income_share_of_gos: number;
  theta: number;
  tax: string;
  include_ofc: boolean;
  consistent_scope: boolean;
  source: string;
  methodology: string;
  status: string;
  confidence_level: string;
}

export interface ReconRow {
  check: string;
  year: number;
  official: number;
  model: number;
  difference: number;
  pct_difference: number;
  passes: boolean;
  explanation: string;
  status: string;
  confidence_level: string;
  source: string;
  source_url: string | null;
}

export interface CatalogueRow {
  dataset: string;
  provider: string;
  URL: string;
  reference_year: string;
  publication_date: string;
  download_date: string;
  license: string;
  geographic_scope: string;
  industry_resolution: string;
  variables: string;
  processing_script: string;
  checksum: string;
}

export interface Names {
  industries: Record<string, string>;
  recipients: Record<string, string>;
}
