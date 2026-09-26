"""Suite-wide guards."""
import traceback

import pytest

from engine.cycle import CycleSimulator


def pytest_configure(config):
    config.addinivalue_line("markers", "allows_phase_crash: the test crashes a phase on purpose")


@pytest.fixture(autouse=True)
def phase_crashes_fail_the_test(request, monkeypatch):
    """The executor survives a crashed phase, so a test would pass through one; fail it instead."""
    crashes = []
    real = CycleSimulator.handle_phase_crash

    def record(self, ctx, phase_name, error):
        crashes.append(f"{phase_name}: " + "".join(traceback.format_exception(type(error), error, error.__traceback__)))
        return real(self, ctx, phase_name, error)

    monkeypatch.setattr(CycleSimulator, "handle_phase_crash", record)
    yield
    allowed = getattr(request.instance, "ALLOWS_PHASE_CRASH", False) or request.node.get_closest_marker("allows_phase_crash")
    if crashes and not allowed:
        pytest.fail(f"{len(crashes)} phase crash(es) swallowed during the test:\n" + "\n".join(crashes), pytrace=False)
