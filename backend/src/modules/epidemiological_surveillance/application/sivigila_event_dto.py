from pydantic import BaseModel


class SivigilaEventReadDto(BaseModel):
    code: str
    definition_id: str
    name: str
    slug: str
