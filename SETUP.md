# Setup Guide

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Configure Environment Variables (Optional)

You can optionally create a `.env` file to configure:

```bash
# Optional: AWS Bedrock Model ID (default: Claude 3 Sonnet)
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0

# Optional: Default AWS Region
AWS_DEFAULT_REGION=us-east-1
```

Available Bedrock models:
- `anthropic.claude-3-sonnet-20240229-v1:0` (recommended - balanced)
- `anthropic.claude-3-haiku-20240307-v1:0` (faster, cheaper)
- `anthropic.claude-3-opus-20240229-v1:0` (most capable, expensive)

## Step 3: AWS Credentials Setup

### Option A: Create IAM User (Recommended)

1. Go to AWS IAM Console
2. Create a new IAM user
3. Attach the policy from `aws_iam_policy.json`
4. Generate access keys
5. Save the Access Key ID and Secret Access Key

### Option B: Use Existing Credentials

Ensure your AWS credentials have the required permissions listed in `aws_iam_policy.json`

## Step 4: Enable Cost Explorer

1. Go to AWS Billing Console
2. Navigate to Cost Explorer
3. Enable Cost Explorer (may take 24 hours to populate data)

## Step 5: Run the Application

```bash
python main.py
```

Enter your AWS credentials when prompted.

## Troubleshooting

### "Cost Explorer not enabled"
- Enable Cost Explorer in AWS Billing Console
- Wait 24 hours for data to populate

### "Access Denied" errors
- Verify IAM permissions match the policy
- Check if Cost Explorer is enabled
- Ensure credentials are correct

### "Bedrock access denied"
- Ensure Bedrock is enabled in your AWS account
- Request model access in Bedrock console
- Verify IAM permissions include bedrock:InvokeModel
- Check you're using a supported region (us-east-1 recommended)

## Cost Considerations

- Cost Explorer API: ~$0.01 per request
- AWS Bedrock (Claude 3 Sonnet): ~$0.003-0.015 per report
- Total estimated cost per report: < $0.05
