from pydantic import BaseModel

class PostOut(BaseModel):
    id: int
    title: str
    content: str
    published: bool 
    