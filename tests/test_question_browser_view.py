import sys

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QListWidgetItem

from doughub.ui.question_browser_view import QuestionBrowserView


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


def test_filter_items(qapp):
    view = QuestionBrowserView()

    # Add items manually
    item1 = QListWidgetItem("Question 1")
    item1.setData(Qt.ItemDataRole.UserRole + 1, "This is the first question about heart")
    view.list_widget.addItem(item1)

    item2 = QListWidgetItem("Question 2")
    item2.setData(Qt.ItemDataRole.UserRole + 1, "This is the second question about lung")
    view.list_widget.addItem(item2)

    item3 = QListWidgetItem("Question 3")
    item3.setData(Qt.ItemDataRole.UserRole + 1, "Another heart question")
    view.list_widget.addItem(item3)

    # Filter by "heart"
    view._filter_items("heart")
    assert not view.list_widget.item(0).isHidden()
    assert view.list_widget.item(1).isHidden()
    assert not view.list_widget.item(2).isHidden()

    # Filter by "LUNG" (case insensitive)
    view._filter_items("LUNG")
    assert view.list_widget.item(0).isHidden()
    assert not view.list_widget.item(1).isHidden()
    assert view.list_widget.item(2).isHidden()

    # Clear filter
    view._filter_items("")
    assert not view.list_widget.item(0).isHidden()
    assert not view.list_widget.item(1).isHidden()
    assert not view.list_widget.item(2).isHidden()
