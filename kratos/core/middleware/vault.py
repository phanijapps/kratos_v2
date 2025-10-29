"""
FileVault - Intelligent Agent Filesystem
A production-ready, context-aware filesystem for AI agents with optional SQLite backend.

Features:
- Real disk storage with automatic directory management
- Session-based and persistent file storage
- Optional SQLite metadata backend for performance
- Context offloading support (summaries for large files)
- Multi-file session management with statistics
- Domain-agnostic (coding, finance, research, etc.)
"""

import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any
import hashlib
import logging

logger = logging.getLogger(__name__)


class FileVault:
    """
    FileVault: Intelligent filesystem for AI agents.
    
    Supports both JSON (simple) and SQLite (advanced) metadata backends.
    Perfect for multi-file agent sessions with automatic cleanup and tracking.
    """
    
    def __init__(
        self,
        workspace_dir: str = "./agent_workspace",
        use_sqlite: bool = True,
        auto_cleanup_days: int = 7,
        max_session_size_mb: int = 500,
        enable_versioning: bool = False
    ):
        """
        Initialize FileVault.
        
        Args:
            workspace_dir: Root directory for file storage
            use_sqlite: Use SQLite backend instead of JSON (recommended for production)
            auto_cleanup_days: Auto-delete sessions older than this (0 = disabled)
            max_session_size_mb: Warn when session exceeds this size
            enable_versioning: Keep file version history (requires SQLite)
        """
        self.workspace_dir = Path(workspace_dir)
        self.use_sqlite = use_sqlite
        self.auto_cleanup_days = auto_cleanup_days
        self.max_session_size_mb = max_session_size_mb
        self.enable_versioning = enable_versioning and use_sqlite
        
        # Create directory structure
        self.sessions_dir = self.workspace_dir / "sessions"
        self.persistent_dir = self.workspace_dir / "persistent"
        self.metadata_dir = self.workspace_dir / ".metadata"
        self.archive_dir = self.workspace_dir / ".archive"
        
        for dir_path in [self.sessions_dir, self.persistent_dir, 
                         self.metadata_dir, self.archive_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        
        # Initialize metadata backend
        if self.use_sqlite:
            self.db_path = self.metadata_dir / "filevault.db"
            self._init_sqlite()
            logger.info(f"FileVault initialized with SQLite backend: {self.db_path}")
        else:
            self.metadata_file = self.metadata_dir / "files_metadata.json"
            self._load_json_metadata()
            logger.info(f"FileVault initialized with JSON backend: {self.metadata_file}")
        
        # Session tracking
        self.session_stats = {}
    
    # ============================================================================
    # SQLITE BACKEND (Recommended for Production)
    # ============================================================================
    
    def _init_sqlite(self):
        """Initialize SQLite database with schema"""
        conn = sqlite3.connect(str(self.db_path))
        
        # Main files table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS files (
                file_id TEXT PRIMARY KEY,
                file_path TEXT NOT NULL,
                namespace TEXT NOT NULL,
                session_id TEXT,
                storage_path TEXT NOT NULL,
                content_hash TEXT,
                size_bytes INTEGER,
                mime_type TEXT,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 0,
                summary TEXT,
                UNIQUE(file_path, namespace, session_id)
            )
        """)
        
        # Session tracking table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                namespace TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_count INTEGER DEFAULT 0,
                total_bytes INTEGER DEFAULT 0,
                purpose TEXT,
                status TEXT DEFAULT 'active'
            )
        """)
        
        # File versions table (optional)
        if self.enable_versioning:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS file_versions (
                    version_id TEXT PRIMARY KEY,
                    file_id TEXT NOT NULL,
                    version_number INTEGER NOT NULL,
                    content_hash TEXT,
                    size_bytes INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by TEXT,
                    FOREIGN KEY (file_id) REFERENCES files(file_id) ON DELETE CASCADE
                )
            """)
        
        # Create indexes for performance
        conn.execute("CREATE INDEX IF NOT EXISTS idx_files_session ON files(session_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_files_namespace ON files(namespace)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_files_path ON files(file_path)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_created ON sessions(created_at)")
        
        conn.commit()
        conn.close()
    
    def _get_sqlite_connection(self) -> sqlite3.Connection:
        """Get SQLite connection with row factory"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn
    
    def _store_metadata_sqlite(
        self,
        file_id: str,
        file_path: str,
        namespace: str,
        session_id: Optional[str],
        storage_path: str,
        content_hash: str,
        size_bytes: int,
        tags: Optional[List[str]] = None
    ):
        """Store file metadata in SQLite"""
        conn = self._get_sqlite_connection()
        cursor = conn.cursor()
        
        now = datetime.utcnow().isoformat()
        tags_str = json.dumps(tags) if tags else None
        
        cursor.execute("""
            INSERT OR REPLACE INTO files 
            (file_id, file_path, namespace, session_id, storage_path, 
             content_hash, size_bytes, tags, created_at, modified_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (file_id, file_path, namespace, session_id, storage_path,
              content_hash, size_bytes, tags_str, now, now))
        
        # Update session stats if session_id provided
        if session_id:
            cursor.execute("""
                INSERT INTO sessions (session_id, namespace, file_count, total_bytes)
                VALUES (?, ?, 1, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    file_count = file_count + 1,
                    total_bytes = total_bytes + ?,
                    last_accessed = CURRENT_TIMESTAMP
            """, (session_id, namespace, size_bytes, size_bytes))
        
        conn.commit()
        conn.close()
    
    def _get_metadata_sqlite(self, file_path: str, namespace: str, session_id: Optional[str]) -> Optional[Dict]:
        """Retrieve file metadata from SQLite"""
        conn = self._get_sqlite_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM files 
            WHERE file_path = ? AND namespace = ? AND 
                  (session_id = ? OR (session_id IS NULL AND ? IS NULL))
        """, (file_path, namespace, session_id, session_id))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def _list_files_sqlite(
        self,
        namespace: Optional[str] = None,
        session_id: Optional[str] = None,
        path_prefix: Optional[str] = None
    ) -> List[Dict]:
        """List files from SQLite with optional filtering"""
        conn = self._get_sqlite_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM files WHERE 1=1"
        params = []
        
        if namespace:
            query += " AND namespace = ?"
            params.append(namespace)
        
        if session_id:
            query += " AND session_id = ?"
            params.append(session_id)
        
        if path_prefix:
            query += " AND file_path LIKE ?"
            params.append(f"{path_prefix}%")
        
        query += " ORDER BY file_path"
        
        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    def _delete_metadata_sqlite(self, file_id: str):
        """Delete file metadata from SQLite"""
        conn = self._get_sqlite_connection()
        cursor = conn.cursor()
        
        # Get file info before deleting
        cursor.execute("SELECT size_bytes, session_id FROM files WHERE file_id = ?", (file_id,))
        row = cursor.fetchone()
        
        if row:
            size_bytes = row['size_bytes']
            session_id = row['session_id']
            
            # Delete file record
            cursor.execute("DELETE FROM files WHERE file_id = ?", (file_id,))
            
            # Update session stats
            if session_id:
                cursor.execute("""
                    UPDATE sessions 
                    SET file_count = file_count - 1,
                        total_bytes = total_bytes - ?
                    WHERE session_id = ?
                """, (size_bytes, session_id))
        
        conn.commit()
        conn.close()
    
    # ============================================================================
    # JSON BACKEND (Simple, for development)
    # ============================================================================
    
    def _load_json_metadata(self):
        """Load metadata from JSON file"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {}
    
    def _save_json_metadata(self):
        """Save metadata to JSON file"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def _store_metadata_json(
        self,
        file_id: str,
        file_path: str,
        namespace: str,
        session_id: Optional[str],
        storage_path: str,
        content_hash: str,
        size_bytes: int,
        tags: Optional[List[str]] = None
    ):
        """Store file metadata in JSON"""
        now = datetime.utcnow().isoformat()
        
        self.metadata[file_id] = {
            "file_id": file_id,
            "file_path": file_path,
            "namespace": namespace,
            "session_id": session_id,
            "storage_path": storage_path,
            "content_hash": content_hash,
            "size_bytes": size_bytes,
            "tags": tags or [],
            "created_at": now,
            "modified_at": now,
            "access_count": 0
        }
        
        self._save_json_metadata()
    
    def _get_metadata_json(self, file_path: str, namespace: str, session_id: Optional[str]) -> Optional[Dict]:
        """Retrieve file metadata from JSON"""
        file_id = self._generate_file_id(file_path, namespace, session_id)
        return self.metadata.get(file_id)
    
    def _list_files_json(
        self,
        namespace: Optional[str] = None,
        session_id: Optional[str] = None,
        path_prefix: Optional[str] = None
    ) -> List[Dict]:
        """List files from JSON with optional filtering"""
        results = []
        
        for file_id, meta in self.metadata.items():
            if namespace and meta.get("namespace") != namespace:
                continue
            if session_id and meta.get("session_id") != session_id:
                continue
            if path_prefix and not meta.get("file_path", "").startswith(path_prefix):
                continue
            
            results.append(meta)
        
        results.sort(key=lambda x: x.get("file_path", ""))
        return results
    
    def _delete_metadata_json(self, file_id: str):
        """Delete file metadata from JSON"""
        if file_id in self.metadata:
            del self.metadata[file_id]
            self._save_json_metadata()
    
    # ============================================================================
    # UNIFIED API (Works with both backends)
    # ============================================================================
    
    def _validate_path(self, path: str | Path) -> str:
        """Validate and normalize file path"""
        if isinstance(path, Path):
            path = str(path)

        if ".." in path or path.startswith("~"):
            raise ValueError(f"Invalid path (traversal attempt): {path}")
        
        normalized = os.path.normpath(path)
        normalized = normalized.replace("\\", "/")
        
        if not normalized.startswith("/"):
            normalized = f"/{normalized}"
        
        return normalized
    
    def _resolve_storage_path(
        self,
        file_path: str,
        namespace: str = "default",
        session_id: Optional[str] = None
    ) -> Path:
        """Resolve where file should be stored on disk"""
        file_path = file_path.lstrip("/")
        
        if session_id:
            storage_path = self.sessions_dir / session_id / file_path
        else:
            storage_path = self.persistent_dir / namespace / file_path
        
        return storage_path
    
    def get_storage_dir_path(
            self,
            asset_type: str,
            namespace: str = "default",
            session_id: Optional[str] = None
    ) -> Path:
        if session_id:
            storage_path = self.sessions_dir / session_id / asset_type
        else:
            storage_path = self.persistent_dir / namespace / asset_type
        
        dir_location = self._validate_path(storage_path)

        print(f"Directory Location {dir_location}")

        # Create parent directories
        storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        return storage_path
        
    
    def get_pwd(
        self,
        namespace: str = "default",
        session_id: Optional[str] = None,
        is_shared: bool = False,
        ensure_exists: bool = True
    ) -> str:
        """
        Return the working directory for the provided session/namespace.
        
        Args:
            namespace: Namespace directory for persistent storage (ignored if session_id provided).
            session_id: Session identifier; when provided, session workspace is returned.
            is_shared: Treat request as shared session storage.
            ensure_exists: Create the directory if it does not yet exist.
        
        Returns:
            Absolute path to the backing directory.
        """
        if is_shared:
            session_id = "shared"
        
        if session_id:
            base_dir = self.sessions_dir / session_id
        else:
            namespace = namespace or "default"
            base_dir = self.persistent_dir / namespace
        
        if ensure_exists:
            base_dir.mkdir(parents=True, exist_ok=True)
        
        return str(base_dir.resolve())
    
    def _generate_file_id(self, file_path: str, namespace: str, session_id: Optional[str]) -> str:
        """Generate unique file ID"""
        key = f"{namespace}:{session_id or 'persistent'}:{file_path}"
        return hashlib.sha256(key.encode()).hexdigest()[:16]
    
    def write_file(
        self,
        file_path: str,
        content: str,
        namespace: str = "default",
        session_id: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Write file to FileVault.
        
        Args:
            file_path: Absolute path like /data/report.csv
            content: File content
            namespace: Namespace for persistent files
            session_id: Session ID for temporary files
            tags: Optional tags for categorization
            
        Returns:
            file_id
        """
        # Validate path
        file_path = self._validate_path(file_path)
        
        # Resolve storage location
        storage_path = self._resolve_storage_path(file_path, namespace, session_id)
        
        # Create parent directories
        storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write content to disk
        storage_path.write_text(content, encoding='utf-8')
        
        # Generate file ID and hash
        file_id = self._generate_file_id(file_path, namespace, session_id)
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        size_bytes = len(content)
        
        # Store metadata in appropriate backend
        if self.use_sqlite:
            self._store_metadata_sqlite(
                file_id, file_path, namespace, session_id,
                str(storage_path), content_hash, size_bytes, tags
            )
        else:
            self._store_metadata_json(
                file_id, file_path, namespace, session_id,
                str(storage_path), content_hash, size_bytes, tags
            )
        
        # Check session size limits
        if session_id:
            self._check_session_limits(session_id)
        
        logger.debug(f"Wrote file: {file_path} ({size_bytes} bytes)")
        return file_id
    
    def read_file(
        self,
        file_path: str,
        namespace: str = "default",
        session_id: Optional[str] = None,
        update_access: bool = True,
        is_shared: bool = False
        
    ) -> str:
        """
        Read file from FileVault.
        
        Args:
            file_path: Absolute path to file
            namespace: Namespace for persistent files
            session_id: Session ID for session files
            update_access: Update access timestamp and count
            
        Returns:
            File content as string
        """
        file_path = self._validate_path(file_path)

        if is_shared: #Need a better startegy
            session_id = "shared"

        storage_path = self._resolve_storage_path(file_path, namespace, session_id)
        
        if not storage_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        content = storage_path.read_text(encoding='utf-8')
        
        # Update access stats if using SQLite
        if update_access and self.use_sqlite:
            conn = self._get_sqlite_connection()
            file_id = self._generate_file_id(file_path, namespace, session_id)
            conn.execute("""
                UPDATE files 
                SET accessed_at = CURRENT_TIMESTAMP,
                    access_count = access_count + 1
                WHERE file_id = ?
            """, (file_id,))
            conn.commit()
            conn.close()
        
        return content
    
    def list_files(
        self,
        namespace: Optional[str] = None,
        session_id: Optional[str] = None,
        path_prefix: Optional[str] = None,
        is_shared: Optional[bool] = False
    ) -> List[Dict]:
        """
        List files with optional filtering.
        
        Args:
            namespace: Filter by namespace
            session_id: Filter by session
            path_prefix: Filter by path prefix
            
        Returns:
            List of file metadata dicts
        """
        if is_shared:
            session_id = "shared"
        if self.use_sqlite:
            return self._list_files_sqlite(namespace, session_id, path_prefix)
        else:
            return self._list_files_json(namespace, session_id, path_prefix)
    
    def edit_file(
        self,
        file_path: str,
        old_string: str,
        new_string: str,
        namespace: str = "default",
        session_id: Optional[str] = None,
        replace_all: bool = False
    ) -> str:
        """Edit file using string replacement"""
        try:
            content = self.read_file(file_path, namespace, session_id, update_access=False)
        except FileNotFoundError:
            return f"Error: File not found: {file_path}"
        
        occurrences = content.count(old_string)
        
        if occurrences == 0:
            return f"Error: String not found in file: '{old_string}'"
        
        if occurrences > 1 and not replace_all:
            return f"Error: String '{old_string}' appears {occurrences} times. Use replace_all=True"
        
        new_content = content.replace(old_string, new_string)
        self.write_file(file_path, new_content, namespace, session_id)
        
        return f"Successfully edited {file_path} ({occurrences} replacement(s))"
    
    def delete_file(
        self,
        file_path: str,
        namespace: str = "default",
        session_id: Optional[str] = None
    ) -> str:
        """Delete file from FileVault"""
        file_path = self._validate_path(file_path)
        storage_path = self._resolve_storage_path(file_path, namespace, session_id)
        
        if storage_path.exists():
            storage_path.unlink()
        
        file_id = self._generate_file_id(file_path, namespace, session_id)
        
        if self.use_sqlite:
            self._delete_metadata_sqlite(file_id)
        else:
            self._delete_metadata_json(file_id)
        
        return f"Deleted {file_path}"
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Get detailed summary of a session.
        
        Returns:
            Dictionary with session statistics
        """
        files = self.list_files(session_id=session_id)
        
        if not files:
            return {
                "session_id": session_id,
                "file_count": 0,
                "total_bytes": 0,
                "directories": {}
            }
        
        # Group by directory
        dirs = {}
        total_size = 0
        
        for f in files:
            path = f['file_path']
            size = f['size_bytes']
            total_size += size
            
            # Get directory
            parts = path.split("/")
            dir_name = "/" + parts[1] if len(parts) > 1 else "/"
            
            if dir_name not in dirs:
                dirs[dir_name] = {"count": 0, "size": 0, "files": []}
            
            dirs[dir_name]["count"] += 1
            dirs[dir_name]["size"] += size
            dirs[dir_name]["files"].append(path)
        
        return {
            "session_id": session_id,
            "file_count": len(files),
            "total_bytes": total_size,
            "total_mb": round(total_size / (1024 * 1024), 2),
            "directories": dirs
        }
    
    def cleanup_session(self, session_id: str) -> str:
        """Clean up all files from a session"""
        session_path = self.sessions_dir / session_id
        
        if session_path.exists():
            import shutil
            shutil.rmtree(session_path)
        
        # Remove metadata
        if self.use_sqlite:
            conn = self._get_sqlite_connection()
            conn.execute("DELETE FROM files WHERE session_id = ?", (session_id,))
            conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
            conn.commit()
            conn.close()
        else:
            to_remove = [
                file_id for file_id, meta in self.metadata.items()
                if meta.get("session_id") == session_id
            ]
            for file_id in to_remove:
                del self.metadata[file_id]
            self._save_json_metadata()
        
        return f"Cleaned up session: {session_id}"
    
    def _check_session_limits(self, session_id: str):
        """Check if session exceeds size limits"""
        summary = self.get_session_summary(session_id)
        total_mb = summary["total_mb"]
        
        if total_mb > self.max_session_size_mb:
            logger.warning(
                f"Session {session_id} exceeds size limit: "
                f"{total_mb}MB > {self.max_session_size_mb}MB"
            )
    
    def cleanup_old_sessions(self, days: Optional[int] = None) -> List[str]:
        """
        Clean up sessions older than specified days.
        
        Args:
            days: Number of days (uses auto_cleanup_days if None)
            
        Returns:
            List of cleaned up session IDs
        """
        if not self.use_sqlite:
            return []  # Only works with SQLite
        
        days = days or self.auto_cleanup_days
        if days <= 0:
            return []
        
        conn = self._get_sqlite_connection()
        cursor = conn.cursor()
        
        # Find old sessions
        cursor.execute("""
            SELECT session_id FROM sessions
            WHERE julianday('now') - julianday(last_accessed) > ?
        """, (days,))
        
        old_sessions = [row['session_id'] for row in cursor.fetchall()]
        conn.close()
        
        # Clean up each session
        cleaned = []
        for session_id in old_sessions:
            try:
                self.cleanup_session(session_id)
                cleaned.append(session_id)
                logger.info(f"Auto-cleaned old session: {session_id}")
            except Exception as e:
                logger.error(f"Failed to cleanup session {session_id}: {e}")
        
        return cleaned
    
    def get_stats(self) -> Dict[str, Any]:
        """Get FileVault statistics"""
        if self.use_sqlite:
            conn = self._get_sqlite_connection()
            cursor = conn.cursor()
            
            # File stats
            cursor.execute("SELECT COUNT(*) as count, SUM(size_bytes) as total FROM files")
            row = cursor.fetchone()
            file_count = row['count']
            total_bytes = row['total'] or 0
            
            # Session stats
            cursor.execute("SELECT COUNT(*) as count FROM sessions WHERE status = 'active'")
            active_sessions = cursor.fetchone()['count']
            
            conn.close()
            
            return {
                "backend": "SQLite",
                "file_count": file_count,
                "total_bytes": total_bytes,
                "total_mb": round(total_bytes / (1024 * 1024), 2),
                "active_sessions": active_sessions,
                "workspace_dir": str(self.workspace_dir)
            }
        else:
            file_count = len(self.metadata)
            total_bytes = sum(m.get('size_bytes', 0) for m in self.metadata.values())
            
            return {
                "backend": "JSON",
                "file_count": file_count,
                "total_bytes": total_bytes,
                "total_mb": round(total_bytes / (1024 * 1024), 2),
                "workspace_dir": str(self.workspace_dir)
            }


# Test FileVault
if __name__ == "__main__":
    print("="*80)
    print("Testing FileVault - Intelligent Agent Filesystem")
    print("="*80)
    
    # Test with SQLite backend
    print("\n🔹 Testing with SQLite backend...")
    vault = FileVault(
        workspace_dir="./test_filevault_sqlite",
        use_sqlite=True,
        max_session_size_mb=100
    )
    
    session_id = "finance_analysis_123"
    
    # Write multiple files
    vault.write_file("/input/transactions.csv", "date,amount,category\n2025-10-01,50.00,food", 
                     session_id=session_id)
    vault.write_file("/input/accounts.json", '{"checking": 5000, "savings": 10000}',
                     session_id=session_id)
    vault.write_file("/analysis/spending.csv", "category,total\nfood,150.00\ntransport,80.00",
                     session_id=session_id)
    vault.write_file("/reports/summary.md", "# Financial Summary\n\nTotal expenses: $230",
                     session_id=session_id)
    
    print(f"✓ Created 4 files in session: {session_id}")
    
    # Get session summary
    summary = vault.get_session_summary(session_id)
    print(f"\n📊 Session Summary:")
    print(f"   Files: {summary['file_count']}")
    print(f"   Size: {summary['total_mb']}MB")
    print(f"   Directories:")
    for dir_name, stats in summary['directories'].items():
        print(f"      {dir_name}: {stats['count']} files, {stats['size']/1024:.1f}KB")
    
    # List files
    files = vault.list_files(session_id=session_id)
    print(f"\n📁 Files in session:")
    for f in files:
        print(f"   {f['file_path']} ({f['size_bytes']} bytes)")
    
    # Get stats
    stats = vault.get_stats()
    print(f"\n📈 FileVault Stats:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n" + "="*80)
    print("✅ FileVault working perfectly!")
    print("="*80)
