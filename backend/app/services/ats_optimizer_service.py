"""
=============================================================================
ATS OPTIMIZER SERVICE
=============================================================================

PURPOSE:
    Advanced AI-powered ATS (Applicant Tracking System) optimization service.
    Analyzes resumes and job descriptions to maximize ATS compatibility and
    pass-through rates. Revolutionary approach that solves the #1 problem
    in job searching.

PROBLEM SOLVED:
    - 75% of qualified candidates are rejected by ATS before human review
    - Generic resumes fail ATS keyword matching
    - Poor formatting causes parsing errors
    - Lack of industry-specific optimization

SOLUTION FEATURES:
    - AI-powered keyword optimization
    - ATS-compatible formatting
    - Industry-specific terminology
    - Parsing error detection and correction
    - Real-time ATS score calculation

=============================================================================
AUTHOR: SmartCareer AI Team
VERSION: 1.0.0
=============================================================================
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone

from app.config import settings
from app.services.ai_service import AIService
from app.services.gemini_service import GeminiService


@dataclass
class ATSAnalysis:
    """ATS analysis results data structure."""
    overall_score: int  # 0-100
    keyword_match_score: int  # 0-100
    format_score: int  # 0-100
    readability_score: int  # 0-100
    industry_alignment_score: int  # 0-100

    keyword_optimization: Dict[str, Any]
    format_issues: List[str]
    readability_improvements: List[str]
    industry_recommendations: List[str]

    ats_friendly_resume: str
    critical_missing_keywords: List[str]
    recommended_additions: List[str]

    parsing_errors: List[str]
    ats_compatibility_warnings: List[str]


class ATSOptimizerService:
    """
    Enterprise-grade ATS optimization service.

    Features:
    - AI-powered keyword extraction and optimization
    - ATS parsing simulation and error detection
    - Industry-specific terminology matching
    - Resume formatting for maximum ATS compatibility
    - Real-time scoring and improvement suggestions
    """

    def __init__(self):
        """Initialize ATS optimizer with AI services."""
        self.ai_service = AIService()
        self.gemini_service = GeminiService()

        # ATS keywords database by industry
        self.ats_keywords = self._load_ats_keywords()

        # Common ATS parsing patterns
        self.ats_patterns = self._load_ats_patterns()

    def _load_ats_keywords(self) -> Dict[str, List[str]]:
        """Load comprehensive ATS keywords database."""
        return {
            "technology": [
                "python", "javascript", "react", "node.js", "aws", "docker",
                "kubernetes", "microservices", "agile", "scrum", "ci/cd",
                "git", "sql", "nosql", "rest api", "graphql", "typescript",
                "java", "c++", "go", "rust", "machine learning", "ai",
                "data science", "big data", "cloud computing"
            ],
            "finance": [
                "financial analysis", "budgeting", "forecasting", "excel",
                "financial modeling", "risk management", "compliance",
                "auditing", "accounting", "treasury", "investment banking",
                "portfolio management", "derivatives", "hedge funds"
            ],
            "healthcare": [
                "patient care", "medical records", "hipaa", "clinical",
                "pharmaceutical", "healthcare administration", "nursing",
                "medical billing", "ehr", "electronic health records",
                "medical coding", "health insurance"
            ],
            "marketing": [
                "digital marketing", "seo", "sem", "social media",
                "content marketing", "brand management", "analytics",
                "google analytics", "marketing automation", "crm",
                "email marketing", "conversion optimization"
            ]
        }

    def _load_ats_patterns(self) -> Dict[str, str]:
        """Load ATS parsing patterns and best practices."""
        return {
            "contact_info": r"^(?:\d{3}-)?\d{3}-\d{4}$|^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            "date_formats": r"\b\d{1,2}/\d{1,2}/\d{4}\b|\b\d{4}-\d{2}-\d{2}\b|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\b",
            "education_keywords": r"\b(?:bachelor|master|phd|doctorate|associate|certificate|diploma)\b",
            "experience_keywords": r"\b(?:experience|years|managed|led|developed|created|implemented|designed)\b"
        }

    async def analyze_resume_for_ats(
        self,
        resume_content: str,
        job_description: str,
        industry: str = "technology"
    ) -> ATSAnalysis:
        """
        Comprehensive ATS analysis of resume against job description.

        Args:
            resume_content: Full resume text
            job_description: Job posting text
            industry: Industry category for keyword matching

        Returns:
            Detailed ATS analysis with scores and recommendations
        """
        try:
            # Extract keywords from job description
            job_keywords = await self._extract_job_keywords(job_description, industry)

            # Analyze resume against keywords
            keyword_analysis = self._analyze_keyword_match(resume_content, job_keywords)

            # Check ATS formatting issues
            format_analysis = self._analyze_formatting_issues(resume_content)

            # Assess readability for ATS parsing
            readability_analysis = self._analyze_readability(resume_content)

            # Generate ATS-optimized resume
            optimized_resume = await self._generate_ats_optimized_resume(
                resume_content, job_keywords, industry
            )

            # Calculate overall scores
            overall_score = self._calculate_overall_ats_score(
                keyword_analysis, format_analysis, readability_analysis
            )

            return ATSAnalysis(
                overall_score=overall_score,
                keyword_match_score=keyword_analysis["score"],
                format_score=format_analysis["score"],
                readability_score=readability_analysis["score"],
                industry_alignment_score=self._calculate_industry_alignment(
                    resume_content, industry
                ),
                keyword_optimization=keyword_analysis,
                format_issues=format_analysis["issues"],
                readability_improvements=readability_analysis["improvements"],
                industry_recommendations=self._generate_industry_recommendations(
                    resume_content, industry
                ),
                ats_friendly_resume=optimized_resume,
                critical_missing_keywords=keyword_analysis["missing_critical"],
                recommended_additions=self._generate_recommended_additions(
                    job_keywords, resume_content
                ),
                parsing_errors=format_analysis["parsing_errors"],
                ats_compatibility_warnings=self._generate_compatibility_warnings(
                    resume_content
                )
            )

        except Exception as e:
            # Return basic analysis if AI processing fails
            return ATSAnalysis(
                overall_score=60,
                keyword_match_score=55,
                format_score=65,
                readability_score=60,
                industry_alignment_score=50,
                keyword_optimization={"score": 55, "matched": [], "missing": [], "missing_critical": []},
                format_issues=["Unable to analyze formatting"],
                readability_improvements=["Basic readability check failed"],
                industry_recommendations=["Industry analysis unavailable"],
                ats_friendly_resume=resume_content,
                critical_missing_keywords=[],
                recommended_additions=["Analysis unavailable"],
                parsing_errors=["Analysis failed"],
                ats_compatibility_warnings=["Unable to perform ATS compatibility check"]
            )

    async def _extract_job_keywords(
        self,
        job_description: str,
        industry: str
    ) -> Dict[str, List[str]]:
        """Extract and categorize keywords from job description using AI."""
        prompt = f"""
        Analyze this job description and extract keywords categorized by importance:

        Job Description:
        {job_description}

        Industry: {industry}

        Return JSON with this structure:
        {{
            "critical": ["must-have keywords"],
            "important": ["should-have keywords"],
            "nice_to_have": ["bonus keywords"],
            "technical_skills": ["specific technical skills"],
            "soft_skills": ["soft skills and competencies"],
            "industry_terms": ["industry-specific terminology"]
        }}

        Focus on keywords that ATS systems typically look for.
        """

        try:
            response = await self.ai_service.generate_response(
                prompt=prompt,
                max_tokens=1000,
                temperature=0.3
            )

            # Parse JSON response
            keywords_data = json.loads(response)
            return keywords_data

        except Exception:
            # Fallback to basic keyword extraction
            return {
                "critical": self.ats_keywords.get(industry, [])[:5],
                "important": self.ats_keywords.get(industry, [])[5:10],
                "nice_to_have": self.ats_keywords.get(industry, [])[10:15],
                "technical_skills": [],
                "soft_skills": [],
                "industry_terms": []
            }

    def _analyze_keyword_match(
        self,
        resume_content: str,
        job_keywords: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """Analyze keyword matching between resume and job requirements."""
        resume_lower = resume_content.lower()
        matched_keywords = []
        missing_critical = []
        missing_important = []

        # Check critical keywords
        for keyword in job_keywords.get("critical", []):
            if keyword.lower() in resume_lower:
                matched_keywords.append(keyword)
            else:
                missing_critical.append(keyword)

        # Check important keywords
        for keyword in job_keywords.get("important", []):
            if keyword.lower() in resume_lower:
                matched_keywords.append(keyword)
            else:
                missing_important.append(keyword)

        # Calculate match score
        total_keywords = len(job_keywords.get("critical", [])) + len(job_keywords.get("important", []))
        matched_count = len(matched_keywords)

        if total_keywords > 0:
            score = int((matched_count / total_keywords) * 100)
        else:
            score = 75  # Default good score if no keywords specified

        return {
            "score": min(100, score),
            "matched": matched_keywords,
            "missing_critical": missing_critical,
            "missing_important": missing_important,
            "total_keywords": total_keywords,
            "matched_count": matched_count
        }

    def _analyze_formatting_issues(self, resume_content: str) -> Dict[str, Any]:
        """Analyze resume formatting for ATS compatibility."""
        issues = []
        parsing_errors = []

        # Check for common ATS formatting issues
        lines = resume_content.split('\n')

        # Check for tables (ATS often can't parse)
        if '|' in resume_content and resume_content.count('|') > 4:
            issues.append("Tables detected - ATS may not parse tabular data correctly")

        # Check for complex formatting
        if '**' in resume_content or '__' in resume_content:
            issues.append("Markdown formatting detected - use simple text formatting")

        # Check for special characters
        special_chars = ['•', '●', '○', '■', '□', '▪', '▫']
        for char in special_chars:
            if char in resume_content:
                issues.append(f"Special bullet points ({char}) may not parse correctly")

        # Check contact information format
        contact_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # Phone
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'  # Email
        ]

        contact_found = False
        for pattern in contact_patterns:
            if re.search(pattern, resume_content):
                contact_found = True
                break

        if not contact_found:
            parsing_errors.append("No clear contact information found")

        # Check for standard sections
        sections = ['experience', 'education', 'skills', 'summary', 'objective']
        sections_found = []

        for section in sections:
            if section.lower() in resume_content.lower():
                sections_found.append(section)

        if len(sections_found) < 3:
            issues.append("Missing standard resume sections (Experience, Education, Skills)")

        # Calculate format score
        score = 100
        score -= len(issues) * 10
        score -= len(parsing_errors) * 15
        score = max(0, min(100, score))

        return {
            "score": score,
            "issues": issues,
            "parsing_errors": parsing_errors,
            "sections_found": sections_found
        }

    def _analyze_readability(self, resume_content: str) -> Dict[str, Any]:
        """Analyze resume readability for ATS parsing."""
        improvements = []

        # Check sentence length
        sentences = re.split(r'[.!?]+', resume_content)
        long_sentences = [s for s in sentences if len(s.split()) > 25]

        if long_sentences:
            improvements.append("Some sentences are very long - break into shorter sentences for better parsing")

        # Check for passive voice (common readability issue)
        passive_indicators = ['was', 'were', 'had been', 'have been', 'being']
        passive_count = sum(1 for word in resume_content.lower().split()
                          if word in passive_indicators)

        if passive_count > len(sentences) * 0.3:
            improvements.append("High use of passive voice - use active voice for clarity")

        # Check paragraph length
        paragraphs = resume_content.split('\n\n')
        long_paragraphs = [p for p in paragraphs if len(p.split()) > 100]

        if long_paragraphs:
            improvements.append("Some paragraphs are very long - break into smaller paragraphs")

        # Check for abbreviations without explanations
        common_abbreviations = ['e.g.', 'i.e.', 'etc.', 'vs.', 'w/', 'w/o']
        unexplained_abbreviations = []

        words = resume_content.split()
        for i, word in enumerate(words):
            if word in common_abbreviations:
                # Check if abbreviation is explained
                context = ' '.join(words[max(0, i-5):i+5])
                if not any(explain in context.lower() for explain in
                          ['for example', 'that is', 'and so on', 'versus', 'with', 'without']):
                    unexplained_abbreviations.append(word)

        if unexplained_abbreviations:
            improvements.append("Abbreviations detected - spell out acronyms on first use")

        # Calculate readability score
        score = 100
        score -= len(improvements) * 8
        score = max(0, min(100, score))

        return {
            "score": score,
            "improvements": improvements,
            "sentence_count": len(sentences),
            "avg_sentence_length": sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        }

    async def _generate_ats_optimized_resume(
        self,
        original_resume: str,
        job_keywords: Dict[str, List[str]],
        industry: str
    ) -> str:
        """Generate ATS-optimized version of the resume."""
        prompt = f"""
        Optimize this resume for ATS compatibility while maintaining professional quality:

        Original Resume:
        {original_resume}

        Target Job Keywords: {json.dumps(job_keywords, indent=2)}
        Industry: {industry}

        Requirements:
        1. Use standard fonts and formatting (no tables, no special characters)
        2. Include critical keywords naturally in context
        3. Use clear section headers (EXPERIENCE, EDUCATION, SKILLS)
        4. Format dates consistently (MM/YYYY)
        5. Use bullet points for achievements
        6. Keep quantifiable achievements
        7. Maintain professional language
        8. Ensure contact information is at the top

        Return the complete optimized resume text.
        """

        try:
            optimized_resume = await self.ai_service.generate_response(
                prompt=prompt,
                max_tokens=2000,
                temperature=0.4
            )
            return optimized_resume.strip()

        except Exception:
            # Return original if optimization fails
            return original_resume

    def _calculate_overall_ats_score(
        self,
        keyword_analysis: Dict,
        format_analysis: Dict,
        readability_analysis: Dict
    ) -> int:
        """Calculate overall ATS compatibility score."""
        keyword_weight = 0.4
        format_weight = 0.3
        readability_weight = 0.3

        overall_score = (
            keyword_analysis["score"] * keyword_weight +
            format_analysis["score"] * format_weight +
            readability_analysis["score"] * readability_weight
        )

        return int(min(100, max(0, overall_score)))

    def _calculate_industry_alignment(self, resume_content: str, industry: str) -> int:
        """Calculate how well resume aligns with industry standards."""
        industry_keywords = self.ats_keywords.get(industry, [])
        resume_lower = resume_content.lower()

        matched_count = sum(1 for keyword in industry_keywords
                          if keyword.lower() in resume_lower)

        if industry_keywords:
            alignment_score = (matched_count / len(industry_keywords)) * 100
        else:
            alignment_score = 75  # Default if no industry keywords

        return int(min(100, alignment_score))

    def _generate_industry_recommendations(
        self,
        resume_content: str,
        industry: str
    ) -> List[str]:
        """Generate industry-specific recommendations."""
        recommendations = []

        # Basic industry recommendations
        industry_tips = {
            "technology": [
                "Include specific programming languages and frameworks",
                "Highlight version control experience (Git)",
                "Mention cloud platform experience (AWS, Azure, GCP)",
                "Include database technologies used"
            ],
            "finance": [
                "Highlight financial software proficiency",
                "Include relevant certifications (CFA, CPA)",
                "Mention regulatory compliance experience",
                "Include financial modeling experience"
            ],
            "healthcare": [
                "Include relevant certifications and licenses",
                "Highlight EHR system experience",
                "Mention HIPAA compliance knowledge",
                "Include specialized medical software experience"
            ],
            "marketing": [
                "Include specific marketing tools and platforms",
                "Highlight campaign metrics and results",
                "Mention SEO/SEM experience",
                "Include social media management experience"
            ]
        }

        recommendations.extend(industry_tips.get(industry, [
            "Include industry-specific certifications",
            "Highlight relevant software and tools",
            "Mention industry-specific achievements"
        ]))

        return recommendations

    def _generate_recommended_additions(
        self,
        job_keywords: Dict[str, List[str]],
        resume_content: str
    ) -> List[str]:
        """Generate recommended additions to improve ATS score."""
        additions = []

        # Check for missing critical skills
        missing_critical = []
        for keyword in job_keywords.get("critical", []):
            if keyword.lower() not in resume_content.lower():
                missing_critical.append(keyword)

        if missing_critical:
            additions.append(f"Consider adding experience with: {', '.join(missing_critical[:3])}")

        # Check for quantifiable achievements
        if not re.search(r'\d+', resume_content):
            additions.append("Add quantifiable achievements (numbers, percentages, metrics)")

        # Check for recent experience
        current_year = datetime.now(timezone.utc).year
        if str(current_year) not in resume_content and str(current_year - 1) not in resume_content:
            additions.append("Update with recent experience and achievements")

        return additions

    def _generate_compatibility_warnings(self, resume_content: str) -> List[str]:
        """Generate ATS compatibility warnings."""
        warnings = []

        # Check file format implications (though we're working with text)
        if len(resume_content) > 50000:  # Roughly 2 pages
            warnings.append("Resume is quite long - consider condensing for ATS parsing")

        # Check for inconsistent formatting
        if resume_content.count('\t') > resume_content.count(' ') * 0.1:
            warnings.append("Mixed tabs and spaces may cause formatting issues")

        # Check for non-standard characters
        non_ascii = [char for char in resume_content if ord(char) > 127]
        if len(non_ascii) > len(resume_content) * 0.05:
            warnings.append("High number of non-ASCII characters may cause parsing issues")

        return warnings


# Singleton instance for application use
ats_optimizer = ATSOptimizerService()
