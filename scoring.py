from typing import Any, Tuple
from dotenv import load_dotenv
import os
from google import genai

load_dotenv()

def calculate_rule_score(lead: dict[str, Any], is_validated: bool = True, missing_value_count: int = 0):
    score = 0
    reasons = []

    # role-relevance (max 20 points)
    role = (lead.get('role') or '').lower() # fetch role string from lead
    # construct keyword arrays
    decision_maker_keywords = ['ceo', 'cto', 'cfo', 'founder', 'head', 'director', 'vp', 'chief', 'president']
    influencer_keywords = ['manager', 'lead', 'senior', 'coordinator', 'specialist', 'analyst', 'developer', 'engineer']

    # score based on keyword occurances in role string
    if any(keyword in role for keyword in decision_maker_keywords):
        score += 20
        reasons.append("Decision maker role detected (+20)")
    elif any(keyword in role for keyword in influencer_keywords):
        score += 10
        reasons.append("Influencer role detected (+10)")
    else:
        reasons.append("Role not relevant +0")

    # industry match (max 20 points)
    industry = (lead.get('industry') or '').lower() # fetch industry string from lead
    #construct keyword arrays
    saas_keywords = ['software', 'saas', 'technology', 'tech', 'b2b', 'startup']
    adjacent_keywords = ['marketing', 'sales', 'consulting', 'services']

    # score based on keyword occurances in industry string
    if any(keyword in industry for keyword in saas_keywords):
        score += 20
        reasons.append("Exact ICP match (+20)")
    elif any(keyword in industry for keyword in adjacent_keywords):
        score += 10
        reasons.append("Adjacent industry (+10)")
    else:
        reasons.append("Non-target industry (+0)")

    # Data completeness (max 10 points)
    if is_validated:
        # pydantic-validated leads gets full points by default
        score +=10
        reasons.append("Complete profile (+10)")
    else:
        # for validation-failed leads, calculate score from it's 'missing_value_count'
        total_fields = 6 # in our case
        filled_fields = total_fields - missing_value_count
        completeness_score = int((filled_fields / total_fields) * 10)
        score += completeness_score
    return score, " | ".join(reasons)

def calculate_ai_score(lead: dict[str, Any], offer: dict[str, Any]) -> Tuple[int, str, str]:
    gemini_api_key = os.getenv("GEMINI_API_KEY")

    if not gemini_api_key:
        return 25, "Gemini api key not found. Using default score.", "Medium"

    try:
        prompt = f"""
            Product/Offer: {offer['name']}
            Value Props: {', '.join(offer['value_props'])}
            Ideal Use Cases: {', '.join(offer['ideal_use_cases'])}

            Prospect:
            - Name: {lead.get('name', 'Unknown')}
            - Role: {lead.get('role', 'Unknown')}
            - Company: {lead.get('company', 'Unknown')}
            - Industry: {lead.get('industry', 'Unknown')}
            - LinkedIn Bio: {lead.get('linkedin_bio', 'Unknown')}
            Based on the prospect's profile and the product offering, classify their buying intent as High, Medium, or Low.
            Explain your reasoning in 1-2 sentences focusing on role fit, industry alignment, and potential need.

            Format: INTENT: [High/Medium/Low] | REASONING: [explanation]
        """
    
        client = genai.Client(api_key=gemini_api_key)

        response = client.models.generate_content(
            model="gemma-3-27b-it",
            contents=prompt,
        )

        response = response.text
        text_lower = response.lower()
        if any(word in text_lower for word in ['high', 'excellent', 'perfect', 'ideal']):
            score, intent = 50, "High"
        elif any(word in text_lower for word in ['medium', 'moderate', 'possible', 'potential']):
            score, intent = 30, "Medium"
        else:
            score, intent = 10, "Low"

        reasoning = f"AI analysis: {response[:300]}"
        return score, reasoning, intent

    except Exception as e:
        return 25, f"AI analysis unavailable: {str(e)}. Using default Medium intent.", "Medium"

    
def calculate_total_score(lead: dict[str, Any], offer: dict[str, Any], is_validated: bool = True, missing_value_count: int = 0):

    # get rule_score, rule_reasoning, ai_score and ai_reasoning
    rule_score, rule_reasoning = calculate_rule_score(lead, is_validated, missing_value_count)
    ai_score, ai_reasoning, ai_intent = calculate_ai_score(lead, offer)

    final_score = rule_score + ai_score

    # calculate intend from final_score
    if final_score >= 70:
        final_intent = "High"
    elif final_score >= 40:
        final_intent = "Medium"
    else:
        final_intent = "Low"

    # final reasoning
    combined_reasoning = f"Rules: {rule_reasoning} | AI: {ai_reasoning}"

    return {
        "name": lead.get('name', 'Unknown'),
        "role": lead.get('role'),
        "company": lead.get('company'),
        "industry": lead.get('industry'),
        "intent": final_intent,
        "score": final_score,
        "reasoning": combined_reasoning,
        "data_completeness": "Complete" if is_validated else "Incomplete"
    }