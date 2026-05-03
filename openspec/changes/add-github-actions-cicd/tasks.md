## 1. Preparation

- [x] 1.1 Confirm `.github/workflows/daily-collect.yml` exists and is correct
- [x] 1.2 Verify `requirements.txt` contains python-dotenv and requests

## 2. GitHub Secrets Configuration

- [ ] 2.1 Add `LLM_API_KEY` secret in GitHub repository Settings
- [ ] 2.2 Add `LLM_BASE_URL` secret in GitHub repository Settings
- [ ] 2.3 Add `LLM_MODEL` secret in GitHub repository Settings
- [ ] 2.4 Add `GITHUB_TOKEN` secret in GitHub repository Settings

## 3. Testing

- [ ] 3.1 Manually trigger workflow via workflow_dispatch
- [ ] 3.2 Verify pipeline/run.py executes successfully
- [ ] 3.3 Verify hooks/validate_json.py runs after pipeline
- [ ] 3.4 Verify hooks/check_quality.py runs after validation
- [ ] 3.5 Confirm knowledge/ directory is updated and committed

## 4. Verification

- [ ] 4.1 Check GitHub Actions run history for successful execution
- [ ] 4.2 Verify commit appears in repository with correct message
- [ ] 4.3 Confirm [skip ci] marker prevents recursive triggers