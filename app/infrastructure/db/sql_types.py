from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import TypeDecorator

# This file defines custom SQLAlchemy types for handling JSON fields with SQLModel models.

class JSONBWithModel(TypeDecorator):
    impl = JSONB
    cache_ok = True
    
    def __init__(self, model_class):
        self.model_class = model_class
        super().__init__()
    
    def process_bind_param(self, value, dialect):
        if value is not None:
            if isinstance(value, self.model_class):
                return value.model_dump()
            elif isinstance(value, list):
                return [
                    item.model_dump() if isinstance(item, self.model_class) else item
                    for item in value
                ]
            return value
        return value
    
    def process_result_value(self, value, dialect):
        if value is None: 
            return value
        
        if isinstance(value, list):
            return [self.model_class(**item) for item in value]
        else:
            return self.model_class(**value)
