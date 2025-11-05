import tkinter as tk
from tkinter import ttk
import serial.tools.list_ports  



#get USB ports in use
def get_ports():

    ports = serial.tools.list_ports.comports()
    # Return a list of the port device names (e.g., 'COM3' or '/dev/ttyUSB0')
    usb = []
    #filter ports 
    for port in ports:
        if port.vid is not None: # checks port vendor ID
            name = f"{port.device} | {port.description}"
            usb.append(name)
    return usb

# conexion
#def connect():

def main():
# /-------------- CONFIG ------------------------------------/
    # main application window
    root  = tk.Tk()
    root.title("Buck Bidireccional Control")
    root.geometry("800x600")
    root.style = ttk.Style(root)
    root.style.theme_use('clam')
    #colors
    root.BG_COLOR = "#2d3748"
    root.FRAME_COLOR = "#4a5568"
    root.TEXT_COLOR = "#e2e8f0"
    root.BUTTON_COLOR = "#4299e1"
    root.SUCCESS_COLOR = "#48bb78"
    root.DANGER_COLOR = "#f56565"
    #config root window
    root.configure(bg=root.BG_COLOR)

    #Style for frames and labels
    root.style.configure("TFrame", background=root.BG_COLOR)
    root.style.configure("TLabel", background=root.BG_COLOR, foreground=root.TEXT_COLOR, font=("Inter", 10))
    root.style.configure("TLabelFrame", background=root.BG_COLOR, foreground=root.TEXT_COLOR, relief="groove")
    root.style.configure("TLabelFrame.Label", background=root.BG_COLOR, foreground=root.TEXT_COLOR, font=("Inter", 12, "bold"))

    #style for buttons
    root.style.configure("TButton", font=("Inter", 10,"bold"), padding=5)
    root.style.map("TButton", foreground=[('active','black')], background=[('active', root.TEXT_COLOR)])
    
    # <-- 2. FIXED TYPOS HERE -->
    root.style.configure("Success.TButton", background=root.SUCCESS_COLOR, foreground="white")
    root.style.map("Success.TButton", background=[('active','#68d391')])                     

    root.style.configure("Danger.TButton", background=root.DANGER_COLOR, foreground="white")
    root.style.map("Danger.TButton", background=[('active', '#fc8181')])
        
    root.style.configure("Primary.TButton", background=root.BUTTON_COLOR, foreground="white")
    root.style.map("Primary.TButton", background=[('active', '#63b3ed')])
    
    #slider config
    root.style.configure("Horizontal.Tscale", background=root.BG_COLOR)
    # pre-conection 
    root.serial_connection = None 

# Slider update
    def duty_change(value_str):
        value = float(value_str)
        rounded_value = round(2*value)/2.0
        # sends value update
        duty_value_label.config(text=f"Duty: {rounded_value} %")
        draw_pwm_waveform(rounded_value)

    def up_duty():
        """Called by the Up button."""
        # --- FIX 2: Get value from var ---
        current_value = duty_var.get()
        new_value = min(current_value + 0.5, 100.0) # Cap at 100
        # --- FIX 3: Set the var. This will trigger duty_change() ---
        rounded = round(2*new_value)/2.0
        duty_var.set(rounded)
        duty_value_label.config(text=f"Duty: {rounded} %")
        draw_pwm_waveform(rounded)

    def down_duty():
        """Called by the Down button."""
        # --- FIX 2: Get value from var ---
        current_value = duty_var.get()
        new_value = max(current_value - 0.5, 0.0) # Floor at 0
        # --- FIX 3: Set the var. ---
        rounded = round(2*new_value)/2.0
        duty_var.set(rounded)
        duty_value_label.config(text=f"Duty: {rounded} %")
        draw_pwm_waveform(rounded)
# --------- widgets ---------------------------    
    # --- connection ---
    conn_frame = ttk.Frame(root, padding=(20,10))
    conn_frame.pack(fill = 'x', side='top')
    
    # Label fro the connection frame
    ttk.Label(conn_frame, text = "Connection Port: ", font=("Inter", 10, "bold")).pack(side='left',padx=(0, 5))
     
    # Get the list of ports
    available_ports = get_ports()
    
    root.com_port_var = tk.StringVar() # Create the variable
    
    root.com_port_combo = ttk.Combobox(
            conn_frame,
            textvariable=root.com_port_var,
            value=available_ports,  # Pass the list directly
            width=15,
            state='readonly' # Optional: prevents user from typing a port name
    )
    
    # Set a sensible default value
    if available_ports:
        root.com_port_var.set(available_ports[0]) # Set to the first available port
    else:
        root.com_port_var.set("No ports found")
        
    root.com_port_combo.pack(side='left', padx=5)
    
    #  refresh button 
    def refresh_ports():
        new_ports = get_ports()
        root.com_port_combo['value'] = new_ports
        if new_ports:
            root.com_port_var.set(new_ports[0])
        else:
            root.com_port_var.set("No ports found")
            
    refresh_button = ttk.Button(conn_frame, text="Refresh", command=refresh_ports, style="Primary.TButton")
    refresh_button.pack(side='left', padx=5)

# /--- Main Frame -------------------/
    #sets the main frame for widgets
    main_frame = ttk.Frame(root, padding = 20)
    main_frame.pack(fill='both', expand=True)

# --- Control Frame ----
    control_frame = ttk.Frame(main_frame)
    control_frame.pack(side='left', fill='y', padx=(0,10))
    
    # Mode 
    mode_card = ttk.LabelFrame(control_frame, text="Mode Control", padding=15)
    mode_card.pack(fill='x', pady=(0,20))
    
    #BUCK and BOOST modes
    def send_mode_buck():
        if root.serial_connection and root.serial_connection.is_open:
            print("COMMAND: Set mode to BUCK (ON)")
        else:
            print("Error: Not connected.")

    def send_mode_boost():
        if root.serial_connection and root.serial_connection.is_open:
            print("COMMAND: Set mode to BOOST (OFF)")
        else:
            print("Error: Not connected.")

    mode_buck = ttk.Button(
        mode_card,
        text = "BUCK",
        command = send_mode_buck,
        style = "Primary.TButton"
    )
    mode_boost = ttk.Button(
        mode_card,
        text = "BOOST",
        command = send_mode_boost,
    )
    mode_buck.pack(side='left', fill='x', expand=True, padx=(0,5))
    mode_boost.pack(side='left', fill='x', expand=True, padx=(5,0))
    
    # Duty silder
    duty_card = ttk.LabelFrame(control_frame, text="Duty (%)", padding=15)
    duty_card.pack(fill='x')

    duty_var = tk.DoubleVar(value=50)
    duty_slider = ttk.Scale(
        duty_card,
        from_= 0,
        to = 100,
        orient = 'horizontal',
        variable = duty_var,
        command = duty_change,
        length = 300
    )
    #buttons
    duty_buttons_frame = ttk.Frame(duty_card)
    duty_buttons_frame.pack(side='right', fill='x',pady=(5,20))
    #up step duty
    duty_button_up = ttk.Button(
        duty_buttons_frame,
        text="↑",
        command= up_duty,
        style = "Primary.TButton",
        width = 2
    )
    #down step duty
    duty_button_down = ttk.Button(
        duty_buttons_frame,
        text="↓",
        command= down_duty,
        style = "Primary.TButton",
        width = 2
    )

    duty_value_label = ttk.Label(
        duty_card,
        text="Current value: 50%",
        font=("Inter", 10, "bold")
    )
    duty_button_up.pack(side='top', fill='x',expand=True)
    duty_button_down.pack(side='top',fill='x', expand=True)
    duty_value_label.pack()
    duty_slider.pack(fill='y', pady=(5,10))

#/--------- Status Log -------------/
    log_frame = ttk.Frame(control_frame)
    log_frame.pack(side='bottom', fill='y',expand=True)

    log_card = ttk.LabelFrame(log_frame, text="Status Log", padding=10)
    log_card.pack(fill='both',expand=True)

    log_text = tk.Text(
        log_card,
        height=10, 
        width=50, 
        state='disabled',  # Start as read-only
        bg=root.FRAME_COLOR, 
        fg=root.TEXT_COLOR, 
        font=("Courier New", 20),
        wrap='word',
        bd=0,
        highlightthickness=0    
    )
    log_text.pack(fill='both', expand=True, pady=(0,0))

#/------- waveform --------------------/
    wave_frame = ttk.Frame(main_frame)
    wave_frame.pack(side='right',fill='both',expand=True)

    wave_label = ttk.LabelFrame(wave_frame, text="PWM Signal", padding=10)
    wave_label.pack(fill='both', expand=True)
    V_BUCK  = 23
    V_BOOST = 27
        # --- 1. THE CANVAS WIDGET ---
    # This creates the white drawing area
    canvas = tk.Canvas(
        wave_label,
        bg="#e0e0e0", # Set a white background
        highlightthickness=0
    )
    canvas.pack(fill='both', expand=True)
        # --- 2. THE DRAWING FUNCTION ---
    # This function draws the waveform on the canvas
    def draw_pwm_waveform(duty_cycle_percent):
        """Draws a PWM waveform on the canvas based on the duty cycle."""
        
        # Clear any old drawings
        canvas.delete("all")
        
        # Get the current size of the canvas (it's responsive)
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        
        # Set signal properties
        amplitude = height * 0.3  # Use 30% of the height
        y_high = (height / 2) - amplitude
        y_low = (height / 2) + amplitude
        
        # Calculate how wide the "high" part should be
        # (width - 20) gives 10px padding on each side
        on_width = (width - 20) * (duty_cycle_percent / 100.0)
        off_width = (width - 20) - on_width

        # Create the list of points for the line
        points = [
            (10, y_low),          # Start low
            (10, y_high),         # Rise
            (10 + on_width, y_high),  # Stay high
            (10 + on_width, y_low),   # Drop
            (10 + on_width + off_width, y_low) # Stay low
        ]
        # --- NEW: Draw Grid ---
        grid_color = "#000000" # A light gray
        
        # Draw 10 vertical grid lines (at 10%, 20%, ..., 90%)
        for i in range(1, 10):
            x = width * (i / 10.0)
            canvas.create_line(x, 0, x, height, fill=grid_color, dash=(2, 4))
            
        # Draw horizontal center line
        y_center = height / 2
        canvas.create_line(0, y_center, width, y_center, fill=grid_color, dash=(2, 4))
        # Draw the signal line
        canvas.create_line(
            points,
            width=3,            # Line thickness
            fill="#4299e1"      # Line color
        )
        # --- NEW: Draw horizontal lines for high/low ---
        canvas.create_line(0, y_high, width, y_high, fill=grid_color, dash=(4, 4))
        canvas.create_line(0, y_low, width, y_low, fill=grid_color, dash=(4, 4))
        
        # --- NEW: Add Voltage Text Labels ---
        canvas.create_text(
            width - 10, # 10px from right edge
            y_high,     # At the high line
            text=f"{V_BUCK:.1f}V", 
            anchor="e", # Anchor text to the right ("east")
            fill="#555" # Dark gray text
        )
        canvas.create_text(
            width - 10, 
            y_low, 
            text="0.0V", 
            anchor="e", 
            fill="#555"
        )
        
        # --- NEW: Calculate and show Average Voltage ---
        v_avg = V_BUCK * (duty_cycle_percent / 100.0)*0.96
        canvas.create_text(
            width - 10, # 10px from right edge
            15,         # 15px from top edge
            text=f"V_avg: {v_avg:.2f}V",
            anchor="ne", # Anchor text to the top-right ("north-east")
            font=("Inter", 12, "bold"),
            fill="#000"
        )

    def initial_draw():
        draw_pwm_waveform(50)
        
    root.after(500, initial_draw) # Wait 100ms then d

    root.mainloop()

if __name__ == "__main__":
    main()

