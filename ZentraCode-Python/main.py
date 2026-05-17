import streamlit as st
import os
import subprocess
import sys
import io
import traceback

# --- STYLING & PAGE INITIALIZATION ---
st.set_page_config(page_title="Acode-VS Cloud Mobile Studio", page_icon="⚡", layout="wide")

# Inject complete VS Code dark theme override styles
st.markdown("""
    <style>
    .stApp {
        background-color: #1e1e1e !important;
        color: #d4d4d4 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    [data-testid="stSidebar"] {
        background-color: #252526 !important;
        border-right: 1px solid #3c3c3c !important;
    }
    div.stTextArea textarea {
        font-family: 'Consolas', 'Fira Code', 'Courier New', monospace !important;
        font-size: 15px !important;
        background-color: #1c1c1c !important;
        color: #9cdcfe !important;
        border: 1px solid #2d2d2d !important;
        line-height: 1.5 !important;
    }
    div.stTextArea textarea:focus {
        border: 1px solid #007acc !important;
    }
    div.stTextInput input {
        background-color: #1c1c1c !important;
        color: #4ec9b0 !important;
        font-family: 'Consolas', monospace !important;
        border: 1px solid #3c3c3c !important;
    }
    div.stButton > button {
        background-color: #0e639c !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 2px !important;
        font-size: 13px !important;
        padding: 6px 12px !important;
    }
    div.stButton > button:hover {
        background-color: #1177bb !important;
    }
    .terminal-box {
        background-color: #181818;
        border: 1px solid #2d2d2d;
        padding: 10px;
        border-radius: 4px;
        font-family: 'Consolas', monospace;
        font-size: 13px;
        color: #d4d4d4;
        white-space: pre-wrap;
        height: 250px;
        overflow-y: auto;
        margin-bottom: 10px;
    }
    .acode-tab-active {
        background-color: #1e1e1e;
        border-bottom: 2px solid #007acc;
        padding: 6px 16px;
        font-size: 13px;
        font-weight: bold;
        color: #ffffff;
        display: inline-block;
    }
    </style>
""", unsafe_allow_html=True)

# Define physical workspaces paths on host container filesystem
WORKSPACE_DIR = os.path.abspath("./workspace")
BIN_DIR = os.path.join(WORKSPACE_DIR, "bin") # Buildozer default output path
os.makedirs(WORKSPACE_DIR, exist_ok=True)

# Generate template compilation file if clean setup
default_target = os.path.join(WORKSPACE_DIR, "main.py")
if not os.path.exists(default_target):
    with open(default_target, "w") as f:
        f.write("# Write Ursina, Kivy, or CustomTkinter scripts naturally!\nimport sys\nprint('Python Runtime Module Hook Verified.')\nprint(f'Interpreter: {sys.version}')")

# Initialize persistent session states
if "open_tabs" not in st.session_state:
    st.session_state.open_tabs = [default_target]
if "active_tab" not in st.session_state:
    st.session_state.active_tab = default_target
if "bash_terminal_log" not in st.session_state:
    st.session_state.bash_terminal_log = "Microsoft Windows Subsystem [Bash Core Online]\nLinked to global custom pip.conf database configurations.\n"
if "python_console_log" not in st.session_state:
    st.session_state.python_console_log = "Python 3 Runtime Compiler Console Active.\nClick 'Run Python Code' to populate output logs stream.\n"

# --- SIDEBAR PANEL: WORKSPACE FILE TREE ---
with st.sidebar:
    st.markdown("<h4 style='color:#ffffff; font-size:13px; letter-spacing:1px;'>EXPLORER: PROJECTS</h4>", unsafe_allow_html=True)
    st.markdown("---")
    
    local_files = sorted(os.listdir(WORKSPACE_DIR))
    # Filter files vs dynamic generation folders
    workspace_files = [f for f in local_files if os.path.isfile(os.path.join(WORKSPACE_DIR, f))]
    
    for f in workspace_files:
        full_p = os.path.join(WORKSPACE_DIR, f)
        icon = "🐍" if f.endswith(".py") else "📄"
        
        btn_style = "● " if st.session_state.active_tab == full_p else "  "
        if st.button(f"{btn_style}{icon} {f}", key=f"sidebar_f_{f}", use_container_width=True):
            if full_p not in st.session_state.open_tabs:
                st.session_state.open_tabs.append(full_p)
            st.session_state.active_tab = full_p
            st.rerun()

    st.markdown("---")
    new_f_input = st.text_input("Create File:", placeholder="script.py", key="new_file_creation_input")
    if st.button("➕ Inject New File Target") and new_f_input:
        new_path = os.path.join(WORKSPACE_DIR, new_f_input)
        with open(new_path, "w") as f: f.write("# New Script Working Context\n")
        if new_path not in st.session_state.open_tabs:
            st.session_state.open_tabs.append(new_path)
        st.session_state.active_tab = new_path
        st.rerun()

# --- TOP AREA NAVIGATION BAR TABS (Acode UI Profile) ---
if st.session_state.open_tabs:
    tab_cols = st.columns(len(st.session_state.open_tabs) + 4)
    for idx, t_path in enumerate(st.session_state.open_tabs):
        f_title = os.path.basename(t_path)
        is_active = st.session_state.active_tab == t_path
        
        with tab_cols[idx]:
            if is_active:
                st.markdown(f'<div class="acode-tab-active">● {f_title}</div>', unsafe_allow_html=True)
            else:
                if st.button(f"  {f_title}  ", key=f"acode_tab_trigger_{idx}"):
                    st.session_state.active_tab = t_path
                    st.rerun()

st.markdown("<div style='margin-bottom:15px; border-bottom: 1px solid #3c3c3c;'></div>", unsafe_allow_html=True)

# --- WORKSPACE GRID DIVISION LAYER ---
left_editor_pane, right_terminal_pane = st.columns([1.1, 0.9])

with left_editor_pane:
    st.markdown(f"<p style='color:#858585; font-size:12px; margin-bottom:2px;'>CURRENT WORKSPACE PATH: {st.session_state.active_tab}</p>", unsafe_allow_html=True)
    
    if os.path.exists(st.session_state.active_tab):
        with open(st.session_state.active_tab, "r") as f:
            file_code_buffer = f.read()
    else:
        file_code_buffer = ""

    editor_canvas = st.text_area(
        label="VS Code Workspace Canvas",
        value=file_code_buffer,
        height=530,
        label_visibility="collapsed",
        key="main_code_canvas_field"
    )

    if editor_canvas != file_code_buffer:
        with open(st.session_state.active_tab, "w") as f:
            f.write(editor_canvas)

    action_cols = st.columns(3)
    with action_cols:
        if st.button("▶ Run Code in Console", use_container_width=True):
            old_stdout = sys.stdout
            redirected_io = sys.stdout = io.StringIO()
            try:
                compiled_code = compile(editor_canvas, '<string>', 'exec')
                exec(compiled_code, {"__name__": "__main__"})
                output_captured = redirected_io.getvalue()
                st.session_state.python_console_log = output_captured if output_captured else "[Code executed successfully with no print output markers returned.]\n"
            except Exception as e:
                err_stream = io.StringIO()
                traceback.print_exc(file=err_stream)
                st.session_state.python_console_log = f"❌ RUNTIME RUN FAULT ERROR:\n-------------------------\n{err_stream.getvalue()}"
            finally:
                sys.stdout = old_stdout
            st.rerun()

    with action_cols:
        if st.button("❌ Close Document Tab", use_container_width=True):
            if len(st.session_state.open_tabs) > 1:
                st.session_state.open_tabs.remove(st.session_state.active_tab)
                st.session_state.active_tab = st.session_state.open_tabs
            st.rerun()
    with action_cols:
        st.download_button("📥 Export Target File", data=editor_canvas, file_name=os.path.basename(st.session_state.active_tab), use_container_width=True)

with right_terminal_pane:
    # --- PANEL ONE: BASH SHELL ---
    st.markdown("<p style='color:#00e6ff; font-size:12px; font-weight:bold; margin-bottom:2px;'>📟 BASH TERMINAL (pip install / git clone / buildozer)</p>", unsafe_allow_html=True)
    st.markdown(f'<div class="terminal-box" style="border-left: 3px solid #0e639c;">{st.session_state.bash_terminal_log}</div>', unsafe_allow_html=True)
    
    def execute_bash_shell_command():
        cmd_query = st.session_state.bash_input_prompt_line.strip()
        if not cmd_query: return
        st.session_state.bash_input_prompt_line = ""
        
        st.session_state.bash_terminal_log += f"\nuser@cloud-studio:~/workspace$ {cmd_query}\n"
        proc = subprocess.run(cmd_query, shell=True, text=True, capture_output=True, cwd=WORKSPACE_DIR)
        
        if proc.stdout: st.session_state.bash_terminal_log += proc.stdout
        if proc.stderr: st.session_state.bash_terminal_log += f"[ERROR LOG THREAD]:\n{proc.stderr}"
        st.rerun()
        
    st.text_input("Bash Prompt Prompt:", placeholder="e.g. pip install colorama  OR  git clone [url]", key="bash_input_prompt_line", on_change=execute_bash_shell_command, label_visibility="collapsed")

    st.markdown("<div style='margin-bottom:15px;'></div>", unsafe_allow_html=True)

    # --- PANEL TWO: PYTHON CONSOLE ---
    st.markdown("<p style='color:#39ff14; font-size:12px; font-weight:bold; margin-bottom:2px;'>🖥️ PYTHON PROGRAM RUNTIME CONSOLE (Execution Results)</p>", unsafe_allow_html=True)
    st.markdown(f'<div class="terminal-box" style="border-left: 3px solid #39ff14; color:#39ff14; height:260px;">{st.session_state.python_console_log}</div>', unsafe_allow_html=True)
    
    # --- AUTOMATED APK DOWNLOAD MODULE CHANNEL ---
    st.markdown("---")
    apk_found = False
    target_apk_path = ""
    
    # Scan the buildozer binary distribution folder for compiled application targets
    if os.path.exists(BIN_DIR):
        apk_files = [f for f in os.listdir(BIN_DIR) if f.endswith(".apk")]
        if apk_files:
            apk_found = True
            target_apk_path = os.path.join(BIN_DIR, apk_files[0]) # Target latest built package file

    if apk_found:
        st.markdown("<p style='color:#ff9900; font-size:13px; font-weight:bold; margin-bottom:2px;'>📥 ANDROID DISTRIBUTION PIPELINE DETECTED</p>", unsafe_allow_html=True)
        with open(target_apk_path, "rb") as apk_file:
            st.download_button(
                label=f"🤖 Download Package: {os.path.basename(target_apk_path)}",
                data=apk_file,
                file_name=os.path.basename(target_apk_path),
                mime="application/vnd.android.package-archive",
                use_container_width=True
            )

    # Bottom Auxiliary Action Strip Layout Row
    tool_cols = st.columns(2)
    with tool_cols:
        if st.button("🤖 Run Buildozer Android Pipeline", use_container_width=True):
            st.session_state.bash_terminal_log += "\nuser@cloud-studio:~$ buildozer android debug\n"
            st.session_state.bash_terminal_log += "Compiling targets profiles. Fetching Android SDK/NDK structures...\n"
            
            # Execute compiler system thread
            proc = subprocess.run("buildozer android debug", shell=True, text=True, capture_output=True, cwd=WORKSPACE_DIR)
            st.session_state.bash_terminal_log += proc.stdout + proc.stderr
            st.rerun()
            
    with tool_cols:
        if st.button("🔧 Init Buildozer Spec Profile", use_container_width=True):
            subprocess.run("buildozer init", shell=True, cwd=WORKSPACE_DIR)
            st.session_state.bash_terminal_log += "\n[System info]: Generated fresh default buildozer.spec profile template inside user files tree.\n"
            st.rerun()
    
