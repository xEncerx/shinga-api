from .create import CreateOperations
from .update import UpdateOperations
from .read import ReadOperations


class TitleSourceDataCRUD:
    create = CreateOperations
    update = UpdateOperations
    read = ReadOperations
