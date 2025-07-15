from .token import Token, TokenPayload
from .forms import *
from .errors import *
from .title import *
from .user import *

class Message(BaseModel):
    message: str