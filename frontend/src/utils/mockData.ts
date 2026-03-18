import type { Article, CompanyProfile, NotificationItem, Preferences } from "../types";

export const defaultPreferences: Preferences = {
  sectors: ["FinTech", "SaaS"],
  regions: ["US", "Europe", "India"],
  followed_companies: ["Stripe", "OpenAI", "Flutterwave"],
  followed_investors: ["Sequoia", "Accel"],
};

export const mockArticles: Article[] = [
  {
    id: 101,
    title: "Stripe opens up secondary liquidity window as fintech valuations thaw",
    url: "https://example.com/stripe-liquidity",
    source_name: "Bloomberg",
    source_quality_score: 0.95,
    published_at: "2026-03-17T07:45:00Z",
    summary_60w:
      "Stripe is giving employees and early investors another secondary sale window, reflecting stronger private-market demand for quality fintech names. The company remains private, but the deal signals renewed investor appetite, fresh price discovery, and more flexibility for top startup talent weighing liquidity against IPO timing across the broader venture ecosystem this year.",
    deep_dive: {
      what_happened:
        "Stripe launched a new secondary liquidity process that lets employees and some early backers sell shares without a public listing. The move gives market participants a new valuation signal while helping Stripe manage retention and compensation pressure as public fintech multiples recover unevenly.",
      key_players: ["Stripe", "Employees", "Early investors", "Secondary buyers"],
      market_impact:
        "The transaction could influence how other late-stage startups balance retention, cap-table pressure, and IPO readiness. It also suggests institutional buyers are becoming more selective but more active in private tech again.",
      whats_next:
        "Watch whether Stripe refreshes internal valuation marks, expands tender access, or uses the momentum to shape a future IPO window.",
    },
    sentiment: "bullish",
    impact_score: 0.92,
    vertical: "funding",
    region: "US",
    image_url:
      "https://images.unsplash.com/photo-1556740749-887f6717d7e4?auto=format&fit=crop&w=1200&q=80",
    audio_url: null,
    why_it_matters: "Late-stage startup liquidity is returning without forcing companies into premature IPOs.",
    companies: ["Stripe"],
    amount: "$1.1B secondary",
    investor_names: ["Institutional secondary buyers"],
    company_slug: "stripe",
    sector: "FinTech",
    funding_stage: "Secondary",
  },
  {
    id: 102,
    title: "OpenAI courts enterprise buyers with bundled agents, sparking platform pressure on SaaS incumbents",
    url: "https://example.com/openai-agents",
    source_name: "TechCrunch",
    source_quality_score: 0.85,
    published_at: "2026-03-17T06:10:00Z",
    summary_60w:
      "OpenAI is expanding its enterprise offering with bundled agent workflows aimed at internal knowledge search, support, and analyst productivity. The package raises pressure on horizontal SaaS vendors whose value depends on workflow orchestration. Buyers may consolidate spend faster if agent quality improves, pushing software companies to differentiate on data access, compliance, and execution depth.",
    deep_dive: {
      what_happened:
        "OpenAI introduced broader packaged enterprise workflows built around reusable agent patterns. The pitch is less about raw model access and more about rapid business deployment, which shifts the conversation from experimentation toward budget line items and procurement competition.",
      key_players: ["OpenAI", "Enterprise buyers", "Horizontal SaaS vendors"],
      market_impact:
        "SaaS platforms that monetized interfaces or lightweight workflow layers may face pricing and retention pressure if foundational model vendors bundle more capability directly into enterprise contracts.",
      whats_next:
        "Expect incumbents to push deeper vertical features, stronger compliance tooling, and more opinionated integrations to defend renewal cycles.",
    },
    sentiment: "risk",
    impact_score: 0.89,
    vertical: "general",
    region: "Global",
    image_url:
      "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1200&q=80",
    audio_url: null,
    why_it_matters: "Platform bundling could compress SaaS margins faster than founders expect.",
    companies: ["OpenAI"],
    company_slug: "openai",
    sector: "DeepTech",
    funding_stage: "Private",
    sources_disagree: true,
  },
  {
    id: 103,
    title: "Flutterwave expands SME lending stack after securing new African banking partnerships",
    url: "https://example.com/flutterwave-lending",
    source_name: "Forbes",
    source_quality_score: 0.88,
    published_at: "2026-03-16T20:15:00Z",
    summary_60w:
      "Flutterwave is broadening beyond payments into SME credit with new banking partners across Africa. The move gives merchants tighter access to working capital and deepens Flutterwave’s role in daily business operations. If underwriting holds, the company can increase revenue quality, strengthen merchant retention, and become a more defensible infrastructure platform for fast-growing regional commerce.",
    deep_dive: {
      what_happened:
        "Flutterwave signed lending-focused partnerships that let it package payment flows with financing options for small businesses. The company is using transaction visibility as a distribution and underwriting advantage rather than staying only in the payments layer.",
      key_players: ["Flutterwave", "African banks", "SME merchants"],
      market_impact:
        "Embedded finance remains attractive in markets where formal credit access is constrained. Strong execution could pressure payment rivals to deepen product breadth and local compliance relationships.",
      whats_next:
        "Monitor default performance, country rollout pace, and whether the product expands into payroll, invoicing, or cross-border trade tools.",
    },
    sentiment: "bullish",
    impact_score: 0.84,
    vertical: "emerging_markets",
    region: "Africa",
    image_url:
      "https://images.unsplash.com/photo-1520607162513-77705c0f0d4a?auto=format&fit=crop&w=1200&q=80",
    audio_url: null,
    why_it_matters: "Payments companies that own merchant data can become credit distribution engines.",
    companies: ["Flutterwave"],
    amount: "$150M lending capacity",
    investor_names: ["Partner banks"],
    company_slug: "flutterwave",
    sector: "FinTech",
    funding_stage: "Series D",
  },
  {
    id: 104,
    title: "EU regulators question fast-growing cross-border payroll startups on data residency",
    url: "https://example.com/eu-payroll-regulation",
    source_name: "VentureBeat",
    source_quality_score: 0.8,
    published_at: "2026-03-16T15:05:00Z",
    summary_60w:
      "European regulators are scrutinizing cross-border payroll startups over employee data residency and consent controls. The review targets how workforce records move through third-party vendors and AI tooling. Compliance gaps could slow expansion plans, increase onboarding costs, and favor startups with stronger governance architecture, local hosting options, and clearer enterprise controls for multinational customers.",
    deep_dive: {
      what_happened:
        "Regulators in Europe are examining payroll and HR software vendors whose architectures route sensitive workforce data across borders or through loosely governed vendors. The scrutiny comes as AI features become more common inside employee management products.",
      key_players: ["EU regulators", "Payroll startups", "Enterprise HR teams"],
      market_impact:
        "Compliance maturity may become a stronger differentiator than growth speed in European B2B software categories involving sensitive employee records and AI-assisted workflows.",
      whats_next:
        "Companies may accelerate regional infrastructure investments, vendor reviews, and product limits for AI features touching regulated records.",
    },
    sentiment: "risk",
    impact_score: 0.73,
    vertical: "regulatory",
    region: "Europe",
    image_url:
      "https://images.unsplash.com/photo-1516321165247-4aa89a48be28?auto=format&fit=crop&w=1200&q=80",
    audio_url: null,
    why_it_matters: "Compliance architecture can become a sales advantage before it becomes a legal problem.",
    companies: ["Remote", "Deel"],
    company_slug: "remote",
    sector: "SaaS",
    funding_stage: "Series C",
  },
  {
    id: 105,
    title: "Consumer app unicorn trims two product teams to refocus on AI retention loops",
    url: "https://example.com/consumer-layoffs",
    source_name: "Bloomberg",
    source_quality_score: 0.95,
    published_at: "2026-03-15T18:50:00Z",
    summary_60w:
      "A consumer app unicorn cut staff across two product teams while redirecting spending toward AI-driven retention experiments. The company says the move is targeted, but it highlights how quickly growth-stage businesses are reallocating capital from breadth to efficiency. Investors will watch whether narrower roadmaps and stronger monetization loops meaningfully improve burn discipline this year.",
    deep_dive: {
      what_happened:
        "The company eliminated roles in lower-priority product lines and consolidated staff into monetization and retention programs tied to AI-assisted engagement. Leadership framed the cuts as strategic rather than a broad retreat.",
      key_players: ["Consumer app unicorn", "Product teams", "Investors"],
      market_impact:
        "More startups may shrink exploratory roadmaps and move talent toward profitability levers if AI tools make teams believe they can ship more with fewer people.",
      whats_next:
        "Expect closer investor scrutiny on whether efficiency gains actually improve retention, monetization, and runway outcomes.",
    },
    sentiment: "bearish",
    impact_score: 0.69,
    vertical: "layoffs",
    region: "US",
    image_url:
      "https://images.unsplash.com/photo-1521737604893-d14cc237f11d?auto=format&fit=crop&w=1200&q=80",
    audio_url: null,
    why_it_matters: "AI spending is increasingly financed by cutting non-core teams and roadmap breadth.",
    companies: ["Nova"],
    company_slug: "nova",
    sector: "Consumer",
    funding_stage: "Series C",
  },
];

export const mockCompanies: CompanyProfile[] = [
  {
    id: 1,
    name: "Stripe",
    slug: "stripe",
    sector: "FinTech",
    hq_country: "US",
    funding_stage: "Private",
    investors: ["Sequoia", "General Catalyst", "Andreessen Horowitz"],
    article_count: 12,
    last_headline: "Stripe opens up secondary liquidity window as fintech valuations thaw",
    created_at: "2026-03-01T12:00:00Z",
    articles: mockArticles.filter((article) => article.companies.includes("Stripe")),
  },
  {
    id: 2,
    name: "OpenAI",
    slug: "openai",
    sector: "DeepTech",
    hq_country: "US",
    funding_stage: "Private",
    investors: ["Microsoft", "Thrive Capital"],
    article_count: 8,
    last_headline:
      "OpenAI courts enterprise buyers with bundled agents, sparking platform pressure on SaaS incumbents",
    created_at: "2026-03-01T12:00:00Z",
    articles: mockArticles.filter((article) => article.companies.includes("OpenAI")),
  },
  {
    id: 3,
    name: "Flutterwave",
    slug: "flutterwave",
    sector: "FinTech",
    hq_country: "Nigeria",
    funding_stage: "Series D",
    investors: ["Tiger Global", "Avenir", "Greenoaks"],
    article_count: 6,
    last_headline: "Flutterwave expands SME lending stack after securing new African banking partnerships",
    created_at: "2026-03-01T12:00:00Z",
    articles: mockArticles.filter((article) => article.companies.includes("Flutterwave")),
  },
];

export const mockNotifications = [
  {
    id: 1,
    user_id: 1,
    article_id: 101,
    type: "followed_company",
    read: false,
    created_at: "2026-03-17T08:00:00Z",
  },
  {
    id: 2,
    user_id: 1,
    article_id: 103,
    type: "regional_alert",
    read: false,
    created_at: "2026-03-16T20:45:00Z",
  },
] satisfies NotificationItem[];
