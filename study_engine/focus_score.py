def compute_focus_score(session_active: bool, face_present: bool, looking_away: bool, distracted: bool) -> int:
    score = 0
    if session_active:
        score += 20
    if face_present:
        score += 30
    if not looking_away:
        score += 30
    if distracted:
        score -= 40
    return max(0, min(100, score))
