"""
=============================================================================
AI INTERVIEW COACH SERVICE
=============================================================================

PURPOSE:
    Revolutionary AI-powered interview preparation and coaching platform.
    Provides personalized interview practice, real-time feedback, and
    company-specific preparation to dramatically improve interview success rates.

PROBLEM SOLVED:
    - Candidates fail interviews due to inadequate preparation
    - No access to personalized coaching and feedback
    - Generic interview advice doesn't address specific roles
    - Lack of practice with industry-specific questions
    - No objective assessment of interview performance

SOLUTION FEATURES:
    - AI-generated personalized interview questions
    - Real-time feedback on responses
    - Company-specific interview preparation
    - Behavioral and technical question practice
    - Performance analytics and improvement tracking
    - Negotiation coaching and salary guidance

=============================================================================
AUTHOR: SmartCareer AI Team
VERSION: 1.0.0
=============================================================================
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

from app.config import settings
from app.services.ai_service import AIService
from app.services.gemini_service import GeminiService


class InterviewType(Enum):
    """Types of interviews supported."""
    BEHAVIORAL = "behavioral"
    TECHNICAL = "technical"
    CASE_STUDY = "case_study"
    SYSTEM_DESIGN = "system_design"
    CULTURAL_FIT = "cultural_fit"
    PANEL = "panel"


class DifficultyLevel(Enum):
    """Interview difficulty levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class InterviewQuestion:
    """Interview question data structure."""
    id: str
    type: InterviewType
    difficulty: DifficultyLevel
    question: str
    context: str
    expected_answer_structure: str
    key_points_to_cover: List[str]
    common_mistakes: List[str]
    follow_up_questions: List[str]


@dataclass
class InterviewResponse:
    """User response analysis."""
    question_id: str
    user_answer: str
    ai_feedback: str
    score: int  # 0-100
    strengths: List[str]
    weaknesses: List[str]
    improvements: List[str]
    suggested_answer: str
    key_points_missed: List[str]
    communication_score: int
    content_score: int
    confidence_score: int


@dataclass
class InterviewSession:
    """Complete interview session data."""
    session_id: str
    user_id: str
    job_title: str
    company: str
    interview_type: InterviewType
    difficulty_level: DifficultyLevel
    questions: List[InterviewQuestion]
    responses: List[InterviewResponse]
    overall_score: int
    session_duration: int  # minutes
    completed_at: datetime
    recommendations: List[str]
    next_steps: List[str]


@dataclass
class CompanyIntelligence:
    """Company-specific interview intelligence."""
    company_name: str
    industry: str
    interview_style: str
    common_questions: List[str]
    company_values: List[str]
    recent_news: List[str]
    interview_tips: List[str]
    salary_range: Tuple[int, int]
    negotiation_strategy: str


class InterviewCoachService:
    """
    Enterprise-grade AI interview coaching platform.

    Features:
    - Personalized interview question generation
    - Real-time response analysis and feedback
    - Company-specific preparation intelligence
    - Performance tracking and improvement analytics
    - Negotiation coaching and salary guidance
    """

    def __init__(self):
        """Initialize interview coach with AI services."""
        self.ai_service = AIService()
        self.gemini_service = GeminiService()

        # Interview patterns and best practices
        self.interview_patterns = self._load_interview_patterns()

        # Company intelligence database
        self.company_intelligence = self._load_company_intelligence()

    def _load_interview_patterns(self) -> Dict[str, Any]:
        """Load interview patterns and question templates."""
        return {
            "behavioral": {
                "star_method": "Situation, Task, Action, Result",
                "question_starters": [
                    "Tell me about a time when...",
                    "Describe a situation where...",
                    "Give me an example of...",
                    "How did you handle..."
                ],
                "evaluation_criteria": [
                    "Specificity of examples",
                    "Problem-solving approach",
                    "Impact measurement",
                    "Lessons learned"
                ]
            },
            "technical": {
                "coding_languages": ["python", "javascript", "java", "c++", "go", "rust"],
                "system_design_principles": [
                    "scalability", "reliability", "security", "performance",
                    "maintainability", "cost-effectiveness"
                ],
                "evaluation_criteria": [
                    "Technical accuracy",
                    "Solution completeness",
                    "Trade-off analysis",
                    "Communication clarity"
                ]
            }
        }

    def _load_company_intelligence(self) -> Dict[str, CompanyIntelligence]:
        """Load company-specific interview intelligence."""
        # This would typically come from a database
        return {
            "google": CompanyIntelligence(
                company_name="Google",
                industry="Technology",
                interview_style="Data-driven and analytical",
                common_questions=[
                    "How would you design a search engine?",
                    "Explain a complex technical concept to a 5-year-old",
                    "Tell me about a time you dealt with ambiguity"
                ],
                company_values=["Innovation", "User Focus", "Sustainability"],
                recent_news=["AI initiatives", "Sustainability goals", "Workforce expansion"],
                interview_tips=[
                    "Focus on data and metrics",
                    "Demonstrate problem-solving approach",
                    "Show cultural fit with company values"
                ],
                salary_range=(150000, 300000),
                negotiation_strategy="Focus on impact and market rate"
            ),
            "amazon": CompanyIntelligence(
                company_name="Amazon",
                industry="E-commerce",
                interview_style="Leadership principles focused",
                common_questions=[
                    "Tell me about a time you failed and what you learned",
                    "How do you handle conflicting priorities?",
                    "Describe your most innovative solution"
                ],
                company_values=["Customer Obsession", "Ownership", "Invent and Simplify"],
                recent_news=["AWS expansion", "Sustainability initiatives", "Remote work policies"],
                interview_tips=[
                    "Reference Amazon's leadership principles",
                    "Show ownership and accountability",
                    "Demonstrate customer-focused thinking"
                ],
                salary_range=(120000, 250000),
                negotiation_strategy="Emphasize business impact and leadership"
            )
        }

    async def generate_interview_session(
        self,
        user_id: str,
        job_title: str,
        company: str,
        experience_level: str = "mid",
        interview_types: List[str] = None,
        session_duration: int = 60
    ) -> InterviewSession:
        """
        Generate a personalized interview session.

        Args:
            user_id: User identifier
            job_title: Target job position
            company: Target company
            experience_level: junior, mid, senior, executive
            interview_types: Types of interviews to include
            session_duration: Session length in minutes

        Returns:
            Complete interview session with questions
        """
        if interview_types is None:
            interview_types = ["behavioral", "technical"]

        # Determine difficulty level
        difficulty_map = {
            "junior": DifficultyLevel.BEGINNER,
            "mid": DifficultyLevel.INTERMEDIATE,
            "senior": DifficultyLevel.ADVANCED,
            "executive": DifficultyLevel.EXPERT
        }
        difficulty = difficulty_map.get(experience_level, DifficultyLevel.INTERMEDIATE)

        # Generate questions for each type
        questions = []
        for interview_type in interview_types:
            type_questions = await self._generate_questions_for_type(
                InterviewType(interview_type), difficulty, job_title, company
            )
            questions.extend(type_questions)

        # Create session
        session = InterviewSession(
            session_id=f"interview_{user_id}_{int(datetime.now(timezone.utc).timestamp())}",
            user_id=user_id,
            job_title=job_title,
            company=company,
            interview_type=InterviewType.BEHAVIORAL,  # Primary type
            difficulty_level=difficulty,
            questions=questions,
            responses=[],
            overall_score=0,
            session_duration=session_duration,
            completed_at=datetime.now(timezone.utc),
            recommendations=[],
            next_steps=[]
        )

        return session

    async def _generate_questions_for_type(
        self,
        interview_type: InterviewType,
        difficulty: DifficultyLevel,
        job_title: str,
        company: str
    ) -> List[InterviewQuestion]:
        """Generate questions for specific interview type."""
        prompt = f"""
        Generate 3 personalized interview questions for a {job_title} position at {company}.

        Interview Type: {interview_type.value}
        Difficulty Level: {difficulty.value}

        For each question, provide:
        1. The question text
        2. Context/background information
        3. Expected answer structure
        4. Key points to cover
        5. Common mistakes to avoid
        6. 2 follow-up questions

        Make questions specific to {company}'s industry and the {job_title} role.
        Ensure questions test real-world application of skills.

        Return as JSON array of question objects.
        """

        try:
            response = await self.ai_service.generate_response(
                prompt=prompt,
                max_tokens=1500,
                temperature=0.7
            )

            # Parse JSON response
            questions_data = json.loads(response)

            questions = []
            for i, q_data in enumerate(questions_data):
                question = InterviewQuestion(
                    id=f"{interview_type.value}_{i+1}",
                    type=interview_type,
                    difficulty=difficulty,
                    question=q_data.get("question", ""),
                    context=q_data.get("context", ""),
                    expected_answer_structure=q_data.get("expected_answer_structure", ""),
                    key_points_to_cover=q_data.get("key_points_to_cover", []),
                    common_mistakes=q_data.get("common_mistakes", []),
                    follow_up_questions=q_data.get("follow_up_questions", [])
                )
                questions.append(question)

            return questions

        except Exception:
            # Fallback questions
            return [
                InterviewQuestion(
                    id=f"{interview_type.value}_fallback_1",
                    type=interview_type,
                    difficulty=difficulty,
                    question=f"Tell me about your experience with {job_title} responsibilities.",
                    context=f"Standard question for {job_title} positions at {company}.",
                    expected_answer_structure="Describe situation, actions taken, and results achieved.",
                    key_points_to_cover=["Experience level", "Key achievements", "Lessons learned"],
                    common_mistakes=["Being too vague", "Not quantifying impact"],
                    follow_up_questions=[
                        "What challenges did you face?",
                        "How did this experience prepare you for this role?"
                    ]
                )
            ]

    async def analyze_response(
        self,
        question: InterviewQuestion,
        user_answer: str,
        job_title: str,
        company: str
    ) -> InterviewResponse:
        """
        Analyze user's interview response and provide detailed feedback.

        Args:
            question: The interview question
            user_answer: User's response
            job_title: Target position
            company: Target company

        Returns:
            Detailed analysis and feedback
        """
        prompt = f"""
        Analyze this interview response and provide detailed feedback:

        QUESTION: {question.question}
        USER ANSWER: {user_answer}

        Position: {job_title} at {company}
        Interview Type: {question.type.value}
        Difficulty: {question.difficulty.value}

        Provide analysis in this JSON format:
        {{
            "score": 0-100,
            "feedback": "Overall assessment",
            "strengths": ["strength1", "strength2"],
            "weaknesses": ["weakness1", "weakness2"],
            "improvements": ["improvement1", "improvement2"],
            "suggested_answer": "Better version of the answer",
            "key_points_missed": ["point1", "point2"],
            "communication_score": 0-100,
            "content_score": 0-100,
            "confidence_score": 0-100
        }}

        Be specific, constructive, and actionable in your feedback.
        """

        try:
            response = await self.ai_service.generate_response(
                prompt=prompt,
                max_tokens=1200,
                temperature=0.3
            )

            analysis = json.loads(response)

            return InterviewResponse(
                question_id=question.id,
                user_answer=user_answer,
                ai_feedback=analysis.get("feedback", "Analysis unavailable"),
                score=analysis.get("score", 50),
                strengths=analysis.get("strengths", []),
                weaknesses=analysis.get("weaknesses", []),
                improvements=analysis.get("improvements", []),
                suggested_answer=analysis.get("suggested_answer", ""),
                key_points_missed=analysis.get("key_points_missed", []),
                communication_score=analysis.get("communication_score", 50),
                content_score=analysis.get("content_score", 50),
                confidence_score=analysis.get("confidence_score", 50)
            )

        except Exception:
            # Fallback analysis
            return InterviewResponse(
                question_id=question.id,
                user_answer=user_answer,
                ai_feedback="Unable to analyze response. Please try again.",
                score=50,
                strengths=["Attempted to answer the question"],
                weaknesses=["Analysis unavailable"],
                improvements=["Try rephrasing your answer"],
                suggested_answer="Please provide a more detailed response.",
                key_points_missed=[],
                communication_score=50,
                content_score=50,
                confidence_score=50
            )

    async def get_company_intelligence(self, company_name: str) -> CompanyIntelligence:
        """
        Get company-specific interview intelligence.

        Args:
            company_name: Name of the company

        Returns:
            Company intelligence data
        """
        # Check if we have cached intelligence
        if company_name.lower() in self.company_intelligence:
            return self.company_intelligence[company_name.lower()]

        # Generate new intelligence using AI
        prompt = f"""
        Provide detailed interview intelligence for {company_name}:

        Include:
        1. Industry and company overview
        2. Interview style and approach
        3. 5 common interview questions
        4. Company values and culture
        5. Recent news or initiatives
        6. Specific interview tips
        7. Salary range for software engineering roles
        8. Negotiation strategy

        Return as JSON with these keys: industry, interview_style, common_questions,
        company_values, recent_news, interview_tips, salary_range, negotiation_strategy.
        """

        try:
            response = await self.ai_service.generate_response(
                prompt=prompt,
                max_tokens=1000,
                temperature=0.4
            )

            data = json.loads(response)

            intelligence = CompanyIntelligence(
                company_name=company_name,
                industry=data.get("industry", "Technology"),
                interview_style=data.get("interview_style", "Standard technical interview"),
                common_questions=data.get("common_questions", []),
                company_values=data.get("company_values", []),
                recent_news=data.get("recent_news", []),
                interview_tips=data.get("interview_tips", []),
                salary_range=tuple(data.get("salary_range", [80000, 150000])),
                negotiation_strategy=data.get("negotiation_strategy", "Focus on market rate and your value")
            )

            # Cache for future use
            self.company_intelligence[company_name.lower()] = intelligence

            return intelligence

        except Exception:
            # Return generic intelligence
            return CompanyIntelligence(
                company_name=company_name,
                industry="Technology",
                interview_style="Standard technical interview",
                common_questions=[
                    "Tell me about yourself",
                    "Why do you want to work here?",
                    "What are your strengths and weaknesses?"
                ],
                company_values=["Innovation", "Teamwork", "Excellence"],
                recent_news=[],
                interview_tips=[
                    "Research the company thoroughly",
                    "Prepare specific examples",
                    "Ask thoughtful questions"
                ],
                salary_range=(70000, 140000),
                negotiation_strategy="Research market rates and be prepared to discuss your value"
            )

    async def generate_negotiation_coach(
        self,
        job_title: str,
        company: str,
        current_offer: Dict[str, Any],
        user_experience: str
    ) -> Dict[str, Any]:
        """
        Generate salary negotiation coaching and strategy.

        Args:
            job_title: Position title
            company: Company name
            current_offer: Current offer details
            user_experience: User's experience level

        Returns:
            Negotiation strategy and talking points
        """
        prompt = f"""
        Create a comprehensive salary negotiation strategy:

        Position: {job_title}
        Company: {company}
        Current Offer: {json.dumps(current_offer)}
        Experience Level: {user_experience}

        Provide:
        1. Market rate analysis
        2. Negotiation strategy
        3. Talking points
        4. Counter-offer suggestions
        5. Benefits to consider
        6. Walk-away points

        Return as JSON with keys: market_analysis, strategy, talking_points,
        counter_offer_suggestions, benefits_to_consider, walk_away_points.
        """

        try:
            response = await self.ai_service.generate_response(
                prompt=prompt,
                max_tokens=1000,
                temperature=0.3
            )

            return json.loads(response)

        except Exception:
            return {
                "market_analysis": "Research current market rates for similar positions",
                "strategy": "Focus on your value and market demand",
                "talking_points": ["Highlight your experience", "Mention market research"],
                "counter_offer_suggestions": ["Request 10-20% increase", "Ask for better benefits"],
                "benefits_to_consider": ["Health insurance", "Retirement contributions", "PTO"],
                "walk_away_points": ["If offer is below 80% of market rate", "Poor company culture"]
            }

    async def generate_performance_report(
        self,
        session: InterviewSession
    ) -> Dict[str, Any]:
        """
        Generate comprehensive performance report for interview session.

        Args:
            session: Completed interview session

        Returns:
            Detailed performance analysis
        """
        prompt = f"""
        Analyze this interview session performance:

        Session Data:
        - Position: {session.job_title}
        - Company: {session.company}
        - Duration: {session.session_duration} minutes
        - Questions Answered: {len(session.responses)}
        - Average Score: {session.overall_score}%

        Response Scores: {[r.score for r in session.responses]}

        Generate a comprehensive performance report including:
        1. Overall assessment
        2. Strengths identified
        3. Areas for improvement
        4. Specific recommendations
        5. Preparation plan for next interview
        6. Confidence level assessment

        Return as JSON with keys: overall_assessment, strengths, improvements,
        recommendations, preparation_plan, confidence_level.
        """

        try:
            response = await self.ai_service.generate_response(
                prompt=prompt,
                max_tokens=1200,
                temperature=0.4
            )

            return json.loads(response)

        except Exception:
            return {
                "overall_assessment": f"Completed {len(session.responses)} interview questions with average score of {session.overall_score}%",
                "strengths": ["Completed the practice session", "Engaged with the process"],
                "improvements": ["Practice more questions", "Focus on structure"],
                "recommendations": ["Review feedback carefully", "Practice regularly"],
                "preparation_plan": ["Daily practice sessions", "Research company", "Prepare stories"],
                "confidence_level": "Developing - keep practicing"
            }


# Singleton instance
interview_coach = InterviewCoachService()
