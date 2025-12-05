"""
Enhanced AI Recommender
Advanced recommendations with priority scoring, ROI, and difficulty ratings
"""

import json
from typing import Dict, List
import boto3

class EnhancedAIRecommender:
    def __init__(self, aws_session=None):
        """Initialize Bedrock client"""
        if aws_session:
            self.bedrock_client = aws_session.client('bedrock-runtime', region_name='us-east-1')
        else:
            self.bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        self.model_id = 'anthropic.claude-3-sonnet-20240229-v1:0'
    
    def generate_enhanced_recommendations(
        self,
        cost_data: Dict,
        ri_data: Dict,
        usage_data: Dict,
        savings_plans: Dict,
        s3_data: Dict,
        rds_data: Dict,
        lambda_data: Dict,
        idle_resources: Dict,
        rightsizing: Dict
    ) -> List[Dict]:
        """Generate comprehensive AI recommendations"""
        
        # Prepare enhanced data summary
        data_summary = self._prepare_enhanced_summary(
            cost_data, ri_data, usage_data, savings_plans,
            s3_data, rds_data, lambda_data, idle_resources, rightsizing
        )
        
        # Create enhanced prompt
        prompt = f"""
        Analyze this comprehensive AWS account data and provide detailed cost optimization recommendations.
        
        Data Summary:
        {json.dumps(data_summary, indent=2)}
        
        For EACH recommendation, provide:
        1. title: Brief, actionable title
        2. description: Detailed explanation (2-3 sentences)
        3. estimated_savings: Specific dollar amount (e.g., "$1,234/month" or "$14,808/year")
        4. timeline: One of: "Immediate" (< 1 day), "Short-term" (1-2 weeks), "Medium-term" (1-3 months), "Long-term" (3-6 months)
        5. severity: One of: "Critical", "High", "Medium", "Low"
        6. impact: Business and technical impact description
        7. difficulty: One of: "Easy", "Medium", "Hard", "Complex"
        8. roi_months: Number of months to break even (integer)
        9. priority_score: Integer 1-100 (higher = more important)
        10. category: One of: "Compute", "Storage", "Database", "Network", "Serverless", "Reserved Capacity"
        11. steps: Array of specific implementation steps
        12. risks: Array of potential risks or considerations
        13. prerequisites: Array of requirements before implementation
        
        Focus on:
        - Idle resources (immediate wins)
        - Savings Plans vs Reserved Instances
        - S3 storage optimization
        - RDS rightsizing
        - Lambda optimization
        - Underutilized resources
        - Cost anomalies
        
        Prioritize recommendations by:
        1. Immediate cost savings
        2. Implementation ease
        3. Risk level
        4. ROI timeline
        
        Return as JSON with key "recommendations" containing an array of recommendation objects.
        """
        
        try:
            # Call Bedrock
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 8000,
                "temperature": 0.7,
                "messages": [
                    {
                        "role": "user",
                        "content": f"You are an AWS cost optimization expert with deep knowledge of cloud economics. {prompt}"
                    }
                ]
            }
            
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            ai_content = response_body['content'][0]['text']
            
            # Extract JSON
            if '```json' in ai_content:
                ai_content = ai_content.split('```json')[1].split('```')[0].strip()
            elif '```' in ai_content:
                ai_content = ai_content.split('```')[1].split('```')[0].strip()
            
            ai_response = json.loads(ai_content)
            ai_recommendations = ai_response.get('recommendations', [])
            
        except Exception as e:
            print(f"Warning: AI recommendation generation failed: {e}")
            ai_recommendations = []
        
        # Generate rule-based recommendations
        rule_based = self._generate_enhanced_rule_based(
            cost_data, ri_data, usage_data, savings_plans,
            s3_data, rds_data, lambda_data, idle_resources, rightsizing
        )
        
        # Merge and deduplicate
        all_recommendations = ai_recommendations + rule_based
        
        # Calculate priority scores if missing
        for rec in all_recommendations:
            if 'priority_score' not in rec:
                rec['priority_score'] = self._calculate_priority_score(rec)
        
        # Sort by priority score
        all_recommendations.sort(key=lambda x: x.get('priority_score', 0), reverse=True)
        
        return all_recommendations
    
    def _prepare_enhanced_summary(
        self, cost_data, ri_data, usage_data, savings_plans,
        s3_data, rds_data, lambda_data, idle_resources, rightsizing
    ) -> Dict:
        """Prepare comprehensive data summary"""
        return {
            'costs': {
                'total_6months': round(cost_data.get('total_cost', 0), 2),
                'monthly_average': round(cost_data.get('total_cost', 0) / 6, 2)
            },
            'reserved_instances': {
                'active_count': len(ri_data.get('current_ris', [])),
                'recommendations_count': len(ri_data.get('recommendations', {}).get('Recommendations', []))
            },
            'savings_plans': {
                'estimated_annual_savings': round(savings_plans.get('estimated_savings', 0), 2)
            },
            's3_storage': {
                'total_gb': s3_data.get('total_size_gb', 0),
                'monthly_cost': s3_data.get('estimated_monthly_cost', 0),
                'optimization_opportunities': len(s3_data.get('optimization_opportunities', []))
            },
            'rds': {
                'total_instances': rds_data.get('total_instances', 0),
                'underutilized_count': rds_data.get('underutilized_count', 0),
                'monthly_cost': rds_data.get('total_monthly_cost', 0)
            },
            'lambda': {
                'total_functions': lambda_data.get('total_functions', 0),
                'rarely_used_count': lambda_data.get('rarely_used_count', 0)
            },
            'idle_resources': {
                'total_items': idle_resources.get('total_items', 0),
                'monthly_waste': idle_resources.get('total_monthly_waste', 0),
                'ebs_volumes': len(idle_resources.get('ebs_volumes', [])),
                'elastic_ips': len(idle_resources.get('elastic_ips', [])),
                'load_balancers': len(idle_resources.get('load_balancers', []))
            },
            'rightsizing': {
                'recommendations_count': len(rightsizing.get('recommendations', [])),
                'monthly_savings': rightsizing.get('total_monthly_savings', 0)
            },
            'compute': {
                'total_instances': usage_data.get('total_instances', 0)
            }
        }
    
    def _generate_enhanced_rule_based(
        self, cost_data, ri_data, usage_data, savings_plans,
        s3_data, rds_data, lambda_data, idle_resources, rightsizing
    ) -> List[Dict]:
        """Generate enhanced rule-based recommendations"""
        recommendations = []
        
        # Idle resources - HIGHEST PRIORITY
        idle_waste = idle_resources.get('total_monthly_waste', 0)
        if idle_waste > 0:
            recommendations.append({
                'title': 'Remove Idle Resources - Immediate Savings',
                'description': f'Found {idle_resources.get("total_items", 0)} idle resources wasting ${idle_waste:.2f}/month. These include unattached EBS volumes, unassociated Elastic IPs, and idle load balancers with no healthy targets.',
                'estimated_savings': f'${idle_waste:.2f}/month (${idle_waste * 12:.2f}/year)',
                'timeline': 'Immediate',
                'severity': 'Critical',
                'impact': 'Zero business impact - these resources are not in use',
                'difficulty': 'Easy',
                'roi_months': 0,
                'priority_score': 95,
                'category': 'Network',
                'steps': [
                    'Review list of idle resources in detailed report',
                    'Verify resources are truly unused (check with teams)',
                    'Create snapshots of EBS volumes before deletion',
                    'Delete or release idle resources',
                    'Set up CloudWatch alarms to detect future idle resources'
                ],
                'risks': [
                    'Ensure EBS volumes are backed up before deletion',
                    'Verify Elastic IPs are not documented anywhere'
                ],
                'prerequisites': ['Resource inventory review', 'Team confirmation']
            })
        
        # Rightsizing recommendations
        rightsizing_savings = rightsizing.get('total_monthly_savings', 0)
        if rightsizing_savings > 100:
            recommendations.append({
                'title': 'Rightsize EC2 Instances',
                'description': f'AWS Cost Explorer identified {len(rightsizing.get("recommendations", []))} instances that can be downsized to save ${rightsizing_savings:.2f}/month without performance impact.',
                'estimated_savings': f'${rightsizing_savings:.2f}/month (${rightsizing_savings * 12:.2f}/year)',
                'timeline': 'Short-term',
                'severity': 'High',
                'impact': 'Minimal performance impact with proper testing',
                'difficulty': 'Medium',
                'roi_months': 1,
                'priority_score': 85,
                'category': 'Compute',
                'steps': [
                    'Review AWS Cost Explorer rightsizing recommendations',
                    'Analyze workload patterns for each instance',
                    'Test recommended instance types in non-production',
                    'Schedule maintenance window for production changes',
                    'Implement changes with rollback plan'
                ],
                'risks': [
                    'Performance degradation if workload patterns change',
                    'Application compatibility with smaller instance types'
                ],
                'prerequisites': ['Performance baseline', 'Testing environment', 'Rollback plan']
            })
        
        # S3 optimization
        s3_opportunities = len(s3_data.get('optimization_opportunities', []))
        if s3_opportunities > 0:
            potential_savings = s3_data.get('estimated_monthly_cost', 0) * 0.3  # 30% savings estimate
            recommendations.append({
                'title': 'Implement S3 Lifecycle Policies',
                'description': f'Found {s3_opportunities} S3 buckets without lifecycle policies. Implementing intelligent tiering and archival can reduce storage costs by 30-70%.',
                'estimated_savings': f'${potential_savings:.2f}/month (${potential_savings * 12:.2f}/year)',
                'timeline': 'Short-term',
                'severity': 'Medium',
                'impact': 'No impact on data availability, improved cost efficiency',
                'difficulty': 'Easy',
                'roi_months': 1,
                'priority_score': 75,
                'category': 'Storage',
                'steps': [
                    'Analyze object access patterns using S3 Analytics',
                    'Create lifecycle policies to transition old data to Glacier',
                    'Enable S3 Intelligent-Tiering for unpredictable access patterns',
                    'Set up expiration policies for temporary data',
                    'Monitor cost impact after 30 days'
                ],
                'risks': [
                    'Retrieval delays for archived data',
                    'Retrieval costs for frequently accessed archived data'
                ],
                'prerequisites': ['Data access pattern analysis', 'Stakeholder approval']
            })
        
        # RDS underutilization
        rds_underutilized = rds_data.get('underutilized_count', 0)
        if rds_underutilized > 0:
            rds_savings = rds_data.get('total_monthly_cost', 0) * 0.4  # 40% savings estimate
            recommendations.append({
                'title': 'Rightsize Underutilized RDS Instances',
                'description': f'{rds_underutilized} RDS instances running at <20% CPU utilization. Downsizing can save approximately 40% of RDS costs.',
                'estimated_savings': f'${rds_savings:.2f}/month (${rds_savings * 12:.2f}/year)',
                'timeline': 'Medium-term',
                'severity': 'High',
                'impact': 'Requires testing and maintenance window',
                'difficulty': 'Medium',
                'roi_months': 2,
                'priority_score': 80,
                'category': 'Database',
                'steps': [
                    'Review RDS Performance Insights for detailed metrics',
                    'Identify appropriate smaller instance types',
                    'Test in non-production environment',
                    'Create snapshot before modification',
                    'Schedule maintenance window for production changes',
                    'Monitor performance for 2 weeks post-change'
                ],
                'risks': [
                    'Database performance degradation during peak loads',
                    'Connection pool limitations with smaller instances',
                    'Downtime during instance modification'
                ],
                'prerequisites': ['Performance baseline', 'Snapshot backup', 'Maintenance window']
            })
        
        # Savings Plans
        sp_savings = savings_plans.get('estimated_savings', 0)
        if sp_savings > 1000:
            recommendations.append({
                'title': 'Purchase Compute Savings Plans',
                'description': f'Savings Plans offer up to 72% discount on compute usage. Based on your usage patterns, you can save ${sp_savings:.2f}/year with 1-year commitment.',
                'estimated_savings': f'${sp_savings / 12:.2f}/month (${sp_savings:.2f}/year)',
                'timeline': 'Immediate',
                'severity': 'High',
                'impact': 'Significant cost reduction with usage commitment',
                'difficulty': 'Easy',
                'roi_months': 0,
                'priority_score': 90,
                'category': 'Reserved Capacity',
                'steps': [
                    'Review AWS Cost Explorer Savings Plans recommendations',
                    'Analyze compute usage stability over past 60 days',
                    'Choose between Compute or EC2 Instance Savings Plans',
                    'Select 1-year or 3-year term based on commitment confidence',
                    'Purchase Savings Plans through AWS Console',
                    'Monitor utilization monthly'
                ],
                'risks': [
                    'Commitment to usage level for 1-3 years',
                    'Reduced flexibility for workload changes',
                    'Underutilization if workloads decrease'
                ],
                'prerequisites': ['Usage pattern analysis', 'Budget approval', 'Commitment strategy']
            })
        
        # Lambda cleanup
        lambda_rarely_used = lambda_data.get('rarely_used_count', 0)
        if lambda_rarely_used > 5:
            recommendations.append({
                'title': 'Clean Up Unused Lambda Functions',
                'description': f'Found {lambda_rarely_used} Lambda functions with <10 invocations in 30 days. Removing unused functions reduces clutter and potential security risks.',
                'estimated_savings': '$50-200/month (reduced complexity and management overhead)',
                'timeline': 'Short-term',
                'severity': 'Low',
                'impact': 'Improved security posture and reduced complexity',
                'difficulty': 'Easy',
                'roi_months': 1,
                'priority_score': 50,
                'category': 'Serverless',
                'steps': [
                    'Review function invocation logs',
                    'Identify truly unused vs. infrequently used functions',
                    'Check for scheduled or event-driven invocations',
                    'Archive function code to S3 before deletion',
                    'Delete unused functions',
                    'Set up CloudWatch alarms for remaining functions'
                ],
                'risks': [
                    'Accidentally deleting functions used for disaster recovery',
                    'Functions triggered by rare events'
                ],
                'prerequisites': ['Function usage audit', 'Code backup']
            })
        
        return recommendations
    
    def _calculate_priority_score(self, recommendation: Dict) -> int:
        """Calculate priority score based on multiple factors"""
        score = 50  # Base score
        
        # Severity impact
        severity_scores = {'Critical': 30, 'High': 20, 'Medium': 10, 'Low': 5}
        score += severity_scores.get(recommendation.get('severity', 'Medium'), 10)
        
        # Difficulty impact (easier = higher priority)
        difficulty_scores = {'Easy': 20, 'Medium': 10, 'Hard': 5, 'Complex': 0}
        score += difficulty_scores.get(recommendation.get('difficulty', 'Medium'), 10)
        
        # Timeline impact (faster = higher priority)
        timeline_scores = {'Immediate': 20, 'Short-term': 15, 'Medium-term': 10, 'Long-term': 5}
        score += timeline_scores.get(recommendation.get('timeline', 'Medium-term'), 10)
        
        # ROI impact (faster ROI = higher priority)
        roi_months = recommendation.get('roi_months', 6)
        if roi_months == 0:
            score += 20
        elif roi_months <= 2:
            score += 15
        elif roi_months <= 6:
            score += 10
        else:
            score += 5
        
        return min(score, 100)  # Cap at 100

    
    def _generate_ec2_sizing_recommendations(self, usage_data: Dict) -> List[Dict]:
        """Generate detailed EC2 instance sizing recommendations with AI insights"""
        recommendations = []
        
        # Instance type families and their characteristics
        instance_info = {
            't3': 'Burstable - Best for variable workloads',
            't3a': 'Burstable AMD - 10% cheaper than t3',
            'm5': 'General Purpose - Balanced compute/memory',
            'm6i': 'Latest Gen General Purpose - 15% better price/performance',
            'm6g': 'Graviton2 - 40% better price/performance',
            'c5': 'Compute Optimized - CPU-intensive workloads',
            'c6g': 'Graviton2 Compute - 40% better price/performance',
            'r5': 'Memory Optimized - Memory-intensive applications',
            'r6g': 'Graviton2 Memory - 40% better price/performance'
        }
        
        for instance in usage_data.get('instances', []):
            cpu_stats = instance.get('cpu_stats', [])
            if not cpu_stats:
                continue
            
            avg_cpu = sum(dp.get('Average', 0) for dp in cpu_stats) / len(cpu_stats)
            max_cpu = max((dp.get('Maximum', 0) for dp in cpu_stats), default=0)
            instance_type = instance.get('instance_type', '')
            instance_id = instance.get('instance_id', '')
            
            # Low utilization - downsize or switch to burstable
            if avg_cpu < 20 and max_cpu < 40:
                recommendations.append({
                    'title': f'🔽 Downsize Low-Utilization Instance: {instance_id}',
                    'description': f'Instance {instance_id} ({instance_type}) averages {avg_cpu:.1f}% CPU (max {max_cpu:.1f}%). Switch to t3/t3a burstable instances or downsize for 40-60% savings.',
                    'estimated_savings': '$50-150/month',
                    'timeline': 'Short-term',
                    'severity': 'Medium',
                    'impact': 'Significant cost reduction with minimal performance impact',
                    'difficulty': 'Easy',
                    'roi_months': 1,
                    'priority_score': 75,
                    'category': 'Compute',
                    'steps': [
                        f'📊 Current: {instance_type} - {avg_cpu:.1f}% avg CPU, {max_cpu:.1f}% max CPU',
                        '✅ Recommended: t3.medium or t3.large (burstable)',
                        '💡 Alternative: Downsize within family (e.g., m5.xlarge → m5.large)',
                        '🧪 Test in non-production environment',
                        '📈 Monitor CPU credits for burstable instances',
                        '⏰ Implement during low-traffic period'
                    ],
                    'risks': [
                        'Burstable instances may exhaust CPU credits under sustained load',
                        'Smaller instances have lower network bandwidth',
                        'May need to scale up if workload increases'
                    ],
                    'prerequisites': ['Performance baseline', 'Load testing', 'Rollback plan']
                })
            
            # Moderate utilization - optimize instance family
            elif 20 <= avg_cpu < 50:
                recommendations.append({
                    'title': f'⚡ Optimize Instance Family: {instance_id}',
                    'description': f'Instance {instance_id} ({instance_type}) has moderate utilization ({avg_cpu:.1f}% avg). Switch to Graviton-based instances (m6g/c6g/r6g) for 20-40% savings with equal or better performance.',
                    'estimated_savings': '$30-100/month',
                    'timeline': 'Medium-term',
                    'severity': 'Low',
                    'impact': 'Cost optimization without performance degradation',
                    'difficulty': 'Medium',
                    'roi_months': 2,
                    'priority_score': 60,
                    'category': 'Compute',
                    'steps': [
                        f'📊 Current: {instance_type} - {avg_cpu:.1f}% avg CPU',
                        '🚀 Recommended: Graviton-based (m6g, c6g, r6g) - 40% better price/performance',
                        '💡 Alternative: Latest gen (m6i, c6i) - 15% better price/performance',
                        '✅ Verify ARM compatibility (for Graviton)',
                        '🧪 Test in staging environment',
                        '📅 Migrate during maintenance window'
                    ],
                    'risks': [
                        'Graviton requires ARM-compatible applications',
                        'Some legacy software may not support ARM',
                        'Migration requires thorough testing'
                    ],
                    'prerequisites': ['ARM compatibility check', 'Performance testing', 'Staging validation']
                })
            
            # High utilization - upgrade or scale
            elif avg_cpu >= 70:
                recommendations.append({
                    'title': f'⚠️ High Utilization Alert: {instance_id}',
                    'description': f'CRITICAL: Instance {instance_id} ({instance_type}) running at {avg_cpu:.1f}% avg CPU (max {max_cpu:.1f}%). Immediate action needed to prevent performance issues.',
                    'estimated_savings': 'N/A - Performance & Reliability',
                    'timeline': 'Immediate',
                    'severity': 'Critical',
                    'impact': 'Prevent performance degradation and service disruptions',
                    'difficulty': 'Medium',
                    'roi_months': 0,
                    'priority_score': 95,
                    'category': 'Compute',
                    'steps': [
                        f'🔴 Current: {instance_type} at {avg_cpu:.1f}% avg CPU (CRITICAL)',
                        '⬆️ Option 1: Upgrade to next size (e.g., m5.large → m5.xlarge)',
                        '📈 Option 2: Implement Auto Scaling Group for horizontal scaling',
                        '⚙️ Option 3: Optimize application code to reduce CPU usage',
                        '📊 Set up CloudWatch alarms for CPU > 80%',
                        '🚨 Immediate monitoring and capacity planning required'
                    ],
                    'risks': [
                        'CRITICAL: Current performance likely impacting users',
                        'Risk of instance throttling or crashes',
                        'May require immediate emergency action',
                        'Potential service disruptions during peak hours'
                    ],
                    'prerequisites': ['IMMEDIATE monitoring', 'Emergency capacity plan', 'Incident response ready']
                })
            
            # Optimal utilization - consider Graviton migration
            elif 50 <= avg_cpu < 70:
                recommendations.append({
                    'title': f'💚 Well-Utilized Instance - Consider Graviton: {instance_id}',
                    'description': f'Instance {instance_id} ({instance_type}) is well-utilized at {avg_cpu:.1f}% avg CPU. Consider migrating to Graviton for 20-40% cost savings while maintaining performance.',
                    'estimated_savings': '$40-120/month',
                    'timeline': 'Long-term',
                    'severity': 'Low',
                    'impact': 'Cost optimization opportunity without urgency',
                    'difficulty': 'Medium',
                    'roi_months': 3,
                    'priority_score': 45,
                    'category': 'Compute',
                    'steps': [
                        f'✅ Current: {instance_type} - {avg_cpu:.1f}% avg CPU (OPTIMAL)',
                        '💡 Opportunity: Migrate to Graviton for cost savings',
                        '🎯 Recommended: Same size Graviton equivalent',
                        '📋 Plan migration during next maintenance cycle',
                        '🧪 Thorough testing required',
                        '📊 Monitor performance post-migration'
                    ],
                    'risks': [
                        'ARM compatibility must be verified',
                        'Non-urgent - can be planned carefully',
                        'Requires application testing'
                    ],
                    'prerequisites': ['ARM compatibility assessment', 'Migration planning', 'Testing strategy']
                })
        
        return recommendations
