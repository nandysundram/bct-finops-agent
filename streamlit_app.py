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

def show_kpi():
    """KPI Dashboard page"""
    st.markdown("## 📊 Key Performance Indicators (KPI)")
    
    if not st.session_state.analyzed:
        st.info("👈 Please run analysis in Settings first")
        return
    
    data = st.session_state.all_analysis_data
    
    # Financial KPIs
    st.markdown("### 💰 Financial KPIs")
    
    fin_col1, fin_col2, fin_col3, fin_col4 = st.columns(4)
    
    with fin_col1:
        total_cost = data.get('cost_data', {}).get('total_cost', 0)
        st.metric("Total Cost (6mo)", f"${total_cost:,.2f}")
    
    with fin_col2:
        monthly_avg = total_cost / 6 if total_cost else 0
        st.metric("Monthly Average", f"${monthly_avg:,.2f}")
    
    with fin_col3:
        idle_waste = data.get('idle_resources', {}).get('total_monthly_waste', 0)
        st.metric("Monthly Waste", f"${idle_waste:,.2f}", delta=f"-${idle_waste:,.2f}", delta_color="inverse")
    
    with fin_col4:
        annual_savings = idle_waste * 12
        st.metric("Annual Savings Potential", f"${annual_savings:,.2f}", delta=f"-${annual_savings:,.2f}", delta_color="inverse")
    
    st.markdown("---")
    
    # Operational KPIs
    st.markdown("### ⚙️ Operational KPIs")
    
    op_col1, op_col2, op_col3, op_col4, op_col5 = st.columns(5)
    
    with op_col1:
        rightsizing = data.get('rightsizing', {})
        ec2_recs = rightsizing.get('recommendations', [])
        if isinstance(ec2_recs, dict):
            ec2_recs = ec2_recs.get('RightsizingRecommendations', [])
        st.metric("EC2 Instances", len(ec2_recs) if ec2_recs else 0)
    
    with op_col2:
        st.metric("S3 Buckets", data.get('s3_data', {}).get('total_buckets', 0))
    
    with op_col3:
        st.metric("RDS Instances", data.get('rds_data', {}).get('total_instances', 0))
    
    with op_col4:
        st.metric("Lambda Functions", data.get('lambda_data', {}).get('total_functions', 0))
    
    with op_col5:
        idle_items = data.get('idle_resources', {}).get('total_items', 0)
        st.metric("Idle Resources", idle_items, delta=f"{idle_items}", delta_color="inverse")
    
    st.markdown("---")
    
    # Optimization KPIs
    st.markdown("### 🎯 Optimization KPIs")
    
    opt_col1, opt_col2, opt_col3, opt_col4 = st.columns(4)
    
    with opt_col1:
        rec_count = len(data.get('recommendations', []))
        st.metric("Total Recommendations", rec_count)
    
    with opt_col2:
        critical_high = sum(1 for r in data.get('recommendations', []) if r.get('severity') in ['Critical', 'High'])
        st.metric("High Priority Items", critical_high, delta=f"{critical_high}", delta_color="inverse")
    
    with opt_col3:
        rds_underutilized = data.get('rds_data', {}).get('underutilized_count', 0)
        st.metric("Underutilized RDS", rds_underutilized, delta=f"{rds_underutilized}", delta_color="inverse")
    
    with opt_col4:
        lambda_rarely_used = data.get('lambda_data', {}).get('rarely_used_count', 0)
        st.metric("Rarely Used Lambda", lambda_rarely_used, delta=f"{lambda_rarely_used}", delta_color="inverse")
    
    st.markdown("---")
    
    # Storage KPIs
    st.markdown("### 💾 Storage KPIs")
    
    stor_col1, stor_col2, stor_col3, stor_col4 = st.columns(4)
    
    with stor_col1:
        s3_size = data.get('s3_data', {}).get('total_size_gb', 0)
        st.metric("S3 Storage", f"{s3_size:,.0f} GB")
    
    with stor_col2:
        s3_cost = data.get('s3_data', {}).get('estimated_monthly_cost', 0)
        st.metric("S3 Monthly Cost", f"${s3_cost:,.2f}")
    
    with stor_col3:
        ebs_volumes = len(data.get('idle_resources', {}).get('ebs_volumes', []))
        st.metric("Unattached EBS", ebs_volumes, delta=f"{ebs_volumes}", delta_color="inverse")
    
    with stor_col4:
        ddb_tables = data.get('dynamodb_data', {}).get('total_tables', 0)
        st.metric("DynamoDB Tables", ddb_tables)
    
    st.markdown("---")
    
    # Compute KPIs
    st.markdown("### 💻 Compute KPIs")
    
    comp_col1, comp_col2, comp_col3, comp_col4 = st.columns(4)
    
    with comp_col1:
        eks_clusters = data.get('eks_data', {}).get('total_clusters', 0)
        st.metric("EKS Clusters", eks_clusters)
    
    with comp_col2:
        ecs_tasks = data.get('ecs_data', {}).get('total_tasks', 0)
        st.metric("ECS Tasks", ecs_tasks)
    
    with comp_col3:
        lambda_invocations = data.get('lambda_data', {}).get('total_invocations_30d', 0)
        st.metric("Lambda Invocations (30d)", f"{lambda_invocations:,}")
    
    with comp_col4:
        rds_cost = data.get('rds_data', {}).get('total_monthly_cost', 0)
        st.metric("RDS Monthly Cost", f"${rds_cost:,.2f}")
    
    st.markdown("---")
    
    # Cost Efficiency Score
    st.markdown("### 🎖️ Cost Efficiency Score")
    
    # Calculate efficiency score (0-100)
    total_resources = (
        len(ec2_recs if ec2_recs else []) +
        data.get('s3_data', {}).get('total_buckets', 0) +
        data.get('rds_data', {}).get('total_instances', 0) +
        data.get('lambda_data', {}).get('total_functions', 0)
    )
    
    idle_count = data.get('idle_resources', {}).get('total_items', 0)
    
    if total_resources > 0:
        efficiency_score = max(0, 100 - (idle_count / total_resources * 100))
    else:
        efficiency_score = 100
    
    score_col1, score_col2 = st.columns([1, 2])
    
    with score_col1:
        st.metric("Efficiency Score", f"{efficiency_score:.1f}%")
        
        if efficiency_score >= 90:
            st.success("🌟 Excellent! Your infrastructure is highly optimized.")
        elif efficiency_score >= 75:
            st.info("👍 Good! Some optimization opportunities exist.")
        elif efficiency_score >= 60:
            st.warning("⚠️ Fair. Consider reviewing idle resources.")
        else:
            st.error("🚨 Poor. Immediate optimization needed!")
    
    with score_col2:
        st.progress(efficiency_score / 100)
        st.caption(f"Based on {total_resources} total resources and {idle_count} idle resources")
        
        # Recommendations based on score
        if efficiency_score < 90:
            st.markdown("**Quick Wins:**")
            if idle_count > 0:
                st.write(f"- Clean up {idle_count} idle resources")
            if critical_high > 0:
                st.write(f"- Address {critical_high} high-priority recommendations")
            if rds_underutilized > 0:
                st.write(f"- Rightsize {rds_underutilized} underutilized RDS instances")

def show_savings():
    """Savings Plans page"""
    st.markdown("## 💰 Savings Plans & Reserved Capacity")
    
    if not st.session_state.analyzed:
        st.info("👈 Please run analysis in Settings first")
        return
    
    data = st.session_state.all_analysis_data
    
    # Savings Plans
    st.markdown("### Savings Plans")
    sp = data.get('savings_plans', {})
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Annual Savings Potential", f"${sp.get('estimated_savings', 0):,.2f}")
    with col2:
        st.metric("Monthly Savings", f"${sp.get('estimated_savings', 0)/12:,.2f}")
    
    st.markdown("---")
    
    # Reserved Instances
    st.markdown("### Reserved Instances")
    ri = data.get('ri_data', {})
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Active RIs", len(ri.get('current_ris', [])))
    with col2:
        st.metric("RI Recommendations", len(ri.get('recommendations', {}).get('Recommendations', [])))

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
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            padding: 40px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
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
        
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin: 25px 0;
        }
        
        .feature-card {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            border: 1px solid #dee2e6;
        }
        
        .feature-card-icon {
            font-size: 36px;
            margin-bottom: 10px;
        }
        
        .feature-card-title {
            font-size: 13px;
            font-weight: 600;
            color: #212529;
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
    
    # Feature highlights
    st.markdown("""
        <div class='feature-grid'>
            <div class='feature-card'>
                <div class='feature-card-icon'>💰</div>
                <div class='feature-card-title'>Cost Analysis</div>
            </div>
            <div class='feature-card'>
                <div class='feature-card-icon'>🤖</div>
                <div class='feature-card-title'>AI Recommendations</div>
            </div>
            <div class='feature-card'>
                <div class='feature-card-icon'>📊</div>
                <div class='feature-card-title'>Resource Insights</div>
            </div>
            <div class='feature-card'>
                <div class='feature-card-icon'>📄</div>
                <div class='feature-card-title'>Export Reports</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Login container
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    
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
            ["Access Keys", "IAM Role ARN"],
            help="Choose how to authenticate with AWS"
        )
        
        with st.form("aws_config_form"):
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
                role_arn = None
                
            else:  # IAM Role ARN
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
                
                **IAM Role ARN Format:**
                ```
                arn:aws:iam::ACCOUNT_ID:role/ROLE_NAME
                ```
                
                **Note:** Cost Explorer must be enabled in AWS Billing Console (takes 24 hours to populate)
            """)
        
        with st.expander("🔒 Security & Privacy"):
            st.markdown("""
                **Your credentials are secure:**
                - All credentials are stored only in your browser session
                - No credentials are saved to disk or transmitted to third parties
                - Session data is cleared when you logout
                - All AWS API calls are made directly from your browser
                
                **Best Practices:**
                - Use IAM users with read-only permissions
                - Enable MFA on your AWS account
                - Regularly rotate access keys
                - Use IAM roles when possible
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
    elif st.session_state.current_page == "Analytics":
        show_analytics()
    elif st.session_state.current_page == "Reports":
        show_reports()

if __name__ == "__main__":
    main()
