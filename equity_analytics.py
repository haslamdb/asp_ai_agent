#!/usr/bin/env python3
"""
Equity Tracking and Analytics System for ASP AI Agent
Monitors and prevents disparities in learning outcomes
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import numpy as np
import sqlite3
import json
from enum import Enum
from collections import defaultdict
import statistics

class DemographicCategory(Enum):
    """Categories for demographic analysis"""
    INSTITUTION_TYPE = "institution_type"  # Academic, Community, VA, etc.
    FELLOWSHIP_YEAR = "fellowship_year"  # PGY4, PGY5, PGY6
    GEOGRAPHIC_REGION = "geographic_region"  # Northeast, South, Midwest, West
    PRIOR_EXPERIENCE = "prior_experience"  # None, Some, Extensive
    LEARNING_STYLE = "learning_style"  # Visual, Verbal, Kinesthetic, Balanced
    TIME_ZONE = "time_zone"  # For accessibility analysis
    INSTITUTION_SIZE = "institution_size"  # Small, Medium, Large

@dataclass
class PerformanceMetric:
    """Performance metric with disaggregation capability"""
    name: str
    value: float
    sample_size: int
    std_deviation: float = 0.0
    confidence_interval: Tuple[float, float] = (0.0, 0.0)
    
    def is_significant_difference(self, other: 'PerformanceMetric', threshold: float = 0.1) -> bool:
        """Check if difference between metrics is significant"""
        if self.sample_size < 5 or other.sample_size < 5:
            return False  # Not enough data
        
        difference = abs(self.value - other.value)
        # Simple threshold-based check (could use statistical tests)
        return difference > threshold

@dataclass
class DisparityAlert:
    """Alert for identified disparity"""
    category: DemographicCategory
    group_affected: str
    metric: str
    severity: str  # low, medium, high
    description: str
    recommended_actions: List[str]
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class EquityReport:
    """Comprehensive equity analysis report"""
    timestamp: datetime = field(default_factory=datetime.now)
    total_users: int = 0
    demographic_breakdowns: Dict[str, Dict] = field(default_factory=dict)
    performance_gaps: List[Dict] = field(default_factory=list)
    disparities_found: List[DisparityAlert] = field(default_factory=list)
    trends: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)

class EquityAnalytics:
    """Main equity tracking and analytics engine"""
    
    def __init__(self, db_path: str = "asp_sessions.db"):
        self.db_path = db_path
        self.disparity_thresholds = {
            "low": 0.1,  # 10% difference
            "medium": 0.2,  # 20% difference
            "high": 0.3  # 30% difference
        }
        self.minimum_sample_size = 5
        
    def analyze_equity(self, time_window_days: int = 30) -> EquityReport:
        """Perform comprehensive equity analysis"""
        report = EquityReport()
        
        # Get user data
        users_data = self._get_user_data(time_window_days)
        report.total_users = len(users_data)
        
        if report.total_users < self.minimum_sample_size:
            report.recommendations.append("Insufficient data for equity analysis. Need more users.")
            return report
        
        # Analyze by different demographic categories
        for category in DemographicCategory:
            breakdown = self._analyze_by_category(users_data, category)
            if breakdown:
                report.demographic_breakdowns[category.value] = breakdown
                
                # Check for disparities
                disparities = self._identify_disparities(breakdown, category)
                report.disparities_found.extend(disparities)
        
        # Analyze performance gaps
        report.performance_gaps = self._analyze_performance_gaps(users_data)
        
        # Analyze trends
        report.trends = self._analyze_trends(users_data)
        
        # Generate recommendations
        report.recommendations = self._generate_recommendations(report)
        
        return report
    
    def _get_user_data(self, days: int) -> List[Dict]:
        """Retrieve user data from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Get user sessions with demographics and performance
        cursor.execute('''
            SELECT 
                s.user_id,
                s.email,
                s.name,
                s.institution,
                s.fellowship_year,
                s.current_difficulty,
                s.learning_velocity,
                s.last_active,
                COUNT(DISTINCT mp.module_id) as modules_attempted,
                AVG(mp.best_score) as avg_best_score,
                AVG(mp.mastery_level) as avg_mastery,
                SUM(mp.attempts) as total_attempts,
                SUM(mp.time_spent_seconds) as total_time
            FROM sessions s
            LEFT JOIN module_progress mp ON s.user_id = mp.user_id
            WHERE s.last_active > ?
            GROUP BY s.user_id
        ''', (cutoff_date,))
        
        columns = [desc[0] for desc in cursor.description]
        users_data = []
        
        for row in cursor.fetchall():
            user_dict = dict(zip(columns, row))
            
            # Add derived demographic categories
            user_dict['institution_type'] = self._categorize_institution(user_dict.get('institution'))
            user_dict['geographic_region'] = self._infer_region(user_dict.get('institution'))
            user_dict['institution_size'] = self._categorize_size(user_dict.get('institution'))
            
            users_data.append(user_dict)
        
        conn.close()
        return users_data
    
    def _categorize_institution(self, institution: str) -> str:
        """Categorize institution type"""
        if not institution:
            return "unknown"
        
        institution_lower = institution.lower()
        
        if any(term in institution_lower for term in ['university', 'college', 'academic']):
            return "academic"
        elif any(term in institution_lower for term in ['community', 'regional']):
            return "community"
        elif 'va' in institution_lower or 'veteran' in institution_lower:
            return "va"
        elif any(term in institution_lower for term in ['children', 'pediatric']):
            return "pediatric"
        else:
            return "other"
    
    def _infer_region(self, institution: str) -> str:
        """Infer geographic region from institution name"""
        if not institution:
            return "unknown"
        
        # Simple mapping - in production, would use more sophisticated geocoding
        institution_lower = institution.lower()
        
        northeast = ['boston', 'new york', 'philadelphia', 'connecticut', 'maine']
        south = ['texas', 'florida', 'georgia', 'carolina', 'virginia']
        midwest = ['chicago', 'michigan', 'ohio', 'wisconsin', 'minnesota']
        west = ['california', 'oregon', 'washington', 'colorado', 'arizona']
        
        for term in northeast:
            if term in institution_lower:
                return "northeast"
        for term in south:
            if term in institution_lower:
                return "south"
        for term in midwest:
            if term in institution_lower:
                return "midwest"
        for term in west:
            if term in institution_lower:
                return "west"
        
        return "unknown"
    
    def _categorize_size(self, institution: str) -> str:
        """Categorize institution size"""
        # This would ideally use actual bed count or fellow count data
        if not institution:
            return "unknown"
        
        # Placeholder logic
        if any(term in institution.lower() for term in ['large', 'major', 'system']):
            return "large"
        elif any(term in institution.lower() for term in ['small', 'rural']):
            return "small"
        else:
            return "medium"
    
    def _analyze_by_category(self, users_data: List[Dict], 
                            category: DemographicCategory) -> Dict:
        """Analyze performance by demographic category"""
        category_key = category.value
        groups = defaultdict(list)
        
        # Group users by category
        for user in users_data:
            group_value = user.get(category_key, "unknown")
            if group_value is not None:  # Handle fellowship year = 0
                groups[str(group_value)].append(user)
        
        # Calculate metrics for each group
        breakdown = {}
        for group_name, group_users in groups.items():
            if len(group_users) >= self.minimum_sample_size:
                metrics = self._calculate_group_metrics(group_users)
                breakdown[group_name] = metrics
        
        return breakdown
    
    def _calculate_group_metrics(self, users: List[Dict]) -> Dict:
        """Calculate performance metrics for a group"""
        metrics = {
            "sample_size": len(users),
            "avg_mastery": 0.0,
            "avg_modules_completed": 0.0,
            "avg_time_hours": 0.0,
            "avg_attempts_per_module": 0.0,
            "completion_rate": 0.0,
            "std_dev_mastery": 0.0
        }
        
        if not users:
            return metrics
        
        # Calculate averages
        mastery_scores = [u.get('avg_mastery', 0) or 0 for u in users]
        modules_attempted = [u.get('modules_attempted', 0) or 0 for u in users]
        total_times = [u.get('total_time', 0) or 0 for u in users]
        total_attempts = [u.get('total_attempts', 0) or 0 for u in users]
        
        metrics["avg_mastery"] = round(statistics.mean(mastery_scores), 3) if mastery_scores else 0
        metrics["avg_modules_completed"] = round(statistics.mean(modules_attempted), 1) if modules_attempted else 0
        metrics["avg_time_hours"] = round(statistics.mean(total_times) / 3600, 1) if total_times else 0
        
        # Calculate attempts per module
        attempts_per_module = []
        for i, user in enumerate(users):
            if modules_attempted[i] > 0:
                attempts_per_module.append(total_attempts[i] / modules_attempted[i])
        
        metrics["avg_attempts_per_module"] = round(statistics.mean(attempts_per_module), 1) if attempts_per_module else 0
        
        # Calculate completion rate (% who completed at least one module)
        completed_count = sum(1 for m in modules_attempted if m > 0)
        metrics["completion_rate"] = round(completed_count / len(users), 2) if users else 0
        
        # Calculate standard deviation for mastery
        if len(mastery_scores) > 1:
            metrics["std_dev_mastery"] = round(statistics.stdev(mastery_scores), 3)
        
        return metrics
    
    def _identify_disparities(self, breakdown: Dict, category: DemographicCategory) -> List[DisparityAlert]:
        """Identify disparities within a category"""
        alerts = []
        
        if len(breakdown) < 2:
            return alerts  # Need at least 2 groups to compare
        
        # Find the best and worst performing groups for each metric
        metrics_to_check = ["avg_mastery", "completion_rate", "avg_modules_completed"]
        
        for metric in metrics_to_check:
            values = [(group, data.get(metric, 0)) for group, data in breakdown.items()]
            values.sort(key=lambda x: x[1])
            
            if len(values) >= 2:
                worst_group, worst_value = values[0]
                best_group, best_value = values[-1]
                
                # Check for significant disparity
                if best_value > 0:  # Avoid division by zero
                    gap = (best_value - worst_value) / best_value
                    
                    severity = None
                    if gap >= self.disparity_thresholds["high"]:
                        severity = "high"
                    elif gap >= self.disparity_thresholds["medium"]:
                        severity = "medium"
                    elif gap >= self.disparity_thresholds["low"]:
                        severity = "low"
                    
                    if severity:
                        alert = DisparityAlert(
                            category=category,
                            group_affected=worst_group,
                            metric=metric,
                            severity=severity,
                            description=f"{worst_group} group shows {round(gap*100, 1)}% lower {metric} compared to {best_group} group",
                            recommended_actions=self._generate_disparity_actions(category, worst_group, metric, severity)
                        )
                        alerts.append(alert)
        
        return alerts
    
    def _generate_disparity_actions(self, category: DemographicCategory, 
                                   affected_group: str, metric: str, severity: str) -> List[str]:
        """Generate recommended actions for addressing disparities"""
        actions = []
        
        if severity == "high":
            actions.append(f"Immediate intervention required for {affected_group} group")
            actions.append("Consider targeted support sessions or mentoring")
            
        if category == DemographicCategory.INSTITUTION_TYPE:
            if affected_group == "community":
                actions.append("Develop resources tailored for community hospital settings")
                actions.append("Consider asynchronous learning options")
            elif affected_group == "va":
                actions.append("Create VA-specific scenarios and examples")
                
        elif category == DemographicCategory.FELLOWSHIP_YEAR:
            if affected_group in ["4", "PGY4"]:
                actions.append("Increase foundational content and scaffolding")
                actions.append("Pair with senior fellows for peer learning")
                
        elif category == DemographicCategory.GEOGRAPHIC_REGION:
            actions.append(f"Schedule region-specific office hours for {affected_group}")
            actions.append("Check for time zone accessibility issues")
            
        if metric == "completion_rate":
            actions.append("Investigate barriers to engagement")
            actions.append("Consider shorter, more focused modules")
        elif metric == "avg_mastery":
            actions.append("Increase scaffolding and support materials")
            actions.append("Provide additional practice opportunities")
            
        return actions
    
    def _analyze_performance_gaps(self, users_data: List[Dict]) -> List[Dict]:
        """Analyze performance gaps across different dimensions"""
        gaps = []
        
        # Gap 1: Time to mastery variance
        time_to_mastery = []
        for user in users_data:
            avg_mastery = user.get('avg_mastery') or 0
            total_time = user.get('total_time') or 0
            if avg_mastery > 0.7 and total_time > 0:
                time_to_mastery.append(user['total_time'] / 3600)  # Convert to hours
        
        if len(time_to_mastery) > 2:
            avg_time = statistics.mean(time_to_mastery)
            std_time = statistics.stdev(time_to_mastery)
            
            gaps.append({
                "gap_type": "time_to_mastery_variance",
                "description": "High variance in time required to achieve mastery",
                "avg_hours": round(avg_time, 1),
                "std_dev_hours": round(std_time, 1),
                "impact": "Some learners require significantly more time",
                "recommendation": "Implement adaptive pacing and additional support for slower learners"
            })
        
        # Gap 2: Module completion disparities
        module_completion_by_user = [u.get('modules_attempted', 0) for u in users_data]
        if module_completion_by_user:
            completion_variance = max(module_completion_by_user) - min(module_completion_by_user)
            if completion_variance > 2:
                gaps.append({
                    "gap_type": "module_completion_disparity",
                    "description": "Large variation in module completion",
                    "range": [min(module_completion_by_user), max(module_completion_by_user)],
                    "impact": "Unequal exposure to curriculum",
                    "recommendation": "Investigate engagement barriers and provide completion incentives"
                })
        
        return gaps
    
    def _analyze_trends(self, users_data: List[Dict]) -> Dict:
        """Analyze trends in equity metrics over time"""
        trends = {
            "improving": [],
            "worsening": [],
            "stable": []
        }
        
        # This would ideally compare with historical data
        # For now, we'll analyze patterns in current data
        
        # Check if newer users (by last_active) perform differently
        if len(users_data) >= 10:
            sorted_by_activity = sorted(users_data, key=lambda x: x.get('last_active', ''))
            
            early_users = sorted_by_activity[:len(sorted_by_activity)//2]
            recent_users = sorted_by_activity[len(sorted_by_activity)//2:]
            
            early_mastery = statistics.mean([u.get('avg_mastery', 0) or 0 for u in early_users])
            recent_mastery = statistics.mean([u.get('avg_mastery', 0) or 0 for u in recent_users])
            
            if recent_mastery > early_mastery * 1.1:
                trends["improving"].append("Overall mastery scores improving for newer users")
            elif recent_mastery < early_mastery * 0.9:
                trends["worsening"].append("Overall mastery scores declining for newer users")
            else:
                trends["stable"].append("Mastery scores remain consistent")
        
        return trends
    
    def _generate_recommendations(self, report: EquityReport) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        # High-severity disparities
        high_severity = [d for d in report.disparities_found if d.severity == "high"]
        if high_severity:
            recommendations.append("PRIORITY: Address high-severity disparities immediately")
            for disparity in high_severity[:2]:  # Top 2 most severe
                recommendations.extend(disparity.recommended_actions[:2])
        
        # Performance gaps
        if report.performance_gaps:
            for gap in report.performance_gaps[:2]:  # Top 2 gaps
                recommendations.append(gap["recommendation"])
        
        # General recommendations based on patterns
        if len(report.disparities_found) > 3:
            recommendations.append("Implement systematic equity monitoring dashboard")
            recommendations.append("Establish equity goals and regular review process")
        
        # Positive reinforcement
        if report.trends.get("improving"):
            recommendations.append("Continue current improvement initiatives - positive trends observed")
        
        return recommendations[:7]  # Limit to 7 actionable recommendations
    
    def generate_dashboard_data(self) -> Dict:
        """Generate data for equity dashboard visualization"""
        report = self.analyze_equity(30)
        
        dashboard = {
            "summary": {
                "total_users": report.total_users,
                "disparity_count": len(report.disparities_found),
                "high_severity_count": len([d for d in report.disparities_found if d.severity == "high"]),
                "last_updated": report.timestamp.isoformat()
            },
            "charts": {
                "performance_by_institution": {},
                "performance_by_year": {},
                "time_to_mastery_distribution": {},
                "module_completion_rates": {}
            },
            "alerts": [],
            "recommendations": report.recommendations[:5]
        }
        
        # Prepare chart data
        if DemographicCategory.INSTITUTION_TYPE.value in report.demographic_breakdowns:
            inst_data = report.demographic_breakdowns[DemographicCategory.INSTITUTION_TYPE.value]
            dashboard["charts"]["performance_by_institution"] = {
                "labels": list(inst_data.keys()),
                "mastery": [d.get("avg_mastery", 0) for d in inst_data.values()],
                "completion": [d.get("completion_rate", 0) for d in inst_data.values()]
            }
        
        # Format alerts
        for disparity in report.disparities_found[:5]:  # Top 5 alerts
            dashboard["alerts"].append({
                "severity": disparity.severity,
                "category": disparity.category.value,
                "group": disparity.group_affected,
                "description": disparity.description,
                "timestamp": disparity.timestamp.isoformat()
            })
        
        return dashboard
    
    def export_equity_report(self, report: EquityReport, format: str = "json") -> str:
        """Export equity report in specified format"""
        if format == "json":
            # Convert to serializable format
            report_dict = {
                "timestamp": report.timestamp.isoformat(),
                "total_users": report.total_users,
                "demographic_breakdowns": report.demographic_breakdowns,
                "performance_gaps": report.performance_gaps,
                "disparities": [
                    {
                        "category": d.category.value,
                        "group_affected": d.group_affected,
                        "metric": d.metric,
                        "severity": d.severity,
                        "description": d.description,
                        "actions": d.recommended_actions
                    }
                    for d in report.disparities_found
                ],
                "trends": report.trends,
                "recommendations": report.recommendations
            }
            return json.dumps(report_dict, indent=2)
        
        elif format == "summary":
            # Human-readable summary
            summary = f"""
EQUITY ANALYSIS REPORT
Generated: {report.timestamp.strftime('%Y-%m-%d %H:%M')}
Total Users Analyzed: {report.total_users}

DISPARITIES IDENTIFIED: {len(report.disparities_found)}
High Severity: {len([d for d in report.disparities_found if d.severity == 'high'])}
Medium Severity: {len([d for d in report.disparities_found if d.severity == 'medium'])}
Low Severity: {len([d for d in report.disparities_found if d.severity == 'low'])}

TOP CONCERNS:
"""
            for i, disparity in enumerate(report.disparities_found[:3], 1):
                summary += f"{i}. {disparity.description} (Severity: {disparity.severity})\n"
            
            summary += "\nRECOMMENDATIONS:\n"
            for i, rec in enumerate(report.recommendations[:5], 1):
                summary += f"{i}. {rec}\n"
            
            return summary
        
        else:
            raise ValueError(f"Unsupported format: {format}")

# Global equity analytics instance
equity_analytics = EquityAnalytics()