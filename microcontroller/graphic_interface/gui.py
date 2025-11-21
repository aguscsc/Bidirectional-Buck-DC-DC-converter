import tkinter as tk
from tkinter import ttk
import serial.tools.list_ports
import serial


# get USB ports in use
def get_ports():
    ports = serial.tools.list_ports.comports()
    usb = []
    # filter ports
    for port in ports:
        if port.vid is not None:  # checks port vendor ID
            name = f"{port.device} | {port.description}"
            usb.append(name)
    if not usb:
        usb.append("No ports found")
    return usb


serial_connection = None  # define to use globally


def main():
    # /-------------- CONFIG ------------------------------------/
    root = tk.Tk()
    root.title("Buck Bidireccional Control")
    root.geometry("1920x1080")
    style = ttk.Style(root)
    style.theme_use("clam")

    # --- Colors ---
    BG_COLOR = "#2d3748"
    FRAME_COLOR = "#4a5568"
    TEXT_COLOR = "#e2e8f0"
    BUTTON_COLOR = "#4299e1"
    SUCCESS_COLOR = "#48bb78"
    DANGER_COLOR = "#f56565"
    root.configure(bg=BG_COLOR)

    # --- App-wide variables ---
    mode_var = tk.IntVar(value=1)  # 1 = BUCK, 0 = BOOST
    warn_var = tk.IntVar(value=0)  # For tracking popup

    # Voltages
    V_BUCK = 23
    V_BOOST = 12

    # --- Style Config ---
    style.configure("TFrame", background=BG_COLOR)
    style.configure(
        "TLabel",
        background=BG_COLOR,
        foreground=TEXT_COLOR,
        font=("Inter", 10),
    )
    style.configure(
        "TLabelFrame",
        background=BG_COLOR,
        foreground=TEXT_COLOR,
        relief="groove",
    )
    style.configure(
        "TLabelFrame.Label",
        background=BG_COLOR,
        foreground=TEXT_COLOR,
        font=("Inter", 12, "bold"),
    )
    style.configure("TButton", font=("Inter", 10, "bold"), padding=5)
    style.map(
        "TButton",
        foreground=[("active", "black")],
        background=[("active", TEXT_COLOR)],
    )
    style.configure("Success.TButton", background=SUCCESS_COLOR, foreground="white")
    style.map("Success.TButton", background=[("active", "#68d391")])
    style.configure("Danger.TButton", background=DANGER_COLOR, foreground="white")
    style.map("Danger.TButton", background=[("active", "#fc8181")])
    style.configure("Primary.TButton", background=BUTTON_COLOR, foreground="white")
    style.map("Primary.TButton", background=[("active", "#63b3ed")])
    style.configure("Horizontal.Tscale", background=BG_COLOR)

    # /--- WIDGET LAYOUT (All widgets created first) ---/

    # --- Connection Frame ---
    conn_frame = ttk.Frame(root, padding=(20, 10))
    conn_frame.pack(fill="x", side="top")

    ttk.Label(conn_frame, text="Connection Port: ", font=("Inter", 10, "bold")).pack(
        side="left", padx=(0, 5)
    )

    available_ports = get_ports()
    com_port_var = tk.StringVar(value=available_ports[0])

    com_port_combo = ttk.Combobox(
        conn_frame,
        textvariable=com_port_var,
        values=available_ports,
        width=30,  # Adjusted width
        state="readonly",
    )
    com_port_combo.pack(side="left", padx=5)

    # --- Baud Rate Dropdown ---
    ttk.Label(conn_frame, text="Baud rate: ", font=("Inter", 10, "bold")).pack(
        side="left", padx=(0, 5)
    )
    baud_rate_var = tk.StringVar(value="115200")
    baud_frame = ttk.Combobox(
        conn_frame,
        textvariable=baud_rate_var,
        values=["9600", "19200", "57600", "115200", "125000"],
        width=8,
        state="readonly",
    )
    baud_frame.pack(side="left", padx=5)

    # --- Frequency combobox ----

    # --- frec change -----
    def frec_change(event):
        duty_change(str(duty_var))

    ttk.Label(conn_frame, text="Frequency: ", font=("Inter", 10, "bold")).pack(
        side="left", padx=(0, 5)
    )
    frec_var = tk.StringVar(value="60k")
    frec_combo = ttk.Combobox(
        conn_frame,
        textvariable=frec_var,
        values=["10k", "20k", "30k", "40k", "50k", "60k", "70k", "80k", "90k", "100k"],
        width=8,
        state="readonly",
    )
    frec_combo.bind("<<ComboboxSelected>>", frec_change)
    frec_combo.pack(side="left", padx=5)

    # -- buttons --
    refresh_button = ttk.Button(conn_frame, text="Refresh", style="Primary.TButton")
    refresh_button.pack(side="left", padx=5)

    connect_button = ttk.Button(conn_frame, text="Connect", style="TButton")
    connect_button.pack(side="left", padx=5)

    disconnect_button = ttk.Button(
        conn_frame, text="Disconnect", style="Danger.TButton", state="disabled"
    )
    disconnect_button.pack(side="left", padx=5)

    # --- Main Frame ---
    main_frame = ttk.Frame(root, padding=20)
    main_frame.pack(fill="both", expand=True)

    # --- Control Frame (Left) ---
    control_frame = ttk.Frame(main_frame)
    control_frame.pack(side="left", fill="y", padx=(0, 10))

    # --- Mode Card ---
    mode_card = ttk.LabelFrame(control_frame, text="Mode Control", padding=15)
    mode_card.pack(fill="x", pady=(0, 20))

    mode_buck = ttk.Button(mode_card, text="BUCK", style="Primary.TButton")
    mode_boost = ttk.Button(
        mode_card,
        text="BOOST",
        style="TButton",  # Set to default
    )
    mode_buck.pack(side="left", fill="x", expand=True, padx=(0, 5))
    mode_boost.pack(side="left", fill="x", expand=True, padx=(5, 0))

    # --- Duty silder Card ---
    duty_card = ttk.LabelFrame(control_frame, text="Duty (%)", padding=15)
    duty_card.pack(fill="x")

    # --- Define variables  ---
    duty_var = tk.DoubleVar(value=0)
    step_size = tk.DoubleVar(value=0.5)  # Define step_size here

    duty_value_label = ttk.Label(
        duty_card, text=f"{duty_var.get():.2f} %", font=("Inter", 12, "bold")
    )
    duty_value_label.pack(pady=(0, 5))

    # Slider + (Button Frame)
    slider_frame = ttk.Frame(duty_card)
    button_frame = ttk.Frame(slider_frame)

    duty_slider = ttk.Scale(
        slider_frame,
        from_=0,
        to=100,
        orient="horizontal",
        variable=duty_var,
        length=400,
    )

    duty_button_up = ttk.Button(
        button_frame, text="▲", style="Primary.TButton", width=2
    )
    duty_button_down = ttk.Button(
        button_frame, text="▼", style="Primary.TButton", width=2
    )

    duty_button_up.pack(side="top", fill="x", pady=(0, 2))
    duty_button_down.pack(side="top", fill="x", pady=(2, 0))
    duty_slider.pack(side="left", fill="x", expand=True, padx=(10, 10))
    button_frame.pack(side="right")
    slider_frame.pack(fill="x", pady=(5, 0))

    # Step Size Dropdown
    step_label = ttk.Label(duty_card, text="Step size: ", font=("Inter", 10, "bold"))
    step_label.pack(side="left", pady=(5, 0))  # Pack to left
    step_frame = ttk.Combobox(
        duty_card,
        textvariable=step_size,
        values=["0.1", "0.2", "0.5", "1.0"],
        state="readonly",
        width=5,  # Add a width
    )
    step_frame.pack(side="left", pady=(5, 0))  # Pack to left

    # --- Status Log Card ---
    log_frame = ttk.Frame(control_frame)
    log_frame.pack(fill="both", expand=True, pady=(20, 0))  # Use fill='both'

    log_card = ttk.LabelFrame(log_frame, text="Status Log", padding=10)
    log_card.pack(fill="both", expand=True)

    log_text = tk.Text(
        log_card,
        height=10,
        width=50,
        state="disabled",
        bg=FRAME_COLOR,
        fg=TEXT_COLOR,
        font=("Courier New", 12),
        wrap="word",
        bd=0,
        highlightthickness=0,
    )

    clear_log_button = ttk.Button(log_card, text="Clear Log", style="TButton")
    clear_log_button.pack(side="bottom", fill="x", pady=(5, 0))

    # Configure tags *after* creating the widget
    log_text.tag_config("timestamp", foreground="#90cdf4")  # Light blue
    log_text.tag_config("info", foreground=TEXT_COLOR)
    log_text.tag_config("error", foreground=DANGER_COLOR, font=("Inter", 12))
    log_text.tag_config("success", foreground=SUCCESS_COLOR)

    log_text.pack(fill="both", expand=True)  # Pack text *after* button

    # --- Waveform Frame (Right) ---
    wave_frame = ttk.Frame(main_frame)
    wave_frame.pack(side="right", fill="both", expand=True)

    wave_label = ttk.LabelFrame(wave_frame, text="PWM Signal", padding=10)
    wave_label.pack(fill="both", expand=True)

    canvas = tk.Canvas(wave_label, bg="#e0e0e0", highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    # /--- ALL HELPER FUNCTIONS (Defined after widgets) ---/

    # --- Custom Warning Popup Function ---
    def warning_popup(title, message):
        """Displays a styled, modal pop-up warning."""
        duty_slider.config(state="disabled")
        duty_button_up.config(state="disabled")
        duty_button_down.config(state="disabled")

        if mode_var.get() == 1:
            warning_log("Keep Duty under 70%")
        elif mode_var.get() == 0:
            warning_log("Keep Duty under 60%")

        def ok_command():
            duty_slider.config(state="enabled")
            duty_button_up.config(state="enabled")
            duty_button_down.config(state="enabled")
            popup.destroy()

        def back_command():
            duty_slider.config(state="enabled")
            duty_button_up.config(state="enabled")
            duty_button_down.config(state="enabled")

            popup.destroy()
            if mode_var.get() == 1:
                duty_var.set(50.0)
            elif mode_var.get() == 0:
                duty_var.set(40.0)
            duty_change(str(duty_var.get()))

        popup = tk.Toplevel(root)
        popup.title(title)

        popup.config(bg=FRAME_COLOR, padx=30, pady=20)
        style = ttk.Style(popup)
        style.theme_use("clam")

        style.configure(
            "TLabel",
            background=FRAME_COLOR,
            foreground=TEXT_COLOR,
            font=("Inter", 11),
        )
        style.configure("TButton", font=("Inter", 10, "bold"), padding=5)
        style.map(
            "TButton",
            foreground=[("active", "black")],
            background=[("active", TEXT_COLOR)],
        )
        style.configure("Primary.TButton", background=BUTTON_COLOR, foreground="white")
        style.map("Primary.TButton", background=[("active", "#63b3ed")])

        popup.resizable(False, False)

        icon_label = ttk.Label(popup, text="⚠️", font=("Inter", 24))
        icon_label.pack(pady=(0, 10))

        message_label = ttk.Label(popup, text=message, wraplength=300, justify="center")
        message_label.pack(pady=(0, 20))

        ok_button = ttk.Button(
            popup, text="OK", style="Primary.TButton", command=ok_command
        )
        go_back_button = ttk.Button(
            popup, text="Go Back", command=back_command, style="TButton"
        )
        ok_button.pack(side="left", fill="x", expand=True, padx=(0, 5))
        go_back_button.pack(side="right", fill="x", expand=True, padx=(5, 0))

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

        popup.wm_attributes("-type", "dialog")  # TWM hint

        popup.grab_set()
        popup.transient(root)
        popup.wait_window()

    # --- Log Functions ---
    def update_log(message):
        log_text.config(state="normal")
        log_text.insert(tk.END, f"{message}\n", ("info",))
        log_text.see(tk.END)
        log_text.config(state="disabled")

    def warning_log(message):
        log_text.config(state="normal")
        log_text.insert(tk.END, f"{message}\n", ("error",))
        log_text.see(tk.END)
        log_text.config(state="disabled")

    def clear_log():
        """Clears all text from the log."""
        log_text.config(state="normal")
        log_text.delete("1.0", tk.END)
        log_text.config(state="disabled")

    # --- Serial Send Function ---
    def send2controller(rounded_value, frec_var):
        if serial_connection and serial_connection.is_open:
            try:
                duty_standarized = str(int((rounded_value * 10)))
                if len(duty_standarized) > 3:
                    duty_standarized = duty_standarized[:3]
                elif len(duty_standarized) < 3:
                    duty_standarized = duty_standarized.zfill(3)
                if len(frec_var) > 3:
                    frec_standarized = frec_var[:3]
                else:
                    frec_standarized = frec_var[:2]
                    frec_standarized = frec_standarized.zfill(3)

                command_string_duty = f"D{duty_standarized}\n"
                command_string_frec = f"F{frec_standarized}\n"

                serial_connection.write(command_string_duty.encode("utf-8"))
                serial_connection.write(command_string_frec.encode("utf-8"))

                # uncomment to debbug commands sent to the microcontroller
                update_log(f"Sent: {command_string_duty.strip()}")
                update_log(f"Sent: {command_string_frec.strip()}\n")

            except serial.SerialException as e:
                warning_log(f"Could not send data: {e}")
                disconnect()  # Auto-disconnect on write error
        else:
            if root.winfo_exists():  # Don't log on init
                warning_log("Not connected. Cannot send duty.")

    # --- Canvas Draw Function ---
    def draw_pwm_waveform(duty_cycle_percent):
        canvas.delete("all")
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        if width <= 1 or height <= 1:
            return

        grid_color = "#000000"

        for i in range(1, 10):
            x = width * (i / 10.0)
            canvas.create_line(x, 0, x, height, fill=grid_color, dash=(2, 4))

        y_center = height / 2
        canvas.create_line(0, y_center, width, y_center, fill=grid_color, dash=(2, 4))

        amplitude = height * 0.3
        y_high = y_center - amplitude
        y_low = y_center + amplitude

        canvas.create_line(0, y_high, width, y_high, fill=grid_color, dash=(4, 4))
        canvas.create_line(0, y_low, width, y_low, fill=grid_color, dash=(4, 4))

        current_mode = mode_var.get()
        duty_decimal = duty_cycle_percent / 100.0

        v_high_label = "3.3V"
        v_low_label = "0.0V"

        if current_mode == 1:  # BUCK
            v_avg = V_BUCK * duty_decimal * 0.96
            v_avg_text = f"Buck V_out: {v_avg:.2f}V"
        else:  # BOOST
            if duty_decimal >= 0.99:
                v_avg_text = "Boost V_out: ---"
            else:
                v_avg = (0.93 * V_BOOST) / (1.0 - duty_decimal)
                v_avg_text = f"Boost V_out: {v_avg:.2f}V"

        canvas.create_text(10, y_high, text=v_high_label, anchor="w", fill="#555")
        canvas.create_text(10, y_low, text=v_low_label, anchor="w", fill="#555")

        # Background for text
        canvas.create_rectangle(
            width - 210,
            10,
            width - 10,
            40,
            fill="#e8db2a",
            outline="",
        )
        canvas.create_text(
            width - 15,
            17,
            text=v_avg_text,  # Centered
            anchor="ne",
            font=("Inter", 15, "bold"),
            fill="#000",
        )

        padding = 10
        signal_width = max(0, width - (padding * 2))
        on_width = signal_width * duty_decimal
        off_width = signal_width - on_width

        points = [
            (padding, y_low),
            (padding, y_high),
            (padding + on_width, y_high),
            (padding + on_width, y_low),
            (padding + on_width + off_width, y_low),
        ]
        canvas.create_line(points, width=3, fill="#4299e1")

    # --- Duty Slider Functions ---
    def duty_change(value_str):
        """Called when the duty slider is moved OR var is set."""
        try:
            value = float(value_str)
        except ValueError:
            value = 0.0

        rounded_value = round(value, 1)  # Use 1 decimal place

        if duty_var.get() != rounded_value:
            duty_var.set(rounded_value)

        if mode_var.get() == 1:  # BUCK
            if rounded_value > 70:
                if warn_var.get() == 0:
                    warn_var.set(1)
                    warning_popup("WARNING", "Over suggested Operation Point")
                    if duty_var.get() != rounded_value:
                        return
            elif rounded_value == 65:
                update_log("Suggested operation point 65 %")
            elif rounded_value < 70:
                warn_var.set(0)

            send2controller(rounded_value, frec_var.get())

        elif mode_var.get() == 0:  # BOOST
            if rounded_value > 60:
                if warn_var.get() == 0:
                    warn_var.set(1)
                    warning_popup("WARNING", "Over suggested Operation Point")
                    if duty_var.get() != rounded_value:
                        return
            # --- FIX: Use 'and', not '&' ---
            elif rounded_value == 55 and mode_var.get() == 0:
                update_log("Suggested operation point 55 %")
            elif rounded_value < 60:
                warn_var.set(0)

            # --- FIX: Send 100-D for BOOST ---
            send2controller(100.0 - rounded_value, frec_var.get())

        duty_value_label.config(text=f"Duty: {rounded_value:.1f} %")  # 1 decimal
        draw_pwm_waveform(rounded_value)

    def up_duty():
        """Called by the Up button."""
        current_value = duty_var.get()
        new_value = min(current_value + step_size.get(), 100.0)
        rounded = round(new_value, 1)  # Round to 1 decimal
        duty_var.set(rounded)
        duty_change(str(rounded))

    def down_duty():
        """Called by the Down button."""
        current_value = duty_var.get()
        new_value = max(current_value - step_size.get(), 0.0)
        rounded = round(new_value, 1)  # Round to 1 decimal
        duty_var.set(rounded)
        duty_change(str(rounded))

    # --- Mode Control Functions ---
    def send_mode_buck():
        mode_buck.config(style="Primary.TButton")
        mode_boost.config(style="TButton")
        mode_var.set(1)
        update_log("Buck Mode activated")

        # No need to send M:1

        duty_var.set(50.0)
        duty_change(str(duty_var.get()))  # Manually call to send duty

    def send_mode_boost():
        mode_boost.config(style="Primary.TButton")
        mode_buck.config(style="TButton")
        mode_var.set(0)
        update_log("Boost Mode activated")

        # No need to send M:0

        duty_var.set(40.0)
        duty_change(str(duty_var.get()))  # Manually call to send duty

    # --- Connection Functions ---
    def connect():
        """Establishes a serial connection to the selected port."""
        global serial_connection
        port_full_name = com_port_var.get()

        if "No ports found" in port_full_name:
            warning_log("Connection failed: No port selected.")
            return

        port_name = port_full_name.split(" | ")[0]
        selected_baud = int(baud_rate_var.get())

        try:
            serial_connection = serial.Serial(port_name, selected_baud, timeout=1)
            update_log(f"Connected to {port_name} at {selected_baud} baud.")
            try:
                send_mode_buck()
            except:
                update_log("Buck mode failed")
            connect_button.config(state="disabled")
            disconnect_button.config(state="normal")
            refresh_button.config(state="disabled")
            com_port_combo.config(state="disabled")
            baud_frame.config(state="disabled")

            # Set initial safe state
            mode_var.set(1)
            duty_var.set(0.0)
            duty_change(str(0.0))

        except serial.SerialException as e:
            warning_log(f"Failed to connect: {e}")
            serial_connection = None

    def disconnect():
        """Closes the active serial connection."""
        global serial_connection
        # 1. Send "safe" command first, only if connected
        if serial_connection and serial_connection.is_open:
            try:
                # Send a final "duty 0" command
                serial_connection.write(b"D:0.0\n")
                serial_connection.close()
                serial_connection = None
                update_log("Disconnected.")
            except serial.SerialException as e:
                warning_log(f"Error on disconnect: {e}")
                serial_connection = None  # Force-set to None

        # 2. Now that port is closed, update GUI
        mode_var.set(1)
        duty_var.set(0.0)
        duty_change(str(0.0))  # Update GUI visuals (won't send)

        # 3. Update buttons
        connect_button.config(state="normal")
        disconnect_button.config(state="disabled")
        refresh_button.config(state="normal")
        com_port_combo.config(state="normal")
        baud_frame.config(state="normal")

    def refresh_ports():
        new_ports = get_ports()
        update_log(f"{len(new_ports)} active ports found")
        com_port_combo["value"] = new_ports
        com_port_var.set(new_ports[0])

    # --- Bindings and Final Setup ---
    refresh_button.config(command=refresh_ports)
    connect_button.config(command=connect)
    disconnect_button.config(command=disconnect)

    mode_buck.config(command=send_mode_buck)
    mode_boost.config(command=send_mode_boost)
    duty_slider.config(command=duty_change)
    duty_button_up.config(command=up_duty)
    duty_button_down.config(command=down_duty)
    clear_log_button.config(command=clear_log)

    def on_resize(event):
        if event.widget == canvas:
            draw_pwm_waveform(duty_var.get())

    canvas.bind("<Configure>", on_resize)

    def on_closing():
        disconnect()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    def initial_draw():
        draw_pwm_waveform(duty_var.get())

    root.after(100, initial_draw)

    root.mainloop()


if __name__ == "__main__":
    main()
