"""
Logs service for handling frontend logs
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

class LogsService:
    def __init__(self):
        self.logs_dir = Path("/workspace/logs")
        self.logs_dir.mkdir(exist_ok=True)
        self.frontend_logs_file = self.logs_dir / "frontend.log"
        self.session_logs_file = self.logs_dir / "frontend_sessions.log"
    
    def clear_logs(self, session_id: str = None):
        """Clear logs for a specific session or all logs"""
        try:
            if session_id:
                # Clear logs for specific session
                self._clear_session_logs(session_id)
            else:
                # Clear all logs
                if self.frontend_logs_file.exists():
                    self.frontend_logs_file.unlink()
                if self.session_logs_file.exists():
                    self.session_logs_file.unlink()
            
            return {"status": "success", "message": "Logs cleared"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def save_logs(self, logs: List[Dict[str, Any]], session_id: str = None):
        """Save logs to file"""
        try:
            timestamp = datetime.now().isoformat()
            
            # Format logs for file output
            formatted_logs = []
            for log in logs:
                formatted_log = {
                    "timestamp": log.get("timestamp", timestamp),
                    "session_id": session_id or log.get("sessionId", "unknown"),
                    "level": log.get("level", "info"),
                    "component": log.get("component", "unknown"),
                    "message": log.get("message", ""),
                    "data": log.get("data")
                }
                formatted_logs.append(formatted_log)
            
            # Write to main log file
            with open(self.frontend_logs_file, "a", encoding="utf-8") as f:
                for log in formatted_logs:
                    f.write(f"[{log['timestamp']}] [{log['session_id']}] [{log['level'].upper()}] [{log['component']}] {log['message']}\n")
                    if log['data']:
                        f.write(f"  Data: {json.dumps(log['data'], indent=2)}\n")
                    f.write("\n")
            
            # Write to session-specific log file
            if session_id:
                session_file = self.logs_dir / f"session_{session_id}.log"
                with open(session_file, "a", encoding="utf-8") as f:
                    for log in formatted_logs:
                        f.write(f"[{log['timestamp']}] [{log['level'].upper()}] [{log['component']}] {log['message']}\n")
                        if log['data']:
                            f.write(f"  Data: {json.dumps(log['data'], indent=2)}\n")
                        f.write("\n")
            
            return {"status": "success", "message": f"Saved {len(logs)} logs"}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_logs(self, session_id: str = None, limit: int = 100):
        """Get logs from file"""
        try:
            logs = []
            log_file = self.session_logs_file if session_id else self.frontend_logs_file
            
            if not log_file.exists():
                return {"status": "success", "logs": []}
            
            with open(log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            # Parse logs (simple implementation)
            current_log = {}
            for line in lines[-limit*10:]:  # Read more lines to account for multi-line logs
                line = line.strip()
                if line.startswith("[") and "]" in line:
                    if current_log:
                        logs.append(current_log)
                    current_log = {"raw": line}
                elif line and current_log:
                    current_log["raw"] += "\n" + line
            
            if current_log:
                logs.append(current_log)
            
            return {"status": "success", "logs": logs[-limit:]}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _clear_session_logs(self, session_id: str):
        """Clear logs for a specific session"""
        session_file = self.logs_dir / f"session_{session_id}.log"
        if session_file.exists():
            session_file.unlink()

# Global instance
logs_service = LogsService()