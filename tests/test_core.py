import unittest
from runbook_builder import build,probe
S={"service":"d","trigger":"a","owner":"o","steps":["x"],"verification":["v"],"rollback":["r"]}
class T(unittest.TestCase):
 def test_build(self):self.assertTrue(build(S)["ok"])
 def test_rollback_required(self):self.assertFalse(build({**S,"rollback":[]})["ok"])
 def test_steps_bound(self):self.assertFalse(build({**S,"steps":[]})["ok"])
 def test_probe(self):self.assertTrue(probe()["ok"])
if __name__=="__main__":unittest.main()
