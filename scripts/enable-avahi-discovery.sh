#!/bin/sh
# Register the Wordclock's web API for Home Assistant discovery on Raspberry Pi OS.
set -eu

if [ "$(id -u)" -ne 0 ]; then
    echo "Run with sudo: sudo $0 [port]" >&2
    exit 1
fi

port=${1:-80}
case "$port" in
    ''|*[!0-9]*) echo "Expected a port between 1 and 65535" >&2; exit 1 ;;
esac
if [ "$#" -gt 1 ] || ! [ "$port" -ge 1 ] || ! [ "$port" -le 65535 ]; then
    echo "Usage: $0 [port between 1 and 65535]" >&2
    exit 1
fi

if [ ! -d /etc/avahi/services ] || ! systemctl is-active --quiet avahi-daemon; then
    echo "Install avahi-daemon and start it before running this script." >&2
    exit 1
fi

# Derive a stable ID for this application without publishing /etc/machine-id.
device_id=$(systemd-id128 --app-specific=3976ade8224247b4973f4f01f20b5637 machine-id)
if ! printf '%s\n' "$device_id" | grep -Eq '^[0-9a-f]{32}$'; then
    echo "Could not generate the Wordclock discovery ID" >&2
    exit 1
fi

service=/etc/avahi/services/rpi-wordclock.service
temp=$(mktemp "${service}.XXXXXX")
trap 'rm -f -- "$temp"' EXIT
cat > "$temp" <<XML
<?xml version="1.0" standalone="no"?>
<!DOCTYPE service-group SYSTEM "avahi-service.dtd">
<service-group>
  <name replace-wildcards="yes">Wordclock on %h</name>
  <service protocol="ipv4">
    <type>_rpi-wordclock._tcp</type>
    <port>$port</port>
    <txt-record>id=$device_id</txt-record>
  </service>
</service-group>
XML

chmod 0644 "$temp"
mv -f -- "$temp" "$service"
echo "Wordclock discovery enabled on HTTP port $port."
