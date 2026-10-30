"""Security and consistency rules for every ESPHome device, checked without compiling."""
import re

import pytest

from conftest import ROOT, Tag, load

ESPHOME = ROOT / "esphome"
DEVICES = sorted(p for p in ESPHOME.glob("*.yaml") if p.name != "secrets.example.yaml")
BASE = load(ESPHOME / "common/base.yaml")
SECRETS = load(ESPHOME / "secrets.example.yaml")


def secrets_used(text):
    return set(re.findall(r"!secret\s+([a-z0-9_]+)", text))


@pytest.mark.parametrize("path", DEVICES, ids=lambda p: p.name)
def test_device_uses_the_shared_base(path):
    conf = load(path)
    assert conf["packages"]["base"].tag == "include"
    assert conf["packages"]["base"] == "common/base.yaml"


@pytest.mark.parametrize("path", DEVICES, ids=lambda p: p.name)
def test_device_opens_nothing_extra(path):
    conf = load(path)
    for banned in ("web_server", "captive_portal", "improv_serial", "esp32_improv", "mqtt"):
        assert banned not in conf, f"{path.name} enables {banned}"
    assert "ap" not in conf.get("wifi", {}), "no fallback hotspot"


@pytest.mark.parametrize("path", DEVICES, ids=lambda p: p.name)
def test_device_has_its_own_api_key(path):
    key = load(path)["substitutions"]["api_key"]
    assert isinstance(key, Tag) and key.tag == "secret"
    assert key in SECRETS


def test_api_keys_are_not_shared():
    keys = [load(p)["substitutions"]["api_key"] for p in DEVICES]
    names = [load(p)["substitutions"]["name"] for p in DEVICES]
    assert len(set(keys)) == len(keys)
    assert len(set(names)) == len(names)


def test_base_encrypts_the_api_and_protects_ota():
    assert BASE["api"]["encryption"]["key"] == "${api_key}"
    [ota] = BASE["ota"]
    assert ota["password"].tag == "secret"
    assert "ap" not in BASE["wifi"]
    assert "web_server" not in BASE and "captive_portal" not in BASE


def test_every_secret_has_an_example():
    used = set()
    for path in [*DEVICES, ESPHOME / "common/base.yaml"]:
        used |= secrets_used(path.read_text())
    assert used <= set(SECRETS), f"missing from secrets.example.yaml: {used - set(SECRETS)}"


def test_example_secrets_are_placeholders():
    for name, value in SECRETS.items():
        if name.startswith("api_key"):
            assert value == "REPLACE_WITH_openssl_rand_base64_32", name
        else:
            assert "example" in value, name


def test_dot_clock_is_a_thin_satellite():
    conf = load(ESPHOME / "dot-clock.yaml")
    assert conf["voice_assistant"]["micro_wake_word"] == "mww"
    assert "micro_wake_word" in conf
    # URLs in the config are downloaded at build time; at runtime the device only talks to HA.
    for component in ("http_request", "online_image", "mqtt", "udp"):
        assert component not in conf, component
