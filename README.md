# BCT FinOps Tool

**Enterprise Cloud Financial Operations & Optimization Platform**

A comprehensive AI-powered platform that analyzes AWS accounts and provides intelligent cost optimization recommendations, resource utilization insights, and financial operations management.

## 🚀 Streamlit Cloud Deployment

### Quick Deploy
1. Push this repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app" and select your repository
4. Main file: `streamlit_app.py`
5. Click "Deploy"

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
streamlit run streamlit_app.py
```

## 📋 Features

### Core Modules
- **🏠 Dashboard**: Executive summary with key metrics and resource overview
- **🌍 Global View**: Multi-region resource distribution with region selector
- **📊 KPI**: Comprehensive Key Performance Indicators dashboard
- **💡 Recommendations**: AI-powered cost optimization suggestions with priority scoring
- **🗂️ Resources**: Detailed analysis across 7 resource types
- **💰 Savings Plans**: Reserved Instances and Savings Plans recommendations
- **📈 Analytics**: EC2 rightsizing with detailed instance recommendations
- **📄 Reports**: Export to PDF, Excel, and Word formats

### Resource Analysis
- **💾 Idle Resources**: Unattached EBS, unused Elastic IPs, idle Load Balancers
- **💻 EC2 Instances**: Rightsizing recommendations with savings calculations
- **📦 S3**: Storage optimization, lifecycle policies, cost analysis
- **🗄️ RDS**: Underutilized instances, Reserved Instance opportunities
- **⚡ Lambda**: Memory optimization, unused function cleanup
- **☸️ Containers**: EKS clusters and ECS services analysis
- **🗃️ Databases**: DynamoDB, ElastiCache, Redshift optimization

### AI-Powered Insights
- Priority scoring (1-100) based on impact and ROI
- Detailed implementation steps
- Risk assessment and prerequisites
- Difficulty ratings (Easy/Medium/Hard/Complex)
- Estimated savings and timeline

## 🔐 Authentication

**Default Credentials:**
- Username: `admin`
- Password: `admin123`

**Demo Mode:** Try without credentials

## 📊 AWS Services Analyzed

- EC2 Instances & Rightsizing
- S3 Storage & Lifecycle
- RDS Databases
- Lambda Functions
- EKS Clusters
- ECS Services
- DynamoDB Tables
- ElastiCache
- Redshift
- Cost Explorer
- Budget Alerts
- Idle Resources

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **AWS SDK**: Boto3
- **AI**: AWS Bedrock (Claude)
- **Visualization**: Plotly, Pandas
- **Reports**: ReportLab, python-docx, openpyxl

## 📦 Project Structure

```
.
├── streamlit_app.py          # Main application
├── requirements.txt          # Python dependencies
├── .streamlit/
│   └── config.toml          # Streamlit configuration
├── src/
│   ├── enhanced_analyzer.py      # AWS analysis engine
│   ├── enhanced_ai_recommender.py # AI recommendations
│   ├── auth_manager.py           # Authentication
│   ├── cache_manager.py          # Session caching
│   ├── export_manager.py         # Excel exports
│   ├── report_generator.py       # PDF/DOCX reports
│   └── scheduler.py              # Automation
└── README.md
```

## 🔑 AWS Permissions Required

The application needs read-only access to:
- Cost Explorer: `ce:GetCostAndUsage`, `ce:GetCostForecast`
- EC2: `ec2:Describe*`
- S3: `s3:ListBucket`, `s3:GetBucketLocation`
- RDS: `rds:Describe*`
- Lambda: `lambda:List*`, `lambda:GetFunction`
- EKS: `eks:ListClusters`, `eks:DescribeCluster`
- ECS: `ecs:ListClusters`, `ecs:DescribeClusters`
- DynamoDB: `dynamodb:ListTables`, `dynamodb:DescribeTable`
- ElastiCache: `elasticache:DescribeCacheClusters`
- Redshift: `redshift:DescribeClusters`
- Bedrock: `bedrock:InvokeModel` (for AI recommendations)

## 💡 Usage Tips

1. **First Time**: Use the Login tab to enter AWS credentials
2. **Analysis**: Click "Analyze Account" to scan your AWS infrastructure
3. **Review**: Check Dashboard and KPI for overview
4. **Optimize**: Review Recommendations for cost savings
5. **Export**: Generate reports from the Reports tab

## 🎯 Cost Efficiency Score

The KPI dashboard includes a Cost Efficiency Score (0-100) calculated based on:
- Total resources vs idle resources
- Optimization opportunities
- Underutilized instances

**Score Ranges:**
- 90-100: Excellent ✅
- 75-89: Good 👍
- 60-74: Fair ⚠️
- 0-59: Needs Improvement 🚨

## 📝 Notes

- Cost Explorer must be enabled in AWS Billing Console (takes 24 hours to populate)
- Analysis covers the last 6 months of usage data
- Credentials are stored only in browser session (not saved to disk)
- Re-run analysis weekly for updated recommendations

## 🤝 Support

For issues or questions, please refer to the documentation or contact your administrator.

---

**Built with ❤️ for Cloud Financial Operations**
