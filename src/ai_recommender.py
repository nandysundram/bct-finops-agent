"""
AI-Powered Recommendation Engine
Generates intelligent cost optimization recommendations
"""

import os
import json
from typing import Dict, List
import boto3

class AIRecommender:
    def __init__(self, aws_session=None):
        """Initialize Bedrock client"""
        if aws_session:
            self.bedrock_client = aws_session.client('bedrock-runtime', region_name='us-east-1')
        else:
            self.bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Use Claude 3 Sonnet by default (good balance of cost and quality)
        self.model_id = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
    
    def generate_recommendations(
        self,
        cost_data: Dict,
        ri_data: Dict,
        usage_data: Dict
    ) -> List[Dict]:
        """Generate AI-powered recommendations"""
        
        # Prepare data summary for AI
        data_summary = self._prepare_data_summary(cost_data, ri_data, usage_data)
        
        # Create prompt for AI
        prompt = f"""
        Analyze the following AWS account data and provide detailed cost optimization recommendations.
        
        Data Summary:
        {json.dumps(data_summary, indent=2)}
        
        For each recommendation, provide:
        1. Title: Brief description
        2. Description: Detailed explanation
        3. Estimated Savings: Dollar amount or percentage
        4. Timeline: Implementation timeframe (Immediate, 1-2 weeks, 1-3 months)
        5. Severity: Critical, High, Medium, Low
        6. Impact: Business and technical impact
        7. Implementation Steps: Specific actions to take
        
        Focus on:
        - Reserved Instance opportunities
        - Underutilized resources
        - Cost trends and anomalies
        - Right-sizing opportunities
        - Savings Plans
        
        Return response as a JSON array of recommendations.
        """
        
        # Prepare request for Claude
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "temperature": 0.7,
            "messages": [
                {
                    "role": "user",
                    "content": f"You are an AWS cost optimization expert. Provide actionable, specific recommendations.\n\n{prompt}"
                }
            ]
        }
        
        try:
            # Call Bedrock
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            ai_content = response_body['content'][0]['text']
            
            # Extract JSON from response (Claude might wrap it in markdown)
            if '```json' in ai_content:
                ai_content = ai_content.split('```json')[1].split('```')[0].strip()
            elif '```' in ai_content:
                ai_content = ai_content.split('```')[1].split('```')[0].strip()
            
            ai_response = json.loads(ai_content)
            recommendations = ai_response.get('recommendations', [])
            
        except Exception as e:
            print(f"Warning: AI recommendation generation failed: {e}")
            print("Falling back to rule-based recommendations only")
            recommendations = []
        
        # Add rule-based recommendations
        rule_based = self._generate_rule_based_recommendations(cost_data, ri_data, usage_data)
        
        return recommendations + rule_based
    
    def _prepare_data_summary(self, cost_data: Dict, ri_data: Dict, usage_data: Dict) -> Dict:
        """Prepare concise data summary for AI analysis"""
        return {
            'total_cost_6months': round(cost_data['total_cost'], 2),
            'monthly_average': round(cost_data['total_cost'] / 6, 2),
            'ri_utilization': self._extract_ri_utilization(ri_data),
            'ri_recommendations_count': len(ri_data['recommendations'].get('Recommendations', [])),
            'total_instances': usage_data['total_instances'],
            'underutilized_instances': self._count_underutilized(usage_data)
        }
    
    def _extract_ri_utilization(self, ri_data: Dict) -> float:
        """Extract average RI utilization percentage"""
        utilization = ri_data['utilization'].get('UtilizationsByTime', [])
        if not utilization:
            return 0.0
        
        total_util = sum(
            float(period['Total'].get('UtilizationPercentage', 0))
            for period in utilization
        )
        return round(total_util / len(utilization), 2)
    
    def _count_underutilized(self, usage_data: Dict) -> int:
        """Count instances with low CPU utilization"""
        count = 0
        for instance in usage_data.get('instances', []):
            cpu_stats = instance.get('cpu_stats', [])
            if cpu_stats:
                try:
                    avg_cpu = sum(dp.get('Average', 0) for dp in cpu_stats) / len(cpu_stats)
                    if avg_cpu < 20:  # Less than 20% average CPU
                        count += 1
                except (ZeroDivisionError, TypeError):
                    continue
        return count
    
    def _generate_rule_based_recommendations(
        self,
        cost_data: Dict,
        ri_data: Dict,
        usage_data: Dict
    ) -> List[Dict]:
        """Generate rule-based recommendations"""
        recommendations = []
        
        # Check RI utilization
        ri_util = self._extract_ri_utilization(ri_data)
        if ri_util < 70:
            recommendations.append({
                'title': 'Low Reserved Instance Utilization',
                'description': f'Current RI utilization is {ri_util}%. Consider modifying or exchanging RIs.',
                'estimated_savings': 'Up to 20% of RI costs',
                'timeline': '1-2 weeks',
                'severity': 'High',
                'impact': 'Optimize existing RI investments without additional purchases',
                'steps': [
                    'Review RI modification options',
                    'Consider RI marketplace for unused capacity',
                    'Evaluate Convertible RI exchanges'
                ]
            })
        
        # Check for underutilized instances
        underutilized = self._count_underutilized(usage_data)
        if underutilized > 0:
            recommendations.append({
                'title': f'Underutilized EC2 Instances Detected',
                'description': f'{underutilized} instances with <20% average CPU utilization',
                'estimated_savings': f'${underutilized * 50}-${underutilized * 200}/month',
                'timeline': 'Immediate',
                'severity': 'Medium',
                'impact': 'Reduce waste without affecting performance',
                'steps': [
                    'Review instance metrics and requirements',
                    'Right-size to smaller instance types',
                    'Consider stopping non-production instances during off-hours'
                ]
            })
        
        return recommendations
