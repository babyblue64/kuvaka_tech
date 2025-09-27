from pydantic import BaseModel

class Offer(BaseModel):
    name: str
    value_props: list[str]
    ideal_use_cases: list[str]

class Lead(BaseModel):
    name: str
    role: str
    company: str
    industry: str
    location: str
    linkedin_bio: str