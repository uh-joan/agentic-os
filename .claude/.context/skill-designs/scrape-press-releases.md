# Press Release & News Scraper

**Skill Name**: `scrape_pharma_news`

**Category**: Data Collection / Competitive Intelligence

**Complexity**: Medium-High

**Purpose**: Automatically monitor and extract pharmaceutical news from company investor relations pages and news aggregators, providing real-time competitive intelligence on clinical developments, regulatory decisions, and partnerships.

---

## Overview

This skill provides continuous monitoring of two critical news sources:
1. **Company IR pages**: Official press releases (structured, authoritative)
2. **News aggregators**: Google News, Yahoo Finance (broad coverage, third-party analysis)

**Key Value**:
- **Early warning**: Detect competitive developments before reflected in databases
- **Context enrichment**: Understand strategic rationale behind pipeline decisions
- **Trend detection**: Identify emerging themes (e.g., increase in ADC partnerships)
- **Deal intelligence**: Track M&A, licensing, collaboration announcements

---

## Input Schema

```python
{
    "sources": List[str],               # ["company_ir", "news_aggregator"] (default: both)
    "company": str,                     # Required: Company name (e.g., "Pfizer")
    "keywords": List[str],              # Filter keywords (default: pharma-focused)
    "filters": {
        "start_date": str,              # ISO format YYYY-MM-DD (default: 6 months ago)
        "end_date": str,                # ISO format YYYY-MM-DD (default: today)
        "categories": List[str],        # ["Clinical", "Regulatory", "M&A", "Pipeline"]
        "exclude_keywords": List[str]   # Noise filter (e.g., ["earnings", "dividend"])
    },
    "analysis_options": {
        "sentiment_analysis": bool,     # Positive/negative/neutral (default: True)
        "entity_extraction": bool,      # Extract drugs, diseases, companies (default: True)
        "event_classification": bool,   # Categorize event type (default: True)
        "deduplicate": bool            # Remove duplicate stories (default: True)
    },
    "output_options": {
        "format": str,                  # "json", "csv", "markdown" (default: "json")
        "max_results": int,             # Limit results (default: 100)
        "sort_by": str                  # "date", "relevance" (default: "date")
    }
}
```

---

## Output Schema

```python
{
    "query_metadata": {
        "company": str,
        "keywords": List[str],
        "date_range": {"start": str, "end": str},
        "sources_searched": List[str],
        "scraped_at": str,
        "total_results": int
    },
    "news_items": List[{
        "title": str,
        "summary": str,                 # First 200 chars or extracted summary
        "full_text": str,               # Full article text (if available)
        "url": str,
        "source": str,                  # "Company IR" or news outlet name
        "published_date": str,          # ISO format
        "category": str,                # "Clinical", "Regulatory", "M&A", "Pipeline"
        "sentiment": {
            "score": float,             # -1 (negative) to +1 (positive)
            "label": str                # "Positive", "Neutral", "Negative"
        },
        "entities": {
            "drugs": List[str],         # Mentioned drug names
            "diseases": List[str],      # Mentioned diseases
            "companies": List[str],     # Mentioned companies (partners, competitors)
            "phases": List[str]         # Clinical phases mentioned
        },
        "event_type": str,              # "Phase 3 results", "FDA approval", "Partnership", etc.
        "key_facts": List[str],         # Extracted bullet points
        "relevance_score": float        # 0-100 (how relevant to query)
    }],
    "insights": {
        "trending_topics": List[str],   # Most common themes
        "sentiment_distribution": {     # Overall news tone
            "positive": int,
            "neutral": int,
            "negative": int
        },
        "timeline": List[{              # Chronological summary
            "date": str,
            "events": List[str]
        }]
    }
}
```

---

## Algorithm

### Step 1: Source-Specific Scraping

#### Source A: Company IR Pages

```python
# Company IR URL database
COMPANY_IR_URLS = {
    "Pfizer": {
        "news_url": "https://www.pfizer.com/news/press-release",
        "rss_feed": "https://www.pfizer.com/news/rss.xml",
        "scraper_type": "press_release_list",
        "pagination": True,
        "max_pages": 10
    },
    "Merck": {
        "news_url": "https://www.merck.com/news/",
        "rss_feed": None,
        "scraper_type": "news_grid",
        "pagination": True,
        "max_pages": 5
    },
    # ... 100+ companies
}

def scrape_company_ir(company: str, start_date: str, keywords: List[str]) -> List[Dict]:
    """Scrape official press releases from IR page."""

    config = COMPANY_IR_URLS.get(company)
    if not config:
        raise CompanyNotFoundError(f"No IR config for {company}")

    # Try RSS feed first (faster, structured)
    if config.get('rss_feed'):
        try:
            return scrape_rss_feed(config['rss_feed'], start_date, keywords)
        except:
            pass  # Fallback to HTML scraping

    # HTML scraping with Playwright
    news_items = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for page_num in range(1, config.get('max_pages', 5) + 1):
            url = build_pagination_url(config['news_url'], page_num)
            page.goto(url, wait_until="networkidle")

            # Extract press release links
            links = page.query_selector_all('a[href*="press-release"], a[href*="/news/"]')

            for link in links:
                title = link.text_content().strip()
                href = link.get_attribute('href')

                # Filter by keywords
                if keywords and not any(kw.lower() in title.lower() for kw in keywords):
                    continue

                # Follow link to get full content
                full_article = scrape_article_page(page, href)

                news_items.append({
                    "title": title,
                    "url": make_absolute_url(config['news_url'], href),
                    "source": f"{company} Press Release",
                    "published_date": full_article.get('date'),
                    "full_text": full_article.get('content'),
                    "summary": full_article.get('summary')
                })

        browser.close()

    return news_items
```

#### Source B: News Aggregators

```python
import requests
from urllib.parse import quote

def scrape_google_news(company: str, keywords: List[str], start_date: str) -> List[Dict]:
    """Search Google News RSS feed."""

    # Build query
    query_parts = [company] + keywords
    query = ' '.join(query_parts)

    # Google News RSS feed
    url = f"https://news.google.com/rss/search?q={quote(query)}&hl=en-US&gl=US&ceid=US:en"

    response = requests.get(url)
    response.raise_for_status()

    # Parse RSS
    import feedparser
    feed = feedparser.parse(response.content)

    news_items = []
    for entry in feed.entries:
        # Filter by date
        published = parse_date(entry.get('published'))
        if published < datetime.fromisoformat(start_date):
            continue

        news_items.append({
            "title": entry.title,
            "url": entry.link,
            "source": entry.get('source', {}).get('title', 'Google News'),
            "published_date": published.isoformat(),
            "summary": clean_html(entry.get('summary', '')),
            "full_text": None  # Would need to scrape article page
        })

    return news_items

def scrape_yahoo_finance(company: str, ticker: str = None) -> List[Dict]:
    """Yahoo Finance news feed (requires ticker symbol)."""

    if not ticker:
        ticker = lookup_ticker(company)  # e.g., "PFE" for Pfizer

    url = f"https://finance.yahoo.com/quote/{ticker}/news"

    # Use Playwright (Yahoo Finance is JavaScript-heavy)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")

        # Extract news items
        articles = page.query_selector_all('li.js-stream-content')

        news_items = []
        for article in articles[:50]:  # Top 50
            title_elem = article.query_selector('h3')
            summary_elem = article.query_selector('p')
            link_elem = article.query_selector('a')

            if title_elem and link_elem:
                news_items.append({
                    "title": title_elem.text_content(),
                    "url": link_elem.get_attribute('href'),
                    "source": "Yahoo Finance",
                    "summary": summary_elem.text_content() if summary_elem else "",
                    "published_date": extract_date_from_article(article)
                })

        browser.close()

    return news_items
```

### Step 2: Content Classification

```python
def classify_news_category(title: str, content: str) -> str:
    """Categorize news by event type."""

    # Keyword-based classification
    categories = {
        "Clinical": ["phase 1", "phase 2", "phase 3", "trial results", "enrollment",
                     "efficacy", "safety data", "clinical trial", "patient"],
        "Regulatory": ["fda approval", "approved", "rejection", "crl", "complete response",
                       "breakthrough", "orphan", "fast track", "nda", "bla"],
        "M&A": ["acquisition", "acquire", "merger", "bought", "divest", "purchase",
                "licensing", "license agreement"],
        "Pipeline": ["pipeline", "discontinue", "advance", "initiate", "program update"],
        "Partnership": ["collaboration", "partnership", "co-develop", "joint venture"],
        "Financial": ["earnings", "revenue", "profit", "guidance", "dividend"],
        "Leadership": ["ceo", "appoint", "hire", "resign", "board"]
    }

    text = (title + " " + content).lower()

    # Score each category
    scores = {}
    for category, keywords in categories.items():
        scores[category] = sum(1 for kw in keywords if kw in text)

    # Return highest scoring category
    if max(scores.values()) > 0:
        return max(scores, key=scores.get)
    else:
        return "Other"
```

### Step 3: Entity Extraction (NER)

```python
import re

def extract_entities(text: str) -> Dict:
    """Extract drugs, diseases, companies, phases."""

    entities = {
        "drugs": [],
        "diseases": [],
        "companies": [],
        "phases": []
    }

    # Phase extraction (regex)
    phase_pattern = r'\b[Pp]hase\s+([1-4]|I{1,3}|IV)\b'
    entities["phases"] = list(set(re.findall(phase_pattern, text)))

    # Drug name extraction (capitalized words, common suffixes)
    drug_pattern = r'\b[A-Z][a-z]+(mab|nib|tinib|stat|pril|sartan|tide|ase)\b'
    entities["drugs"] = list(set(re.findall(drug_pattern, text)))

    # Disease extraction (using medical dictionary)
    from medical_dictionaries import DISEASE_NAMES  # Pre-loaded list
    for disease in DISEASE_NAMES:
        if disease.lower() in text.lower():
            entities["diseases"].append(disease)

    # Company extraction (using pharma company list)
    from company_lists import PHARMA_COMPANIES
    for company in PHARMA_COMPANIES:
        if company.lower() in text.lower():
            entities["companies"].append(company)

    # Deduplicate
    for key in entities:
        entities[key] = list(set(entities[key]))

    return entities
```

### Step 4: Sentiment Analysis

```python
from transformers import pipeline

# Load pre-trained sentiment model (once)
sentiment_analyzer = pipeline("sentiment-analysis", model="finiteautomata/bertweet-base-sentiment-analysis")

def analyze_sentiment(text: str) -> Dict:
    """Determine if news is positive, negative, or neutral."""

    # Truncate to 512 tokens (BERT limit)
    text_truncated = text[:512]

    # Run sentiment analysis
    result = sentiment_analyzer(text_truncated)[0]

    # Map to -1 to +1 scale
    sentiment_map = {
        "POS": 1.0,
        "NEU": 0.0,
        "NEG": -1.0
    }

    return {
        "score": sentiment_map.get(result['label'], 0.0),
        "label": result['label'],
        "confidence": result['score']
    }
```

### Step 5: Deduplication

```python
from difflib import SequenceMatcher

def deduplicate_news(news_items: List[Dict]) -> List[Dict]:
    """Remove duplicate stories (same event, different outlets)."""

    unique_items = []
    seen_titles = []

    for item in news_items:
        # Check for similar titles (fuzzy matching)
        is_duplicate = False

        for seen_title in seen_titles:
            similarity = SequenceMatcher(None, item['title'], seen_title).ratio()
            if similarity > 0.8:  # 80% similar = duplicate
                is_duplicate = True
                break

        if not is_duplicate:
            unique_items.append(item)
            seen_titles.append(item['title'])

    return unique_items
```

### Step 6: Insights Generation

```python
from collections import Counter

def generate_insights(news_items: List[Dict]) -> Dict:
    """Extract high-level patterns and trends."""

    # Trending topics (most common entities)
    all_drugs = [drug for item in news_items for drug in item['entities']['drugs']]
    all_diseases = [disease for item in news_items for disease in item['entities']['diseases']]

    trending_drugs = Counter(all_drugs).most_common(10)
    trending_diseases = Counter(all_diseases).most_common(10)

    # Sentiment distribution
    sentiment_dist = {
        "positive": sum(1 for item in news_items if item['sentiment']['label'] == 'POS'),
        "neutral": sum(1 for item in news_items if item['sentiment']['label'] == 'NEU'),
        "negative": sum(1 for item in news_items if item['sentiment']['label'] == 'NEG')
    }

    # Timeline
    timeline = {}
    for item in news_items:
        date = item['published_date'][:10]  # YYYY-MM-DD
        if date not in timeline:
            timeline[date] = []
        timeline[date].append(item['title'])

    timeline_list = [{"date": date, "events": events} for date, events in sorted(timeline.items())]

    return {
        "trending_topics": [f"{drug} ({count} mentions)" for drug, count in trending_drugs],
        "trending_diseases": [f"{disease} ({count} mentions)" for disease, count in trending_diseases],
        "sentiment_distribution": sentiment_dist,
        "timeline": timeline_list
    }
```

---

## Visualization & Output

### Terminal Output (Timeline View)

```python
def print_news_timeline(news_items: List[Dict]):
    """Chronological news feed."""

    print("\n" + "="*80)
    print("  PHARMACEUTICAL NEWS TIMELINE")
    print("="*80 + "\n")

    # Sort by date
    sorted_news = sorted(news_items, key=lambda x: x['published_date'], reverse=True)

    current_date = None

    for item in sorted_news:
        date = item['published_date'][:10]

        # Date separator
        if date != current_date:
            print(f"\n📅 {date}")
            print("-" * 80)
            current_date = date

        # Sentiment emoji
        sentiment_emoji = {
            "POS": "✅",
            "NEU": "ℹ️",
            "NEG": "❌"
        }
        emoji = sentiment_emoji.get(item['sentiment']['label'], "📰")

        # Print news item
        print(f"\n{emoji} {item['title']}")
        print(f"   Source: {item['source']}")
        print(f"   Category: {item['category']}")
        if item['entities']['drugs']:
            print(f"   Drugs: {', '.join(item['entities']['drugs'][:3])}")
        print(f"   URL: {item['url']}")
```

**Example Output**:
```
================================================================================
  PHARMACEUTICAL NEWS TIMELINE
================================================================================

📅 2025-01-24
────────────────────────────────────────────────────────────────────────────────

✅ Pfizer Announces Positive Phase 3 Results for Danuglipron in Type 2 Diabetes
   Source: Pfizer Press Release
   Category: Clinical
   Drugs: Danuglipron
   URL: https://www.pfizer.com/news/press-release/2025-01-24

ℹ️ Merck Pipeline Update: Advancing 15 Programs to Phase 2
   Source: Merck IR
   Category: Pipeline
   URL: https://www.merck.com/news/2025-01-24

📅 2025-01-23
────────────────────────────────────────────────────────────────────────────────

❌ Roche Discontinues IL-6 Program Due to Safety Concerns
   Source: Yahoo Finance
   Category: Clinical
   Drugs: RG7845
   URL: https://finance.yahoo.com/news/roche-discontinues...
```

### Sentiment Breakdown Visualization

```python
import matplotlib.pyplot as plt

def visualize_sentiment_over_time(news_items: List[Dict], output_path: str):
    """Plot sentiment trends over time."""

    # Group by date
    dates = [item['published_date'][:10] for item in news_items]
    sentiments = [item['sentiment']['score'] for item in news_items]

    # Create DataFrame
    import pandas as pd
    df = pd.DataFrame({"date": dates, "sentiment": sentiments})
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')

    # Rolling average
    df['sentiment_ma'] = df['sentiment'].rolling(window=7, min_periods=1).mean()

    # Plot
    fig, ax = plt.subplots(figsize=(14, 6))

    # Scatter plot (individual news items)
    colors = ['green' if s > 0 else 'red' if s < 0 else 'gray' for s in df['sentiment']]
    ax.scatter(df['date'], df['sentiment'], c=colors, alpha=0.5, s=50)

    # Trend line
    ax.plot(df['date'], df['sentiment_ma'], color='blue', linewidth=2, label='7-day moving average')

    # Zero line
    ax.axhline(0, color='black', linestyle='--', alpha=0.3)

    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Sentiment Score (-1 to +1)', fontsize=12)
    ax.set_title('News Sentiment Over Time', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
```

---

## Usage Examples

### Example 1: Monitor Pfizer News (Past 3 Months)

```python
from .claude.skills.scrape_pharma_news.scripts.scrape_pharma_news import scrape_pharma_news
from datetime import datetime, timedelta

three_months_ago = (datetime.now() - timedelta(days=90)).isoformat()[:10]

result = scrape_pharma_news(
    sources=["company_ir", "news_aggregator"],
    company="Pfizer",
    keywords=["Phase 3", "FDA approval", "clinical trial"],
    filters={
        "start_date": three_months_ago,
        "categories": ["Clinical", "Regulatory"],
        "exclude_keywords": ["earnings", "dividend"]
    },
    analysis_options={
        "sentiment_analysis": True,
        "entity_extraction": True,
        "event_classification": True
    }
)

print(f"Total news items: {result['query_metadata']['total_results']}")
print(f"Sentiment: {result['insights']['sentiment_distribution']}")

# Print recent clinical updates
clinical_news = [item for item in result['news_items'] if item['category'] == 'Clinical']
for news in clinical_news[:5]:
    print(f"\n{news['published_date']}: {news['title']}")
```

### Example 2: Track Competitive GLP-1 Developments

```python
glp1_companies = ["Novo Nordisk", "Eli Lilly", "Pfizer", "Roche"]

all_news = []

for company in glp1_companies:
    result = scrape_pharma_news(
        sources=["company_ir"],
        company=company,
        keywords=["GLP-1", "obesity", "diabetes", "semaglutide", "tirzepatide"],
        filters={"start_date": "2024-01-01"}
    )
    all_news.extend(result['news_items'])

# Sort by date
all_news.sort(key=lambda x: x['published_date'], reverse=True)

# Print GLP-1 competitive timeline
for news in all_news[:20]:
    print(f"{news['published_date'][:10]} | {news['source']:20} | {news['title']}")
```

**Output**:
```
2025-01-24 | Pfizer Press Release | Positive Phase 3 Data for Danuglipron
2025-01-18 | Eli Lilly IR         | FDA Approves Mounjaro for Weight Loss
2025-01-12 | Novo Nordisk IR      | Wegovy Expands to Adolescent Indication
2024-12-20 | Roche News           | Initiates Phase 2 Oral GLP-1 Program
```

### Example 3: M&A Deal Tracking

```python
result = scrape_pharma_news(
    sources=["news_aggregator"],
    company=None,  # All companies
    keywords=["acquisition", "licensing deal", "partnership", "bought"],
    filters={
        "start_date": "2024-01-01",
        "categories": ["M&A", "Partnership"]
    },
    output_options={"max_results": 50}
)

# Extract deal details
deals = []
for news in result['news_items']:
    if news['category'] == 'M&A':
        deals.append({
            "date": news['published_date'][:10],
            "title": news['title'],
            "companies": news['entities']['companies'],
            "url": news['url']
        })

# Print recent deals
print(f"Recent M&A Activity ({len(deals)} deals):\n")
for deal in deals[:10]:
    print(f"{deal['date']} | {deal['title']}")
    print(f"           Companies: {', '.join(deal['companies'][:3])}\n")
```

---

## Implementation Notes

### Dependencies

```bash
# Core scraping
pip install playwright beautifulsoup4 requests feedparser

# NLP & sentiment
pip install transformers torch

# Optional (for advanced NER)
pip install spacy
python -m spacy download en_core_web_sm
```

### File Structure

```
scrape-pharma-news/
├── SKILL.md                               # This documentation
├── config/
│   ├── company_ir_urls.json               # IR page URLs
│   └── keywords.json                      # Industry-specific keywords
└── scripts/
    ├── scrape_pharma_news.py              # Main entry point
    ├── scrapers/
    │   ├── company_ir_scraper.py          # IR page scraping
    │   ├── google_news_scraper.py         # Google News RSS
    │   └── yahoo_finance_scraper.py       # Yahoo Finance news
    ├── analysis/
    │   ├── sentiment_analysis.py          # BERT-based sentiment
    │   ├── entity_extraction.py           # NER (drugs, diseases)
    │   └── classification.py              # Event categorization
    ├── utils/
    │   ├── deduplication.py               # Remove duplicates
    │   └── date_parser.py                 # Flexible date parsing
    └── test_news_scraping.py              # Unit tests
```

### Rate Limiting & Caching

```python
import hashlib
import json
from pathlib import Path

CACHE_DIR = Path(".cache/news")

def cache_key(company: str, start_date: str, keywords: List[str]) -> str:
    """Generate cache key."""
    data = f"{company}_{start_date}_{'_'.join(sorted(keywords))}"
    return hashlib.md5(data.encode()).hexdigest()

def get_cached_results(cache_key: str, max_age_hours: int = 6) -> Optional[Dict]:
    """Retrieve cached results if fresh."""
    cache_file = CACHE_DIR / f"{cache_key}.json"

    if cache_file.exists():
        age = time.time() - cache_file.stat().st_mtime
        if age < max_age_hours * 3600:
            with open(cache_file) as f:
                return json.load(f)

    return None

def save_to_cache(cache_key: str, data: Dict):
    """Save results to cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / f"{cache_key}.json"

    with open(cache_file, 'w') as f:
        json.dump(data, f, indent=2)
```

---

## Advanced Features

### Real-Time Alerts

```python
def setup_news_alerts(companies: List[str], keywords: List[str], webhook_url: str):
    """Continuous monitoring with Slack/email alerts."""

    import schedule

    def check_for_news():
        """Run every hour."""
        for company in companies:
            result = scrape_pharma_news(
                company=company,
                keywords=keywords,
                filters={"start_date": (datetime.now() - timedelta(hours=1)).isoformat()[:10]}
            )

            # Alert if breaking news
            if result['query_metadata']['total_results'] > 0:
                send_alert(webhook_url, f"🚨 New {company} news: {result['news_items'][0]['title']}")

    # Schedule hourly checks
    schedule.every().hour.do(check_for_news)

    while True:
        schedule.run_pending()
        time.sleep(60)
```

### Historical Trend Analysis

```python
def analyze_news_trends(company: str, years: int = 5):
    """Analyze multi-year news patterns."""

    start_date = (datetime.now() - timedelta(days=365*years)).isoformat()[:10]

    result = scrape_pharma_news(
        company=company,
        keywords=["Phase 3", "FDA approval", "acquisition"],
        filters={"start_date": start_date}
    )

    # Analyze trends
    news_by_year = {}
    for item in result['news_items']:
        year = item['published_date'][:4]
        news_by_year[year] = news_by_year.get(year, 0) + 1

    # Plot
    import matplotlib.pyplot as plt
    years_list = sorted(news_by_year.keys())
    counts = [news_by_year[y] for y in years_list]

    plt.figure(figsize=(10, 6))
    plt.bar(years_list, counts, color='steelblue')
    plt.xlabel('Year')
    plt.ylabel('News Items')
    plt.title(f'{company} News Volume Over Time')
    plt.savefig(f'{company}_news_trends.png')
```

---

## Future Enhancements

1. **Multilingual support**: Scrape non-English company sites (China, Japan, EU)
2. **Audio/video transcription**: Extract insights from earnings calls, conferences
3. **Social media monitoring**: Track Twitter, LinkedIn for informal announcements
4. **Predictive alerts**: ML model to predict newsworthy events before official release
5. **Competitive comparison**: Side-by-side news volume, sentiment across competitors
6. **Knowledge graph**: Build entity relationship network from news corpus

---

## References

- **RSS Feed Standards**: https://www.rssboard.org/rss-specification
- **Google News RSS**: https://news.google.com/
- **BERT Sentiment Analysis**: https://huggingface.co/finiteautomata/bertweet-base-sentiment-analysis
- **SpaCy NER**: https://spacy.io/usage/linguistic-features#named-entities
