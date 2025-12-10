#!/usr/bin/env python3
"""
BCT FinOps Tool v2.0
Professional Enterprise Cloud Financial Operations Platform
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import json
import hashlib

from src.enhanced_analyzer import EnhancedAWSAnalyzer
from src.enhanced_ai_recommender import EnhancedAIRecommender
from src.report_generator import ReportGenerator
from src.export_manager import ExportManager
from src.auth_manager import AuthManager
from src.cache_manager import CacheManager

# Page configuration
st.set_page_config(
    page_title="BCT FinOps Tool",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session cache manager
@st.cache_resource
def get_cache_manager():
    return CacheManager()

def init_session_state():
    """Initialize session state"""
    defaults = {
        'authenticated': False,
        'username': None,
        'user_email': None,
        'login_time': None,
        'analyzed': False,
        'current_page': 'Dashboard',
        'cost_data': None,
        'recommendations': None,
        'all_analysis_data': None
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def show_login_page():
    """Professional login page"""
    
    # Custom CSS for login
    st.markdown("""
        <style>
        .login-container {
            max-width: 500px;
            margin: 80px auto;
            padding: 50px;
            background: linear-gradient(135deg, #0066cc 0%, #003d7a 100%);
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 102, 204, 0.3);
        }
        
        .login-logo {
            text-align: center;
            color: white;
            font-size: 56px;
            font-weight: 900;
            letter-spacing: 3px;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }
        
        .login-subtitle {
            text-align: center;
            color: #e9ecef;
            font-size: 18px;
            margin-bottom: 40px;
        }
        
        .login-form {
            background: white;
            padding: 30px;
            border-radius: 15px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
            <div class='login-container'>
                <div class='login-logo'>BCT</div>
                <div class='login-subtitle'>FinOps Tool</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🔐 Sign In to Continue")
        
        with st.form("login_form"):
            username = st.text_input("👤 Username", placeholder="Enter your username")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                login_button = st.form_submit_button("🚀 Sign In", use_container_width=True)
            
            with col_b:
                demo_button = st.form_submit_button("👁️ Demo Mode", use_container_width=True)
        
        if login_button:
            if username and password:
                auth_manager = AuthManager()
                if auth_manager.authenticate(username, password):
                    user_info = auth_manager.get_user_info(username)
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.user_email = user_info.get('email', 'N/A')
                    st.session_state.login_time = datetime.now()
                    st.session_state.current_page = "Configuration"  # Start at Configuration page
                    st.success(f"✅ Welcome back, {username}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
            else:
                st.warning("⚠️ Please enter both username and password")
        
        if demo_button:
            st.session_state.authenticated = True
            st.session_state.username = "demo_user"
            st.session_state.user_email = "demo@bct.com"
            st.session_state.login_time = datetime.now()
            st.session_state.current_page = "Configuration"  # Start at Configuration page
            st.info("👁️ Entering demo mode...")
            st.rerun()
        
        st.markdown("---")
        
        st.info("""
            **Default Credentials:**
            - Username: `admin`
            - Password: `admin123`
            
            **Demo Mode:** Try without credentials
        """)

def show_user_info():
    """Display user info in header"""
    login_duration = ""
    if st.session_state.login_time:
        duration = datetime.now() - st.session_state.login_time
        hours = int(duration.total_seconds() // 3600)
        minutes = int((duration.total_seconds() % 3600) // 60)
        login_duration = f"{hours}h {minutes}m"
    
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, #0066cc 0%, #003d7a 100%); 
                    padding: 20px; border-radius: 10px; margin-bottom: 20px;
                    box-shadow: 0 4px 12px rgba(0, 102, 204, 0.2);'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div>
                    <h1 style='color: white; margin: 0; font-size: 36px;'>BCT FINOPS TOOL</h1>
                    <p style='color: #e9ecef; margin: 5px 0 0 0;'>Enterprise Cloud Financial Operations Platform</p>
                </div>
                <div style='text-align: right;'>
                    <div style='background: rgba(255,255,255,0.2); padding: 10px 20px; border-radius: 8px;'>
                        <div style='color: white; font-size: 14px;'>
                            <strong>👤 {st.session_state.username}</strong><br>
                            <small>{st.session_state.user_email}</small><br>
                            <small>⏱️ Session: {login_duration}</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def show_sidebar_navigation():
    """Side navigation with tabs"""
    
    st.sidebar.markdown("""
        <div style='text-align: center; padding: 20px 0; background: linear-gradient(135deg, #0066cc 0%, #003d7a 100%); 
                    border-radius: 10px; margin-bottom: 20px;'>
            <div style='font-size: 32px; font-weight: 800; color: white;'>BCT</div>
            <div style='font-size: 14px; color: #e9ecef;'>FinOps Tool</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("### 📋 Navigation")
    
    pages = {
        "🔐 Login": "Configuration",
        "🏠 Dashboard": "Dashboard",
        "🌍 Global View": "Global",
        "📊 KPI": "KPI",
        "💡 Recommendations": "Recommendations",
        "🗂️ Resources": "Resources",
        "💰 Savings Plans": "Savings",
        "💳 Budget Manager": "Budget",
        "📈 Analytics": "Analytics",
        "📄 Reports": "Reports"
    }
    
    for label, page in pages.items():
        if st.sidebar.button(label, use_container_width=True, 
                            type="primary" if st.session_state.current_page == page else "secondary"):
            st.session_state.current_page = page
            st.rerun()
    
    st.sidebar.markdown("---")
    
    # User info in sidebar
    st.sidebar.markdown(f"""
        <div style='background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 10px;'>
            <div style='font-size: 12px; color: #6c757d;'>Logged in as:</div>
            <div style='font-size: 14px; font-weight: 600; color: #212529;'>{st.session_state.username}</div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

def show_dashboard():
    """Main dashboard"""
    st.markdown("## 📊 Executive Dashboard")
    
    if not st.session_state.analyzed:
        st.info("👈 Please configure AWS credentials in Settings to begin analysis")
        
        # Quick stats placeholder
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Cost", "$0.00", help="6-month total")
        with col2:
            st.metric("Monthly Avg", "$0.00", help="Average monthly cost")
        with col3:
            st.metric("Recommendations", "0", help="Optimization opportunities")
        with col4:
            st.metric("Potential Savings", "$0.00", help="Monthly savings")
        
        st.markdown("---")
        
        st.markdown("""
            ### 🚀 Get Started
            
            1. Go to **Settings** in the sidebar
            2. Enter your AWS credentials
            3. Click **Analyze Account**
            4. View comprehensive cost analysis and recommendations
        """)
    else:
        # Show actual dashboard with data
        data = st.session_state.all_analysis_data
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_cost = data.get('cost_data', {}).get('total_cost', 0)
            st.metric("Total Cost (6mo)", f"${total_cost:,.2f}")
        
        with col2:
            monthly_avg = total_cost / 6
            st.metric("Monthly Average", f"${monthly_avg:,.2f}")
        
        with col3:
            rec_count = len(data.get('recommendations', []))
            st.metric("Recommendations", rec_count)
        
        with col4:
            idle_waste = data.get('idle_resources', {}).get('total_monthly_waste', 0)
            st.metric("Potential Savings", f"${idle_waste:,.2f}/mo", 
                     delta=f"-${idle_waste*12:,.2f}/yr", delta_color="inverse")
        
        st.markdown("---")
        
        # Resource summary
        st.markdown("### 📦 Resource Summary")
        
        res_col1, res_col2, res_col3, res_col4, res_col5 = st.columns(5)
        
        with res_col1:
            # Get EC2 count from rightsizing recommendations
            rightsizing = data.get('rightsizing', {})
            ec2_recommendations = rightsizing.get('recommendations', [])
            if isinstance(ec2_recommendations, dict):
                ec2_recommendations = ec2_recommendations.get('RightsizingRecommendations', [])
            ec2_count = len(ec2_recommendations) if ec2_recommendations else 0
            st.metric("EC2 Instances", ec2_count)
        
        with res_col2:
            st.metric("S3 Buckets", data.get('s3_data', {}).get('total_buckets', 0))
        
        with res_col3:
            st.metric("RDS Instances", data.get('rds_data', {}).get('total_instances', 0))
        
        with res_col4:
            st.metric("Lambda Functions", data.get('lambda_data', {}).get('total_functions', 0))
        
        with res_col5:
            st.metric("Idle Resources", data.get('idle_resources', {}).get('total_items', 0))

def show_global_view():
    """Global resource view"""
    st.markdown("## 🌍 Global View")
    
    if not st.session_state.analyzed:
        st.info("👈 Please run analysis in Settings first")
        return
    
    data = st.session_state.all_analysis_data
    
    # Budget Alerts
    budget_alerts = data.get('budget_alerts', {})
    
    if budget_alerts.get('alert_count', 0) > 0:
        st.error(f"⚠️ {budget_alerts['alert_count']} Budget Alert(s) Detected!")
        
        for alert in budget_alerts.get('alerts', []):
            severity_color = 'red' if alert['severity'] == 'Critical' else 'orange'
            st.warning(f"**{alert['severity']}**: {alert['message']}")
    else:
        st.success("✅ All budgets within limits")
    
    # Budget metrics
    budget_col1, budget_col2, budget_col3, budget_col4 = st.columns(4)
    
    with budget_col1:
        st.metric("Total Budget", f"${budget_alerts.get('total_budget', 0):,.0f}")
    with budget_col2:
        st.metric("Actual Spend", f"${budget_alerts.get('total_actual', 0):,.0f}")
    with budget_col3:
        st.metric("Forecasted", f"${budget_alerts.get('total_forecasted', 0):,.0f}")
    with budget_col4:
        total_budget = budget_alerts.get('total_budget', 0)
        total_actual = budget_alerts.get('total_actual', 0)
        utilization = (total_actual / total_budget * 100) if total_budget > 0 else 0
        st.metric("Utilization", f"{utilization:.1f}%")
    
    st.markdown("---")
    
    # Global Resources
    st.markdown("### 🗺️ Multi-Region Resource Distribution")
    
    global_resources = data.get('global_resources', {})
    
    global_col1, global_col2, global_col3 = st.columns(3)
    
    with global_col1:
        st.metric("Regions with Resources", len(global_resources.get('regions_analyzed', [])))
    with global_col2:
        st.metric("Total Resources", global_resources.get('total_resources', 0))
    with global_col3:
        st.metric("S3 Buckets (Global)", global_resources.get('s3_buckets', 0))
    
    st.markdown("---")
    
    # Regional breakdown - Build region list from multiple sources
    regions_list = global_resources.get('regions_analyzed', [])
    
    # If no regions from global analysis, try to extract from other data sources
    if not regions_list:
        # Try to get regions from RDS data
        rds_data = data.get('rds_data', {})
        if rds_data.get('instances'):
            regions_list.extend([inst.get('region') for inst in rds_data['instances'] if inst.get('region')])
        
        # Try to get regions from Lambda data
        lambda_data = data.get('lambda_data', {})
        if lambda_data.get('functions'):
            regions_list.extend([func.get('region') for func in lambda_data['functions'] if func.get('region')])
        
        # Remove duplicates and None values
        regions_list = list(set([r for r in regions_list if r]))
    
    # If still no regions, use common AWS regions as fallback
    if not regions_list:
        regions_list = ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1', 'ap-south-1']
        st.info("💡 Using default AWS regions. Run a fresh analysis to get actual regional data.")
    
    # Show regional breakdown table if we have data
    if global_resources.get('regions_analyzed'):
        st.markdown("##### 📊 Resources by Region")
        
        region_data = []
        for region in global_resources['regions_analyzed']:
            region_data.append({
                'Region': region,
                'EC2': global_resources.get('ec2_instances', {}).get(region, 0),
                'RDS': global_resources.get('rds_instances', {}).get(region, 0),
                'Lambda': global_resources.get('lambda_functions', {}).get(region, 0),
                'EBS': global_resources.get('ebs_volumes', {}).get(region, 0)
            })
        
        df = pd.DataFrame(region_data)
        st.dataframe(df, use_container_width=True)
        
        st.markdown("---")
    
    # Region Selector for Detailed View - Always show
    st.markdown("### 🔍 Regional Resource Explorer")
    
    # Check if we have actual regional data
    has_regional_data = bool(global_resources.get('regions_analyzed'))
    
    if not has_regional_data:
        st.warning("""
            ⚠️ **Regional data not available in current analysis.**
            
            The current analysis doesn't include region-specific resource information. 
            All resources shown below are from all regions combined.
            
            **Note:** Region selector is shown for reference, but filtering by region 
            requires the analyzer to capture region information during analysis.
        """)
    
    if regions_list:
            # Region selector
            selected_region = st.selectbox(
                "Select a region:",
                options=regions_list,
                index=0,
                help="Region selector for reference. Actual filtering requires regional data from analysis."
            )
            
            if has_regional_data:
                st.markdown(f"#### 📍 Resources in {selected_region}")
            else:
                st.markdown(f"#### 📍 All Resources (Region filter not available)")
            
            # Create tabs for different resource types
            reg_tab1, reg_tab2, reg_tab3, reg_tab4, reg_tab5 = st.tabs([
                "💻 EC2", "🗄️ RDS", "⚡ Lambda", "💾 EBS", "📊 Summary"
            ])
            
            with reg_tab1:
                st.markdown(f"##### EC2 Instances")
                
                # Get EC2 data from rightsizing recommendations
                rightsizing = data.get('rightsizing', {})
                ec2_recommendations = rightsizing.get('recommendations', [])
                if isinstance(ec2_recommendations, dict):
                    ec2_recommendations = ec2_recommendations.get('RightsizingRecommendations', [])
                
                # Try to filter by region if region info is available
                filtered_ec2 = []
                if ec2_recommendations:
                    for rec in ec2_recommendations:
                        current_instance = rec.get('CurrentInstance', {})
                        
                        # Try to extract region from resource details
                        resource_details = current_instance.get('ResourceDetails', {})
                        ec2_details = resource_details.get('EC2ResourceDetails', {})
                        instance_region = ec2_details.get('Region', '')
                        
                        # If region matches or no region info available, include it
                        if not instance_region or instance_region == selected_region:
                            instance_id = (
                                current_instance.get('ResourceId') or 
                                current_instance.get('InstanceId') or
                                'Unknown'
                            )
                            instance_type = (
                                current_instance.get('InstanceType') or
                                ec2_details.get('InstanceType') or
                                'Unknown'
                            )
                            
                            filtered_ec2.append({
                                'Instance ID': instance_id,
                                'Instance Type': instance_type,
                                'Region': instance_region if instance_region else 'Not specified',
                                'Finding': rec.get('Finding', 'N/A')
                            })
                
                if filtered_ec2:
                    st.metric("EC2 Instances", len(filtered_ec2))
                    df_ec2 = pd.DataFrame(filtered_ec2)
                    st.dataframe(df_ec2, use_container_width=True)
                    
                    # Check if region filtering worked
                    regions_in_data = [inst['Region'] for inst in filtered_ec2 if inst['Region'] != 'Not specified']
                    if not regions_in_data:
                        st.info(f"ℹ️ Showing all EC2 instances (region data not available in analysis)")
                    elif len(filtered_ec2) < len(ec2_recommendations):
                        st.success(f"✅ Filtered to show {len(filtered_ec2)} EC2 instance(s) in {selected_region}")
                    else:
                        st.info(f"ℹ️ Showing all EC2 instances")
                    
                    st.caption(f"💡 Check Resources → EC2 tab for detailed rightsizing recommendations.")
                else:
                    st.info(f"No EC2 instances found")
            
            with reg_tab2:
                st.markdown(f"##### RDS Instances")
                
                # Show RDS instances
                rds_data = data.get('rds_data', {})
                
                if rds_data.get('instances'):
                    # Try to filter by region
                    rds_instances = rds_data['instances']
                    filtered_rds = [inst for inst in rds_instances if inst.get('region') == selected_region or inst.get('availability_zone', '').startswith(selected_region)]
                    
                    # If no region info or no matches, show all
                    if not filtered_rds:
                        filtered_rds = rds_instances
                        has_region_info = False
                    else:
                        has_region_info = True
                    
                    st.metric("RDS Instances", len(filtered_rds))
                    
                    # Display RDS table
                    try:
                        df_rds = pd.DataFrame(filtered_rds)
                        st.dataframe(df_rds, use_container_width=True)
                        
                        if not has_region_info and len(filtered_rds) == len(rds_instances):
                            st.info(f"ℹ️ Showing all RDS instances (region data not available in analysis)")
                        elif len(filtered_rds) < len(rds_instances):
                            st.success(f"✅ Filtered to show {len(filtered_rds)} RDS instance(s) in {selected_region}")
                        else:
                            st.info(f"ℹ️ Showing all RDS instances")
                        
                        st.caption(f"💡 Check Resources → RDS tab for optimization recommendations.")
                    except Exception as e:
                        st.error(f"Error displaying RDS data: {str(e)}")
                else:
                    st.info(f"No RDS instances found")
            
            with reg_tab3:
                st.markdown(f"##### Lambda Functions")
                
                # Show Lambda functions
                lambda_data = data.get('lambda_data', {})
                
                if lambda_data.get('functions'):
                    # Try to filter by region
                    lambda_functions = lambda_data['functions']
                    filtered_lambda = [func for func in lambda_functions if func.get('region') == selected_region]
                    
                    # If no region info or no matches, show all
                    if not filtered_lambda:
                        filtered_lambda = lambda_functions
                        has_region_info = False
                    else:
                        has_region_info = True
                    
                    st.metric("Lambda Functions", len(filtered_lambda))
                    
                    # Display Lambda table
                    try:
                        df_lambda = pd.DataFrame(filtered_lambda)
                        st.dataframe(df_lambda, use_container_width=True)
                        
                        if not has_region_info and len(filtered_lambda) == len(lambda_functions):
                            st.info(f"ℹ️ Showing all Lambda functions (region data not available in analysis)")
                        elif len(filtered_lambda) < len(lambda_functions):
                            st.success(f"✅ Filtered to show {len(filtered_lambda)} Lambda function(s) in {selected_region}")
                        else:
                            st.info(f"ℹ️ Showing all Lambda functions")
                        
                        st.caption(f"💡 Check Resources → Lambda tab for optimization recommendations.")
                    except Exception as e:
                        st.error(f"Error displaying Lambda data: {str(e)}")
                else:
                    st.info(f"No Lambda functions found")
            
            with reg_tab4:
                st.markdown(f"##### EBS Volumes")
                
                # Show EBS volumes from idle resources
                idle_resources = data.get('idle_resources', {})
                ebs_volumes = idle_resources.get('ebs_volumes', [])
                
                if ebs_volumes:
                    # Try to filter by region
                    filtered_ebs = [vol for vol in ebs_volumes if vol.get('region') == selected_region or vol.get('availability_zone', '').startswith(selected_region)]
                    
                    # If no region info or no matches, show all
                    if not filtered_ebs:
                        filtered_ebs = ebs_volumes
                        has_region_info = False
                    else:
                        has_region_info = True
                    
                    st.metric("Unattached EBS Volumes", len(filtered_ebs))
                    
                    # Display EBS table
                    try:
                        df_ebs = pd.DataFrame(filtered_ebs)
                        st.dataframe(df_ebs, use_container_width=True)
                        
                        if not has_region_info and len(filtered_ebs) == len(ebs_volumes):
                            st.info(f"ℹ️ Showing all unattached EBS volumes (region data not available in analysis)")
                        elif len(filtered_ebs) < len(ebs_volumes):
                            st.success(f"✅ Filtered to show {len(filtered_ebs)} EBS volume(s) in {selected_region}")
                        else:
                            st.info(f"ℹ️ Showing all unattached EBS volumes")
                        
                        st.caption(f"💡 These are unattached volumes. Consider deleting or attaching them to reduce costs.")
                    except Exception as e:
                        st.error(f"Error displaying EBS data: {str(e)}")
                else:
                    st.info(f"No unattached EBS volumes found")
            
            with reg_tab5:
                st.markdown(f"##### Resource Summary")
                
                # Get actual counts from data
                rightsizing = data.get('rightsizing', {})
                ec2_recs = rightsizing.get('recommendations', [])
                if isinstance(ec2_recs, dict):
                    ec2_recs = ec2_recs.get('RightsizingRecommendations', [])
                ec2_count = len(ec2_recs) if ec2_recs else 0
                
                rds_count = len(data.get('rds_data', {}).get('instances', []))
                lambda_count = len(data.get('lambda_data', {}).get('functions', []))
                ebs_count = len(data.get('idle_resources', {}).get('ebs_volumes', []))
                s3_count = data.get('s3_data', {}).get('total_buckets', 0)
                
                # Summary metrics
                sum_col1, sum_col2, sum_col3, sum_col4, sum_col5 = st.columns(5)
                
                with sum_col1:
                    st.metric("EC2 Instances", ec2_count)
                with sum_col2:
                    st.metric("RDS Instances", rds_count)
                with sum_col3:
                    st.metric("Lambda Functions", lambda_count)
                with sum_col4:
                    st.metric("EBS Volumes", ebs_count)
                with sum_col5:
                    st.metric("S3 Buckets", s3_count)
                
                # Total resources
                total_resources = ec2_count + rds_count + lambda_count + ebs_count + s3_count
                
                st.markdown("---")
                st.metric("Total Resources", total_resources)
                
                # Resource breakdown chart
                if total_resources > 0:
                    st.markdown("##### Resource Distribution")
                    
                    resource_breakdown = {
                        'EC2': ec2_count,
                        'RDS': rds_count,
                        'Lambda': lambda_count,
                        'EBS': ebs_count,
                        'S3': s3_count
                    }
                    
                    # Filter out zero values
                    resource_breakdown = {k: v for k, v in resource_breakdown.items() if v > 0}
                    
                    if resource_breakdown:
                        import plotly.express as px
                        fig = px.pie(
                            values=list(resource_breakdown.values()),
                            names=list(resource_breakdown.keys()),
                            title='Resource Type Distribution'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("---")
                
                # Regional recommendations
                st.markdown("##### 💡 Optimization Tips")
                
                if total_resources > 0:
                    st.info(f"""
                        **General Optimization Opportunities:**
                        
                        - Review if all resources are actively used
                        - Consider consolidating resources to fewer regions to reduce complexity
                        - Check for cross-region data transfer costs
                        - Ensure proper tagging for cost allocation
                        - Implement backup and disaster recovery strategies
                        - Use the Recommendations tab for specific optimization actions
                    """)
    else:
        st.warning("⚠️ No regional data available.")
        
        # Show alternative view with available data
        st.markdown("#### 📊 Available Resources Overview")
        
        alt_col1, alt_col2, alt_col3, alt_col4 = st.columns(4)
        
        with alt_col1:
            s3_buckets = data.get('s3_data', {}).get('total_buckets', 0)
            st.metric("S3 Buckets", s3_buckets)
        
        with alt_col2:
            rds_instances = data.get('rds_data', {}).get('total_instances', 0)
            st.metric("RDS Instances", rds_instances)
        
        with alt_col3:
            lambda_functions = data.get('lambda_data', {}).get('total_functions', 0)
            st.metric("Lambda Functions", lambda_functions)
        
        with alt_col4:
            rightsizing = data.get('rightsizing', {})
            ec2_recs = rightsizing.get('recommendations', [])
            if isinstance(ec2_recs, dict):
                ec2_recs = ec2_recs.get('RightsizingRecommendations', [])
            st.metric("EC2 Instances", len(ec2_recs) if ec2_recs else 0)
        
        st.info("💡 **Tip**: Run a fresh analysis to get detailed regional resource distribution.")

def show_recommendations():
    """Recommendations page"""
    st.markdown("## 💡 Cost Optimization Recommendations")
    
    if not st.session_state.analyzed:
        st.info("👈 Please run analysis in Settings first")
        return
    
    data = st.session_state.all_analysis_data
    recommendations = data.get('recommendations', [])
    
    if not recommendations:
        st.warning("⚠️ No recommendations available. This could mean:")
        st.info("""
            - Your AWS account is already well-optimized
            - The analysis didn't find any optimization opportunities
            - There was an issue generating recommendations
        """)
        return
    
    # Summary cards
    st.markdown("### 📊 Recommendations Summary")
    
    sum_col1, sum_col2, sum_col3, sum_col4 = st.columns(4)
    
    with sum_col1:
        st.metric("Total Recommendations", len(recommendations))
    
    with sum_col2:
        critical_high = sum(1 for r in recommendations if r.get('severity') in ['Critical', 'High'])
        st.metric("High Priority", critical_high)
    
    with sum_col3:
        easy_recs = sum(1 for r in recommendations if r.get('difficulty') == 'Easy')
        st.metric("Easy to Implement", easy_recs)
    
    with sum_col4:
        # Calculate total potential savings
        total_savings = 0
        for rec in recommendations:
            savings_str = rec.get('estimated_savings', '')
            try:
                numeric_str = savings_str.replace('$', '').replace(',', '').split('/')[0].strip()
                if numeric_str and numeric_str[0].isdigit():
                    total_savings += float(numeric_str)
            except:
                continue
        st.metric("Potential Savings", f"${total_savings:,.0f}/mo")
    
    st.markdown("---")
    
    # Filters
    st.markdown("### 🔍 Filter Recommendations")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        severity_filter = st.multiselect(
            "Severity",
            ["Critical", "High", "Medium", "Low"],
            default=["Critical", "High", "Medium", "Low"]
        )
    
    with col2:
        categories = list(set(r.get('category', 'Other') for r in recommendations))
        category_filter = st.multiselect("Category", categories, default=categories)
    
    with col3:
        difficulty_filter = st.multiselect(
            "Difficulty",
            ["Easy", "Medium", "Hard", "Complex"],
            default=["Easy", "Medium", "Hard", "Complex"]
        )
    
    # Filter recommendations
    filtered = [r for r in recommendations 
                if r.get('severity') in severity_filter 
                and r.get('category', 'Other') in category_filter
                and r.get('difficulty', 'Medium') in difficulty_filter]
    
    st.markdown(f"### 📋 Showing {len(filtered)} of {len(recommendations)} recommendations")
    
    if not filtered:
        st.warning("No recommendations match your filters. Try adjusting the filters above.")
        return
    
    # Display recommendations
    for idx, rec in enumerate(filtered, 1):
        severity_emoji = {'Critical': '🔴', 'High': '🟠', 'Medium': '🟡', 'Low': '🟢'}
        priority_score = rec.get('priority_score', 50)
        
        # Create a colored header based on severity
        severity = rec.get('severity', 'Medium')
        severity_colors = {
            'Critical': '#dc3545',
            'High': '#fd7e14',
            'Medium': '#ffc107',
            'Low': '#28a745'
        }
        
        with st.expander(
            f"{severity_emoji.get(severity, '⚪')} [{priority_score}] {rec.get('title', 'Recommendation')}",
            expanded=(idx <= 3)  # Expand first 3 recommendations
        ):
            # Metrics row
            met_col1, met_col2, met_col3, met_col4 = st.columns(4)
            
            with met_col1:
                st.metric("💰 Savings", rec.get('estimated_savings', 'N/A'))
            with met_col2:
                st.metric("⏱️ Timeline", rec.get('timeline', 'N/A'))
            with met_col3:
                st.metric("🔧 Difficulty", rec.get('difficulty', 'N/A'))
            with met_col4:
                st.metric("📈 ROI", f"{rec.get('roi_months', 'N/A')} months")
            
            # Details
            st.markdown(f"**📂 Category:** {rec.get('category', 'N/A')}")
            st.markdown(f"**📝 Description:** {rec.get('description', 'N/A')}")
            st.markdown(f"**💥 Impact:** {rec.get('impact', 'N/A')}")
            
            # Implementation steps
            if rec.get('steps'):
                st.markdown("**📋 Implementation Steps:**")
                for i, step in enumerate(rec['steps'], 1):
                    st.markdown(f"{i}. {step}")
            
            # Risks
            if rec.get('risks'):
                st.markdown("**⚠️ Risks & Considerations:**")
                for risk in rec['risks']:
                    st.markdown(f"- {risk}")
            
            # Prerequisites
            if rec.get('prerequisites'):
                st.markdown("**✅ Prerequisites:**")
                for prereq in rec['prerequisites']:
                    st.markdown(f"- {prereq}")

def show_resources():
    """Resources page"""
    st.markdown("## 🗂️ Resource Analysis")
    
    if not st.session_state.analyzed:
        st.info("👈 Please run analysis in Settings first")
        return
    
    data = st.session_state.all_analysis_data
    
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "💾 Idle Resources",
        "💻 EC2 Instances",
        "📦 S3", 
        "🗄️ RDS", 
        "⚡ Lambda",
        "☸️ Containers",
        "🗃️ Databases"
    ])
    
    with tab1:
        idle = data.get('idle_resources', {})
        st.metric("Total Monthly Waste", f"${idle.get('total_monthly_waste', 0):,.2f}")
        
        if idle.get('ebs_volumes'):
            st.markdown("##### 💾 Unattached EBS Volumes")
            df = pd.DataFrame(idle['ebs_volumes'])
            st.dataframe(df, use_container_width=True)
        
        if idle.get('elastic_ips'):
            st.markdown("##### 🌐 Unassociated Elastic IPs")
            df = pd.DataFrame(idle['elastic_ips'])
            st.dataframe(df, use_container_width=True)
        
        if idle.get('load_balancers'):
            st.markdown("##### ⚖️ Idle Load Balancers")
            df = pd.DataFrame(idle['load_balancers'])
            st.dataframe(df, use_container_width=True)
        
        # AI Recommendations for Idle Resources
        total_waste = idle.get('total_monthly_waste', 0)
        if total_waste > 0:
            st.markdown("---")
            st.markdown("##### 🤖 AI Recommendations for Idle Resources")
            
            with st.expander("💡 View Immediate Cost Savings Actions", expanded=True):
                st.markdown(f"""
                    **💰 Potential Monthly Savings: ${total_waste:,.2f}**
                    
                    **Immediate Actions:**
                    
                    1. **Unattached EBS Volumes** ({len(idle.get('ebs_volumes', []))} found)
                       - Create snapshots of important volumes before deletion
                       - Delete volumes that are no longer needed
                       - Set up automated cleanup policies
                       - **Action**: Review each volume and delete or snapshot
                    
                    2. **Unassociated Elastic IPs** ({len(idle.get('elastic_ips', []))} found)
                       - Release unused Elastic IPs immediately
                       - Each idle EIP costs $0.005/hour ($3.60/month)
                       - Associate with instances or release
                       - **Action**: Release all unused IPs today
                    
                    3. **Idle Load Balancers** ({len(idle.get('load_balancers', []))} found)
                       - Review load balancers with no targets
                       - Delete unused load balancers
                       - Each ALB costs ~$16-25/month minimum
                       - **Action**: Audit and remove unused load balancers
                    
                    **Best Practices:**
                    - Set up AWS Config rules to detect idle resources
                    - Implement tagging strategy for resource tracking
                    - Schedule regular audits (weekly/monthly)
                    - Use AWS Trusted Advisor for automated detection
                    - Create CloudWatch alarms for unused resources
                    
                    **Automation Tips:**
                    - Use Lambda functions to automatically tag idle resources
                    - Implement automated cleanup after X days of inactivity
                    - Set up SNS notifications for new idle resources
                """)
                
                if total_waste > 100:
                    st.error(f"🚨 **Critical**: You're wasting ${total_waste:,.2f}/month on idle resources! Take immediate action to reduce costs.")
                elif total_waste > 50:
                    st.warning(f"⚠️ **Warning**: ${total_waste:,.2f}/month in idle resources detected. Review and clean up soon.")
                else:
                    st.info(f"💡 **Opportunity**: ${total_waste:,.2f}/month can be saved by cleaning up idle resources.")
    
    with tab2:
        st.markdown("### 💻 EC2 Instances")
        
        # Get rightsizing data which contains EC2 information
        rightsizing = data.get('rightsizing', {})
        
        # Handle different possible data structures
        if isinstance(rightsizing, dict):
            ec2_recommendations = rightsizing.get('recommendations', [])
            if isinstance(ec2_recommendations, dict):
                # If recommendations is a dict with 'RightsizingRecommendations' key
                ec2_recommendations = ec2_recommendations.get('RightsizingRecommendations', [])
        else:
            ec2_recommendations = []
        
        # Display EC2 metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Instances", len(ec2_recommendations))
        with col2:
            annual_savings = rightsizing.get('total_annual_savings', 0)
            monthly_savings = annual_savings / 12 if annual_savings else 0
            st.metric("Potential Monthly Savings", f"${monthly_savings:,.2f}")
        with col3:
            st.metric("Rightsizing Opportunities", len(ec2_recommendations))
        
        # Display EC2 instances from rightsizing recommendations
        if ec2_recommendations:
            st.markdown("##### 📋 EC2 Instance Details")
            
            ec2_data = []
            for rec in ec2_recommendations:
                # Try different possible keys for instance ID
                current_instance = rec.get('CurrentInstance', {})
                instance_id = (
                    current_instance.get('ResourceId') or 
                    current_instance.get('InstanceId') or
                    rec.get('InstanceId') or
                    rec.get('ResourceId') or
                    'Unknown'
                )
                
                # Get instance type
                current_type = (
                    current_instance.get('InstanceType') or
                    current_instance.get('ResourceDetails', {}).get('EC2ResourceDetails', {}).get('InstanceType') or
                    'Unknown'
                )
                
                finding = rec.get('Finding', 'Optimize')
                
                # Get savings
                monthly_savings = 0
                try:
                    monthly_savings = float(rec.get('EstimatedMonthlySavings', 0))
                except (ValueError, TypeError):
                    monthly_savings = 0
                
                # Get recommended instance type
                recommended_type = 'N/A'
                modify_rec = rec.get('ModifyRecommendationDetail', {})
                target_instances = modify_rec.get('TargetInstances', [])
                if target_instances and len(target_instances) > 0:
                    recommended_type = target_instances[0].get('InstanceType', 'N/A')
                
                # Also check for TerminateRecommendationDetail
                if recommended_type == 'N/A' and rec.get('TerminateRecommendationDetail'):
                    recommended_type = 'Terminate'
                
                ec2_data.append({
                    'Instance ID': instance_id,
                    'Current Type': current_type,
                    'Recommended Type': recommended_type,
                    'Finding': finding,
                    'Monthly Savings': f"${monthly_savings:.2f}"
                })
            
            if ec2_data:
                df = pd.DataFrame(ec2_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("⚠️ EC2 data structure not recognized. Please check the analysis data.")
        else:
            st.info("✅ No EC2 rightsizing recommendations found. Your instances appear to be optimally sized!")
        
        # AI Recommendations for EC2
        st.markdown("---")
        st.markdown("##### 🤖 AI Recommendations for EC2")
        
        with st.expander("💡 View Comprehensive EC2 Cost Optimization Strategies", expanded=True):
            st.markdown("""
                **EC2 Cost Optimization Strategies:**
                
                **1. Instance Rightsizing** (30-50% Savings)
                - Monitor CPU, memory, network, and disk utilization
                - Use CloudWatch metrics for at least 2 weeks
                - Downsize over-provisioned instances
                - Consider burstable instances (T3/T4g) for variable workloads
                - Use AWS Compute Optimizer for recommendations
                - **Action**: Review CloudWatch metrics and rightsize
                
                **2. Reserved Instances** (Up to 72% Savings)
                - Purchase RIs for steady-state workloads
                - Choose 1-year or 3-year terms
                - Standard RIs: Best discount, less flexibility
                - Convertible RIs: Change instance types, lower discount
                - All Upfront payment: Maximum savings
                - **ROI**: Typically pays back in 6-9 months
                
                **3. Savings Plans** (Up to 72% Savings)
                - More flexible than Reserved Instances
                - Compute Savings Plans: Any instance family, region, OS
                - EC2 Instance Savings Plans: Specific instance family
                - Automatically applies to eligible usage
                - **Recommended**: Start with Compute Savings Plans
                
                **4. Spot Instances** (Up to 90% Savings)
                - Perfect for fault-tolerant workloads
                - Batch processing, data analysis, CI/CD
                - Use Spot Fleet for automatic management
                - Implement Spot Instance interruption handling
                - Mix with On-Demand for critical workloads
                - **Best For**: Non-critical, flexible workloads
                
                **5. Graviton Instances** (40% Better Price-Performance)
                - AWS-designed ARM processors (Graviton2/3)
                - Instance types: M6g, C6g, R6g, T4g
                - Compatible with most Linux workloads
                - Better performance at lower cost
                - **Action**: Test and migrate compatible workloads
                
                **6. Auto Scaling** (20-40% Savings)
                - Scale instances based on demand
                - Use target tracking scaling policies
                - Schedule scaling for predictable patterns
                - Implement scale-in protection for critical instances
                - **Benefit**: Pay only for what you need
                
                **7. Stop/Start Automation** (Up to 70% Savings)
                - Stop non-production instances during off-hours
                - Use AWS Instance Scheduler
                - Automate with Lambda and EventBridge
                - **Example**: Stop dev/test instances nights and weekends
                
                **8. Instance Storage Optimization:**
                - Use EBS gp3 instead of gp2 (20% cheaper)
                - Right-size EBS volumes (monitor free space)
                - Delete unattached volumes
                - Use EBS snapshots for backups, not volumes
                - Consider instance store for temporary data
                
                **9. Network Optimization:**
                - Minimize cross-AZ data transfer
                - Use VPC endpoints for AWS services
                - Implement CloudFront for content delivery
                - Use Direct Connect for large data transfers
                - **Cost**: Data transfer can be 10-20% of EC2 costs
                
                **10. Operating System Optimization:**
                - Use Amazon Linux 2 (free, optimized for AWS)
                - Consider Windows Server alternatives
                - Optimize licensing (BYOL when beneficial)
                - Use License Manager for tracking
                
                **11. Monitoring & Automation:**
                - Enable detailed CloudWatch monitoring
                - Set up cost anomaly detection
                - Use AWS Trusted Advisor
                - Implement automated tagging
                - Create cost allocation tags
                
                **12. Placement Groups:**
                - Use cluster placement for HPC workloads
                - Spread placement for high availability
                - Partition placement for distributed systems
                - **Benefit**: Better performance, lower latency
                
                **13. Elastic Load Balancing:**
                - Use Application Load Balancer efficiently
                - Delete unused load balancers
                - Optimize health check intervals
                - Consider Gateway Load Balancer for specific use cases
                
                **14. Hibernation:**
                - Hibernate instances instead of stopping
                - Faster startup times
                - Preserve RAM contents
                - **Use Case**: Instances that need quick recovery
                
                **15. Migration Strategies:**
                - Containerize applications (ECS/EKS)
                - Move to serverless (Lambda, Fargate)
                - Use managed services when possible
                - Evaluate lift-and-shift vs re-architecture
            """)
            
            # Contextual recommendations based on data
            if len(ec2_recommendations) > 0:
                total_monthly_savings = sum(float(rec.get('EstimatedMonthlySavings', 0)) for rec in ec2_recommendations)
                st.error(f"🚨 **Immediate Action Required**: {len(ec2_recommendations)} instances can be rightsized for ${total_monthly_savings:,.2f}/month savings!")
            
            if len(ec2_recommendations) > 5:
                st.warning("⚠️ **Multiple Opportunities**: With multiple rightsizing opportunities, prioritize by savings amount and business impact.")
            
            st.info("""
                💡 **Quick Wins:**
                1. Start with rightsizing (immediate impact)
                2. Purchase RIs/Savings Plans for steady workloads
                3. Implement stop/start for dev/test environments
                4. Enable Auto Scaling for variable workloads
                5. Test Graviton instances for compatible workloads
            """)
    
    with tab3:
        st.markdown("### 📦 S3 Storage")
        
        s3 = data.get('s3_data', {})
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Buckets", s3.get('total_buckets', 0))
        with col2:
            st.metric("Total Size", f"{s3.get('total_size_gb', 0):,.0f} GB")
        with col3:
            st.metric("Monthly Cost", f"${s3.get('estimated_monthly_cost', 0):,.2f}")
        
        if s3.get('storage_details'):
            st.markdown("##### 📋 Bucket Details")
            try:
                df = pd.DataFrame(s3['storage_details'])
                st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"Error displaying bucket details: {str(e)}")
        
        if s3.get('optimization_opportunities'):
            st.markdown("##### 💡 Optimization Opportunities")
            for opp in s3['optimization_opportunities']:
                st.warning(f"**{opp.get('bucket', 'Unknown')}**: {opp.get('issue', 'N/A')} - {opp.get('recommendation', 'N/A')}")
        
        # AI Recommendations for S3
        if s3.get('total_buckets', 0) > 0:
            st.markdown("---")
            st.markdown("##### 🤖 AI Recommendations for S3")
            
            with st.expander("💡 View S3 Cost Optimization Strategies", expanded=False):
                st.markdown("""
                    **Storage Class Optimization:**
                    
                    1. **Intelligent-Tiering** (Recommended for Unknown Access Patterns)
                       - Automatically moves objects between access tiers
                       - No retrieval fees, no operational overhead
                       - Ideal for data with changing access patterns
                       - **Savings**: Up to 70% on storage costs
                    
                    2. **Lifecycle Policies** (High Impact)
                       - Transition to Standard-IA after 30 days (50% cheaper)
                       - Move to Glacier after 90 days (80% cheaper)
                       - Move to Glacier Deep Archive after 180 days (95% cheaper)
                       - Delete old versions and incomplete multipart uploads
                       - **Action**: Implement lifecycle rules on all buckets
                    
                    3. **Storage Class Selection Guide:**
                       - **Standard**: Frequently accessed data (most expensive)
                       - **Standard-IA**: Infrequent access, rapid retrieval (50% cheaper)
                       - **One Zone-IA**: Non-critical, infrequent access (20% cheaper than Standard-IA)
                       - **Glacier Instant Retrieval**: Archive with instant access (68% cheaper)
                       - **Glacier Flexible Retrieval**: Archive, minutes-hours retrieval (82% cheaper)
                       - **Glacier Deep Archive**: Long-term archive, 12-hour retrieval (95% cheaper)
                    
                    4. **Request Optimization:**
                       - Use S3 Select to retrieve only needed data
                       - Implement caching with CloudFront
                       - Batch small objects to reduce request costs
                       - Use S3 Batch Operations for bulk changes
                    
                    5. **Data Transfer Optimization:**
                       - Use CloudFront for content delivery (reduces data transfer costs)
                       - Enable S3 Transfer Acceleration for faster uploads
                       - Use VPC endpoints to avoid data transfer charges
                       - Compress data before uploading
                    
                    6. **Versioning & Replication:**
                       - Review versioning needs (old versions cost money)
                       - Implement lifecycle rules for non-current versions
                       - Evaluate cross-region replication necessity
                       - Use S3 Replication Time Control only when needed
                    
                    7. **Monitoring & Analytics:**
                       - Enable S3 Storage Lens for visibility
                       - Use S3 Analytics to understand access patterns
                       - Set up CloudWatch metrics for bucket monitoring
                       - Review S3 Inventory reports regularly
                """)
                
                total_size = s3.get('total_size_gb', 0)
                total_cost = s3.get('estimated_monthly_cost', 0)
                
                if total_size > 1000:  # More than 1TB
                    potential_savings = total_cost * 0.5  # Estimate 50% savings with optimization
                    st.warning(f"💰 **Large Storage Detected**: {total_size:,.0f} GB stored. Implementing lifecycle policies could save ~${potential_savings:,.2f}/month.")
                
                if total_cost > 100:
                    st.info(f"💡 **Optimization Opportunity**: With ${total_cost:,.2f}/month in S3 costs, consider Intelligent-Tiering and lifecycle policies.")
    
    with tab4:
        st.markdown("### 🗄️ RDS Databases")
        
        rds = data.get('rds_data', {})
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Instances", rds.get('total_instances', 0))
        with col2:
            st.metric("Underutilized", rds.get('underutilized_count', 0))
        with col3:
            st.metric("Monthly Cost", f"${rds.get('total_monthly_cost', 0):,.2f}")
        
        if rds.get('instances'):
            df = pd.DataFrame(rds['instances'])
            st.dataframe(df, use_container_width=True)
        
        # AI Recommendations for RDS
        if rds.get('total_instances', 0) > 0:
            st.markdown("---")
            st.markdown("##### 🤖 AI Recommendations for RDS")
            
            with st.expander("💡 View RDS Cost Optimization Strategies", expanded=False):
                st.markdown("""
                    **Database Cost Optimization:**
                    
                    1. **Instance Rightsizing** (High Impact)
                       - Monitor CPU, memory, and IOPS utilization
                       - Downsize underutilized instances
                       - Use CloudWatch metrics for 2-4 weeks before deciding
                       - Consider burstable instances (db.t3/t4g) for variable workloads
                       - **Savings**: 30-50% by rightsizing
                    
                    2. **Reserved Instances** (Highest ROI)
                       - Purchase RIs for production databases (up to 69% savings)
                       - Choose 1-year or 3-year terms
                       - All Upfront payment offers maximum discount
                       - **Action**: Commit to RIs for steady-state workloads
                    
                    3. **Storage Optimization:**
                       - Use gp3 instead of gp2 (20% cheaper, better performance)
                       - Right-size allocated storage (monitor free space)
                       - Enable storage autoscaling for growth
                       - Use Provisioned IOPS only when necessary
                       - Archive old data to S3
                    
                    4. **Multi-AZ Considerations:**
                       - Evaluate if Multi-AZ is necessary for all databases
                       - Use Multi-AZ for production only
                       - Consider read replicas for read-heavy workloads
                       - **Cost**: Multi-AZ doubles instance costs
                    
                    5. **Backup Optimization:**
                       - Adjust backup retention period (default is 7 days)
                       - Use automated backups instead of manual snapshots
                       - Delete old manual snapshots
                       - Consider cross-region backup necessity
                    
                    6. **Aurora Considerations:**
                       - Migrate from RDS to Aurora for better price-performance
                       - Use Aurora Serverless v2 for variable workloads
                       - Implement Aurora Global Database only when needed
                       - **Benefit**: Aurora can be more cost-effective at scale
                    
                    7. **Stop/Start Automation:**
                       - Stop non-production databases during off-hours
                       - Automate start/stop schedules with Lambda
                       - **Savings**: Up to 70% on dev/test environments
                    
                    8. **Performance Optimization:**
                       - Enable Performance Insights for query analysis
                       - Optimize slow queries to reduce compute needs
                       - Use read replicas to offload read traffic
                       - Implement connection pooling (RDS Proxy)
                    
                    9. **Graviton Instances:**
                       - Migrate to Graviton2/3 instances (db.m6g, db.r6g)
                       - **Savings**: Up to 35% better price-performance
                       - Compatible with most database engines
                """)
                
                underutilized = rds.get('underutilized_count', 0)
                total_cost = rds.get('total_monthly_cost', 0)
                
                if underutilized > 0:
                    potential_savings = total_cost * 0.3  # Estimate 30% savings
                    st.warning(f"⚠️ **{underutilized} Underutilized Instance(s)**: Rightsizing could save ~${potential_savings:,.2f}/month.")
                
                if total_cost > 500:
                    ri_savings = total_cost * 0.4  # Estimate 40% savings with RIs
                    st.info(f"💰 **Reserved Instance Opportunity**: With ${total_cost:,.2f}/month in RDS costs, RIs could save ~${ri_savings:,.2f}/month.")
    
    with tab5:
        st.markdown("### ⚡ Lambda Functions")
        
        lambda_data = data.get('lambda_data', {})
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Functions", lambda_data.get('total_functions', 0))
        with col2:
            st.metric("Rarely Used", lambda_data.get('rarely_used_count', 0))
        with col3:
            st.metric("30-Day Invocations", f"{lambda_data.get('total_invocations_30d', 0):,}")
        
        if lambda_data.get('functions'):
            df = pd.DataFrame(lambda_data['functions'])
            st.dataframe(df, use_container_width=True)
        
        # AI Recommendations for Lambda
        if lambda_data.get('total_functions', 0) > 0:
            st.markdown("---")
            st.markdown("##### 🤖 AI Recommendations for Lambda")
            
            with st.expander("💡 View Lambda Cost Optimization Strategies", expanded=False):
                st.markdown("""
                    **Serverless Cost Optimization:**
                    
                    1. **Memory Optimization** (Critical)
                       - Right-size memory allocation (128MB to 10GB)
                       - More memory = more CPU (proportional)
                       - Use AWS Lambda Power Tuning tool
                       - Test different memory settings for optimal cost/performance
                       - **Impact**: Can reduce costs by 20-50%
                    
                    2. **Execution Time Optimization:**
                       - Optimize code to reduce execution duration
                       - Use connection pooling for databases
                       - Implement caching strategies
                       - Minimize cold starts with provisioned concurrency
                       - Remove unnecessary dependencies
                       - **Billing**: Charged per 1ms of execution
                    
                    3. **Architecture Patterns:**
                       - Use Step Functions for complex workflows
                       - Implement async processing where possible
                       - Batch process multiple items per invocation
                       - Use SQS for buffering and rate limiting
                       - Consider EventBridge for event routing
                    
                    4. **Graviton2 Processors:**
                       - Use arm64 architecture instead of x86_64
                       - **Savings**: 20% lower cost, 19% better performance
                       - Compatible with most runtimes
                       - **Action**: Migrate functions to arm64
                    
                    5. **Provisioned Concurrency:**
                       - Use only for latency-sensitive functions
                       - Expensive: charged per hour of provisioned capacity
                       - Consider alternatives: Application Load Balancer warming
                       - Use auto-scaling for provisioned concurrency
                    
                    6. **Unused Function Cleanup:**
                       - Delete functions with zero invocations
                       - Remove old versions and aliases
                       - Clean up unused layers
                       - Implement automated cleanup policies
                    
                    7. **Monitoring & Alerts:**
                       - Set up CloudWatch alarms for high costs
                       - Monitor throttling and errors
                       - Track concurrent executions
                       - Use AWS Cost Anomaly Detection
                    
                    8. **VPC Configuration:**
                       - Avoid VPC unless necessary (adds cold start time)
                       - Use VPC endpoints to reduce NAT Gateway costs
                       - Consider Lambda Hyperplane ENIs for better performance
                    
                    9. **Request Optimization:**
                       - Reduce invocation frequency where possible
                       - Use CloudWatch Events/EventBridge scheduling
                       - Implement exponential backoff for retries
                       - Batch API calls
                    
                    10. **Alternative Services:**
                        - Consider Fargate for long-running tasks (>15 min)
                        - Use ECS/EKS for sustained high-volume workloads
                        - Evaluate AWS Batch for batch processing
                """)
                
                rarely_used = lambda_data.get('rarely_used_count', 0)
                total_functions = lambda_data.get('total_functions', 0)
                
                if rarely_used > 0:
                    st.warning(f"🗑️ **{rarely_used} Rarely Used Function(s)**: Consider deleting or consolidating unused functions.")
                
                if total_functions > 50:
                    st.info(f"📊 **Large Function Count**: With {total_functions} functions, consider using Lambda Power Tuning and arm64 architecture for optimization.")
                
                invocations = lambda_data.get('total_invocations_30d', 0)
                if invocations > 1000000:  # More than 1M invocations
                    st.success(f"💡 **High Volume Detected**: {invocations:,} invocations/month. Optimize memory and execution time for maximum savings.")
    
    with tab6:
        st.markdown("### ☸️ Container Services")
        
        # EKS
        eks = data.get('eks_data', {})
        st.markdown("#### Amazon EKS")
        
        eks_col1, eks_col2, eks_col3 = st.columns(3)
        with eks_col1:
            st.metric("Clusters", eks.get('total_clusters', 0))
        with eks_col2:
            st.metric("Monthly Cost", f"${eks.get('total_monthly_cost', 0):,.2f}")
        with eks_col3:
            total_nodes = sum(c.get('total_nodes', 0) for c in eks.get('clusters', []))
            st.metric("Total Nodes", total_nodes)
        
        if eks.get('clusters'):
            for cluster in eks['clusters']:
                with st.expander(f"🔷 {cluster['cluster_name']}"):
                    st.write(f"**Version:** {cluster['version']}")
                    st.write(f"**Status:** {cluster['status']}")
                    st.write(f"**Monthly Cost:** ${cluster['estimated_monthly_cost']:.2f}")
        
        # AI Recommendations for EKS
        if eks.get('total_clusters', 0) > 0:
            st.markdown("##### 🤖 AI Recommendations for EKS")
            
            with st.expander("💡 View EKS Optimization Recommendations", expanded=False):
                st.markdown("""
                    **Cost Optimization Strategies:**
                    
                    1. **Node Group Rightsizing**
                       - Review node instance types and sizes
                       - Consider using Spot Instances for non-critical workloads (up to 90% savings)
                       - Implement Cluster Autoscaler for dynamic scaling
                    
                    2. **Resource Utilization**
                       - Set appropriate resource requests and limits for pods
                       - Use Horizontal Pod Autoscaler (HPA) for automatic scaling
                       - Monitor and eliminate over-provisioned resources
                    
                    3. **Storage Optimization**
                       - Use EBS gp3 volumes instead of gp2 (up to 20% cost savings)
                       - Implement storage lifecycle policies
                       - Clean up unused Persistent Volumes
                    
                    4. **Networking Costs**
                       - Minimize cross-AZ data transfer
                       - Use VPC endpoints for AWS service communication
                       - Consider using AWS PrivateLink
                    
                    5. **Version Management**
                       - Keep EKS clusters updated to latest versions
                       - Newer versions often include performance improvements
                       - Plan regular upgrade cycles
                """)
                
                if eks.get('total_monthly_cost', 0) > 500:
                    st.warning("💰 **High Cost Alert**: Your EKS costs exceed $500/month. Consider implementing Spot Instances and rightsizing node groups.")
        
        st.markdown("---")
        
        # ECS
        ecs = data.get('ecs_data', {})
        st.markdown("#### Amazon ECS")
        
        ecs_col1, ecs_col2, ecs_col3 = st.columns(3)
        with ecs_col1:
            st.metric("Clusters", ecs.get('total_clusters', 0))
        with ecs_col2:
            st.metric("Running Tasks", ecs.get('total_tasks', 0))
        with ecs_col3:
            total_services = sum(c.get('services', 0) for c in ecs.get('clusters', []))
            st.metric("Services", total_services)
        
        # AI Recommendations for ECS
        if ecs.get('total_clusters', 0) > 0:
            st.markdown("##### 🤖 AI Recommendations for ECS")
            
            with st.expander("💡 View ECS Optimization Recommendations", expanded=False):
                st.markdown("""
                    **Cost Optimization Strategies:**
                    
                    1. **Compute Options**
                       - Consider AWS Fargate for simplified management (no EC2 to manage)
                       - Use EC2 launch type with Spot Instances for cost savings
                       - Evaluate Fargate Spot for non-critical workloads (70% discount)
                    
                    2. **Task Sizing**
                       - Right-size CPU and memory allocations
                       - Use CloudWatch Container Insights for utilization metrics
                       - Avoid over-provisioning resources
                    
                    3. **Auto Scaling**
                       - Implement ECS Service Auto Scaling
                       - Use target tracking scaling policies
                       - Scale based on actual demand patterns
                    
                    4. **Capacity Providers**
                       - Use ECS Capacity Providers for better resource utilization
                       - Mix On-Demand and Spot instances
                       - Implement cluster auto scaling
                    
                    5. **Task Placement**
                       - Optimize task placement strategies
                       - Use binpack strategy to maximize resource utilization
                       - Minimize cross-AZ traffic
                """)
                
                if ecs.get('total_tasks', 0) > 50:
                    st.info("📊 **Optimization Opportunity**: With 50+ tasks, consider implementing auto-scaling and capacity providers for better cost efficiency.")
    
    with tab7:
        st.markdown("### 🗃️ Database & Caching Services")
        
        # DynamoDB
        ddb = data.get('dynamodb_data', {})
        st.markdown("#### Amazon DynamoDB")
        
        ddb_col1, ddb_col2, ddb_col3 = st.columns(3)
        with ddb_col1:
            st.metric("Tables", ddb.get('total_tables', 0))
        with ddb_col2:
            st.metric("Monthly Cost", f"${ddb.get('total_monthly_cost', 0):,.2f}")
        with ddb_col3:
            total_size = sum(t.get('size_gb', 0) for t in ddb.get('tables', []))
            st.metric("Total Size", f"{total_size:.2f} GB")
        
        if ddb.get('tables'):
            df = pd.DataFrame(ddb['tables'])
            st.dataframe(df, use_container_width=True)
        
        # AI Recommendations for DynamoDB
        if ddb.get('total_tables', 0) > 0:
            st.markdown("##### 🤖 AI Recommendations for DynamoDB")
            
            with st.expander("💡 View DynamoDB Optimization Recommendations", expanded=False):
                st.markdown("""
                    **Cost Optimization Strategies:**
                    
                    1. **Capacity Mode Selection**
                       - Use On-Demand mode for unpredictable workloads
                       - Switch to Provisioned mode for predictable traffic (up to 60% savings)
                       - Consider Auto Scaling for provisioned capacity
                    
                    2. **Table Class Optimization**
                       - Use DynamoDB Standard-IA for infrequently accessed data (60% storage savings)
                       - Evaluate access patterns to determine optimal table class
                       - Monitor table access metrics
                    
                    3. **Data Lifecycle Management**
                       - Enable Time to Live (TTL) to automatically delete expired items
                       - Archive old data to S3 using DynamoDB exports
                       - Implement data retention policies
                    
                    4. **Query Optimization**
                       - Use efficient query patterns and indexes
                       - Avoid full table scans
                       - Implement pagination for large result sets
                    
                    5. **Backup Strategy**
                       - Use on-demand backups instead of continuous backups when possible
                       - Implement point-in-time recovery only when necessary
                       - Consider backup retention policies
                """)
                
                total_cost = ddb.get('total_monthly_cost', 0)
                if total_cost > 100:
                    st.warning(f"💰 **Cost Alert**: DynamoDB costs are ${total_cost:.2f}/month. Review capacity modes and consider Standard-IA for infrequent data.")
        
        st.markdown("---")
        
        # ElastiCache
        cache = data.get('elasticache_data', {})
        st.markdown("#### Amazon ElastiCache")
        
        cache_col1, cache_col2, cache_col3 = st.columns(3)
        with cache_col1:
            st.metric("Clusters", cache.get('total_clusters', 0))
        with cache_col2:
            st.metric("Monthly Cost", f"${cache.get('total_monthly_cost', 0):,.2f}")
        with cache_col3:
            total_nodes = sum(c.get('num_nodes', 0) for c in cache.get('clusters', []))
            st.metric("Nodes", total_nodes)
        
        # AI Recommendations for ElastiCache
        if cache.get('total_clusters', 0) > 0:
            st.markdown("##### 🤖 AI Recommendations for ElastiCache")
            
            with st.expander("💡 View ElastiCache Optimization Recommendations", expanded=False):
                st.markdown("""
                    **Cost Optimization Strategies:**
                    
                    1. **Instance Type Selection**
                       - Right-size cache nodes based on memory and CPU usage
                       - Consider current generation instance types (r6g, m6g)
                       - Use Graviton2-based instances for better price-performance
                    
                    2. **Reserved Nodes**
                       - Purchase Reserved Nodes for steady-state workloads (up to 55% savings)
                       - Choose 1-year or 3-year terms based on commitment
                       - Monitor utilization before committing
                    
                    3. **Cluster Configuration**
                       - Use cluster mode for Redis to distribute data across shards
                       - Implement read replicas for read-heavy workloads
                       - Optimize shard count based on data size
                    
                    4. **Data Management**
                       - Set appropriate TTL values for cached data
                       - Implement eviction policies (LRU, LFU)
                       - Monitor cache hit rates
                    
                    5. **Backup Strategy**
                       - Schedule backups during low-traffic periods
                       - Adjust backup retention based on requirements
                       - Consider snapshot costs in total cost
                """)
                
                if cache.get('total_monthly_cost', 0) > 200:
                    st.info("💡 **Savings Opportunity**: Consider Reserved Nodes for up to 55% savings on steady-state ElastiCache workloads.")
        
        st.markdown("---")
        
        # Redshift
        rs = data.get('redshift_data', {})
        st.markdown("#### Amazon Redshift")
        
        rs_col1, rs_col2, rs_col3 = st.columns(3)
        with rs_col1:
            st.metric("Clusters", rs.get('total_clusters', 0))
        with rs_col2:
            st.metric("Monthly Cost", f"${rs.get('total_monthly_cost', 0):,.2f}")
        with rs_col3:
            total_nodes = sum(c.get('num_nodes', 0) for c in rs.get('clusters', []))
            st.metric("Nodes", total_nodes)
        
        # AI Recommendations for Redshift
        if rs.get('total_clusters', 0) > 0:
            st.markdown("##### 🤖 AI Recommendations for Redshift")
            
            with st.expander("💡 View Redshift Optimization Recommendations", expanded=False):
                st.markdown("""
                    **Cost Optimization Strategies:**
                    
                    1. **Cluster Sizing**
                       - Right-size clusters based on query performance and storage needs
                       - Use Redshift Advisor recommendations
                       - Consider elastic resize for quick adjustments
                    
                    2. **Reserved Nodes**
                       - Purchase Reserved Nodes for production clusters (up to 75% savings)
                       - Choose appropriate node types and commitment terms
                       - Monitor utilization patterns
                    
                    3. **Pause and Resume**
                       - Pause clusters during non-business hours
                       - Automate pause/resume schedules
                       - Save costs on development/test clusters
                    
                    4. **Data Management**
                       - Implement data lifecycle policies
                       - Use Redshift Spectrum for infrequently accessed data
                       - Archive old data to S3
                    
                    5. **Query Optimization**
                       - Optimize table design and distribution keys
                       - Use sort keys effectively
                       - Monitor and optimize slow queries
                    
                    6. **Concurrency Scaling**
                       - Enable concurrency scaling for burst workloads
                       - Monitor concurrency scaling usage
                       - Set appropriate limits
                """)
                
                if rs.get('total_monthly_cost', 0) > 500:
                    st.warning("💰 **High Cost Alert**: Redshift costs exceed $500/month. Consider Reserved Nodes and pause/resume schedules for non-production clusters.")

def generate_maturity_data(data):
    """Generate maturity scoring data for export"""
    # Get basic metrics
    rightsizing = data.get('rightsizing', {})
    ec2_recs = rightsizing.get('recommendations', [])
    if isinstance(ec2_recs, dict):
        ec2_recs = ec2_recs.get('RightsizingRecommendations', [])
    
    idle_count = data.get('idle_resources', {}).get('total_items', 0)
    idle_waste = data.get('idle_resources', {}).get('total_monthly_waste', 0)
    total_cost = data.get('cost_data', {}).get('total_cost', 0)
    monthly_avg = total_cost / 6 if total_cost else 0
    rds_underutilized = data.get('rds_data', {}).get('underutilized_count', 0)
    lambda_rarely_used = data.get('lambda_data', {}).get('rarely_used_count', 0)
    
    # Calculate scores
    total_resources_count = (
        len(ec2_recs if ec2_recs else []) +
        data.get('s3_data', {}).get('total_buckets', 0) +
        data.get('rds_data', {}).get('total_instances', 0) +
        data.get('lambda_data', {}).get('total_functions', 0)
    )
    
    tagged_percentage = 50  # Placeholder
    if tagged_percentage >= 90:
        tag_score = 4
    elif tagged_percentage >= 70:
        tag_score = 3
    elif tagged_percentage >= 40:
        tag_score = 2
    else:
        tag_score = 1
    
    budget_alerts = data.get('budget_alerts', {})
    total_budget = budget_alerts.get('total_budget', 0)
    total_actual = budget_alerts.get('total_actual', 0)
    budget_utilization = (total_actual / total_budget * 100) if total_budget > 0 else 0
    
    if 80 <= budget_utilization <= 95:
        budget_score = 4
    elif 70 <= budget_utilization < 80 or 95 < budget_utilization <= 100:
        budget_score = 3
    elif 50 <= budget_utilization < 70 or 100 < budget_utilization <= 110:
        budget_score = 2
    else:
        budget_score = 1
    
    potential_monthly_savings = idle_waste
    if monthly_avg > 0:
        savings_percentage = (potential_monthly_savings / monthly_avg) * 100
    else:
        savings_percentage = 0
    
    if savings_percentage < 5:
        savings_score = 4
    elif savings_percentage < 15:
        savings_score = 3
    elif savings_percentage < 30:
        savings_score = 2
    else:
        savings_score = 1
    
    underutilized_count = rds_underutilized + lambda_rarely_used + idle_count
    if total_resources_count > 0:
        utilization_percentage = ((total_resources_count - underutilized_count) / total_resources_count) * 100
    else:
        utilization_percentage = 100
    
    if utilization_percentage >= 90:
        utilization_score = 4
    elif utilization_percentage >= 75:
        utilization_score = 3
    elif utilization_percentage >= 60:
        utilization_score = 2
    else:
        utilization_score = 1
    
    overall_maturity = (tag_score + budget_score + savings_score + utilization_score) / 4
    
    if overall_maturity >= 3.5:
        maturity_level = "Optimize / Innovate"
        maturity_description = "Continuous optimization, predictive analytics, business value tracking"
    elif overall_maturity >= 2.5:
        maturity_level = "Run"
        maturity_description = "Mature governance, fully automated, cost-efficient systems"
    elif overall_maturity >= 1.5:
        maturity_level = "Walk"
        maturity_description = "Defined processes, partial automation, beginning operational discipline"
    else:
        maturity_level = "Crawl"
        maturity_description = "Ad-hoc processes, limited visibility, reactive cost control"
    
    return {
        'overall_maturity': overall_maturity,
        'maturity_level': maturity_level,
        'maturity_description': maturity_description,
        'tag_score': tag_score,
        'budget_score': budget_score,
        'savings_score': savings_score,
        'utilization_score': utilization_score,
        'tagged_percentage': tagged_percentage,
        'budget_utilization': budget_utilization,
        'savings_percentage': savings_percentage,
        'utilization_percentage': utilization_percentage,
        'potential_monthly_savings': potential_monthly_savings,
        'total_resources_count': total_resources_count,
        'underutilized_count': underutilized_count,
        'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

def show_kpi():
    """FinOps Maturity Scoring Dashboard"""
    st.markdown("## 🎯 FinOps Maturity Scoring")
    
    if not st.session_state.analyzed:
        st.info("👈 Please run analysis in Settings first")
        return
    
    data = st.session_state.all_analysis_data
    
    # Get basic metrics for calculations
    rightsizing = data.get('rightsizing', {})
    ec2_recs = rightsizing.get('recommendations', [])
    if isinstance(ec2_recs, dict):
        ec2_recs = ec2_recs.get('RightsizingRecommendations', [])
    
    idle_count = data.get('idle_resources', {}).get('total_items', 0)
    idle_waste = data.get('idle_resources', {}).get('total_monthly_waste', 0)
    total_cost = data.get('cost_data', {}).get('total_cost', 0)
    monthly_avg = total_cost / 6 if total_cost else 0
    rds_underutilized = data.get('rds_data', {}).get('underutilized_count', 0)
    lambda_rarely_used = data.get('lambda_data', {}).get('rarely_used_count', 0)
    
    # Export buttons at the top
    st.markdown("### 📥 Export Maturity Report")
    
    export_col1, export_col2, export_col3 = st.columns(3)
    
    with export_col1:
        if st.button("📄 Export PDF", use_container_width=True):
            with st.spinner("Generating PDF report..."):
                try:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    pdf_path = f"finops_maturity_report_{timestamp}.pdf"
                    
                    # Generate maturity report data
                    maturity_data = generate_maturity_data(data)
                    
                    # Generate enhanced KPI PDF with charts and visualizations
                    cost_data_for_pdf = {
                        'total_cost': data.get('cost_data', {}).get('total_cost', 0)
                    }
                    
                    report_gen = ReportGenerator()
                    report_gen.generate_kpi_pdf(maturity_data, cost_data_for_pdf, pdf_path)
                    
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            "⬇️ Download PDF Report",
                            f,
                            file_name=pdf_path,
                            mime="application/pdf",
                            use_container_width=True
                        )
                    
                    st.success("✅ PDF report generated successfully!")
                    
                except Exception as e:
                    st.error(f"❌ Error generating PDF: {str(e)}")
    
    with export_col2:
        if st.button("📊 Export Excel", use_container_width=True):
            with st.spinner("Generating Excel report..."):
                try:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    excel_path = f"finops_maturity_report_{timestamp}.xlsx"
                    
                    # Generate maturity report data
                    maturity_data = generate_maturity_data(data)
                    
                    # Create Excel file using pandas
                    
                    # Create maturity summary
                    summary_data = {
                        'Metric': ['Overall Maturity Score', 'Maturity Level', 'Tagged Resources Score', 
                                  'Budget Utilization Score', 'Savings Optimization Score', 'Resource Utilization Score'],
                        'Value': [f"{maturity_data['overall_maturity']:.1f}/4.0", maturity_data['maturity_level'],
                                 f"{maturity_data['tag_score']}/4", f"{maturity_data['budget_score']}/4",
                                 f"{maturity_data['savings_score']}/4", f"{maturity_data['utilization_score']}/4"],
                        'Percentage': [f"{maturity_data['overall_maturity']/4*100:.1f}%", "N/A",
                                      f"{maturity_data['tagged_percentage']:.1f}%", f"{maturity_data['budget_utilization']:.1f}%",
                                      f"{maturity_data['savings_percentage']:.1f}%", f"{maturity_data['utilization_percentage']:.1f}%"]
                    }
                    
                    df_summary = pd.DataFrame(summary_data)
                    
                    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                        df_summary.to_excel(writer, sheet_name='Maturity Summary', index=False)
                        
                        # Add raw data sheet
                        raw_data = pd.DataFrame([maturity_data])
                        raw_data.to_excel(writer, sheet_name='Raw Data', index=False)
                    
                    with open(excel_path, "rb") as f:
                        st.download_button(
                            "⬇️ Download Excel Report",
                            f,
                            file_name=excel_path,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    
                    st.success("✅ Excel report generated successfully!")
                    
                except Exception as e:
                    st.error(f"❌ Error generating Excel: {str(e)}")
    
    with export_col3:
        if st.button("📝 Export Word", use_container_width=True):
            with st.spinner("Generating Word document..."):
                try:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    docx_path = f"finops_maturity_report_{timestamp}.docx"
                    
                    # Generate maturity report data
                    maturity_data = generate_maturity_data(data)
                    
                    # Create Word document using existing generator
                    mock_cost_data = {
                        'total_cost': data.get('cost_data', {}).get('total_cost', 0),
                        'monthly_average': data.get('cost_data', {}).get('total_cost', 0) / 6
                    }
                    mock_ri_data = {
                        'current_ris': [],
                        'recommendations': {'Recommendations': []}
                    }
                    
                    maturity_recommendations = [
                        {
                            'title': f'FinOps Maturity Assessment',
                            'description': f'Overall Maturity Level: {maturity_data["maturity_level"]} (Score: {maturity_data["overall_maturity"]:.1f}/4.0)',
                            'severity': 'High' if maturity_data["overall_maturity"] < 2.5 else 'Medium',
                            'estimated_savings': f'${maturity_data["potential_monthly_savings"]:,.2f}/month',
                            'category': 'FinOps Maturity'
                        }
                    ]
                    
                    report_gen = ReportGenerator()
                    report_gen.generate_docx(mock_cost_data, mock_ri_data, maturity_recommendations, docx_path)
                    
                    with open(docx_path, "rb") as f:
                        st.download_button(
                            "⬇️ Download Word Document",
                            f,
                            file_name=docx_path,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True
                        )
                    
                    st.success("✅ Word document generated successfully!")
                    
                except Exception as e:
                    st.error(f"❌ Error generating Word: {str(e)}")
    
    st.markdown("---")
    
    # Calculate maturity scores for different dimensions
    
    # 1. Tagged Resources Score (0-4)
    total_resources_count = (
        len(ec2_recs if ec2_recs else []) +
        data.get('s3_data', {}).get('total_buckets', 0) +
        data.get('rds_data', {}).get('total_instances', 0) +
        data.get('lambda_data', {}).get('total_functions', 0)
    )
    # Assume 50% are tagged (in real scenario, this would come from actual tag analysis)
    tagged_percentage = 50  # Placeholder
    if tagged_percentage >= 90:
        tag_score = 4
    elif tagged_percentage >= 70:
        tag_score = 3
    elif tagged_percentage >= 40:
        tag_score = 2
    else:
        tag_score = 1
    
    # 2. Budget Utilization Score (0-4)
    budget_alerts = data.get('budget_alerts', {})
    total_budget = budget_alerts.get('total_budget', 0)
    total_actual = budget_alerts.get('total_actual', 0)
    budget_utilization = (total_actual / total_budget * 100) if total_budget > 0 else 0
    
    if 80 <= budget_utilization <= 95:
        budget_score = 4  # Optimal range
    elif 70 <= budget_utilization < 80 or 95 < budget_utilization <= 100:
        budget_score = 3
    elif 50 <= budget_utilization < 70 or 100 < budget_utilization <= 110:
        budget_score = 2
    else:
        budget_score = 1
    
    # 3. Savings from Optimization Score (0-4)
    potential_monthly_savings = idle_waste
    if monthly_avg > 0:
        savings_percentage = (potential_monthly_savings / monthly_avg) * 100
    else:
        savings_percentage = 0
    
    if savings_percentage < 5:
        savings_score = 4  # Already optimized
    elif savings_percentage < 15:
        savings_score = 3
    elif savings_percentage < 30:
        savings_score = 2
    else:
        savings_score = 1  # High waste
    
    # 4. Resource Utilization Score (0-4)
    underutilized_count = rds_underutilized + lambda_rarely_used + idle_count
    if total_resources_count > 0:
        utilization_percentage = ((total_resources_count - underutilized_count) / total_resources_count) * 100
    else:
        utilization_percentage = 100
    
    if utilization_percentage >= 90:
        utilization_score = 4
    elif utilization_percentage >= 75:
        utilization_score = 3
    elif utilization_percentage >= 60:
        utilization_score = 2
    else:
        utilization_score = 1
    
    # Calculate overall maturity score
    overall_maturity = (tag_score + budget_score + savings_score + utilization_score) / 4
    
    # Determine maturity level
    if overall_maturity >= 3.5:
        maturity_level = "Optimize / Innovate"
        maturity_color = "green"
        maturity_description = "Continuous optimization, predictive analytics, business value tracking"
    elif overall_maturity >= 2.5:
        maturity_level = "Run"
        maturity_color = "blue"
        maturity_description = "Mature governance, fully automated, cost-efficient systems"
    elif overall_maturity >= 1.5:
        maturity_level = "Walk"
        maturity_color = "orange"
        maturity_description = "Defined processes, partial automation, beginning operational discipline"
    else:
        maturity_level = "Crawl"
        maturity_color = "red"
        maturity_description = "Ad-hoc processes, limited visibility, reactive cost control"
    

    
    # FinOps Maturity Visualization
    st.markdown("### 📊 FinOps Maturity Analysis")
    
    # Calculate scores first (moved up from below)
    # 1. Tagged Resources Score (0-4)
    total_resources_count = (
        len(ec2_recs if ec2_recs else []) +
        data.get('s3_data', {}).get('total_buckets', 0) +
        data.get('rds_data', {}).get('total_instances', 0) +
        data.get('lambda_data', {}).get('total_functions', 0)
    )
    # Assume 50% are tagged (in real scenario, this would come from actual tag analysis)
    tagged_percentage = 50  # Placeholder
    if tagged_percentage >= 90:
        tag_score = 4
    elif tagged_percentage >= 70:
        tag_score = 3
    elif tagged_percentage >= 40:
        tag_score = 2
    else:
        tag_score = 1
    
    # 2. Budget Utilization Score (0-4)
    budget_alerts = data.get('budget_alerts', {})
    total_budget = budget_alerts.get('total_budget', 0)
    total_actual = budget_alerts.get('total_actual', 0)
    budget_utilization = (total_actual / total_budget * 100) if total_budget > 0 else 0
    
    if 80 <= budget_utilization <= 95:
        budget_score = 4  # Optimal range
    elif 70 <= budget_utilization < 80 or 95 < budget_utilization <= 100:
        budget_score = 3
    elif 50 <= budget_utilization < 70 or 100 < budget_utilization <= 110:
        budget_score = 2
    else:
        budget_score = 1
    
    # 3. Savings from Optimization Score (0-4)
    potential_monthly_savings = idle_waste
    if monthly_avg > 0:
        savings_percentage = (potential_monthly_savings / monthly_avg) * 100
    else:
        savings_percentage = 0
    
    if savings_percentage < 5:
        savings_score = 4  # Already optimized
    elif savings_percentage < 15:
        savings_score = 3
    elif savings_percentage < 30:
        savings_score = 2
    else:
        savings_score = 1  # High waste
    
    # 4. Resource Utilization Score (0-4)
    underutilized_count = rds_underutilized + lambda_rarely_used + idle_count
    if total_resources_count > 0:
        utilization_percentage = ((total_resources_count - underutilized_count) / total_resources_count) * 100
    else:
        utilization_percentage = 100
    
    if utilization_percentage >= 90:
        utilization_score = 4
    elif utilization_percentage >= 75:
        utilization_score = 3
    elif utilization_percentage >= 60:
        utilization_score = 2
    else:
        utilization_score = 1
    
    # Calculate overall maturity score
    overall_maturity = (tag_score + budget_score + savings_score + utilization_score) / 4
    
    # Create visualizations
    viz_col1, viz_col2 = st.columns(2)
    
    with viz_col1:
        # Maturity Score Gauge Chart
        import plotly.graph_objects as go
        
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = overall_maturity,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Overall FinOps Maturity"},
            delta = {'reference': 2.5},
            gauge = {
                'axis': {'range': [None, 4]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 1], 'color': "lightgray"},
                    {'range': [1, 2], 'color': "orange"},
                    {'range': [2, 3], 'color': "yellow"},
                    {'range': [3, 4], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 3.5
                }
            }
        ))
        fig_gauge.update_layout(height=300)
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    with viz_col2:
        # Dimension Scores Radar Chart
        import plotly.graph_objects as go
        
        categories = ['Tagged Resources', 'Budget Utilization', 'Savings Optimization', 'Resource Utilization']
        scores = [tag_score, budget_score, savings_score, utilization_score]
        
        fig_radar = go.Figure()
        
        fig_radar.add_trace(go.Scatterpolar(
            r=scores,
            theta=categories,
            fill='toself',
            name='Current Score',
            line_color='rgb(0, 102, 204)'
        ))
        
        # Add ideal score line
        fig_radar.add_trace(go.Scatterpolar(
            r=[4, 4, 4, 4],
            theta=categories,
            fill='toself',
            name='Target Score',
            line_color='rgb(40, 167, 69)',
            opacity=0.3
        ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 4]
                )),
            showlegend=True,
            title="Maturity Dimensions",
            height=300
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)
    
    # Cost Analysis Charts
    st.markdown("### 💰 Cost Analysis Dashboard")
    
    cost_col1, cost_col2 = st.columns(2)
    
    with cost_col1:
        # Monthly Cost Trend (simulated data)
        import plotly.express as px
        
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        monthly_costs = [monthly_avg * 0.9, monthly_avg * 1.1, monthly_avg * 0.95, 
                        monthly_avg * 1.05, monthly_avg * 0.98, monthly_avg]
        
        fig_trend = px.line(
            x=months, 
            y=monthly_costs,
            title='6-Month Cost Trend',
            labels={'x': 'Month', 'y': 'Cost ($)'}
        )
        fig_trend.update_traces(line_color='rgb(0, 102, 204)', line_width=3)
        fig_trend.update_layout(height=300)
        st.plotly_chart(fig_trend, use_container_width=True)
    
    with cost_col2:
        # Savings Opportunity Breakdown
        savings_data = {
            'Category': ['Idle Resources', 'Rightsizing', 'Reserved Instances', 'Storage Optimization'],
            'Savings': [idle_waste * 0.4, idle_waste * 0.3, idle_waste * 0.2, idle_waste * 0.1]
        }
        
        fig_savings = px.pie(
            values=savings_data['Savings'],
            names=savings_data['Category'],
            title='Potential Monthly Savings Breakdown'
        )
        fig_savings.update_layout(height=300)
        st.plotly_chart(fig_savings, use_container_width=True)
    
    # Resource Utilization Analysis
    st.markdown("### 📈 Resource Utilization Analysis")
    
    util_col1, util_col2 = st.columns(2)
    
    with util_col1:
        # Resource Type Distribution
        resource_counts = {
            'EC2': len(ec2_recs) if ec2_recs else 0,
            'RDS': data.get('rds_data', {}).get('total_instances', 0),
            'Lambda': data.get('lambda_data', {}).get('total_functions', 0),
            'S3': data.get('s3_data', {}).get('total_buckets', 0)
        }
        
        # Filter out zero values
        resource_counts = {k: v for k, v in resource_counts.items() if v > 0}
        
        if resource_counts:
            fig_resources = px.bar(
                x=list(resource_counts.keys()),
                y=list(resource_counts.values()),
                title='Resource Count by Service',
                labels={'x': 'Service', 'y': 'Count'},
                color=list(resource_counts.values()),
                color_continuous_scale='Blues'
            )
            fig_resources.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig_resources, use_container_width=True)
        else:
            st.info("No resource data available for visualization")
    
    with util_col2:
        # Utilization vs Waste Comparison
        utilization_data = {
            'Status': ['Utilized', 'Underutilized', 'Idle'],
            'Count': [
                max(0, total_resources_count - underutilized_count - idle_count),
                underutilized_count,
                idle_count
            ],
            'Color': ['#28a745', '#ffc107', '#dc3545']
        }
        
        fig_util = px.bar(
            x=utilization_data['Status'],
            y=utilization_data['Count'],
            title='Resource Utilization Status',
            labels={'x': 'Status', 'y': 'Resource Count'},
            color=utilization_data['Status'],
            color_discrete_map={
                'Utilized': '#28a745',
                'Underutilized': '#ffc107', 
                'Idle': '#dc3545'
            }
        )
        fig_util.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig_util, use_container_width=True)
    
    st.markdown("---")
    
    # FinOps Maturity Scoring Model
    st.markdown("### 🎯 FinOps Maturity Scoring Model")
    
    # Determine maturity level
    if overall_maturity >= 3.5:
        maturity_level = "Optimize / Innovate"
        maturity_color = "green"
        maturity_description = "Continuous optimization, predictive analytics, business value tracking"
    elif overall_maturity >= 2.5:
        maturity_level = "Run"
        maturity_color = "blue"
        maturity_description = "Mature governance, fully automated, cost-efficient systems"
    elif overall_maturity >= 1.5:
        maturity_level = "Walk"
        maturity_color = "orange"
        maturity_description = "Defined processes, partial automation, beginning operational discipline"
    else:
        maturity_level = "Crawl"
        maturity_color = "red"
        maturity_description = "Ad-hoc processes, limited visibility, reactive cost control"
    
    # Display Maturity Model
    mat_col1, mat_col2 = st.columns([1, 2])
    
    with mat_col1:
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, #0066cc 0%, #003d7a 100%); 
                        padding: 30px; border-radius: 12px; text-align: center; color: white;'>
                <div style='font-size: 48px; font-weight: 800; margin-bottom: 10px;'>{overall_maturity:.1f}</div>
                <div style='font-size: 20px; font-weight: 600;'>{maturity_level}</div>
                <div style='font-size: 14px; margin-top: 10px; opacity: 0.9;'>Maturity Score</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if overall_maturity >= 3.5:
            st.success("🌟 Excellent! Leading FinOps practices")
        elif overall_maturity >= 2.5:
            st.info("👍 Good! Mature FinOps implementation")
        elif overall_maturity >= 1.5:
            st.warning("⚠️ Fair. Developing FinOps capabilities")
        else:
            st.error("🚨 Needs Improvement. Begin FinOps journey")
    
    with mat_col2:
        st.markdown(f"**Description:** {maturity_description}")
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Dimension scores
        st.markdown("#### 📊 Dimension Scores")
        
        dim_data = {
            'Dimension': ['Tagged Resources', 'Budget Utilization', 'Savings Optimization', 'Resource Utilization'],
            'Score': [tag_score, budget_score, savings_score, utilization_score],
            'Status': [
                f"{tagged_percentage:.0f}% tagged",
                f"{budget_utilization:.1f}% utilized",
                f"{savings_percentage:.1f}% potential savings",
                f"{utilization_percentage:.1f}% utilized"
            ]
        }
        
        dim_df = pd.DataFrame(dim_data)
        
        # Color code the scores
        def color_score(val):
            if val >= 3.5:
                return 'background-color: #d4edda'
            elif val >= 2.5:
                return 'background-color: #d1ecf1'
            elif val >= 1.5:
                return 'background-color: #fff3cd'
            else:
                return 'background-color: #f8d7da'
        
        styled_df = dim_df.style.applymap(color_score, subset=['Score'])
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Maturity Level Reference Table
    st.markdown("#### 📋 FinOps Maturity Levels")
    
    maturity_ref = pd.DataFrame({
        'Maturity Level': ['Crawl', 'Walk', 'Run', 'Optimize / Innovate'],
        'Score': ['1', '2', '3', '4'],
        'Description': [
            'Ad-hoc processes, limited visibility, reactive cost control',
            'Defined processes, partial automation, beginning operational discipline',
            'Mature governance, fully automated, cost-efficient systems',
            'Continuous optimization, predictive analytics, business value tracking'
        ]
    })
    
    st.dataframe(maturity_ref, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Account Scanner Report
    st.markdown("### 🔍 Account Scanner Report")
    
    scanner_col1, scanner_col2, scanner_col3, scanner_col4 = st.columns(4)
    
    with scanner_col1:
        st.markdown("""
            <div style='background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #0066cc;'>
                <div style='font-size: 14px; color: #6c757d; margin-bottom: 5px;'>Tagged Resources</div>
                <div style='font-size: 32px; font-weight: 700; color: #0066cc;'>{:.0f}%</div>
                <div style='font-size: 12px; color: #6c757d; margin-top: 5px;'>Score: {}/4</div>
            </div>
        """.format(tagged_percentage, tag_score), unsafe_allow_html=True)
        
        if tag_score < 3:
            st.caption("⚠️ Improve resource tagging")
        else:
            st.caption("✅ Good tagging coverage")
    
    with scanner_col2:
        st.markdown("""
            <div style='background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #28a745;'>
                <div style='font-size: 14px; color: #6c757d; margin-bottom: 5px;'>Budget Utilization</div>
                <div style='font-size: 32px; font-weight: 700; color: #28a745;'>{:.1f}%</div>
                <div style='font-size: 12px; color: #6c757d; margin-top: 5px;'>Score: {}/4</div>
            </div>
        """.format(budget_utilization, budget_score), unsafe_allow_html=True)
        
        if budget_score < 3:
            st.caption("⚠️ Review budget allocation")
        else:
            st.caption("✅ Optimal budget usage")
    
    with scanner_col3:
        st.markdown("""
            <div style='background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #ffc107;'>
                <div style='font-size: 14px; color: #6c757d; margin-bottom: 5px;'>Savings Opportunity</div>
                <div style='font-size: 32px; font-weight: 700; color: #ffc107;'>${:,.0f}</div>
                <div style='font-size: 12px; color: #6c757d; margin-top: 5px;'>Score: {}/4</div>
            </div>
        """.format(potential_monthly_savings, savings_score), unsafe_allow_html=True)
        
        if savings_score < 3:
            st.caption("⚠️ High optimization potential")
        else:
            st.caption("✅ Well optimized")
    
    with scanner_col4:
        st.markdown("""
            <div style='background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #17a2b8;'>
                <div style='font-size: 14px; color: #6c757d; margin-bottom: 5px;'>Resource Utilization</div>
                <div style='font-size: 32px; font-weight: 700; color: #17a2b8;'>{:.1f}%</div>
                <div style='font-size: 12px; color: #6c757d; margin-top: 5px;'>Score: {}/4</div>
            </div>
        """.format(utilization_percentage, utilization_score), unsafe_allow_html=True)
        
        if utilization_score < 3:
            st.caption("⚠️ Many underutilized resources")
        else:
            st.caption("✅ High utilization")
    
    
    st.markdown("---")
    
    st.markdown("""
        ### 📋 Report Contents
        
        **FinOps Maturity Assessment includes:**
        - **Overall Maturity Score**: Comprehensive 1-4 scale assessment
        - **Dimension Analysis**: Tagged Resources, Budget Utilization, Savings Optimization, Resource Utilization
        - **Maturity Level**: Crawl, Walk, Run, or Optimize/Innovate classification
        - **Account Scanner Results**: Detailed metrics and recommendations
        - **Implementation Roadmap**: Next steps for improving maturity
        - **Best Practices**: Industry-standard FinOps recommendations
        
        **Export Formats:**
        - **PDF**: Executive summary with visual charts and recommendations
        - **Excel**: Detailed data with pivot tables and analysis worksheets
        - **Word**: Editable document for customization and sharing
    """)

def show_savings():
    """Savings Plans page"""
    st.markdown("## 💰 Savings Plans & Reserved Capacity")
    
    if not st.session_state.analyzed:
        st.info("👈 Please run analysis in Settings first")
        return
    
    data = st.session_state.all_analysis_data
    
    # AI-Powered RI Recommendations Section
    st.markdown("### 🤖 AI-Powered Reserved Instance Recommendations")
    
    ri_data = data.get('ri_data', {})
    ri_recommendations = ri_data.get('recommendations', {}).get('Recommendations', [])
    current_ris = ri_data.get('current_ris', [])
    
    # Summary metrics
    ai_col1, ai_col2, ai_col3, ai_col4 = st.columns(4)
    
    with ai_col1:
        total_potential_savings = sum(float(rec.get('EstimatedMonthlySavingsAmount', 0)) for rec in ri_recommendations)
        st.metric("💡 AI Identified Savings", f"${total_potential_savings * 12:,.0f}/year", 
                 delta=f"${total_potential_savings:,.0f}/month")
    
    with ai_col2:
        st.metric("🎯 RI Opportunities", len(ri_recommendations))
    
    with ai_col3:
        active_ris = len(current_ris)
        st.metric("✅ Active RIs", active_ris)
    
    with ai_col4:
        if ri_recommendations:
            avg_savings_percent = sum(float(rec.get('EstimatedSavingsPercentage', 0)) for rec in ri_recommendations) / len(ri_recommendations)
            st.metric("📈 Avg Savings %", f"{avg_savings_percent:.1f}%")
        else:
            st.metric("📈 Avg Savings %", "0%")
    
    st.markdown("---")
    
    # AI Recommendations Details
    if ri_recommendations:
        st.markdown("### 🧠 Intelligent RI Purchase Recommendations")
        
        # Priority filter
        priority_filter = st.selectbox(
            "Filter by Priority:",
            ["All Recommendations", "High Savings (>$500/month)", "Medium Savings ($100-$500/month)", "Low Savings (<$100/month)"]
        )
        
        # Filter recommendations based on priority
        filtered_recs = ri_recommendations
        if priority_filter == "High Savings (>$500/month)":
            filtered_recs = [r for r in ri_recommendations if float(r.get('EstimatedMonthlySavingsAmount', 0)) > 500]
        elif priority_filter == "Medium Savings ($100-$500/month)":
            filtered_recs = [r for r in ri_recommendations if 100 <= float(r.get('EstimatedMonthlySavingsAmount', 0)) <= 500]
        elif priority_filter == "Low Savings (<$100/month)":
            filtered_recs = [r for r in ri_recommendations if float(r.get('EstimatedMonthlySavingsAmount', 0)) < 100]
        
        if not filtered_recs:
            st.info(f"No recommendations match the selected filter: {priority_filter}")
        else:
            for idx, rec in enumerate(filtered_recs, 1):
                # Extract recommendation details
                instance_family = rec.get('InstanceDetails', {}).get('EC2InstanceDetails', {}).get('Family', 'N/A')
                instance_type = rec.get('InstanceDetails', {}).get('EC2InstanceDetails', {}).get('InstanceType', 'N/A')
                region = rec.get('InstanceDetails', {}).get('EC2InstanceDetails', {}).get('Region', 'N/A')
                platform = rec.get('InstanceDetails', {}).get('EC2InstanceDetails', {}).get('Platform', 'N/A')
                
                monthly_savings = float(rec.get('EstimatedMonthlySavingsAmount', 0))
                savings_percentage = float(rec.get('EstimatedSavingsPercentage', 0))
                upfront_cost = float(rec.get('UpfrontCost', 0))
                monthly_cost = float(rec.get('RecurringStandardAmount', 0))
                
                # Determine priority color
                if monthly_savings > 500:
                    priority_color = "🔴"
                    priority_text = "High Priority"
                elif monthly_savings >= 100:
                    priority_color = "🟡"
                    priority_text = "Medium Priority"
                else:
                    priority_color = "🟢"
                    priority_text = "Low Priority"
                
                with st.expander(f"{priority_color} RI #{idx}: {instance_type} in {region} - ${monthly_savings:,.0f}/month savings", expanded=(idx <= 2)):
                    
                    # Key metrics row
                    rec_col1, rec_col2, rec_col3, rec_col4 = st.columns(4)
                    
                    with rec_col1:
                        st.metric("💰 Monthly Savings", f"${monthly_savings:,.2f}")
                    with rec_col2:
                        st.metric("📊 Savings %", f"{savings_percentage:.1f}%")
                    with rec_col3:
                        st.metric("💳 Upfront Cost", f"${upfront_cost:,.2f}")
                    with rec_col4:
                        st.metric("🔄 Monthly Cost", f"${monthly_cost:,.2f}")
                    
                    st.markdown("---")
                    
                    # AI Analysis
                    st.markdown("#### 🤖 AI Analysis & Recommendations")
                    
                    # ROI calculation
                    annual_savings = monthly_savings * 12
                    roi_months = upfront_cost / monthly_savings if monthly_savings > 0 else 0
                    
                    analysis_col1, analysis_col2 = st.columns(2)
                    
                    with analysis_col1:
                        st.markdown(f"""
                        **💡 Smart Insights:**
                        - **Instance Family:** {instance_family}
                        - **Platform:** {platform}
                        - **Priority Level:** {priority_text}
                        - **ROI Timeline:** {roi_months:.1f} months to break even
                        - **Annual Impact:** ${annual_savings:,.0f} savings per year
                        """)
                    
                    with analysis_col2:
                        # Recommendation strength indicator
                        if savings_percentage > 30:
                            strength = "🌟 Excellent"
                            strength_color = "green"
                        elif savings_percentage > 20:
                            strength = "👍 Good"
                            strength_color = "blue"
                        elif savings_percentage > 10:
                            strength = "👌 Fair"
                            strength_color = "orange"
                        else:
                            strength = "⚠️ Low Impact"
                            strength_color = "red"
                        
                        st.markdown(f"""
                        **📈 Recommendation Strength:** <span style='color: {strength_color}; font-weight: bold;'>{strength}</span>
                        
                        **🎯 Action Items:**
                        - Review usage patterns for {instance_type}
                        - Consider 1-year term for faster ROI
                        - Monitor utilization after purchase
                        - Set up billing alerts for tracking
                        """, unsafe_allow_html=True)
                    
                    # Payment options comparison
                    st.markdown("#### 💳 Payment Options Analysis")
                    
                    payment_col1, payment_col2, payment_col3 = st.columns(3)
                    
                    with payment_col1:
                        st.markdown("""
                        **🏃 No Upfront**
                        - Lower commitment
                        - Moderate savings
                        - Good for testing
                        """)
                    
                    with payment_col2:
                        st.markdown("""
                        **💰 Partial Upfront**
                        - Balanced approach
                        - Better savings
                        - Recommended option
                        """)
                    
                    with payment_col3:
                        st.markdown("""
                        **💎 All Upfront**
                        - Maximum savings
                        - Higher commitment
                        - Best for stable workloads
                        """)
    else:
        st.success("🎉 Excellent! No Reserved Instance recommendations found. Your current usage patterns are already optimized!")
        st.info("💡 This could mean you're already using RIs effectively or your workloads are variable and better suited for On-Demand pricing.")
    
    st.markdown("---")
    
    # RI Timeline Visualization
    st.markdown("### 📅 Reserved Instance Timeline & Management")
    
    if current_ris:
        st.markdown("#### 🕒 Active RI Timeline")
        
        # Create timeline visualization
        import plotly.graph_objects as go
        from datetime import datetime, timedelta
        import pandas as pd
        
        # Simulate RI timeline data (in real implementation, this would come from actual RI data)
        timeline_data = []
        colors = ['#0066cc', '#28a745', '#ffc107', '#dc3545', '#6f42c1']
        
        for idx, ri in enumerate(current_ris[:5]):  # Show up to 5 RIs
            # Simulate RI details (replace with actual data parsing)
            ri_id = ri.get('ReservedInstancesId', f'ri-{idx+1:03d}')
            instance_type = ri.get('InstanceType', f't3.medium')
            start_date = datetime.now() - timedelta(days=180)  # Simulate 6 months ago
            end_date = start_date + timedelta(days=365)  # 1 year term
            
            timeline_data.append({
                'RI_ID': ri_id,
                'Instance_Type': instance_type,
                'Start': start_date,
                'End': end_date,
                'Color': colors[idx % len(colors)],
                'Status': 'Active' if end_date > datetime.now() else 'Expired'
            })
        
        if timeline_data:
            # Create Gantt chart for RI timeline
            fig_timeline = go.Figure()
            
            for idx, ri in enumerate(timeline_data):
                fig_timeline.add_trace(go.Scatter(
                    x=[ri['Start'], ri['End']],
                    y=[idx, idx],
                    mode='lines+markers',
                    line=dict(color=ri['Color'], width=8),
                    marker=dict(size=10),
                    name=f"{ri['RI_ID']} ({ri['Instance_Type']})",
                    hovertemplate=f"<b>{ri['RI_ID']}</b><br>" +
                                f"Instance: {ri['Instance_Type']}<br>" +
                                f"Start: {ri['Start'].strftime('%Y-%m-%d')}<br>" +
                                f"End: {ri['End'].strftime('%Y-%m-%d')}<br>" +
                                f"Status: {ri['Status']}<extra></extra>"
                ))
            
            # Add current date line
            current_date = datetime.now()
            fig_timeline.add_vline(
                x=current_date,
                line_dash="dash",
                line_color="red",
                annotation_text="Today",
                annotation_position="top"
            )
            
            fig_timeline.update_layout(
                title="Reserved Instance Timeline",
                xaxis_title="Date",
                yaxis_title="Reserved Instances",
                yaxis=dict(
                    tickmode='array',
                    tickvals=list(range(len(timeline_data))),
                    ticktext=[f"{ri['RI_ID']}<br>({ri['Instance_Type']})" for ri in timeline_data]
                ),
                height=400,
                showlegend=True
            )
            
            st.plotly_chart(fig_timeline, use_container_width=True)
            
            # RI Status Summary
            st.markdown("#### 📊 RI Status Summary")
            
            status_col1, status_col2, status_col3 = st.columns(3)
            
            active_count = sum(1 for ri in timeline_data if ri['Status'] == 'Active')
            expired_count = len(timeline_data) - active_count
            
            with status_col1:
                st.metric("🟢 Active RIs", active_count)
            
            with status_col2:
                st.metric("🔴 Expired RIs", expired_count)
            
            with status_col3:
                # Calculate days until next expiration
                active_ris = [ri for ri in timeline_data if ri['Status'] == 'Active']
                if active_ris:
                    next_expiry = min(ri['End'] for ri in active_ris)
                    days_to_expiry = (next_expiry - datetime.now()).days
                    st.metric("⏰ Next Expiry", f"{days_to_expiry} days")
                else:
                    st.metric("⏰ Next Expiry", "N/A")
            
            # Renewal recommendations
            st.markdown("#### 🔄 Renewal Recommendations")
            
            renewal_recommendations = []
            for ri in timeline_data:
                if ri['Status'] == 'Active':
                    days_to_expiry = (ri['End'] - datetime.now()).days
                    if days_to_expiry <= 60:  # Expiring within 60 days
                        renewal_recommendations.append({
                            'RI_ID': ri['RI_ID'],
                            'Instance_Type': ri['Instance_Type'],
                            'Days_to_Expiry': days_to_expiry,
                            'Action': 'Renew Soon' if days_to_expiry <= 30 else 'Plan Renewal'
                        })
            
            if renewal_recommendations:
                st.warning("⚠️ **Action Required:** Some RIs are expiring soon!")
                
                renewal_df = pd.DataFrame(renewal_recommendations)
                st.dataframe(renewal_df, use_container_width=True, hide_index=True)
                
                st.markdown("""
                **💡 Renewal Tips:**
                - Review usage patterns before renewal
                - Consider newer instance types for better performance
                - Evaluate 3-year terms for maximum savings
                - Set calendar reminders 90 days before expiry
                """)
            else:
                st.success("✅ All RIs are well-managed with no immediate renewal actions needed.")
        
    else:
        st.info("📋 No active Reserved Instances found. Consider the AI recommendations above to start saving!")
        
        # Show potential timeline if RIs were purchased
        st.markdown("#### 🎯 Projected Savings Timeline")
        
        if ri_recommendations:
            # Create a projected savings chart
            months = list(range(1, 13))
            cumulative_savings = [sum(float(rec.get('EstimatedMonthlySavingsAmount', 0)) for rec in ri_recommendations) * month 
                                for month in months]
            
            fig_savings = go.Figure()
            fig_savings.add_trace(go.Scatter(
                x=months,
                y=cumulative_savings,
                mode='lines+markers',
                name='Cumulative Savings',
                line=dict(color='#28a745', width=3),
                marker=dict(size=8)
            ))
            
            fig_savings.update_layout(
                title="Projected Annual Savings if RIs are Purchased",
                xaxis_title="Month",
                yaxis_title="Cumulative Savings ($)",
                height=300
            )
            
            st.plotly_chart(fig_savings, use_container_width=True)
    
    st.markdown("---")
    
    # Savings Plans Section
    st.markdown("### 💎 Savings Plans Analysis")
    
    sp_data = data.get('savings_plans', {})
    
    sp_col1, sp_col2, sp_col3 = st.columns(3)
    
    with sp_col1:
        annual_sp_savings = sp_data.get('estimated_savings', 0)
        st.metric("💰 Annual SP Savings", f"${annual_sp_savings:,.0f}")
    
    with sp_col2:
        monthly_sp_savings = annual_sp_savings / 12 if annual_sp_savings else 0
        st.metric("📅 Monthly SP Savings", f"${monthly_sp_savings:,.0f}")
    
    with sp_col3:
        # Compare RI vs SP savings
        total_ri_annual = total_potential_savings * 12 if ri_recommendations else 0
        if total_ri_annual > 0 and annual_sp_savings > 0:
            better_option = "Savings Plans" if annual_sp_savings > total_ri_annual else "Reserved Instances"
            st.metric("🏆 Better Option", better_option)
        else:
            st.metric("🏆 Better Option", "Analyze Both")
    
    # Savings Plans vs RI comparison
    if annual_sp_savings > 0 or total_ri_annual > 0:
        st.markdown("#### ⚖️ Savings Plans vs Reserved Instances Comparison")
        
        comparison_data = {
            'Option': ['Reserved Instances', 'Savings Plans'],
            'Annual Savings': [total_ri_annual, annual_sp_savings],
            'Flexibility': ['Instance-specific', 'Compute-wide'],
            'Commitment': ['Instance type & region', 'Compute usage'],
            'Best For': ['Predictable workloads', 'Variable workloads']
        }
        
        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(comparison_df, use_container_width=True, hide_index=True)
        
        # Recommendation
        if total_ri_annual > annual_sp_savings:
            st.success("🎯 **Recommendation:** Focus on Reserved Instances for maximum savings with your current usage patterns.")
        elif annual_sp_savings > total_ri_annual:
            st.success("🎯 **Recommendation:** Savings Plans offer better value and flexibility for your workloads.")
        else:
            st.info("🎯 **Recommendation:** Consider a hybrid approach combining both RIs and Savings Plans.")
    
    else:
        st.info("💡 No specific savings plans data available. Run a fresh analysis to get current recommendations.")

def show_budget_manager():
    """Budget Management and Alerts page"""
    st.markdown("## 💳 Budget Manager & Alerts")
    
    # Initialize budget data in session state
    if 'budgets' not in st.session_state:
        st.session_state.budgets = []
    
    if 'budget_alerts' not in st.session_state:
        st.session_state.budget_alerts = []
    
    # Tabs for different budget functions
    budget_tab1, budget_tab2, budget_tab3, budget_tab4 = st.tabs([
        "📊 Budget Overview", 
        "➕ Create Budget", 
        "🚨 Alert Settings", 
        "📈 Budget Analytics"
    ])
    
    with budget_tab1:
        st.markdown("### 📊 Current Budgets Overview")
        
        if not st.session_state.budgets:
            st.info("📋 No budgets created yet. Use the 'Create Budget' tab to set up your first budget.")
            
            # Show sample budget template
            st.markdown("#### 💡 Budget Management Benefits")
            
            benefit_col1, benefit_col2, benefit_col3 = st.columns(3)
            
            with benefit_col1:
                st.markdown("""
                **🎯 Cost Control**
                - Set spending limits
                - Prevent cost overruns
                - Track budget utilization
                """)
            
            with benefit_col2:
                st.markdown("""
                **🚨 Proactive Alerts**
                - Real-time notifications
                - Threshold-based warnings
                - Email/SMS alerts
                """)
            
            with benefit_col3:
                st.markdown("""
                **📈 Financial Planning**
                - Forecast spending
                - Departmental allocation
                - ROI tracking
                """)
        
        else:
            # Display existing budgets
            for idx, budget in enumerate(st.session_state.budgets):
                with st.expander(f"💰 {budget['name']} - ${budget['amount']:,.2f}", expanded=True):
                    
                    # Budget metrics
                    budget_col1, budget_col2, budget_col3, budget_col4 = st.columns(4)
                    
                    with budget_col1:
                        st.metric("💵 Budget Amount", f"${budget['amount']:,.2f}")
                    
                    with budget_col2:
                        # Simulate current spend (in real implementation, this would come from AWS)
                        current_spend = budget['amount'] * 0.65  # 65% utilization
                        st.metric("💸 Current Spend", f"${current_spend:,.2f}")
                    
                    with budget_col3:
                        utilization = (current_spend / budget['amount']) * 100
                        st.metric("📊 Utilization", f"{utilization:.1f}%")
                    
                    with budget_col4:
                        remaining = budget['amount'] - current_spend
                        st.metric("💰 Remaining", f"${remaining:,.2f}")
                    
                    # Progress bar
                    progress_color = "green" if utilization < 80 else "orange" if utilization < 95 else "red"
                    st.progress(min(utilization / 100, 1.0))
                    
                    # Budget details
                    detail_col1, detail_col2 = st.columns(2)
                    
                    with detail_col1:
                        st.markdown(f"""
                        **📋 Budget Details:**
                        - **Period:** {budget['period']}
                        - **Department:** {budget.get('department', 'N/A')}
                        - **Services:** {', '.join(budget.get('services', ['All']))}
                        """)
                    
                    with detail_col2:
                        st.markdown(f"""
                        **🚨 Alert Settings:**
                        - **Threshold:** {budget.get('alert_threshold', 80)}%
                        - **Email:** {budget.get('alert_email', 'Not set')}
                        - **Status:** {'🟢 Active' if budget.get('alerts_enabled', True) else '🔴 Disabled'}
                        """)
                    
                    # Action buttons
                    action_col1, action_col2, action_col3 = st.columns(3)
                    
                    with action_col1:
                        if st.button(f"✏️ Edit", key=f"edit_{idx}"):
                            st.session_state[f'edit_budget_{idx}'] = True
                    
                    with action_col2:
                        if st.button(f"📊 Details", key=f"details_{idx}"):
                            st.session_state[f'show_details_{idx}'] = True
                    
                    with action_col3:
                        if st.button(f"🗑️ Delete", key=f"delete_{idx}"):
                            st.session_state.budgets.pop(idx)
                            st.rerun()
    
    with budget_tab2:
        st.markdown("### ➕ Create New Budget")
        
        with st.form("create_budget_form"):
            form_col1, form_col2 = st.columns(2)
            
            with form_col1:
                budget_name = st.text_input("💼 Budget Name", placeholder="e.g., Development Team Q1 2024")
                budget_amount = st.number_input("💵 Budget Amount ($)", min_value=0.0, step=100.0, value=1000.0)
                budget_period = st.selectbox("📅 Budget Period", [
                    "Monthly", "Quarterly", "Annually", "Custom"
                ])
                department = st.text_input("🏢 Department/Team", placeholder="e.g., Engineering, Marketing")
            
            with form_col2:
                # AWS Services selection
                aws_services = st.multiselect("☁️ AWS Services (Optional)", [
                    "EC2", "S3", "RDS", "Lambda", "ECS", "EKS", 
                    "CloudFront", "Route53", "VPC", "All Services"
                ], default=["All Services"])
                
                # Alert settings
                alert_threshold = st.slider("🚨 Alert Threshold (%)", 50, 100, 80)
                alert_email = st.text_input("📧 Alert Email", placeholder="admin@company.com")
                alerts_enabled = st.checkbox("🔔 Enable Alerts", value=True)
            
            # Advanced settings
            with st.expander("⚙️ Advanced Settings"):
                # Cost allocation tags
                cost_tags = st.text_area("🏷️ Cost Allocation Tags (Optional)", 
                                        placeholder="Environment:Production\nProject:WebApp\nOwner:TeamA")
                
                # Forecast settings
                enable_forecast = st.checkbox("📈 Enable Spend Forecasting", value=True)
                forecast_method = st.selectbox("📊 Forecast Method", [
                    "Linear Trend", "Seasonal", "Machine Learning"
                ]) if enable_forecast else None
            
            # Submit button
            submitted = st.form_submit_button("💾 Create Budget", use_container_width=True)
            
            if submitted:
                if budget_name and budget_amount > 0:
                    new_budget = {
                        'name': budget_name,
                        'amount': budget_amount,
                        'period': budget_period,
                        'department': department,
                        'services': aws_services,
                        'alert_threshold': alert_threshold,
                        'alert_email': alert_email,
                        'alerts_enabled': alerts_enabled,
                        'cost_tags': cost_tags,
                        'enable_forecast': enable_forecast,
                        'forecast_method': forecast_method,
                        'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    st.session_state.budgets.append(new_budget)
                    st.success(f"✅ Budget '{budget_name}' created successfully!")
                    st.rerun()
                else:
                    st.error("❌ Please provide a budget name and amount greater than 0")
    
    with budget_tab3:
        st.markdown("### 🚨 Alert Configuration")
        
        # Global alert settings
        st.markdown("#### 🌐 Global Alert Settings")
        
        global_col1, global_col2 = st.columns(2)
        
        with global_col1:
            # Default alert channels
            st.markdown("**📢 Default Alert Channels:**")
            email_alerts = st.checkbox("📧 Email Alerts", value=True)
            slack_alerts = st.checkbox("💬 Slack Notifications", value=False)
            sms_alerts = st.checkbox("📱 SMS Alerts", value=False)
            
            if email_alerts:
                default_email = st.text_input("📧 Default Email", placeholder="alerts@company.com")
            
            if slack_alerts:
                slack_webhook = st.text_input("🔗 Slack Webhook URL", placeholder="https://hooks.slack.com/...")
            
            if sms_alerts:
                sms_number = st.text_input("📱 SMS Number", placeholder="+1234567890")
        
        with global_col2:
            # Alert frequency and timing
            st.markdown("**⏰ Alert Timing:**")
            alert_frequency = st.selectbox("🔄 Alert Frequency", [
                "Real-time", "Hourly", "Daily", "Weekly"
            ])
            
            quiet_hours = st.checkbox("🌙 Quiet Hours (No alerts 10PM - 6AM)", value=True)
            weekend_alerts = st.checkbox("📅 Weekend Alerts", value=False)
            
            # Alert severity levels
            st.markdown("**⚠️ Alert Severity Levels:**")
            warning_threshold = st.slider("⚠️ Warning Level (%)", 50, 90, 75)
            critical_threshold = st.slider("🚨 Critical Level (%)", 80, 100, 90)
        
        st.markdown("---")
        
        # Custom alert rules
        st.markdown("#### 🎯 Custom Alert Rules")
        
        with st.expander("➕ Create Custom Alert Rule"):
            rule_col1, rule_col2 = st.columns(2)
            
            with rule_col1:
                rule_name = st.text_input("📝 Rule Name", placeholder="High EC2 Spend Alert")
                rule_condition = st.selectbox("📊 Condition", [
                    "Spend exceeds threshold", 
                    "Spend increases by %", 
                    "Anomaly detected",
                    "Service cost spike"
                ])
                rule_value = st.number_input("💯 Threshold Value", min_value=0.0, step=10.0)
            
            with rule_col2:
                rule_services = st.multiselect("☁️ Apply to Services", [
                    "EC2", "S3", "RDS", "Lambda", "All"
                ])
                rule_action = st.selectbox("🎬 Action", [
                    "Send Email", "Send Slack Message", "Create Ticket", "All"
                ])
                rule_enabled = st.checkbox("✅ Enable Rule", value=True)
            
            if st.button("💾 Save Alert Rule"):
                st.success("✅ Custom alert rule saved!")
        
        # Existing alert rules
        st.markdown("#### 📋 Active Alert Rules")
        
        sample_rules = [
            {"name": "Budget Threshold Alert", "condition": "80% of budget", "status": "🟢 Active"},
            {"name": "EC2 Cost Spike", "condition": "50% increase in 24h", "status": "🟢 Active"},
            {"name": "Unused Resources", "condition": "Idle for 7 days", "status": "🟡 Warning"}
        ]
        
        for rule in sample_rules:
            rule_container = st.container()
            with rule_container:
                rule_display_col1, rule_display_col2, rule_display_col3 = st.columns([3, 2, 1])
                
                with rule_display_col1:
                    st.write(f"**{rule['name']}**")
                    st.caption(rule['condition'])
                
                with rule_display_col2:
                    st.write(rule['status'])
                
                with rule_display_col3:
                    st.button("⚙️", key=f"config_{rule['name']}")
    
    with budget_tab4:
        st.markdown("### 📈 Budget Analytics & Insights")
        
        if st.session_state.budgets:
            # Budget performance analytics
            analytics_col1, analytics_col2 = st.columns(2)
            
            with analytics_col1:
                # Budget utilization chart
                import plotly.graph_objects as go
                
                budget_names = [b['name'] for b in st.session_state.budgets]
                utilizations = [65, 78, 45, 92]  # Simulated data
                
                fig_util = go.Figure(data=[
                    go.Bar(x=budget_names, y=utilizations, 
                          marker_color=['green' if u < 80 else 'orange' if u < 95 else 'red' for u in utilizations])
                ])
                fig_util.update_layout(
                    title="Budget Utilization by Department",
                    yaxis_title="Utilization (%)",
                    height=300
                )
                st.plotly_chart(fig_util, use_container_width=True)
            
            with analytics_col2:
                # Spending trend
                months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
                spending = [8500, 9200, 8800, 10500, 9800, 11200]
                
                fig_trend = go.Figure()
                fig_trend.add_trace(go.Scatter(
                    x=months, y=spending,
                    mode='lines+markers',
                    name='Actual Spend',
                    line=dict(color='blue', width=3)
                ))
                
                # Add budget line
                avg_budget = sum(b['amount'] for b in st.session_state.budgets) / len(st.session_state.budgets)
                fig_trend.add_hline(y=avg_budget, line_dash="dash", line_color="red", 
                                   annotation_text="Average Budget")
                
                fig_trend.update_layout(
                    title="Monthly Spending Trend",
                    yaxis_title="Spend ($)",
                    height=300
                )
                st.plotly_chart(fig_trend, use_container_width=True)
            
            # Budget insights
            st.markdown("#### 💡 Budget Insights & Recommendations")
            
            insight_col1, insight_col2, insight_col3 = st.columns(3)
            
            with insight_col1:
                st.markdown("""
                **🎯 Performance Summary**
                - 3 budgets on track
                - 1 budget at risk
                - Average utilization: 70%
                """)
            
            with insight_col2:
                st.markdown("""
                **🚨 Alert Summary**
                - 2 active alerts
                - 5 warnings this month
                - 0 critical breaches
                """)
            
            with insight_col3:
                st.markdown("""
                **📈 Forecast**
                - Projected overspend: $2,400
                - Recommended actions: 3
                - Savings opportunity: $1,800
                """)
            
            # Detailed recommendations
            st.markdown("#### 🎯 AI-Powered Budget Recommendations")
            
            recommendations = [
                {
                    "title": "Optimize Development Environment",
                    "description": "Development team budget is 92% utilized. Consider rightsizing EC2 instances.",
                    "impact": "Potential savings: $800/month",
                    "priority": "High"
                },
                {
                    "title": "Set Up Reserved Instance Budget",
                    "description": "Create separate budget for RI purchases to better track commitment savings.",
                    "impact": "Improved cost visibility",
                    "priority": "Medium"
                },
                {
                    "title": "Enable Automated Scaling Alerts",
                    "description": "Set up alerts for auto-scaling events that might impact budget.",
                    "impact": "Prevent unexpected costs",
                    "priority": "Medium"
                }
            ]
            
            for idx, rec in enumerate(recommendations):
                priority_color = "🔴" if rec['priority'] == 'High' else "🟡" if rec['priority'] == 'Medium' else "🟢"
                
                with st.expander(f"{priority_color} {rec['title']}", expanded=(idx == 0)):
                    st.markdown(f"**Description:** {rec['description']}")
                    st.markdown(f"**Impact:** {rec['impact']}")
                    st.markdown(f"**Priority:** {rec['priority']}")
                    
                    if st.button(f"✅ Implement", key=f"implement_{idx}"):
                        st.success(f"✅ Recommendation '{rec['title']}' marked for implementation!")
        
        else:
            st.info("📊 Create budgets first to see analytics and insights.")
            
            # Show sample analytics
            st.markdown("#### 📈 Sample Budget Analytics")
            st.image("https://via.placeholder.com/800x400/0066cc/ffffff?text=Budget+Analytics+Dashboard", 
                    caption="Sample budget analytics dashboard")

def show_analytics():
    """Analytics page"""
    st.markdown("## 📈 Advanced Analytics")
    
    if not st.session_state.analyzed:
        st.info("👈 Please run analysis in Settings first")
        return
    
    data = st.session_state.all_analysis_data
    
    # Rightsizing
    st.markdown("### 💻 EC2 Rightsizing")
    rs = data.get('rightsizing', {})
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Recommendations", len(rs.get('recommendations', [])))
    with col2:
        st.metric("Annual Savings", f"${rs.get('total_annual_savings', 0):,.2f}")
    
    st.markdown("---")
    
    # Display detailed recommendations
    recommendations = rs.get('recommendations', [])
    
    if not recommendations:
        st.info("✅ No rightsizing recommendations found. Your EC2 instances are optimally sized!")
    else:
        st.markdown("#### 📋 Detailed Rightsizing Recommendations")
        
        for idx, rec in enumerate(recommendations, 1):
            # Extract recommendation details
            instance_id = rec.get('CurrentInstance', {}).get('ResourceId', 'N/A')
            current_type = rec.get('CurrentInstance', {}).get('InstanceType', 'N/A')
            
            # Get modification details
            modify_rec = rec.get('ModifyRecommendationDetail', {})
            target_instances = modify_rec.get('TargetInstances', [])
            
            # Calculate savings
            estimated_monthly_savings = float(rec.get('EstimatedMonthlySavings', 0))
            estimated_savings_percentage = float(rec.get('EstimatedSavingsPercentage', 0))
            
            with st.expander(f"🔧 {idx}. Instance: {instance_id} ({current_type})", expanded=(idx <= 3)):
                # Metrics row
                met_col1, met_col2, met_col3 = st.columns(3)
                
                with met_col1:
                    st.metric("Current Type", current_type)
                with met_col2:
                    st.metric("Monthly Savings", f"${estimated_monthly_savings:.2f}")
                with met_col3:
                    st.metric("Savings %", f"{estimated_savings_percentage:.1f}%")
                
                st.markdown("---")
                
                # Recommended instance types
                if target_instances:
                    st.markdown("**🎯 Recommended Instance Types:**")
                    
                    for target in target_instances:
                        target_type = target.get('InstanceType', 'N/A')
                        expected_utilization = target.get('ExpectedResourceUtilization', {})
                        
                        # Create a nice card for each recommendation
                        st.markdown(f"""
                            <div style='background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #0066cc;'>
                                <h4 style='margin: 0 0 10px 0; color: #0066cc;'>➡️ {target_type}</h4>
                        """, unsafe_allow_html=True)
                        
                        # CPU and Memory utilization
                        cpu_util = expected_utilization.get('EbsResourceUtilization', {})
                        max_cpu = cpu_util.get('EbsReadOpsPerSecond', {}).get('Maximum', 'N/A')
                        
                        col_a, col_b = st.columns(2)
                        
                        with col_a:
                            if max_cpu != 'N/A':
                                st.write(f"**Expected Max CPU:** {max_cpu}%")
                            else:
                                st.write("**Expected Max CPU:** Data not available")
                        
                        with col_b:
                            # Platform differences
                            platform_diffs = target.get('PlatformDifferences', [])
                            if platform_diffs:
                                st.write(f"**Platform Changes:** {', '.join(platform_diffs)}")
                            else:
                                st.write("**Platform Changes:** None")
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.warning("No specific target instance recommendations available")
                
                # Finding reason
                finding = rec.get('Finding', 'N/A')
                finding_reason = rec.get('FindingReasonCodes', [])
                
                st.markdown("**📊 Analysis:**")
                st.info(f"**Finding:** {finding}")
                
                if finding_reason:
                    st.write("**Reasons:**")
                    for reason in finding_reason:
                        st.write(f"- {reason}")
                
                # Current resource details
                current_instance = rec.get('CurrentInstance', {})
                resource_details = current_instance.get('ResourceDetails', {})
                
                if resource_details:
                    st.markdown("**💾 Current Resource Details:**")
                    ec2_details = resource_details.get('EC2ResourceDetails', {})
                    
                    detail_col1, detail_col2, detail_col3 = st.columns(3)
                    
                    with detail_col1:
                        st.write(f"**Platform:** {ec2_details.get('Platform', 'N/A')}")
                    with detail_col2:
                        st.write(f"**Region:** {ec2_details.get('Region', 'N/A')}")
                    with detail_col3:
                        st.write(f"**vCPUs:** {ec2_details.get('Vcpu', 'N/A')}")
    
    st.markdown("---")
    
    # Additional analytics sections
    st.markdown("### 📊 Cost Trends & Forecasting")
    st.info("💡 Cost trend analysis and forecasting features coming soon!")

def show_reports():
    """Reports page"""
    st.markdown("## 📄 Generate & Download Reports")
    
    if not st.session_state.analyzed:
        st.info("👈 Please run analysis in Settings first")
        return
    
    data = st.session_state.all_analysis_data
    
    # Report summary
    st.markdown("### 📊 Report Summary")
    
    sum_col1, sum_col2, sum_col3, sum_col4 = st.columns(4)
    
    with sum_col1:
        st.metric("Total Recommendations", len(data.get('recommendations', [])))
    
    with sum_col2:
        critical_count = sum(1 for r in data.get('recommendations', []) if r.get('severity') == 'Critical')
        st.metric("Critical Items", critical_count)
    
    with sum_col3:
        idle_waste = data.get('idle_resources', {}).get('total_monthly_waste', 0)
        st.metric("Monthly Savings", f"${idle_waste:,.0f}")
    
    with sum_col4:
        st.metric("Analysis Date", datetime.now().strftime("%Y-%m-%d"))
    
    st.markdown("---")
    
    st.markdown("### 📥 Export Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Generate PDF", use_container_width=True):
            with st.spinner("Generating PDF report..."):
                try:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    pdf_path = f"bct_finops_report_{timestamp}.pdf"
                    
                    report_gen = ReportGenerator()
                    report_gen.generate_pdf(
                        data.get('cost_data', {}),
                        data.get('ri_data', {}),
                        data.get('recommendations', []),
                        pdf_path
                    )
                    
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            "⬇️ Download PDF Report",
                            f,
                            file_name=pdf_path,
                            mime="application/pdf",
                            use_container_width=True
                        )
                    
                    st.success("✅ PDF report generated successfully!")
                    
                except Exception as e:
                    st.error(f"❌ Error generating PDF: {str(e)}")
    
    with col2:
        if st.button("📥 Generate Excel", use_container_width=True):
            with st.spinner("Generating Excel report..."):
                try:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    excel_path = f"bct_finops_report_{timestamp}.xlsx"
                    
                    export_mgr = ExportManager()
                    export_mgr.export_to_excel(
                        data.get('cost_data', {}),
                        data.get('recommendations', []),
                        data.get('idle_resources', {}),
                        data.get('s3_data', {}),
                        data.get('rds_data', {}),
                        excel_path
                    )
                    
                    with open(excel_path, "rb") as f:
                        st.download_button(
                            "⬇️ Download Excel Report",
                            f,
                            file_name=excel_path,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    
                    st.success("✅ Excel report generated successfully!")
                    
                except Exception as e:
                    st.error(f"❌ Error generating Excel: {str(e)}")
    
    with col3:
        if st.button("📥 Generate DOCX", use_container_width=True):
            with st.spinner("Generating Word document..."):
                try:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    docx_path = f"bct_finops_report_{timestamp}.docx"
                    
                    report_gen = ReportGenerator()
                    report_gen.generate_docx(
                        data.get('cost_data', {}),
                        data.get('ri_data', {}),
                        data.get('recommendations', []),
                        docx_path
                    )
                    
                    with open(docx_path, "rb") as f:
                        st.download_button(
                            "⬇️ Download Word Document",
                            f,
                            file_name=docx_path,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True
                        )
                    
                    st.success("✅ Word document generated successfully!")
                    
                except Exception as e:
                    st.error(f"❌ Error generating DOCX: {str(e)}")
    
    st.markdown("---")
    
    st.markdown("""
        ### 📋 Report Contents
        
        All reports include:
        - **Executive Summary**: Key metrics and cost overview
        - **Cost Analysis**: 6-month historical data and trends
        - **Recommendations**: Detailed optimization suggestions with priority scores
        - **Resource Inventory**: EC2, S3, RDS, Lambda, and more
        - **Idle Resources**: Immediate savings opportunities
        - **Implementation Roadmap**: Prioritized action plan
        
        **Report Formats:**
        - **PDF**: Professional formatted report for presentations
        - **Excel**: Multi-sheet workbook with pivot tables for analysis
        - **DOCX**: Editable Word document for customization
    """)

def show_aws_configuration():
    """AWS Configuration page with unified home page header"""
    
    # Custom CSS for unified home page design
    st.markdown("""
        <style>
        .home-header {
            background: linear-gradient(135deg, #0066cc 0%, #003d7a 100%);
            padding: 60px 40px;
            text-align: center;
            color: white;
            border-radius: 16px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0, 102, 204, 0.3);
        }
        
        .home-title {
            font-size: 56px;
            font-weight: 900;
            letter-spacing: 4px;
            margin: 0 0 15px 0;
            color: white;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
        }
        
        .home-subtitle {
            font-size: 20px;
            color: #e9ecef;
            margin: 0 0 10px 0;
            font-weight: 400;
        }
        
        .home-status {
            font-size: 14px;
            color: #ffc107;
            margin: 10px 0 0 0;
        }
        
        .home-status.success {
            color: #28a745;
        }
        
        .login-container {
            max-width: 900px;
            margin: -50px auto 0 auto;
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            position: relative;
            z-index: 10;
            transform: translateY(-20px);
        }
        
        .info-section {
            background: #f8f9fa;
            border-left: 4px solid #0066cc;
            padding: 15px;
            margin: 20px 0;
            border-radius: 6px;
        }
        
        .info-section h4 {
            margin: 0 0 10px 0;
            color: #0066cc;
            font-size: 16px;
        }
        
        .info-section ul {
            margin: 0;
            padding-left: 20px;
        }
        
        .info-section li {
            margin: 5px 0;
            color: #495057;
            font-size: 14px;
        }
        
        .feature-slider {
            display: flex;
            gap: 20px;
            margin: 15px 0 0 0;
            padding: 0 10px 0 10px;
            overflow-x: auto;
            scroll-behavior: smooth;
            position: relative;
            z-index: 5;
        }
        
        .feature-card {
            min-width: 200px;
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            padding: 25px 20px;
            border-radius: 15px;
            text-align: center;
            border: 1px solid #e9ecef;
            box-shadow: 0 4px 15px rgba(0, 102, 204, 0.1);
            transition: all 0.3s ease;
            cursor: pointer;
            animation: slideInUp 0.6s ease-out;
        }
        
        .feature-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 8px 25px rgba(0, 102, 204, 0.2);
            border-color: #0066cc;
        }
        
        .feature-card-icon {
            font-size: 48px;
            margin-bottom: 15px;
            transition: transform 0.3s ease;
        }
        
        .feature-card:hover .feature-card-icon {
            transform: scale(1.1);
        }
        
        .feature-card-title {
            font-size: 16px;
            font-weight: 700;
            color: #212529;
            margin-bottom: 8px;
        }
        
        .feature-card-desc {
            font-size: 12px;
            color: #6c757d;
            line-height: 1.4;
        }
        
        @keyframes slideInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .feature-card:nth-child(1) { animation-delay: 0.1s; }
        .feature-card:nth-child(2) { animation-delay: 0.2s; }
        .feature-card:nth-child(3) { animation-delay: 0.3s; }
        .feature-card:nth-child(4) { animation-delay: 0.4s; }
        
        /* Aggressive Streamlit spacing removal */
        .main .block-container {
            padding: 0 !important;
            max-width: 100% !important;
        }
        
        /* Remove ALL default margins and padding */
        .element-container,
        .stMarkdown,
        div[data-testid="stMarkdownContainer"],
        .row-widget,
        .stTabs,
        div[data-baseweb="tab-list"],
        div[data-baseweb="tab-panel"] {
            margin: 0 !important;
            padding: 0 !important;
        }
        
        /* Force zero spacing on all containers */
        .main > div {
            margin: 0 !important;
            padding: 0 !important;
        }
        
        /* Remove space from tabs specifically */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0;
            margin-top: 0 !important;
        }
        
        /* Hide any empty divs that might create space */
        div:empty {
            display: none !important;
        }
        
        /* Target the specific container that might be causing space */
        .main .block-container > div:first-child {
            margin-top: 0 !important;
        }
        
        /* Remove any potential spacing from the app container */
        .appview-container .main .block-container {
            padding-top: 0 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Unified Home Page Header
    if st.session_state.analyzed:
        data = st.session_state.all_analysis_data
        st.markdown(f"""
            <div class='home-header'>
                <div class='home-title'>BCT FINOPS TOOL</div>
                <div class='home-subtitle'>Enterprise Cloud Financial Operations Platform</div>
                <div class='home-status success'>✅ Logged in as: {st.session_state.username} | ✅ Analysis Complete</div>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🔄 Re-analyze Account", use_container_width=True, type="primary"):
                st.session_state.analyzed = False
                st.rerun()
            
            st.success(f"**Last analyzed:** {data.get('analyzed_at', 'N/A')}")
        
        return
    
    # Show home page with login form
    st.markdown(f"""
        <div class='home-header'>
            <div class='home-title'>BCT FINOPS TOOL</div>
            <div class='home-subtitle'>Enterprise Cloud Financial Operations Platform</div>
            <div class='home-status'>🔐 Logged in as: {st.session_state.username} | ⚠️ No AWS Account Connected</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Feature highlights - Sliding Cards with Login Container
    st.markdown("""
        <div class='feature-slider'>
            <div class='feature-card'>
                <div class='feature-card-icon'>💰</div>
                <div class='feature-card-title'>Cost Analysis</div>
                <div class='feature-card-desc'>Comprehensive 6-month cost analysis with forecasting</div>
            </div>
            <div class='feature-card'>
                <div class='feature-card-icon'>🤖</div>
                <div class='feature-card-title'>AI Recommendations</div>
                <div class='feature-card-desc'>Intelligent optimization suggestions with priority scoring</div>
            </div>
            <div class='feature-card'>
                <div class='feature-card-icon'>📊</div>
                <div class='feature-card-title'>Resource Insights</div>
                <div class='feature-card-desc'>Multi-service analysis across EC2, S3, RDS, Lambda & more</div>
            </div>
            <div class='feature-card'>
                <div class='feature-card-icon'>📄</div>
                <div class='feature-card-title'>Export Reports</div>
                <div class='feature-card-desc'>Professional PDF, Excel & Word reports with BCT branding</div>
            </div>
        </div>
        <div class='login-container'>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 AWS Credentials", "👤 User Profile"])
    
    with tab1:
        st.markdown("### 🔑 Connect Your AWS Account")
        
        # Information section
        st.markdown("""
            <div class='info-section'>
                <h4>🚀 What You'll Get:</h4>
                <ul>
                    <li>Comprehensive cost analysis across all AWS services</li>
                    <li>AI-powered optimization recommendations</li>
                    <li>Idle resource detection and savings opportunities</li>
                    <li>Multi-region resource visibility</li>
                    <li>Professional PDF, Excel, and Word reports</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        
        # Authentication method selector
        auth_method = st.radio(
            "Authentication Method",
            ["Access Keys", "IAM Role ARN", "Multi-Account (Organizations)", "Cross-Account Role"],
            help="Choose how to authenticate with AWS"
        )
        
        # Account scope selector
        account_scope = st.selectbox(
            "Analysis Scope",
            ["Single Account", "Multiple Accounts", "AWS Organizations (All Accounts)"],
            help="Choose the scope of your analysis"
        )
        
        with st.form("aws_config_form"):
            # Common fields
            aws_access_key = None
            aws_secret_key = None
            role_arn = None
            org_master_account = None
            account_list = None
            
            if auth_method == "Access Keys":
                st.info("💡 Use your AWS Access Key ID and Secret Access Key")
                aws_access_key = st.text_input(
                    "AWS Access Key ID",
                    placeholder="Enter your access key",
                    type="password",
                    help="Your AWS Access Key ID"
                )
                aws_secret_key = st.text_input(
                    "AWS Secret Access Key",
                    placeholder="Enter your secret key",
                    type="password",
                    help="Your AWS Secret Access Key"
                )
                
            elif auth_method == "IAM Role ARN":
                st.info("💡 Assume an IAM role for cross-account access")
                aws_access_key = st.text_input(
                    "AWS Access Key ID",
                    placeholder="Enter your access key",
                    type="password",
                    help="Base credentials to assume the role"
                )
                aws_secret_key = st.text_input(
                    "AWS Secret Access Key",
                    placeholder="Enter your secret key",
                    type="password",
                    help="Base credentials to assume the role"
                )
                role_arn = st.text_input(
                    "IAM Role ARN",
                    placeholder="arn:aws:iam::123456789012:role/FinOpsRole",
                    help="ARN of the IAM role to assume"
                )
                
            elif auth_method == "Multi-Account (Organizations)":
                st.info("💡 Analyze multiple accounts using AWS Organizations")
                aws_access_key = st.text_input(
                    "Master Account Access Key ID",
                    placeholder="Enter master account access key",
                    type="password",
                    help="Access Key for the Organizations master account"
                )
                aws_secret_key = st.text_input(
                    "Master Account Secret Access Key",
                    placeholder="Enter master account secret key",
                    type="password",
                    help="Secret Key for the Organizations master account"
                )
                org_master_account = st.text_input(
                    "Organizations Master Account ID",
                    placeholder="123456789012",
                    help="12-digit AWS Account ID of the Organizations master account"
                )
                role_arn = st.text_input(
                    "Cross-Account Role ARN Template",
                    placeholder="arn:aws:iam::{account_id}:role/OrganizationAccountAccessRole",
                    help="Role ARN template for accessing member accounts (use {account_id} placeholder)"
                )
                
            else:  # Cross-Account Role
                st.info("💡 Access multiple specific accounts using cross-account roles")
                aws_access_key = st.text_input(
                    "AWS Access Key ID",
                    placeholder="Enter your access key",
                    type="password",
                    help="Base credentials for assuming roles"
                )
                aws_secret_key = st.text_input(
                    "AWS Secret Access Key",
                    placeholder="Enter your secret key",
                    type="password",
                    help="Base credentials for assuming roles"
                )
                account_list = st.text_area(
                    "Account IDs and Role ARNs",
                    placeholder="123456789012:arn:aws:iam::123456789012:role/FinOpsRole\n234567890123:arn:aws:iam::234567890123:role/FinOpsRole",
                    help="Enter one account per line in format: AccountID:RoleARN"
                )
            
            # Multi-account specific options
            if account_scope in ["Multiple Accounts", "AWS Organizations (All Accounts)"]:
                st.markdown("---")
                st.markdown("#### 🏢 Multi-Account Options")
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    consolidate_reports = st.checkbox(
                        "Consolidate Reports",
                        value=True,
                        help="Combine all accounts into a single report"
                    )
                
                with col_b:
                    parallel_analysis = st.checkbox(
                        "Parallel Analysis",
                        value=True,
                        help="Analyze accounts in parallel for faster processing"
                    )
                
                max_accounts = st.number_input(
                    "Maximum Accounts to Analyze",
                    min_value=1,
                    max_value=100,
                    value=10,
                    help="Limit the number of accounts to analyze (for performance)"
                )
            
            aws_region = st.selectbox(
                "AWS Region",
                ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1", "ap-south-1", "ap-northeast-1"],
                help="Primary AWS region for analysis"
            )
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                analyze_button = st.form_submit_button("🚀 Sign In & Analyze", use_container_width=True, type="primary")
            
            with col2:
                test_button = st.form_submit_button("🧪 Test Connection", use_container_width=True)
        
        if test_button:
            if aws_access_key and aws_secret_key:
                with st.spinner("Testing AWS connection..."):
                    try:
                        analyzer = EnhancedAWSAnalyzer(
                            aws_access_key, aws_secret_key, aws_region,
                            role_arn=role_arn if auth_method == "IAM Role ARN" else None
                        )
                        
                        identity = analyzer.sts_client.get_caller_identity()
                        st.success(f"""
                            ✅ **Connection Successful!**
                            
                            - Account: {identity['Account']}
                            - User ARN: {identity['Arn']}
                            - Region: {aws_region}
                        """)
                    except Exception as e:
                        st.error(f"❌ Connection failed: {str(e)}")
                        
                        if "UnrecognizedClientException" in str(e) or "security token" in str(e):
                            st.warning("**Invalid credentials** - Please check your Access Key and Secret Key")
                        elif "AccessDenied" in str(e):
                            st.warning("**Permission denied** - Ensure your IAM user has the required permissions")
            else:
                st.warning("⚠️ Please enter AWS credentials")
        
        if analyze_button:
            if aws_access_key and aws_secret_key:
                with st.spinner("🔍 Analyzing AWS account..."):
                    try:
                        # Initialize analyzer
                        analyzer = EnhancedAWSAnalyzer(
                            aws_access_key, aws_secret_key, aws_region,
                            role_arn=role_arn if auth_method == "IAM Role ARN" else None
                        )
                        
                        # Validate credentials
                        status_text = st.empty()
                        status_text.text("🔐 Validating credentials...")
                        
                        identity = analyzer.sts_client.get_caller_identity()
                        st.success(f"✅ Authenticated as: {identity['Arn']}")
                        
                        # Perform comprehensive analysis
                        progress = st.progress(0)
                        
                        status_text.text("📊 Analyzing costs...")
                        cost_data = analyzer.analyze_costs()
                        progress.progress(15)
                        
                        status_text.text("🎯 Analyzing Reserved Instances...")
                        ri_data = analyzer.analyze_reserved_instances()
                        progress.progress(25)
                        
                        status_text.text("💰 Analyzing Savings Plans...")
                        savings_plans = analyzer.analyze_savings_plans()
                        progress.progress(35)
                        
                        status_text.text("📦 Analyzing S3 storage...")
                        s3_data = analyzer.analyze_s3_storage()
                        progress.progress(45)
                        
                        status_text.text("🗄️ Analyzing RDS instances...")
                        rds_data = analyzer.analyze_rds_instances()
                        progress.progress(55)
                        
                        status_text.text("⚡ Analyzing Lambda functions...")
                        lambda_data = analyzer.analyze_lambda_functions()
                        progress.progress(65)
                        
                        status_text.text("🔍 Detecting idle resources...")
                        idle_resources = analyzer.detect_idle_resources()
                        progress.progress(75)
                        
                        status_text.text("📈 Getting rightsizing recommendations...")
                        rightsizing = analyzer.get_rightsizing_recommendations()
                        progress.progress(75)
                        
                        status_text.text("☸️ Analyzing EKS clusters...")
                        eks_data = analyzer.analyze_eks_clusters()
                        progress.progress(78)
                        
                        status_text.text("🐳 Analyzing ECS services...")
                        ecs_data = analyzer.analyze_ecs_services()
                        progress.progress(81)
                        
                        status_text.text("🗄️ Analyzing DynamoDB tables...")
                        dynamodb_data = analyzer.analyze_dynamodb_tables()
                        progress.progress(84)
                        
                        status_text.text("⚡ Analyzing ElastiCache...")
                        elasticache_data = analyzer.analyze_elasticache_clusters()
                        progress.progress(87)
                        
                        status_text.text("📊 Analyzing Redshift...")
                        redshift_data = analyzer.analyze_redshift_clusters()
                        progress.progress(90)
                        
                        status_text.text("🌍 Analyzing global resources...")
                        global_resources = analyzer.analyze_global_resources()
                        progress.progress(93)
                        
                        status_text.text("💰 Checking budget alerts...")
                        budget_alerts = analyzer.get_budget_alerts()
                        progress.progress(96)
                        
                        status_text.text("🤖 Generating AI recommendations...")
                        recommender = EnhancedAIRecommender(aws_session=analyzer.session)
                        
                        usage_data = analyzer.analyze_usage_patterns()
                        
                        recommendations = recommender.generate_enhanced_recommendations(
                            cost_data, ri_data, usage_data, savings_plans,
                            s3_data, rds_data, lambda_data, idle_resources, rightsizing
                        )
                        progress.progress(100)
                        
                        # Store in session with cache
                        cache_manager = get_cache_manager()
                        cache_key = f"analysis_{aws_access_key[:8]}"
                        
                        analysis_data = {
                            'cost_data': cost_data,
                            'ri_data': ri_data,
                            'savings_plans': savings_plans,
                            's3_data': s3_data,
                            'rds_data': rds_data,
                            'lambda_data': lambda_data,
                            'idle_resources': idle_resources,
                            'rightsizing': rightsizing,
                            'eks_data': eks_data,
                            'ecs_data': ecs_data,
                            'dynamodb_data': dynamodb_data,
                            'elasticache_data': elasticache_data,
                            'redshift_data': redshift_data,
                            'global_resources': global_resources,
                            'budget_alerts': budget_alerts,
                            'usage_data': usage_data,
                            'recommendations': recommendations,
                            'analyzed_at': datetime.now().isoformat()
                        }
                        
                        cache_manager.set(cache_key, analysis_data)
                        st.session_state.all_analysis_data = analysis_data
                        st.session_state.analyzed = True
                        
                        status_text.empty()
                        st.success("✅ **Analysis complete!** Go to Dashboard to view results.")
                        st.balloons()
                        
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        
                        error_str = str(e)
                        if "UnrecognizedClientException" in error_str or "security token" in error_str:
                            st.warning("""
                                **Authentication Error:**
                                - Your AWS credentials are invalid or have expired
                                - Please verify your Access Key ID and Secret Access Key
                                - If using IAM role, ensure you have permission to assume it
                            """)
                        elif "AccessDenied" in error_str:
                            st.warning("""
                                **Permission Error:**
                                - Your credentials don't have the required permissions
                                - Please attach the IAM policy from `aws_iam_policy.json`
                                - Ensure Cost Explorer is enabled in AWS Billing Console
                            """)
                        
                        with st.expander("📋 Technical Details"):
                            import traceback
                            st.code(traceback.format_exc())
            else:
                st.warning("⚠️ Please enter AWS credentials")
        
        st.markdown("---")
        
        with st.expander("📚 Help & Documentation"):
            st.markdown("""
                **Required IAM Permissions:**
                - Cost Explorer: `ce:GetCostAndUsage`, `ce:GetCostForecast`
                - EC2: `ec2:Describe*`
                - S3: `s3:ListBucket`, `s3:GetBucketLocation`
                - RDS: `rds:Describe*`
                - Lambda: `lambda:List*`
                - Bedrock: `bedrock:InvokeModel`
                - Organizations: `organizations:ListAccounts` (for multi-account)
                - STS: `sts:AssumeRole` (for cross-account access)
                
                **Authentication Methods:**
                
                **1. Access Keys** - Direct access with IAM user credentials
                ```
                Access Key ID: AKIA...
                Secret Access Key: wJalrXUt...
                ```
                
                **2. IAM Role ARN** - Assume role for enhanced security
                ```
                arn:aws:iam::123456789012:role/FinOpsRole
                ```
                
                **3. Multi-Account (Organizations)** - Analyze all organization accounts
                ```
                Master Account: 123456789012
                Role Template: arn:aws:iam::{account_id}:role/OrganizationAccountAccessRole
                ```
                
                **4. Cross-Account Role** - Specific accounts with individual roles
                ```
                Format: AccountID:RoleARN
                Example: 123456789012:arn:aws:iam::123456789012:role/FinOpsRole
                ```
                
                **Multi-Account Setup:**
                1. Create a role in each target account with FinOps permissions
                2. Add trust relationship to allow assumption from master account
                3. Use Organizations master account credentials or cross-account roles
                4. Enable parallel analysis for faster processing
                
                **Note:** Cost Explorer must be enabled in AWS Billing Console (takes 24 hours to populate)
            """)
        
        with st.expander("🏢 Multi-Account & Organizations Setup"):
            st.markdown("""
                **AWS Organizations Setup:**
                
                **Step 1: Enable Organizations**
                - Go to AWS Organizations console in master account
                - Create organization or use existing one
                - Note down the master account ID
                
                **Step 2: Create Cross-Account Role**
                Create this role in each member account:
                ```json
                {
                  "Version": "2012-10-17",
                  "Statement": [
                    {
                      "Effect": "Allow",
                      "Principal": {
                        "AWS": "arn:aws:iam::MASTER_ACCOUNT_ID:root"
                      },
                      "Action": "sts:AssumeRole"
                    }
                  ]
                }
                ```
                
                **Step 3: Attach FinOps Policy**
                Attach these permissions to the cross-account role:
                - ReadOnlyAccess (AWS managed policy)
                - CostExplorerServiceRolePolicy
                - Custom policy for Bedrock access
                
                **Cross-Account Role Benefits:**
                - Enhanced security (no long-term credentials)
                - Centralized access management
                - Audit trail through CloudTrail
                - Easy credential rotation
                
                **Parallel Analysis:**
                - Analyzes multiple accounts simultaneously
                - Reduces total analysis time
                - Consolidates results into unified reports
                - Handles rate limiting automatically
                
                **Account Limits:**
                - Maximum 100 accounts per analysis
                - Recommended: Start with 10 accounts for testing
                - Increase gradually based on performance
            """)
        
        with st.expander("🔒 Security & Privacy"):
            st.markdown("""
                **Your credentials are secure:**
                - All credentials are stored only in your browser session
                - No credentials are saved to disk or transmitted to third parties
                - Session data is cleared when you logout
                - All AWS API calls are made directly from your browser
                
                **Multi-Account Security:**
                - Cross-account roles provide enhanced security
                - No need to store credentials for each account
                - Centralized access control through master account
                - Automatic credential rotation support
                
                **Best Practices:**
                - Use IAM roles instead of access keys when possible
                - Enable MFA on master/management accounts
                - Regularly audit cross-account role permissions
                - Use least privilege principle for FinOps roles
                - Monitor CloudTrail for cross-account access
            """)
        
    with tab2:
        st.markdown("### 👤 User Profile")
        
        st.markdown("""
            <div class='info-section'>
                <h4>Current Session</h4>
            </div>
        """, unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.metric("Username", st.session_state.username)
            st.metric("Email", st.session_state.user_email)
        
        with col_b:
            login_time_str = st.session_state.login_time.strftime('%Y-%m-%d %H:%M:%S') if st.session_state.login_time else 'N/A'
            st.metric("Login Time", login_time_str)
            
            if st.session_state.login_time:
                duration = datetime.now() - st.session_state.login_time
                hours = int(duration.total_seconds() // 3600)
                minutes = int((duration.total_seconds() % 3600) // 60)
                st.metric("Session Duration", f"{hours}h {minutes}m")
        
        st.markdown("---")
        
        if st.button("🔄 Change Password", use_container_width=True):
            st.info("Password change functionality coming soon!")
        
        st.markdown("""
            <div class='info-section'>
                <h4>💡 Tips for Better Analysis</h4>
                <ul>
                    <li>Ensure Cost Explorer is enabled in AWS Billing Console</li>
                    <li>Use IAM credentials with appropriate read permissions</li>
                    <li>Analysis covers the last 6 months of usage data</li>
                    <li>Re-run analysis weekly for updated recommendations</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    # Close login container
    st.markdown("</div>", unsafe_allow_html=True)

def main():
    """Main application"""
    init_session_state()
    
    # Check authentication
    if not st.session_state.authenticated:
        show_login_page()
        return
    
    # Show user info header (except on Configuration page which has its own header)
    if st.session_state.current_page != "Configuration":
        show_user_info()
    
    # Show sidebar navigation
    show_sidebar_navigation()
    
    # Show current page
    if st.session_state.current_page == "Configuration":
        show_aws_configuration()
    elif st.session_state.current_page == "Dashboard":
        show_dashboard()
    elif st.session_state.current_page == "Global":
        show_global_view()
    elif st.session_state.current_page == "KPI":
        show_kpi()
    elif st.session_state.current_page == "Recommendations":
        show_recommendations()
    elif st.session_state.current_page == "Resources":
        show_resources()
    elif st.session_state.current_page == "Savings":
        show_savings()
    elif st.session_state.current_page == "Budget":
        show_budget_manager()
    elif st.session_state.current_page == "Analytics":
        show_analytics()
    elif st.session_state.current_page == "Reports":
        show_reports()

if __name__ == "__main__":
    main()
