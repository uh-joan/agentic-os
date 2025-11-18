#!/usr/bin/env python3
"""
Atomic Competitive Analysis Functions

Reusable functions for pharmaceutical competitive intelligence analysis.
Based on competitive-analyst rubrics and scoring systems.
"""


def calculate_competitive_intensity(recruiting_count: int, phase3_count: int,
                                    leading_moa_count: int) -> float:
    """
    Calculate competitive intensity score (0-1000 scale)

    Formula: recruiting_count + phase3_count + (leading_moa_count / 10)

    Interpretation:
    - 700+: EXTREMELY INTENSE - Saturated market
    - 500-700: VERY INTENSE - High competition
    - 300-500: INTENSE - Moderate competition
    - <300: MODERATE - Room for new entrants

    Args:
        recruiting_count: Number of actively recruiting trials
        phase3_count: Number of Phase 3 trials
        leading_moa_count: Number of trials for leading mechanism (e.g., GLP-1)

    Returns:
        Competitive intensity score (0-1000)
    """
    return recruiting_count + phase3_count + (leading_moa_count / 10)


def assess_competitive_intensity_level(score: float) -> str:
    """
    Assess competitive intensity level from score

    Args:
        score: Competitive intensity score

    Returns:
        Assessment string (EXTREMELY INTENSE, VERY INTENSE, INTENSE, MODERATE)
    """
    if score >= 700:
        return "EXTREMELY INTENSE"
    elif score >= 500:
        return "VERY INTENSE"
    elif score >= 300:
        return "INTENSE"
    else:
        return "MODERATE"


def assess_market_maturity(phase3_count: int) -> str:
    """
    Assess market maturity based on Phase 3 trial count

    Args:
        phase3_count: Number of Phase 3 trials

    Returns:
        Market maturity level (HIGH, MODERATE, EMERGING)
    """
    if phase3_count > 50:
        return "HIGH"
    elif phase3_count > 20:
        return "MODERATE"
    else:
        return "EMERGING"


def assess_current_competition(recruiting_count: int) -> str:
    """
    Assess current competitive pressure based on recruiting trials

    Args:
        recruiting_count: Number of actively recruiting trials

    Returns:
        Competition level (VERY INTENSE, INTENSE, MODERATE, LOW)
    """
    if recruiting_count > 500:
        return "VERY INTENSE"
    elif recruiting_count > 300:
        return "INTENSE"
    elif recruiting_count > 100:
        return "MODERATE"
    else:
        return "LOW"


def assess_industry_activity(industry_pct: float) -> str:
    """
    Assess industry activity level based on industry-sponsored trial percentage

    Args:
        industry_pct: Percentage of industry-sponsored trials (0-100)

    Returns:
        Activity level (High, Moderate, Low)
    """
    if industry_pct > 50:
        return "High"
    elif industry_pct > 30:
        return "Moderate"
    else:
        return "Low"


def assess_moa_dominance(moa_pct: float) -> str:
    """
    Assess mechanism of action dominance

    Args:
        moa_pct: Percentage of trials using this MOA (0-100)

    Returns:
        Dominance level (VERY HIGH, HIGH, MODERATE, LOW)
    """
    if moa_pct > 15:
        return "VERY HIGH"
    elif moa_pct > 10:
        return "HIGH"
    elif moa_pct > 5:
        return "MODERATE"
    else:
        return "LOW"


def assess_pipeline_velocity(new_trials_per_year: float) -> str:
    """
    Assess pipeline velocity based on new trials per year

    Args:
        new_trials_per_year: Average new trials per year

    Returns:
        Velocity assessment (Accelerating, Steady, Slowing)
    """
    if new_trials_per_year > 50:
        return "Accelerating"
    elif new_trials_per_year > 30:
        return "Steady"
    else:
        return "Slowing"


def score_threat_level(phase: str, sponsor_strength: int, differentiation: int,
                       market_timing: int, genetic_precision: int) -> tuple[float, str]:
    """
    Score competitive threat level using 5-component rubric

    Based on competitive-analyst threat scoring system (Section 3).

    Args:
        phase: Trial phase (PHASE3, PHASE2, PHASE1, EARLY_PHASE1)
        sponsor_strength: 1-10 (10=top pharma, 1=early biotech)
        differentiation: 1-10 (10=breakthrough, 1=me-too)
        market_timing: 1-10 (10=1-2yr launch, 1=7+ yr)
        genetic_precision: 1-10 (10=Phase 3 genetic enrichment, 1=all-comers)

    Returns:
        Tuple of (threat_score, threat_level)
        - threat_score: 1-10 average
        - threat_level: 🔴 HIGH (7-10), 🟡 MODERATE (4-6), 🟢 LOW (1-3)
    """
    # Phase score
    phase_scores = {
        'PHASE3': 9,
        'PHASE2': 6,
        'PHASE1': 3,
        'EARLY_PHASE1': 2
    }
    phase_score = phase_scores.get(phase, 5)

    # Calculate average
    avg_score = (phase_score + sponsor_strength + differentiation +
                 market_timing + genetic_precision) / 5

    # Determine threat level
    if avg_score >= 7:
        threat_level = "🔴 HIGH"
    elif avg_score >= 4:
        threat_level = "🟡 MODERATE"
    else:
        threat_level = "🟢 LOW"

    return avg_score, threat_level


def calculate_phase_ratio(phase3_count: int, phase2_count: int) -> float:
    """
    Calculate Phase 3/2 ratio (pipeline maturity indicator)

    Interpretation:
    - >0.5: Mature pipeline (many programs advancing)
    - 0.3-0.5: Developing pipeline
    - <0.3: Early pipeline

    Args:
        phase3_count: Number of Phase 3 trials
        phase2_count: Number of Phase 2 trials

    Returns:
        Phase 3/2 ratio
    """
    if phase2_count == 0:
        return 0.0
    return phase3_count / phase2_count


def assess_pipeline_maturity(phase32_ratio: float) -> str:
    """
    Assess pipeline maturity from Phase 3/2 ratio

    Args:
        phase32_ratio: Phase 3/2 ratio

    Returns:
        Maturity assessment (mature, developing, early)
    """
    if phase32_ratio > 0.5:
        return "mature"
    elif phase32_ratio > 0.3:
        return "developing"
    else:
        return "early"


def calculate_market_concentration(competitors: list[dict]) -> tuple[str, str]:
    """
    Calculate market concentration and structure

    Args:
        competitors: List of dicts with 'name' and 'market_share' keys

    Returns:
        Tuple of (structure, concentration_analysis)
        - structure: Monopoly, Oligopoly, Fragmented
        - concentration_analysis: Description
    """
    num_competitors = len(competitors)

    if num_competitors <= 1:
        structure = "Monopoly"
        analysis = "Single dominant player, high entry barriers"
    elif num_competitors <= 4:
        structure = "Oligopoly"
        analysis = f"{num_competitors} major players, differentiation critical"
    else:
        structure = "Fragmented"
        analysis = f"{num_competitors}+ players, price pressure likely"

    return structure, analysis


def assess_threat_timeline(phase: str) -> tuple[str, str]:
    """
    Assess threat timeline based on trial phase

    Args:
        phase: Trial phase

    Returns:
        Tuple of (timeline, risk_level)
    """
    timelines = {
        'PHASE3': ('2-3 years', 'HIGH - regulatory de-risked'),
        'PHASE2': ('4-6 years', 'MODERATE - execution risk'),
        'PHASE1': ('7+ years', 'LOW - high attrition'),
        'EARLY_PHASE1': ('7+ years', 'LOW - high attrition')
    }
    return timelines.get(phase, ('Unknown', 'Unknown'))


def calculate_approval_probability(base_rate: float, sponsor_strength: int,
                                   validated_moa: bool, genetic_precision: bool) -> float:
    """
    Calculate probability-adjusted approval likelihood

    Base rates:
    - Phase 3 → Approval: 58%
    - Phase 2 → Approval: 31%

    Args:
        base_rate: Base approval probability (0-1)
        sponsor_strength: 1-10 sponsor strength score
        validated_moa: True if MOA has precedent
        genetic_precision: True if genetic biomarker enrichment

    Returns:
        Adjusted approval probability (0-1)
    """
    prob = base_rate

    # Sponsor adjustment
    if sponsor_strength >= 9:
        prob += 0.10

    # Validated MOA
    if validated_moa:
        prob += 0.05

    # Genetic precision
    if genetic_precision:
        prob += 0.15

    # Cap at 95%
    return min(prob, 0.95)
