"""
Enhanced AI Recommender
Calls CloudXcelAI FinOps and CSPA agent endpoints via Load Balancer URLs
"""

import json
import os
import requests
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

FINOPS_AGENT_URL = os.getenv('FINOPS_AGENT_URL', 'http://cloudxcel-finops-agent-412099103-637641256.us-east-1.elb.amazonaws.com')
CSPA_AGENT_URL   = os.getenv('CSPA_AGENT_URL',   'http://cloudxcel-cspa-agent-1575281111-744372133.us-east-1.elb.amazonaws.com')


class EnhancedAIRecommender:
    def __init__(self, aws_session=None):
        self.finops_url = FINOPS_AGENT_URL
        self.cspa_url   = CSPA_AGENT_URL
        self.timeout    = 60  # seconds

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------
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
        """Call FinOps + CSPA agents, fall back to rule-based if unavailable."""

        summary = self._prepare_enhanced_summary(
            cost_data, ri_data, usage_data, savings_plans,
            s3_data, rds_data, lambda_data, idle_resources, rightsizing
        )

        ai_recommendations = []

        # --- FinOps Agent ---
        try:
            ai_recommendations += self._call_finops_agent(summary)
        except Exception as e:
            print(f"FinOps agent unavailable: {e}")

        # --- CSPA Agent ---
        try:
            ai_recommendations += self._call_cspa_agent(summary)
        except Exception as e:
            print(f"CSPA agent unavailable: {e}")

        # --- Rule-based fallback ---
        rule_based = self._generate_enhanced_rule_based(
            cost_data, ri_data, usage_data, savings_plans,
            s3_data, rds_data, lambda_data, idle_resources, rightsizing
        )

        all_recommendations = ai_recommendations + rule_based

        for rec in all_recommendations:
            if 'priority_score' not in rec:
                rec['priority_score'] = self._calculate_priority_score(rec)

        all_recommendations.sort(key=lambda x: x.get('priority_score', 0), reverse=True)
        return all_recommendations

    # ------------------------------------------------------------------
    # Agent callers
    # ------------------------------------------------------------------
    def _call_finops_agent(self, summary: Dict) -> List[Dict]:
        """POST analysis data to the FinOps agent LB and parse recommendations."""
        payload = {
            "query": "Analyze this AWS account data and return cost optimization recommendations.",
            "context": summary
        }
        resp = requests.post(
            f"{self.finops_url}/recommend",
            json=payload,
            timeout=self.timeout
        )
        resp.raise_for_status()
        data = resp.json()
        recs = data.get('recommendations', data.get('data', {}).get('recommendations', []))
        for r in recs:
            r.setdefault('source', 'FinOps Agent')
        return recs if isinstance(recs, list) else []

    def _call_cspa_agent(self, summary: Dict) -> List[Dict]:
        """POST analysis data to the CSPA agent LB and parse recommendations."""
        payload = {
            "query": "Provide cloud spend and performance analysis recommendations.",
            "context": summary
        }
        resp = requests.post(
            f"{self.cspa_url}/recommend",
            json=payload,
            timeout=self.timeout
        )
        resp.raise_for_status()
        data = resp.json()
        recs = data.get('recommendations', data.get('data', {}).get('recommendations', []))
        for r in recs:
            r.setdefault('source', 'CSPA Agent')
        return recs if isinstance(recs, list) else []

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _prepare_enhanced_summary(
        self, cost_data, ri_data, usage_data, savings_plans,
        s3_data, rds_data, lambda_data, idle_resources, rightsizing
    ) -> Dict:
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
        recommendations = []

        idle_waste = idle_resources.get('total_monthly_waste', 0)
        if idle_waste > 0:
            recommendations.append({
                'title': 'Remove Idle Resources - Immediate Savings',
                'description': f'Found {idle_resources.get("total_items", 0)} idle resources wasting ${idle_waste:.2f}/month.',
                'estimated_savings': f'${idle_waste:.2f}/month',
                'timeline': 'Immediate', 'severity': 'Critical',
                'impact': 'Zero business impact - resources not in use',
                'difficulty': 'Easy', 'roi_months': 0, 'priority_score': 95,
                'category': 'Network', 'source': 'Rule-based',
                'steps': ['Review idle resources', 'Snapshot EBS volumes', 'Delete/release idle resources'],
                'risks': ['Ensure EBS volumes are backed up'], 'prerequisites': ['Team confirmation']
            })

        rightsizing_savings = rightsizing.get('total_monthly_savings', 0)
        if rightsizing_savings > 100:
            recommendations.append({
                'title': 'Rightsize EC2 Instances',
                'description': f'{len(rightsizing.get("recommendations", []))} instances can be downsized to save ${rightsizing_savings:.2f}/month.',
                'estimated_savings': f'${rightsizing_savings:.2f}/month',
                'timeline': 'Short-term', 'severity': 'High',
                'impact': 'Minimal performance impact with proper testing',
                'difficulty': 'Medium', 'roi_months': 1, 'priority_score': 85,
                'category': 'Compute', 'source': 'Rule-based',
                'steps': ['Review Cost Explorer recommendations', 'Test in non-production', 'Apply changes'],
                'risks': ['Performance degradation if workload changes'], 'prerequisites': ['Performance baseline']
            })

        s3_opportunities = len(s3_data.get('optimization_opportunities', []))
        if s3_opportunities > 0:
            potential_savings = s3_data.get('estimated_monthly_cost', 0) * 0.3
            recommendations.append({
                'title': 'Implement S3 Lifecycle Policies',
                'description': f'{s3_opportunities} S3 buckets without lifecycle policies. Archival can reduce costs 30-70%.',
                'estimated_savings': f'${potential_savings:.2f}/month',
                'timeline': 'Short-term', 'severity': 'Medium',
                'impact': 'No impact on data availability',
                'difficulty': 'Easy', 'roi_months': 1, 'priority_score': 75,
                'category': 'Storage', 'source': 'Rule-based',
                'steps': ['Analyze access patterns', 'Create lifecycle policies', 'Enable Intelligent-Tiering'],
                'risks': ['Retrieval delays for archived data'], 'prerequisites': ['Data access pattern analysis']
            })

        rds_underutilized = rds_data.get('underutilized_count', 0)
        if rds_underutilized > 0:
            rds_savings = rds_data.get('total_monthly_cost', 0) * 0.4
            recommendations.append({
                'title': 'Rightsize Underutilized RDS Instances',
                'description': f'{rds_underutilized} RDS instances at <20% CPU. Downsizing saves ~40%.',
                'estimated_savings': f'${rds_savings:.2f}/month',
                'timeline': 'Medium-term', 'severity': 'High',
                'impact': 'Requires testing and maintenance window',
                'difficulty': 'Medium', 'roi_months': 2, 'priority_score': 80,
                'category': 'Database', 'source': 'Rule-based',
                'steps': ['Review Performance Insights', 'Test smaller instance type', 'Apply with maintenance window'],
                'risks': ['Downtime during modification'], 'prerequisites': ['Snapshot backup', 'Maintenance window']
            })

        sp_savings = savings_plans.get('estimated_savings', 0)
        if sp_savings > 1000:
            recommendations.append({
                'title': 'Purchase Compute Savings Plans',
                'description': f'Savings Plans offer up to 72% discount. Estimated ${sp_savings:.2f}/year savings.',
                'estimated_savings': f'${sp_savings / 12:.2f}/month',
                'timeline': 'Immediate', 'severity': 'High',
                'impact': 'Significant cost reduction with usage commitment',
                'difficulty': 'Easy', 'roi_months': 0, 'priority_score': 90,
                'category': 'Reserved Capacity', 'source': 'Rule-based',
                'steps': ['Review Cost Explorer SP recommendations', 'Choose 1-year term', 'Purchase via AWS Console'],
                'risks': ['Commitment to usage level for 1-3 years'], 'prerequisites': ['Usage pattern analysis']
            })

        return recommendations

    def _calculate_priority_score(self, rec: Dict) -> int:
        score = 50
        score += {'Critical': 30, 'High': 20, 'Medium': 10, 'Low': 5}.get(rec.get('severity', 'Medium'), 10)
        score += {'Easy': 20, 'Medium': 10, 'Hard': 5, 'Complex': 0}.get(rec.get('difficulty', 'Medium'), 10)
        score += {'Immediate': 20, 'Short-term': 15, 'Medium-term': 10, 'Long-term': 5}.get(rec.get('timeline', 'Medium-term'), 10)
        roi = rec.get('roi_months', 6)
        score += 20 if roi == 0 else (15 if roi <= 2 else (10 if roi <= 6 else 5))
        return min(score, 100)
