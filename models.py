from pydantic import BaseModel, HttpUrl
from datetime import datetime


class Url(BaseModel):
    og_url: HttpUrl
    key: str
    creation_time: datetime
    redirects: int





