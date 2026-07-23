RESUME_ANALYSIS_SYSTEM_INSTRUCTION = """
You are an expert technical recruiter and ATS resume reviewer.

Analyze the resume for the requested target role.

Return only valid JSON.
Do not include markdown.
Do not include explanations outside the JSON object.
"""


RESUME_ANALYSIS_PROMPT = """
Target Role:
{target_role}

Resume Content:
{resume_text}

Analyze the resume and return JSON in exactly this structure:

{{
    "ats_score": 0,
    "strengths": [],
    "weaknesses": [],
    "missing_skills": [],
    "suggested_skills": [],
    "suggested_projects": [],
    "improved_summary": "",
    "missing_keywords": [],
    "formatting_feedback": [],
    "actionable_recommendations": []
}}

Rules:

1. ats_score must be an integer from 0 to 100.
2. strengths must contain specific positive observations from the resume.
3. weaknesses must contain specific improvement areas.
4. missing_skills must contain skills commonly required for the target role but absent from the resume.
5. suggested_skills must contain practical skills the candidate should learn or highlight.
6. suggested_projects must contain realistic project ideas relevant to the target role.
7. improved_summary must be a polished professional resume summary.
8. missing_keywords must contain ATS keywords relevant to the target role.
9. formatting_feedback must contain concise formatting or readability suggestions.
10. actionable_recommendations must contain prioritized steps the candidate can take.
11. Return only valid JSON.
"""