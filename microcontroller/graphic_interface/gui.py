import tkinter as tk
from tkinter import ttk
import serial.tools.list_ports  
import time


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

# ------------------ WARNING POPOUP ------------------------------
# /--- Custom Warning Popup Function ---/
    # This is the function you asked for

    def warning_popup(title, message):
        """Displays a styled, modal pop-up warning."""
        def back_command():
            popup.destroy()
            if root.mode_var.get() == 1:
                duty_var.set(50)
            elif root.mode_var.get() ==0:
                duty_var.set(40)
            duty_change(str(duty_var.get()))
        popup = tk.Toplevel(root)
        popup.title(title)
        
        popup.config(bg=root.FRAME_COLOR, padx=30, pady=20)
        popup.style = ttk.Style(popup)
        popup.style.theme_use('clam')
        
        popup.style.configure("TLabel", background=root.FRAME_COLOR, foreground=root.TEXT_COLOR, font=("Inter", 11))
        popup.style.configure("TButton", font=("Inter", 10,"bold"), padding=5)
        # --- AND THE FIX WAS HERE (Added parentheses) ---
        popup.style.map("TButton", foreground=[('active','black')], background=[('active', root.TEXT_COLOR)])
        popup.style.configure("Primary.TButton", background=root.BUTTON_COLOR, foreground="white")
        popup.style.map("Primary.TButton", background=[('active', '#63b3ed')])

        popup.resizable(False, False)
        
        icon_label = ttk.Label(popup, text="⚠️", font=("Inter", 24))
        icon_label.pack(pady=(0, 10))
        
        message_label = ttk.Label(popup, text=message, wraplength=300, justify='center')
        message_label.pack(pady=(0, 20))
        
        ok_button = ttk.Button(
            popup, text="OK", style="Primary.TButton", command=popup.destroy
        )
        go_back = ttk.Button (
            popup, text="Go Back", command=back_command
        )
        ok_button.pack()
        go_back.pack() 

        # Calculate position to center on root
        root.update_idletasks()
        root_x = root.winfo_x()
        root_y = root.winfo_y()
        root_width = root.winfo_width()
        root_height = root.winfo_height()
        
        popup.update_idletasks()
        popup_width = popup.winfo_width()
        popup_height = popup.winfo_height()
        
        x = root_x + (root_width // 2) - (popup_width // 2)
        y = root_y + (root_height // 2) - (popup_height // 2)
        
        popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")
        
        # --- TWM HINT ---
        # This tells Tiling Window Managers to float this window
        popup.wm_attributes("-type", "dialog") 
        
        popup.grab_set()
        popup.transient(root)
        popup.wait_window()
################################################################
# Slider update
    root.mode_var = tk.IntVar(value=1) 
    warn_var = tk.IntVar(value=0) 
    def send2controller(rounded_value):
        if root.serial_connection and root.serial_connection.is_open:
            command_string = f"D:{rounded_value}\n"
            root.serial_connection.write(command_string.encode('utf-8'))
            # update_log(f"Sent: {command_string.strip()}") # Optional: for debugging
        else:
            if root.winfo_exists(): # Don't log on init
                warning_log("Not connected. Cannot send duty.")


    def duty_change(value_str):
        value = float(value_str)
        rounded_value = round(2*value)/2.0
        if (root.mode_var.get() == 1):
            if rounded_value > 70:
                if (warn_var.get() == 0):
                    warn_var.set(1)
                    warning_popup("WARNING","Over suggested Operation Point")
                    warning_log("Over suggested operation Point, keep Duty under 70 %")
                    if duty_var.get() != rounded_value:
                        return
            elif (rounded_value == 65):
                update_log("Suggested operation point 65 %")
            elif(rounded_value < 70):
                warn_var.set(0)
            send2controller(rounded_value)

        elif (root.mode_var.get() == 0):
            if rounded_value > 60:
                if warn_var.get() ==0:
                    warn_var.set(1)
                    warning_popup("WARNING","Over suggested Operation Point")
                    warning_log("Over suggested operation Point, keep Duty under 60 %")
                    if duty_var.get() != rounded_value:
                        return
            elif (rounded_value == 55):
                update_log("Suggested operation point 55 %")
            elif(rounded_value < 60):
                warn_var.set(0)
            send2controller(1-rounded_value)
        # sends value update
        duty_value_label.config(text=f"Duty: {rounded_value} %")
        draw_pwm_waveform(rounded_value)

    def up_duty():
        """Called by the Up button."""
        current_value = duty_var.get()
        new_value = min(current_value + 0.5, 100.0) # Cap at 100
        rounded = round(2*new_value)/2.0
        duty_var.set(rounded)
        duty_change(str(rounded))

    def down_duty():
        """Called by the Down button."""
        current_value = duty_var.get()
        new_value = max(current_value - 0.5, 0.0) # Floor at 0
        rounded = round(2*new_value)/2.0
        duty_var.set(rounded)
        duty_change(str(rounded))

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
    
    baud_rate = tk.StringVar()
    baud_frame = ttk.Combobox(
        conn_frame,
        textvariable = baud_rate,
        value = ["9600", "19200", "115200"],
        state='readonly'
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
        update_log(f"{len(new_ports)} active ports found")
        root.com_port_combo['value'] = new_ports
        if new_ports:
            root.com_port_var.set(new_ports[0])
        else:
            root.com_port_var.set("No ports found")
            
    refresh_button = ttk.Button(conn_frame, text="Refresh", command=refresh_ports, style="Primary.TButton")
    refresh_button.pack(side='left', padx=5)
    
    baud_rate.set("115200")
    baud_frame.pack(side='left',padx=5)

    # --- Connection Functions ---
    def connect():
        """Establishes a serial connection to the selected port."""
        port_full_name = root.com_port_var.get()
        
        if "No ports found" in port_full_name:
            warning_log("Connection failed: No port selected.")
            return
            
        port_name = port_full_name.split(' | ')[0]
        
        try:
            # --- IMPORTANT: Set baud rate to match microcontroller ---
            root.serial_connection = serial.Serial(port_name, int(baud_rate.get()), timeout=1)
            update_log(f"Connected to {port_name}")
            connect_button.config(state='disabled')
            disconnect_button.config(state='normal')
            refresh_button.config(state='disabled')
            root.com_port_combo.config(state='disabled')
            root.mode_var.set(1)
            duty_var.set(0)
            duty_change(0)
            
        except serial.SerialException as e:
            warning_log(f"Failed to connect: {e}")
            root.serial_connection = None

    def disconnect():
        """Closes the active serial connection."""
        root.mode_var.set(1)
        duty_var.set(0)
        duty_change(0)
        time.sleep(0.1)
        if root.serial_connection and root.serial_connection.is_open:
            root.serial_connection.close()
            root.serial_connection = None
            update_log("Disconnected.")
         
        connect_button.config(state='normal')
        disconnect_button.config(state='disabled')
        refresh_button.config(state='normal')
        root.com_port_combo.config(state='normal')
    
    

    connect_button = ttk.Button(conn_frame, text="Connect", command=connect, style="TButton")
    connect_button.pack(side='left',padx=5)
    disconnect_button = ttk.Button(conn_frame, text="Disconnect", command=disconnect, style="Danger.TButton")
    disconnect_button.pack(side='left',padx=5)
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
        mode_buck.config(style = "Primary.TButton")
        mode_boost.config(style = "TButton")
        duty_var.set(50)
        duty_value_label.config(text=f"Duty: {50} %")
        update_log("Buck Mode activated")
        root.mode_var.set(1) # Set mode to BUCK
        duty_change(50)
        if root.serial_connection and root.serial_connection.is_open:
            print("COMMAND: Set mode to BUCK (ON)")
        else:
            print("Error: Not connected.")
               # Redraw canvas with new mode
        draw_pwm_waveform(duty_var.get())

    def send_mode_boost():
        mode_boost.config(style = "Primary.TButton")
        mode_buck.config(style = "TButton")
        duty_var.set(40)
        duty_value_label.config(text=f"Duty: {40} %")
        update_log("Boost Mode activated")
        root.mode_var.set(0) # Set mode to BOOST        
        duty_change(40)
        if root.serial_connection and root.serial_connection.is_open:
            print("COMMAND: Set mode to BOOST (OFF)")
        else:
            print("Error: Not connected.")
               # Redraw canvas with new mode
        draw_pwm_waveform(duty_var.get())

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

    duty_var = tk.DoubleVar(value=0)
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
        text="Current value: 0%",
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

    #update status log
    def update_log(message):

        log_text.config(state='normal')
        log_text.insert(tk.END, f"{message}\n")
        log_text.see(tk.END)
        log_text.config(state='disabled')

    def warning_log(message):
        log_text.config(state='normal')
        log_text.insert(tk.END, f"{message}\n","error" )
        log_text.see(tk.END)
        log_text.config(state='disabled')

    log_text = tk.Text(
        log_card,
        height=10, 
        width=50, 
        state='disabled',  # Start as read-only
        bg=root.FRAME_COLOR, 
        fg=root.TEXT_COLOR, 
        font=("Courier New", 10),
        wrap='word',
        bd=0,
        highlightthickness=0    
    )
    log_text.tag_config("timestamp", foreground="#90cdf4") # Light blue
    log_text.tag_config("info", foreground=root.TEXT_COLOR)
    log_text.tag_config("error", foreground=root.DANGER_COLOR, font=("Inter", 12))
    log_text.tag_config("success", foreground=root.SUCCESS_COLOR)
    
    log_text.pack(fill='both', expand=True )

#/------- waveform --------------------/
    wave_frame = ttk.Frame(main_frame)
    wave_frame.pack(side='right',fill='both',expand=True)

    wave_label = ttk.LabelFrame(wave_frame, text="PWM Signal", padding=10)
    wave_label.pack(fill='both', expand=True)
    V_BUCK  = 23
    V_BOOST = 12
        # --- 1. THE CANVAS WIDGET ---
    # This creates the white drawing area
    canvas = tk.Canvas(
        wave_label,
        bg="#e0e0e0", # Set a white background
        highlightthickness=0
    )
    canvas.pack(fill='both', expand=True)
        # --- Resize and Close Handlers ---
    def on_resize(event):
        # Only redraw if the canvas itself is resizing
        if event.widget == canvas:
            draw_pwm_waveform(root.duty_var.get())


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
        # --- Draw horizontal lines for high/low ---
        canvas.create_line(0, y_high, width, y_high, fill=grid_color, dash=(4, 4))
        canvas.create_line(0, y_low, width, y_low, fill=grid_color, dash=(4, 4))
        
        current_mode = root.mode_var.get()
        duty_decimal = duty_cycle_percent/100.0        
        # Use V_BUCK for PWM high, V_BOOST_IN for calculation
        v_high_label = f"{5}V" # PWM signal is always from V_BUCK
        v_low_label = "0.0V"
        
        # ---  Calculate and show Average Voltage ---
        if current_mode == 1: # BUCK
            # Ideal V_out = D * V_in
            v_avg = V_BUCK * duty_decimal*0.96
            v_avg_text = f"Buck V_out: {v_avg:.2f}V"
        else: # BOOST
            # Ideal V_out = V_in / (1 - D)
            if duty_decimal >= 0.99: # Avoid division by zero
                v_avg_text = "Boost V_out: ---"
            else:
                v_avg = 0.93*V_BOOST / (1.0 - duty_decimal)
                v_avg_text = f"Boost V_out: {v_avg:.2f}V"
                
        canvas.create_text(10, y_high, text=v_high_label, anchor="w", fill="#555")
        canvas.create_text(10, y_low, text=v_low_label, anchor="w", fill="#555")
        
        canvas.create_rectangle(
            width - 170, # x1 (top-left)
            10,          # y1 (top-left)
            width - 10,  # x2 (bottom-right)
            35,          # y2 (bottom-right)
            fill="#e8db2a", # Light gray background
            outline=""     # No border
        )
        
        canvas.create_text(
            width - 10, 15, text=v_avg_text,
            anchor="ne", font=("Inter", 12, "bold"), fill="#000"
        )

    def initial_draw():
        draw_pwm_waveform(0)
        
    root.after(500, initial_draw) # Wait 100ms then d

    root.mainloop()

if __name__ == "__main__":
    main()

