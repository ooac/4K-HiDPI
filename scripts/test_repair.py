"""Offline tests: no display changes and no LaunchAgent installation."""
import json
import pathlib
import tempfile
import unittest
from unittest.mock import patch

import repair
import install


class RepairTests(unittest.TestCase):
    def setUp(self):
        self.source = {'_name': 'Remote 4K', '_spdisplays_pixels': '3840 x 2160',
                       '_spdisplays_resolution': '1920 x 1080 @ 60.00Hz',
                       'spdisplays_main': 'spdisplays_yes',
                       'spdisplays_mirror_status': 'spdisplays_master_mirror'}
        self.uu = dict(self.source, _name='UU远程 1',
                       spdisplays_mirror_status='spdisplays_hardware_mirror')
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.marker = patch.object(repair, 'FAILURE', pathlib.Path(self.folder.name) / 'paused')
        self.marker.start()
        self.addCleanup(self.marker.stop)

    def test_healthy_does_not_mutate(self):
        with patch.object(repair, 'screens', return_value=[self.source, self.uu]), patch.object(repair, 'run') as command:
            repair.repair()
            command.assert_not_called()

    def test_detects_regressions_and_accepts_single_screen(self):
        self.assertFalse(repair.needs_repair([self.source]))
        self.assertTrue(repair.needs_repair([self.uu]))
        self.assertTrue(repair.needs_repair([dict(self.source, _spdisplays_pixels='7680 x 4320')]))
        self.assertTrue(repair.needs_repair([self.source, dict(self.uu, spdisplays_mirror_status='off')]))

    def test_reconnection_uses_new_tag(self):
        devices = [{'deviceType': 'VirtualScreen', 'name': 'Remote 4K', 'tagID': '72', 'displayID': '91'},
                   {'deviceType': 'Display', 'name': 'UU远程 1', 'vendor': '21828', 'tagID': '999', 'displayID': '92'},
                   {'deviceType': 'Display', 'name': 'Physical Monitor', 'vendor': '1', 'tagID': '888', 'displayID': '93'}]
        identifiers = ','.join(json.dumps(device) for device in devices)
        broken = [self.source, dict(self.uu, spdisplays_mirror_status='off')]
        with patch.object(repair, 'screens', side_effect=[broken, [self.source, self.uu]]), patch.object(repair, 'run', return_value=identifiers) as command:
            repair.repair()
            command.assert_any_call(repair.BETTERDISPLAY, 'set', '-tagID=72', '-mirror=on', '-targetTagID=999')
            self.assertFalse(any('-targetTagID=888' in call.args for call in command.call_args_list))

    def test_failed_verification_raises(self):
        devices = json.dumps({'deviceType': 'VirtualScreen', 'name': 'Remote 4K', 'tagID': '72', 'displayID': '91'})
        with patch.object(repair, 'screens', return_value=[]), patch.object(repair, 'run', return_value=devices):
            with self.assertRaisesRegex(RuntimeError, 'verification failed'):
                repair.repair()

    def test_pause_marker_blocks_mutation(self):
        repair.FAILURE.write_text('A prior error needs inspection')
        with patch.object(repair, 'run') as command, patch.object(repair, 'screens') as read:
            repair.repair()
            command.assert_not_called()
            read.assert_not_called()

    def test_install_paths_follow_target_user(self):
        config = install.launch_configuration(pathlib.Path('/Users/another-user'), '/opt/python3')
        self.assertEqual(config['ProgramArguments'], ['/opt/python3', '/Users/another-user/Library/Application Support/UU4KRepair/repair.py'])
        self.assertEqual(config['StartInterval'], 15)


if __name__ == '__main__':
    unittest.main()
