# Guide: Running Claude Code Multi-Account Workflows in Zed (Windows)

This guide outlines how to configure **Zed** as your central workspace (rooted at `C:\dev`) to manage multiple nested customer projects and spin up parallel **Claude Code** sessions across different accounts or custom aliases (`claude-priv`, `agv`) using keyboard shortcuts.

---

## 1. Prerequisites
* **Zed Editor** installed on Windows.
* **Claude Code** CLI installed and configured globally.
* Your root workspace opened in Zed at **`C:\dev`** to expose your full directory tree (`customers`, subfolders, etc.).

---

## 2. Setting Up Task Automation (`tasks.json`)
Zed allows you to define reusable commands that automatically target your active workspace directory. 

1. Open the Zed Command Palette (**`Ctrl + Shift + P`**).
2. Run **`task: edit tasks`**.
3. Replace or update your tasks file with the following configuration:

```json
[
  {
    "label": "Claude: Primary",
    "command": "claude",
    "cwd": "$WORKSPACE_DIR",
    "reveal": "always"
  },
  {
    "label": "Claude: Private Account",
    "command": "powershell -Command \"$env:ANTHROPIC_API_KEY='YOUR_API_KEY_HERE'; claude\"",
    "cwd": "$WORKSPACE_DIR",
    "reveal": "always"
  },
  {
    "label": "Run AGV",
    "command": "agv",
    "cwd": "$WORKSPACE_DIR",
    "reveal": "always"
  }
]
```

---

## 3. Configuring Keyboard Shortcuts (`keymap.json`)
To launch your sessions instantly without typing out paths or navigating menus, bind your tasks to custom keybindings.

1. Open the Zed Command Palette (**`Ctrl + Shift + P`**).
2. Run **`zed: open keymap`**.
3. Add the following keymap configuration:

```json
[
  {
    "context": "Workspace",
    "bindings": {
      "ctrl-alt-c": "task::Spawn { label: \"Claude: Primary\" }",
      "ctrl-alt-p": "task::Spawn { label: \"Claude: Private Account\" }",
      "ctrl-alt-a": "task::Spawn { label: \"Run AGV\" }"
    }
  }
]
```

---

## 4. Daily Workflow
1. **Open Workspace:** Launch Zed and open your root `C:\dev` folder. Your complete directory tree (including deep nested paths like `customers\Aeven\atomicservicenow`) is displayed in the sidebar.
2. **Focus Project:** Click or highlight the specific customer/project folder in your sidebar that you want to target.
3. **Launch Instantly:**
   * Press **`Ctrl + Alt + C`** to start your primary Claude Code session.
   * Press **`Ctrl + Alt + P`** to start your secondary/private account session.
   * Press **`Ctrl + Alt + A`** to run your custom `agv` tool.
4. **Parallel Execution:** Split your terminal panels inside Zed to run multiple Claude sessions side-by-side across different customer folders simultaneously.