"""Tests for callback handling functionality."""

from unittest.mock import Mock

from autoupdate.autoupdate import call_callback


class TestCallCallback:
    """Tests for call_callback function."""

    def test_calls_callback_with_args(self):
        """Test that callback is called with provided arguments."""
        callback = Mock()
        args = (1, 2, 3)

        call_callback(callback, *args)

        callback.assert_called_once_with(1, 2, 3)

    def test_calls_callback_with_kwargs(self):
        """Test that callback is called with keyword arguments."""
        callback = Mock()
        kwargs = {"key1": "value1", "key2": "value2"}

        call_callback(callback, **kwargs)

        callback.assert_called_once_with(key1="value1", key2="value2")

    def test_calls_callback_with_args_and_kwargs(self):
        """Test that callback is called with both args and kwargs."""
        callback = Mock()

        call_callback(callback, 1, 2, key="value")

        callback.assert_called_once_with(1, 2, key="value")

    def test_callback_exception_is_caught(self):
        """Test that exceptions from callback are caught and logged."""
        callback = Mock(side_effect=ValueError("Test error"))

        # Should not raise exception
        call_callback(callback, "arg1")

        # Callback should have been called
        callback.assert_called_once_with("arg1")

    def test_callback_with_no_args(self):
        """Test calling callback with no arguments."""
        callback = Mock()

        call_callback(callback)

        callback.assert_called_once_with()

    def test_multiple_exceptions_are_handled(self):
        """Test that different exception types are handled."""
        # Test with various exception types
        exceptions = [
            ValueError("value error"),
            TypeError("type error"),
            KeyError("key error"),
            RuntimeError("runtime error"),
        ]

        for exc in exceptions:
            callback = Mock(side_effect=exc)
            # Should not raise
            call_callback(callback, "test")
            callback.assert_called_once()

    def test_callback_return_value_when_successful(self):
        """Test that callback return value is not used (void function)."""
        callback = Mock(return_value="some_value")

        # call_callback doesn't return anything
        result = call_callback(callback, "arg")

        assert result is None
        callback.assert_called_once_with("arg")

    def test_callback_with_complex_args(self):
        """Test callback with complex argument types."""
        callback = Mock()
        args = ([1, 2, 3], {"key": "value"}, None, 42)

        call_callback(callback, *args)

        callback.assert_called_once_with([1, 2, 3], {"key": "value"}, None, 42)

    def test_callback_exception_logged(self, caplog):
        """Test that callback exceptions are logged."""
        import logging

        callback = Mock(side_effect=ValueError("Test exception"))

        with caplog.at_level(logging.ERROR):
            call_callback(callback, "arg1", "arg2")

        # Should have logged the exception
        assert len(caplog.records) == 1
        assert "Failed calling callback" in caplog.text
        assert "Test exception" in caplog.text

    def test_preserves_callback_side_effects(self):
        """Test that callback side effects are executed before exception."""
        side_effect_list = []

        def callback_with_side_effect(value):
            side_effect_list.append(value)
            raise ValueError("Error after side effect")

        call_callback(callback_with_side_effect, "test_value")

        # Side effect should have occurred
        assert side_effect_list == ["test_value"]

    def test_callback_with_nested_structures(self):
        """Test callback with deeply nested data structures."""
        callback = Mock()
        nested_data = {"outer": {"inner": {"deep": [1, 2, {"nested": "value"}]}}}

        call_callback(callback, nested_data)

        callback.assert_called_once_with(nested_data)
