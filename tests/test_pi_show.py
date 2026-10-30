"""The Show device's firewall and services, rendered into a temp dir."""
import os
import re
import shutil
import subprocess

import pytest

from conftest import ROOT

RENDER = ROOT / "pi-show/render.sh"
BASH = shutil.which("bash")


def render(tmp_path, ip="192.0.2.10", user="kiosk"):
    env = {"PATH": os.environ["PATH"], "HA_HOST_IP": ip, "KIOSK_USER": user}
    return subprocess.run([BASH, str(RENDER), str(tmp_path)], env=env, capture_output=True, text=True)


def test_firewall_admits_only_home_assistant_to_the_satellite(tmp_path):
    assert render(tmp_path).returncode == 0
    nft = (tmp_path / "etc/nftables.conf").read_text()
    assert "@HA_HOST_IP@" not in nft
    assert "type filter hook input priority 0; policy drop;" in nft
    accepts = [line.strip() for line in nft.splitlines() if "dport 10700" in line]
    assert accepts == ["ip saddr 192.0.2.10 tcp dport 10700 accept"]
    assert "dport 22" not in nft


def test_forwarding_is_dropped(tmp_path):
    render(tmp_path)
    nft = (tmp_path / "etc/nftables.conf").read_text()
    assert re.search(r"chain forward \{[^}]*policy drop", nft)


@pytest.mark.parametrize("bad", ["0.0.0.0", "0.0.0.0/0", "192.0.2.0/24", "192.0.2.10 accept; ip saddr 0.0.0.0/0",
                                 "homeassistant.local", "256.1.1.1", ""])
def test_rejects_anything_but_one_ipv4_host(tmp_path, bad):
    r = render(tmp_path, ip=bad)
    assert r.returncode != 0
    assert not (tmp_path / "etc/nftables.conf").exists()


@pytest.mark.parametrize("bad", ["root", "kiosk; rm -rf /", "Kiosk", ""])
def test_rejects_unsafe_user_names(tmp_path, bad):
    assert render(tmp_path, user=bad).returncode != 0


def test_services_run_as_the_kiosk_user(tmp_path):
    render(tmp_path, user="show")
    for unit in ("home-show-wakeword.service", "home-show-satellite.service"):
        text = (tmp_path / "etc/systemd/system" / unit).read_text()
        assert "User=show" in text and "@USER@" not in text


def test_wake_word_service_listens_on_localhost_only(tmp_path):
    render(tmp_path)
    wake = (tmp_path / "etc/systemd/system/home-show-wakeword.service").read_text()
    sat = (tmp_path / "etc/systemd/system/home-show-satellite.service").read_text()
    assert "--uri tcp://127.0.0.1:10400" in wake
    assert "--wake-uri tcp://127.0.0.1:10400" in sat


def test_install_validates_before_installing_anything():
    text = (ROOT / "pi-show/install.sh").read_text()
    check = text.index('render.sh" "$(mktemp -d)"')
    assert check < text.index("apt-get install")


def test_example_env_has_every_setting_the_scripts_read():
    example = (ROOT / "pi-show/home-show.env.example").read_text()
    names = set(re.findall(r"^([A-Z_]+)=", example, re.M))
    used = set()
    for path in [*(ROOT / "pi-show").glob("*.sh"), *(ROOT / "pi-show/systemd").glob("*.service")]:
        used |= set(re.findall(r"\$\{?([A-Z][A-Z_]+)", path.read_text()))
    used -= {"EUID", "HERE", "ENV_FILE", "KHOME", "TERM", "ROOT", "URL", "WAYLAND_DISPLAY"}
    assert used <= names, f"missing from home-show.env.example: {used - names}"
