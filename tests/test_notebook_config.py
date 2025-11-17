"""Tests for notebook configuration and directory management."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from doughub import config
from doughub.notebook.manager import NotesiumManager


class TestNotebookConfig:
    """Test notebook configuration loading and validation."""

    def test_notes_dir_default(self) -> None:
        """Test that NOTES_DIR has a sensible default."""
        assert config.NOTES_DIR is not None
        assert isinstance(config.NOTES_DIR, str)
        # Should be in user's home directory
        assert ".doughub" in config.NOTES_DIR or "doughub" in config.NOTES_DIR.lower()

    def test_notesium_port_default(self) -> None:
        """Test that NOTESIUM_PORT has a valid default."""
        assert config.NOTESIUM_PORT == 3030
        assert isinstance(config.NOTESIUM_PORT, int)
        assert 1024 <= config.NOTESIUM_PORT <= 65535

    def test_notes_dir_from_env(self) -> None:
        """Test that NOTES_DIR can be overridden via environment variable."""
        test_path = "/custom/notes/path"
        with patch.dict(os.environ, {"NOTES_DIR": test_path}):
            # Re-import to pick up env var
            import importlib
            importlib.reload(config)
            assert config.NOTES_DIR == test_path

    def test_notesium_port_from_env(self) -> None:
        """Test that NOTESIUM_PORT can be overridden via environment variable."""
        with patch.dict(os.environ, {"NOTESIUM_PORT": "5000"}):
            import importlib
            importlib.reload(config)
            assert config.NOTESIUM_PORT == 5000


class TestNotesDirectoryCreation:
    """Test notes directory creation and permissions handling."""

    def test_manager_creates_notes_directory(self, tmp_path: Path) -> None:
        """Test that NotesiumManager creates the notes directory."""
        notes_dir = tmp_path / "test_notes"
        assert not notes_dir.exists()

        manager = NotesiumManager(notes_dir=str(notes_dir), port=9999)
        # Start will attempt to create directory
        manager.start()
        manager.stop()

        assert notes_dir.exists()
        assert notes_dir.is_dir()

    def test_manager_handles_existing_directory(self, tmp_path: Path) -> None:
        """Test that manager works with pre-existing directory."""
        notes_dir = tmp_path / "existing_notes"
        notes_dir.mkdir()

        manager = NotesiumManager(notes_dir=str(notes_dir), port=9998)
        # Should not raise an error
        manager.start()
        manager.stop()

        assert notes_dir.exists()

    def test_manager_handles_invalid_path_gracefully(self) -> None:
        """Test that manager handles invalid paths without crashing."""
        # Use a path that's likely to fail (null byte in Windows/Unix)
        invalid_path = "/invalid\x00path"

        manager = NotesiumManager(notes_dir=invalid_path, port=9997)
        # start() should return False and log error, not crash
        result = manager.start()

        assert result is False
        assert not manager.is_healthy()
        manager.stop()

    def test_notes_directory_with_spaces(self, tmp_path: Path) -> None:
        """Test notes directory with spaces in the path."""
        notes_dir = tmp_path / "my notes folder"
        manager = NotesiumManager(notes_dir=str(notes_dir), port=9996)

        manager.start()
        manager.stop()

        assert notes_dir.exists()

    def test_notes_directory_with_unicode(self, tmp_path: Path) -> None:
        """Test notes directory with unicode characters."""
        notes_dir = tmp_path / "notes_测试_тест"
        manager = NotesiumManager(notes_dir=str(notes_dir), port=9995)

        manager.start()
        manager.stop()

        assert notes_dir.exists()

    def test_nested_directory_creation(self, tmp_path: Path) -> None:
        """Test that manager creates nested directories (parents=True)."""
        notes_dir = tmp_path / "level1" / "level2" / "notes"
        assert not notes_dir.exists()

        manager = NotesiumManager(notes_dir=str(notes_dir), port=9994)
        manager.start()
        manager.stop()

        assert notes_dir.exists()
        assert (tmp_path / "level1").exists()
        assert (tmp_path / "level1" / "level2").exists()


class TestConfigEdgeCases:
    """Test configuration edge cases and error conditions."""

    def test_config_change_detection(self, tmp_path: Path) -> None:
        """Test that changing config requires manager restart."""
        notes_dir_1 = tmp_path / "notes1"
        notes_dir_2 = tmp_path / "notes2"

        # Create manager with first directory
        manager = NotesiumManager(notes_dir=str(notes_dir_1), port=9993)
        assert manager.notes_dir == notes_dir_1

        # Changing notes_dir on existing manager
        manager.notes_dir = notes_dir_2
        manager.start()
        manager.stop()

        # Both directories should now exist
        assert notes_dir_2.exists()

    def test_relative_path_handling(self) -> None:
        """Test that relative paths in config are handled correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Change to temp directory
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                relative_path = "./my_notes"

                manager = NotesiumManager(notes_dir=relative_path, port=9992)
                manager.start()
                manager.stop()

                # Verify directory was created relative to cwd
                assert Path(tmpdir, "my_notes").exists()
            finally:
                os.chdir(original_cwd)
