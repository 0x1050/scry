import json
import subprocess

SERVICES = ['sshd', 'systemd-resolved']

def run_command(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

with open('/etc/os-release') as f:
    lines = f.readlines()

os_info = {}
for line in lines:
    line = line.strip()
    if '=' in line:
        key, val = line.split('=', 1)
        os_info[key] = val.strip('"')

output = {
        "distro": os_info.get('ID', 'unknown'),
        "distro_version": os_info.get('VERSION_ID', 'unknown')
}

pkg_list_command = ''
if output['distro'] in ['debian', 'ubuntu']:
    pkg_list_command = "dpkg-query --show --showformat='${Package}\t${Version}\n'"
    check_updates_command = "apt update >/dev/null 2>&1 && apt list --upgradable | grep -v '^Listing'"
elif output['distro'] == 'arch':
    pkg_list_command = "pacman -Q"
    check_updates_command = "checkupdates"
else:
    raise Exception(f"Unsupported distro: {output['distro']}")

output_lines =  run_command(pkg_list_command)
packages = []
for line in output_lines.strip().split('\n'):
    if line:
        name, version = line.split(None, 1)
        packages.append({"name": name, "version": version})

service_list = run_command('systemctl list-units --type=service --state=running --no-legend --plain')
running_services = []
for line in service_list.split('\n'):
    if line.strip():
        parts = line.split()
        if parts:
            running_services.append(parts[0])

active_services = []
for service in SERVICES:
    status = run_command(f'systemctl is-active {service}')
    active_services.append({"name": service, "status": status})

output["packages"] = packages
output["running_services"] = running_services
output["services"] = active_services

print(json.dumps(output, indent=2))














