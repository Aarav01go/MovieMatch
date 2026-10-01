from pydantic import BaseModel


class AIAssistantRequest(BaseModel):
    query: str
