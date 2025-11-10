"""
FileVault Middleware - Production-Ready Agent Filesystem Middleware (FIXED)
Integrates FileVault with DeepAgents for intelligent file management.

Features:
- Domain-agnostic (finance, coding, research, healthcare, etc.)
- Session summary tools
- Formatted outputs with helpful error messages
- Optional SQLite backend (just set use_sqlite=True)
- Multi-file session support
- Automatic session tracking and cleanup

FIXED: Pydantic JsonSchema compatibility using InjectedToolArg
"""

from typing import Any, Callable, Optional, List, Dict, Annotated, Literal, TypedDict
from operator import add
from collections.abc import Awaitable
from langchain_core.tools import tool, InjectedToolArg  # ADDED InjectedToolArg
from langgraph.types import Command
from langchain_core.messages import ToolMessage
import logging
import re
import fnmatch
import time
from pathlib import Path

# Import FileVault
from kratos.core.middleware.vault import FileVault

# DeepAgents/LangGraph imports with proper typing
from langchain.agents.middleware.types import (
    AgentMiddleware,
    AgentState,
    ModelRequest,
    ModelResponse,
)
from langchain.tools import ToolRuntime
from langchain.tools.tool_node import ToolCallRequest

DEEPAGENTS_AVAILABLE = True

logger = logging.getLogger(__name__)


def merge_if_not_exists(x: Optional[str], y: Optional[str]) -> Optional[str]:
    """Reducer for un: keeps existing if set, otherwise takes new."""
    if x is not None:
        return x
    return y

class ContextPath(TypedDict):
    relative_path: str
    absolute_path: str
    description: str

class FileVaultState(AgentState):
    """
    Enhanced state schema for FileVault middleware.
    """
    session_id: Annotated[Optional[str], merge_if_not_exists]
    namespace: Annotated[Optional[str], merge_if_not_exists]
    context_data_loc:Annotated[Optional[list[ContextPath]], merge_if_not_exists]
    files_created: Annotated[Optional[int], add]  # Can accumulate
    files_read: Annotated[Optional[int], add]     # Can accumulate  
    total_bytes_written: Annotated[Optional[int], add]  # Can accumulate


class ContextVaultMiddleware(AgentMiddleware):
    """
    Production-ready filesystem middleware powered by FileVault.
    
    Domain-agnostic - works for any agent purpose:
    - Finance: Store transactions, reports, analysis
    - Coding: Store code files, tests, documentation
    - Research: Store papers, notes, summaries
    - Healthcare: Store patient data, reports (with proper security)
    - Any other domain!
    """
    
    state_schema = FileVaultState
    
    def __init__(
        self,
        workspace_dir: str = "./agent_workspace",
        default_namespace: str = "default",
        session_id: str = None,
        use_sqlite: bool = True,
        max_file_size_warning: int = 100_000,
        enable_logging: bool = True,
        format_outputs: bool = True,
        agent_purpose: str = "general_assistant"
    ):
        """
        Initialize FileVault middleware.
        
        Args:
            workspace_dir: Root directory for file storage
            default_namespace: Default namespace for persistent files
            use_sqlite: Use SQLite backend (recommended for production)
            max_file_size_warning: Warn when files exceed this size
            enable_logging: Enable debug logging
            format_outputs: Use formatted output for better readability
            agent_purpose: Purpose of agent (for customized system prompt)
        """
        self.workspace_dir = workspace_dir
        self.default_namespace = default_namespace
        #self.session_id = session_id
        self.max_file_size_warning = max_file_size_warning
        self.enable_logging = enable_logging
        self.format_outputs = format_outputs
        self.agent_purpose = agent_purpose
        
        # Initialize FileVault
        self.vault = FileVault(
            workspace_dir=workspace_dir,
            use_sqlite=use_sqlite,
            auto_cleanup_days=7,
            max_session_size_mb=500
        )
        
        # Create tools
        self.tools = self._create_tools()
        
        
        # System prompt (domain-agnostic)
        self.system_prompt = self._generate_system_prompt()
        
        if enable_logging:
            backend = "SQLite" if use_sqlite else "JSON"
            logger.info(f"FileVault middleware initialized ({backend} backend)")
    
    def _generate_system_prompt(self) -> str:
        """Generate domain-agnostic system prompt"""
        
        # Customize examples based on agent purpose
        examples = self._get_purpose_examples()
        
        return f"""## FileVault - Your Intelligent File Storage

You have access to **FileVault**, a powerful filesystem for managing files across sessions.

### Available Tools

**📁 ls(path=None)** - List files
  - Lists all files in your workspace
  - Optional `path` parameter to filter by directory (e.g., "/data/")
  - Shows file sizes and storage type

**📄 read_file(file_path)** - Read file content
  - Reads complete file content
  - Returns formatted output with metadata

**✍️ write_file(file_path, content)** - Create new file
  - Writes a new file to disk
  - Automatically tracks size and provides warnings for large files
  - Files persist across sessions

**✏️ edit_file(file_path, old_string, new_string, replace_all=False)** - Edit existing file
  - Uses string replacement for precise edits
  - Set `replace_all=True` to replace all occurrences
  - Safer than rewriting entire files

**📊 get_session_summary()** - View session files
  - Shows all files created in current session
  - Breaks down by directory
  - Displays total size

**🔍 glob_search(pattern)** - Find files by pattern
  - Use wildcards: *.csv, /data/*.json, test_*.py
  - Fast file discovery without knowing exact names

**🔎 grep_search(search_term)** - Search file contents
  - Find specific text or patterns inside files
  - Optional regex for advanced matching
  - Filter by file type with file_pattern

### File Organization

Organize files by purpose using directories:
{examples}

### Storage Types

- **Session files**: Temporary, auto-cleaned after 7 days
- **Persistent files**: Permanent, available across all sessions

### Best Practices

1. 📋 Always `ls()` first to see what files exist
2. 📖 `read_file()` before editing to understand current content
3. 📂 Organize files in logical directories
4. 🏷️ Use descriptive file names
5. 📊 Use `get_session_summary()` to track your work
6. 🧹 Large sessions will trigger size warnings

### Error Handling

If a file isn't found:
- Use `ls()` to verify the path
- Check spelling and directory structure
- Remember files are isolated by namespace/session
"""
    
    def _get_purpose_examples(self) -> str:
        """Get file organization examples based on agent purpose"""
        examples_map = {
            "finance_assistant": """
  - `/input/` - Raw financial data (transactions, accounts)
  - `/analysis/` - Processed analysis and calculations
  - `/reports/` - Generated financial reports
  - `/charts/` - Data for visualizations
  - `/temp/` - Temporary calculations""",
            
            "coding_assistant": """
  - `/code/` - Source code files
  - `/tests/` - Test files
  - `/docs/` - Documentation
  - `/config/` - Configuration files
  - `/temp/` - Temporary working files""",
            
            "research_assistant": """
  - `/papers/` - Research papers and articles
  - `/notes/` - Research notes and summaries
  - `/data/` - Research data and datasets
  - `/analysis/` - Analysis results
  - `/reports/` - Final research reports""",
            
            "general_assistant": """
  - `/input/` - Input data and files
  - `/data/` - Processed data
  - `/analysis/` - Analysis and calculations
  - `/reports/` - Generated reports
  - `/docs/` - Documentation
  - `/temp/` - Temporary working files"""
        }
        
        return examples_map.get(self.agent_purpose, examples_map["general_assistant"])
    
    def _get_state_values(self, state: Dict[str, Any]) -> tuple[str, Optional[str]]:
        """Extract namespace and session_id from state"""
        namespace = state.get("namespace", self.default_namespace)
        session_id = state.get("session_id", None)
        return namespace, session_id
    
    def _format_file_list(self, files: List[Dict], show_details: bool = True) -> str:
        """Format file list for better readability"""
        if not files:
            return "📁 No files found."
        
        if not self.format_outputs:
            return "\n".join(f['file_path'] for f in files)
        
        output = [f"📁 Found {len(files)} file(s):", ""]
        
        if show_details:
            output.append("┌─────────────────────────────────────────┬──────────┬────────────┐")
            output.append("│ File Path                               │ Size     │ Storage    │")
            output.append("├─────────────────────────────────────────┼──────────┼────────────┤")
            
            for f in files:
                file_path = f['file_path']
                size_bytes = f['size_bytes']
                storage = "session" if f.get('session_id') else "persistent"
                
                if size_bytes < 1024:
                    size_str = f"{size_bytes}B"
                elif size_bytes < 1024 * 1024:
                    size_str = f"{size_bytes/1024:.1f}KB"
                else:
                    size_str = f"{size_bytes/(1024*1024):.1f}MB"
                
                if len(file_path) > 39:
                    file_path = "..." + file_path[-36:]
                
                output.append(f"│ {file_path:<39} │ {size_str:>8} │ {storage:<10} │")
            
            output.append("└─────────────────────────────────────────┴──────────┴────────────┘")
        else:
            for f in files:
                output.append(f"  • {f['file_path']}")
        
        return "\n".join(output)
    
    def _format_error(self, error_type: str, message: str, suggestion: str = "") -> str:
        """Format error messages with helpful suggestions"""
        output = [f"❌ {error_type}: {message}"]
        if suggestion:
            output.append(f"💡 Suggestion: {suggestion}")
        return "\n".join(output)
    
    def _create_tools(self) -> List[Any]:
        """Create FileVault tools with proper InjectedToolArg"""
        tools = []
        
        vault = self.vault
        get_state = self._get_state_values
        format_list = self._format_file_list
        format_error = self._format_error
        max_size = self.max_file_size_warning
        format_out = self.format_outputs
        
        @tool
        def ls(
            path: Optional[str] = None,
            is_shared: Optional[bool]=False,
            runtime: Annotated[Optional[Any], InjectedToolArg()] = None  # FIXED
        ) -> str:
            """
            List all files in FileVault.
            
            Args:
                path: Optional directory path to filter (e.g., "/data/")
                is_shared: Default is False, used if shared context/instructiosn need to be listed.
            
            Returns:
                Formatted list of files with metadata
            """
            try:
                if runtime and hasattr(runtime, 'state'):
                    namespace, session_id = get_state(runtime.state)
                else:
                    namespace, session_id = "default", None
                
                files = vault.list_files_filesystem(
                    namespace=namespace,
                    session_id=session_id,
                    path_prefix=path,
                    is_shared=is_shared
                )
                
                return format_list(files, show_details=True)
                
            except Exception as e:
                logger.error(f"Error in ls: {e}")
                return format_error("List Error", str(e))
        
        @tool
        def read_file(
            file_path: str,
            is_shared: bool=False,
            runtime: Annotated[Optional[Any], InjectedToolArg()] = None  # FIXED
        ) -> str:
            """
            Read file content from FileVault.
            
            Args:
                file_path: Absolute path to file (e.g., /data/report.csv)
                is_shared: Default is false. Is used if shared context templates need to be read.
            
            Returns:
                File content with metadata header
            """
            try:
                if runtime and hasattr(runtime, 'state'):
                    namespace, session_id = get_state(runtime.state)
                else:
                    namespace, session_id = "default", None
                
                content = vault.read_file(
                    file_path=file_path,
                    namespace=namespace,
                    session_id=session_id,
                    is_shared=is_shared
                )
                
                if format_out:
                    size_kb = len(content) / 1024
                    lines = content.count('\n') + 1
                    header = [
                        f"📄 File: {file_path}",
                        f"📊 Size: {size_kb:.1f}KB, {lines} lines",
                        "─" * 60,
                        ""
                    ]
                    return "\n".join(header) + content
                else:
                    return content
                
            except FileNotFoundError:
                return format_error(
                    "File Not Found",
                    f"'{file_path}' does not exist",
                    "Use ls() to see available files"
                )
            except Exception as e:
                logger.error(f"Error reading file: {e}")
                return format_error("Read Error", str(e))
        
        @tool
        def pwd(
            is_shared: bool = False,
            ensure_exists: bool = True,
            runtime: Annotated[Optional[Any], InjectedToolArg()] = None  # FIXED
        ) -> str:
            """
            Return the backing directory for the current session or namespace.
            
            Args:
                is_shared: Return the shared session directory.
                ensure_exists: Create the directory if it is missing.
            
            Returns:
                Absolute path to the workspace directory.
            """
            try:
                if runtime and hasattr(runtime, 'state'):
                    namespace, session_id = get_state(runtime.state)
                else:
                    namespace, session_id = "default", None
                
                path = vault.get_pwd(
                    namespace=namespace,
                    session_id=session_id,
                    is_shared=is_shared,
                    ensure_exists=ensure_exists
                )
                
                if format_out:
                    if is_shared:
                        storage = "shared session"
                    elif session_id:
                        storage = f"session '{session_id}'"
                    else:
                        storage = f"namespace '{namespace}'"
                    return f"📂 Workspace directory: {path}\n🗂️  Storage: {storage}"
                return path
            except Exception as e:
                logger.error(f"Error resolving workspace directory: {e}")
                return format_error("PWD Error", str(e))
            
        #@tool
        def get_vault_location(
            asset_type: Literal["code","tool_results","reports","charts"],
            runtime: Annotated[Optional[Any], InjectedToolArg()] = None 
        ) -> str:
            """
            Gets absolute directory path for different types of assets. reports, code, charts, tool_results etc.

            Args:
                asset_type: Type of asset (code for python files, tool_results for saved large tool results, charts, for generated charts, reports for generated reports)
            
            Returns:
                Message with Absolute File Path
            """
            try:
                if runtime and hasattr(runtime, 'state'):
                    namespace, session_id = get_state(runtime.state)
                else:
                    namespace, session_id = "default", None
                
                location = vault.get_storage_dir_path(asset_type=asset_type, namespace=namespace, session_id=session_id)
                print(f"Location is {location}")
                return location
            except Exception as ex:
                return f"Error fetching location for get vault session for asset {asset_type}"
        
        @tool
        def write_file(
            file_path: str,
            content: str,
            runtime: Annotated[Optional[Any], InjectedToolArg()] = None  # FIXED
        ) -> str:
            """
            Write a new file to FileVault.
            
            Args:
                file_path: Absolute path (e.g., /reports/summary.md)
                content: Complete file content
            
            Returns:
                Success message with file details
            """
            try:
                if runtime and hasattr(runtime, 'state'):
                    namespace, session_id = get_state(runtime.state)
                else:
                    namespace, session_id = "default", None
                
                size_bytes = len(content)
                size_kb = size_bytes / 1024
                
                file_id = vault.write_file(
                    file_path=file_path,
                    content=content,
                    namespace=namespace,
                    session_id=session_id
                )
                
                storage = "session" if session_id else "persistent"
                response = f"✅ Successfully wrote {file_path}\n"
                response += f"📊 Size: {size_kb:.1f}KB, Storage: {storage}"
                
                if size_bytes > max_size:
                    response += f"\n⚠️  Warning: Large file ({size_kb:.1f}KB)"
                
                return response
                
            except Exception as e:
                logger.error(f"Error writing file: {e}")
                return format_error("Write Error", str(e))
        
        @tool
        def edit_file(
            file_path: str,
            old_string: str,
            new_string: str,
            replace_all: bool = False,
            runtime: Annotated[Optional[Any], InjectedToolArg()] = None  # FIXED
        ) -> str:
            """
            Edit an existing file using string replacement.
            
            Args:
                file_path: Path to file
                old_string: String to find and replace
                new_string: Replacement string
                replace_all: Replace all occurrences (default: False)
            
            Returns:
                Success message with replacement count
            """
            try:
                if runtime and hasattr(runtime, 'state'):
                    namespace, session_id = get_state(runtime.state)
                else:
                    namespace, session_id = "default", None
                
                result = vault.edit_file(
                    file_path=file_path,
                    old_string=old_string,
                    new_string=new_string,
                    namespace=namespace,
                    session_id=session_id,
                    replace_all=replace_all
                )
                
                if "Successfully" in result:
                    return f"✅ {result}"
                else:
                    if "not found" in result.lower():
                        return format_error(
                            "String Not Found",
                            f"'{old_string}' not found in {file_path}",
                            "Read the file first to verify the exact string"
                        )
                    elif "appears" in result:
                        return format_error(
                            "Multiple Matches",
                            result.replace("Error: ", ""),
                            "Add more context to old_string or use replace_all=True"
                        )
                    else:
                        return format_error("Edit Error", result)
                
            except Exception as e:
                logger.error(f"Error editing file: {e}")
                return format_error("Edit Error", str(e))
        
        @tool
        def get_session_summary(
            runtime: Annotated[Optional[Any], InjectedToolArg()] = None  # FIXED
        ) -> str:
            """
            Get summary of all files in current session.
            
            Returns:
                Formatted summary with file counts and sizes
            """
            try:
                if not runtime or not hasattr(runtime, 'state'):
                    return "⚠️  No session context available"
                
                session_id = runtime.state.get("session_id")
                context_data_loc = runtime.state.get("context_data_loc")
                if not session_id:
                    return "⚠️  No active session (using persistent storage)"
                
                
                summary = vault.get_session_summary(session_id)
                
               
                
                output = [
                    f"📊 Session Summary: {session_id}",
                    "**Context Data (Directories with explanation)**",

                ]
                
                output.append(f"""
                                {context_data_loc}
                              """)
                
                print(f"{output}")

                
                return "\n".join(output)
                
            except Exception as e:
                logger.error(f"Error getting session summary: {e}")
                return format_error("Summary Error", str(e))
        
        @tool
        def glob_search(
            pattern: str,
            case_sensitive: bool = False,
            runtime: Annotated[Optional[Any], InjectedToolArg()] = None  # FIXED
        ) -> str:
            """
            Search for files using glob patterns (wildcard matching).
            
            Args:
                pattern: Glob pattern (supports *, ?, [], {})
                case_sensitive: Case-sensitive matching (default: False)
            
            Examples:
                "*.csv" - All CSV files
                "/data/*.json" - JSON files in /data/
                "*.{csv,json}" - Multiple extensions
            
            Returns:
                Formatted list of matching files
            """
            try:
                if runtime and hasattr(runtime, 'state'):
                    namespace = runtime.state.get("namespace", "default")
                    session_id = runtime.state.get("session_id")
                else:
                    namespace = "default"
                    session_id = None
                
                all_files = vault.list_files(namespace=namespace, session_id=session_id)
                
                if not all_files:
                    return "📁 No files in workspace to search"
                
                # Handle {a,b,c} brace expansion
                if '{' in pattern and '}' in pattern:
                    start = pattern.find('{')
                    end = pattern.find('}')
                    if start != -1 and end != -1:
                        before = pattern[:start]
                        options = pattern[start+1:end].split(',')
                        after = pattern[end+1:]
                        patterns = [before + opt.strip() + after for opt in options]
                    else:
                        patterns = [pattern]
                else:
                    patterns = [pattern]
                
                # Match files
                matched_files = []
                for file_meta in all_files:
                    file_path = file_meta['file_path']
                    for pat in patterns:
                        if case_sensitive:
                            match = fnmatch.fnmatch(file_path, pat)
                        else:
                            match = fnmatch.fnmatch(file_path.lower(), pat.lower())
                        
                        if match:
                            matched_files.append(file_meta)
                            break
                
                if not matched_files:
                    return f"🔍 No files match pattern: '{pattern}'"
                
                # Format results
                output = [f"🔍 Found {len(matched_files)} file(s) matching '{pattern}':", ""]
                
                by_dir = {}
                for f in matched_files:
                    path = f['file_path']
                    dir_name = str(Path(path).parent)
                    if dir_name not in by_dir:
                        by_dir[dir_name] = []
                    by_dir[dir_name].append(f)
                
                for dir_name in sorted(by_dir.keys()):
                    output.append(f"📂 {dir_name}")
                    for f in by_dir[dir_name]:
                        filename = Path(f['file_path']).name
                        size_kb = f['size_bytes'] / 1024
                        output.append(f"   • {filename:<40} ({size_kb:>6.1f}KB)")
                    output.append("")
                
                return "\n".join(output)
                
            except Exception as e:
                return format_error("Glob Search Error", str(e))
        
        @tool
        def grep_search(
            search_term: str,
            file_pattern: Optional[str] = None,
            case_sensitive: bool = False,
            regex: bool = False,
            max_results: int = 50,
            context_lines: int = 0,
            is_shared: bool=False,
            runtime: Annotated[Optional[Any], InjectedToolArg()] = None  # FIXED
        ) -> str:
            """
            Search file contents using grep-like functionality.
            
            Args:
                search_term: Text or regex pattern to search for
                file_pattern: Optional glob pattern to filter files
                case_sensitive: Case-sensitive search
                regex: Treat search_term as regex
                max_results: Maximum matches to return
                context_lines: Lines of context before/after match
                is_shared: If search needs to be done inside shared context like (Templates, Additional Instructions, etc.)
            
            Returns:
                Formatted list of matches with line numbers
            """
            try:
                if runtime and hasattr(runtime, 'state'):
                    namespace = runtime.state.get("namespace", "default")
                    session_id = runtime.state.get("session_id")
                else:
                    namespace = "default"
                    session_id = None
                
                all_files = vault.list_files(namespace=namespace, session_id=session_id)
                
                if not all_files:
                    return "📁 No files in workspace to search"
                
                # Filter by file pattern
                if file_pattern:
                    files_to_search = [
                        f for f in all_files 
                        if fnmatch.fnmatch(f['file_path'].lower(), file_pattern.lower())
                    ]
                    if not files_to_search:
                        return f"🔍 No files match pattern: '{file_pattern}'"
                else:
                    files_to_search = all_files
                
                # Compile pattern
                if regex:
                    try:
                        if case_sensitive:
                            pattern = re.compile(search_term)
                        else:
                            pattern = re.compile(search_term, re.IGNORECASE)
                    except re.error as e:
                        return format_error("Invalid Regex", str(e))
                else:
                    escaped = re.escape(search_term)
                    if case_sensitive:
                        pattern = re.compile(escaped)
                    else:
                        pattern = re.compile(escaped, re.IGNORECASE)
                
                # Search files
                matches = []
                files_searched = 0
                
                for file_meta in files_to_search:
                    try:
                        content = vault.read_file(
                            file_meta['file_path'],
                            namespace=namespace,
                            session_id=session_id,
                            update_access=False,
                            is_shared=is_shared
                        )
                        
                        files_searched += 1
                        lines = content.split('\n')
                        
                        for line_num, line in enumerate(lines, 1):
                            if pattern.search(line):
                                context_before = []
                                context_after = []
                                
                                if context_lines > 0:
                                    start = max(0, line_num - context_lines - 1)
                                    end = min(len(lines), line_num + context_lines)
                                    context_before = lines[start:line_num-1]
                                    context_after = lines[line_num:end]
                                
                                matches.append({
                                    'file': file_meta['file_path'],
                                    'line_num': line_num,
                                    'line': line.strip(),
                                    'context_before': context_before,
                                    'context_after': context_after
                                })
                                
                                if len(matches) >= max_results:
                                    break
                        
                        if len(matches) >= max_results:
                            break
                    except:
                        continue
                
                if not matches:
                    return f"🔍 No matches found for '{search_term}' in {files_searched} file(s)"
                
                # Format results
                output = [
                    f"🔍 Found {len(matches)} match(es) for '{search_term}' in {files_searched} file(s):",
                    ""
                ]
                
                current_file = None
                for match in matches[:max_results]:
                    if match['file'] != current_file:
                        if current_file is not None:
                            output.append("")
                        output.append(f"📄 {match['file']}")
                        current_file = match['file']
                    
                    for ctx_line in match['context_before']:
                        output.append(f"     {ctx_line[:100]}")
                    
                    line_preview = match['line'][:100]
                    output.append(f"  ➤  Line {match['line_num']}: {line_preview}")
                    
                    for ctx_line in match['context_after']:
                        output.append(f"     {ctx_line[:100]}")
                
                if len(matches) > max_results:
                    output.append("")
                    output.append(f"⚠️  Showing first {max_results} of {len(matches)} total matches")
                
                return "\n".join(output)
                
            except Exception as e:
                return format_error("Grep Search Error", str(e))
        
        tools = [ls, read_file, pwd, write_file, edit_file, get_session_summary, glob_search, grep_search]
        return tools
    
    def before_agent(self, state: AgentState, runtime: Any) -> Optional[Dict[str, Any]]:
        """Initialize FileVault state"""
        updates = {}
        
        if "namespace" not in state:
            updates["namespace"] = self.default_namespace
        if "session_id" not in state or state["session_id"] is None:
            updates["session_id"] = str(time.time() * 1000)
            self.session_id = updates["session_id"]
        if "files_created" not in state:
            updates["files_created"] = 0
        if "files_read" not in state:
            updates["files_read"] = 0
        if "total_bytes_written" not in state:
            updates["total_bytes_written"] = 0

        if "context_data_loc" not in state:
            print("updating context data_loca")
            updates["context_data_loc"]=[
            ContextPath(relative_path="/code", 
                        absolute_path= self.vault.get_storage_dir_path(session_id=self.session_id,asset_type="code"),
                        description="Location where ananlysis Python or r-base code is saved"),
            ContextPath(relative_path="/charts", 
                        absolute_path= self.vault.get_storage_dir_path(session_id=self.session_id,asset_type="charts"),
                        description="Location where Charts png files are saved."),
            ContextPath(relative_path="/reports", 
                        absolute_path= self.vault.get_storage_dir_path(session_id=self.session_id,asset_type="reports"),
                        description="Location where reports are saved"),
            ContextPath(relative_path="/data", 
                        absolute_path= self.vault.get_storage_dir_path(session_id=self.session_id,asset_type="data"),
                        description="Location where data from tool calls are saved"),
            ContextPath(relative_path="/analysis", 
                        absolute_path= self.vault.get_storage_dir_path(session_id=self.session_id,asset_type="analysis"),
                        description="Location where agent analysis is stored"),
            ContextPath(relative_path="/tool_results", 
                        absolute_path= self.vault.get_storage_dir_path(session_id=self.session_id,asset_type="tool_results"),
                        description="Location where Large tool results are saved.")
          
        ]
        
        return updates if updates else None
    
    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        """Add FileVault system prompt"""
        if self.system_prompt:
            if request.system_prompt:
                request.system_prompt = request.system_prompt + "\n\n" + self.system_prompt
            else:
                request.system_prompt = self.system_prompt
        
        return handler(request)
    
    async def awrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], Awaitable[ModelResponse]],
    ) -> ModelResponse:
        """Async version of wrap_model_call"""
        if self.system_prompt:
            if request.system_prompt:
                request.system_prompt = request.system_prompt + "\n\n" + self.system_prompt
            else:
                request.system_prompt = self.system_prompt
        
        return await handler(request)
