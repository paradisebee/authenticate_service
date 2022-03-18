import unittest

from auth_serv.user import User

class TestUser(unittest.TestCase):
    
    def test_set_user(self):
        u = User("Kate", "Peace%123*")

        # test user name and password
        self.assertEqual("Kate", u.name)
        self.assertEqual("Peace%123*", u.password)

    def test_add_role(self):
        u = User("John", "HelloWorld123")

        # test add role and all roles
        u.add_role("Admin")
        self.assertEqual(["Admin"], u.all_roles())
        u.add_role("Remote")
        self.assertEqual(["Admin", "Remote"], u.all_roles())    

    def test_check_role(self):
        u = User("Gary", "B#@$sdf2")
        u.add_role("User")
        u.add_role("Remote")

        # check role and non-exist role
        self.assertTrue(u.check_role("Remote"))
        self.assertTrue(u.check_role("User"))
        self.assertFalse(u.check_role("Guest"))
    
    def test_delete_role(self):
        u = User("Kevin", "65^%@&edsee")
        u.add_role("User")
        u.add_role("Remote")
        u.add_role("Test")

        # delete normal and non-exist role
        u.delete_role("Remote")
        self.assertEqual(["User", "Test"], u.all_roles())
        u.delete_role("Admin")
        self.assertEqual(["User", "Test"], u.all_roles())


if __name__ == "__main__":
    unittest.main()
