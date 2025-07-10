from .token import Token, TokenPayload
from .user import *
from .errors import *

class Message(BaseModel):
    message: str