import unittest

if __name__ == '__main__':
    testsuite = unittest.TestLoader().discover(start_dir='test')
    unittest.TextTestRunner(verbosity=1).run(testsuite)
