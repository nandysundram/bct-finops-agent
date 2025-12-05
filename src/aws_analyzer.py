"""
AWS Account Analyzer
Collects cost, RI, and usage data from AWS
"""

import boto3
from datetime import datetime, timedelta
from typing import Dict, List

class AWSAnalyzer:
    def __init__(self, access_key: str, secret_key: str, region: str):
        """Initialize AWS clients"""
        self.session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        
        self.ce_client = self.session.client('ce')  # Cost Explorer
        self.ec2_client = self.session.client('ec2')
        self.cloudwatch_client = self.session.client('cloudwatch')
    
    def analyze_costs(self) -> Dict:
        """Analyze cost data for the last 6 months"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=180)
        
        try:
            # Get cost and usage data - simplified without GroupBy
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='MONTHLY',
                Metrics=['UnblendedCost']
            )
            
            # Calculate total cost safely
            total_cost = 0.0
            for period in response.get('ResultsByTime', []):
                if 'Total' in period and 'UnblendedCost' in period['Total']:
                    amount = period['Total']['UnblendedCost'].get('Amount', '0')
                    total_cost += float(amount)
            
            # Get cost forecast
            try:
                forecast_response = self.ce_client.get_cost_forecast(
                    TimePeriod={
                        'Start': end_date.strftime('%Y-%m-%d'),
                        'End': (end_date + timedelta(days=90)).strftime('%Y-%m-%d')
                    },
                    Metric='UNBLENDED_COST',
                    Granularity='MONTHLY'
                )
            except Exception as e:
                print(f"Warning: Could not get cost forecast: {e}")
                forecast_response = {'Total': {'Amount': '0', 'Unit': 'USD'}}
            
            return {
                'historical': response.get('ResultsByTime', []),
                'forecast': forecast_response,
                'total_cost': total_cost
            }
            
        except Exception as e:
            print(f"Error analyzing costs: {e}")
            raise
    
    def analyze_reserved_instances(self) -> Dict:
        """Analyze Reserved Instance utilization and recommendations"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        try:
            # Get RI utilization
            utilization_response = self.ce_client.get_reservation_utilization(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='MONTHLY'
            )
        except Exception as e:
            print(f"Warning: Could not get RI utilization: {e}")
            utilization_response = {'UtilizationsByTime': []}
        
        try:
            # Get RI purchase recommendations
            recommendations_response = self.ce_client.get_reservation_purchase_recommendation(
                Service='Amazon Elastic Compute Cloud - Compute',
                LookbackPeriodInDays='SIXTY_DAYS',
                TermInYears='ONE_YEAR',
                PaymentOption='NO_UPFRONT'
            )
        except Exception as e:
            print(f"Warning: Could not get RI recommendations: {e}")
            recommendations_response = {'Recommendations': []}
        
        try:
            # Get current RIs
            ec2_ris = self.ec2_client.describe_reserved_instances(
                Filters=[{'Name': 'state', 'Values': ['active']}]
            )
        except Exception as e:
            print(f"Warning: Could not get current RIs: {e}")
            ec2_ris = {'ReservedInstances': []}
        
        return {
            'utilization': utilization_response,
            'recommendations': recommendations_response,
            'current_ris': ec2_ris.get('ReservedInstances', [])
        }
    
    def analyze_usage_patterns(self) -> Dict:
        """Analyze EC2 usage patterns"""
        try:
            # Get all running instances
            instances = self.ec2_client.describe_instances(
                Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
            )
            
            usage_data = []
            
            for reservation in instances.get('Reservations', []):
                for instance in reservation.get('Instances', []):
                    instance_id = instance.get('InstanceId')
                    instance_type = instance.get('InstanceType')
                    
                    if not instance_id:
                        continue
                    
                    try:
                        # Get CPU utilization
                        cpu_stats = self.cloudwatch_client.get_metric_statistics(
                            Namespace='AWS/EC2',
                            MetricName='CPUUtilization',
                            Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                            StartTime=datetime.now() - timedelta(days=14),
                            EndTime=datetime.now(),
                            Period=86400,  # Daily
                            Statistics=['Average', 'Maximum']
                        )
                        
                        usage_data.append({
                            'instance_id': instance_id,
                            'instance_type': instance_type,
                            'cpu_stats': cpu_stats.get('Datapoints', [])
                        })
                    except Exception as e:
                        print(f"Warning: Could not get metrics for {instance_id}: {e}")
                        usage_data.append({
                            'instance_id': instance_id,
                            'instance_type': instance_type,
                            'cpu_stats': []
                        })
            
            return {
                'instances': usage_data,
                'total_instances': len(usage_data)
            }
            
        except Exception as e:
            print(f"Warning: Could not analyze usage patterns: {e}")
            return {
                'instances': [],
                'total_instances': 0
            }
