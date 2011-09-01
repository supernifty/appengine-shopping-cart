import unittest

import ebay

class TestNotification(unittest.TestCase):

  def setUp(self):
    pass

  def test_notify(self):
    n = ebay.Notification( '<ItemID>itemid</ItemID>' )

if __name__ == '__main__':
    unittest.main()
