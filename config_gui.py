"""
Configuration GUI for MTGA Bot.

Provides a user-friendly interface for configuring bot settings.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys


class ConfigGUI:
    """GUI for configuring MTGA Bot settings."""
    
    def __init__(self, root):
        """Initialize the configuration GUI.
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("MTGA Bot Configuration")
        self.root.geometry("600x700")
        self.root.resizable(False, False)
        
        # Configuration values
        self.config_values = {}
        
        # Load existing config if available
        self.load_existing_config()
        
        # Create GUI elements
        self.create_widgets()
    
    def load_existing_config(self):
        """Load existing configuration from config.py if it exists."""
        try:
            if os.path.exists('config.py'):
                with open('config.py', 'r') as f:
                    content = f.read()
                    # Parse basic config values
                    for line in content.split('\n'):
                        if '=' in line and not line.strip().startswith('#'):
                            try:
                                key, value = line.split('=', 1)
                                key = key.strip()
                                value = value.strip().strip('"\'')
                                if value == 'None':
                                    value = ''
                                elif value in ('True', 'False'):
                                    value = value == 'True'
                                elif value.isdigit():
                                    value = int(value)
                                self.config_values[key] = value
                            except:
                                pass
        except Exception as e:
            print(f"Could not load existing config: {e}")
    
    def create_widgets(self):
        """Create all GUI widgets."""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        general_frame = ttk.Frame(notebook)
        game_frame = ttk.Frame(notebook)
        window_frame = ttk.Frame(notebook)
        advanced_frame = ttk.Frame(notebook)
        
        notebook.add(general_frame, text="General")
        notebook.add(game_frame, text="Game Settings")
        notebook.add(window_frame, text="Window")
        notebook.add(advanced_frame, text="Advanced")
        
        # Populate tabs
        self.create_general_tab(general_frame)
        self.create_game_tab(game_frame)
        self.create_window_tab(window_frame)
        self.create_advanced_tab(advanced_frame)
        
        # Create bottom buttons
        self.create_buttons()
    
    def create_general_tab(self, parent):
        """Create general settings tab."""
        frame = ttk.LabelFrame(parent, text="General Settings", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # MTGA Username
        ttk.Label(frame, text="MTGA Username:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.username_var = tk.StringVar(value=self.config_values.get('MTGA_USER_NAME', 'chriscas'))
        ttk.Entry(frame, textvariable=self.username_var, width=30).grid(row=0, column=1, pady=5)
        
        # Tesseract Path
        ttk.Label(frame, text="Tesseract Path:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.tesseract_var = tk.StringVar(value=self.config_values.get('TESSERACT_PATH', ''))
        path_entry = ttk.Entry(frame, textvariable=self.tesseract_var, width=30)
        path_entry.grid(row=1, column=1, pady=5)
        ttk.Button(frame, text="Browse", command=self.browse_tesseract).grid(row=1, column=2, padx=5)
        
        # Help text
        help_text = "Leave Tesseract path empty for auto-detection"
        ttk.Label(frame, text=help_text, font=('TkDefaultFont', 8), foreground='gray').grid(
            row=2, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        # Log Level
        ttk.Label(frame, text="Log Level:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.loglevel_var = tk.StringVar(value=self.config_values.get('LOG_LEVEL', 'INFO'))
        log_combo = ttk.Combobox(frame, textvariable=self.loglevel_var, 
                                 values=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                                 state='readonly', width=27)
        log_combo.grid(row=3, column=1, pady=5)
    
    def create_game_tab(self, parent):
        """Create game settings tab."""
        frame = ttk.LabelFrame(parent, text="Game Settings", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Attack Probability
        ttk.Label(frame, text="Attack Probability (%):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.attack_var = tk.IntVar(value=self.config_values.get('ATTACK_PROBABILITY', 100))
        attack_scale = ttk.Scale(frame, from_=0, to=100, variable=self.attack_var, orient=tk.HORIZONTAL)
        attack_scale.grid(row=0, column=1, sticky=tk.EW, pady=5)
        self.attack_label = ttk.Label(frame, text=f"{self.attack_var.get()}%")
        self.attack_label.grid(row=0, column=2, padx=5)
        attack_scale.configure(command=lambda v: self.attack_label.config(text=f"{int(float(v))}%"))
        
        # Max Card Cycles
        ttk.Label(frame, text="Max Card Cycles:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.cycles_var = tk.IntVar(value=self.config_values.get('MAX_CARD_CYCLES', 2))
        ttk.Spinbox(frame, from_=1, to=5, textvariable=self.cycles_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Clicks Disabled (Testing Mode)
        self.clicks_disabled_var = tk.BooleanVar(value=self.config_values.get('CLICKS_DISABLED', False))
        ttk.Checkbutton(frame, text="Disable Mouse Clicks (Testing Mode)", 
                       variable=self.clicks_disabled_var).grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=10)
        
        # Help text
        help_text = ("Attack Probability: Chance to attack with all creatures each turn\n"
                    "Max Card Cycles: How many times to try playing cards from hand\n"
                    "Testing Mode: Disables clicks for safe testing")
        ttk.Label(frame, text=help_text, font=('TkDefaultFont', 8), 
                 foreground='gray', justify=tk.LEFT).grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        frame.columnconfigure(1, weight=1)
    
    def create_window_tab(self, parent):
        """Create window settings tab."""
        frame = ttk.LabelFrame(parent, text="Window Settings", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Resolution
        ttk.Label(frame, text="Window Resolution:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        resolutions = [
            "1920x1080 (Full HD)",
            "1680x1050 (WSXGA+)",
            "1600x900 (HD+)",
            "1440x900 (WXGA+)",
            "1366x768 (HD)",
            "1280x1024 (SXGA)",
            "1280x800 (WXGA)",
            "1280x720 (HD)",
        ]
        
        # Determine current resolution
        window_loc = self.config_values.get('WINDOW_LOC_REZ', (0, 0, 1920, 1080))
        if isinstance(window_loc, str):
            # Parse string representation
            window_loc = eval(window_loc)
        current_res = f"{window_loc[2]}x{window_loc[3]}"
        default_selection = resolutions[0]
        for res in resolutions:
            if current_res in res:
                default_selection = res
                break
        
        self.resolution_var = tk.StringVar(value=default_selection)
        res_combo = ttk.Combobox(frame, textvariable=self.resolution_var, 
                                values=resolutions, state='readonly', width=30)
        res_combo.grid(row=0, column=1, pady=5)
        
        # Window Position
        ttk.Label(frame, text="Window Position:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Label(frame, text="Top-left corner (0, 0)").grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Help text
        help_text = ("The bot will automatically resize and position the MTGA window.\n"
                    "Recommended: 1920x1080 for best compatibility.\n"
                    "Other resolutions use coordinate scaling.")
        ttk.Label(frame, text=help_text, font=('TkDefaultFont', 8), 
                 foreground='gray', justify=tk.LEFT, wraplength=450).grid(
                     row=2, column=0, columnspan=2, sticky=tk.W, pady=10)
    
    def create_advanced_tab(self, parent):
        """Create advanced settings tab."""
        frame = ttk.LabelFrame(parent, text="Advanced Settings", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # OCR Settings
        ttk.Label(frame, text="OCR Settings", font=('TkDefaultFont', 10, 'bold')).grid(
            row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Enable preprocessing
        self.ocr_preprocess_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Enable OCR Preprocessing", 
                       variable=self.ocr_preprocess_var).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Enable adaptive threshold
        self.ocr_adaptive_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, text="Use Adaptive Thresholding", 
                       variable=self.ocr_adaptive_var).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Resolution Scaling
        ttk.Label(frame, text="Resolution Scaling", font=('TkDefaultFont', 10, 'bold')).grid(
            row=3, column=0, columnspan=2, sticky=tk.W, pady=(15, 10))
        
        self.auto_scale_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Auto-scale coordinates for different resolutions", 
                       variable=self.auto_scale_var).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Help text
        help_text = ("Advanced settings for experienced users.\n\n"
                    "OCR Preprocessing: Improves text recognition accuracy\n"
                    "Adaptive Thresholding: Better for varying lighting conditions\n"
                    "Auto-scaling: Automatically adjusts coordinates for your resolution")
        ttk.Label(frame, text=help_text, font=('TkDefaultFont', 8), 
                 foreground='gray', justify=tk.LEFT, wraplength=450).grid(
                     row=5, column=0, columnspan=2, sticky=tk.W, pady=15)
    
    def create_buttons(self):
        """Create bottom action buttons."""
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(button_frame, text="Save Configuration", 
                  command=self.save_config).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", 
                  command=self.root.quit).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Load Defaults", 
                  command=self.load_defaults).pack(side=tk.LEFT, padx=5)
    
    def browse_tesseract(self):
        """Open file dialog to browse for Tesseract executable."""
        filename = filedialog.askopenfilename(
            title="Select Tesseract Executable",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        if filename:
            self.tesseract_var.set(filename)
    
    def load_defaults(self):
        """Load default configuration values."""
        if messagebox.askyesno("Load Defaults", "This will reset all settings to defaults. Continue?"):
            self.username_var.set("chriscas")
            self.tesseract_var.set("")
            self.loglevel_var.set("INFO")
            self.attack_var.set(100)
            self.cycles_var.set(2)
            self.clicks_disabled_var.set(False)
            self.resolution_var.set("1920x1080 (Full HD)")
            self.ocr_preprocess_var.set(True)
            self.ocr_adaptive_var.set(False)
            self.auto_scale_var.set(True)
    
    def save_config(self):
        """Save configuration to config.py file."""
        try:
            # Parse resolution
            res_str = self.resolution_var.get().split()[0]  # Get "1920x1080" part
            width, height = map(int, res_str.split('x'))
            window_loc_rez = f"(0, 0, {width}, {height})"
            
            # Create config file content
            config_content = f'''"""
Configuration file for MTGA Bot.

Copy this file and customize the settings for your system.
"""

# ===== USER CONFIGURATION =====
# Your MTGA username (used for text recognition to determine if you're in a match)
MTGA_USER_NAME = "{self.username_var.get()}"

# Tesseract OCR path
# Set to None to auto-detect from common installation paths
# Or provide the full path to tesseract.exe
TESSERACT_PATH = {f'r"{self.tesseract_var.get()}"' if self.tesseract_var.get() else 'None'}

# ===== GAME SETTINGS =====
# Percentage chance that the bot will attack with all creatures (0-100)
ATTACK_PROBABILITY = {self.attack_var.get()}

# Maximum number of times the bot will cycle through cards attempting to play them
MAX_CARD_CYCLES = {self.cycles_var.get()}

# Disable mouse clicks for testing (True/False)
CLICKS_DISABLED = {self.clicks_disabled_var.get()}

# ===== WINDOW SETTINGS =====
# Expected resolution and location of game window (x1, y1, x2, y2)
WINDOW_LOC_REZ = {window_loc_rez}

# ===== LOGGING SETTINGS =====
# Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL
# Set to DEBUG for detailed output, INFO for normal operation
LOG_LEVEL = "{self.loglevel_var.get()}"

# ===== ADVANCED SETTINGS =====
# Enable OCR preprocessing for better accuracy
OCR_PREPROCESSING = {self.ocr_preprocess_var.get()}

# Use adaptive thresholding (better for varying lighting)
OCR_ADAPTIVE_THRESHOLD = {self.ocr_adaptive_var.get()}

# Auto-scale coordinates for different resolutions
AUTO_SCALE_COORDINATES = {self.auto_scale_var.get()}
'''
            
            # Write to file
            with open('config.py', 'w') as f:
                f.write(config_content)
            
            messagebox.showinfo("Success", "Configuration saved successfully!")
            self.root.quit()
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration:\n{str(e)}")
    
    def run(self):
        """Run the GUI main loop."""
        self.root.mainloop()


def main():
    """Main entry point for configuration GUI."""
    root = tk.Tk()
    app = ConfigGUI(root)
    app.run()


if __name__ == "__main__":
    main()

