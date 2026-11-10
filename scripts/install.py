"""Install the current user's UU 4K LaunchAgent; --dry-run only prints its plist."""
import os
import pathlib
import plistlib
import shutil
import subprocess
import sys

LABEL = 'local.mc.uu4k-repair'


def launch_configuration(home, interpreter):
    return {
        'Label': LABEL,
        'ProgramArguments': [str(interpreter), str(home / 'Library/Application Support/UU4KRepair/repair.py')],
        'RunAtLoad': True,
        'StartInterval': 15,
        'LimitLoadToSessionType': 'Aqua',
        'StandardOutPath': str(home / 'Library/Logs/UU4KRepair/repair.log'),
        'StandardErrorPath': str(home / 'Library/Logs/UU4KRepair/error.log'),
    }


def install():
    if sys.argv[1:] not in ([], ['--dry-run']):
        raise ValueError('Unsupported arguments: ' + repr(sys.argv[1:]))
    home = pathlib.Path.home()
    interpreter = pathlib.Path(sys.executable).resolve()
    configuration = plistlib.dumps(launch_configuration(home, interpreter))
    if sys.argv[1:] == ['--dry-run']:
        print(configuration.decode())
        return
    if sys.platform != 'darwin' or os.getuid() == 0:
        raise RuntimeError('Run as the logged-in macOS user, not root; platform=' + sys.platform)
    if not pathlib.Path('/Applications/BetterDisplay.app/Contents/MacOS/BetterDisplay').is_file():
        raise FileNotFoundError('/Applications/BetterDisplay.app/Contents/MacOS/BetterDisplay')
    destination = home / 'Library/Application Support/UU4KRepair'
    if (destination / 'paused-error.txt').exists():
        raise RuntimeError('Resolve the previous error before reinstalling: ' + str(destination / 'paused-error.txt'))
    # A read-only check ensures the manually configured baseline is healthy first.
    source = pathlib.Path(__file__).with_name('repair.py')
    subprocess.run([str(interpreter), str(source), '--check'], check=True, timeout=30)
    for folder in (destination, home / 'Library/LaunchAgents', home / 'Library/Logs/UU4KRepair'):
        folder.mkdir(parents=True, exist_ok=True)
    domain = 'gui/' + str(os.getuid())
    current = subprocess.run(['/bin/launchctl', 'print', domain + '/' + LABEL], capture_output=True, text=True)
    if current.returncode == 0:
        subprocess.run(['/bin/launchctl', 'bootout', domain + '/' + LABEL], check=True)
    elif current.returncode != 113:
        raise RuntimeError('Cannot inspect LaunchAgent: ' + str(current.returncode) + ' ' + current.stderr)
    shutil.copy2(source, destination / 'repair.py')
    plist = home / 'Library/LaunchAgents' / (LABEL + '.plist')
    plist.write_bytes(configuration)
    subprocess.run(['/usr/bin/plutil', '-lint', str(plist)], check=True)
    subprocess.run(['/bin/launchctl', 'bootstrap', domain, str(plist)], check=True)
    subprocess.run(['/bin/launchctl', 'print', domain + '/' + LABEL], check=True)
    print('Installed. Repair runs every 15 seconds. Logs: ' + str(home / 'Library/Logs/UU4KRepair'))


if __name__ == '__main__':
    install()
