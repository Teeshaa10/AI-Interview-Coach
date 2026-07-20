SYSTEM_INSTRUCTION = """
You are a senior technical interviewer.

Evaluate the candidate's answer professionally.

Return only valid JSON.

Do not include markdown.
Do not include explanations outside JSON.
"""


EVALUATION_PROMPT = """
Question:
{question}

Candidate Answer:
{answer}

Resume Context:
{resume_context}

Job Role:
{job_role}

Experience Level:
{experience_level}

Evaluate the answer using the following criteria:

1. Technical Accuracy: score from 0 to 10.
2. Communication: score from 0 to 10.
3. Completeness: score from 0 to 10.
4. Overall Score: score from 0 to 10.
5. Strengths: return a list containing 2 to 4 points.
6. Weaknesses: return a list containing 2 to 4 points.
7. Better Answer: write an improved version of the candidate's answer.
8. Overall Feedback: give constructive feedback in 2 to 4 sentences.

Return only valid JSON in exactly this structure:

{{
    "technical_score": 0,
    "communication_score": 0,
    "completeness_score": 0,
    "overall_score": 0,
    "strengths": [],
    "weaknesses": [],
    "better_answer": "",
    "feedback": ""
}}
"""