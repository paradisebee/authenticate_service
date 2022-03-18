import unittest
import time

from auth_serv.service import AuthService
from auth_serv.user import User

class TestAuth(unittest.TestCase):
    
    def test_encrypt(self):
        serv = AuthService()
        # test encryption
        self.assertEqual("6df90c9e0a46004559f9d56011df876e", serv.encrypt("Peace%123*"))

    def test_set_user(self):
        serv = AuthService()
        serv.create_user("Kate", "Peace%123*")
        serv.create_user("John", "HelloWorld123")

        # check user name and encrypted password
        self.assertEqual("Kate", serv.users["Kate"].name)
        self.assertEqual("6df90c9e0a46004559f9d56011df876e", serv.users["Kate"].password)
        self.assertEqual("John", serv.users["John"].name)
        self.assertEqual("624825620c7cdd818e697366727aa594", serv.users["John"].password)

    def test_delete_user(self):
        serv = AuthService()
        serv.create_user("Kate", "Peace%123*")
        serv.create_user("John", "HelloWorld123")
        serv.create_user("Gary", "B#@$sdf2")

        # delete non-exist user and real user
        self.assertFalse(serv.delete_user("Kevin"))
        self.assertTrue(serv.delete_user("John"))
        
        # check remaining user name
        self.assertEqual(["Kate", "Gary"], list(serv.users.keys()))
        self.assertEqual("Kate", serv.users["Kate"].name)
        self.assertEqual("Gary", serv.users["Gary"].name)

    def test_create_role(self):
        serv = AuthService()
        serv.create_role("Admin")
        self.assertEqual(["Admin"], serv.roles)

        serv.create_role("Remote")
        self.assertEqual(["Admin", "Remote"], serv.roles)

        # Adding same role
        serv.create_role("Remote")
        self.assertEqual(["Admin", "Remote"], serv.roles)

        # Adding empty role
        serv.create_role("")
        self.assertEqual(["Admin", "Remote"], serv.roles)

    def test_delete_role(self):
        serv = AuthService()
        serv.create_role("Admin")
        serv.create_role("Remote")
        serv.create_role("Guest")

        # test all roles
        self.assertEqual(["Admin", "Remote", "Guest"], serv.roles)

        # test normal delete
        serv.delete_role("Remote")
        self.assertEqual(["Admin", "Guest"], serv.roles)

        # delete empty role
        serv.delete_role("")
        self.assertEqual(["Admin", "Guest"], serv.roles)

        # delete non-exist role
        serv.delete_role("Remote")
        self.assertEqual(["Admin", "Guest"], serv.roles)
    
    def test_add_role_to_user(self):
        serv = AuthService()
        serv.create_role("Admin")
        serv.create_role("Guest")

        # add role
        serv.create_user("Kate", "Peace%123*")
        serv.add_role_to_user("Kate", "Admin")
        self.assertEqual(["Admin"], serv.users["Kate"].all_roles())

        # add new role and check user's roles and all roles
        serv.add_role_to_user("Kate", "Remote")
        self.assertEqual(["Admin", "Remote"], serv.users["Kate"].all_roles())
        self.assertEqual(["Admin", "Guest", "Remote"], serv.roles)

        # test non-exist user
        self.assertFalse(serv.add_role_to_user("John", "Remote"))
        
    def test_delete_role_from_user(self):
        serv = AuthService()
        serv.create_role("Admin")
        serv.create_role("Guest")
        serv.create_role("Remote")

        serv.create_user("Kate", "Peace%123*")
        serv.add_role_to_user("Kate", "Admin")
        serv.add_role_to_user("Kate", "Remote")

        # wrong user name
        self.assertFalse(serv.delete_role_from_user("John", "Admin"))

        # role not in list
        serv.delete_role_from_user("Kate", "Guest")
        self.assertEqual(["Admin", "Remote"], serv.users["Kate"].all_roles())

        # delete role in list
        serv.delete_role_from_user("Kate", "Admin")
        self.assertEqual(["Remote"], serv.users["Kate"].all_roles())

    def test_set_expiry_time(self):
        serv = AuthService()

        serv.set_expiry(5, 's')
        self.assertEqual(5, serv.expiry_time)

        serv.set_expiry(2, 'm')
        self.assertEqual(120, serv.expiry_time)

        serv.set_expiry(3, 'h')
        self.assertEqual(10800, serv.expiry_time)

        serv.set_expiry(2, 'd')
        self.assertEqual(172800, serv.expiry_time)

    def test_authenticate(self):
        serv = AuthService()
        serv.set_expiry(2, 's')

        serv.create_user("Kate", "Peace%123*")

        # test username error and password error
        self.assertFalse(serv.authenticate("John", "Peace%123*"))
        self.assertFalse(serv.authenticate("Kate", "Peace%456*"))

        # test token expiry
        token = serv.authenticate("Kate", "Peace%123*")
        self.assertTrue(serv.authorize(token))     
        time.sleep(3)
        self.assertFalse(serv.authorize(token))
        
    def test_check_role(self):
        serv = AuthService()
        serv.set_expiry(2, 's')

        serv.create_role("Admin")
        serv.create_role("Guest")

        serv.create_user("Kate", "Peace%123*")
        serv.add_role_to_user("Kate", "Admin")
        serv.add_role_to_user("Kate", "Guest")
        
        token = serv.authenticate("Kate", "Peace%123*")

        # check role and get all roles
        self.assertTrue(serv.check_role(token, "Admin"))
        self.assertFalse(serv.check_role(token, "Remote"))
        self.assertEqual(["Admin", "Guest"], serv.all_roles(token))

        # test expiry
        time.sleep(3)
        self.assertFalse(serv.check_role(token, "Admin"))
        self.assertFalse(serv.check_role(token, "Admin"))
        self.assertEqual([], serv.all_roles(token))

        # reset and try again
        new_token = serv.authenticate("Kate", "Peace%123*")
        self.assertNotEqual(token, new_token)
        self.assertTrue(serv.check_role(new_token, "Admin"))
        self.assertFalse(serv.check_role(new_token, "Remote"))
        time.sleep(3)
        self.assertEqual([], serv.all_roles(new_token))
        self.assertFalse(serv.check_role(new_token, "Admin"))

if __name__ == "__main__":
    unittest.main()