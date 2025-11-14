import gradio as gr
import sqlite3
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

DB_PATH = ".vault/.metadata/filevault.db"
RECENT_SESSION_LIMIT = 100
ALL_TICKERS_VALUE = "__all__"
UNTITLED_TICKER_VALUE = "__untitled__"

FILE_TYPE_EXTENSIONS = {
    ".py": "Code",
    ".ipynb": "Notebooks",
    ".md": "Reports",
    ".txt": "Text",
    ".log": "Logs",
    ".csv": "Data",
    ".tsv": "Data",
    ".json": "Data",
    ".yaml": "Data",
    ".yml": "Data",
    ".html": "Reports",
    ".htm": "Reports",
    ".pdf": "Reports",
    ".png": "Visuals",
    ".jpg": "Visuals",
    ".jpeg": "Visuals",
    ".gif": "Visuals",
    ".svg": "Visuals",
    ".xlsx": "Data",
    ".xls": "Data",
}

FILE_TYPE_KEYWORDS = {
    "reports": "Reports",
    "report": "Reports",
    "charts": "Visuals",
    "chart": "Visuals",
    "images": "Visuals",
    "analysis": "Reports",
    "analytics": "Reports",
    "summaries": "Summaries",
    "summary": "Summaries",
    "notes": "Notes",
    "logs": "Logs",
    "code": "Code",
    "scripts": "Code",
    "notebooks": "Notebooks",
    "notebook": "Notebooks",
    "data": "Data",
    "datasets": "Data",
    "dataset": "Data",
    "tool_results": "Tool Output",
}

MIME_PREFIX_CATEGORIES = {
    "image": "Visuals",
    "text": "Text",
    "audio": "Audio",
    "video": "Media",
    "application": "Data",
}


def parse_tags(tags_field) -> List[str]:
    """Return lower-cased tags from JSON/text storage."""
    if not tags_field:
        return []
    if isinstance(tags_field, list):
        return [str(tag).lower() for tag in tags_field]
    try:
        parsed = json.loads(tags_field)
        if isinstance(parsed, list):
            return [str(tag).lower() for tag in parsed]
    except json.JSONDecodeError:
        pass
    return [str(tags_field).lower()]


def infer_file_type(file_row: Dict) -> str:
    """Classify a file into a friendly bucket using tags, path segments, and extensions."""
    file_path = file_row.get('file_path') or file_row.get('storage_path') or ""
    mime_type = (file_row.get('mime_type') or "").lower()
    tags = parse_tags(file_row.get('tags'))
    path_obj = Path(file_path)
    parts = [part.lower() for part in path_obj.parts if part not in (".", "")]
    
    for tag in tags:
        if tag in FILE_TYPE_KEYWORDS:
            return FILE_TYPE_KEYWORDS[tag]
    
    for part in parts:
        if part in FILE_TYPE_KEYWORDS:
            return FILE_TYPE_KEYWORDS[part]
    
    ext = path_obj.suffix.lower()
    if ext in FILE_TYPE_EXTENSIONS:
        return FILE_TYPE_EXTENSIONS[ext]
    
    if mime_type:
        prefix = mime_type.split("/", 1)[0]
        if prefix in MIME_PREFIX_CATEGORIES:
            return MIME_PREFIX_CATEGORIES[prefix]
    
    return "Other"


def human_size(bytes_value: Optional[int]) -> str:
    """Convert raw byte counts into a readable string."""
    if not bytes_value:
        return "0 KB"
    size = float(bytes_value)
    if size < 1024:
        return f"{size:.0f} B"
    size /= 1024
    if size < 1024:
        return f"{size:.1f} KB"
    size /= 1024
    return f"{size:.2f} MB"


def format_timestamp(timestamp: Optional[str]) -> str:
    """Render timestamps in a consistent short format."""
    if not timestamp:
        return ""
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", ""))
        return dt.strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return timestamp[:19]


def group_files_by_type(file_rows: List[Dict]) -> Dict[str, List[Dict]]:
    """Return files bucketed by type with newest files first."""
    grouped: Dict[str, List[Dict]] = defaultdict(list)
    for row in file_rows:
        row['file_type'] = infer_file_type(row)
        grouped[row['file_type']].append(row)
    
    for file_list in grouped.values():
        file_list.sort(key=lambda f: f.get('created_at', ''), reverse=True)
    
    return dict(sorted(grouped.items(), key=lambda item: item[0].lower()))


def decode_ticker_choice(raw_value: Optional[str]) -> Optional[str]:
    """Map dropdown sentinel values back to database filters."""
    if raw_value in (None, "", ALL_TICKERS_VALUE):
        return None
    if raw_value == UNTITLED_TICKER_VALUE:
        return UNTITLED_TICKER_VALUE
    return raw_value


def display_ticker_label(raw_value: Optional[str]) -> str:
    """Human-readable ticker label for UI highlights."""
    if not raw_value or raw_value == ALL_TICKERS_VALUE:
        return "All"
    if raw_value in ("", UNTITLED_TICKER_VALUE):
        return "Unassigned"
    return raw_value

def get_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_all_sessions() -> List[dict]:
    """Fetch all sessions from database"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                session_id,
                namespace,
                created_at,
                last_accessed,
                file_count,
                total_bytes,
                ticker,
                summary,
                status
            FROM sessions
            ORDER BY last_accessed DESC
            LIMIT ?
        """, (RECENT_SESSION_LIMIT,))
        
        sessions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return sessions
    except Exception as e:
        gr.Warning(f"Error fetching sessions: {str(e)}")
        return []

def get_session_details(session_id: str) -> Tuple[str, str, str, str, str, str, str]:
    """Fetch detailed session information"""
    if not session_id:
        return "", "", "", "", "", "", ""
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get session
        cursor.execute("""
            SELECT 
                session_id,
                namespace,
                created_at,
                last_accessed,
                file_count,
                total_bytes,
                ticker,
                summary,
                status
            FROM sessions
            WHERE session_id = ?
        """, (session_id,))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return "", "", "", "", "", "", ""
        
        session = dict(row)
        
        cursor.execute("""
            SELECT 
                file_id,
                file_path,
                storage_path,
                size_bytes,
                mime_type,
                tags,
                created_at
            FROM files
            WHERE session_id = ?
            ORDER BY created_at DESC
        """, (session_id,))
        
        file_rows = [dict(file_row) for file_row in cursor.fetchall()]
        conn.close()
        
        grouped = group_files_by_type(file_rows)
        
        file_display = ""
        for type_name, type_files in grouped.items():
            file_display += f"\n### 📁 {type_name} ({len(type_files)})\n"
            for f in type_files:
                label = Path(f.get('file_path') or f.get('storage_path', '')).name or f.get('file_id')
                file_display += (
                    f"- **{label}** · {human_size(f.get('size_bytes'))} · "
                    f"{format_timestamp(f.get('created_at'))}\n"
                )
        
        summary = session.get('summary') or "No session summary recorded."
        stats = (
            f"{session.get('file_count', 0)} files · {human_size(session.get('total_bytes'))} · "
            f"Last accessed {format_timestamp(session.get('last_accessed'))}"
        )
        
        return (
            session.get('ticker', '') or "Unassigned",
            session.get('status', ''),
            session.get('namespace', ''),
            format_timestamp(session.get('created_at')),
            stats,
            summary,
            file_display or "No files recorded for this session."
        )
    except Exception as e:
        gr.Warning(f"Error: {str(e)}")
        return "", "", "", "", "", "", ""

def view_file(file_id: str) -> Tuple[str, str, str]:
    """View file content"""
    if not file_id:
        return "No file selected", "", ""
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                file_id,
                file_path,
                storage_path,
                size_bytes,
                mime_type,
                tags,
                summary
            FROM files
            WHERE file_id = ?
        """, (file_id,))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return "File not found", "", ""
        
        file = dict(row)
        conn.close()
        
        file_type = infer_file_type(file)
        file_path = Path(file['storage_path'])
        
        if not file_path.exists():
            return f"❌ File not found at: {file['storage_path']}", file_id, file_type
        
        # Determine file type and read
        if file_path.suffix in ['.txt', '.csv', '.json', '.md', '.log']:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            # Limit to first 10000 chars for display
            if len(content) > 10000:
                content = content[:10000] + "\n\n... (truncated)"
            html_content = f"<pre style='background: #1e293b; padding: 20px; border-radius: 8px; color: #e2e8f0; overflow-x: auto; font-family: monospace; font-size: 12px;'>{content}</pre>"
            return html_content, file_id, file_type
        
        elif file_path.suffix in ['.png', '.jpg', '.jpeg', '.gif']:
            return str(file_path), file_id, file_type
        
        elif file_path.suffix == '.html':
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content, file_id, file_type
        
        else:
            return f"⚠️ Unsupported file type: {file_path.suffix}", file_id, file_type
    
    except Exception as e:
        return f"❌ Error reading file: {str(e)}", file_id, ""

def get_namespace_stats() -> str:
    """Get statistics about all namespaces"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                namespace,
                COUNT(*) as session_count,
                SUM(file_count) as total_files,
                SUM(total_bytes) as total_bytes
            FROM sessions
            GROUP BY namespace
            ORDER BY total_bytes DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        stats = "## 📊 Namespace Statistics\n\n"
        stats += "| Namespace | Sessions | Files | Size (MB) |\n"
        stats += "|-----------|----------|-------|----------|\n"
        
        for row in rows:
            row_dict = dict(row)
            total_mb = (row_dict['total_bytes'] or 0) / (1024 * 1024)
            stats += f"| {row_dict['namespace']} | {row_dict['session_count']} | {row_dict['total_files'] or 0} | {total_mb:.2f} |\n"
        
        return stats
    except Exception as e:
        return f"Error fetching statistics: {str(e)}"


def fetch_files_for_sessions(session_ids: List[str]) -> Dict[str, List[Dict]]:
    """Retrieve all files for the provided session ids."""
    if not session_ids:
        return {}
    
    conn = get_connection()
    cursor = conn.cursor()
    placeholders = ",".join(["?"] * len(session_ids))
    
    cursor.execute(f"""
        SELECT 
            session_id,
            file_id,
            file_path,
            storage_path,
            size_bytes,
            mime_type,
            tags,
            summary,
            created_at
        FROM files
        WHERE session_id IN ({placeholders})
        ORDER BY created_at DESC
    """, session_ids)
    
    files_map: Dict[str, List[Dict]] = defaultdict(list)
    for row in cursor.fetchall():
        row_dict = dict(row)
        files_map[row_dict['session_id']].append(row_dict)
    
    conn.close()
    return files_map


def get_session_file_groups(session_id: Optional[str]) -> Dict[str, List[Dict]]:
    """Return grouped files for a single session."""
    if not session_id:
        return {}
    files_map = fetch_files_for_sessions([session_id])
    return group_files_by_type(files_map.get(session_id, []))


def build_type_summary_md(grouped: Dict[str, List[Dict]]) -> str:
    """Markdown summary for grouped files."""
    if not grouped:
        return "No files available for this session."
    
    lines = ["### File Groups"]
    for type_name, files in grouped.items():
        total_bytes = sum(f.get('size_bytes') or 0 for f in files)
        lines.append(
            f"- **{type_name}** · {len(files)} file{'s' if len(files) != 1 else ''} · {human_size(total_bytes)}"
        )
    return "\n".join(lines)


def file_type_choices(grouped: Dict[str, List[Dict]]) -> List[Tuple[str, str]]:
    """Build dropdown choices for file type selector."""
    return [
        (f"{type_name} ({len(files)})", type_name)
        for type_name, files in grouped.items()
    ]


def file_choices_for_type(grouped: Dict[str, List[Dict]], file_type: Optional[str]) -> List[Tuple[str, str]]:
    """Build dropdown choices for individual files within a type."""
    if not file_type or file_type not in grouped:
        return []
    choices: List[Tuple[str, str]] = []
    for file_row in grouped[file_type]:
        label = Path(file_row.get('file_path') or file_row.get('storage_path', '')).name or file_row['file_id']
        choices.append((f"{label} · {human_size(file_row.get('size_bytes'))}", file_row['file_id']))
    return choices


def fetch_sessions_for_choice(choice: Optional[str]) -> List[Dict]:
    """Fetch sessions filtered by ticker dropdown selection."""
    decoded = decode_ticker_choice(choice)
    conn = get_connection()
    cursor = conn.cursor()
    
    base_query = """
        SELECT 
            session_id,
            ticker,
            namespace,
            created_at,
            last_accessed,
            file_count,
            total_bytes,
            status
        FROM sessions
    """
    where_clause = ""
    params: List = []
    
    if decoded == UNTITLED_TICKER_VALUE:
        where_clause = "WHERE (ticker IS NULL OR ticker = '')"
    elif decoded:
        where_clause = "WHERE ticker = ?"
        params.append(decoded)
    
    query = f"""
        {base_query}
        {where_clause}
        ORDER BY created_at DESC
        LIMIT ?
    """
    params.append(RECENT_SESSION_LIMIT)
    
    cursor.execute(query, params)
    sessions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return sessions


def get_ticker_tree_data() -> Dict[str, List[Dict]]:
    """Return recent sessions grouped by ticker with file summaries for the tree view."""
    sessions = get_all_sessions()
    if not sessions:
        return {}
    
    session_ids = [s['session_id'] for s in sessions]
    files_map = fetch_files_for_sessions(session_ids)
    
    grouped_by_ticker: Dict[str, List[Dict]] = defaultdict(list)
    for session in sessions:
        file_rows = files_map.get(session['session_id'], [])
        session['files_grouped'] = group_files_by_type(file_rows)
        ticker_label = session.get('ticker') or "Unassigned"
        grouped_by_ticker[ticker_label].append(session)
    
    for ticker_sessions in grouped_by_ticker.values():
        ticker_sessions.sort(key=lambda s: s.get('created_at', ''), reverse=True)
    
    return dict(sorted(grouped_by_ticker.items(), key=lambda item: item[0].lower()))


def build_ticker_tree_html(selected_ticker_value: Optional[str], selected_session: Optional[str]) -> str:
    """Render a collapsible HTML tree showing ticker→session→files."""
    tree_data = get_ticker_tree_data()
    if not tree_data:
        return "<div class='empty-tree'>No sessions recorded yet.</div>"
    
    decoded = decode_ticker_choice(selected_ticker_value)
    if decoded == UNTITLED_TICKER_VALUE:
        highlight_ticker = "Unassigned"
    else:
        highlight_ticker = decoded
    
    html_parts = ["<div class='ticker-tree'>"]
    
    for ticker, sessions in tree_data.items():
        ticker_open = " open" if highlight_ticker and ticker == highlight_ticker else ""
        html_parts.append(f"<details class='tree-node ticker'{ticker_open}>")
        html_parts.append(
            f"<summary><span class='node-title'>{ticker}</span>"
            f"<span class='meta'>{len(sessions)} session{'s' if len(sessions) != 1 else ''}</span></summary>"
        )
        
        for session in sessions:
            session_open = " open" if selected_session and session['session_id'] == selected_session else ""
            html_parts.append(f"<details class='tree-node session'{session_open}>")
            html_parts.append(
                "<summary>"
                f"<span class='node-title'>{session['session_id']}</span>"
                f"<span class='meta'>{human_size(session.get('total_bytes'))} · "
                f"{session.get('status') or 'unknown'} · {format_timestamp(session.get('created_at'))}</span>"
                "</summary>"
            )
            
            grouped = session.get('files_grouped', {})
            if not grouped:
                html_parts.append("<p class='muted'>No files captured yet.</p>")
            else:
                for type_name, files in grouped.items():
                    html_parts.append(
                        f"<div class='file-type'><strong>{type_name}</strong>"
                        f"<span class='meta'>{len(files)} file{'s' if len(files) != 1 else ''}</span></div>"
                    )
                    html_parts.append("<ul>")
                    for file_row in files[:6]:
                        label = Path(file_row.get('file_path') or file_row.get('storage_path', '')).name or file_row['file_id']
                        html_parts.append(
                            f"<li>{label}<span class='meta'>{human_size(file_row.get('size_bytes'))}</span></li>"
                        )
                    if len(files) > 6:
                        html_parts.append(f"<li class='muted'>… {len(files) - 6} more</li>")
                    html_parts.append("</ul>")
            
            html_parts.append("</details>")
        
        html_parts.append("</details>")
    
    html_parts.append("</div>")
    return "".join(html_parts)


def get_ticker_dropdown_choices() -> List[Tuple[str, str]]:
    """Choices for ticker selector, including All & Unassigned."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            ticker,
            COUNT(*) as session_count
        FROM sessions
        GROUP BY ticker
        ORDER BY ticker
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    choices: List[Tuple[str, str]] = [("✨ All tickers", ALL_TICKERS_VALUE)]
    unassigned_total = 0
    
    for row in rows:
        ticker = row['ticker']
        count = row['session_count']
        if ticker in (None, ""):
            unassigned_total += count
            continue
        choices.append((f"{ticker} ({count})", ticker))
    
    if unassigned_total:
        choices.append((f"Unassigned ({unassigned_total})", UNTITLED_TICKER_VALUE))
    
    return choices


def format_session_choice_label(session: Dict) -> str:
    """Readable label for session dropdown entries."""
    created = format_timestamp(session.get('created_at'))
    namespace = session.get('namespace') or "default"
    return (
        f"{session['session_id']} · {session.get('ticker') or 'Unassigned'} · "
        f"{session.get('status') or 'unknown'} · {namespace} · {created}"
    )


def resolve_explorer_state(
    ticker_value: Optional[str],
    session_value: Optional[str] = None,
    file_type_value: Optional[str] = None
):
    """Compute dropdown updates, tree, and summaries for the explorer tab."""
    sessions = fetch_sessions_for_choice(ticker_value)
    session_choices = [
        (format_session_choice_label(session), session['session_id'])
        for session in sessions
    ]
    session_ids = {value for _, value in session_choices}
    active_session = session_value if session_value in session_ids else (
        session_choices[0][1] if session_choices else None
    )
    
    grouped = get_session_file_groups(active_session)
    type_choices_list = file_type_choices(grouped)
    type_values = {value for _, value in type_choices_list}
    active_type = file_type_value if file_type_value in type_values else (
        type_choices_list[0][1] if type_choices_list else None
    )
    
    file_choices_list = file_choices_for_type(grouped, active_type)
    active_file = file_choices_list[0][1] if file_choices_list else None
    
    return {
        "session": gr.update(choices=session_choices, value=active_session),
        "file_type": gr.update(choices=type_choices_list, value=active_type),
        "file": gr.update(choices=file_choices_list, value=active_file),
        "tree_html": build_ticker_tree_html(ticker_value, active_session),
        "summary": build_type_summary_md(grouped)
    }


def init_or_refresh_explorer(current_ticker: Optional[str] = None):
    """Return dropdown updates and hierarchy for explorer initialization/refresh."""
    choices = get_ticker_dropdown_choices()
    available_values = [value for _, value in choices]
    active_ticker = current_ticker if current_ticker in available_values else (
        choices[0][1] if choices else None
    )
    state = resolve_explorer_state(active_ticker)
    return (
        gr.update(choices=choices, value=active_ticker),
        state["session"],
        state["file_type"],
        state["file"],
        state["tree_html"],
        state["summary"]
    )


CUSTOM_CSS = """
.gradio-container {
    font-family: 'Inter', 'Segoe UI', sans-serif;
}
:root {
    --panel-bg: #0f172a;
    --border-color: #1f2942;
    --muted: #94a3b8;
}
.card {
    background: var(--panel-bg);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 8px 20px rgba(2, 6, 23, 0.35);
}
.ticker-tree {
    background: rgba(15, 23, 42, 0.9);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 18px;
    max-height: 520px;
    overflow-y: auto;
}
.ticker-tree details {
    margin-bottom: 10px;
}
.ticker-tree summary {
    cursor: pointer;
    font-weight: 600;
    color: #e2e8f0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.ticker-tree .meta {
    color: var(--muted);
    font-size: 0.85rem;
}
.ticker-tree ul {
    list-style: none;
    padding-left: 1rem;
    margin: 6px 0 10px;
}
.ticker-tree li {
    color: #cbd5f5;
    font-size: 0.9rem;
    display: flex;
    justify-content: space-between;
}
.ticker-tree .file-type {
    margin: 10px 0 4px;
    color: #f8fafc;
    display: flex;
    justify-content: space-between;
    font-weight: 600;
}
.ticker-tree .muted {
    color: var(--muted);
    font-size: 0.85rem;
}
.empty-tree {
    border: 1px dashed var(--border-color);
    border-radius: 12px;
    padding: 24px;
    text-align: center;
    color: var(--muted);
}
"""

# Create the Gradio app with custom theme
modern_theme = gr.themes.Soft(
    primary_hue="indigo",
    secondary_hue="cyan",
    neutral_hue="slate"
).set(
    body_background_fill="#050915",
    body_text_color="#e2e8f0",
    block_background_fill="#0b1220",
    block_border_color="#1d2640",
    block_label_text_color="#c7d2fe",
    input_background_fill="#0f1a2f",
    input_border_color="#2a3553",
    button_primary_background_fill="#6366f1",
    button_primary_text_color="#f8fafc",
    button_secondary_background_fill="#1f2937",
    button_secondary_text_color="#e2e8f0",
)

with gr.Blocks(
    title="Session Vault",
    theme=modern_theme,
    css=CUSTOM_CSS
) as app:
    
    # Header
    with gr.Row():
        with gr.Column(scale=10):
            gr.Markdown("""
# 📊 Session Vault
### Multi-Namespace File Storage Viewer
**Database:** `.vault/.metadata/filevault.db`
            """)
        with gr.Column(scale=2, min_width=150):
            refresh_btn = gr.Button("🔄 Refresh All", size="lg")
    
    # Tabs for different sections
    with gr.Tabs():
        
        # ======================
        # TAB 1: Browse Sessions
        # ======================
        with gr.TabItem("📋 Browse Sessions"):
            gr.Markdown("### View all recorded sessions")
            
            with gr.Row():
                sessions_refresh_btn = gr.Button("🔄 Load Sessions", scale=1)
            
            sessions_output = gr.Dataframe(
                headers=["Session ID", "Namespace", "Ticker", "Status", "Files", "Size (MB)", "Last Accessed"],
                interactive=False,
                scale=1
            )
            
            def load_sessions_table():
                sessions = get_all_sessions()
                data = []
                for s in sessions:
                    total_mb = (s['total_bytes'] or 0) / (1024 * 1024)
                    data.append([
                        s['session_id'],
                        s['namespace'],
                        s['ticker'] or 'N/A',
                        s['status'],
                        s['file_count'],
                        f"{total_mb:.2f}",
                        s['last_accessed'][:19] if s['last_accessed'] else ''
                    ])
                return data
            
            sessions_refresh_btn.click(
                load_sessions_table,
                outputs=[sessions_output]
            )
        
        # ======================
        # TAB 2: Session Details
        # ======================
        with gr.TabItem("📁 Session Details"):
            gr.Markdown("### View detailed session information and files")
            
            with gr.Row():
                session_dropdown = gr.Dropdown(
                    label="Select Session",
                    info="Choose a session to view details",
                    choices=[],
                    scale=10
                )
                load_detail_btn = gr.Button("📖 Load", scale=2)
            
            with gr.Row():
                with gr.Column(scale=1):
                    ticker_display = gr.Textbox(label="Ticker", interactive=False)
                    status_display = gr.Textbox(label="Status", interactive=False)
                
                with gr.Column(scale=1):
                    namespace_display = gr.Textbox(label="Namespace", interactive=False)
                    created_display = gr.Textbox(label="Created", interactive=False)
            
            stats_display = gr.Textbox(
                label="File Stats",
                interactive=False,
                lines=1
            )
            
            summary_display = gr.Textbox(
                label="Summary",
                interactive=False,
                lines=3
            )
            
            files_display = gr.Markdown("### Files\nLoad a session to see files")
            
            def update_session_dropdown():
                sessions = get_all_sessions()
                choices = [
                    (
                        f"{s['session_id']} · {s.get('ticker') or 'Unassigned'} · "
                        f"{format_timestamp(s.get('created_at'))}",
                        s['session_id']
                    )
                    for s in sessions
                ]
                default_value = choices[0][1] if choices else None
                return gr.update(choices=choices, value=default_value)
            
            def load_session_details(session_id):
                ticker, status, namespace, created, summary, stats, files_md = get_session_details(session_id)
                return ticker, status, namespace, created, stats, summary, files_md
            
            load_detail_btn.click(
                load_session_details,
                inputs=[session_dropdown],
                outputs=[
                    ticker_display,
                    status_display,
                    namespace_display,
                    created_display,
                    stats_display,
                    summary_display,
                    files_display
                ]
            )
            
            refresh_btn.click(
                update_session_dropdown,
                outputs=[session_dropdown]
            )
        
        # ======================
        # TAB 3: Ticker Explorer
        # ======================
        with gr.TabItem("📂 Ticker Explorer"):
            gr.Markdown("### Navigate tickers → sessions → grouped files and preview content")
            
            with gr.Row():
                with gr.Column(scale=1, min_width=320):
                    ticker_selector = gr.Dropdown(
                        label="Ticker",
                        info="Filter sessions by ticker",
                        choices=[],
                        interactive=True
                    )
                    explorer_session_dropdown = gr.Dropdown(
                        label="Session",
                        info="Pick a session for the selected ticker",
                        choices=[],
                        interactive=True
                    )
                    file_type_dropdown = gr.Dropdown(
                        label="File Group",
                        info="Files are grouped by inferred type",
                        choices=[],
                        interactive=True
                    )
                    explorer_file_dropdown = gr.Dropdown(
                        label="File",
                        info="Select a file to preview",
                        choices=[],
                        interactive=True
                    )
                    explorer_view_btn = gr.Button("👁️ View File", variant="primary")
                
                with gr.Column(scale=2):
                    hierarchy_display = gr.HTML(
                        label="Ticker → Session → Files",
                        value="<div class='empty-tree'>Loading hierarchy…</div>"
                    )
                    group_summary_display = gr.Markdown(
                        "Select a ticker to view file groups.",
                        elem_classes=["card"]
                    )
            
            explorer_file_output = gr.HTML(label="File Preview")
            
            with gr.Row():
                explorer_file_id = gr.Textbox(label="File ID", interactive=False, scale=1)
                explorer_file_type = gr.Textbox(label="File Type", interactive=False, scale=1)
            
            def explorer_outputs(state):
                return (
                    state["session"],
                    state["file_type"],
                    state["file"],
                    state["tree_html"],
                    state["summary"]
                )
            
            def on_ticker_change(selected_ticker):
                return explorer_outputs(resolve_explorer_state(selected_ticker))
            
            def on_session_change(selected_ticker, selected_session):
                return explorer_outputs(resolve_explorer_state(selected_ticker, selected_session))
            
            def on_file_type_change(selected_ticker, selected_session, selected_type):
                return explorer_outputs(resolve_explorer_state(selected_ticker, selected_session, selected_type))
            
            ticker_selector.change(
                on_ticker_change,
                inputs=[ticker_selector],
                outputs=[
                    explorer_session_dropdown,
                    file_type_dropdown,
                    explorer_file_dropdown,
                    hierarchy_display,
                    group_summary_display
                ]
            )
            
            explorer_session_dropdown.change(
                on_session_change,
                inputs=[ticker_selector, explorer_session_dropdown],
                outputs=[
                    explorer_session_dropdown,
                    file_type_dropdown,
                    explorer_file_dropdown,
                    hierarchy_display,
                    group_summary_display
                ]
            )
            
            file_type_dropdown.change(
                on_file_type_change,
                inputs=[ticker_selector, explorer_session_dropdown, file_type_dropdown],
                outputs=[
                    explorer_session_dropdown,
                    file_type_dropdown,
                    explorer_file_dropdown,
                    hierarchy_display,
                    group_summary_display
                ]
            )
            
            explorer_view_btn.click(
                view_file,
                inputs=[explorer_file_dropdown],
                outputs=[explorer_file_output, explorer_file_id, explorer_file_type]
            )
        
        # ======================
        # TAB 4: Statistics
        # ======================
        with gr.TabItem("📊 Statistics"):
            gr.Markdown("### Storage and namespace statistics")
            
            with gr.Row():
                stats_refresh_btn = gr.Button("🔄 Refresh Stats", scale=1)
            
            stats_markdown = gr.Markdown("")
            
            def load_stats():
                return get_namespace_stats()
            
            stats_refresh_btn.click(
                load_stats,
                outputs=[stats_markdown]
            )
        
        # ======================
        # TAB 5: API Documentation
        # ======================
        with gr.TabItem("📚 API Docs"):
            gr.Markdown("""
## Push Data from Your Agent

The database schema expects:

### Sessions Table
```python
{
    "session_id": "sess_12345",
    "namespace": "my_namespace",
    "ticker": "AAPL",
    "summary": "Analysis summary...",
    "status": "active"
}
``````

### Files Table
```
{
    "file_id": "file_12345",
    "session_id": "sess_12345",
    "file_type": "reports",  # or "charts", "data", etc.
    "storage_path": "/path/to/file.html",
    "file_size": 15360
}
``````

### File Versions Table (optional)
```python
{
    "version_id": "v_12345",
    "file_id": "file_12345",
    "version_number": 1,
    "content_hash": "sha256_hash",
    "size_bytes": 15360,
    "created_by": "agent_name"
}
``````



Then click **🔄 Refresh All** to see your data!
            """)
    
    # Auto-load key data on startup
    app.load(
        load_sessions_table,
        outputs=[sessions_output]
    )
    app.load(
        update_session_dropdown,
        outputs=[session_dropdown]
    )
    app.load(
        init_or_refresh_explorer,
        outputs=[
            ticker_selector,
            explorer_session_dropdown,
            file_type_dropdown,
            explorer_file_dropdown,
            hierarchy_display,
            group_summary_display
        ]
    )
    
    refresh_btn.click(
        load_sessions_table,
        outputs=[sessions_output]
    )
    refresh_btn.click(
        init_or_refresh_explorer,
        inputs=[ticker_selector],
        outputs=[
            ticker_selector,
            explorer_session_dropdown,
            file_type_dropdown,
            explorer_file_dropdown,
            hierarchy_display,
            group_summary_display
        ]
    )

if __name__ == "__main__":
    app.launch(share=True, server_name="0.0.0.0", server_port=7860)
