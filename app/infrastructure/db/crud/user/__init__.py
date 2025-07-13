from .create import CreateOperations
from .read import ReadOperations
from .update import UpdateOperations

class UserCRUD:
    create = CreateOperations
    read = ReadOperations
    update = UpdateOperations