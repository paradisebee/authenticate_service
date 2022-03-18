from .base import BaseUser

class User(BaseUser):
    """ User class for saving user information and utility functions. """
    def __init__(self, name, password):
        self.name = name
        self.password = password
        self.roles = []
        self.token = ""
        self.token_generate_time = -1

    def check_role(self, role):
        """ Check if current role is associated with the user. """
        for r in self.roles:
            if r==role:
                return True
        return False

    def add_role(self, role):
        """" Add role to the user. """
        if len(role)==0:
            print("Error: Add role failed! Role must be a valid string!")

        if role not in self.roles:
            self.roles.append(role)
            print("Info: Add role '{}' to user '{}' succeed.".format(role, self.name))
        else:
            print("Error: Creation failed!. Role {} is already exist!.".format(role))

    def delete_role(self, role):
        """" Delete role from the user. """
        if role in self.roles:
            self.roles.remove(role)
            print("Info: Role '{}' is deleted from user '{}'.".format(role, self.name))
        else:
            print("Error: Role {} is not associated with user {}!".format(role, self.name))
    
    def all_roles(self):
        """ Show all roles associated with the user. """
        return self.roles

