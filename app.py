import os
import sys
import io
import socket
import threading
import time
import multiprocessing
import webbrowser

# 處理 PyInstaller --noconsole 模式下 sys.stdout / sys.stderr 為 None 的情況
class DummyStream(io.StringIO):
    def isatty(self):
        return False
    def write(self, s):
        pass
    def flush(self):
        pass

if sys.stdout is None:
    sys.stdout = DummyStream()
if sys.stderr is None:
    sys.stderr = DummyStream()
if sys.stdin is None:
    sys.stdin = DummyStream()

import uvicorn
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# 處理 PyInstaller 打包時的資源路徑
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys._MEIPASS)
    APP_DIR = Path(os.path.dirname(sys.executable))
else:
    BASE_DIR = Path(__file__).resolve().parent
    APP_DIR = BASE_DIR

sys.path.insert(0, str(BASE_DIR))

from services.agent_manager import AgentManager
from services.installer import SubagentInstaller

app = FastAPI(title="Agency Subagents 專家子代理管理器", version="1.2.0")

# 允許跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent_manager = AgentManager(str(BASE_DIR))
installer = SubagentInstaller(str(APP_DIR))

# Pydantic 請求模型
class InstallRequest(BaseModel):
    agent_id: str
    target_type: str = "antigravity_project"
    custom_path: Optional[str] = None
    project_path: Optional[str] = None

class InstallBatchRequest(BaseModel):
    agent_ids: List[str]
    target_type: str = "antigravity_project"
    custom_path: Optional[str] = None
    project_path: Optional[str] = None

class UninstallRequest(BaseModel):
    agent_id: str
    target_type: str = "antigravity_project"
    custom_path: Optional[str] = None
    project_path: Optional[str] = None

class UninstallBatchRequest(BaseModel):
    agent_ids: List[str]
    target_type: str = "antigravity_project"
    custom_path: Optional[str] = None
    project_path: Optional[str] = None

class RuleInstallRequest(BaseModel):
    target_type: str = "antigravity_project"
    project_path: Optional[str] = None
    custom_content: Optional[str] = None

class RuleUninstallRequest(BaseModel):
    target_type: str = "antigravity_project"
    project_path: Optional[str] = None

@app.get("/api/browse-folder")
async def browse_folder():
    """呼叫原生資料夾選擇視窗"""
    # 優先使用 pywebview 原生視窗 API
    try:
        if webview.windows and len(webview.windows) > 0:
            win = webview.windows[0]
            res = win.create_file_dialog(webview.FOLDER_DIALOG, directory=str(Path.home()))
            if res and len(res) > 0:
                selected = os.path.normpath(res[0])
                return {"success": True, "path": selected}
            return {"success": False, "path": None, "message": "未選擇資料夾"}
    except Exception:
        pass

    # 備用方案：Tkinter 原生對話框
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        folder_selected = filedialog.askdirectory(title="請選擇專案資料夾")
        root.destroy()
        if folder_selected:
            return {"success": True, "path": os.path.normpath(folder_selected)}
        return {"success": False, "path": None, "message": "未選擇資料夾"}
    except Exception as e:
        return {"success": False, "message": f"開啟選擇視窗失敗: {str(e)}"}

@app.get("/api/divisions")
async def get_divisions():
    """獲取部門分類清單"""
    return {
        "success": True,
        "divisions": agent_manager.get_divisions(),
        "total_agents": len(agent_manager.agents)
    }

@app.get("/api/destinations")
async def get_destinations(project_path: Optional[str] = None):
    """獲取可用的 Subagent 安裝目標路徑"""
    return {
        "success": True,
        "destinations": installer.get_destinations(current_project_path=project_path)
    }

@app.get("/api/agents")
async def get_agents(
    query: str = "",
    division: str = "all",
    target_type: str = "antigravity_project",
    custom_path: Optional[str] = None,
    project_path: Optional[str] = None,
    filter_status: str = "all"
):
    """查詢與篩選專家清單"""
    installed_ids = installer.get_installed_agent_ids(
        target_type=target_type,
        custom_path=custom_path,
        project_path=project_path
    )
    agents = agent_manager.search_agents(
        query=query,
        division=division,
        installed_ids=installed_ids,
        filter_status=filter_status
    )
    
    result = []
    for a in agents:
        item = dict(a)
        item["is_installed"] = item["id"] in installed_ids
        item.pop("raw_markdown", None)
        item.pop("body_markdown", None)
        result.append(item)

    return {
        "success": True,
        "count": len(result),
        "total": len(agent_manager.agents),
        "installed_count": len(installed_ids),
        "agents": result
    }

@app.get("/api/agents/{agent_id}")
async def get_agent_detail(
    agent_id: str,
    target_type: str = "antigravity_project",
    custom_path: Optional[str] = None,
    project_path: Optional[str] = None
):
    """獲取單個專家完整資料 (含 Markdown)"""
    agent = agent_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="找不到指定的專家")
    
    installed_ids = installer.get_installed_agent_ids(
        target_type=target_type,
        custom_path=custom_path,
        project_path=project_path
    )
    item = dict(agent)
    item["is_installed"] = agent_id in installed_ids
    return {
        "success": True,
        "agent": item
    }

@app.post("/api/install")
async def install_agent_endpoint(req: InstallRequest):
    """安裝單個專家為 Subagent"""
    agent = agent_manager.get_agent(req.agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="找不到指定的專家")
    
    res = installer.install_agent(
        agent=agent,
        target_type=req.target_type,
        custom_path=req.custom_path,
        project_path=req.project_path
    )
    return res

@app.post("/api/install-batch")
async def install_batch_endpoint(req: InstallBatchRequest):
    """批次安裝多個專家為 Subagent"""
    agents_to_install = []
    for aid in req.agent_ids:
        agent = agent_manager.get_agent(aid)
        if agent:
            agents_to_install.append(agent)
    
    if not agents_to_install:
        raise HTTPException(status_code=400, detail="沒有選取任何有效的專家")

    res = installer.install_batch(
        agents=agents_to_install,
        target_type=req.target_type,
        custom_path=req.custom_path,
        project_path=req.project_path
    )
    return res

@app.post("/api/uninstall")
async def uninstall_agent_endpoint(req: UninstallRequest):
    """解除安裝單個 Subagent"""
    res = installer.uninstall_agent(
        agent_id=req.agent_id,
        target_type=req.target_type,
        custom_path=req.custom_path,
        project_path=req.project_path
    )
    return res

@app.post("/api/uninstall-batch")
async def uninstall_batch_endpoint(req: UninstallBatchRequest):
    """批次解除安裝多個 Subagent"""
    if not req.agent_ids:
        raise HTTPException(status_code=400, detail="沒有選取任何專家 ID")
    res = installer.uninstall_batch(
        agent_ids=req.agent_ids,
        target_type=req.target_type,
        custom_path=req.custom_path,
        project_path=req.project_path
    )
    return res

@app.post("/api/sync")
async def sync_github():
    """從 GitHub 官方倉庫同步最新專家"""
    res = agent_manager.sync_from_github()
    return res

# 協作工作流規範 (Rule) 相關 API
@app.get("/api/rule/status")
async def get_rule_status(
    target_type: str = "antigravity_project",
    project_path: Optional[str] = None
):
    """查詢目標專案之 Subagent 協作規範安裝狀態"""
    res = installer.check_rule_status(target_type=target_type, project_path=project_path)
    return res

@app.get("/api/rule/preview")
async def get_rule_preview(target_type: str = "antigravity_project"):
    """獲取 Subagent 協作規範標準模板內容"""
    content = installer.get_default_rule_content(target_type=target_type)
    return {
        "success": True,
        "content": content
    }

@app.post("/api/rule/install")
async def install_rule_endpoint(req: RuleInstallRequest):
    """一鍵安裝/更新 Subagent 協作規範 (Rule)"""
    res = installer.install_collaboration_rule(
        target_type=req.target_type,
        project_path=req.project_path,
        custom_content=req.custom_content
    )
    return res

@app.post("/api/rule/uninstall")
async def uninstall_rule_endpoint(req: RuleUninstallRequest):
    """解除安裝 Subagent 協作規範 (Rule)"""
    res = installer.uninstall_collaboration_rule(
        target_type=req.target_type,
        project_path=req.project_path
    )
    return res

# 掛載前端靜態檔案
static_dir = BASE_DIR / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/")
async def root():
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return JSONResponse({"message": "Agency Subagents API running."})

def find_available_port(start_port: int = 8000, max_attempts: int = 50) -> int:
    """自動尋找可用的 TCP 連接埠"""
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return port
            except OSError:
                continue
    return start_port

def run_fastapi_server(port: int):
    """在背景執行緒中運行 FastAPI / Uvicorn 服務 (相容 PyInstaller 無終端模式)"""
    config = uvicorn.Config(
        app=app,
        host="127.0.0.1",
        port=port,
        log_level="error",
        access_log=False,
        use_colors=False,
        log_config=None
    )
    server = uvicorn.Server(config)
    # 取消信號安裝，避免在非主執行緒拋出 ValueError
    server.install_signal_handlers = lambda: None
    server.run()

def wait_for_server(port: int, timeout: float = 6.0) -> bool:
    """確認本機連接埠已開始提供 HTTP 服務"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.2)
                if s.connect_ex(('127.0.0.1', port)) == 0:
                    return True
        except Exception:
            pass
        time.sleep(0.1)
    return False

def main():
    multiprocessing.freeze_support()
    
    port = find_available_port(8000)
    url = f"http://127.0.0.1:{port}"
    
    # 啟動伺服器後台執行緒
    server_thread = threading.Thread(target=run_fastapi_server, args=(port,), daemon=True)
    server_thread.start()
    
    # 等待伺服器確認啟動完成
    server_ready = wait_for_server(port, timeout=8.0)
    
    # 嘗試建立原生桌面應用程式獨立視窗，若環境不支援則開啟預設瀏覽器
    opened_window = False
    if server_ready:
        try:
            import webview
            window = webview.create_window(
                title="Agency Subagents - 繁體中文專家子代理管理器",
                url=url,
                width=1320,
                height=880,
                min_size=(960, 640),
                text_select=True,
                easy_drag=False
            )
            webview.start(debug=False)
            opened_window = True
        except Exception:
            opened_window = False
    
    if not opened_window:
        webbrowser.open(url)
        # 保持伺服器主程序活躍
        try:
            while True:
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            pass

if __name__ == "__main__":
    main()
