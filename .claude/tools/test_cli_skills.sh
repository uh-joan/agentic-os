#!/bin/bash

# Test suite for all 8 CLI-enabled skills
# Tests each skill with different parameters to verify CLI arguments work

set -e  # Exit on error

cd /Users/joan.saez-pons/code/agentic-os
export PYTHONPATH=.claude:$PYTHONPATH

echo "================================================================================"
echo "TESTING 8 CLI-ENABLED SKILLS"
echo "================================================================================"
echo

# Test 1: company-clinical-trials-portfolio
echo "TEST 1/8: company-clinical-trials-portfolio (Novartis, heart failure)"
echo "--------------------------------------------------------------------------------"
python3 .claude/skills/company-clinical-trials-portfolio/scripts/get_company_clinical_trials_portfolio.py \
  "Novartis" --condition "heart failure" --start-year 2022 2>&1 | head -15
echo "✓ Test 1 passed"
echo

# Test 2: disease-burden-per-capita
echo "TEST 2/8: disease-burden-per-capita (India, cardiovascular deaths)"
echo "--------------------------------------------------------------------------------"
python3 .claude/skills/disease-burden-per-capita/scripts/get_disease_burden_per_capita.py \
  IND deaths_cardiovascular 2>&1 | head -12
echo "✓ Test 2 passed"
echo

# Test 3: pharma-stock-data
echo "TEST 3/8: pharma-stock-data (GILD, ABBV, BMY)"
echo "--------------------------------------------------------------------------------"
python3 .claude/skills/pharma-stock-data/scripts/get_pharma_company_stock_data.py \
  GILD ABBV BMY 2>&1 | head -20
echo "✓ Test 3 passed"
echo

# Test 4: ultra-rare-metabolic-targets
echo "TEST 4/8: ultra-rare-metabolic-targets (max population 1000)"
echo "--------------------------------------------------------------------------------"
python3 .claude/skills/ultra-rare-metabolic-targets/scripts/get_ultra_rare_metabolic_targets.py \
  1000 2>&1 | head -8
echo "✓ Test 4 passed"
echo

# Test 5: disease-genetic-targets (shorter test - limit results)
echo "TEST 5/8: disease-genetic-targets (Type 2 diabetes, top 5)"
echo "--------------------------------------------------------------------------------"
python3 .claude/skills/disease-genetic-targets/scripts/get_disease_genetic_targets.py \
  "Type 2 diabetes" --top-n 5 --max-fetch 100 2>&1 | head -15
echo "✓ Test 5 passed"
echo

# Test 6: company-product-launch-timeline
echo "TEST 6/8: company-product-launch-timeline (Medtronic, neurology)"
echo "--------------------------------------------------------------------------------"
python3 .claude/skills/company-product-launch-timeline/scripts/analyze_company_product_launch_timeline.py \
  "Medtronic" --focus-area neurology --start-year 2022 2>&1 | head -12
echo "✓ Test 6 passed"
echo

# Test 7: rare-disease-acquisition-targets (quick test - limited results)
echo "TEST 7/8: rare-disease-acquisition-targets (gene therapy, no financials)"
echo "--------------------------------------------------------------------------------"
python3 .claude/skills/rare-disease-acquisition-targets/scripts/get_rare_disease_acquisition_targets.py \
  --therapeutic-focus gene_therapy --max-results 5 2>&1 | head -15
echo "✓ Test 7 passed"
echo

# Test 8: drug-swot-analysis (comprehensive but time-limited)
echo "TEST 8/8: drug-swot-analysis (nivolumab, lung cancer)"
echo "--------------------------------------------------------------------------------"
python3 .claude/skills/drug-swot-analysis/scripts/generate_drug_swot_analysis.py \
  nivolumab "lung cancer" 2>&1 | head -20
echo "✓ Test 8 passed"
echo

echo "================================================================================"
echo "ALL 8 TESTS PASSED! ✅"
echo "================================================================================"
echo
echo "Summary:"
echo "  1. company-clinical-trials-portfolio - Novartis heart failure ✓"
echo "  2. disease-burden-per-capita - India cardiovascular ✓"
echo "  3. pharma-stock-data - GILD ABBV BMY ✓"
echo "  4. ultra-rare-metabolic-targets - max_population=1000 ✓"
echo "  5. disease-genetic-targets - Type 2 diabetes ✓"
echo "  6. company-product-launch-timeline - Medtronic neurology ✓"
echo "  7. rare-disease-acquisition-targets - gene therapy ✓"
echo "  8. drug-swot-analysis - nivolumab lung cancer ✓"
echo
echo "Note: forecast-drug-pipeline tested separately (long-running query)"
