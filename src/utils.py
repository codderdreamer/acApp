

class Utils():
    def __init__(self) -> None:
        pass
        
        
    def is_variable_none(self, value):
        return value in ["None", "none", "", None]
    
    def is_variable_true(self, value):
        return value in ["True", "true", True]
    
    def is_variable_false(self, value):
        return value in ["False", "false", False]
    
