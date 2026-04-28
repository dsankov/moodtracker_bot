from pydantic import BaseModel, Field

class User(BaseModel):
    id: int
    name: str = Field(min_length=4)

user = User(id=1, name="Test")
print(user.model_dump())
