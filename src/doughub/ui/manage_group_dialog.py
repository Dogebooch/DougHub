from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from doughub.models import Question


class ManageGroupDialog(QDialog):
    """Dialog to manage grouped questions (unlink children)."""

    unlink_requested = pyqtSignal(int)  # Emits child_id to unlink

    def __init__(self, parent_question: Question, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.parent_question = parent_question
        self.setWindowTitle(f"Manage Group: Q {parent_question.question_id}")
        self.resize(400, 300)
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Grouped Questions:"))

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        # Add children to list
        for child in self.parent_question.children:
            item = QListWidgetItem(self.list_widget)
            widget = QWidget()
            h_layout = QHBoxLayout(widget)
            h_layout.setContentsMargins(5, 2, 5, 2)

            label = QLabel(f"Q {child.question_id} - {child.source_question_key}")
            h_layout.addWidget(label)

            unlink_btn = QPushButton("Unlink")
            unlink_btn.clicked.connect(
                lambda checked, cid=child.question_id: self._on_unlink(cid)
            )
            h_layout.addWidget(unlink_btn)

            item.setSizeHint(widget.sizeHint())
            self.list_widget.setItemWidget(item, widget)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def _on_unlink(self, child_id: int) -> None:
        self.unlink_requested.emit(child_id)
        self.accept()  # Close dialog after action for simplicity
