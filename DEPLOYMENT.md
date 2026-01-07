# Streamlit Cloud Deployment Checklist

## ✅ Pre-Deployment Checklist

### Files Cleaned Up
- [x] Removed old app versions (app.py, app_bct.py, app_enhanced.py)
- [x] Removed test files (test_connection.py)
- [x] Removed generated reports (*.pdf, *.xlsx, *.docx)
- [x] Removed batch files (*.bat, *.sh)
- [x] Removed main.py (duplicate)

### Required Files Present
- [x] `streamlit_app.py` - Main application
- [x] `requirements.txt` - Python dependencies
- [x] `README.md` - Documentation
- [x] `.gitignore` - Git ignore rules
- [x] `src/` folder - All source modules
- [x] `.streamlit/config.toml` - Streamlit configuration

### Git Repository
- [ ] Initialize git (if not done): `git init`
- [ ] Add files: `git add .`
- [ ] Commit: `git commit -m "Initial commit for Streamlit deployment"`
- [ ] Create GitHub repository
- [ ] Add remote: `git remote add origin <your-repo-url>`
- [ ] Push: `git push -u origin main`

## 🚀 Deployment Steps

### 1. Streamlit Cloud Setup
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"

### 2. App Configuration
- **Repository**: Select your GitHub repository
- **Branch**: main (or master)
- **Main file path**: `streamlit_app.py`
- **App URL**: Choose a custom URL (optional)

### 3. Advanced Settings (Optional)
- **Python version**: 3.9 or higher
- **Secrets**: Add AWS credentials if needed (not recommended for security)

### 4. Deploy
- Click "Deploy!"
- Wait for deployment (usually 2-5 minutes)
- Your app will be live at: `https://your-app-name.streamlit.app`

## 🔒 Security Considerations

### DO NOT commit to Git:
- `.env` file (already in .gitignore)
- AWS credentials
- API keys
- Passwords

### For Production:
1. Use Streamlit Secrets for sensitive data
2. Implement proper authentication
3. Use IAM roles instead of access keys when possible
4. Enable MFA on AWS accounts
5. Regularly rotate credentials

## 📊 Post-Deployment

### Testing
- [ ] Test login functionality
- [ ] Test AWS credential input
- [ ] Run a sample analysis
- [ ] Test all navigation tabs
- [ ] Test report generation
- [ ] Verify AI recommendations work

### Monitoring
- Check Streamlit Cloud logs for errors
- Monitor app performance
- Track user feedback

### Updates
To update your deployed app:
```bash
git add .
git commit -m "Update description"
git push origin main
```
Streamlit Cloud will automatically redeploy.

## 🆘 Troubleshooting

### Common Issues

**App won't start:**
- Check requirements.txt for missing dependencies
- Verify Python version compatibility
- Check Streamlit Cloud logs

**Import errors:**
- Ensure all files in `src/` folder are present
- Check for typos in import statements

**AWS connection fails:**
- Verify AWS credentials are correct
- Check IAM permissions
- Ensure Cost Explorer is enabled

**Slow performance:**
- Implement caching with `@st.cache_data`
- Optimize data loading
- Consider pagination for large datasets

## 📝 Environment Variables

If using Streamlit Secrets, add to `.streamlit/secrets.toml` (locally) or Streamlit Cloud dashboard:

```toml
# Example (DO NOT use in production)
[aws]
access_key_id = "YOUR_ACCESS_KEY"
secret_access_key = "YOUR_SECRET_KEY"
region = "us-east-1"
```

## 🎉 Success!

Your BCT FinOps Tool is now deployed and accessible worldwide!

**Next Steps:**
1. Share the URL with your team
2. Set up monitoring and alerts
3. Gather user feedback
4. Plan regular updates and improvements

---

**Deployment Date:** _____________________
**Deployed By:** _____________________
**App URL:** _____________________

## AWS App Runner Deployment (containerized)

### Overview
- This repository includes a `Dockerfile` and a GitHub Actions workflow at `.github/workflows/deploy-app-runner.yml` which build a container, push it to ECR, and create/update an App Runner service.

### Quick commands (replace placeholders)
```bash
# Create ECR repo (optional)
aws ecr create-repository --repository-name bct-finops-agent --region $AWS_REGION

# Login, build, tag, push
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.$AWS_REGION.amazonaws.com
docker build -t bct-finops-agent .
docker tag bct-finops-agent:latest <ACCOUNT_ID>.dkr.ecr.$AWS_REGION.amazonaws.com/bct-finops-agent:latest
docker push <ACCOUNT_ID>.dkr.ecr.$AWS_REGION.amazonaws.com/bct-finops-agent:latest

# Create App Runner (one-off) or update from workflow
aws apprunner create-service --service-name bct-finops-agent --source-configuration 'ImageRepository={ImageIdentifier="<ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/bct-finops-agent:latest",ImageRepositoryType="ECR",ImageConfiguration={Port="8080"}}'
```

### GitHub Actions
- Workflow: `.github/workflows/deploy-app-runner.yml`
- Required secrets: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `AWS_ACCOUNT_ID`, and optionally `APP_RUNNER_SERVICE_ARN` to update an existing service.
- Optional secret for private ECR: `APP_RUNNER_ACCESS_ROLE_ARN` — when set, the workflow will pass this role ARN to App Runner so it can pull from private ECR repositories (see steps below).
- Prefer using GitHub OIDC or a minimal IAM user/role with ECR/App Runner permissions.

### If your image is in a private ECR repository
App Runner needs permission to pull private images. Create an IAM role App Runner can assume and give it ECR read permissions, then set the role ARN as the `APP_RUNNER_ACCESS_ROLE_ARN` repository secret.

Quick role example (replace placeholders):

```bash
# Trust policy (save as trust.json)
cat > trust.json <<'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": { "Service": "build.apprunner.amazonaws.com" },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create role
aws iam create-role --role-name AppRunnerECRAccessRole --assume-role-policy-document file://trust.json

# Attach inline policy with minimal ECR permissions (save as apprunner-ecr-policy.json)
cat > apprunner-ecr-policy.json <<'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    { "Effect": "Allow", "Action": ["ecr:GetAuthorizationToken"], "Resource": "*" },
    { "Effect": "Allow", "Action": ["ecr:BatchGetImage","ecr:GetDownloadUrlForLayer"], "Resource": "arn:aws:ecr:<REGION>:<ACCOUNT_ID>:repository/bct-finops-agent" },
    { "Effect": "Allow", "Action": ["ecr:DescribeRepositories","ecr:ListImages","ecr:DescribeImages"], "Resource": "*" }
  ]
}
EOF

aws iam put-role-policy --role-name AppRunnerECRAccessRole --policy-name AppRunnerECRPolicy --policy-document file://apprunner-ecr-policy.json

# Copy the role ARN and set it in GitHub Secrets as APP_RUNNER_ACCESS_ROLE_ARN
```

**Notes**
- The Dockerfile runs Streamlit on port `8080` and sets `STREAMLIT_SERVER_HEADLESS=true`.
- Never commit secrets — use GitHub Secrets or OIDC.
