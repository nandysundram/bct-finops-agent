"""
Report Scheduler
Schedule automated cost analysis reports
"""

import schedule
import time
from datetime import datetime
from typing import Callable, Dict, List
import json
import os

class ReportScheduler:
    def __init__(self, config_path: str = 'scheduler_config.json'):
        """Initialize scheduler"""
        self.config_path = config_path
        self.jobs = []
        self.load_config()
    
    def load_config(self):
        """Load scheduler configuration"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
            except:
                self.config = {'schedules': []}
        else:
            self.config = {'schedules': []}
    
    def save_config(self):
        """Save scheduler configuration"""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def add_schedule(
        self,
        name: str,
        frequency: str,  # 'daily', 'weekly', 'monthly'
        time_str: str,  # '09:00'
        day_of_week: str = None,  # 'monday', 'tuesday', etc.
        recipients: List[str] = None,
        report_formats: List[str] = None,
        enabled: bool = True
    ):
        """Add a new schedule"""
        schedule_config = {
            'name': name,
            'frequency': frequency,
            'time': time_str,
            'day_of_week': day_of_week,
            'recipients': recipients or [],
            'report_formats': report_formats or ['PDF'],
            'enabled': enabled,
            'created_at': datetime.now().isoformat()
        }
        
        self.config['schedules'].append(schedule_config)
        self.save_config()
        
        return schedule_config
    
    def remove_schedule(self, name: str):
        """Remove a schedule by name"""
        self.config['schedules'] = [
            s for s in self.config['schedules'] if s['name'] != name
        ]
        self.save_config()
    
    def get_schedules(self) -> List[Dict]:
        """Get all schedules"""
        return self.config.get('schedules', [])
    
    def setup_jobs(self, report_function: Callable):
        """Setup scheduled jobs"""
        schedule.clear()
        
        for sched in self.config.get('schedules', []):
            if not sched.get('enabled', True):
                continue
            
            frequency = sched['frequency']
            time_str = sched['time']
            
            if frequency == 'daily':
                schedule.every().day.at(time_str).do(
                    report_function,
                    schedule_config=sched
                )
            
            elif frequency == 'weekly':
                day = sched.get('day_of_week', 'monday').lower()
                getattr(schedule.every(), day).at(time_str).do(
                    report_function,
                    schedule_config=sched
                )
            
            elif frequency == 'monthly':
                # Run on first day of month
                schedule.every().day.at(time_str).do(
                    self._check_monthly,
                    report_function,
                    sched
                )
    
    def _check_monthly(self, report_function: Callable, schedule_config: Dict):
        """Check if it's the first day of month"""
        if datetime.now().day == 1:
            report_function(schedule_config=schedule_config)
    
    def run_pending(self):
        """Run pending scheduled jobs"""
        schedule.run_pending()
    
    def run_forever(self, report_function: Callable):
        """Run scheduler continuously"""
        self.setup_jobs(report_function)
        
        print("Scheduler started. Press Ctrl+C to stop.")
        print(f"Active schedules: {len([s for s in self.config['schedules'] if s.get('enabled', True)])}")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\nScheduler stopped.")


class SchedulerConfig:
    """Helper class for creating scheduler configurations"""
    
    @staticmethod
    def create_daily_report(time: str = "09:00", recipients: List[str] = None):
        """Create daily report configuration"""
        return {
            'name': 'Daily Cost Report',
            'frequency': 'daily',
            'time': time,
            'recipients': recipients or [],
            'report_formats': ['PDF'],
            'enabled': True
        }
    
    @staticmethod
    def create_weekly_report(day: str = 'monday', time: str = "09:00", recipients: List[str] = None):
        """Create weekly report configuration"""
        return {
            'name': 'Weekly Cost Report',
            'frequency': 'weekly',
            'time': time,
            'day_of_week': day,
            'recipients': recipients or [],
            'report_formats': ['PDF', 'XLSX'],
            'enabled': True
        }
    
    @staticmethod
    def create_monthly_report(time: str = "09:00", recipients: List[str] = None):
        """Create monthly report configuration"""
        return {
            'name': 'Monthly Cost Report',
            'frequency': 'monthly',
            'time': time,
            'recipients': recipients or [],
            'report_formats': ['PDF', 'XLSX'],
            'enabled': True
        }
