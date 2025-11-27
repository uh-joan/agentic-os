"""
Level 4: Strategy Decision Tree

Decide whether to REUSE, ADAPT, or CREATE a skill based on index queries,
health checks, and semantic matching. Provides actionable execution plan.
"""

import json
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

    def to_dict(self) -> dict:
        """Convert to dict for JSON serialization."""
        return {
            'strategy': self.strategy.value,
            'skill': self.skill,
            'reference': self.reference,
            'reason': self.reason,
            'action_plan': self.action_plan
        }


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
        2. Exact match exists but degraded? → ADAPT (migrate structure)
        3. Exact match exists but broken? → CREATE (from scratch)
        4. Semantic match exists and healthy? → ADAPT (fork and modify)
        5. No match? → CREATE (using best reference pattern)

    Args:
        skill_name: Name of skill needed
        requirements: Skill requirements

    Returns:
        StrategyDecision with action plan
    """

    # Step 1: Check for exact match
    exact_match = find_skill_in_index(skill_name)

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
                ]
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
                ]
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
                ]
            )

    # Step 2: Check for semantic match
    semantic_match = find_matching_skill(requirements)

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
                    ]
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
                ]
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
        ]
    )


def main():
    """CLI interface for strategy decisions."""
    import argparse

    parser = argparse.ArgumentParser(description='Determine skill strategy')
    parser.add_argument('--skill', required=True, help='Skill name needed')
    parser.add_argument('--therapeutic-area', required=True, help='Therapeutic area')
    parser.add_argument('--data-type', required=True,
                        choices=['trials', 'fda_drugs', 'patents', 'publications',
                                'strategic_analysis', 'financial_analysis', 'competitive_intelligence', 'target_validation'])
    parser.add_argument('--filters', help='JSON dict of filters')
    parser.add_argument('--servers', help='Comma-separated list of servers')
    parser.add_argument('--json', action='store_true', help='Output JSON')

    args = parser.parse_args()

    filters = json.loads(args.filters) if args.filters else None
    servers = args.servers.split(',') if args.servers else None

    requirements = SkillRequirements(
        therapeutic_area=args.therapeutic_area,
        data_type=args.data_type,
        filters=filters,
        servers=servers
    )

    decision = determine_skill_strategy(args.skill, requirements)

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
