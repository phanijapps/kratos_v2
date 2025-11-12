from pathlib import Path

from kratos.core.middleware.vault import FileVault


def test_write_file_creates_session_file_and_metadata(tmp_path):
    vault = FileVault(workspace_dir=str(tmp_path), use_sqlite=False)
    session_id = "session-123"
    file_path = "/reports/output.txt"
    content = "vault writes this"

    file_id = vault.write_file(file_path, content, namespace="research", session_id=session_id)

    expected_path = Path(tmp_path) / "sessions" / session_id / "reports" / "output.txt"
    assert expected_path.exists()
    assert expected_path.read_text(encoding="utf-8") == content
    assert file_id in vault.metadata

    record = vault.metadata[file_id]
    assert record["file_path"] == file_path
    assert record["namespace"] == "research"
    assert record["session_id"] == session_id
    assert record["size_bytes"] == len(content)
    assert record["storage_path"] == expected_path.as_posix()
