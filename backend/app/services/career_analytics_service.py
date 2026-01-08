"""
=============================================================================
CAREER ANALYTICS SERVICE
=============================================================================

PURPOSE:
    Advanced career analytics and development platform providing data-driven
    insights, personalized career roadmaps, and predictive analytics for
    career success. Revolutionary approach that transforms career planning
    from guesswork to data-driven strategy.

PROBLEM SOLVED:
    - Career planning based on intuition rather than data
    - No visibility into career progression metrics
    - Lack of personalized development recommendations
    - Generic career advice not tailored to individual goals
    - No predictive analytics for career success

SOLUTION FEATURES:
    - Personalized career trajectory forecasting
    - Skills gap analysis with learning recommendations
    - Market trend analysis and salary predictions
    - Performance tracking across multiple applications
    - ROI calculation for career investments
    - Network strength analysis and recommendations

=============================================================================
AUTHOR: SmartCareer AI Team
VERSION: 1.0.0
=============================================================================
"""

import json
import statistics
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from collections import defaultdict

from app.config import settings
from app.services.ai_service import AIService
from app.services.gemini_service import GeminiService


@dataclass
class CareerMetrics:
    """Career performance metrics."""
    applications_submitted: int
    interviews_scheduled: int
    offers_received: int
    rejections_received: int
    average_response_time: float  # days
    interview_success_rate: float  # percentage
    offer_acceptance_rate: float  # percentage
    applications_per_week: float
    network_strength_score: int  # 0-100


@dataclass
class SkillGap:
    """Skills gap analysis result."""
    skill_name: str
    current_level: int  # 1-10
    required_level: int  # 1-10
    gap_size: int  # difference
    priority: str  # high, medium, low
    recommended_resources: List[str]
    estimated_learning_time: int  # weeks
    market_demand: str  # high, medium, low


@dataclass
class CareerPrediction:
    """Career trajectory prediction."""
    timeline_months: int
    predicted_salary: float
    confidence_score: int  # 0-100
    key_milestones: List[str]
    required_skills: List[str]
    market_factors: List[str]
    risk_factors: List[str]


@dataclass
class PersonalizedRoadmap:
    """Personalized career development roadmap."""
    career_goal: str
    timeline_months: int
    current_position: str
    target_position: str
    skill_gaps: List[SkillGap]
    learning_path: List[Dict[str, Any]]
    networking_goals: List[str]
    monthly_milestones: List[str]
    success_metrics: List[str]
    contingency_plans: List[str]


class CareerAnalyticsService:
    """
    Enterprise-grade career analytics and development platform.

    Features:
    - Data-driven career insights and predictions
    - Personalized skill development roadmaps
    - Performance analytics and ROI tracking
    - Market trend analysis and salary forecasting
    - Network optimization recommendations
    """

    def __init__(self):
        """Initialize career analytics service."""
        self.ai_service = AIService()
        self.gemini_service = GeminiService()

        # Market data and trends
        self.market_data = self._load_market_data()

        # Skills database with demand metrics
        self.skills_database = self._load_skills_database()

    def _load_market_data(self) -> Dict[str, Any]:
        """Load market trends and salary data."""
        return {
            "salary_trends": {
                "software_engineer": {
                    "junior": 75000,
                    "mid": 110000,
                    "senior": 160000,
                    "lead": 200000
                },
                "product_manager": {
                    "junior": 90000,
                    "mid": 130000,
                    "senior": 180000,
                    "director": 220000
                },
                "data_scientist": {
                    "junior": 85000,
                    "mid": 120000,
                    "senior": 170000,
                    "lead": 210000
                }
            },
            "growth_rates": {
                "technology": 0.08,  # 8% annual growth
                "healthcare": 0.05,
                "finance": 0.06,
                "education": 0.03
            },
            "remote_work_trends": {
                "software_engineer": 0.85,  # 85% remote-friendly
                "product_manager": 0.75,
                "data_scientist": 0.80
            }
        }

    def _load_skills_database(self) -> Dict[str, Dict[str, Any]]:
        """Load skills database with demand and learning metrics."""
        return {
            "python": {
                "demand": "high",
                "avg_learning_time": 12,  # weeks
                "difficulty": "medium",
                "salary_premium": 15000,
                "related_roles": ["data scientist", "backend developer", "ml engineer"]
            },
            "machine_learning": {
                "demand": "very_high",
                "avg_learning_time": 24,
                "difficulty": "hard",
                "salary_premium": 25000,
                "related_roles": ["ml engineer", "data scientist", "ai researcher"]
            },
            "react": {
                "demand": "high",
                "avg_learning_time": 8,
                "difficulty": "medium",
                "salary_premium": 12000,
                "related_roles": ["frontend developer", "fullstack developer"]
            },
            "aws": {
                "demand": "very_high",
                "avg_learning_time": 16,
                "difficulty": "medium",
                "salary_premium": 20000,
                "related_roles": ["cloud engineer", "devops engineer", "backend developer"]
            },
            "leadership": {
                "demand": "high",
                "avg_learning_time": 52,  # 1 year
                "difficulty": "hard",
                "salary_premium": 30000,
                "related_roles": ["manager", "director", "executive"]
            }
        }

    async def calculate_career_metrics(
        self,
        user_id: str,
        application_history: List[Dict[str, Any]],
        time_period_days: int = 90
    ) -> CareerMetrics:
        """
        Calculate comprehensive career performance metrics.

        Args:
            user_id: User identifier
            application_history: List of application records
            time_period_days: Analysis period in days

        Returns:
            Career performance metrics
        """
        # Filter applications by time period
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=time_period_days)
        recent_applications = [
            app for app in application_history
            if datetime.fromisoformat(app.get('created_at', '2020-01-01')) > cutoff_date
        ]

        if not recent_applications:
            return CareerMetrics(
                applications_submitted=0,
                interviews_scheduled=0,
                offers_received=0,
                rejections_received=0,
                average_response_time=0,
                interview_success_rate=0,
                offer_acceptance_rate=0,
                applications_per_week=0,
                network_strength_score=0
            )

        # Calculate metrics
        total_applications = len(recent_applications)

        interviews = [app for app in recent_applications if app.get('status') in ['interview_scheduled', 'interviewed']]
        offers = [app for app in recent_applications if app.get('status') == 'offer_received']
        rejections = [app for app in recent_applications if app.get('status') == 'rejected']

        # Calculate response times
        response_times = []
        for app in recent_applications:
            if app.get('updated_at') and app.get('created_at'):
                created = datetime.fromisoformat(app['created_at'])
                updated = datetime.fromisoformat(app['updated_at'])
                if updated > created:
                    response_times.append((updated - created).days)

        avg_response_time = statistics.mean(response_times) if response_times else 0

        # Calculate rates
        interview_success_rate = (len(interviews) / total_applications) * 100 if total_applications > 0 else 0
        offer_acceptance_rate = (len(offers) / len(interviews)) * 100 if interviews else 0

        # Applications per week
        weeks_in_period = time_period_days / 7
        applications_per_week = total_applications / weeks_in_period if weeks_in_period > 0 else 0

        # Network strength (simplified calculation)
        network_score = min(100, (len(interviews) * 10) + (len(offers) * 20))

        return CareerMetrics(
            applications_submitted=total_applications,
            interviews_scheduled=len(interviews),
            offers_received=len(offers),
            rejections_received=len(rejections),
            average_response_time=round(avg_response_time, 1),
            interview_success_rate=round(interview_success_rate, 1),
            offer_acceptance_rate=round(offer_acceptance_rate, 1),
            applications_per_week=round(applications_per_week, 1),
            network_strength_score=network_score
        )

    async def analyze_skill_gaps(
        self,
        current_skills: Dict[str, int],  # skill_name -> proficiency_level (1-10)
        target_role: str,
        industry: str
    ) -> List[SkillGap]:
        """
        Analyze skills gaps and provide learning recommendations.

        Args:
            current_skills: User's current skill levels
            target_role: Target job position
            industry: Target industry

        Returns:
            List of skill gaps with recommendations
        """
        prompt = f"""
        Analyze skill gaps for a {target_role} position in {industry}:

        Current Skills: {json.dumps(current_skills, indent=2)}
        Target Role: {target_role}
        Industry: {industry}

        Identify the top 5 most important skills for this role that the user needs to develop.
        For each skill, provide:
        1. Required proficiency level (1-10)
        2. Learning priority (high/medium/low)
        3. Recommended learning resources
        4. Estimated learning time in weeks
        5. Market demand level

        Return as JSON array of skill gap objects.
        """

        try:
            response = await self.ai_service.generate_response(
                prompt=prompt,
                max_tokens=1200,
                temperature=0.3
            )

            gaps_data = json.loads(response)

            skill_gaps = []
            for gap_data in gaps_data:
                skill_name = gap_data.get('skill_name', '')
                required_level = gap_data.get('required_level', 5)
                current_level = current_skills.get(skill_name, 1)
                gap_size = required_level - current_level

                skill_gap = SkillGap(
                    skill_name=skill_name,
                    current_level=current_level,
                    required_level=required_level,
                    gap_size=max(0, gap_size),
                    priority=gap_data.get('priority', 'medium'),
                    recommended_resources=gap_data.get('recommended_resources', []),
                    estimated_learning_time=gap_data.get('estimated_learning_time', 8),
                    market_demand=gap_data.get('market_demand', 'medium')
                )
                skill_gaps.append(skill_gap)

            return skill_gaps

        except Exception:
            # Fallback skill gaps based on common requirements
            return [
                SkillGap(
                    skill_name="Communication",
                    current_level=current_skills.get("communication", 3),
                    required_level=7,
                    gap_size=4,
                    priority="high",
                    recommended_resources=["Toastmasters", "LinkedIn Learning courses"],
                    estimated_learning_time=12,
                    market_demand="high"
                ),
                SkillGap(
                    skill_name="Technical Skills",
                    current_level=current_skills.get("technical", 4),
                    required_level=8,
                    gap_size=4,
                    priority="high",
                    recommended_resources=["Coursera", "Udacity", "Pluralsight"],
                    estimated_learning_time=24,
                    market_demand="very_high"
                )
            ]

    async def generate_career_roadmap(
        self,
        current_position: str,
        target_position: str,
        current_skills: Dict[str, int],
        years_experience: int,
        career_goal: str,
        industry: str
    ) -> PersonalizedRoadmap:
        """
        Generate personalized career development roadmap.

        Args:
            current_position: Current job title
            target_position: Desired job title
            current_skills: Current skill levels
            years_experience: Years of experience
            career_goal: Long-term career objective
            industry: Target industry

        Returns:
            Comprehensive career development roadmap
        """
        prompt = f"""
        Create a personalized career development roadmap:

        Current Position: {current_position}
        Target Position: {target_position}
        Current Skills: {json.dumps(current_skills, indent=2)}
        Years Experience: {years_experience}
        Career Goal: {career_goal}
        Industry: {industry}

        Generate a comprehensive roadmap including:
        1. Timeline in months
        2. Key skill gaps to address
        3. Learning path with specific courses/resources
        4. Networking goals and activities
        5. Monthly milestones and checkpoints
        6. Success metrics and KPIs
        7. Contingency plans for setbacks

        Return as JSON with keys: timeline_months, skill_gaps, learning_path,
        networking_goals, monthly_milestones, success_metrics, contingency_plans.
        """

        try:
            response = await self.ai_service.generate_response(
                prompt=prompt,
                max_tokens=1500,
                temperature=0.4
            )

            roadmap_data = json.loads(response)

            # Analyze skill gaps
            skill_gaps = await self.analyze_skill_gaps(current_skills, target_position, industry)

            roadmap = PersonalizedRoadmap(
                career_goal=career_goal,
                timeline_months=roadmap_data.get('timeline_months', 24),
                current_position=current_position,
                target_position=target_position,
                skill_gaps=skill_gaps,
                learning_path=roadmap_data.get('learning_path', []),
                networking_goals=roadmap_data.get('networking_goals', []),
                monthly_milestones=roadmap_data.get('monthly_milestones', []),
                success_metrics=roadmap_data.get('success_metrics', []),
                contingency_plans=roadmap_data.get('contingency_plans', [])
            )

            return roadmap

        except Exception:
            # Fallback roadmap
            skill_gaps = await self.analyze_skill_gaps(current_skills, target_position, industry)

            return PersonalizedRoadmap(
                career_goal=career_goal,
                timeline_months=24,
                current_position=current_position,
                target_position=target_position,
                skill_gaps=skill_gaps,
                learning_path=[
                    {"month": 1, "focus": "Skill assessment", "resources": ["Online courses"]},
                    {"month": 6, "focus": "Core skills development", "resources": ["Specialized training"]},
                    {"month": 12, "focus": "Advanced skills", "resources": ["Industry certifications"]},
                    {"month": 18, "focus": "Leadership development", "resources": ["Mentorship programs"]},
                    {"month": 24, "focus": "Career transition", "resources": ["Networking events"]}
                ],
                networking_goals=[
                    "Attend 2 industry conferences",
                    "Join 3 professional groups",
                    "Connect with 50 industry professionals"
                ],
                monthly_milestones=[
                    "Complete skill assessment",
                    "Start learning plan",
                    "Network with 5 professionals",
                    "Update resume and LinkedIn",
                    "Apply to target positions"
                ],
                success_metrics=[
                    "Complete 80% of learning objectives",
                    "Expand network by 25 contacts",
                    "Receive positive feedback on applications",
                    "Achieve target skill levels"
                ],
                contingency_plans=[
                    "If progress is slow, reduce scope and focus on high-impact skills",
                    "Network through existing connections if events are unavailable",
                    "Consider freelance projects to build portfolio"
                ]
            )

    async def predict_career_trajectory(
        self,
        current_position: str,
        years_experience: int,
        current_salary: float,
        target_position: str,
        industry: str,
        performance_metrics: Dict[str, Any]
    ) -> List[CareerPrediction]:
        """
        Predict career trajectory with multiple scenarios.

        Args:
            current_position: Current job title
            years_experience: Years of experience
            current_salary: Current annual salary
            target_position: Target position
            industry: Industry
            performance_metrics: Career performance data

        Returns:
            List of career trajectory predictions
        """
        predictions = []

        # Generate 3 different scenarios
        scenarios = [
            {"name": "Conservative", "growth_rate": 0.03, "confidence": 80},
            {"name": "Moderate", "growth_rate": 0.06, "confidence": 60},
            {"name": "Aggressive", "growth_rate": 0.10, "confidence": 40}
        ]

        for scenario in scenarios:
            # Predict salary progression
            base_salary = self.market_data["salary_trends"].get(target_position, {}).get("mid", current_salary)

            # Adjust for experience and performance
            experience_multiplier = min(2.0, 1 + (years_experience * 0.1))
            performance_multiplier = 1 + (performance_metrics.get("interview_success_rate", 50) / 100 * 0.2)

            predicted_salary = base_salary * experience_multiplier * performance_multiplier

            # Apply growth rate over time
            timeline_months = 24
            growth_factor = (1 + scenario["growth_rate"]) ** (timeline_months / 12)
            final_salary = predicted_salary * growth_factor

            # Generate milestones and requirements
            milestones = [
                f"Achieve {target_position} role",
                "Complete advanced certifications",
                "Build strong professional network",
                f"Reach ${(final_salary * 0.7):,.0f} salary milestone"
            ]

            required_skills = [
                "Advanced technical skills",
                "Leadership and communication",
                "Industry-specific expertise",
                "Project management experience"
            ]

            market_factors = [
                f"{industry} industry growth",
                "Remote work trends",
                "Economic conditions",
                "Company hiring patterns"
            ]

            risk_factors = [
                "Economic downturns",
                "Industry disruption",
                "Competition for roles",
                "Skill obsolescence"
            ]

            prediction = CareerPrediction(
                timeline_months=timeline_months,
                predicted_salary=round(final_salary, 2),
                confidence_score=scenario["confidence"],
                key_milestones=milestones,
                required_skills=required_skills,
                market_factors=market_factors,
                risk_factors=risk_factors
            )

            predictions.append(prediction)

        return predictions

    async def calculate_career_roi(
        self,
        career_investments: List[Dict[str, Any]],
        career_outcomes: List[Dict[str, Any]],
        time_period_years: int = 5
    ) -> Dict[str, Any]:
        """
        Calculate ROI for career development investments.

        Args:
            career_investments: List of career investments (courses, certifications, etc.)
            career_outcomes: List of career outcomes (salary increases, promotions, etc.)
            time_period_years: Analysis period

        Returns:
            Career ROI analysis
        """
        # Calculate total investment
        total_investment = sum(investment.get('cost', 0) for investment in career_investments)

        # Calculate total returns (salary increases, bonuses, etc.)
        total_returns = sum(outcome.get('value', 0) for outcome in career_outcomes)

        # Calculate time-weighted ROI
        if total_investment > 0:
            roi_percentage = ((total_returns - total_investment) / total_investment) * 100
            annual_roi = roi_percentage / time_period_years if time_period_years > 0 else 0
        else:
            roi_percentage = 0
            annual_roi = 0

        # Calculate payback period
        cumulative_returns = 0
        payback_months = 0

        for outcome in career_outcomes:
            cumulative_returns += outcome.get('value', 0)
            payback_months += 1
            if cumulative_returns >= total_investment:
                break

        return {
            "total_investment": total_investment,
            "total_returns": total_returns,
            "net_return": total_returns - total_investment,
            "roi_percentage": round(roi_percentage, 2),
            "annual_roi_percentage": round(annual_roi, 2),
            "payback_period_months": payback_months,
            "break_even_achieved": cumulative_returns >= total_investment,
            "investment_breakdown": career_investments,
            "outcome_breakdown": career_outcomes,
            "recommendations": [
                "Continue investing in high-ROI skills",
                "Track all career development expenses",
                "Measure impact of each investment",
                "Focus on skills with highest market demand"
            ]
        }

    async def generate_market_insights(
        self,
        role: str,
        location: str,
        industry: str
    ) -> Dict[str, Any]:
        """
        Generate market insights for specific role and location.

        Args:
            role: Job role
            location: Geographic location
            industry: Industry sector

        Returns:
            Comprehensive market analysis
        """
        prompt = f"""
        Generate market insights for {role} in {location} within {industry}:

        Provide analysis on:
        1. Current salary ranges and trends
        2. Job market demand and growth
        3. Required skills and qualifications
        4. Competition level
        5. Remote work opportunities
        6. Future outlook and predictions
        7. Negotiation leverage factors

        Return as JSON with keys: salary_ranges, market_demand, required_skills,
        competition_level, remote_work_available, future_outlook, negotiation_factors.
        """

        try:
            response = await self.ai_service.generate_response(
                prompt=prompt,
                max_tokens=1000,
                temperature=0.3
            )

            insights = json.loads(response)

            # Add market data from our database
            salary_data = self.market_data["salary_trends"].get(role, {})
            insights["salary_data_from_database"] = salary_data

            return insights

        except Exception:
            # Fallback insights
            return {
                "salary_ranges": {
                    "entry": 60000,
                    "mid": 90000,
                    "senior": 130000,
                    "lead": 170000
                },
                "market_demand": "High",
                "required_skills": ["Technical skills", "Communication", "Problem-solving"],
                "competition_level": "Medium",
                "remote_work_available": True,
                "future_outlook": "Positive growth expected",
                "negotiation_factors": ["Experience level", "Skill set", "Market demand"]
            }


# Singleton instance
career_analytics = CareerAnalyticsService()
