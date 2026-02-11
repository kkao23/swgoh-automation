"""
Graphical User Interface for SWGOH Automation Bot
Provides user-friendly interface for controlling and monitoring automation
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import time
from typing import Optional
import json
from main import SWGOHAutomator, GameConfig
from config import config_manager, AutomationConfig, TeamConfig
from modules.energy_manager import EnergyManager
from modules.battle_automation import BattleAutomation
from modules.collection_manager import CollectionManager
from modules.ai_decision_engine import AIDecisionEngine
from utils.logger import swgoh_logger

class SWGOHGUI:
    """Main GUI application for SWGOH automation"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SWGOH Automation Bot")
        self.root.geometry("900x700")
        
        # Automation components
        self.automator: Optional[SWGOHAutomator] = None
        self.energy_manager: Optional[EnergyManager] = None
        self.battle_automation: Optional[BattleAutomation] = None
        self.collection_manager: Optional[CollectionManager] = None
        self.ai_engine: Optional[AIDecisionEngine] = None
        
        # Control variables
        self.is_running = False
        self.current_thread = None
        
        # Setup GUI
        self.setup_gui()
        self.load_config()
        
    def setup_gui(self):
        """Setup the GUI layout"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create tabs
        self.create_main_tab()
        self.create_energy_tab()
        self.create_battle_tab()
        self.create_collection_tab()
        self.create_ai_tab()
        self.create_config_tab()
        self.create_logs_tab()
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def create_main_tab(self):
        """Create main control tab"""
        main_frame = ttk.Frame(self.notebook)
        self.notebook.add(main_frame, text="Main")
        
        # Connection section
        conn_frame = ttk.LabelFrame(main_frame, text="Connection", padding=10)
        conn_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(conn_frame, text="Initialize Bot", command=self.initialize_bot).pack(side='left', padx=5)
        ttk.Button(conn_frame, text="Test Connection", command=self.test_connection).pack(side='left', padx=5)
        
        # Quick actions
        actions_frame = ttk.LabelFrame(main_frame, text="Quick Actions", padding=10)
        actions_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(actions_frame, text="Complete Dailies", command=self.complete_dailies).pack(side='left', padx=5)
        ttk.Button(actions_frame, text="Auto Farm", command=self.auto_farm).pack(side='left', padx=5)
        ttk.Button(actions_frame, text="AI Automation", command=self.start_ai_automation).pack(side='left', padx=5)
        
        # Status display
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding=10)
        status_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.status_text = scrolledtext.ScrolledText(status_frame, height=10, width=80)
        self.status_text.pack(fill='both', expand=True)
        
    def create_energy_tab(self):
        """Create energy management tab"""
        energy_frame = ttk.Frame(self.notebook)
        self.notebook.add(energy_frame, text="Energy")
        
        # Energy display
        display_frame = ttk.LabelFrame(energy_frame, text="Current Energy", padding=10)
        display_frame.pack(fill='x', padx=5, pady=5)
        
        self.energy_labels = {}
        energy_types = ['cantina', 'regular', 'fleet']
        for i, energy_type in enumerate(energy_types):
            ttk.Label(display_frame, text=f"{energy_type.title()}:").grid(row=0, column=i*2, padx=5, sticky='w')
            self.energy_labels[energy_type] = ttk.Label(display_frame, text="0/0")
            self.energy_labels[energy_type].grid(row=0, column=i*2+1, padx=5, sticky='w')
            
        ttk.Button(display_frame, text="Refresh", command=self.refresh_energy).grid(row=1, column=0, columnspan=6, pady=10)
        
        # Energy controls
        control_frame = ttk.LabelFrame(energy_frame, text="Energy Controls", padding=10)
        control_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(control_frame, text="Refill Cantina", command=lambda: self.refill_energy('cantina')).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Refill Regular", command=lambda: self.refill_energy('regular')).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Refill Fleet", command=lambda: self.refill_energy('fleet')).pack(side='left', padx=5)
        
        # Auto refill settings
        auto_frame = ttk.LabelFrame(energy_frame, text="Auto Refill Settings", padding=10)
        auto_frame.pack(fill='x', padx=5, pady=5)
        
        self.auto_refill_var = tk.BooleanVar()
        ttk.Checkbutton(auto_frame, text="Enable Auto Refill", variable=self.auto_refill_var).pack(anchor='w')
        
        ttk.Label(auto_frame, text="Refill Threshold:").pack(anchor='w')
        self.refill_threshold_var = tk.DoubleVar(value=0.2)
        ttk.Scale(auto_frame, from_=0.1, to=0.5, variable=self.refill_threshold_var, orient='horizontal').pack(fill='x')
        
    def create_battle_tab(self):
        """Create battle automation tab"""
        battle_frame = ttk.Frame(self.notebook)
        self.notebook.add(battle_frame, text="Battles")
        
        # Battle setup
        setup_frame = ttk.LabelFrame(battle_frame, text="Battle Setup", padding=10)
        setup_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(setup_frame, text="Mode:").grid(row=0, column=0, sticky='w')
        self.battle_mode_var = tk.StringVar(value="regular")
        mode_combo = ttk.Combobox(setup_frame, textvariable=self.battle_mode_var, values=["regular", "cantina", "fleet"])
        mode_combo.grid(row=0, column=1, padx=5)
        
        ttk.Label(setup_frame, text="Stage:").grid(row=1, column=0, sticky='w')
        self.battle_stage_var = tk.StringVar(value="1-A")
        ttk.Entry(setup_frame, textvariable=self.battle_stage_var).grid(row=1, column=1, padx=5)
        
        ttk.Label(setup_frame, text="Team:").grid(row=2, column=0, sticky='w')
        self.battle_team_var = tk.StringVar(value="regular")
        ttk.Entry(setup_frame, textvariable=self.battle_team_var).grid(row=2, column=1, padx=5)
        
        ttk.Label(setup_frame, text="Repetitions:").grid(row=3, column=0, sticky='w')
        self.battle_reps_var = tk.IntVar(value=3)
        ttk.Spinbox(setup_frame, from_=1, to=10, textvariable=self.battle_reps_var).grid(row=3, column=1, padx=5)
        
        # Battle controls
        control_frame = ttk.LabelFrame(battle_frame, text="Battle Controls", padding=10)
        control_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(control_frame, text="Start Battle", command=self.start_battle).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Auto Farm Stage", command=self.auto_farm_stage).pack(side='left', padx=5)
        
        # Battle results
        results_frame = ttk.LabelFrame(battle_frame, text="Battle Results", padding=10)
        results_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.battle_results_text = scrolledtext.ScrolledText(results_frame, height=15, width=80)
        self.battle_results_text.pack(fill='both', expand=True)
        
    def create_collection_tab(self):
        """Create collection management tab"""
        collection_frame = ttk.Frame(self.notebook)
        self.notebook.add(collection_frame, text="Collection")
        
        # Daily activities
        daily_frame = ttk.LabelFrame(collection_frame, text="Daily Activities", padding=10)
        daily_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(daily_frame, text="Complete All Dailies", command=self.complete_dailies).pack(side='left', padx=5)
        ttk.Button(daily_frame, text="Check Login Rewards", command=self.check_login_rewards).pack(side='left', padx=5)
        ttk.Button(daily_frame, text="Guild Activities", command=self.guild_activities).pack(side='left', padx=5)
        
        # Collection analysis
        analysis_frame = ttk.LabelFrame(collection_frame, text="Collection Analysis", padding=10)
        analysis_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(analysis_frame, text="Analyze Collection", command=self.analyze_collection).pack(side='left', padx=5)
        ttk.Button(analysis_frame, text="Export Collection Data", command=self.export_collection).pack(side='left', padx=5)
        
        # Collection display
        display_frame = ttk.LabelFrame(collection_frame, text="Collection Status", padding=10)
        display_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.collection_text = scrolledtext.ScrolledText(display_frame, height=15, width=80)
        self.collection_text.pack(fill='both', expand=True)
        
    def create_ai_tab(self):
        """Create AI decision engine tab"""
        ai_frame = ttk.Frame(self.notebook)
        self.notebook.add(ai_frame, text="AI Engine")
        
        # AI controls
        control_frame = ttk.LabelFrame(ai_frame, text="AI Controls", padding=10)
        control_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(control_frame, text="Analyze Game State", command=self.analyze_game_state).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Get AI Recommendations", command=self.get_ai_recommendations).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Start AI Automation", command=self.start_ai_automation).pack(side='left', padx=5)
        
        # AI settings
        settings_frame = ttk.LabelFrame(ai_frame, text="AI Settings", padding=10)
        settings_frame.pack(fill='x', padx=5, pady=5)
        
        self.ai_enabled_var = tk.BooleanVar()
        ttk.Checkbutton(settings_frame, text="Enable AI", variable=self.ai_enabled_var).pack(anchor='w')
        
        ttk.Label(settings_frame, text="Decision Threshold:").pack(anchor='w')
        self.ai_threshold_var = tk.DoubleVar(value=0.7)
        ttk.Scale(settings_frame, from_=0.5, to=0.9, variable=self.ai_threshold_var, orient='horizontal').pack(fill='x')
        
        # AI display
        display_frame = ttk.LabelFrame(ai_frame, text="AI Analysis", padding=10)
        display_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.ai_text = scrolledtext.ScrolledText(display_frame, height=15, width=80)
        self.ai_text.pack(fill='both', expand=True)
        
    def create_config_tab(self):
        """Create configuration tab"""
        config_frame = ttk.Frame(self.notebook)
        self.notebook.add(config_frame, text="Config")
        
        # Configuration display
        display_frame = ttk.LabelFrame(config_frame, text="Current Configuration", padding=10)
        display_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.config_text = scrolledtext.ScrolledText(display_frame, height=20, width=80)
        self.config_text.pack(fill='both', expand=True)
        
        # Config controls
        control_frame = ttk.LabelFrame(config_frame, text="Configuration Controls", padding=10)
        control_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(control_frame, text="Load Config", command=self.load_config).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Save Config", command=self.save_config).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Reset to Defaults", command=self.reset_config).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Import Config", command=self.import_config).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Export Config", command=self.export_config).pack(side='left', padx=5)
        
    def create_logs_tab(self):
        """Create logs tab"""
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text="Logs")
        
        # Log display
        self.logs_text = scrolledtext.ScrolledText(logs_frame, height=25, width=100)
        self.logs_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Log controls
        control_frame = ttk.Frame(logs_frame)
        control_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(control_frame, text="Refresh Logs", command=self.refresh_logs).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Clear Logs", command=self.clear_logs).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Export Logs", command=self.export_logs).pack(side='left', padx=5)
        
    # GUI Action Methods
    def initialize_bot(self):
        """Initialize the automation bot"""
        try:
            config = config_manager.get_automation_config()
            self.automator = SWGOHAutomator(GameConfig(
                screenshot_delay=config.screenshot_delay,
                click_delay=config.click_delay,
                confidence_threshold=config.confidence_threshold,
                debug_mode=config.debug_mode
            ))
            
            # Initialize modules
            self.energy_manager = EnergyManager(self.automator)
            self.battle_automation = BattleAutomation(self.automator)
            self.collection_manager = CollectionManager(self.automator)
            self.ai_engine = AIDecisionEngine(self.automator)
            
            self.update_status("Bot initialized successfully")
            self.log_message("Bot initialized successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize bot: {e}")
            self.log_message(f"Initialization failed: {e}")
            
    def test_connection(self):
        """Test connection to game"""
        if not self.automator:
            messagebox.showwarning("Warning", "Please initialize the bot first")
            return
            
        try:
            # Test by taking a screenshot
            screenshot = self.automator.capture_screen()
            self.update_status("Connection test successful")
            self.log_message("Connection test successful")
        except Exception as e:
            messagebox.showerror("Error", f"Connection test failed: {e}")
            self.log_message(f"Connection test failed: {e}")
            
    def complete_dailies(self):
        """Complete daily activities"""
        if not self.collection_manager:
            messagebox.showwarning("Warning", "Please initialize the bot first")
            return
            
        def run_dailies():
            try:
                results = self.collection_manager.auto_complete_dailies()
                self.log_message(f"Daily activities completed: {results}")
                self.update_status("Dailies completed")
            except Exception as e:
                self.log_message(f"Daily activities failed: {e}")
                
        threading.Thread(target=run_dailies, daemon=True).start()
        
    def start_ai_automation(self):
        """Start AI-driven automation"""
        if not self.ai_engine:
            messagebox.showwarning("Warning", "Please initialize the bot first")
            return
            
        if self.is_running:
            messagebox.showwarning("Warning", "Automation is already running")
            return
            
        def run_ai_automation():
            try:
                self.is_running = True
                self.update_status("AI automation running...")
                
                results = self.ai_engine.run_ai_automation(
                    max_actions=10,
                    time_limit=1800  # 30 minutes
                )
                
                self.log_message(f"AI automation completed: {results}")
                self.update_status("AI automation completed")
                
            except Exception as e:
                self.log_message(f"AI automation failed: {e}")
            finally:
                self.is_running = False
                
        threading.Thread(target=run_ai_automation, daemon=True).start()
        
    # Helper methods
    def update_status(self, message: str):
        """Update status bar"""
        self.status_var.set(message)
        self.root.update_idletasks()
        
    def log_message(self, message: str):
        """Add message to log display"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.status_text.insert(tk.END, log_entry)
        self.status_text.see(tk.END)
        
    def load_config(self):
        """Load configuration into display"""
        config_summary = config_manager.get_config_summary()
        self.config_text.delete(1.0, tk.END)
        self.config_text.insert(1.0, config_summary)
        
    def save_config(self):
        """Save current configuration"""
        config_manager.save_config()
        messagebox.showinfo("Success", "Configuration saved")
        
    def reset_config(self):
        """Reset configuration to defaults"""
        if messagebox.askyesno("Confirm", "Reset configuration to defaults?"):
            config_manager.reset_to_defaults()
            self.load_config()
            messagebox.showinfo("Success", "Configuration reset to defaults")
            
    def import_config(self):
        """Import configuration from file"""
        filename = filedialog.askopenfilename(
            title="Import Configuration",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r') as f:
                    config_data = json.load(f)
                # Apply configuration (implementation needed)
                messagebox.showinfo("Success", "Configuration imported")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import configuration: {e}")
                
    def export_config(self):
        """Export configuration to file"""
        filename = filedialog.asksaveasfilename(
            title="Export Configuration",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                config_data = {
                    'automation': config_manager.automation_config.__dict__,
                    'user_preferences': config_manager.user_preferences.__dict__
                }
                with open(filename, 'w') as f:
                    json.dump(config_data, f, indent=2)
                messagebox.showinfo("Success", "Configuration exported")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export configuration: {e}")
                
    def refresh_logs(self):
        """Refresh log display"""
        try:
            with open('logs/swgoh_bot.log', 'r') as f:
                logs = f.read()
                self.logs_text.delete(1.0, tk.END)
                self.logs_text.insert(1.0, logs)
        except FileNotFoundError:
            self.logs_text.delete(1.0, tk.END)
            self.logs_text.insert(1.0, "No log file found")
            
    def clear_logs(self):
        """Clear log display"""
        self.logs_text.delete(1.0, tk.END)
        
    def export_logs(self):
        """Export logs to file"""
        filename = filedialog.asksaveasfilename(
            title="Export Logs",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.logs_text.get(1.0, tk.END))
                messagebox.showinfo("Success", "Logs exported")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export logs: {e}")
                
    # Placeholder methods for other functions
    def refresh_energy(self):
        """Refresh energy display"""
        if self.energy_manager:
            # Implementation needed
            pass
            
    def refill_energy(self, energy_type: str):
        """Refill specified energy type"""
        if self.energy_manager:
            # Implementation needed
            pass
            
    def start_battle(self):
        """Start configured battle"""
        if self.battle_automation:
            # Implementation needed
            pass
            
    def auto_farm_stage(self):
        """Auto farm configured stage"""
        if self.battle_automation:
            # Implementation needed
            pass
            
    def auto_farm(self):
        """Start auto farming"""
        # Implementation needed
        pass
        
    def check_login_rewards(self):
        """Check login rewards"""
        if self.collection_manager:
            # Implementation needed
            pass
            
    def guild_activities(self):
        """Complete guild activities"""
        if self.collection_manager:
            # Implementation needed
            pass
            
    def analyze_collection(self):
        """Analyze character collection"""
        if self.collection_manager:
            # Implementation needed
            pass
            
    def export_collection(self):
        """Export collection data"""
        if self.collection_manager:
            # Implementation needed
            pass
            
    def analyze_game_state(self):
        """Analyze current game state"""
        if self.ai_engine:
            # Implementation needed
            pass
            
    def get_ai_recommendations(self):
        """Get AI recommendations"""
        if self.ai_engine:
            # Implementation needed
            pass
            
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = SWGOHGUI()
    app.run()
