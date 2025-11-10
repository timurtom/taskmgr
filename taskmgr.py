#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GObject
import psutil
import os
import signal
import subprocess
import threading
import time

class WinXPTaskManager(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Task Manager")
        self.set_default_size(600, 400)
        self.set_resizable(True)
        self.set_icon_name("system-task-manager")
        
        # Windows XP style colors
        self.style_provider = Gtk.CssProvider()
        css = """
        .xp-header {
            background: linear-gradient(to bottom, #0a246a 0%, #a3c6f3 100%);
            color: white;
            padding: 4px;
            font-weight: bold;
        }
        
        .xp-tab {
            background: linear-gradient(to bottom, #f0f0f0 0%, #d4d0c8 100%);
            border: 1px solid #808080;
            padding: 4px 8px;
            font-size: 11px;
            color: black;
        }
        
        .xp-tab:checked {
            background: linear-gradient(to bottom, #ffffff 0%, #d4d0c8 100%);
        }
        
        .xp-button {
            background: linear-gradient(to bottom, #f0f0f0 0%, #d4d0c8 100%);
            border: 1px solid #808080;
            padding: 4px 12px;
            font-size: 11px;
            color: black;
        }
        
        .xp-button:hover {
            background: linear-gradient(to bottom, #ffffff 0%, #e8e8e8 100%);
        }
        
        .xp-button:active {
            background: linear-gradient(to bottom, #d4d0c8 0%, #f0f0f0 100%);
        }
        
        /* Only style the tab labels and buttons, not treeview text */
        GtkLabel.xp-tab {
            color: black;
        }
        
        GtkButton.xp-button {
            color: black;
        }
        """
        self.style_provider.load_from_data(css.encode())
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            self.style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        
        self.create_ui()
        self.update_interval = 2000  # ms
        self.start_updates()
        
    def create_ui(self):
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_box)
        
        # Menu bar (XP style)
        menu_bar = Gtk.MenuBar()
        file_menu = Gtk.Menu()
        file_item = Gtk.MenuItem(label="File")
        exit_item = Gtk.MenuItem(label="Exit")
        exit_item.connect("activate", self.on_exit_clicked)
        file_menu.append(exit_item)
        file_item.set_submenu(file_menu)
        menu_bar.append(file_item)
        
        options_menu = Gtk.Menu()
        options_item = Gtk.MenuItem(label="Options")
        refresh_item = Gtk.MenuItem(label="Refresh Now")
        refresh_item.connect("activate", self.refresh_all)
        options_menu.append(refresh_item)
        options_item.set_submenu(options_menu)
        menu_bar.append(options_item)
        
        main_box.pack_start(menu_bar, False, False, 0)
        
        # Notebook for tabs
        self.notebook = Gtk.Notebook()
        self.notebook.set_tab_pos(Gtk.PositionType.TOP)
        
        # Applications tab
        self.apps_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.apps_box.set_border_width(8)
        
        # Applications list
        apps_scrolled = Gtk.ScrolledWindow()
        apps_scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        self.apps_liststore = Gtk.ListStore(str, int, str, float)  # Name, PID, Status, CPU
        self.apps_treeview = Gtk.TreeView(model=self.apps_liststore)
        
        # Columns
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Application", renderer, text=0)
        self.apps_treeview.append_column(column)
        
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("PID", renderer, text=1)
        self.apps_treeview.append_column(column)
        
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Status", renderer, text=2)
        self.apps_treeview.append_column(column)
        
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("CPU %", renderer, text=3)
        self.apps_treeview.append_column(column)
        
        apps_scrolled.add(self.apps_treeview)
        self.apps_box.pack_start(apps_scrolled, True, True, 0)
        
        # Buttons for applications tab
        button_box = Gtk.Box(spacing=6)
        end_task_btn = Gtk.Button(label="End Task")
        end_task_btn.connect("clicked", self.on_end_task_clicked)
        end_task_btn.get_style_context().add_class('xp-button')
        
        switch_to_btn = Gtk.Button(label="Switch To")
        switch_to_btn.connect("clicked", self.on_switch_to_clicked)
        switch_to_btn.get_style_context().add_class('xp-button')
        
        new_task_btn = Gtk.Button(label="New Task")
        new_task_btn.connect("clicked", self.on_new_task_clicked)
        new_task_btn.get_style_context().add_class('xp-button')
        
        button_box.pack_start(end_task_btn, False, False, 0)
        button_box.pack_start(switch_to_btn, False, False, 0)
        button_box.pack_start(new_task_btn, False, False, 0)
        
        self.apps_box.pack_start(button_box, False, False, 0)
        
        # Processes tab
        self.processes_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.processes_box.set_border_width(8)
        
        processes_scrolled = Gtk.ScrolledWindow()
        processes_scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        self.processes_liststore = Gtk.ListStore(str, int, str, float, float, str)  # Name, PID, User, CPU, Memory, Status
        self.processes_treeview = Gtk.TreeView(model=self.processes_liststore)
        
        # Columns for processes
        columns = ["Process Name", "PID", "User", "CPU %", "Memory %", "Status"]
        for i, col_name in enumerate(columns):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(col_name, renderer, text=i)
            self.processes_treeview.append_column(column)
        
        processes_scrolled.add(self.processes_treeview)
        self.processes_box.pack_start(processes_scrolled, True, True, 0)
        
        # Buttons for processes tab
        process_button_box = Gtk.Box(spacing=6)
        end_process_btn = Gtk.Button(label="End Process")
        end_process_btn.connect("clicked", self.on_end_process_clicked)
        end_process_btn.get_style_context().add_class('xp-button')
        
        process_button_box.pack_start(end_process_btn, False, False, 0)
        self.processes_box.pack_start(process_button_box, False, False, 0)
        
        # Performance tab
        self.performance_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.performance_box.set_border_width(8)
        
        # CPU usage
        cpu_label = Gtk.Label(label="CPU Usage")
        cpu_label.set_xalign(0)
        self.performance_box.pack_start(cpu_label, False, False, 0)
        
        self.cpu_progress = Gtk.ProgressBar()
        self.performance_box.pack_start(self.cpu_progress, False, False, 0)
        
        # Memory usage
        mem_label = Gtk.Label(label="Physical Memory")
        mem_label.set_xalign(0)
        self.performance_box.pack_start(mem_label, False, False, 0)
        
        self.mem_progress = Gtk.ProgressBar()
        self.performance_box.pack_start(self.mem_progress, False, False, 0)
        
        # Stats
        self.stats_label = Gtk.Label(label="")
        self.stats_label.set_xalign(0)
        self.performance_box.pack_start(self.stats_label, False, False, 0)
        
        # Add tabs to notebook
        apps_label = Gtk.Label(label="Applications")
        processes_label = Gtk.Label(label="Processes") 
        performance_label = Gtk.Label(label="Performance")
        
        # Apply styles to tab labels
        for label in [apps_label, processes_label, performance_label]:
            label.get_style_context().add_class('xp-tab')
        
        self.notebook.append_page(self.apps_box, apps_label)
        self.notebook.append_page(self.processes_box, processes_label)
        self.notebook.append_page(self.performance_box, performance_label)
        
        main_box.pack_start(self.notebook, True, True, 0)
        
        # Status bar
        self.status_bar = Gtk.Statusbar()
        self.status_bar.push(0, "Ready")
        main_box.pack_start(self.status_bar, False, False, 0)
    
    def start_updates(self):
        self.update_processes()
        GLib.timeout_add(self.update_interval, self.update_processes)
        GLib.timeout_add(1000, self.update_performance)
    
    def update_processes(self):
        # Clear existing data
        self.apps_liststore.clear()
        self.processes_liststore.clear()
        
        # Get all processes
        for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_percent', 'username']):
            try:
                cpu_percent = proc.info['cpu_percent']
                if cpu_percent is None:
                    cpu_percent = 0.0
                
                memory_percent = proc.info['memory_percent'] 
                if memory_percent is None:
                    memory_percent = 0.0
                
                # Add to processes list
                self.processes_liststore.append([
                    proc.info['name'] or 'Unknown',
                    proc.info['pid'],
                    proc.info['username'] or 'N/A',
                    round(cpu_percent, 1),
                    round(memory_percent, 1),
                    proc.info['status'] or 'unknown'
                ])
                
                # Add GUI applications to apps list (filter for common GUI apps)
                if proc.info['name'] and any(x in proc.info['name'].lower() for x in 
                    ['firefox', 'chrome', 'gedit', 'nautilus', 'thunar', 'code', 'atom', 'sublime', 'gnome-terminal']):
                    self.apps_liststore.append([
                        proc.info['name'],
                        proc.info['pid'],
                        proc.info['status'] or 'unknown',
                        round(cpu_percent, 1)
                    ])
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        self.status_bar.push(0, f"Processes: {len(self.processes_liststore)}")
        return True
    
    def update_performance(self):
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=None)
        self.cpu_progress.set_fraction(cpu_percent / 100)
        self.cpu_progress.set_text(f"{cpu_percent:.1f}%")
        
        # Memory usage
        memory = psutil.virtual_memory()
        mem_percent = memory.percent
        self.mem_progress.set_fraction(mem_percent / 100)
        self.mem_progress.set_text(f"{mem_percent:.1f}%")
        
        # Stats
        stats_text = f"Processes: {len(psutil.pids())}  |  " \
                    f"CPU Usage: {cpu_percent:.1f}%  |  " \
                    f"Physical Memory: {memory.used//1024//1024}MB / {memory.total//1024//1024}MB"
        self.stats_label.set_text(stats_text)
        
        return True
    
    def get_selected_pid(self, treeview):
        """Get the selected PID from a treeview"""
        selection = treeview.get_selection()
        model, treeiter = selection.get_selected()
        if treeiter:
            return model[treeiter][1]  # PID is in the second column
        return None
    
    def on_end_task_clicked(self, widget):
        pid = self.get_selected_pid(self.apps_treeview)
        if pid:
            self.terminate_process(pid)
        else:
            self.status_bar.push(0, "No application selected")
    
    def on_end_process_clicked(self, widget):
        pid = self.get_selected_pid(self.processes_treeview)
        if pid:
            self.terminate_process(pid)
        else:
            self.status_bar.push(0, "No process selected")
    
    def terminate_process(self, pid):
        try:
            process = psutil.Process(pid)
            process_name = process.name()
            
            # Try terminate first (graceful)
            process.terminate()
            
            # Wait a bit and check if it's still alive
            try:
                process.wait(timeout=3)
                self.status_bar.push(0, f"Process '{process_name}' (PID: {pid}) terminated")
            except psutil.TimeoutExpired:
                # If still alive, force kill
                process.kill()
                self.status_bar.push(0, f"Process '{process_name}' (PID: {pid}) killed")
                
        except psutil.NoSuchProcess:
            self.status_bar.push(0, f"Process {pid} not found (already terminated)")
        except psutil.AccessDenied:
            self.status_bar.push(0, f"Permission denied to terminate process {pid}")
        except Exception as e:
            self.status_bar.push(0, f"Error terminating process {pid}: {str(e)}")
    
    def on_switch_to_clicked(self, widget):
        # Basic implementation - just show a message
        pid = self.get_selected_pid(self.apps_treeview)
        if pid:
            self.status_bar.push(0, f"Switch To: Process {pid} (Not fully implemented)")
        else:
            self.status_bar.push(0, "No application selected to switch to")
    
    def on_new_task_clicked(self, widget):
        dialog = Gtk.Dialog(title="Create New Task", parent=self, flags=0)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                         Gtk.STOCK_OK, Gtk.ResponseType.OK)
        dialog.set_default_size(400, 120)
        
        box = dialog.get_content_area()
        box.set_spacing(8)
        
        label = Gtk.Label(label="Type the name of a program, folder, document, or Internet resource, and Windows will open it for you.")
        label.set_line_wrap(True)
        box.pack_start(label, False, False, 0)
        
        entry = Gtk.Entry()
        entry.set_placeholder_text("Enter program, folder, document, or Internet resource")
        box.pack_start(entry, False, False, 0)
        
        dialog.show_all()
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            command = entry.get_text().strip()
            if command:
                try:
                    # Use shell=True to handle commands with spaces/paths
                    subprocess.Popen(command, shell=True)
                    self.status_bar.push(0, f"Started: {command}")
                except Exception as e:
                    self.status_bar.push(0, f"Error starting '{command}': {str(e)}")
            else:
                self.status_bar.push(0, "No command entered")
        
        dialog.destroy()
    
    def refresh_all(self, widget=None):
        self.update_processes()
        self.update_performance()
        self.status_bar.push(0, "Refreshed")
    
    def on_exit_clicked(self, widget):
        Gtk.main_quit()

def main():
    app = WinXPTaskManager()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
