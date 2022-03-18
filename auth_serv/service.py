import hashlib
import datetime
from collections import OrderedDict

from .user import User

class AuthService(object):
    """ A simple authentication and authorization service. """

    def __init__(self):
        self.users = OrderedDict()
        self.roles = []
        self.token_list = {}
        self.expiry_time = 7200

    def encrypt(self, password):
        """ Password encryption with md5. """
        encypt = hashlib.md5()
        encypt.update(password.encode(encoding='utf-8'))
        # print(encypt.hexdigest())
        return encypt.hexdigest()

    def create_user(self, username='', password=''):
        """ Create a new user. """
        if username in self.users.keys():
            print("Error: User '{}' is already exist! Use a different user name.".format(username))
        else:
            self.users[username] = User(username, self.encrypt(password))

    def delete_user(self, username):
        """ Delete a user. Raise error if user doesn't exist."""
        if username not in self.users.keys():
            print("Error: User '{}' is not in the system!".format(username))
            return False
        else:
            del self.users[username]
            print("Info: User '{}' is deleted from the system.".format(username))
            return True
    
    def create_role(self, role, verbose=True):
        """ Create a new role. """
        if role in self.roles:
            if verbose:
                print("Error: Creation failed!. Role '{}' is already exist!.".format(role))
        else:
            # don't add empty role
            if len(role) > 0:
                self.roles.append(role)
                print("Info: Added role '{}' to role list.".format(role))
    
    def delete_role(self, role):
        """ Delete an unwanted role. """
        if role not in self.roles:
            print("Error: Delete role failed!. Role '{}' is not in the system!.".format(role))
        else:
            self.roles.remove(role)

    def add_role_to_user(self, username, role):
        """ Add role to user, create role if not exist. """
        if username not in self.users.keys():
            print("Error: Add role to user failed! User '{}' is not in the system!".format(username))
            return False
        # create role before adding to user
        self.create_role(role, verbose=False)
        self.users[username].add_role(role)
        return True

    def delete_role_from_user(self, username, role):
        """ Delete a role from user. """
        if username not in self.users.keys():
            print("Error: Delete role from user failed! User '{}' is not in the system!".format(username))
            return False
        
        self.users[username].delete_role(role)
        return True
    
    def authenticate(self, username, password):
        """ 
        User sign-in, return a secret token
        if username and password are correct, 
        else return False. 
        """
        if username not in self.users.keys():
            print("Error: User '{}' is not in the system!".format(username))
            return False

        if self.encrypt(password)==self.users[username].password:
            current_time = datetime.datetime.now()
            # simple encryption for token generation
            token = self.encrypt(str({"user": username, "password": password, "time": current_time}))
            self.users[username].token = token
            self.users[username].token_generate_time = current_time

            self.token_list[token] = username
            return token
        else:
            print("Error: Password incorrect!")
            return False
    
    def invalidate(self, token):
        """ Invalidate the token. The token is invalid after the call. """
        if token in self.token_list.keys():
            # reset and return
            username = self.token_list[token]
            self.users[username].token = ""
            self.users[username].token_generate_time = -1
            del self.token_list[token]
            return

        print("Warning: the input token is not a valid token!")
    
    def check_role(self, token, role):
        """ Check if certain role exist in user.
        
        Inputs:
            token: authenticated secret token after sign-in.
            role: a certain role to check.

        Return:
            True if exist, else False.    
        """
        if self.authorize(token):
            username = self.token_list[token]
            return self.users[username].check_role(role)
        else:
            print("Error: token is invalid!")
            return False

    def all_roles(self, token):
        """ Return all roles of current user. 
        Input:
            token: authenticated secret token after sign-in.
        
        Return:
            if token is valid, return all role of current user, 
            else return empty list [].
        """
        if self.authorize(token):
            username = self.token_list[token]
            return self.users[username].all_roles()
        else:
            print("Error: token is invalid!")
            return []

    def authorize(self, token):
        """ Authorize token, return True if valid, else invalidate the token and return False."""
        if token in self.token_list.keys():
            username = self.token_list[token]
            # check if token is valid within expiry time
            current_time = datetime.datetime.now()
            elapsed = current_time.timestamp() - self.users[username].token_generate_time.timestamp()
            if elapsed < self.expiry_time:
                return True
            else:
                # make the expired token invalid
                self.invalidate(token)
                return False
        else:
            return False

    def set_expiry(self, t=2, fmt='h'):
        """ Set the expiration time of the secret token. 
        
        Inputs:
            t: integer, time of expiry.
            fmt: time's format, can be one of 's', 'm', 'h', 'd' (second, minute, hour, day)

        Return:
            None
        """
        if fmt=='s':
            self.expiry_time = t
            pstr = 'seconds'
        elif fmt=='m':
            self.expiry_time = t*60
            pstr = 'minutes'
        elif fmt=='d':
            self.expiry_time = t*3600*24
            pstr = 'days'
        else: # default to hour, and set all irrlevant input to hour
            self.expiry_time = t*3600
            pstr = 'hours'
        
        print("The token expiry time is set to: {} {}.".format(t, pstr))
