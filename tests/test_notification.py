"""
Unit tests for notification module
"""
import pytest
from unittest.mock import patch, MagicMock
from clipper_agent.notification import NotificationWindow, show_notification

@patch("clipper_agent.notification.tk")
@patch("clipper_agent.notification.threading")
def test_notification_window_show(mock_threading, mock_tk):
    """Test NotificationWindow.show calls tkinter methods correctly"""
    # Setup mocks
    mock_tk_instance = MagicMock()
    mock_tk.Tk.return_value = mock_tk_instance

    # Mock font
    mock_font = MagicMock()
    with patch("clipper_agent.notification.tkfont.Font", return_value=mock_font):
        # Create window instance
        notification = NotificationWindow("Test Title", "Test Message", timeout=1)

        # Call show (this usually starts mainloop, so we need to mock mainloop to return immediately)
        mock_tk_instance.mainloop.side_effect = None

        # We need to prevent the separate thread creation or mock it
        # The auto_close thread is created in show()

        notification.show()

        # Verify Tk was initialized
        mock_tk.Tk.assert_called_once()

        # Verify title and attributes
        mock_tk_instance.title.assert_called_with("LLM Clipper")
        mock_tk_instance.attributes.assert_called_with("-topmost", True)
        mock_tk_instance.overrideredirect.assert_called_with(True)

        # Verify geometry calculation (it calls update_idletasks and winfo_*)
        mock_tk_instance.update_idletasks.assert_called()

        # Verify deiconify
        mock_tk_instance.deiconify.assert_called()

        # Verify mainloop was called
        mock_tk_instance.mainloop.assert_called_once()

@patch("clipper_agent.notification.NotificationWindow")
@patch("clipper_agent.notification.threading")
def test_show_notification_function(mock_threading, mock_notification_window):
    """Test show_notification wrapper function"""

    # Setup mocks
    mock_thread_instance = MagicMock()
    mock_threading.Thread.return_value = mock_thread_instance

    show_notification("Title", "Message")

    # Verify thread creation
    mock_threading.Thread.assert_called_once()

    # Check that daemon attribute was set on the instance
    assert mock_thread_instance.daemon is False

    # Verify thread start
    mock_thread_instance.start.assert_called_once()

@patch("clipper_agent.notification.tk")
def test_notification_color_style(mock_tk):
    """Test that error and success notifications have different styles"""
    mock_tk_instance = MagicMock()
    mock_tk.Tk.return_value = mock_tk_instance

    with patch("clipper_agent.notification.tk.Frame") as mock_frame, \
         patch("clipper_agent.notification.tk.Label") as mock_label, \
         patch("clipper_agent.notification.tkfont.Font"):

        # Test Success Style
        success_notification = NotificationWindow("Success", "Msg")
        success_notification.show()

        # Check that Frame and Label were called with success colors
        # Note: This is a bit fragile as it depends on exact implementation details
        # But we can check that different calls happened
        frame_calls = mock_frame.call_args_list
        label_calls = mock_label.call_args_list

        assert len(frame_calls) > 0
        success_bg = frame_calls[0][1]['bg']

        # Reset mocks
        mock_frame.reset_mock()
        mock_label.reset_mock()

        # Test Error Style
        error_notification = NotificationWindow("エラー", "Msg")
        error_notification.show()

        assert len(mock_frame.call_args_list) > 0
        error_bg = mock_frame.call_args_list[0][1]['bg']

        assert success_bg != error_bg
        assert error_bg == "#ffeb3b" # Yellow from code
