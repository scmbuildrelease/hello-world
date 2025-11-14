# Package & Release Workflow

**Audience**: Release engineers and maintainers  
**Purpose**: Document the complete process for building, tagging, and releasing, combining automation and manual steps.

## 1. Overview

The release process is a hybrid of manual and automated steps designed to ensure controlled, reproducible, and high-quality releases. **Only the merge from main → stable is manual**; all tagging, building, testing, and publishing steps are handled automatically through CI.

```
Manual Step (only one)
┌────────────────────────────────────────────────┐
│ Create PR: merge main → stable with (MINOR)    │
│ Merge locally, accept all from main            │
└────────────────────────────────────────────────┘
              ↓ push stable
CI automations:
  • Create semantic version tag (dev/rc/prod)
  • Build and run tests
  • Generate changelog & release notes
  • Create GitHub Release (draft for RC, published for prod)
  • Auto-trigger prod after successful RC
```

## 2. Branching and Versioning Policy

### Branches

- **main**: Integration branch containing the latest validated work
- **stable**: Production branch updated only via main → stable promotion

### Commit/PR Message Policy

Merge commit and PR title **must contain** version bump indicator:
- `(MINOR)` - New features (0.31.0 → 0.32.0)
- `(MAJOR)` - Breaking changes (0.32.0 → 1.0.0)
- `(PATCH)` - Bug fixes (0.32.0 → 0.32.1)

**Example**: `release: (MINOR) Promote main → stable (2025-11-14)`

### Tag Types

- **dev**: `vX.Y.Z-devYYYYMMDD` — Nightly/development builds
- **rc**: `vX.Y.Z-rcN` — Release candidates
- **prod**: `vX.Y.Z` — Final production releases

## 3. Manual Promotion (Main → Stable)

### 3.1 Update VERSION File

```bash
cd /path/to/project
echo "0.32.0" > VERSION
git add VERSION
git commit -m "Bump version to 0.32.0"
git push origin main
```

### 3.2 Create the PR

1. Create PR with `base = stable`, `compare = main`
2. Add `(MINOR)` in both title and description
3. **Do not merge via GitHub UI** (for large changesets)

### 3.3 Merge Locally (Accept All from Main)

```bash
git fetch origin
git checkout stable
git merge -X theirs origin/main -m "release: (MINOR) Promote main → stable"
git push origin stable
```

**Notes**:
- `-X theirs` = main branch takes priority
- CI automatically triggers Package & Release workflow

## 4. Recovery Playbook (If Build Fails)

If CI build fails after merge, resync code files from main:

```bash
git fetch origin
git checkout stable
git checkout origin/main -- '**/*.py' '**/*.c' '**/*.cpp' '**/*.hpp'
git add -A
git commit -m "fix: resync code files from main after bad auto-merge"
git push origin stable
```

Re-run CI and confirm green build.

## 5. Automated CI Workflows

### 5.1 Triggers

| Trigger | Condition | Result |
|---------|-----------|--------|
| **Schedule** | Daily @ 00:00 UTC | Creates dev build |
| **Push to main** | With/without (MINOR) | Creates dev build |
| **Push to stable** | After manual merge | Creates RC |
| **workflow_dispatch** | Manual trigger | Create dev/rc/prod |

### 5.2 Key Jobs

#### release-precheck
- Determines release type (dev/rc/prod)
- Checks for semantic version indicators
- Validates if release should be created
- Outputs: `release-type`, `should-create-release`, `bump-type`

#### build-and-test
- Runs all tests (Python, C)
- Validates code quality
- Must pass before tag creation

#### create-tag
- Calculates semantic version from VERSION file
- Creates appropriate tag (dev/rc/prod)
- Force-updates if tag exists
- Supports dry-run mode

#### create-changelog
- Generates changelog from git commits
- Compares with previous tag
- Outputs markdown for GitHub Release

#### create-release
- Creates GitHub Release
- Draft for RC, published for prod
- Includes generated changelog

#### trigger-prod-after-rc-success
- **Automatically promotes RC → prod**
- Triggers when RC build succeeds
- No manual intervention needed

### 5.3 Tag Format Examples

```
Dev:  v0.32.0-dev20251114
RC:   v0.32.0-rc1, v0.32.0-rc2, ...
Prod: v0.32.0
```

### 5.4 Dry-Run Semantics

A dry-run simulates the full release without publishing:

```bash
GitHub Actions → Package and Release → Run workflow
→ release-type: rc
→ dry-run: true
→ Run workflow
```

**During dry-run**:
- ✅ All builds and tests run
- ✅ Tags are calculated
- ❌ Tags are NOT pushed
- ❌ Releases are NOT created
- ✅ Artifacts generated for inspection

## 6. Monthly Release Process (Cadence)

Release cadence: 1 month, ending on **N = Friday, 17:00 (EOD)**

### N − 30 Days: Start of Cadence

1. **Bump Version**
   ```bash
   echo "0.32.0" > VERSION
   git add VERSION
   git commit -m "#1234: (MINOR) Bump version for new release cycle"
   git push origin main
   ```

2. **Validate Workflow**
   - Run Package & Release workflow manually
   - Ensure dev builds work correctly

### N − 29 to N − 7 Days: Generate RCs on Main

- **Nightly runs create dev tags automatically**
- Dev tags: `v0.32.0-dev20251114`, `v0.32.0-dev20251115`, ...

### N − 7 to N − 1 Days: Stabilization

1. **Merge main → stable**
   ```bash
   git checkout stable
   git merge -X theirs origin/main -m "release: (MINOR) Promote main → stable"
   git push origin stable
   ```

2. **RC Tags Created Automatically**
   - First RC: `v0.32.0-rc1`
   - CI runs, tests, creates draft release

3. **Fix Failures and Re-run**
   - Monitor pipeline for failures
   - Fix deterministic failures:
     * Cherry-pick fix from main
     * Or patch directly on stable
   - Re-run workflow until green
   - Each re-run creates new RC: rc2, rc3, etc.

### N − 1 Day: Final Candidate

- **Final fix is in stable branch**
- Ensure all pipelines green ✅
- Verify changelog and release notes

### N (Release Day)

- **Release triggers automatically** after successful RC
- `trigger-prod-after-rc-success` job promotes RC → prod
- Creates final tag: `v0.32.0`
- Publishes GitHub Release

**Validation**:
- ✅ GitHub Release published
- ✅ Tag `v0.32.0` exists
- ✅ All tests green

## 7. Workflow Inputs

### Manual Trigger Options

```yaml
release-type:
  - dev: Development build
  - rc: Release candidate  
  - prod: Production release

dry-run:
  - true: Simulate without publishing
  - false: Real release (default)
```

### Usage Examples

**Create RC manually**:
```
Actions → Package and Release → Run workflow
→ release-type: rc
→ dry-run: false
```

**Test workflow without publishing**:
```
Actions → Package and Release → Run workflow
→ release-type: rc
→ dry-run: true
```

## 8. Troubleshooting

| Problem | Symptom | Resolution |
|---------|---------|------------|
| **Tag already exists** | Tag mismatch | Auto force-updates; verify SHA |
| **Build breaks after merge** | Compile/import errors | Use resync recipe (section 4) |
| **RC instability** | Flaky tests | Re-run; coordinate with test owners |
| **Deterministic RC failure** | Same test fails | Cherry-pick fix from main |
| **No new commits** | Workflow exits early | Check branch/ref; expected behavior |

## 9. Definition of Done

✅ Tag created and matches intended commit  
✅ All tests pass  
✅ GitHub Release created  
✅ Changelog generated  
✅ After main → stable merge, everything else is automated

## 10. Git Tips & Rationale

**Conflict strategy**: Use `git merge -X theirs origin/main` to prioritize main's changes when merging into stable.

**Targeted resync**: Use `git checkout origin/main -- '**/*.py' '**/*.c'` to restore authoritative code files after a bad merge.

**Force tag updates**: Tags are automatically force-updated if they exist, preventing conflicts.

## 11. Security & Permissions

**Required permissions**:
- `contents: write` - Create tags and releases
- `actions: write` - Trigger workflows
- `packages: write` - Publish artifacts

**Tokens**:
- Uses `GITHUB_TOKEN` (automatically provided)
- No additional secrets required for basic workflow
