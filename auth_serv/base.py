import abc

class BaseUser(abc.ABC):
    """ Abstract base class for user. """
    def __init__(self, name, password):
        self.name = name
        self.password = password

    @abc.abstractmethod
    def check_role(self, role):
        pass

    @abc.abstractmethod
    def add_role(self, role):
        pass
    
    @abc.abstractmethod
    def all_roles(self):
        pass