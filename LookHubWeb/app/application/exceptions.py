

class EntityNotFoundError(Exception):
    """Error should raise when Entity not found in dada base"""
    def __init__(self, entity_name: str = 'Entity'):
        self.entity_name = entity_name
        super().__init__(f"{entity_name} not found")


class InvalidFileError(Exception):
    """Error should raise when an invalid file is received"""
    def __init__(self):
        super().__init__('Invalid file received')


class UnknownError(Exception):
    """Error should raise in other unknown cases"""
    def __init__(self):
        super().__init__('Unknown error')

