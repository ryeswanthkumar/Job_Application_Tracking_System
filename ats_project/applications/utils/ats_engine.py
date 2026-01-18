def calculate_score(candidate, rule):
    score = 0

    if candidate.experience >= rule.min_experience:
        score += 30

    candidate_skills = set(candidate.skills.lower().split(","))
    required_skills = set(rule.required_skills.lower().split(","))

    score += min(len(candidate_skills & required_skills) * 10, 50)

    return score
