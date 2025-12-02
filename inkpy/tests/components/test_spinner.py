"""
Tests for Spinner component.

Spinner provides an animated loading indicator with:
- Multiple spinner types/styles
- Custom text alongside spinner
- Animation frame cycling
"""

import pytest


class TestSpinnerImport:
    """Test Spinner can be imported"""

    def test_spinner_imports(self):
        """Spinner should be importable from components"""
        from inkpy.components.spinner import Spinner

        assert Spinner is not None
        assert callable(Spinner)


class TestSpinnerProps:
    """Test Spinner prop handling"""

    def test_spinner_default(self):
        """Spinner should work with default props"""
        from inkpy.components.spinner import Spinner

        element = Spinner()
        assert element is not None

    def test_spinner_with_text(self):
        """Spinner should accept text prop"""
        from inkpy.components.spinner import Spinner

        element = Spinner(text="Loading...")
        assert element is not None

    def test_spinner_with_type(self):
        """Spinner should accept type prop for different styles"""
        from inkpy.components.spinner import Spinner

        dots = Spinner(type="dots")
        line = Spinner(type="line")
        arc = Spinner(type="arc")
        assert dots is not None
        assert line is not None
        assert arc is not None

    def test_spinner_with_color(self):
        """Spinner should accept color prop"""
        from inkpy.components.spinner import Spinner

        element = Spinner(color="cyan")
        assert element is not None


class TestSpinnerTypes:
    """Test spinner type definitions"""

    def test_spinner_types_available(self):
        """SPINNER_TYPES should be available"""
        from inkpy.components.spinner import SPINNER_TYPES

        assert isinstance(SPINNER_TYPES, dict)
        assert "dots" in SPINNER_TYPES
        assert "line" in SPINNER_TYPES

    def test_spinner_type_has_frames(self):
        """Each spinner type should have frames"""
        from inkpy.components.spinner import SPINNER_TYPES

        for name, config in SPINNER_TYPES.items():
            assert "frames" in config
            assert isinstance(config["frames"], (list, tuple))
            assert len(config["frames"]) > 0

    def test_spinner_type_has_interval(self):
        """Each spinner type should have interval"""
        from inkpy.components.spinner import SPINNER_TYPES

        for name, config in SPINNER_TYPES.items():
            assert "interval" in config
            assert isinstance(config["interval"], (int, float))
            assert config["interval"] > 0


class TestSpinnerStatus:
    """Test Spinner status states"""

    def test_spinner_status_enum_imports(self):
        """SpinnerStatus should be importable"""
        from inkpy.components.spinner import SpinnerStatus

        assert SpinnerStatus is not None
        assert SpinnerStatus.SPINNING.value == "spinning"
        assert SpinnerStatus.SUCCESS.value == "success"
        assert SpinnerStatus.FAILURE.value == "failure"
        assert SpinnerStatus.WARNING.value == "warning"
        assert SpinnerStatus.INFO.value == "info"

    def test_spinner_success_state(self):
        """Spinner should display success icon when status is SUCCESS"""
        from inkpy.components.spinner import Spinner, SpinnerStatus

        element = Spinner(text="Completed", status=SpinnerStatus.SUCCESS)
        assert element is not None

    def test_spinner_failure_state(self):
        """Spinner should display failure icon when status is FAILURE"""
        from inkpy.components.spinner import Spinner, SpinnerStatus

        element = Spinner(text="Failed", status=SpinnerStatus.FAILURE)
        assert element is not None

    def test_spinner_warning_state(self):
        """Spinner should display warning icon when status is WARNING"""
        from inkpy.components.spinner import Spinner, SpinnerStatus

        element = Spinner(text="Warning", status=SpinnerStatus.WARNING)
        assert element is not None

    def test_spinner_info_state(self):
        """Spinner should display info icon when status is INFO"""
        from inkpy.components.spinner import Spinner, SpinnerStatus

        element = Spinner(text="Info", status=SpinnerStatus.INFO)
        assert element is not None

    def test_spinner_custom_icons(self):
        """Spinner should accept custom icons for status states"""
        from inkpy.components.spinner import Spinner, SpinnerStatus

        element = Spinner(
            text="Done",
            status=SpinnerStatus.SUCCESS,
            success_icon="👍",
        )
        assert element is not None

    def test_spinner_status_default_colors(self):
        """SpinnerStatus should have default colors defined"""
        from inkpy.components.spinner import DEFAULT_STATUS_COLORS, SpinnerStatus

        assert DEFAULT_STATUS_COLORS[SpinnerStatus.SUCCESS] == "green"
        assert DEFAULT_STATUS_COLORS[SpinnerStatus.FAILURE] == "red"
        assert DEFAULT_STATUS_COLORS[SpinnerStatus.WARNING] == "yellow"
        assert DEFAULT_STATUS_COLORS[SpinnerStatus.INFO] == "blue"


class TestSpinnerExport:
    """Test Spinner is exported from components module"""

    def test_spinner_exported(self):
        """Spinner should be exported from inkpy.components"""
        from inkpy.components import Spinner

        assert Spinner is not None

    def test_spinner_status_exported(self):
        """SpinnerStatus should be exported from inkpy.components"""
        from inkpy.components import SpinnerStatus

        assert SpinnerStatus is not None
