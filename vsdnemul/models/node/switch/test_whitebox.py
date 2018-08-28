from unittest import TestCase
from vsdnemul.models.node.switch.whitebox import Whitebox

class TestWhitebox(TestCase):

    def setUp(self):
        self.sw =  Whitebox("sw1")
        self.sw.commit()

    def tearDown(self):
        self.sw.destroy()

    def test_br_oper(self):
        self.fail()

    def test_br_oper(self):
        self.fail()

    def test_control_addr(self):
        self.fail()

    def test_control_addr(self):
        self.fail()

    def test_set_openflow_version(self):
        self.fail()

    def test_set_manager(self):
        self.fail()

    def test_set_controller(self):
        self.fail()

    def test_del_controller(self):
        self.fail()

    def test_add_port(self):
        self.fail()

    def test_del_port(self):
        self.fail()

    def test_get_port(self):
        self.fail()

    def test_get_len_ports(self):
        self.fail()

    def test_commit(self):
        self.fail()

    def test_destroy(self):
        self.fail()
