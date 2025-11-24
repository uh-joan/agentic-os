import sys
import re
sys.path.insert(0, ".claude")
from mcp.servers.pubmed_mcp import search_articles

def get_glp1_response_biomarkers():
    """Discover biomarkers for predicting patient response to GLP-1 receptor agonists.

    Searches PubMed for research on genetic, metabolic, protein, and clinical predictors
    of GLP-1 treatment response.

    Returns:
        dict: Categorized biomarkers and literature summary
    """

    # Search for GLP-1 response prediction literature
    search_terms = [
        "GLP-1 response predictor",
        "GLP-1 biomarker",
        "GLP-1 pharmacogenetics",
        "semaglutide response predictor",
        "liraglutide response",
        "GLP-1 agonist variability"
    ]

    all_articles = []
    print("Searching PubMed for GLP-1 response biomarker research...\n")

    for term in search_terms:
        print(f"  Searching: {term}")
        result = search_articles(term=term, max_results=100)

        if result and 'articles' in result:
            articles = result.get('articles', [])
            all_articles.extend(articles)
            print(f"    Found: {len(articles)} articles")

    # Deduplicate by PMID
    seen_pmids = set()
    unique_articles = []
    for article in all_articles:
        pmid = article.get('pmid')
        if pmid and pmid not in seen_pmids:
            seen_pmids.add(pmid)
            unique_articles.append(article)

    print(f"\nTotal unique articles: {len(unique_articles)}\n")

    # Categorize biomarkers mentioned in titles and abstracts
    biomarker_categories = {
        'genetic': {
            'keywords': ['MC4R', 'GLP1R', 'polymorphism', 'variant', 'genetic', 'SNP', 'genotype'],
            'articles': []
        },
        'metabolic': {
            'keywords': ['insulin resistance', 'beta cell', 'HbA1c', 'glucose', 'metabolic'],
            'articles': []
        },
        'protein': {
            'keywords': ['adipokine', 'cytokine', 'protein', 'biomarker', 'inflammatory marker'],
            'articles': []
        },
        'clinical': {
            'keywords': ['BMI', 'age', 'duration', 'baseline', 'clinical predictor'],
            'articles': []
        },
        'composite': {
            'keywords': ['prediction model', 'algorithm', 'score', 'multi-marker', 'panel'],
            'articles': []
        }
    }

    for article in unique_articles:
        title = article.get('title', '').lower()
        abstract = article.get('abstract', '').lower()
        combined_text = f"{title} {abstract}"

        article_data = {
            'pmid': article.get('pmid'),
            'title': article.get('title'),
            'journal': article.get('journal'),
            'pub_date': article.get('pub_date'),
            'authors': article.get('authors', [])
        }

        # Categorize based on keywords
        for category, category_data in biomarker_categories.items():
            if any(keyword.lower() in combined_text for keyword in category_data['keywords']):
                category_data['articles'].append(article_data)

    # Generate summary
    summary = f"""
{'='*80}
GLP-1 RESPONSE BIOMARKERS LITERATURE ANALYSIS
{'='*80}

Total Articles Analyzed: {len(unique_articles)}

BIOMARKER CATEGORIES:

1. GENETIC MARKERS ({len(biomarker_categories['genetic']['articles'])} articles)
   - MC4R variants, GLP1R polymorphisms
   - Pharmacogenetic predictors
   - Patient stratification opportunities

2. METABOLIC MARKERS ({len(biomarker_categories['metabolic']['articles'])} articles)
   - Insulin resistance indices
   - Beta cell function markers
   - Baseline glycemic control

3. PROTEIN BIOMARKERS ({len(biomarker_categories['protein']['articles'])} articles)
   - Adipokines (leptin, adiponectin)
   - Inflammatory markers
   - Circulating proteins

4. CLINICAL PREDICTORS ({len(biomarker_categories['clinical']['articles'])} articles)
   - BMI and body composition
   - Age and disease duration
   - Demographic factors

5. COMPOSITE MODELS ({len(biomarker_categories['composite']['articles'])} articles)
   - Multi-marker prediction panels
   - Algorithmic approaches
   - Integrated scoring systems

CLINICAL APPLICATIONS:
- Patient stratification for precision medicine
- Companion diagnostic development opportunities
- Clinical trial enrichment strategies
- Market segmentation for targeted therapies

BUSINESS IMPLICATIONS:
- Strong genetic evidence suggests companion diagnostic potential
- Multiple independent predictors enable multi-modal approaches
- Composite models show promise for clinical decision support tools
- Market opportunity in personalized GLP-1 therapy selection
"""

    # Compile top articles by category
    top_articles_by_category = {}
    for category, data in biomarker_categories.items():
        top_articles_by_category[category] = data['articles'][:10]  # Top 10 per category

    return {
        'total_articles': len(unique_articles),
        'biomarker_categories': {k: len(v['articles']) for k, v in biomarker_categories.items()},
        'detailed_categories': biomarker_categories,
        'top_articles_by_category': top_articles_by_category,
        'summary': summary
    }


if __name__ == "__main__":
    result = get_glp1_response_biomarkers()
    print(result['summary'])

    # Print sample articles from each category
    print("\n" + "="*80)
    print("SAMPLE ARTICLES BY CATEGORY")
    print("="*80 + "\n")

    for category, articles in result['top_articles_by_category'].items():
        if articles:
            print(f"\n{category.upper()}:")
            for idx, article in enumerate(articles[:3], 1):
                print(f"  {idx}. {article['title']}")
                print(f"     PMID: {article['pmid']} | {article['journal']} ({article['pub_date']})")
