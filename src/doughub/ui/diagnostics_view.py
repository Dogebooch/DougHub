"""Diagnostics view for displaying logs and system information."""

import platform
import sys
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import BodyLabel, PrimaryPushButton, TitleLabel

from doughub import __version__ as app_version


class DiagnosticsView(QWidget):
    """View for displaying application logs and diagnostics.

    Provides a read-only log viewer and export functionality for
    debugging and bug reporting.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the diagnostics view.

        Args:
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the diagnostics view UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title = TitleLabel("Diagnostics & Logs")
        layout.addWidget(title)

        # Description
        description = BodyLabel(
            "View application logs and export diagnostic information for bug reports."
        )
        description.setWordWrap(True)
        layout.addWidget(description)

        # System info label
        self.system_info_label = BodyLabel()
        self.system_info_label.setText(self._get_system_info())
        self.system_info_label.setWordWrap(True)
        layout.addWidget(self.system_info_label)

        # Log text view
        self.log_text_edit = QTextEdit()
        self.log_text_edit.setReadOnly(True)
        self.log_text_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

        # Use monospaced font for better log readability
        font = QFont("Consolas", 9)
        if not font.exactMatch():
            font = QFont("Courier New", 9)
        self.log_text_edit.setFont(font)

        layout.addWidget(self.log_text_edit, stretch=1)

        # Button toolbar
        button_layout = QHBoxLayout()

        self.export_button = PrimaryPushButton("Export Logs")
        self.export_button.clicked.connect(self._export_logs)
        button_layout.addWidget(self.export_button)

        self.clear_button = PrimaryPushButton("Clear Display")
        self.clear_button.clicked.connect(self.log_text_edit.clear)
        button_layout.addWidget(self.clear_button)

        button_layout.addStretch()

        layout.addLayout(button_layout)

    def _get_system_info(self) -> str:
        """Get system information string.

        Returns:
            Formatted system information.
        """
        try:
            version = app_version
        except Exception:
            version = "unknown"

        info = [
            f"DougHub Version: {version}",
            f"Python: {sys.version.split()[0]}",
            f"OS: {platform.system()} {platform.release()}",
            f"Platform: {platform.platform()}",
        ]
        return " | ".join(info)

    def _export_logs(self) -> None:
        """Export logs and system info to a text file."""
        # Generate default filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"doughub_diagnostics_{timestamp}.txt"

        # Open file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Diagnostics",
            default_filename,
            "Text Files (*.txt);;All Files (*.*)"
        )

        if not file_path:
            return

        try:
            # Prepare export content
            content_parts = [
                "=" * 80,
                "DougHub Diagnostics Export",
                "=" * 80,
                "",
                "System Information:",
                "-" * 80,
                self._get_system_info_detailed(),
                "",
                "Application Logs:",
                "-" * 80,
                self.log_text_edit.toPlainText(),
                "",
                "=" * 80,
                f"Generated: {datetime.now().isoformat()}",
                "=" * 80,
            ]

            content = "\n".join(content_parts)

            # Write to file
            Path(file_path).write_text(content, encoding="utf-8")

            # Show success message via status (parent window should handle this)
            from qfluentwidgets import InfoBar, InfoBarPosition
            InfoBar.success(
                title="Export Successful",
                content=f"Diagnostics saved to:\n{file_path}",
                orient=Qt.Orientation.Vertical,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=3000,
                parent=self.window()
            )

        except Exception as e:
            from qfluentwidgets import InfoBar, InfoBarPosition
            InfoBar.error(
                title="Export Failed",
                content=f"Failed to export diagnostics:\n{e}",
                orient=Qt.Orientation.Vertical,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=5000,
                parent=self.window()
            )

    def _get_system_info_detailed(self) -> str:
        """Get detailed system information for export.

        Returns:
            Detailed formatted system information.
        """
        try:
            version = app_version
        except Exception:
            version = "unknown"

        info_lines = [
            f"DougHub Version: {version}",
            f"Python Version: {sys.version}",
            f"Python Executable: {sys.executable}",
            f"Operating System: {platform.system()} {platform.release()}",
            f"Platform: {platform.platform()}",
            f"Architecture: {platform.machine()}",
            f"Processor: {platform.processor()}",
        ]

        return "\n".join(info_lines)

    def get_log_widget(self) -> QTextEdit:
        """Get the log text widget for connecting to logging handler.

        Returns:
            The QTextEdit widget displaying logs.
        """
        return self.log_text_edit
