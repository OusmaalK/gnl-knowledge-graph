#!/usr/bin/env python
"""
Lanceur unifié de la plateforme GNL Knowledge Graph
Version Windows - Corrigée
"""

import os
import sys
import subprocess
import threading
import time
import webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import socket
import shutil

class GNLLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GNL Knowledge Graph - Launcher")
        self.root.geometry("1000x750")
        self.root.resizable(True, True)

        self.processes = {}
        self.is_running = False
        self.root_dir = Path(__file__).parent
        self.backend_dir = self.root_dir / "backend"
        self.frontend_dir = self.root_dir / "frontend"

        self.setup_ui()
        self.check_services_status()

    def setup_ui(self):
        """Configure l'interface utilisateur"""
        style = ttk.Style()
        style.theme_use('clam')

        title = tk.Label(
            self.root,
            text="🚀 GNL Knowledge Graph Platform",
            font=("Arial", 20, "bold"),
            fg="#1a365d"
        )
        title.pack(pady=15)

        subtitle = tk.Label(
            self.root,
            text="Transport de Gaz Naturel Liquéfié - Intelligence Artificielle",
            font=("Arial", 11),
            fg="#4a5568"
        )
        subtitle.pack(pady=(0, 20))

        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # État des services
        services_frame = ttk.LabelFrame(main_frame, text="📊 État des Services", padding="10")
        services_frame.pack(fill=tk.X, pady=(0, 10))

        self.services_status = {}
        services = [
            ("Neo4j", "bolt://localhost:7687", "7474"),
            ("Qdrant", "http://localhost:6333", "6333"),
            ("Redis", "redis://localhost:6379", "6379"),
            ("Kafka", "localhost:9092", "9092"),
            ("Backend API", "http://localhost:8000", "8000"),
            ("Frontend", "http://localhost:3000", "3000")
        ]

        for name, url, port in services:
            frame = ttk.Frame(services_frame)
            frame.pack(fill=tk.X, pady=3)

            label = tk.Label(frame, text=f"• {name}:", width=16, anchor="w", font=("Arial", 10))
            label.pack(side=tk.LEFT)

            status_label = tk.Label(frame, text="🔴 Non disponible", fg="red", font=("Arial", 10))
            status_label.pack(side=tk.LEFT, padx=(10, 0))

            port_label = tk.Label(frame, text=f"Port: {port}", font=("Courier", 8), fg="#718096")
            port_label.pack(side=tk.RIGHT)

            self.services_status[name] = {
                'label': status_label,
                'url': url,
                'port': port,
                'status': False
            }

        # Contrôles
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=15)

        btn_frame = ttk.Frame(controls_frame)
        btn_frame.pack()

        self.start_btn = tk.Button(
            btn_frame,
            text="▶️ Démarrer la Plateforme",
            command=self.start_platform,
            bg="#48bb78",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=25,
            pady=12,
            width=25,
            cursor="hand2"
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = tk.Button(
            btn_frame,
            text="⏹️ Arrêter",
            command=self.stop_platform,
            bg="#fc8181",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=25,
            pady=12,
            width=15,
            state=tk.DISABLED,
            cursor="hand2"
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.open_btn = tk.Button(
            btn_frame,
            text="🌐 Ouvrir l'Interface",
            command=self.open_interface,
            bg="#4299e1",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=25,
            pady=12,
            width=20,
            state=tk.DISABLED,
            cursor="hand2"
        )
        self.open_btn.pack(side=tk.LEFT, padx=5)

        self.refresh_btn = tk.Button(
            btn_frame,
            text="🔄 Actualiser",
            command=self.check_services_status,
            bg="#e2e8f0",
            fg="#2d3748",
            font=("Arial", 10),
            padx=15,
            pady=12,
            width=12,
            cursor="hand2"
        )
        self.refresh_btn.pack(side=tk.LEFT, padx=5)

        # Logs
        logs_frame = ttk.LabelFrame(main_frame, text="📋 Logs", padding="10")
        logs_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.log_text = scrolledtext.ScrolledText(
            logs_frame,
            height=15,
            font=("Courier", 9),
            bg="#1a202c",
            fg="#68d391",
            insertbackground="white"
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        self.log_text.tag_config("INFO", foreground="#68d391")
        self.log_text.tag_config("WARNING", foreground="#f6ad55")
        self.log_text.tag_config("ERROR", foreground="#fc8181")
        self.log_text.tag_config("SUCCESS", foreground="#48bb78")

        self.progress = ttk.Progressbar(main_frame, mode='indeterminate', length=400)
        self.progress.pack(pady=10)

        self.status_bar = tk.Label(
            self.root,
            text="✅ Prêt - Cliquez sur 'Démarrer'",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=("Arial", 9),
            bg="#f7fafc"
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.log("✅ Launcher initialisé", "SUCCESS")

    def log(self, message, level="INFO"):
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] ", "INFO")
        self.log_text.insert(tk.END, f"{message}\n", level)
        self.log_text.see(tk.END)
        self.log_text.update_idletasks()
        self.status_bar.config(text=message[:100])

    def check_services_status(self):
        """Vérifie l'état des services"""
        self.log("🔄 Vérification des services...", "INFO")

        for name, info in self.services_status.items():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', int(info['port'])))
                sock.close()
                if result == 0:
                    info['status'] = True
                    info['label'].config(text="🟢 Disponible", fg="green")
                else:
                    info['status'] = False
                    info['label'].config(text="🔴 Indisponible", fg="red")
            except:
                info['status'] = False
                info['label'].config(text="🔴 Indisponible", fg="red")

        self.log("✅ Vérification terminée", "SUCCESS")

    def start_platform(self):
        if self.is_running:
            return

        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress.start(10)

        self.log("🚀 Démarrage de la plateforme...", "INFO")
        thread = threading.Thread(target=self._start_services)
        thread.daemon = True
        thread.start()

    def _start_services(self):
        try:
            # 1. Démarrer Docker Compose
            self.log("🐳 Démarrage des services Docker...", "INFO")
            docker_cmd = self._find_command("docker-compose", "docker")
            if docker_cmd:
                subprocess.Popen(
                    [docker_cmd, "up", "-d"],
                    cwd=self.root_dir,
                    creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
                )
                time.sleep(10)
                self.log("✅ Services Docker démarrés", "SUCCESS")
            else:
                self.log("⚠️ Docker non trouvé, vérifiez le PATH", "WARNING")

            # 2. Démarrer le backend
            self.log("🐍 Démarrage du backend...", "INFO")
            python_cmd = self._find_command("python", "python")
            if python_cmd:
                backend = subprocess.Popen(
                    [python_cmd, "-m", "uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"],
                    cwd=self.backend_dir,
                    creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                self.processes['backend'] = backend
                self.log("✅ Backend démarré", "SUCCESS")
            else:
                self.log("⚠️ Python non trouvé", "WARNING")

            time.sleep(5)

            # 3. Démarrer le frontend
            self.log("🌐 Démarrage du frontend...", "INFO")
            npm_cmd = self._find_command("npm", "npm")
            if npm_cmd and (self.frontend_dir / "node_modules").exists():
                frontend = subprocess.Popen(
                    [npm_cmd, "run", "dev"],
                    cwd=self.frontend_dir,
                    creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                self.processes['frontend'] = frontend
                self.log("✅ Frontend démarré", "SUCCESS")
            else:
                self.log("⚠️ npm non trouvé ou node_modules manquant", "WARNING")

            time.sleep(8)

            self.check_services_status()
            self.log("✅ PLATEFORME DÉMARRÉE", "SUCCESS")
            self.open_btn.config(state=tk.NORMAL)
            self.progress.stop()
            self.status_bar.config(text="✅ Plateforme opérationnelle - http://localhost:3000")
            self.open_interface()

        except Exception as e:
            self.log(f"❌ Erreur : {str(e)}", "ERROR")
            self.progress.stop()
            self.is_running = False
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            messagebox.showerror("Erreur", f"Erreur:\n\n{str(e)}")

    def _find_command(self, *names):
        """Trouve une commande dans le PATH"""
        for name in names:
            path = shutil.which(name)
            if path:
                return path
        return None

    def stop_platform(self):
        self.log("⏹️ Arrêt de la plateforme...", "INFO")

        for name, process in self.processes.items():
            try:
                process.terminate()
                process.wait(timeout=5)
                self.log(f"✅ {name} arrêté", "SUCCESS")
            except:
                try:
                    process.kill()
                except:
                    pass

        self.processes.clear()

        try:
            docker_cmd = self._find_command("docker-compose", "docker")
            if docker_cmd:
                subprocess.run([docker_cmd, "down"], cwd=self.root_dir, capture_output=True)
                self.log("✅ Services Docker arrêtés", "SUCCESS")
        except:
            pass

        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.open_btn.config(state=tk.DISABLED)
        self.progress.stop()

        for name, info in self.services_status.items():
            info['status'] = False
            info['label'].config(text="🔴 Non disponible", fg="red")

        self.log("✅ Plateforme arrêtée", "SUCCESS")
        self.status_bar.config(text="Plateforme arrêtée")

    def open_interface(self):
        webbrowser.open("http://localhost:3000")
        self.log("🌐 Interface ouverte", "SUCCESS")

    def on_close(self):
        if self.is_running and messagebox.askyesno("Confirmation", "Arrêter les services ?"):
            self.stop_platform()
        self.root.destroy()

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

if __name__ == "__main__":
    launcher = GNLLauncher()
    launcher.run()