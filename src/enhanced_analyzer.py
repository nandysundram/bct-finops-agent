"""
Enhanced AWS Account Analyzer
Comprehensive analysis including S3, RDS, Lambda, Savings Plans, and idle resources
"""

import boto3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json

class EnhancedAWSAnalyzer:
    def __init__(self, access_key: str, secret_key: str, region: str, role_arn: Optional[str] = None):
        """Initialize AWS clients with optional role assumption"""
        
        if role_arn:
            # Use STS to assume role
            sts_client = boto3.client(
                'sts',
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )
            
            assumed_role = sts_client.assume_role(
                RoleArn=role_arn,
                RoleSessionName='CostOptimizerSession'
            )
            
            credentials = assumed_role['Credentials']
            self.session = boto3.Session(
                aws_access_key_id=credentials['AccessKeyId'],
                aws_secret_access_key=credentials['SecretAccessKey'],
                aws_session_token=credentials['SessionToken'],
                region_name=region
            )
        else:
            self.session = boto3.Session(
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )
        
        self.region = region
        self._init_clients()
    
    def _init_clients(self):
        """Initialize all AWS service clients"""
        self.ce_client = self.session.client('ce', region_name='us-east-1')
        self.ec2_client = self.session.client('ec2')
        self.s3_client = self.session.client('s3')
        self.rds_client = self.session.client('rds')
        self.lambda_client = self.session.client('lambda')
        self.elb_client = self.session.client('elbv2')
        self.cloudwatch_client = self.session.client('cloudwatch')
        self.organizations_client = self.session.client('organizations')
        self.sts_client = self.session.client('sts')
        self.eks_client = self.session.client('eks')
        self.ecs_client = self.session.client('ecs')
        self.dynamodb_client = self.session.client('dynamodb')
        self.elasticache_client = self.session.client('elasticache')
        self.redshift_client = self.session.client('redshift')
        self.autoscaling_client = self.session.client('autoscaling')
    
    def get_account_info(self) -> Dict:
        """Get AWS account information"""
        try:
            identity = self.sts_client.get_caller_identity()
            return {
                'account_id': identity['Account'],
                'arn': identity['Arn'],
                'user_id': identity['UserId']
            }
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_costs(self) -> Dict:
        """Analyze cost data for the last 6 months"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=180)
        
        try:
            # Get cost and usage data
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
    
    def analyze_savings_plans(self) -> Dict:
        """Analyze Savings Plans utilization and recommendations"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        try:
            # Get Savings Plans utilization
            utilization = self.ce_client.get_savings_plans_utilization(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='MONTHLY'
            )
            
            # Get Savings Plans purchase recommendations
            recommendations = self.ce_client.get_savings_plans_purchase_recommendation(
                SavingsPlansType='COMPUTE_SP',
                TermInYears='ONE_YEAR',
                PaymentOption='NO_UPFRONT',
                LookbackPeriodInDays='SIXTY_DAYS'
            )
            
            return {
                'utilization': utilization,
                'recommendations': recommendations.get('SavingsPlansPurchaseRecommendation', {}),
                'estimated_savings': self._calculate_sp_savings(recommendations)
            }
        except Exception as e:
            print(f"Warning: Could not analyze Savings Plans: {e}")
            return {'utilization': {}, 'recommendations': {}, 'estimated_savings': 0}
    
    def _calculate_sp_savings(self, recommendations: Dict) -> float:
        """Calculate potential savings from Savings Plans"""
        try:
            details = recommendations.get('SavingsPlansPurchaseRecommendation', {})
            recommendation_details = details.get('SavingsPlansPurchaseRecommendationDetails', [])
            
            total_savings = 0
            for rec in recommendation_details:
                savings = rec.get('EstimatedMonthlySavingsAmount', '0')
                total_savings += float(savings)
            
            return total_savings * 12  # Annual savings
        except:
            return 0
    
    def analyze_s3_storage(self) -> Dict:
        """Analyze S3 storage optimization opportunities"""
        try:
            buckets = self.s3_client.list_buckets()
            
            storage_analysis = []
            total_size = 0
            optimization_opportunities = []
            
            for bucket in buckets.get('Buckets', [])[:20]:  # Limit to 20 buckets
                bucket_name = bucket['Name']
                
                try:
                    # Get bucket size from CloudWatch
                    metrics = self.cloudwatch_client.get_metric_statistics(
                        Namespace='AWS/S3',
                        MetricName='BucketSizeBytes',
                        Dimensions=[
                            {'Name': 'BucketName', 'Value': bucket_name},
                            {'Name': 'StorageType', 'Value': 'StandardStorage'}
                        ],
                        StartTime=datetime.now() - timedelta(days=2),
                        EndTime=datetime.now(),
                        Period=86400,
                        Statistics=['Average']
                    )
                    
                    if metrics['Datapoints']:
                        size_bytes = metrics['Datapoints'][0]['Average']
                        size_gb = size_bytes / (1024**3)
                        total_size += size_gb
                        
                        # Check lifecycle policy
                        try:
                            self.s3_client.get_bucket_lifecycle_configuration(Bucket=bucket_name)
                            has_lifecycle = True
                        except:
                            has_lifecycle = False
                        
                        # Check versioning
                        versioning = self.s3_client.get_bucket_versioning(Bucket=bucket_name)
                        is_versioned = versioning.get('Status') == 'Enabled'
                        
                        storage_analysis.append({
                            'bucket': bucket_name,
                            'size_gb': round(size_gb, 2),
                            'has_lifecycle': has_lifecycle,
                            'is_versioned': is_versioned
                        })
                        
                        # Identify optimization opportunities
                        if size_gb > 100 and not has_lifecycle:
                            optimization_opportunities.append({
                                'bucket': bucket_name,
                                'issue': 'No lifecycle policy',
                                'potential_savings': f"${size_gb * 0.015:.2f}/month",
                                'recommendation': 'Implement lifecycle policy to move old data to Glacier'
                            })
                        
                        if is_versioned and size_gb > 50:
                            optimization_opportunities.append({
                                'bucket': bucket_name,
                                'issue': 'Versioning enabled without lifecycle',
                                'potential_savings': f"${size_gb * 0.01:.2f}/month",
                                'recommendation': 'Add lifecycle policy to expire old versions'
                            })
                
                except Exception as e:
                    continue
            
            return {
                'total_buckets': len(buckets.get('Buckets', [])),
                'analyzed_buckets': len(storage_analysis),
                'total_size_gb': round(total_size, 2),
                'storage_details': storage_analysis,
                'optimization_opportunities': optimization_opportunities,
                'estimated_monthly_cost': round(total_size * 0.023, 2)  # Standard storage cost
            }
        
        except Exception as e:
            print(f"Warning: Could not analyze S3 storage: {e}")
            return {'total_buckets': 0, 'optimization_opportunities': []}
    
    def analyze_rds_instances(self) -> Dict:
        """Analyze RDS instances for optimization"""
        try:
            instances = self.rds_client.describe_db_instances()
            
            rds_analysis = []
            total_monthly_cost = 0
            
            for instance in instances.get('DBInstances', []):
                instance_id = instance['DBInstanceIdentifier']
                instance_class = instance['DBInstanceClass']
                engine = instance['Engine']
                storage_gb = instance['AllocatedStorage']
                multi_az = instance['MultiAZ']
                
                # Get CPU utilization
                try:
                    cpu_stats = self.cloudwatch_client.get_metric_statistics(
                        Namespace='AWS/RDS',
                        MetricName='CPUUtilization',
                        Dimensions=[{'Name': 'DBInstanceIdentifier', 'Value': instance_id}],
                        StartTime=datetime.now() - timedelta(days=14),
                        EndTime=datetime.now(),
                        Period=86400,
                        Statistics=['Average', 'Maximum']
                    )
                    
                    avg_cpu = 0
                    if cpu_stats['Datapoints']:
                        avg_cpu = sum(dp['Average'] for dp in cpu_stats['Datapoints']) / len(cpu_stats['Datapoints'])
                    
                    # Estimate cost (rough approximation)
                    estimated_cost = self._estimate_rds_cost(instance_class, storage_gb, multi_az)
                    total_monthly_cost += estimated_cost
                    
                    rds_analysis.append({
                        'instance_id': instance_id,
                        'instance_class': instance_class,
                        'engine': engine,
                        'storage_gb': storage_gb,
                        'multi_az': multi_az,
                        'avg_cpu': round(avg_cpu, 2),
                        'estimated_monthly_cost': estimated_cost,
                        'underutilized': avg_cpu < 20
                    })
                
                except Exception as e:
                    continue
            
            return {
                'total_instances': len(instances.get('DBInstances', [])),
                'instances': rds_analysis,
                'total_monthly_cost': round(total_monthly_cost, 2),
                'underutilized_count': sum(1 for i in rds_analysis if i['underutilized'])
            }
        
        except Exception as e:
            print(f"Warning: Could not analyze RDS: {e}")
            return {'total_instances': 0, 'instances': []}
    
    def _estimate_rds_cost(self, instance_class: str, storage_gb: int, multi_az: bool) -> float:
        """Estimate RDS monthly cost"""
        # Rough cost estimates (actual costs vary by region)
        instance_costs = {
            'db.t3.micro': 15,
            'db.t3.small': 30,
            'db.t3.medium': 60,
            'db.t3.large': 120,
            'db.m5.large': 140,
            'db.m5.xlarge': 280,
            'db.r5.large': 180,
            'db.r5.xlarge': 360
        }
        
        base_cost = instance_costs.get(instance_class, 100)
        if multi_az:
            base_cost *= 2
        
        storage_cost = storage_gb * 0.115  # GP2 storage
        
        return base_cost + storage_cost
    
    def analyze_lambda_functions(self) -> Dict:
        """Analyze Lambda functions for optimization"""
        try:
            functions = self.lambda_client.list_functions()
            
            lambda_analysis = []
            total_invocations = 0
            
            for func in functions.get('Functions', [])[:50]:  # Limit to 50 functions
                func_name = func['FunctionName']
                memory_mb = func['MemorySize']
                timeout = func['Timeout']
                
                try:
                    # Get invocation metrics
                    invocations = self.cloudwatch_client.get_metric_statistics(
                        Namespace='AWS/Lambda',
                        MetricName='Invocations',
                        Dimensions=[{'Name': 'FunctionName', 'Value': func_name}],
                        StartTime=datetime.now() - timedelta(days=30),
                        EndTime=datetime.now(),
                        Period=2592000,  # 30 days
                        Statistics=['Sum']
                    )
                    
                    # Get duration metrics
                    duration = self.cloudwatch_client.get_metric_statistics(
                        Namespace='AWS/Lambda',
                        MetricName='Duration',
                        Dimensions=[{'Name': 'FunctionName', 'Value': func_name}],
                        StartTime=datetime.now() - timedelta(days=7),
                        EndTime=datetime.now(),
                        Period=604800,  # 7 days
                        Statistics=['Average']
                    )
                    
                    invocation_count = 0
                    if invocations['Datapoints']:
                        invocation_count = int(invocations['Datapoints'][0]['Sum'])
                    
                    avg_duration = 0
                    if duration['Datapoints']:
                        avg_duration = duration['Datapoints'][0]['Average']
                    
                    total_invocations += invocation_count
                    
                    lambda_analysis.append({
                        'function_name': func_name,
                        'memory_mb': memory_mb,
                        'timeout': timeout,
                        'invocations_30d': invocation_count,
                        'avg_duration_ms': round(avg_duration, 2),
                        'rarely_used': invocation_count < 10
                    })
                
                except Exception as e:
                    continue
            
            return {
                'total_functions': len(functions.get('Functions', [])),
                'analyzed_functions': len(lambda_analysis),
                'total_invocations_30d': total_invocations,
                'functions': lambda_analysis,
                'rarely_used_count': sum(1 for f in lambda_analysis if f['rarely_used'])
            }
        
        except Exception as e:
            print(f"Warning: Could not analyze Lambda: {e}")
            return {'total_functions': 0, 'functions': []}
    
    def detect_idle_resources(self) -> Dict:
        """Detect idle and unused resources"""
        idle_resources = {
            'ebs_volumes': [],
            'elastic_ips': [],
            'load_balancers': [],
            'nat_gateways': []
        }
        
        try:
            # Unattached EBS volumes
            volumes = self.ec2_client.describe_volumes(
                Filters=[{'Name': 'status', 'Values': ['available']}]
            )
            
            for vol in volumes.get('Volumes', []):
                size_gb = vol['Size']
                vol_type = vol['VolumeType']
                cost_per_gb = {'gp2': 0.10, 'gp3': 0.08, 'io1': 0.125, 'io2': 0.125, 'st1': 0.045, 'sc1': 0.015}
                monthly_cost = size_gb * cost_per_gb.get(vol_type, 0.10)
                
                idle_resources['ebs_volumes'].append({
                    'volume_id': vol['VolumeId'],
                    'size_gb': size_gb,
                    'type': vol_type,
                    'monthly_cost': round(monthly_cost, 2),
                    'created': vol['CreateTime'].strftime('%Y-%m-%d')
                })
            
            # Unassociated Elastic IPs
            addresses = self.ec2_client.describe_addresses()
            
            for addr in addresses.get('Addresses', []):
                if 'InstanceId' not in addr:
                    idle_resources['elastic_ips'].append({
                        'allocation_id': addr.get('AllocationId', 'N/A'),
                        'public_ip': addr.get('PublicIp', 'N/A'),
                        'monthly_cost': 3.60  # $0.005/hour
                    })
            
            # Idle Load Balancers (no targets)
            load_balancers = self.elb_client.describe_load_balancers()
            
            for lb in load_balancers.get('LoadBalancers', []):
                lb_arn = lb['LoadBalancerArn']
                lb_name = lb['LoadBalancerName']
                
                try:
                    target_groups = self.elb_client.describe_target_groups(LoadBalancerArn=lb_arn)
                    
                    has_healthy_targets = False
                    for tg in target_groups.get('TargetGroups', []):
                        health = self.elb_client.describe_target_health(TargetGroupArn=tg['TargetGroupArn'])
                        if any(t['TargetHealth']['State'] == 'healthy' for t in health.get('TargetHealthDescriptions', [])):
                            has_healthy_targets = True
                            break
                    
                    if not has_healthy_targets:
                        idle_resources['load_balancers'].append({
                            'name': lb_name,
                            'type': lb['Type'],
                            'monthly_cost': 16.20 if lb['Type'] == 'application' else 18.00
                        })
                
                except Exception as e:
                    continue
        
        except Exception as e:
            print(f"Warning: Could not detect all idle resources: {e}")
        
        # Calculate total waste
        total_waste = (
            sum(v['monthly_cost'] for v in idle_resources['ebs_volumes']) +
            sum(ip['monthly_cost'] for ip in idle_resources['elastic_ips']) +
            sum(lb['monthly_cost'] for lb in idle_resources['load_balancers'])
        )
        
        idle_resources['total_monthly_waste'] = round(total_waste, 2)
        idle_resources['total_items'] = (
            len(idle_resources['ebs_volumes']) +
            len(idle_resources['elastic_ips']) +
            len(idle_resources['load_balancers'])
        )
        
        return idle_resources
    
    def analyze_cost_by_tags(self) -> Dict:
        """Analyze costs by resource tags"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        try:
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='MONTHLY',
                Metrics=['UnblendedCost'],
                GroupBy=[
                    {'Type': 'TAG', 'Key': 'Environment'},
                    {'Type': 'TAG', 'Key': 'Project'},
                    {'Type': 'TAG', 'Key': 'Team'}
                ]
            )
            
            tag_costs = {}
            for period in response.get('ResultsByTime', []):
                for group in period.get('Groups', []):
                    keys = group.get('Keys', [])
                    amount = float(group['Metrics']['UnblendedCost']['Amount'])
                    
                    for key in keys:
                        if key and key != 'No tag':
                            tag_costs[key] = tag_costs.get(key, 0) + amount
            
            return {
                'tag_breakdown': sorted(
                    [{'tag': k, 'cost': round(v, 2)} for k, v in tag_costs.items()],
                    key=lambda x: x['cost'],
                    reverse=True
                )[:20],
                'untagged_resources': self._count_untagged_resources()
            }
        
        except Exception as e:
            print(f"Warning: Could not analyze costs by tags: {e}")
            return {'tag_breakdown': [], 'untagged_resources': 0}
    
    def _count_untagged_resources(self) -> int:
        """Count resources without tags"""
        untagged_count = 0
        
        try:
            # Check EC2 instances
            instances = self.ec2_client.describe_instances()
            for reservation in instances.get('Reservations', []):
                for instance in reservation.get('Instances', []):
                    if not instance.get('Tags'):
                        untagged_count += 1
        except:
            pass
        
        return untagged_count
    
    def get_rightsizing_recommendations(self) -> Dict:
        """Get AWS Cost Explorer rightsizing recommendations"""
        try:
            response = self.ce_client.get_rightsizing_recommendation(
                Service='AmazonEC2',
                Configuration={
                    'RecommendationTarget': 'SAME_INSTANCE_FAMILY',
                    'BenefitsConsidered': True
                }
            )
            
            recommendations = []
            total_savings = 0
            
            for rec in response.get('RightsizingRecommendations', []):
                current = rec.get('CurrentInstance', {})
                target = rec.get('ModifyRecommendationDetail', {})
                
                if target:
                    monthly_savings = float(target.get('TargetInstances', [{}])[0].get('EstimatedMonthlySavings', '0'))
                    total_savings += monthly_savings
                    
                    recommendations.append({
                        'instance_id': current.get('ResourceId', 'N/A'),
                        'current_type': current.get('InstanceType', 'N/A'),
                        'recommended_type': target.get('TargetInstances', [{}])[0].get('InstanceType', 'N/A'),
                        'monthly_savings': round(monthly_savings, 2)
                    })
            
            return {
                'recommendations': recommendations,
                'total_monthly_savings': round(total_savings, 2),
                'total_annual_savings': round(total_savings * 12, 2)
            }
        
        except Exception as e:
            print(f"Warning: Could not get rightsizing recommendations: {e}")
            return {'recommendations': [], 'total_monthly_savings': 0}

    
    def analyze_eks_clusters(self) -> Dict:
        """Analyze EKS clusters for optimization"""
        try:
            clusters = self.eks_client.list_clusters()
            
            eks_analysis = []
            total_monthly_cost = 0
            
            for cluster_name in clusters.get('clusters', []):
                try:
                    cluster = self.eks_client.describe_cluster(name=cluster_name)
                    cluster_info = cluster['cluster']
                    
                    # Get node groups
                    nodegroups = self.eks_client.list_nodegroups(clusterName=cluster_name)
                    
                    node_group_details = []
                    total_nodes = 0
                    
                    for ng_name in nodegroups.get('nodegroups', []):
                        ng = self.eks_client.describe_nodegroup(
                            clusterName=cluster_name,
                            nodegroupName=ng_name
                        )
                        ng_info = ng['nodegroup']
                        
                        desired_size = ng_info.get('scalingConfig', {}).get('desiredSize', 0)
                        instance_types = ng_info.get('instanceTypes', [])
                        
                        total_nodes += desired_size
                        
                        node_group_details.append({
                            'name': ng_name,
                            'instance_types': instance_types,
                            'desired_size': desired_size,
                            'min_size': ng_info.get('scalingConfig', {}).get('minSize', 0),
                            'max_size': ng_info.get('scalingConfig', {}).get('maxSize', 0)
                        })
                    
                    # Estimate cost (EKS control plane + nodes)
                    control_plane_cost = 73  # $0.10/hour * 730 hours
                    node_cost = total_nodes * 50  # Rough estimate per node
                    cluster_cost = control_plane_cost + node_cost
                    total_monthly_cost += cluster_cost
                    
                    eks_analysis.append({
                        'cluster_name': cluster_name,
                        'version': cluster_info.get('version', 'N/A'),
                        'status': cluster_info.get('status', 'N/A'),
                        'node_groups': len(nodegroups.get('nodegroups', [])),
                        'total_nodes': total_nodes,
                        'node_group_details': node_group_details,
                        'estimated_monthly_cost': cluster_cost
                    })
                
                except Exception as e:
                    print(f"Warning: Could not analyze EKS cluster {cluster_name}: {e}")
                    continue
            
            return {
                'total_clusters': len(clusters.get('clusters', [])),
                'clusters': eks_analysis,
                'total_monthly_cost': round(total_monthly_cost, 2)
            }
        
        except Exception as e:
            print(f"Warning: Could not analyze EKS: {e}")
            return {'total_clusters': 0, 'clusters': [], 'total_monthly_cost': 0}
    
    def analyze_ecs_services(self) -> Dict:
        """Analyze ECS services and tasks"""
        try:
            clusters = self.ecs_client.list_clusters()
            
            ecs_analysis = []
            total_tasks = 0
            
            for cluster_arn in clusters.get('clusterArns', [])[:10]:  # Limit to 10 clusters
                cluster_name = cluster_arn.split('/')[-1]
                
                try:
                    # Get services
                    services = self.ecs_client.list_services(cluster=cluster_arn)
                    
                    # Get tasks
                    tasks = self.ecs_client.list_tasks(cluster=cluster_arn)
                    task_count = len(tasks.get('taskArns', []))
                    total_tasks += task_count
                    
                    ecs_analysis.append({
                        'cluster_name': cluster_name,
                        'services': len(services.get('serviceArns', [])),
                        'running_tasks': task_count
                    })
                
                except Exception as e:
                    continue
            
            return {
                'total_clusters': len(clusters.get('clusterArns', [])),
                'clusters': ecs_analysis,
                'total_tasks': total_tasks
            }
        
        except Exception as e:
            print(f"Warning: Could not analyze ECS: {e}")
            return {'total_clusters': 0, 'clusters': [], 'total_tasks': 0}
    
    def analyze_dynamodb_tables(self) -> Dict:
        """Analyze DynamoDB tables for optimization"""
        try:
            tables = self.dynamodb_client.list_tables()
            
            dynamodb_analysis = []
            total_monthly_cost = 0
            
            for table_name in tables.get('TableNames', [])[:20]:  # Limit to 20 tables
                try:
                    table = self.dynamodb_client.describe_table(TableName=table_name)
                    table_info = table['Table']
                    
                    billing_mode = table_info.get('BillingModeSummary', {}).get('BillingMode', 'PROVISIONED')
                    table_size_bytes = table_info.get('TableSizeBytes', 0)
                    table_size_gb = table_size_bytes / (1024**3)
                    item_count = table_info.get('ItemCount', 0)
                    
                    # Estimate cost
                    if billing_mode == 'PAY_PER_REQUEST':
                        # On-demand pricing
                        estimated_cost = table_size_gb * 0.25  # Storage cost
                    else:
                        # Provisioned capacity
                        read_capacity = table_info.get('ProvisionedThroughput', {}).get('ReadCapacityUnits', 0)
                        write_capacity = table_info.get('ProvisionedThroughput', {}).get('WriteCapacityUnits', 0)
                        estimated_cost = (read_capacity * 0.00013 + write_capacity * 0.00065) * 730 + table_size_gb * 0.25
                    
                    total_monthly_cost += estimated_cost
                    
                    dynamodb_analysis.append({
                        'table_name': table_name,
                        'billing_mode': billing_mode,
                        'size_gb': round(table_size_gb, 2),
                        'item_count': item_count,
                        'estimated_monthly_cost': round(estimated_cost, 2)
                    })
                
                except Exception as e:
                    continue
            
            return {
                'total_tables': len(tables.get('TableNames', [])),
                'tables': dynamodb_analysis,
                'total_monthly_cost': round(total_monthly_cost, 2)
            }
        
        except Exception as e:
            print(f"Warning: Could not analyze DynamoDB: {e}")
            return {'total_tables': 0, 'tables': [], 'total_monthly_cost': 0}
    
    def analyze_elasticache_clusters(self) -> Dict:
        """Analyze ElastiCache clusters"""
        try:
            clusters = self.elasticache_client.describe_cache_clusters()
            
            elasticache_analysis = []
            total_monthly_cost = 0
            
            for cluster in clusters.get('CacheClusters', []):
                cluster_id = cluster.get('CacheClusterId', 'N/A')
                engine = cluster.get('Engine', 'N/A')
                node_type = cluster.get('CacheNodeType', 'N/A')
                num_nodes = cluster.get('NumCacheNodes', 0)
                status = cluster.get('CacheClusterStatus', 'N/A')
                
                # Rough cost estimate (varies by node type)
                node_costs = {
                    'cache.t3.micro': 12,
                    'cache.t3.small': 24,
                    'cache.t3.medium': 48,
                    'cache.m5.large': 120,
                    'cache.r5.large': 150
                }
                
                node_cost = node_costs.get(node_type, 50)
                cluster_cost = node_cost * num_nodes
                total_monthly_cost += cluster_cost
                
                elasticache_analysis.append({
                    'cluster_id': cluster_id,
                    'engine': engine,
                    'node_type': node_type,
                    'num_nodes': num_nodes,
                    'status': status,
                    'estimated_monthly_cost': cluster_cost
                })
            
            return {
                'total_clusters': len(clusters.get('CacheClusters', [])),
                'clusters': elasticache_analysis,
                'total_monthly_cost': round(total_monthly_cost, 2)
            }
        
        except Exception as e:
            print(f"Warning: Could not analyze ElastiCache: {e}")
            return {'total_clusters': 0, 'clusters': [], 'total_monthly_cost': 0}
    
    def analyze_redshift_clusters(self) -> Dict:
        """Analyze Redshift clusters"""
        try:
            clusters = self.redshift_client.describe_clusters()
            
            redshift_analysis = []
            total_monthly_cost = 0
            
            for cluster in clusters.get('Clusters', []):
                cluster_id = cluster.get('ClusterIdentifier', 'N/A')
                node_type = cluster.get('NodeType', 'N/A')
                num_nodes = cluster.get('NumberOfNodes', 0)
                status = cluster.get('ClusterStatus', 'N/A')
                
                # Rough cost estimate
                node_costs = {
                    'dc2.large': 180,
                    'dc2.8xlarge': 4800,
                    'ra3.xlplus': 1086,
                    'ra3.4xlarge': 3261,
                    'ra3.16xlarge': 13044
                }
                
                node_cost = node_costs.get(node_type, 500)
                cluster_cost = node_cost * num_nodes
                total_monthly_cost += cluster_cost
                
                redshift_analysis.append({
                    'cluster_id': cluster_id,
                    'node_type': node_type,
                    'num_nodes': num_nodes,
                    'status': status,
                    'estimated_monthly_cost': cluster_cost
                })
            
            return {
                'total_clusters': len(clusters.get('Clusters', [])),
                'clusters': redshift_analysis,
                'total_monthly_cost': round(total_monthly_cost, 2)
            }
        
        except Exception as e:
            print(f"Warning: Could not analyze Redshift: {e}")
            return {'total_clusters': 0, 'clusters': [], 'total_monthly_cost': 0}
    
    def analyze_autoscaling_groups(self) -> Dict:
        """Analyze Auto Scaling Groups"""
        try:
            asgs = self.autoscaling_client.describe_auto_scaling_groups()
            
            asg_analysis = []
            
            for asg in asgs.get('AutoScalingGroups', []):
                asg_name = asg.get('AutoScalingGroupName', 'N/A')
                desired = asg.get('DesiredCapacity', 0)
                min_size = asg.get('MinSize', 0)
                max_size = asg.get('MaxSize', 0)
                instances = len(asg.get('Instances', []))
                
                # Check if underutilized (desired == min)
                underutilized = desired == min_size and min_size > 0
                
                asg_analysis.append({
                    'name': asg_name,
                    'desired': desired,
                    'min': min_size,
                    'max': max_size,
                    'current_instances': instances,
                    'underutilized': underutilized
                })
            
            return {
                'total_asgs': len(asgs.get('AutoScalingGroups', [])),
                'asgs': asg_analysis,
                'underutilized_count': sum(1 for asg in asg_analysis if asg['underutilized'])
            }
        
        except Exception as e:
            print(f"Warning: Could not analyze Auto Scaling Groups: {e}")
            return {'total_asgs': 0, 'asgs': [], 'underutilized_count': 0}

    
    def get_all_regions(self) -> List[str]:
        """Get all available AWS regions"""
        try:
            regions = self.ec2_client.describe_regions()
            return [region['RegionName'] for region in regions['Regions']]
        except Exception as e:
            print(f"Warning: Could not get regions: {e}")
            return ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1']
    
    def analyze_global_resources(self) -> Dict:
        """Analyze resources across all regions"""
        regions = self.get_all_regions()
        
        global_resources = {
            'regions_analyzed': [],
            'ec2_instances': {},
            'rds_instances': {},
            'lambda_functions': {},
            'ebs_volumes': {},
            's3_buckets': 0,  # S3 is global
            'total_resources': 0
        }
        
        for region in regions[:10]:  # Limit to 10 regions for performance
            try:
                # Create regional clients
                ec2_regional = self.session.client('ec2', region_name=region)
                rds_regional = self.session.client('rds', region_name=region)
                lambda_regional = self.session.client('lambda', region_name=region)
                
                # Count EC2 instances
                ec2_response = ec2_regional.describe_instances()
                ec2_count = sum(len(r['Instances']) for r in ec2_response.get('Reservations', []))
                
                # Count RDS instances
                rds_response = rds_regional.describe_db_instances()
                rds_count = len(rds_response.get('DBInstances', []))
                
                # Count Lambda functions
                lambda_response = lambda_regional.list_functions()
                lambda_count = len(lambda_response.get('Functions', []))
                
                # Count EBS volumes
                ebs_response = ec2_regional.describe_volumes()
                ebs_count = len(ebs_response.get('Volumes', []))
                
                if ec2_count > 0 or rds_count > 0 or lambda_count > 0 or ebs_count > 0:
                    global_resources['regions_analyzed'].append(region)
                    global_resources['ec2_instances'][region] = ec2_count
                    global_resources['rds_instances'][region] = rds_count
                    global_resources['lambda_functions'][region] = lambda_count
                    global_resources['ebs_volumes'][region] = ebs_count
                    global_resources['total_resources'] += ec2_count + rds_count + lambda_count + ebs_count
            
            except Exception as e:
                continue
        
        # S3 is global
        try:
            buckets = self.s3_client.list_buckets()
            global_resources['s3_buckets'] = len(buckets.get('Buckets', []))
            global_resources['total_resources'] += global_resources['s3_buckets']
        except:
            pass
        
        return global_resources
    
    def get_budget_alerts(self) -> Dict:
        """Get AWS Budget alerts and forecasts"""
        try:
            budgets_client = self.session.client('budgets', region_name='us-east-1')
            account_id = self.sts_client.get_caller_identity()['Account']
            
            # List budgets
            budgets_response = budgets_client.describe_budgets(AccountId=account_id)
            
            budget_analysis = []
            total_budget = 0
            total_actual = 0
            total_forecasted = 0
            alerts = []
            
            for budget in budgets_response.get('Budgets', []):
                budget_name = budget.get('BudgetName', 'N/A')
                budget_limit = float(budget.get('BudgetLimit', {}).get('Amount', 0))
                
                calculated_spend = budget.get('CalculatedSpend', {})
                actual_spend = float(calculated_spend.get('ActualSpend', {}).get('Amount', 0))
                forecasted_spend = float(calculated_spend.get('ForecastedSpend', {}).get('Amount', 0))
                
                utilization = (actual_spend / budget_limit * 100) if budget_limit > 0 else 0
                
                total_budget += budget_limit
                total_actual += actual_spend
                total_forecasted += forecasted_spend
                
                # Check for alerts
                if utilization > 80:
                    alerts.append({
                        'budget': budget_name,
                        'severity': 'Critical' if utilization > 100 else 'High',
                        'message': f'{budget_name} at {utilization:.1f}% utilization',
                        'actual': actual_spend,
                        'limit': budget_limit
                    })
                
                budget_analysis.append({
                    'name': budget_name,
                    'limit': budget_limit,
                    'actual': actual_spend,
                    'forecasted': forecasted_spend,
                    'utilization': utilization
                })
            
            return {
                'budgets': budget_analysis,
                'total_budget': total_budget,
                'total_actual': total_actual,
                'total_forecasted': total_forecasted,
                'alerts': alerts,
                'alert_count': len(alerts)
            }
        
        except Exception as e:
            print(f"Warning: Could not get budget information: {e}")
            return {
                'budgets': [],
                'total_budget': 0,
                'total_actual': 0,
                'total_forecasted': 0,
                'alerts': [],
                'alert_count': 0
            }
    
    def generate_overall_recommendations(self, all_data: Dict) -> Dict:
        """Generate overall account-level cost savings recommendations"""
        recommendations = {
            'immediate_actions': [],
            'short_term': [],
            'long_term': [],
            'total_potential_savings': 0
        }
        
        # Calculate total potential savings
        idle_waste = all_data.get('idle_resources', {}).get('total_monthly_waste', 0)
        rightsizing_savings = all_data.get('rightsizing', {}).get('total_monthly_savings', 0)
        sp_savings = all_data.get('savings_plans', {}).get('estimated_savings', 0) / 12
        
        total_monthly_savings = idle_waste + rightsizing_savings + sp_savings
        recommendations['total_potential_savings'] = total_monthly_savings
        
        # Immediate actions (0-1 week)
        if idle_waste > 0:
            recommendations['immediate_actions'].append({
                'title': 'Remove Idle Resources',
                'savings': f'${idle_waste:,.2f}/month',
                'effort': 'Low',
                'description': f'Delete {all_data.get("idle_resources", {}).get("total_items", 0)} idle resources'
            })
        
        # Check for unattached EBS volumes
        ebs_count = len(all_data.get('idle_resources', {}).get('ebs_volumes', []))
        if ebs_count > 0:
            recommendations['immediate_actions'].append({
                'title': 'Delete Unattached EBS Volumes',
                'savings': f'${sum(v["monthly_cost"] for v in all_data.get("idle_resources", {}).get("ebs_volumes", [])):,.2f}/month',
                'effort': 'Low',
                'description': f'Remove {ebs_count} unattached volumes'
            })
        
        # Short-term actions (1-4 weeks)
        if rightsizing_savings > 100:
            recommendations['short_term'].append({
                'title': 'Rightsize EC2 Instances',
                'savings': f'${rightsizing_savings:,.2f}/month',
                'effort': 'Medium',
                'description': f'{len(all_data.get("rightsizing", {}).get("recommendations", []))} instances can be downsized'
            })
        
        # Check RDS underutilization
        rds_underutilized = all_data.get('rds_data', {}).get('underutilized_count', 0)
        if rds_underutilized > 0:
            rds_savings = all_data.get('rds_data', {}).get('total_monthly_cost', 0) * 0.4
            recommendations['short_term'].append({
                'title': 'Rightsize RDS Instances',
                'savings': f'${rds_savings:,.2f}/month',
                'effort': 'Medium',
                'description': f'{rds_underutilized} underutilized RDS instances'
            })
        
        # Check S3 optimization
        s3_opportunities = len(all_data.get('s3_data', {}).get('optimization_opportunities', []))
        if s3_opportunities > 0:
            s3_savings = all_data.get('s3_data', {}).get('estimated_monthly_cost', 0) * 0.3
            recommendations['short_term'].append({
                'title': 'Implement S3 Lifecycle Policies',
                'savings': f'${s3_savings:,.2f}/month',
                'effort': 'Low',
                'description': f'{s3_opportunities} buckets without lifecycle policies'
            })
        
        # Long-term actions (1-3 months)
        if sp_savings > 100:
            recommendations['long_term'].append({
                'title': 'Purchase Savings Plans',
                'savings': f'${sp_savings:,.2f}/month',
                'effort': 'Low',
                'description': 'Commit to 1-year Savings Plans for predictable workloads'
            })
        
        # Check for Reserved Instance opportunities
        ri_recs = len(all_data.get('ri_data', {}).get('recommendations', {}).get('Recommendations', []))
        if ri_recs > 0:
            recommendations['long_term'].append({
                'title': 'Purchase Reserved Instances',
                'savings': 'Up to 72% discount',
                'effort': 'Low',
                'description': f'{ri_recs} RI purchase recommendations available'
            })
        
        return recommendations
