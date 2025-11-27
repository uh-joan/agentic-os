"""
Level 4: Strategy Decision Tree

Decide whether to REUSE, ADAPT, or CREATE a skill based on index queries,
health checks, and semantic matching. Provides actionable execution plan.
"""

import json
import re
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

try:
    from .index_query import find_skill_in_index
    from .health_check import verify_skill_health, HealthStatus
    from .semantic_matcher import find_matching_skill, SkillRequirements
except ImportError:
    # Running as script
    sys.path.insert(0, str(Path(__file__).parent))
    from index_query import find_skill_in_index
    from health_check import verify_skill_health, HealthStatus
    from semantic_matcher import find_matching_skill, SkillRequirements


def normalize_skill_name(name: str) -> str:
    """Normalize skill name for fuzzy matching.

    Removes common prefixes, converts to lowercase, replaces separators.

    Examples:
        'get_copd_fda_timeline' -> 'copd fda timeline'
        'fda-approvals-timeline-by-indication' -> 'fda approvals timeline indication'
        'generate_drug_swot_analysis' -> 'drug swot analysis'
    """
    # Remove common prefixes
    prefixes = ['get_', 'generate_', 'analyze_', 'create_', 'fetch_']
    name_lower = name.lower()
    for prefix in prefixes:
        if name_lower.startswith(prefix):
            name_lower = name_lower[len(prefix):]
            break

    # Replace separators with spaces
    normalized = re.sub(r'[-_]', ' ', name_lower)

    # Remove extra whitespace
    normalized = ' '.join(normalized.split())

    return normalized


def fuzzy_match_skill_name(query_name: str, index_path: Path = Path('.claude/skills/index.json')) -> Optional[dict]:
    """Find skill using fuzzy name matching.

    Args:
        query_name: Skill name to search for
        index_path: Path to index.json

    Returns:
        Best matching skill or None
    """
    if not index_path.exists():
        return None

    index = json.loads(index_path.read_text())
    skills = index.get('skills', [])

    normalized_query = normalize_skill_name(query_name)
    query_tokens = set(normalized_query.split())

    best_match = None
    best_score = 0

    for skill in skills:
        skill_name = skill.get('name', '')
        normalized_skill = normalize_skill_name(skill_name)
        skill_tokens = set(normalized_skill.split())

        # Calculate token overlap
        common = query_tokens & skill_tokens
        total = query_tokens | skill_tokens

        if total:
            score = len(common) / len(total)

            # Bonus for exact substring match
            if normalized_query in normalized_skill or normalized_skill in normalized_query:
                score += 0.3

            if score > best_score:
                best_score = score
                best_match = skill

    # Return if good enough match (>= 60% similarity)
    if best_score >= 0.6:
        return best_match

    return None


def extract_params_from_query(query: str) -> dict:
    """Extract parameters from natural language query.

    Simple pattern matching - not LLM-based.

    Args:
        query: Natural language query

    Returns:
        Dict with extracted params: skill_name, therapeutic_area, data_type, etc.
    """
    query_lower = query.lower()

    # Extract data type
    data_type = None
    if any(word in query_lower for word in ['trial', 'trials', 'study', 'studies']):
        data_type = 'trials'
    elif any(word in query_lower for word in ['fda', 'drug', 'approved', 'approval']):
        data_type = 'fda_drugs'
    elif any(word in query_lower for word in ['patent', 'ip', 'intellectual property']):
        data_type = 'patents'
    elif any(word in query_lower for word in ['publication', 'pubmed', 'paper', 'literature']):
        data_type = 'publications'
    elif any(word in query_lower for word in ['swot', 'competitive', 'landscape']):
        data_type = 'strategic_analysis'
    elif any(word in query_lower for word in ['revenue', 'financial', 'stock', 'market cap']):
        data_type = 'financial_analysis'

    # Extract therapeutic area (capitalized words that aren't common words)
    stop_words = {'get', 'the', 'for', 'and', 'or', 'of', 'in', 'with', 'by', 'from',
                  'what', 'how', 'many', 'which', 'are', 'is'}

    words = query.split()
    therapeutic_area = None
    for word in words:
        clean_word = re.sub(r'[^\w\s]', '', word)
        if clean_word and clean_word.lower() not in stop_words:
            # Check if it's an acronym (all caps) or proper noun
            if clean_word.isupper() or (len(clean_word) > 2 and clean_word[0].isupper()):
                therapeutic_area = clean_word
                break

    # Generate skill name from query (keep important keywords like timeline, trial, fda)
    skill_tokens = []
    for word in query.lower().split():
        clean = re.sub(r'[^\w]', '', word)
        if clean and clean not in stop_words and len(clean) > 2:
            skill_tokens.append(clean)

    skill_name = '_'.join(skill_tokens[:5]) if skill_tokens else 'unknown_skill'

    return {
        'skill_name': skill_name,
        'therapeutic_area': therapeutic_area or 'unspecified',
        'data_type': data_type or 'trials',
        'query': query
    }


class SkillStrategy(Enum):
    """Strategy for obtaining required skill."""
    REUSE = "reuse"      # Use existing skill as-is
    ADAPT = "adapt"      # Modify existing skill
    CREATE = "create"    # Create new skill from reference


@dataclass
class StrategyDecision:
    """Decision on how to obtain required skill."""
    strategy: SkillStrategy
    skill: Optional[dict]          # For reuse/adapt
    reference: Optional[dict]      # For create (pattern reference)
    reason: str
    action_plan: list[str]
    debug: Optional[dict] = None   # Debug information

    def to_dict(self) -> dict:
        """Convert to dict for JSON serialization."""
        result = {
            'strategy': self.strategy.value,
            'skill': self.skill,
            'reference': self.reference,
            'reason': self.reason,
            'action_plan': self.action_plan
        }
        if self.debug:
            result['debug'] = self.debug
        return result


def find_best_reference(requirements: SkillRequirements) -> dict:
    """Find best skill to use as reference for creating new skill.

    Uses pattern_categories in index to identify best references.

    Args:
        requirements: Skill requirements

    Returns:
        Reference skill metadata
    """
    index_path = Path('.claude/skills/index.json')
    if not index_path.exists():
        return {}

    index = json.loads(index_path.read_text())

    # Determine pattern category
    pattern_categories = index.get('pattern_categories', {})

    if requirements.data_type == 'trials':
        pattern_cat = pattern_categories.get('ct_gov_queries', {})
    elif requirements.data_type == 'fda_drugs':
        pattern_cat = pattern_categories.get('fda_queries', {})
    elif requirements.data_type == 'strategic_analysis':
        pattern_cat = pattern_categories.get('strategic_analysis', {})
    elif requirements.data_type == 'financial_analysis':
        pattern_cat = pattern_categories.get('financial_analysis', {})
    elif requirements.data_type == 'competitive_intelligence':
        pattern_cat = pattern_categories.get('competitive_intelligence', {})
    elif requirements.data_type == 'target_validation':
        pattern_cat = pattern_categories.get('target_validation', {})
    elif requirements.data_type == 'patents':
        pattern_cat = pattern_categories.get('patent_queries', {})
    elif requirements.data_type == 'publications':
        pattern_cat = pattern_categories.get('pubmed_queries', {})
    else:
        # Default to most comprehensive
        pattern_cat = pattern_categories.get('pagination', {})

    best_ref_name = pattern_cat.get('best_reference')

    if best_ref_name:
        # Find reference skill metadata
        for skill in index.get('skills', []):
            if skill['name'] == best_ref_name:
                return skill

    # Fallback: return first skill in pattern category
    for skill in index.get('skills', []):
        if skill['name'] in pattern_cat.get('skills', []):
            return skill

    # Last resort: return first skill matching data type
    for skill in index.get('skills', []):
        if requirements.data_type == 'trials' and 'ct_gov_mcp' in skill.get('servers_used', []):
            return skill
        elif requirements.data_type == 'fda_drugs' and 'fda_mcp' in skill.get('servers_used', []):
            return skill

    # Ultimate fallback: return first skill in index
    skills = index.get('skills', [])
    return skills[0] if skills else {}


def determine_skill_strategy(
    skill_name: str,
    requirements: SkillRequirements
) -> StrategyDecision:
    """Determine best strategy for obtaining required skill.

    Decision tree:
        1. Exact match exists and healthy? → REUSE
        2. Fuzzy match exists and healthy? → REUSE (with note)
        3. Exact/fuzzy match exists but degraded? → ADAPT (migrate structure)
        4. Exact/fuzzy match exists but broken? → CREATE (from scratch)
        5. Semantic match exists and healthy? → ADAPT (fork and modify)
        6. No match? → CREATE (using best reference pattern)

    Args:
        skill_name: Name of skill needed
        requirements: Skill requirements

    Returns:
        StrategyDecision with action plan
    """

    debug_info = {
        'skill_name_query': skill_name,
        'exact_match_found': False,
        'fuzzy_match_found': False,
        'semantic_match_found': False
    }

    # Step 1: Check for exact match
    exact_match = find_skill_in_index(skill_name)
    if exact_match:
        debug_info['exact_match_found'] = True
        debug_info['exact_match_name'] = exact_match.get('name')

    if exact_match:
        health = verify_skill_health(exact_match)

        if health.status == HealthStatus.HEALTHY:
            return StrategyDecision(
                strategy=SkillStrategy.REUSE,
                skill=exact_match,
                reference=None,
                reason=f"Skill '{skill_name}' exists and is healthy",
                action_plan=[
                    f"Execute: .claude/skills/{exact_match['script']}",
                    "No modifications needed"
                ],
                debug=debug_info
            )

        elif health.status == HealthStatus.DEGRADED:
            return StrategyDecision(
                strategy=SkillStrategy.ADAPT,
                skill=exact_match,
                reference=None,
                reason=f"Skill '{skill_name}' exists but needs improvement: {', '.join(health.issues)}",
                action_plan=[
                    *health.recommendations,
                    "Test execution after fixes",
                    "Update index with new health status"
                ],
                debug=debug_info
            )

        else:  # BROKEN
            reference = find_best_reference(requirements)
            return StrategyDecision(
                strategy=SkillStrategy.CREATE,
                skill=None,
                reference=reference,
                reason=f"Skill '{skill_name}' is broken: {', '.join(health.issues)}. Recreating from scratch.",
                action_plan=[
                    f"Remove broken skill files",
                    f"Task(pharma-search-specialist) with reference: {reference.get('name', 'unknown')}",
                    "Agent reads reference pattern and regenerates skill",
                    "Save new skill and update index"
                ],
                debug=debug_info
            )

    # Step 1.5: Try fuzzy match if exact match failed
    fuzzy_match = fuzzy_match_skill_name(skill_name)
    if fuzzy_match:
        debug_info['fuzzy_match_found'] = True
        debug_info['fuzzy_match_name'] = fuzzy_match.get('name')

        health = verify_skill_health(fuzzy_match)

        if health.status == HealthStatus.HEALTHY:
            return StrategyDecision(
                strategy=SkillStrategy.REUSE,
                skill=fuzzy_match,
                reference=None,
                reason=f"Fuzzy matched skill '{fuzzy_match['name']}' (queried as '{skill_name}') - healthy and ready to use",
                action_plan=[
                    f"Execute: .claude/skills/{fuzzy_match['script']}",
                    f"Note: Matched via fuzzy name matching (normalized names match)"
                ],
                debug=debug_info
            )

    # Step 2: Check for semantic match
    semantic_match = find_matching_skill(requirements)
    if semantic_match:
        debug_info['semantic_match_found'] = True
        debug_info['semantic_match_name'] = semantic_match.skill.get('name')
        debug_info['semantic_match_score'] = semantic_match.score

    if semantic_match and semantic_match.score >= 8:
        health = verify_skill_health(semantic_match.skill)

        if health.status == HealthStatus.HEALTHY:
            # Check if this is a generic skill
            if semantic_match.skill.get('is_generic'):
                return StrategyDecision(
                    strategy=SkillStrategy.REUSE,
                    skill=semantic_match.skill,
                    reference=None,
                    reason=f"Generic skill '{semantic_match.skill['name']}' can handle this query. {semantic_match.reason}",
                    action_plan=[
                        f"Execute generic skill: .claude/skills/{semantic_match.skill['script']}",
                        f"Pass parameters: term='{requirements.therapeutic_area}'",
                        "No new skill creation needed - generic skill handles this use case"
                    ],
                    debug=debug_info
                )

            # Non-generic skill - needs adaptation
            return StrategyDecision(
                strategy=SkillStrategy.ADAPT,
                skill=semantic_match.skill,
                reference=None,
                reason=f"Similar skill '{semantic_match.skill['name']}' found (score: {semantic_match.score}). {semantic_match.reason}",
                action_plan=[
                    f"Read: .claude/skills/{semantic_match.skill['script']}",
                    f"Fork skill and adapt for: {requirements.therapeutic_area}",
                    "Modify query parameters for new therapeutic area",
                    "Test execution with new parameters",
                    "Save as new skill and update index"
                ],
                debug=debug_info
            )

    # Step 3: No match - create from best reference
    reference = find_best_reference(requirements)

    return StrategyDecision(
        strategy=SkillStrategy.CREATE,
        skill=None,
        reference=reference,
        reason=f"No matching skill found for '{skill_name}'. Creating new skill using '{reference.get('name', 'unknown')}' as reference pattern.",
        action_plan=[
            f"Task(pharma-search-specialist) with:",
            f"  - Query: {requirements.therapeutic_area} {requirements.data_type}",
            f"  - Reference pattern: {reference.get('name', 'unknown')}",
            f"  - Required patterns: {', '.join(reference.get('patterns_demonstrated', []))}",
            "Agent generates new skill following reference patterns",
            "Agent executes and verifies (closed loop)",
            "Main agent saves skill files",
            "Update index with new skill entry"
        ],
        debug=debug_info
    )


def main():
    """CLI interface for strategy decisions."""
    import argparse

    parser = argparse.ArgumentParser(description='Determine skill strategy')

    # Either use --query (natural language) OR structured params (--skill, --therapeutic-area, --data-type)
    parser.add_argument('--query', help='Natural language query (alternative to structured params)')
    parser.add_argument('--skill', help='Skill name needed (required if not using --query)')
    parser.add_argument('--therapeutic-area', help='Therapeutic area (required if not using --query)')
    parser.add_argument('--data-type',
                        choices=['trials', 'fda_drugs', 'patents', 'publications',
                                'strategic_analysis', 'financial_analysis', 'competitive_intelligence', 'target_validation'],
                        help='Data type (required if not using --query)')
    parser.add_argument('--filters', help='JSON dict of filters')
    parser.add_argument('--servers', help='Comma-separated list of servers')
    parser.add_argument('--json', action='store_true', help='Output JSON')

    args = parser.parse_args()

    # Extract parameters from query or use structured params
    if args.query:
        extracted = extract_params_from_query(args.query)
        skill_name = extracted['skill_name']
        therapeutic_area = extracted['therapeutic_area']
        data_type = extracted['data_type']
    else:
        if not args.skill or not args.therapeutic_area or not args.data_type:
            parser.error('--skill, --therapeutic-area, and --data-type are required when not using --query')
        skill_name = args.skill
        therapeutic_area = args.therapeutic_area
        data_type = args.data_type

    filters = json.loads(args.filters) if args.filters else None
    servers = args.servers.split(',') if args.servers else None

    requirements = SkillRequirements(
        therapeutic_area=therapeutic_area,
        data_type=data_type,
        filters=filters,
        servers=servers
    )

    decision = determine_skill_strategy(skill_name, requirements)

    if args.json:
        print(json.dumps(decision.to_dict(), indent=2))
    else:
        print(f"Strategy: {decision.strategy.value.upper()}")
        print(f"Reason: {decision.reason}")
        print()
        print("Action Plan:")
        for i, step in enumerate(decision.action_plan, 1):
            print(f"  {i}. {step}")
        print()
        if decision.skill:
            print(f"Target Skill: {decision.skill['name']}")
            print(f"  Script: {decision.skill.get('script', 'unknown')}")
        if decision.reference:
            print(f"Reference Skill: {decision.reference.get('name', 'unknown')}")
            print(f"  Script: {decision.reference.get('script', 'unknown')}")
            print(f"  Patterns: {', '.join(decision.reference.get('patterns_demonstrated', []))}")

    return 0


if __name__ == "__main__":
    exit(main())
