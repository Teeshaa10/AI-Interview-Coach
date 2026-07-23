from app.schemas.embedding import EmbeddingSearchResult


SYSTEM_INSTRUCTION = """You are a senior software engineering interviewer.
Generate rigorous, personalized interview questions using only the supplied resume evidence.
Never invent technologies, projects, employers, achievements, metrics, or experience.
Every technical, project, and coding question must be traceable to at least one supplied resume chunk.
HR questions must still reference the candidate's demonstrated experience, decisions, teamwork, ownership,
or learning shown in the supplied chunks. Return only the requested structured response."""


def _question_distribution(total: int) -> dict[str, int]:
    """Distribute the requested total while keeping all four categories populated."""

    base = total // 4
    remainder = total % 4
    names = ("technical", "project", "hr", "coding")
    distribution = {name: base for name in names}
    for name in names[:remainder]:
        distribution[name] += 1
    return distribution


def build_interview_prompt(
    *,
    job_role: str,
    experience_level: str,
    number_of_questions: int,
    chunks: list[EmbeddingSearchResult],
) -> str:
    """Build a prompt containing only authenticated, semantically retrieved resume text."""

    distribution = _question_distribution(number_of_questions)
    evidence = "\n\n".join(
        f"[Resume chunk {index + 1} | similarity={chunk.similarity_score:.4f}]\n"
        f"{chunk.chunk_text.strip()}"
        for index, chunk in enumerate(chunks)
    )

    return f"""Create interview questions for this candidate.

Target job role: {job_role}
Candidate experience level: {experience_level}
Exact total number of questions: {number_of_questions}

Required distribution:
- technical_questions: exactly {distribution['technical']}
- project_questions: exactly {distribution['project']}
- hr_questions: exactly {distribution['hr']}
- coding_questions: exactly {distribution['coding']}

Grounding rules:
1. Use only facts present in the resume chunks below.
2. Make questions specific by naming relevant skills, systems, projects, responsibilities, or outcomes from those chunks.
3. Do not ask generic questions that could apply to any candidate.
4. Coding questions should connect to algorithms, data structures, languages, frameworks, databases, APIs,
   performance issues, or engineering work visible in the resume evidence.
5. Do not include answers, explanations, numbering, markdown, or category labels inside question strings.
6. Return exactly the requested count and no duplicate questions.

Authenticated resume evidence:
{evidence}
"""
