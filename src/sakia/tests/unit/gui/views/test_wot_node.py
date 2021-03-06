import unittest
from unittest.mock import patch
from PyQt5.QtCore import QLocale
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QStyleOptionGraphicsItem, QWidget
from sakia.tests import QuamashTest
from sakia.gui.views.nodes import WotNode
from sakia.core.graph.constants import NodeStatus


class TestWotNode(unittest.TestCase, QuamashTest):
    def setUp(self):
        self.setUpQuamash()
        QLocale.setDefault(QLocale("en_GB"))

    def tearDown(self):
        self.tearDownQuamash()

    def test_create_wot_node(self):
        metadata = {
            'status': NodeStatus.NEUTRAL,
            'text': "UserA",
            'tooltip': "TestTooltip"
        }
        nx_pos = {
            "A": (0, 5),
            "B": (10, 20)
        }
        async def exec_test():
            node = WotNode(("A", metadata), nx_pos)
            self.assertEqual(node.id, "A")
            self.assertEqual(node.metadata['status'], NodeStatus.NEUTRAL)
            self.assertEqual(node.x(), 0)
            self.assertEqual(node.y(), 5)
            self.assertEqual(node.status_wallet, False)
            self.assertEqual(node.status_member, True)
            self.assertEqual(node.text, "UserA")
            self.assertEqual(node.toolTip(), "TestTooltip")

        self.lp.run_until_complete(exec_test())

    def test_paint(self):
        painter = QPainter()
        widget = QWidget()
        metadata = {
            'status': NodeStatus.NEUTRAL,
            'text': "UserA",
            'tooltip': "TestTooltip"
        }
        nx_pos = {
            "A": (0, 5),
            "B": (10, 20)
        }
        async def exec_test():
            node = WotNode(("A", metadata), nx_pos)
            node.paint(painter, QStyleOptionGraphicsItem(), widget)

        self.lp.run_until_complete(exec_test())

    @patch('PyQt5.QtGui.QPainter', spec=QPainter)
    @patch('PyQt5.QtWidgets.QWidget')
    def test_bounding_rect(self, painter, widget):
        metadata = {
            'status': NodeStatus.NEUTRAL,
            'text': "A",
            'tooltip': "TestTooltip"
        }
        nx_pos = {
            "A": (0, 5),
            "B": (10, 20)
        }
        async def exec_test():
            node = WotNode(("A", metadata), nx_pos)
            bounding_rect = node.boundingRect()
            self.assertAlmostEqual(bounding_rect.x(), -0.5, delta=1)
            self.assertAlmostEqual(bounding_rect.y(), -0.5, delta=1)
            self.assertAlmostEqual(bounding_rect.width(), 19.59375, delta=15)
            self.assertAlmostEqual(bounding_rect.height(), 37.0, delta=15)

        self.lp.run_until_complete(exec_test())
