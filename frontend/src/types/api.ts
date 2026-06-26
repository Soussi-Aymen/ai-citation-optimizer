export interface HealthResponse {
  peec_available: boolean
}

export interface Competitor {
  name: string
  domain: string
  is_own: boolean
  citations: number
  visibility: number
}

export interface GapsResponse {
  domain: string
  peec_available: boolean
  total_sitemap_pages: number
  total_cited_pages: number | null
  citation_coverage_pct: number | null
  performance_score: number | null
  gaps: string[]
  orphans: string[]
  sitemap_metrics: Record<string, unknown>
  brands: unknown[]
  competitors: Competitor[]
}

export interface BenchmarkAction {
  id: string
  text: string
  url: string
}

export interface RoadmapItem {
  priority: string
  priority_emoji: string
  title: string
  channel: string
  gap_percentage: number
  opportunity_score: number
  actions: BenchmarkAction[]
  type: string
  slice_id: string
}

export interface ChannelGapCompetitor {
  name: string
  visibility: number
}

export interface ChannelGap {
  channel: string
  competitors: ChannelGapCompetitor[]
  own: { name: string; visibility: number }
  gap_label: string
}

export interface TabAction {
  gap_percentage: number
  opportunity_score: number
  items: BenchmarkAction[]
  has_data: boolean
}

export interface BenchmarkResponse {
  peec_available?: boolean
  domain: string
  current: { visibility_score: number; citation_count: number }
  estimated: { visibility_score: number; citation_count: number }
  roadmap: RoadmapItem[]
  channel_gaps: ChannelGap[]
  tab_actions: Record<string, TabAction>
  own_brand_name: string
}

export interface GuidanceItem {
  id: string
  steps: string[]
}

export interface AuditGuidanceItem {
  id?: string
  metric: string
  score: string
  advice: string
  steps?: string[]
}

export interface AuditSignals {
  js_impact?: string
  unused_js_pct?: number | null
  js_payload_mb?: number | null
  lcp_seconds?: number | null
  console_errors?: number | null
  has_llms_txt?: boolean
  llms_txt_valid?: boolean
  llms_txt_lists_page?: boolean
  load_time_ms?: number
  dom_depth?: number
  has_json_ld?: boolean
  text_delta?: number
  domain?: string
}

export interface FixResponse {
  problem: string
  checklist: string[]
  json_ld: string
  llms_txt_template: string
  metrics?: AuditSignals
  guidance?: GuidanceItem[]
}

export interface AuditAnalysis {
  signals?: AuditSignals
  guidance?: AuditGuidanceItem[]
  logs?: string[]
  performance_report?: {
    score: number
    issues?: string[]
    fixes?: string[]
  }
  sitemap_audit?: {
    score: number
    analysis?: string
    improvements?: string[]
  }
  competitive_analysis?: {
    competitor_edge: string
    gap_to_close: string
  }
  ai_readiness?: {
    overall_score: number
    estimated_impact: string
  }
  execution_time_ms?: number
  error?: boolean
  message?: string
}

export interface AuditResponse {
  url: string
  analysis: AuditAnalysis
}

export interface ContentResponse {
  content: string
}

export type TabName = 'YouTube' | 'Reddit' | 'Editorial'
