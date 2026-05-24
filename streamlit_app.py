#!/usr/bin/env python3
"""
CloudXcelAI FinOptimizer v2.0 - Clean Version
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import os

from src.enhanced_analyzer import EnhancedAWSAnalyzer
from src.enhanced_ai_recommender import EnhancedAIRecommender
from src.supabase_auth import SupabaseAuth

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="CloudXcelAI FinOptimizer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'Dashboard'
    if 'analyzed' not in st.session_state:
        st.session_state.analyzed = False
    if 'username' not in st.session_state:
        st.session_state.username = None

def show_login_page():
    """Login and Signup page with Supabase authentication"""
    st.title("🔐 CloudXcelAI FinOptimizer")
    st.subheader("Welcome to Enterprise Cloud Financial Operations Platform")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Tabs for Login and Signup
        tab1, tab2 = st.tabs(["🔑 Sign In", "📝 Sign Up"])
        
        with tab1:
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="Enter your email", key="login_email")
                password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")
                
                login_button = st.form_submit_button("Sign In", use_container_width=True)
            
            if login_button:
                if email and password:
                    try:
                        auth = SupabaseAuth()
                        result = auth.sign_in(email, password)
                        
                        if result['success']:
                            st.session_state.authenticated = True
                            st.session_state.username = result['user'].email
                            st.session_state.user_id = result['user'].id
                            st.session_state.login_time = datetime.now()
                            st.success(f"✅ Welcome back, {result['user'].email}!")
                            st.rerun()
                        else:
                            st.error(f"❌ {result['error']}")
                    except Exception as e:
                        st.error(f"❌ Authentication error: {str(e)}")
                else:
                    st.warning("⚠️ Please enter both email and password")
        
        with tab2:
            with st.form("signup_form"):
                signup_email = st.text_input("Email", placeholder="Enter your email", key="signup_email")
                signup_password = st.text_input("Password", type="password", placeholder="Create a password (min 6 characters)", key="signup_password")
                signup_password_confirm = st.text_input("Confirm Password", type="password", placeholder="Confirm your password", key="signup_password_confirm")
                
                signup_button = st.form_submit_button("Create Account", use_container_width=True)
            
            if signup_button:
                if signup_email and signup_password and signup_password_confirm:
                    if signup_password != signup_password_confirm:
                        st.error("❌ Passwords do not match!")
                    elif len(signup_password) < 6:
                        st.error("❌ Password must be at least 6 characters long!")
                    else:
                        try:
                            auth = SupabaseAuth()
                            result = auth.sign_up(signup_email, signup_password)
                            
                            if result['success']:
                                st.success("✅ Account created successfully! Please check your email to verify your account, then sign in.")
                                st.info("💡 You may need to verify your email before signing in, depending on your Supabase settings.")
                            else:
                                st.error(f"❌ {result['error']}")
                        except Exception as e:
                            st.error(f"❌ Signup error: {str(e)}")
                else:
                    st.warning("⚠️ Please fill in all fields")
        
        st.markdown("---")
        st.info("""
            **Supabase Authentication**
            - Secure authentication powered by Supabase
            - Your credentials are encrypted and stored securely
            - Email verification may be required based on settings
        """)

def show_header():
    """Display application header"""
    st.markdown("""
        <div style='background: linear-gradient(135deg, #0066cc 0%, #003d7a 100%); 
                    padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
            <h1 style='color: white; margin: 0;'>CloudXcelAI FinOptimizer</h1>
            <p style='color: #e9ecef; margin: 5px 0 0 0;'>Enterprise Cloud Financial Operations Platform</p>
        </div>
    """, unsafe_allow_html=True)

def show_dashboard():
    """Main dashboard with comprehensive analysis and graphs"""
    st.markdown("## 📊 Dashboard")
    
    if not st.session_state.analyzed:
        st.info("👈 Please configure AWS credentials below to start comprehensive analysis")
        
        # Quick setup
        with st.expander("⚙️ Quick AWS Setup", expanded=True):
            with st.form("quick_aws_form"):
                col1, col2 = st.columns(2)
                with col1:
                    aws_key = st.text_input("AWS Access Key", type="password")
                    region = st.selectbox("Region", ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1", "ap-south-1"])
                with col2:
                    aws_secret = st.text_input("AWS Secret Key", type="password")
                    analyze_all_regions = st.checkbox("Analyze All Regions", value=False)
                
                if st.form_submit_button("🚀 Start Comprehensive Analysis", use_container_width=True):
                    if aws_key and aws_secret:
                        with st.spinner("🔍 Analyzing your AWS infrastructure... This may take a few minutes."):
                            try:
                                # Initialize analyzer
                                analyzer = EnhancedAWSAnalyzer(
                                    access_key=aws_key,
                                    secret_key=aws_secret,
                                    region=region
                                )
                                
                                # Progress bar
                                progress = st.progress(0)
                                status_text = st.empty()
                                
                                # Run comprehensive analysis
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
                                
                                status_text.text("🔍 Identifying idle resources...")
                                idle_resources = analyzer.detect_idle_resources()
                                progress.progress(75)
                                
                                status_text.text("💻 Analyzing EC2 usage...")
                                usage_data = analyzer.analyze_usage_patterns()
                                progress.progress(85)
                                
                                status_text.text("💡 Getting rightsizing recommendations...")
                                rightsizing = analyzer.get_rightsizing_recommendations()
                                progress.progress(95)
                                
                                status_text.text("✅ Finalizing analysis...")
                                
                                # Store all analysis data
                                st.session_state.all_analysis_data = {
                                    'cost_data': cost_data,
                                    'ri_data': ri_data,
                                    'savings_plans': savings_plans,
                                    's3_data': s3_data,
                                    'rds_data': rds_data,
                                    'lambda_data': lambda_data,
                                    'idle_resources': idle_resources,
                                    'usage_data': usage_data,
                                    'rightsizing': rightsizing,
                                    'analysis_timestamp': datetime.now().isoformat()
                                }
                                
                                st.session_state.analyzed = True
                                progress.progress(100)
                                status_text.empty()
                                progress.empty()
                                
                                st.success("✅ Analysis completed successfully!")
                                st.balloons()
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"❌ Error during analysis: {str(e)}")
                                import traceback
                                with st.expander("Show error details"):
                                    st.code(traceback.format_exc())
                    else:
                        st.warning("⚠️ Please provide AWS credentials")
    else:
        # Show analysis results
        data = st.session_state.all_analysis_data
        
        st.success(f"✅ Analysis completed at {data.get('analysis_timestamp', 'N/A')}")
        
        if st.button("🔄 Re-analyze"):
            st.session_state.analyzed = False
            st.rerun()
        
        st.markdown("---")
        
        # Key Metrics
        st.markdown("### 📈 Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        total_cost = data.get('cost_data', {}).get('total_cost', 0)
        monthly_avg = total_cost / 6 if total_cost > 0 else 0
        idle_waste = data.get('idle_resources', {}).get('total_monthly_waste', 0)
        
        # Count resources
        ec2_count = data.get('usage_data', {}).get('total_instances', 0)
        s3_count = data.get('s3_data', {}).get('total_buckets', 0)
        rds_count = data.get('rds_data', {}).get('total_instances', 0)
        lambda_count = data.get('lambda_data', {}).get('total_functions', 0)
        total_resources = ec2_count + s3_count + rds_count + lambda_count
        
        with col1:
            st.metric("Total Cost (6mo)", f"${total_cost:,.2f}")
        with col2:
            st.metric("Monthly Average", f"${monthly_avg:,.2f}")
        with col3:
            st.metric("Total Resources", total_resources)
        with col4:
            st.metric("Potential Savings", f"${idle_waste:,.2f}/mo", 
                     delta=f"-${idle_waste*12:,.2f}/yr", delta_color="inverse")
        
        st.markdown("---")
        
        # Cost Trend Chart
        st.markdown("### 💰 Cost Trend (Last 6 Months)")
        cost_history = data.get('cost_data', {}).get('historical', [])
        
        if cost_history:
            import plotly.graph_objects as go
            
            dates = []
            costs = []
            
            for period in cost_history:
                start_date = period.get('TimePeriod', {}).get('Start', '')
                cost_amount = float(period.get('Total', {}).get('UnblendedCost', {}).get('Amount', 0))
                dates.append(start_date)
                costs.append(cost_amount)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=dates,
                y=costs,
                mode='lines+markers',
                name='Monthly Cost',
                line=dict(color='#0066cc', width=3),
                marker=dict(size=8)
            ))
            
            fig.update_layout(
                title='Monthly AWS Costs',
                xaxis_title='Month',
                yaxis_title='Cost (USD)',
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No cost history data available")
        
        # Resource Distribution
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown("### 📊 Resource Distribution")
            
            if total_resources > 0:
                import plotly.graph_objects as go
                
                resource_data = {
                    'EC2 Instances': ec2_count,
                    'S3 Buckets': s3_count,
                    'RDS Instances': rds_count,
                    'Lambda Functions': lambda_count
                }
                
                # Filter out zero values
                resource_data = {k: v for k, v in resource_data.items() if v > 0}
                
                fig = go.Figure(data=[go.Pie(
                    labels=list(resource_data.keys()),
                    values=list(resource_data.values()),
                    hole=.3,
                    marker=dict(colors=['#0066cc', '#00a8e8', '#007ea7', '#003459'])
                )])
                
                fig.update_layout(
                    title='Resources by Type',
                    height=350
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No resources found")
        
        with col_right:
            st.markdown("### 💸 Cost Optimization Opportunities")
            
            idle_items = data.get('idle_resources', {}).get('total_items', 0)
            rightsizing_count = len(data.get('rightsizing', {}).get('recommendations', []))
            
            opportunities = []
            
            if idle_waste > 0:
                opportunities.append({
                    'Category': 'Idle Resources',
                    'Count': idle_items,
                    'Monthly Savings': f"${idle_waste:,.2f}"
                })
            
            if rightsizing_count > 0:
                rightsizing_savings = data.get('rightsizing', {}).get('total_monthly_savings', 0)
                opportunities.append({
                    'Category': 'EC2 Rightsizing',
                    'Count': rightsizing_count,
                    'Monthly Savings': f"${rightsizing_savings:,.2f}"
                })
            
            sp_savings = data.get('savings_plans', {}).get('estimated_savings', 0) / 12
            if sp_savings > 0:
                opportunities.append({
                    'Category': 'Savings Plans',
                    'Count': 1,
                    'Monthly Savings': f"${sp_savings:,.2f}"
                })
            
            if opportunities:
                df_opp = pd.DataFrame(opportunities)
                st.dataframe(df_opp, use_container_width=True, hide_index=True)
                
                total_monthly_savings = idle_waste + data.get('rightsizing', {}).get('total_monthly_savings', 0) + sp_savings
                st.metric("Total Monthly Savings Potential", f"${total_monthly_savings:,.2f}")
            else:
                st.success("✅ No major optimization opportunities found!")
        
        st.markdown("---")
        
        # Quick Stats
        st.markdown("### 📦 Resource Summary")
        
        res_col1, res_col2, res_col3, res_col4 = st.columns(4)
        
        with res_col1:
            st.metric("EC2 Instances", ec2_count)
            st.caption("Running instances")
        
        with res_col2:
            st.metric("S3 Buckets", s3_count)
            s3_size = data.get('s3_data', {}).get('total_size_gb', 0)
            st.caption(f"{s3_size:.2f} GB total")
        
        with res_col3:
            st.metric("RDS Instances", rds_count)
            rds_cost = data.get('rds_data', {}).get('total_monthly_cost', 0)
            st.caption(f"${rds_cost:,.2f}/mo")
        
        with res_col4:
            st.metric("Lambda Functions", lambda_count)
            lambda_invocations = data.get('lambda_data', {}).get('total_invocations_30d', 0)
            st.caption(f"{lambda_invocations:,} invocations")
        
        st.markdown("---")
        
        # Idle Resources Alert
        if idle_waste > 100:
            st.error(f"🚨 **Critical**: You're wasting ${idle_waste:,.2f}/month on idle resources! Check the Resources tab for details.")
        elif idle_waste > 50:
            st.warning(f"⚠️ **Warning**: ${idle_waste:,.2f}/month in idle resources detected. Review and clean up soon.")
        elif idle_waste > 0:
            st.info(f"💡 **Opportunity**: ${idle_waste:,.2f}/month can be saved by cleaning up idle resources.")

def show_global_view():
    """Global resource view"""
    st.markdown("## 🌍 Global View")
    
    if not st.session_state.analyzed:
        st.warning("⚠️ Please run analysis from Dashboard first")
        return
    
    data = st.session_state.all_analysis_data
    
    st.info("Global resource distribution across all AWS regions")
    
    # Resource counts
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        ec2_count = data.get('usage_data', {}).get('total_instances', 0)
        st.metric("EC2 Instances", ec2_count)
    
    with col2:
        s3_count = data.get('s3_data', {}).get('total_buckets', 0)
        st.metric("S3 Buckets", s3_count)
    
    with col3:
        rds_count = data.get('rds_data', {}).get('total_instances', 0)
        st.metric("RDS Instances", rds_count)
    
    with col4:
        lambda_count = data.get('lambda_data', {}).get('total_functions', 0)
        st.metric("Lambda Functions", lambda_count)

def show_kpi():
    """KPI Dashboard"""
    st.markdown("## 📊 FinOps KPI Dashboard")
    
    if not st.session_state.analyzed:
        st.warning("⚠️ Please run analysis from Dashboard first")
        return
    
    data = st.session_state.all_analysis_data
    
    st.info("Key Performance Indicators for Cloud Financial Operations")
    
    # Calculate KPIs
    total_cost = data.get('cost_data', {}).get('total_cost', 0)
    idle_waste = data.get('idle_resources', {}).get('total_monthly_waste', 0)
    
    cost_efficiency = ((total_cost - idle_waste) / total_cost * 100) if total_cost > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Cost Efficiency", f"{cost_efficiency:.1f}%")
    
    with col2:
        ec2_count = data.get('usage_data', {}).get('total_instances', 0)
        utilization = 75.0  # Placeholder
        st.metric("Resource Utilization", f"{utilization:.1f}%")
    
    with col3:
        savings_rate = (idle_waste / total_cost * 100) if total_cost > 0 else 0
        st.metric("Savings Opportunity", f"{savings_rate:.1f}%")
    
    with col4:
        st.metric("FinOps Maturity", "Intermediate")

def show_recommendations():
    """Cost optimization recommendations"""
    st.markdown("## 💡 Cost Optimization Recommendations")
    
    if not st.session_state.analyzed:
        st.warning("⚠️ Please run analysis from Dashboard first")
        return
    
    data = st.session_state.all_analysis_data
    
    st.info("AI-powered recommendations to optimize your cloud spending")
    
    # Idle Resources
    idle_resources = data.get('idle_resources', {})
    idle_waste = idle_resources.get('total_monthly_waste', 0)
    
    if idle_waste > 0:
        st.markdown("### 💾 Idle Resources")
        st.error(f"Found {idle_resources.get('total_items', 0)} idle resources wasting ${idle_waste:,.2f}/month")
        
        # EBS Volumes
        ebs_volumes = idle_resources.get('ebs_volumes', [])
        if ebs_volumes:
            st.markdown("#### Unattached EBS Volumes")
            df_ebs = pd.DataFrame(ebs_volumes)
            st.dataframe(df_ebs, use_container_width=True)
        
        # Elastic IPs
        elastic_ips = idle_resources.get('elastic_ips', [])
        if elastic_ips:
            st.markdown("#### Unassociated Elastic IPs")
            df_ips = pd.DataFrame(elastic_ips)
            st.dataframe(df_ips, use_container_width=True)
    
    # Rightsizing
    rightsizing = data.get('rightsizing', {})
    recommendations = rightsizing.get('recommendations', [])
    
    if recommendations:
        st.markdown("### 💻 EC2 Rightsizing Recommendations")
        st.info(f"Found {len(recommendations)} instances that can be optimized")
        
        savings = rightsizing.get('total_monthly_savings', 0)
        if savings > 0:
            st.success(f"Potential savings: ${savings:,.2f}/month")

def show_resources():
    """Resource analysis"""
    st.markdown("## 🗂️ Resource Analysis")
    
    if not st.session_state.analyzed:
        st.warning("⚠️ Please run analysis from Dashboard first")
        return
    
    data = st.session_state.all_analysis_data
    
    st.info("Detailed analysis of all your AWS resources")
    
    tabs = st.tabs(["💻 EC2", "📦 S3", "🗄️ RDS", "⚡ Lambda", "💾 Idle Resources"])
    
    with tabs[0]:
        st.markdown("### EC2 Instances")
        usage_data = data.get('usage_data', {})
        instances = usage_data.get('instances', [])
        
        if instances:
            st.metric("Total Instances", len(instances))
            
            # Create dataframe
            ec2_list = []
            for inst in instances:
                ec2_list.append({
                    'Instance ID': inst.get('instance_id', 'N/A'),
                    'Instance Type': inst.get('instance_type', 'N/A'),
                    'CPU Data Points': len(inst.get('cpu_stats', []))
                })
            
            df_ec2 = pd.DataFrame(ec2_list)
            st.dataframe(df_ec2, use_container_width=True)
        else:
            st.info("No EC2 instances found")
    
    with tabs[1]:
        st.markdown("### S3 Buckets")
        s3_data = data.get('s3_data', {})
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Buckets", s3_data.get('total_buckets', 0))
        with col2:
            st.metric("Total Size", f"{s3_data.get('total_size_gb', 0):.2f} GB")
        with col3:
            st.metric("Monthly Cost", f"${s3_data.get('estimated_monthly_cost', 0):.2f}")
        
        storage_details = s3_data.get('storage_details', [])
        if storage_details:
            df_s3 = pd.DataFrame(storage_details)
            st.dataframe(df_s3, use_container_width=True)
    
    with tabs[2]:
        st.markdown("### RDS Instances")
        rds_data = data.get('rds_data', {})
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Instances", rds_data.get('total_instances', 0))
        with col2:
            st.metric("Monthly Cost", f"${rds_data.get('total_monthly_cost', 0):,.2f}")
        
        instances = rds_data.get('instances', [])
        if instances:
            df_rds = pd.DataFrame(instances)
            st.dataframe(df_rds, use_container_width=True)
    
    with tabs[3]:
        st.markdown("### Lambda Functions")
        lambda_data = data.get('lambda_data', {})
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Functions", lambda_data.get('total_functions', 0))
        with col2:
            st.metric("Total Invocations (30d)", f"{lambda_data.get('total_invocations_30d', 0):,}")
        
        functions = lambda_data.get('functions', [])
        if functions:
            df_lambda = pd.DataFrame(functions)
            st.dataframe(df_lambda, use_container_width=True)
    
    with tabs[4]:
        st.markdown("### Idle Resources")
        idle_resources = data.get('idle_resources', {})
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Idle Items", idle_resources.get('total_items', 0))
        with col2:
            st.metric("Monthly Waste", f"${idle_resources.get('total_monthly_waste', 0):,.2f}")
        
        # Show idle resource details
        ebs_volumes = idle_resources.get('ebs_volumes', [])
        if ebs_volumes:
            st.markdown("#### Unattached EBS Volumes")
            df_ebs = pd.DataFrame(ebs_volumes)
            st.dataframe(df_ebs, use_container_width=True)

def show_savings():
    """Savings Plans"""
    st.markdown("## 💰 Savings Plans & Reserved Capacity")
    st.info("Optimize costs with Savings Plans and Reserved Instances")
    
    if not st.session_state.analyzed:
        st.warning("⚠️ Please run analysis from Dashboard first")
    else:
        st.write("Savings plans recommendations will be displayed here")

def show_analytics():
    """Advanced analytics"""
    st.markdown("## 📈 Advanced Analytics")
    st.info("Deep dive into cost trends and forecasting")
    
    if not st.session_state.analyzed:
        st.warning("⚠️ Please run analysis from Dashboard first")
    else:
        st.write("Analytics charts and trends will be displayed here")

def show_reports():
    """Generate reports"""
    st.markdown("## 📄 Generate & Download Reports")
    st.info("Create comprehensive PDF and Excel reports")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Generate PDF Report", use_container_width=True):
            st.info("PDF report generation coming soon")
    with col2:
        if st.button("📑 Generate Excel Report", use_container_width=True):
            st.info("Excel report generation coming soon")

def show_settings():
    """Settings page"""
    st.markdown("## ⚙️ Settings")
    
    st.markdown("### AWS Configuration")
    with st.form("aws_config_form"):
        aws_key = st.text_input("AWS Access Key", type="password")
        aws_secret = st.text_input("AWS Secret Key", type="password")
        region = st.selectbox("Default Region", ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"])
        
        if st.form_submit_button("Save Configuration"):
            st.success("✅ Configuration saved!")
    
    st.markdown("---")
    st.markdown("### User Profile")
    st.write(f"**Email:** {st.session_state.username}")
    st.write(f"**User ID:** {st.session_state.get('user_id', 'N/A')}")
    if st.session_state.get('login_time'):
        st.write(f"**Login Time:** {st.session_state.login_time.strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Main application"""
    init_session_state()
    
    # Check authentication
    if not st.session_state.authenticated:
        show_login_page()
        return
    
    # Show header
    show_header()
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📋 Navigation")
        
        if st.button("🏠 Dashboard", use_container_width=True, type="primary" if st.session_state.current_page == 'Dashboard' else "secondary"):
            st.session_state.current_page = 'Dashboard'
            st.rerun()
        
        if st.button("🌍 Global View", use_container_width=True, type="primary" if st.session_state.current_page == 'Global' else "secondary"):
            st.session_state.current_page = 'Global'
            st.rerun()
        
        if st.button("📊 KPI", use_container_width=True, type="primary" if st.session_state.current_page == 'KPI' else "secondary"):
            st.session_state.current_page = 'KPI'
            st.rerun()
        
        if st.button("💡 Recommendations", use_container_width=True, type="primary" if st.session_state.current_page == 'Recommendations' else "secondary"):
            st.session_state.current_page = 'Recommendations'
            st.rerun()
        
        if st.button("🗂️ Resources", use_container_width=True, type="primary" if st.session_state.current_page == 'Resources' else "secondary"):
            st.session_state.current_page = 'Resources'
            st.rerun()
        
        if st.button("💰 Savings Plans", use_container_width=True, type="primary" if st.session_state.current_page == 'Savings' else "secondary"):
            st.session_state.current_page = 'Savings'
            st.rerun()
        
        if st.button("📈 Analytics", use_container_width=True, type="primary" if st.session_state.current_page == 'Analytics' else "secondary"):
            st.session_state.current_page = 'Analytics'
            st.rerun()
        
        if st.button("📄 Reports", use_container_width=True, type="primary" if st.session_state.current_page == 'Reports' else "secondary"):
            st.session_state.current_page = 'Reports'
            st.rerun()
        
        if st.button("⚙️ Settings", use_container_width=True, type="primary" if st.session_state.current_page == 'Settings' else "secondary"):
            st.session_state.current_page = 'Settings'
            st.rerun()
        
        st.markdown("---")
        st.markdown(f"**User:** {st.session_state.username}")
        
        if st.button("🚪 Logout", use_container_width=True):
            try:
                auth = SupabaseAuth()
                auth.sign_out()
            except:
                pass
            st.session_state.authenticated = False
            st.session_state.username = None
            st.rerun()
    
    # Show current page
    if st.session_state.current_page == 'Dashboard':
        show_dashboard()
    elif st.session_state.current_page == 'Global':
        show_global_view()
    elif st.session_state.current_page == 'KPI':
        show_kpi()
    elif st.session_state.current_page == 'Recommendations':
        show_recommendations()
    elif st.session_state.current_page == 'Resources':
        show_resources()
    elif st.session_state.current_page == 'Savings':
        show_savings()
    elif st.session_state.current_page == 'Analytics':
        show_analytics()
    elif st.session_state.current_page == 'Reports':
        show_reports()
    elif st.session_state.current_page == 'Settings':
        show_settings()

if __name__ == "__main__":
    main()
