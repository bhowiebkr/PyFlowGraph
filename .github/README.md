# GitHub Actions Workflows

This directory contains the automated workflows for PyFlowGraph.

## Workflows

### 1. `windows-build.yml` - Build Windows App
**Triggers:**
- Push to tags (`v*`) - Creates build artifacts
- Pull requests to main - Validates builds

**What it does:**
- Builds the Windows application with Nuitka
- For tag pushes: Stores the build as a workflow artifact
- For PRs: Just validates that the build works

**Artifacts:**
- Tag builds create artifacts named `PyFlowGraph-Windows-v1.0.0` (example)
- Artifacts are kept for 90 days
- No public release is created automatically

### 2. `create-release.yml` - Create Release (Manual)
**Triggers:**
- Manual workflow dispatch only

**What it does:**
- Downloads a previously built artifact by tag name
- Creates a public GitHub release with that artifact
- Generates changelog automatically

**Inputs:**
- `tag_name`: Which tag version to release (e.g., v1.0.0)
- `release_type`: Choose "release" or "prerelease"  
- `make_latest`: Whether to mark as the latest release

## Development Workflow

### For Regular Development
1. Create pull requests as normal
2. The build workflow will validate your changes
3. No artifacts are created for PRs

### For Creating Releases
1. **Tag your release:**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **Automatic build:**
   - GitHub Actions will build automatically
   - Build artifact is stored (not released)
   - Check the Actions tab for build status

3. **Test the build:**
   - Go to Actions → find your build run
   - Download the artifact zip file
   - Test locally to verify everything works

4. **Create the release:**
   - Go to Actions → "Create Release" workflow
   - Click "Run workflow"
   - Enter your tag name (e.g., v1.0.0)
   - Choose release type and options
   - Click "Run workflow"

5. **Release published:**
   - The workflow downloads your tested build
   - Creates a public GitHub release
   - Attaches the verified zip file

## Benefits

✅ **Safe releases**: Test builds before they become public  
✅ **No mistakes**: Prevents accidental releases from experimental tags  
✅ **Full automation**: Once approved, release creation is automatic  
✅ **PR validation**: Ensures pull requests don't break builds  
✅ **Flexible**: Can delay, skip, or retry releases as needed

## Troubleshooting

### "Artifact not found" error
- Make sure the tag exists and was pushed to GitHub
- Verify the build workflow completed successfully
- Check that the tag name matches exactly (including 'v' prefix)

### Build failures
- Check the build logs in the Actions tab
- Common issues: missing dependencies, syntax errors, import problems
- PR builds help catch issues before tagging

### Release workflow fails
- Ensure you have write permissions to the repository
- Verify the artifact exists and hasn't expired (90 day limit)
- Check that the tag name is entered correctly