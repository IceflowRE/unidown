import unittest

from packaging.version import InvalidVersion

from unidown.plugin.plugin_info import PluginInfo
from unidown.plugin.protobuf.plugin_info_pb2 import PluginInfoProto


class PluginInfoTest(unittest.TestCase):
    def setUp(self):
        self.info = PluginInfo('Blub', '1.0.0', 'example.com')

    def test_init(self):
        with self.subTest(desc="name empty"):
            with self.assertRaises(ValueError) as rai:
                PluginInfo('', '1.0.0', 'example.com')
            self.assertEqual('Plugin name cannot be empty.', str(rai.exception))

        with self.subTest(desc="host empty"):
            with self.assertRaises(ValueError) as rai:
                PluginInfo('Blub', '1.0.0', '')
            self.assertEqual('Plugin host cannot be empty.', str(rai.exception))

        with self.subTest(desc="invalid version"):
            version = '1.0.0.dd'
            with self.assertRaises(InvalidVersion) as rai:
                PluginInfo('Blub', version, 'example.com')
            self.assertEqual(f"Plugin version is not PEP440 conform: {version}", str(rai.exception))

    def test_equality(self):
        with self.subTest(desc="different type"):
            self.assertFalse(self.info == "blub")
            self.assertTrue(self.info != "blub")
        with self.subTest(desc="equal"):
            plugin = PluginInfo('Blub', '1.0.0', 'example.com')
            self.assertTrue(self.info == plugin)
            self.assertFalse(self.info != plugin)
        with self.subTest(desc="unequal"):
            plugin = PluginInfo('Whatever', '1.0.0', 'example.com')
            self.assertFalse(self.info == plugin)
            self.assertTrue(self.info != plugin)
            plugin = PluginInfo('Blub', '2.4.5', 'example.com')
            self.assertFalse(self.info == plugin)
            self.assertTrue(self.info != plugin)
            plugin = PluginInfo('Blub', '1.0.0', 'example.org')
            self.assertFalse(self.info == plugin)
            self.assertTrue(self.info != plugin)

    def test_str(self):
        self.assertEqual('Blub - 1.0.0 : example.com', str(self.info))

    def test_from_protobuf(self):
        with self.subTest(desc="name empty"):
            proto = PluginInfoProto()
            proto.name = ""
            with self.assertRaises(ValueError):
                PluginInfo.from_protobuf(proto)

        with self.subTest(desc="version empty"):
            proto = PluginInfoProto()
            proto.name = "blub"
            proto.version = ""
            with self.assertRaises(ValueError):
                PluginInfo.from_protobuf(proto)

        with self.subTest(desc="host empty"):
            proto = PluginInfoProto()
            proto.name = "blub"
            proto.version = "1.0.0"
            proto.host = ""
            with self.assertRaises(ValueError):
                PluginInfo.from_protobuf(proto)
