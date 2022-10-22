from pydantic import BaseModel, AnyHttpUrl


class Page(BaseModel):
    class_name: str
    name: str
    
