from pathlib import Path

from kratos.core.util.vault import FileVault


def test_filevault_write_file_persists_to_correct_paths(tmp_path):
    vault = FileVault(workspace_dir=str(tmp_path), use_sqlite=True)

    session_id = "session-int"
    namespace = "finance"
    session_file = "/reports/session.txt"
    persistent_file = "/reports/persistent.txt"

    session_content = "integration session content"
    persistent_content = "integration persistent content"

    session_file_id = vault.write_file(
        session_file,
        session_content,
        session_id=session_id,
        namespace=namespace,
    )
    persistent_file_id = vault.write_file(
        persistent_file,
        persistent_content,
        namespace=namespace,
    )

    session_expected_path = Path(tmp_path) / "sessions" / session_id / "reports" / "session.txt"
    persistent_expected_path = (
        Path(tmp_path) / "persistent" / namespace / "reports" / "persistent.txt"
    )

    assert session_expected_path.exists()
    assert session_expected_path.read_text(encoding="utf-8") == session_content

    assert persistent_expected_path.exists()
    assert persistent_expected_path.read_text(encoding="utf-8") == persistent_content

    assert vault.read_file(session_file, namespace=namespace, session_id=session_id) == session_content
    assert vault.read_file(persistent_file, namespace=namespace) == persistent_content

    session_records = vault.list_files(session_id=session_id)
    assert any(
        Path(record["storage_path"]) == session_expected_path and record["file_id"] == session_file_id
        for record in session_records
    )

    persistent_records = vault.list_files(namespace=namespace)
    assert any(
        record["session_id"] is None
        and record["file_id"] == persistent_file_id
        and Path(record["storage_path"]) == persistent_expected_path
        for record in persistent_records
    )
