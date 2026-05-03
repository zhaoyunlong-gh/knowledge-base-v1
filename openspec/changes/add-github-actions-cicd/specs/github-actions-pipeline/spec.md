## ADDED Requirements

### Requirement: GitHub Actions Pipeline Trigger
The system SHALL support GitHub Actions workflow with both scheduled and manual trigger mechanisms.

#### Scenario: Scheduled trigger
- **WHEN** the cron expression `0 0 * * *` fires (UTC 00:00)
- **THEN** the pipeline job SHALL be executed automatically

#### Scenario: Manual trigger
- **WHEN** user clicks "Run workflow" in GitHub Actions UI
- **THEN** the pipeline job SHALL be executed with no additional parameters

### Requirement: Pipeline Execution
The system SHALL execute the full pipeline: Collector → Analyzer → Organizer.

#### Scenario: Successful pipeline run
- **WHEN** the workflow starts
- **THEN** it SHALL install dependencies from `requirements.txt`
- **AND** it SHALL run `python pipeline/run.py` with environment variables
- **AND** it SHALL run `python hooks/validate_json.py` after pipeline completes
- **AND** it SHALL run `python hooks/check_quality.py` after validation

### Requirement: Environment Variable Management
The system SHALL inject environment variables from GitHub Secrets at runtime.

#### Scenario: Secrets injection
- **WHEN** the workflow runs
- **THEN** it SHALL make available: `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL`, `GITHUB_TOKEN`
- **AND** these values SHALL NOT be exposed in workflow logs

### Requirement: Auto-commit Results
The system SHALL automatically commit knowledge base changes to the repository after pipeline and hooks complete.

#### Scenario: Commit on changes
- **WHEN** pipeline and hooks complete successfully
- **AND** there are changes in `knowledge/` directory
- **THEN** it SHALL create a commit with message "Update knowledge base [skip ci]"
- **AND** it SHALL push the commit to the repository

#### Scenario: No commit when no changes
- **WHEN** pipeline and hooks complete
- **AND** there are no changes in `knowledge/` directory
- **THEN** it SHALL NOT create any commit