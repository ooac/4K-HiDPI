import json
import pathlib
import subprocess
import sys
from datetime import datetime

BETTERDISPLAY = '/Applications/BetterDisplay.app/Contents/MacOS/BetterDisplay'
ROOT = pathlib.Path(__file__).resolve().parent
FAILURE = ROOT / 'paused-error.txt'


def run(*arguments):
    return subprocess.run(arguments, check=True, capture_output=True,
                          text=True, timeout=20).stdout


def screens():
    report = json.loads(run('/usr/sbin/system_profiler', 'SPDisplaysDataType', '-json'))
    return [screen for gpu in report['SPDisplaysDataType']
            for screen in gpu.get('spdisplays_ndrvs', [])]


def is_4k(screen):
    return (screen.get('_spdisplays_pixels') == '3840 x 2160'
            and screen.get('_spdisplays_resolution', '').startswith('1920 x 1080 @ 60'))


def needs_repair(displays):
    remote = [screen for screen in displays if screen['_name'] == 'Remote 4K']
    uu_screens = [screen for screen in displays if screen['_name'].startswith('UU远程')]
    if len(remote) != 1:
        return True
    source = remote[0]
    if not is_4k(source) or source.get('spdisplays_main') != 'spdisplays_yes':
        return True
    return bool(uu_screens) and (
        source.get('spdisplays_mirror_status') != 'spdisplays_master_mirror'
        or any(not is_4k(screen) or screen.get('spdisplays_mirror_status')
               != 'spdisplays_hardware_mirror' for screen in uu_screens))


def repair():
    if FAILURE.exists():
        return
    if not needs_repair(screens()):
        return
    devices = json.loads('[' + run(BETTERDISPLAY, 'get', '-identifiers') + ']')
    remote = [device for device in devices
              if device.get('deviceType') == 'VirtualScreen'
              and device.get('name') == 'Remote 4K']
    if len(remote) != 1:
        raise RuntimeError('Expected one Remote 4K virtual screen, found: ' + str(remote))
    source = '-tagID=' + remote[0]['tagID']
    if remote[0].get('displayID') == '0':
        run(BETTERDISPLAY, 'set', source, '-connected=on')
    run(BETTERDISPLAY, 'set', source, '-resolution=1920x1080', '-hiDPI=on', '-main=on')
    for device in devices:
        if (device.get('deviceType') == 'Display'
                and device.get('name', '').startswith('UU远程')
                and device.get('vendor') == '21828'
                and device.get('displayID', '0') != '0'):
            run(BETTERDISPLAY, 'set', source, '-mirror=on',
                '-targetTagID=' + device['tagID'])
    verified = screens()
    if needs_repair(verified):
        raise RuntimeError('4K mirror verification failed: ' + json.dumps(verified, ensure_ascii=False))
    print(datetime.now().isoformat(), 'Restored 4K HiDPI and UU mirroring.', flush=True)


if __name__ == '__main__':
    if sys.argv[1:] == ['--check']:
        current = screens()
        if needs_repair(current):
            raise RuntimeError('Baseline is not 4K HiDPI with UU mirroring: ' + json.dumps(current, ensure_ascii=False))
        print('Verified: 4K HiDPI baseline and any UU mirrors are healthy.')
        sys.exit(0)
    if sys.argv[1:]:
        raise ValueError('Unsupported arguments: ' + repr(sys.argv[1:]))
    try:
        repair()
    except (subprocess.SubprocessError, OSError, ValueError, KeyError, RuntimeError) as error:
        details = datetime.now().isoformat() + '\n' + repr(error)
        if isinstance(error, subprocess.CalledProcessError):
            details += '\n' + error.stdout + '\n' + error.stderr
        FAILURE.write_text(details + '\n')
        print(details + '\nAutomatic repair paused; inspect paused-error.txt before resuming.', file=sys.stderr)
        sys.exit(1)
