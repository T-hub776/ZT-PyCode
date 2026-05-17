import streamlit as st
import os
import subprocess
import time

# --- VS CODE / ACODE MONOCHROME THEME CORE INJECTION ---
st.set_page_config(page_title="Acode-VS Web Core", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    /* Global Background Elements matching VS Code Dark Pro */
    .stApp {
        background-color: #1e1e1e !important;
        color: #d4d4d4 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* VS Code Left Activity Bar & Sidebar Restyling */
    [data-testid="stSidebar"] {
        background-color: #252526 !important;
        border-right: 1px solid #3c3c3c !important;
    }
    
    /* Document Monospace Text Area Overhaul (Code Canvas) */
    div.stTextArea textarea {
        font-family: 'Consolas', 'Fira Code', 'Courier New', monospace !important;
        font-size: 15px !important;
        background-color: #1c1c1c !important;
        color: #9cdcfe !important; /* VS Code Variable Cyan Tint */
        border: 1px solid #2d2d2d !important;
        line-height: 1.5 !important;
        border-radius: 4px !important;
    }
    div.stTextArea textarea:focus {
        border: 1px solid #007acc !important; /* VS Code Focus Blue */
    }

    /* Terminal Prompt Box */
    div.stTextInput input {
        background-color: #1c1c1c !important;
        color: #4ec9b0 !important; /* Hacker Emerald */
        font-family: 'Consolas', monospace !important;
        border: 1px solid #3c3c3c !important;
        border-radius: 4px !important;
    }

    /* VS Code Action Buttons Styling */
    div.stButton > button {
        background-color: #0e639c !important; /* VS Code Accent Blue */
        color: #ffffff !important;
        border: none !important;
        border-radius: 2px !important;
        font-weight: 500 !important;
        font-size: 13px !important;
        padding: 6px 12px !important;
        transition: background-color 0.2s ease;
    }
    div.stButton > button:hover {
        background-color: #1177bb !important;
        color: #ffffff !important;
    }

    /* Standardized output view blocks */
    .vscode-terminal-box {
        background-color: #1e1e1e;
        border: 1px solid #3c3c3c;
        padding: 12px;
        border-radius: 4px;
        font-family: 'Consolas', monospace;
        font-size: 13px;
        color: #f1f1f1;
        white-space: pre-wrap;
        height: 280px;
        overflow-y: auto;
    }
    
    /* Acode Styled Tab Indicators */
    .acode-tab-active {
        background-color: #1e1e1e;
        border-bottom: 2px solid #007acc;
        padding: 6px 16px;
        font-size: 13px;
        font-weight: bold;
        display: inline-block;
        color: #ffffff;
    }
    </style>
""", unsafe_allow_html=True)

# Ensure project sandbox environments exist on server storage disk
WORKSPACE_DIR = os.path.abspath("./workspace")
os.makedirs(WORKSPACE_DIR, exist_ok=True)

# Generate baseline template targets if clean boot
default_target = os.path.join(WORKSPACE_DIR, "main.py")
if not os.path.exists(default_target):
    with open(default_target, "w") as f:
        f.write("# VS Code + Acode Workspace Environment\nprint('Initializing Core Debug Test Link...')")

# Initialize workspace tracking dictionaries
if "open_tabs" not in st.session_state:
    st.session_state.open_tabs = [default_target]
if "active_tab" not in st.session_state:
    st.session_state.active_tab = default_target
if "terminal_log" not in st.session_state:
    st.session_state.terminal_log = "Microsoft VS Code Server Protocol Initialized.\nWelcome to Acode Web Console Cloud Sync Subsystem v2.0.\n"

# --- SIDEBAR PANEL: VS CODE FILE EXPLORER TREE ---
with st.sidebar:
    st.markdown("<h3 style='color:#ffffff; font-size:14px; letter-spacing:1px; margin-bottom:15px;'>EXPLORER: WORKSPACE</h3>", unsafe_allow_html=True)
    
    # Read workspace contents dynamically
    local_files = sorted(os.listdir(WORKSPACE_DIR))
    
    # Display files as an interactive click-list
    st.markdown("<div style='margin-bottom:10px;'></div>", unsafe_allow_html=True)
    for f in local_files:
        full_p = os.path.join(WORKSPACE_DIR, f)
        icon = "🐍" if f.endswith(".py") else "📄"
        
        # Highlight selected active tab
        label_color = "#ffffff" if st.session_state.active_tab == full_p else "#858585"
        if st.button(f"{icon} {f}", key=f"file_{f}", use_container_width=True):
            if full_p not in st.session_state.open_tabs:
                st.session_state.open_tabs.append(full_p)
            st.session_state.active_tab = full_p
            st.rerun()

    st.markdown("---")
    new_f_name = st.text_input("New File Name:", placeholder="script.py")
    if st.button("📝 Add New File") and new_f_name:
        new_path = os.path.join(WORKSPACE_DIR, new_f_name)
        with open(new_path, "w") as f: f.write("# New Script Context Layer\n")
        if new_path not in st.session_state.open_tabs:
            st.session_state.open_tabs.append(new_path)
        st.session_state.active_tab = new_path
        st.rerun()

# --- MAIN WORKSPACE INTERFACE PANEL ---
st.markdown("<h2 style='color:#ffffff; font-size:18px; margin-bottom:0px;'>⚡ Code Engine IDE</h2>", unsafe_allow_html=True)

# --- ACODE MULTI-TAB PANEL BAR ---
if st.session_state.open_tabs:
    tab_cols = st.columns(len(st.session_state.open_tabs) + 4) # Add buffer room
    for idx, t_path in enumerate(st.session_state.open_tabs):
        f_title = os.path.basename(t_path)
        is_active = st.session_state.active_tab == t_path
        
        with tab_cols[idx]:
            # Graphical styling highlighting which workspace tab is open
            if is_active:
                st.markdown(f'<div class="acode-tab-active">● {f_title}</div>', unsafe_allow_html=True)
            else:
                if st.button(f"  {f_title}  ", key=f"tab_btn_{idx}"):
                    st.session_state.active_tab = t_path
                    st.rerun()

st.markdown("<div style='margin-bottom:15px; border-bottom: 1px solid #2d2d2d;'></div>", unsafe_allow_html=True)

# --- CENTRAL WORKSPACE DIVISION LAYER ---
left_editor_pane, right_terminal_pane = st.columns([1.2, 0.8])

with left_editor_pane:
    # Read active file content onto text area box
    if os.path.exists(st.session_state.active_tab):
        with open(st.session_state.active_tab, "r") as f:
            code_payload = f.read()
    else:
        code_payload = ""

    # Large Multi-Line Coding Dashboard Panel Box
    code_canvas = st.text_area(
        label="VS Code Canvas Block",
        value=code_payload,
        height=400,
        label_visibility="collapsed",
        key="canvas_editor_field"
    )

    # Save to workspace filesystem silently on updates
    if code_canvas != code_payload:
        with open(st.session_state.active_tab, "w") as f:
            f.write(code_canvas)

    # IDE Execution Panel Action Strip Row
    action_cols = st.columns([1, 1, 1])
    with action_cols[0]:
        if st.button("▶ Run Script (Xvfb Headless)", use_container_width=True):
            st.session_state.terminal_log += f"\nuser@cloud-ide:~$ xvfb-run python3 {os.path.basename(st.session_state.active_tab)}\n"
            
            # Pipe execution through headless frame buffer to support Kivy/Tkinter/Ursina GUI frameworks
            execution_cmd = f"xvfb-run --server-args='-screen 0 1024x768x24' python3 {st.session_state.active_tab}"
            proc_run = subprocess.run(execution_cmd, shell=True, text=True, capture_output=True)
            
            if proc_run.stdout: st.session_state.terminal_log += proc_run.stdout
            if proc_run.stderr: st.session_state.terminal_log += f"Error Log Thread Output:\n{proc_run.stderr}"
            st.rerun()
            
    with action_cols[1]:
        if st.button("❌ Close File Tab", use_container_width=True):
            if len(st.session_state.open_tabs) > 1:
                st.session_state.open_tabs.remove(st.session_state.active_tab)
                st.session_state.active_tab = st.session_state.open_tabs[0]
            st.rerun()
            
    with action_cols[2]:
        st.download_button("📥 Export Code", data=code_canvas, file_name=os.path.basename(st.session_state.active_tab), use_container_width=True)

with right_terminal_pane:
    st.markdown("<p style='color:#aaaaaa; font-size:13px; font-weight:bold; margin-bottom:5px;'>⚙️ OUTPUT CONSOLE & BASH TERMINAL</p>", unsafe_allow_html=True)
    
    # Render the styled integrated output console box
    st.markdown(f'<div class="vscode-terminal-box">{st.session_state.terminal_log}</div>', unsafe_allow_html=True)

    # Shell intake routine pipeline intercept processor
    def shell_input_handler():
        raw_prompt = st.session_state.terminal_prompt_field.strip()
        if not raw_prompt: return
        st.session_state.terminal_prompt_field = "" # Flush prompt string
        
        st.session_state.terminal_log += f"\nuser@cloud-ide:~$ {raw_prompt}\n"
        
        # Execute natively on the host container shell layer
        shell_proc = subprocess.run(raw_prompt, shell=True, text=True, capture_output=True, cwd=WORKSPACE_DIR)
        
        if shell_proc.stdout: st.session_state.terminal_log += shell_proc.stdout
        if shell_proc.stderr: st.session_state.terminal_log += shell_proc.stderr

    st.text_input("Terminal Shell Input Line Prompt:", placeholder="pip install [package] / buildozer android debug", key="terminal_prompt_field", on_change=shell_input_handler, label_visibility="collapsed")

    # Lower Framework Accelerator Bar Layout Block
    st.markdown("<div style='margin-bottom:15px;'></div>", unsafe_allow_html=True)
    tool_cols = st.columns(2)
    with tool_cols[0]:
        if st.button("🤖 Buildozer Init Profile", use_container_width=True):
            subprocess.run("buildozer init", shell=True, cwd=WORKSPACE_DIR)
            st.session_state.terminal_log += "\n[System info]: Initiated buildozer.spec profile sheet inside user workspace storage.\n"
            st.rerun()
    with tool_cols[1]:
        if st.button("🧹 Flush Logs", use_container_width=True):
            st.session_state.terminal_log = "Terminal logs cleared.\n"
            st.rerun()

