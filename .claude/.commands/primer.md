# Primer Command

**Purpose**: Initialize project context files from a source document (transcript, summary, or initial context) to set up the pharma assistant for a new project.

**Usage**: `/primer <source_file_path>`

**Parameters**:
- `source_file_path` (required): Path to the source file containing project information (e.g., transcript, conversation summary, project brief)

---

## Workflow

### Step 1: Read Foundation Files
Read the following files to understand the repository structure and atomic agent architecture:
- `.claude/CLAUDE.md` (if exists) - Project instructions and agent architecture
- `README.md` (if exists) - Repository overview

### Step 2: Read Source File
Read the provided source file to extract:
- **Project overview**: Company, decision maker, strategic question
- **Program details**: Lead compounds, indication, therapeutic area
- **Decision criteria**: Key parameters for decision-making
- **Timeline**: Decision timeline and milestones
- **User profile**: Decision maker background, expertise, communication preferences

### Step 3: Generate Context Files

**CRITICAL - Timeline Adjustment**:
Before creating context files, get the current date using `mcp__time-mcp-server__get_current_time` (timezone: "Europe/London" or appropriate timezone).

If the source document contains past dates or timelines:
- **Recalculate** all timelines relative to current date
- **Flag** to user that timelines were adjusted from source document
- **Example**: If source says "May 15, 2025 decision" but current date is October 15, 2025:
  - Adjust to "October 2025 decision" (current) or "Q1 2026 decision" (future)
  - Note: "Timeline adjusted from source document (May 2025 → October 2025)"

Create/update the following context files based on the source file content:

**Root directory files**:
- `project-brief.md`: Strategic question, background, lead compounds, decision criteria, expected outputs, token budget, **adjusted timeline**
- `user-profile.md`: Decision maker profile, background, expertise, decision-making style, expected deliverables, communication preferences
- `PROJECT_WORKFLOW.md`: 5-phase workflow guide with queries, expected outputs, verification steps, troubleshooting, **current-date-relative milestones**

**.claude/ directory file**:
- `.claude/project-context.md`: Agent-facing strategic context, decision framework, MCP integrations, file organization, success criteria

### Step 4: Validate Context Files
After creating the files, verify:
- All 4 context files are created with appropriate content
- Company name, decision maker, and strategic question are consistent across files
- Lead compounds/programs are clearly defined
- Decision criteria are quantified where possible
- File paths match the expected structure

### Step 5: Summary Report
Provide a summary of:
- **Project Purpose**: What decision needs to be made
- **Key Stakeholder**: Decision maker name and role
- **Timeline**: Decision deadline
- **Context Files Created**: List of files with byte counts
- **Next Step**: Recommend running `/create-plan` to generate Task Master workflow

---

## Example Usage

```bash
/primer kras_project_transcript.md
```

**Expected Output**:
```
✅ Read foundation files (.claude/CLAUDE.md, README.md)
✅ Extracted project information from source file
✅ Created project-brief.md (7,908 bytes)
✅ Created user-profile.md (12,869 bytes)
✅ Created PROJECT_WORKFLOW.md (25,937 bytes)
✅ Created .claude/project-context.md (17,758 bytes)

📋 Project Summary:
- Purpose: Select next-gen KRAS G12C lead for IND-enabling studies
- Stakeholder: Adrian Gill, Ph.D., EVP Discovery Chemistry (Revolution Medicines)
- Timeline: Q1 2026 decision (IND filing Q3 2026)

📁 Context Files Ready:
- project-brief.md: Strategic scenario and decision criteria
- user-profile.md: Adrian Gill's background and expectations
- PROJECT_WORKFLOW.md: 5-phase workflow with 12 queries
- .claude/project-context.md: Agent-facing decision framework

➡️  Next Step: Run `/create-plan` to generate Task Master workflow
```

---

## Notes

- This command only creates context files; it does NOT create Task Master tasks
- The source file can be in any format (markdown, text, conversation transcript)
- If context files already exist, they will be OVERWRITTEN
- Ensure the source file contains sufficient detail for all 4 context files
- The command will infer missing information where possible but may ask for clarification

---

## Related Commands

- `/create-plan` - Generate Task Master workflow from context files using pharma-search-orchestrator
