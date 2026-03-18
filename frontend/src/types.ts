export type Sentiment = "bullish" | "bearish" | "risk" | "neutral";
export type Vertical =
  | "funding"
  | "founder_stories"
  | "layoffs"
  | "regulatory"
  | "emerging_markets"
  | "general";

export interface DeepDive {
  what_happened: string;
  key_players: string[];
  market_impact: string;
  whats_next: string;
}

export interface Article {
  id: number;
  title: string;
  url: string;
  source_name: string;
  source_quality_score: number;
  published_at: string;
  raw_content?: string | null;
  summary_60w: string;
  deep_dive: DeepDive;
  sentiment: Sentiment;
  impact_score: number;
  vertical: Vertical;
  region: string;
  image_url?: string | null;
  audio_url?: string | null;
  why_it_matters: string;
  companies: string[];
  amount?: string;
  investor_names?: string[];
  company_slug?: string;
  sector?: string;
  funding_stage?: string;
  sources_disagree?: boolean;
}

export interface CompanyProfile {
  id: number;
  name: string;
  slug: string;
  sector: string;
  hq_country: string;
  funding_stage: string;
  investors: string[];
  article_count: number;
  last_headline: string;
  created_at: string;
  articles: Article[];
}

export interface NotificationItem {
  id: number;
  user_id: number;
  article_id: number;
  type: string;
  read: boolean;
  created_at: string;
}

export interface Preferences {
  sectors: string[];
  regions: string[];
  followed_companies: string[];
  followed_investors: string[];
}
