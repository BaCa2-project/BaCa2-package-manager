
import unittest as ut
from typing import Any

import baca2PackageManager.judge as judge


class JNAlpha(judge.JudgeNodeBase):

    def start(self, *args, **kwargs) -> Any:
        return None

    def receive(self, *args, **kwargs) -> judge.JudgeVerdict:
        assert len(args) > 0
        return judge.JudgeVerdict.OK if args[0] else judge.JudgeVerdict.FAIL


class JNBeta(judge.JudgeNodeBase):

    def start(self, *args, **kwargs) -> Any:
        return None

    def receive(self, *args, **kwargs) -> judge.JudgeVerdict:
        assert len(args) > 0
        return judge.JudgeVerdict.FAIL if args[0] else judge.JudgeVerdict.OK


class JNTheta(judge.JudgeNodeBase):

    def start(self, *args, **kwargs) -> Any:
        return None

    def receive(self, *args, **kwargs) -> judge.JudgeVerdict:
        return judge.JudgeVerdict.OK


class GeneralTest(ut.TestCase):

    def setUp(self) -> None:
        self.a = JNAlpha('a')
        self.a2 = JNAlpha('a2')
        self.b = JNBeta('b')
        self.c = JNTheta('c')
        self.end = judge.EndNode('END', judge.JudgeVerdict.OK)

    def test_from_dict(self):
        default = {
            self.a: {judge.JudgeVerdict.OK: self.a2, judge.JudgeVerdict.FAIL: self.a},
            self.a2: {judge.JudgeVerdict.OK: self.b},
            self.b: {judge.JudgeVerdict.OK: self.c, judge.JudgeVerdict.FAIL: self.a},
            self.c: {judge.JudgeVerdict.OK: self.end, judge.JudgeVerdict.FAIL: self.b},
            self.end: {}
        }
        manager = judge.JudgeManager.from_dict(default, self.a)
        manager.remove_node(manager.get_node_by_name('!SUCCESS'))
        self.assertEqual(manager.graph, default)

    def test_adding(self):
        manager = judge.JudgeManager()
        manager.add_node(self.a)
        self.assertRaises(ValueError, manager.add_node, self.a)
        self.assertRaises(KeyError, manager.add_connection, self.a, self.b, judge.JudgeVerdict.OK)
        self.assertRaises(KeyError, manager.add_connection, self.b, self.a, judge.JudgeVerdict.OK)
        manager.add_node(self.b)
        self.assertTrue(self.a in manager.graph and manager.graph[self.a] == {} and
                        self.b in manager.graph and manager.graph[self.b] == {})
        manager.add_connection(self.a, self.b, judge.JudgeVerdict.OK)
        self.assertEqual(manager.graph[self.a], {judge.JudgeVerdict.OK: self.b})
        manager.add_node(self.c)
        manager.add_connection(self.a, self.c, judge.JudgeVerdict.FAIL)
        self.assertEqual(manager.graph[self.a], {judge.JudgeVerdict.OK: self.b, judge.JudgeVerdict.FAIL: self.c})
        manager.add_node(self.end)
        self.assertRaises(ResourceWarning, manager.add_connection, self.end, self.a, judge.JudgeVerdict.OK)

    def test_removing(self):
        manager = judge.JudgeManager()
        manager.add_node(self.a)
        self.assertRaises(KeyError, manager.remove_node, self.b)
        manager.add_node(self.b)
        manager.add_node(self.c)
        self.assertRaises(KeyError, manager.remove_connection_by_node, self.a, self.b)
        self.assertRaises(KeyError, manager.remove_connection_by_verdict, self.a, judge.JudgeVerdict.FAIL)
        manager.add_connection(self.a, self.b, judge.JudgeVerdict.OK)
        manager.add_connection(self.a, self.c, judge.JudgeVerdict.FAIL)
        manager.remove_node(self.b)
        self.assertTrue(manager.graph[self.a] == {judge.JudgeVerdict.FAIL: self.c})
        manager.remove_connection_by_node(self.a, self.c)
        self.assertTrue(manager.graph[self.a] == {} and self.c in manager.graph)
        manager.add_connection(self.a, self.c, judge.JudgeVerdict.FAIL)
        manager.remove_connection_by_verdict(self.a, judge.JudgeVerdict.FAIL)
        self.assertTrue(manager.graph[self.a] == {} and self.c in manager.graph)

    def test_send_receive(self):
        manager = judge.JudgeManager()
        manager.add_node(self.a)
        manager.add_node(self.b)
        manager.add_connection(self.a, self.b, judge.JudgeVerdict.OK)
        manager.add_connection(self.b, (end := manager.get_node_by_name('!SUCCESS')), judge.JudgeVerdict.OK)
        manager.add_connection(self.b, self.a, judge.JudgeVerdict.FAIL)
        self.assertEquals(manager.send(self.a, True), None)
        self.assertRaises(KeyError, manager.send, self.a2)
        self.assertRaises(ValueError, manager.receive)
        manager.set_start_node(self.a)
        current = manager.receive()
        self.assertEquals(current, manager.start_node)
        current = manager.receive(current, True)
        self.assertEquals(current, self.b)
        current = manager.receive(current, True)
        self.assertEquals(current, self.a)
        current = manager.receive(current, True)
        current = manager.receive(current, False)
        self.assertEquals(current, end)
        self.assertRaises(TypeError, manager.receive, current)
