"""
Export Manager
Handle exports to Excel, JSON, CSV and integrations with Slack, Jira
"""

import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
import xlsxwriter
from io import BytesIO

class ExportManager:
    def __init__(self):
        """Initialize export manager"""
        pass
    
    def export_to_excel(
        self,
        cost_data: Dict,
        recommendations: List[Dict],
        idle_resources: Dict,
        s3_data: Dict,
        rds_data: Dict,
        output_path: str
    ) -> str:
        """Export comprehensive data to Excel with multiple sheets"""
        
        # Create Excel writer
        writer = pd.ExcelWriter(output_path, engine='xlsxwriter')
        workbook = writer.book
        
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1
        })
        
        money_format = workbook.add_format({'num_format': '$#,##0.00'})
        percent_format = workbook.add_format({'num_format': '0.00%'})
        
        # Sheet 1: Executive Summary
        summary_data = {
            'Metric': [
                'Total Cost (6 months)',
                'Monthly Average',
                'Total Recommendations',
                'High Priority Items',
                'Idle Resource Waste',
                'Potential Monthly Savings'
            ],
            'Value': [
                f"${cost_data.get('total_cost', 0):,.2f}",
                f"${cost_data.get('total_cost', 0) / 6:,.2f}",
                len(recommendations),
                sum(1 for r in recommendations if r.get('severity') in ['Critical', 'High']),
                f"${idle_resources.get('total_monthly_waste', 0):,.2f}",
                f"${self._calculate_total_savings(recommendations):,.2f}"
            ]
        }
        
        df_summary = pd.DataFrame(summary_data)
        df_summary.to_excel(writer, sheet_name='Executive Summary', index=False)
        
        # Sheet 2: Recommendations
        rec_data = []
        for rec in recommendations:
            rec_data.append({
                'Priority Score': rec.get('priority_score', 0),
                'Title': rec.get('title', ''),
                'Severity': rec.get('severity', ''),
                'Category': rec.get('category', ''),
                'Estimated Savings': rec.get('estimated_savings', ''),
                'Timeline': rec.get('timeline', ''),
                'Difficulty': rec.get('difficulty', ''),
                'ROI (months)': rec.get('roi_months', ''),
                'Description': rec.get('description', ''),
                'Impact': rec.get('impact', '')
            })
        
        df_recommendations = pd.DataFrame(rec_data)
        df_recommendations.to_excel(writer, sheet_name='Recommendations', index=False)
        
        # Sheet 3: Idle Resources
        idle_data = []
        
        for vol in idle_resources.get('ebs_volumes', []):
            idle_data.append({
                'Type': 'EBS Volume',
                'Resource ID': vol['volume_id'],
                'Details': f"{vol['size_gb']} GB {vol['type']}",
                'Monthly Cost': vol['monthly_cost'],
                'Created': vol['created']
            })
        
        for ip in idle_resources.get('elastic_ips', []):
            idle_data.append({
                'Type': 'Elastic IP',
                'Resource ID': ip['public_ip'],
                'Details': 'Unassociated',
                'Monthly Cost': ip['monthly_cost'],
                'Created': 'N/A'
            })
        
        for lb in idle_resources.get('load_balancers', []):
            idle_data.append({
                'Type': 'Load Balancer',
                'Resource ID': lb['name'],
                'Details': lb['type'],
                'Monthly Cost': lb['monthly_cost'],
                'Created': 'N/A'
            })
        
        if idle_data:
            df_idle = pd.DataFrame(idle_data)
            df_idle.to_excel(writer, sheet_name='Idle Resources', index=False)
        
        # Sheet 4: S3 Analysis
        if s3_data.get('storage_details'):
            df_s3 = pd.DataFrame(s3_data['storage_details'])
            df_s3.to_excel(writer, sheet_name='S3 Storage', index=False)
        
        # Sheet 5: RDS Analysis
        if rds_data.get('instances'):
            df_rds = pd.DataFrame(rds_data['instances'])
            df_rds.to_excel(writer, sheet_name='RDS Instances', index=False)
        
        # Sheet 6: Implementation Roadmap
        roadmap_data = []
        for rec in sorted(recommendations, key=lambda x: x.get('priority_score', 0), reverse=True)[:20]:
            roadmap_data.append({
                'Priority': rec.get('priority_score', 0),
                'Action': rec.get('title', ''),
                'Timeline': rec.get('timeline', ''),
                'Savings': rec.get('estimated_savings', ''),
                'Difficulty': rec.get('difficulty', ''),
                'First Step': rec.get('steps', [''])[0] if rec.get('steps') else ''
            })
        
        df_roadmap = pd.DataFrame(roadmap_data)
        df_roadmap.to_excel(writer, sheet_name='Implementation Roadmap', index=False)
        
        # Format all sheets
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            worksheet.set_column('A:Z', 20)  # Set column width
        
        writer.close()
        
        return output_path
    
    def export_to_json(
        self,
        cost_data: Dict,
        recommendations: List[Dict],
        idle_resources: Dict,
        all_data: Dict,
        output_path: str
    ) -> str:
        """Export all data to JSON format"""
        
        export_data = {
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_cost_6months': cost_data.get('total_cost', 0),
                'monthly_average': cost_data.get('total_cost', 0) / 6,
                'total_recommendations': len(recommendations),
                'idle_resource_waste': idle_resources.get('total_monthly_waste', 0)
            },
            'recommendations': recommendations,
            'idle_resources': idle_resources,
            'detailed_analysis': all_data
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        return output_path
    
    def export_to_csv(
        self,
        recommendations: List[Dict],
        output_path: str
    ) -> str:
        """Export recommendations to CSV"""
        
        df = pd.DataFrame(recommendations)
        df.to_csv(output_path, index=False)
        
        return output_path
    
    def _calculate_total_savings(self, recommendations: List[Dict]) -> float:
        """Calculate total potential monthly savings"""
        total = 0
        
        for rec in recommendations:
            savings_str = rec.get('estimated_savings', '')
            
            # Extract numeric value from strings like "$1,234/month"
            try:
                # Remove currency symbols and text
                numeric_str = savings_str.replace('$', '').replace(',', '').split('/')[0].strip()
                if numeric_str and numeric_str[0].isdigit():
                    total += float(numeric_str)
            except:
                continue
        
        return total


class IntegrationManager:
    def __init__(self):
        """Initialize integration manager"""
        pass
    
    def send_to_slack(
        self,
        webhook_url: str,
        summary: Dict,
        top_recommendations: List[Dict]
    ) -> bool:
        """Send summary to Slack"""
        try:
            from slack_sdk.webhook import WebhookClient
            
            webhook = WebhookClient(webhook_url)
            
            # Build message
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "💰 AWS Cost Optimization Report"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Total Cost (6mo):*\n${summary.get('total_cost', 0):,.2f}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Monthly Average:*\n${summary.get('monthly_avg', 0):,.2f}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Recommendations:*\n{summary.get('total_recs', 0)}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Potential Savings:*\n${summary.get('potential_savings', 0):,.2f}/mo"
                        }
                    ]
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Top 5 Recommendations:*"
                    }
                }
            ]
            
            # Add top recommendations
            for i, rec in enumerate(top_recommendations[:5], 1):
                severity_emoji = {
                    'Critical': '🔴',
                    'High': '🟠',
                    'Medium': '🟡',
                    'Low': '🟢'
                }
                
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"{severity_emoji.get(rec.get('severity', 'Medium'), '⚪')} *{rec.get('title', '')}*\n"
                                f"💰 {rec.get('estimated_savings', 'N/A')} | ⏱️ {rec.get('timeline', 'N/A')}"
                    }
                })
            
            response = webhook.send(blocks=blocks)
            return response.status_code == 200
            
        except Exception as e:
            print(f"Error sending to Slack: {e}")
            return False
    
    def create_jira_tickets(
        self,
        jira_url: str,
        jira_email: str,
        jira_token: str,
        project_key: str,
        recommendations: List[Dict],
        max_tickets: int = 10
    ) -> List[str]:
        """Create Jira tickets for top recommendations"""
        try:
            from jira import JIRA
            
            jira = JIRA(
                server=jira_url,
                basic_auth=(jira_email, jira_token)
            )
            
            created_tickets = []
            
            # Create tickets for top recommendations
            for rec in recommendations[:max_tickets]:
                # Build description
                description = f"""
h2. Description
{rec.get('description', '')}

h2. Estimated Savings
{rec.get('estimated_savings', 'N/A')}

h2. Timeline
{rec.get('timeline', 'N/A')}

h2. Difficulty
{rec.get('difficulty', 'N/A')}

h2. Impact
{rec.get('impact', '')}

h2. Implementation Steps
"""
                
                for i, step in enumerate(rec.get('steps', []), 1):
                    description += f"\n# {step}"
                
                if rec.get('risks'):
                    description += "\n\nh2. Risks\n"
                    for risk in rec['risks']:
                        description += f"\n* {risk}"
                
                # Map severity to priority
                priority_map = {
                    'Critical': 'Highest',
                    'High': 'High',
                    'Medium': 'Medium',
                    'Low': 'Low'
                }
                
                issue_dict = {
                    'project': {'key': project_key},
                    'summary': rec.get('title', 'Cost Optimization'),
                    'description': description,
                    'issuetype': {'name': 'Task'},
                    'priority': {'name': priority_map.get(rec.get('severity', 'Medium'), 'Medium')},
                    'labels': ['cost-optimization', 'aws', rec.get('category', '').lower()]
                }
                
                new_issue = jira.create_issue(fields=issue_dict)
                created_tickets.append(new_issue.key)
            
            return created_tickets
            
        except Exception as e:
            print(f"Error creating Jira tickets: {e}")
            return []
    
    def send_email_report(
        self,
        smtp_server: str,
        smtp_port: int,
        sender_email: str,
        sender_password: str,
        recipient_emails: List[str],
        subject: str,
        summary: Dict,
        pdf_path: Optional[str] = None
    ) -> bool:
        """Send email report with optional PDF attachment"""
        try:
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            from email.mime.application import MIMEApplication
            
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = ', '.join(recipient_emails)
            msg['Subject'] = subject
            
            # HTML body
            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h1 style="color: #4472C4;">AWS Cost Optimization Report</h1>
                    <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    
                    <h2>Executive Summary</h2>
                    <table style="border-collapse: collapse; width: 100%;">
                        <tr style="background-color: #f2f2f2;">
                            <td style="padding: 10px; border: 1px solid #ddd;"><strong>Total Cost (6 months)</strong></td>
                            <td style="padding: 10px; border: 1px solid #ddd;">${summary.get('total_cost', 0):,.2f}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border: 1px solid #ddd;"><strong>Monthly Average</strong></td>
                            <td style="padding: 10px; border: 1px solid #ddd;">${summary.get('monthly_avg', 0):,.2f}</td>
                        </tr>
                        <tr style="background-color: #f2f2f2;">
                            <td style="padding: 10px; border: 1px solid #ddd;"><strong>Total Recommendations</strong></td>
                            <td style="padding: 10px; border: 1px solid #ddd;">{summary.get('total_recs', 0)}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border: 1px solid #ddd;"><strong>Potential Monthly Savings</strong></td>
                            <td style="padding: 10px; border: 1px solid #ddd; color: green; font-weight: bold;">
                                ${summary.get('potential_savings', 0):,.2f}
                            </td>
                        </tr>
                    </table>
                    
                    <p style="margin-top: 20px;">
                        Please review the attached detailed report for comprehensive analysis and recommendations.
                    </p>
                    
                    <p style="color: #666; font-size: 12px; margin-top: 30px;">
                        This is an automated report from AWS Cost Optimization Analyzer.
                    </p>
                </body>
            </html>
            """
            
            msg.attach(MIMEText(html_body, 'html'))
            
            # Attach PDF if provided
            if pdf_path:
                with open(pdf_path, 'rb') as f:
                    pdf_attachment = MIMEApplication(f.read(), _subtype='pdf')
                    pdf_attachment.add_header('Content-Disposition', 'attachment', 
                                            filename=pdf_path.split('/')[-1])
                    msg.attach(pdf_attachment)
            
            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
