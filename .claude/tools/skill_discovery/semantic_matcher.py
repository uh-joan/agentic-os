"""
Level 3: Semantic Matching (Smart)

Find skills that match intent, not just exact names. Uses scoring algorithm
to identify skills that could be reused or adapted for new requirements.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class SkillRequirements:
    """Requirements for a skill to fulfill."""
    therapeutic_area: str
    data_type: str  # 'trials' | 'fda_drugs' | 'patents' | 'publications'
    filters: Optional[dict] = None  # {'phase': 'PHASE3', 'status': 'recruiting', 'location': 'US'}
    servers: Optional[list[str]] = None
    query: Optional[str] = None  # Original user query for trigger keyword matching


@dataclass
class SkillMatch:
    """A skill that matches the requirements."""
    skill: dict
    score: int
    match_type: str  # 'exact' | 'therapeutic_area' | 'data_type' | 'pattern'
    reason: str


def find_matching_skill(requirements: SkillRequirements) -> Optional[SkillMatch]:
    """Find skill that semantically matches requirements.

    Scoring:
        10 points: Exact therapeutic area match
        8 points:  Same data type + server
        5 points:  Has required patterns (e.g., pagination)
        3 points:  Appropriate complexity for filters
        2 points:  Same category

    Args:
        requirements: Skill requirements to match

    Returns:
        Best matching skill with score ≥5, or None
    """
    index_path = Path('.claude/skills/index.json')
    if not index_path.exists():
        return None

    index = json.loads(index_path.read_text())
    candidates = []

    # Build candidate list (filter by data type)
    for skill in index.get('skills', []):
        if requirements.data_type == 'trials':
            if 'ct_gov_mcp' in skill.get('servers_used', []):
                candidates.append(skill)
        elif requirements.data_type == 'fda_drugs':
            if 'fda_mcp' in skill.get('servers_used', []):
                candidates.append(skill)
        elif requirements.servers:
            # Custom server requirement
            if any(s in skill.get('servers_used', []) for s in requirements.servers):
                candidates.append(skill)

    # Score candidates
    for candidate in candidates:
        score = 0
        reasons = []

        # Trigger keyword match (HIGHEST PRIORITY - checks user intent)
        if requirements.query and 'trigger_keywords' in candidate:
            query_lower = requirements.query.lower()
            for keyword in candidate['trigger_keywords']:
                keyword_lower = keyword.lower()
                # Check both exact substring match and fuzzy match (all words present)
                if keyword_lower in query_lower:
                    score += 15
                    reasons.append(f"Trigger keyword match: '{keyword}'")
                    break
                else:
                    # Fuzzy match: check if all significant words in keyword are in query
                    # Skip common stopwords
                    stopwords = {'a', 'an', 'the', 'of', 'in', 'on', 'at', 'by', 'for', 'with', 'is', 'are'}
                    keyword_words = set(w for w in keyword_lower.split() if w not in stopwords)
                    query_words = set(requirements.query.lower().split())

                    if keyword_words and keyword_words.issubset(query_words):
                        score += 15
                        reasons.append(f"Trigger keyword match (fuzzy): '{keyword}'")
                        break  # Only count one trigger match

        # Exact therapeutic area match (case-insensitive)
        if requirements.therapeutic_area.lower() in candidate['name'].lower():
            score += 10
            reasons.append(f"Therapeutic area match: {requirements.therapeutic_area}")

        # Same data type (check both name and server)
        data_type_match = False
        if requirements.data_type in candidate['name']:
            score += 8
            reasons.append(f"Data type match: {requirements.data_type}")
            data_type_match = True
        elif not data_type_match:
            # Check if skill uses the right server (for generic skills)
            if requirements.data_type == 'trials' and 'ct_gov_mcp' in candidate.get('servers_used', []):
                score += 8
                reasons.append(f"Data type match (server): trials via ct_gov_mcp")
            elif requirements.data_type == 'fda_drugs' and 'fda_mcp' in candidate.get('servers_used', []):
                score += 8
                reasons.append(f"Data type match (server): fda_drugs via fda_mcp")
            elif requirements.data_type == 'patents' and 'uspto_patents_mcp' in candidate.get('servers_used', []):
                score += 8
                reasons.append(f"Data type match (server): patents via uspto_patents_mcp")
            elif requirements.data_type == 'publications' and 'pubmed_mcp' in candidate.get('servers_used', []):
                score += 8
                reasons.append(f"Data type match (server): publications via pubmed_mcp")

        # Has required patterns
        if requirements.filters:
            # Need pagination for large datasets
            if 'pagination' in candidate.get('patterns_demonstrated', []):
                score += 5
                reasons.append("Has pagination pattern")

            # Need filtering for complex queries
            filter_count = len(requirements.filters)
            if filter_count > 2 and 'multi_filter' in candidate.get('patterns_demonstrated', []):
                score += 3
                reasons.append(f"Supports complex filtering ({filter_count} filters)")

        # Complexity match
        if requirements.filters:
            expected_complexity = 'medium' if len(requirements.filters) > 2 else 'simple'
            if candidate.get('complexity') == expected_complexity:
                score += 3
                reasons.append(f"Appropriate complexity: {expected_complexity}")

        # Same category
        if requirements.data_type == 'trials' and candidate.get('category') == 'clinical-trials':
            score += 2
            reasons.append("Category match: clinical-trials")
        elif requirements.data_type == 'fda_drugs' and candidate.get('category') == 'drug-discovery':
            score += 2
            reasons.append("Category match: drug-discovery")

        candidate['_match_score'] = score
        candidate['_match_reasons'] = reasons

    # Sort by score and return best match
    candidates.sort(key=lambda x: x.get('_match_score', 0), reverse=True)

    if not candidates or candidates[0]['_match_score'] < 5:
        return None

    best = candidates[0]
    match_type = 'exact' if best['_match_score'] >= 10 else \
                 'therapeutic_area' if best['_match_score'] >= 8 else \
                 'data_type' if best['_match_score'] >= 5 else 'pattern'

    return SkillMatch(
        skill=best,
        score=best['_match_score'],
        match_type=match_type,
        reason='; '.join(best['_match_reasons'])
    )


def main():
    """CLI interface for semantic matching."""
    import argparse

    parser = argparse.ArgumentParser(description='Find semantically matching skills')
    parser.add_argument('--therapeutic-area', required=True, help='Therapeutic area (e.g., "KRAS inhibitor")')
    parser.add_argument('--data-type', required=True, choices=['trials', 'fda_drugs', 'patents', 'publications'], help='Data type')
    parser.add_argument('--filters', help='JSON dict of filters')
    parser.add_argument('--servers', help='Comma-separated list of servers')
    parser.add_argument('--query', help='Original user query for trigger keyword matching')
    parser.add_argument('--json', action='store_true', help='Output JSON')

    args = parser.parse_args()

    filters = json.loads(args.filters) if args.filters else None
    servers = args.servers.split(',') if args.servers else None

    requirements = SkillRequirements(
        therapeutic_area=args.therapeutic_area,
        data_type=args.data_type,
        filters=filters,
        servers=servers,
        query=args.query
    )

    match = find_matching_skill(requirements)

    if args.json:
        if match:
            result = {
                'skill': match.skill,
                'score': match.score,
                'match_type': match.match_type,
                'reason': match.reason
            }
            print(json.dumps(result, indent=2))
        else:
            print(json.dumps({'match': None}, indent=2))
    else:
        if match:
            print(f"Best Match: {match.skill['name']}")
            print(f"  Score: {match.score}")
            print(f"  Match Type: {match.match_type}")
            print(f"  Reason: {match.reason}")
            print(f"  Script: {match.skill.get('script', 'unknown')}")
            print(f"  Patterns: {', '.join(match.skill.get('patterns_demonstrated', []))}")
        else:
            print(f"No matching skill found for {args.therapeutic_area} {args.data_type}")
            print("Consider creating a new skill")

    return 0 if match else 1


if __name__ == "__main__":
    exit(main())
