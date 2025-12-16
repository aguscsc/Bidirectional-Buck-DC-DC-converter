import tkinter as tk
from tkinter import ttk
import serial.tools.list_ports
import serial
import math
import socket
import threading
import re


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
        usb.append("No se encontraron puertos")
    return usb


serial_connection = None  # define to use globally


def main():
    # /-------------- CONFIG ------------------------------------/
    root = tk.Tk()
    root.title("Buck Bidireccional Control")
    root.geometry("1344x756")
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

    ttk.Label(conn_frame, text="Puerto de conexión: ", font=("Inter", 10, "bold")).pack(
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
    ttk.Label(conn_frame, text="Baudios: ", font=("Inter", 10, "bold")).pack(
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

    # --- Frequency Slider ---
    # Variable de frecuencia
    frec_var = tk.DoubleVar(value=60.0)  # Valor inicial 60 kHz

    def frec_slider_change(value_str):
        try:
            val = float(value_str)
        except ValueError:
            val = 60.0
        rounded_frec = round(val, 0)
        frec_value_label.config(text=f"{int(rounded_frec)} kHz")
        duty_change(str(duty_var.get()))

    ttk.Label(conn_frame, text="Frecuencia:", font=("Inter", 10, "bold")).pack(
        side="left", padx=(10, 5)
    )

    # Frame para el slider de frecuencia
    frec_frame = ttk.Frame(conn_frame)
    frec_frame.pack(side="left", padx=5)

    # Etiqueta de valor
    frec_value_label = ttk.Label(frec_frame, text=f"{int(frec_var.get())} kHz", width=8)
    frec_value_label.pack(side="left", padx=(0, 5))

    # Slider
    frec_slider = ttk.Scale(
        frec_frame,
        from_=40,
        to=80,
        orient="horizontal",
        variable=frec_var,
        length=150,
        command=frec_slider_change,  # Vinculación
    )
    frec_slider.pack(side="left")

    # -- buttons --
    refresh_button = ttk.Button(conn_frame, text="Refrescar", style="Primary.TButton")
    refresh_button.pack(side="left", padx=5)

    connect_button = ttk.Button(conn_frame, text="Connectar", style="TButton")
    connect_button.pack(side="left", padx=5)

    disconnect_button = ttk.Button(
        conn_frame, text="Desconectar", style="Danger.TButton", state="disabled"
    )
    disconnect_button.pack(side="left", padx=5)

    # --- Main Frame ---
    main_frame = ttk.Frame(root, padding=20)
    main_frame.pack(fill="both", expand=True)

    # --- Control Frame (Left) ---
    control_frame = ttk.Frame(main_frame)
    control_frame.pack(side="left", fill="y", padx=(0, 10))

    # --- Mode Card ---
    mode_card = ttk.LabelFrame(control_frame, text="Control de Modo", padding=15)
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

    # --- Telemetry Variables (UDP) ---
    live_buck_var = tk.DoubleVar(value=0.0)
    live_boost_var = tk.DoubleVar(value=0.0)
    stop_udp_thread = False  # Flag to kill thread on close

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

    duty_set_button = ttk.Button(
        duty_card, text="Puntor de operación", width=4, style="Primary.TButton"
    )
    duty_button_up = ttk.Button(
        button_frame, text="▲", style="Primary.TButton", width=2
    )
    duty_button_down = ttk.Button(
        button_frame, text="▼", style="Primary.TButton", width=2
    )

    duty_set_button.pack(side="top", fill="x", padx=(1, 1))
    duty_button_up.pack(side="top", fill="x", pady=(0, 2))
    duty_button_down.pack(side="top", fill="x", pady=(2, 0))
    duty_slider.pack(side="left", fill="x", expand=True, padx=(10, 10))
    button_frame.pack(side="right")
    slider_frame.pack(fill="x", pady=(5, 0))

    # Step Size Dropdown
    step_label = ttk.Label(
        duty_card, text="Tamaño de paso: ", font=("Inter", 10, "bold")
    )
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

    clear_log_button = ttk.Button(log_card, text="Limpiar Log", style="TButton")
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

    # PWM signal
    wave_label = ttk.LabelFrame(wave_frame, text="Señal PWM", padding=10)
    wave_label.pack(side="bottom", fill="both", expand=True)

    canvas = tk.Canvas(wave_label, bg="#e0e0e0", highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    # voltage output graph
    output_label = ttk.LabelFrame(wave_frame, text="Voltaje de salida", padding=10)
    output_label.pack(side="right", fill="both", expand=True)

    output_canvas = tk.Canvas(output_label, bg="#e0e0e0", highlightthickness=0)
    output_canvas.pack(fill="both", expand=True)

    # Frequency graph
    frec_label = ttk.LabelFrame(wave_frame, text="Frecuencia", padding=10)
    frec_label.pack(side="left", fill="both", expand=True)

    frec_canvas = tk.Canvas(frec_label, bg="#e0e0e0", highlightthickness=0)
    frec_canvas.pack(fill="both", expand=True)

    # /--- ALL HELPER FUNCTIONS (Defined after widgets) ---/

    # --- Custom Warning Popup Function ---
    def warning_popup(title, message):
        """Displays a styled, modal pop-up warning."""
        duty_slider.config(state="disabled")
        duty_button_up.config(state="disabled")
        duty_button_down.config(state="disabled")
        duty_set_button.config(state="disabled")
        mode_boost.config(state="disabled")
        mode_buck.config(state="disabled")
        # También deshabilitamos el slider de frecuencia en alertas
        frec_slider.config(state="disabled")

        if mode_var.get() == 1:
            warning_log("Keep Duty under 80%")
        elif mode_var.get() == 0:
            warning_log("Keep Duty under 80%")

        def enable_controls():
            duty_slider.config(state="enabled")
            duty_button_up.config(state="enabled")
            duty_button_down.config(state="enabled")
            duty_set_button.config(state="enabled")
            mode_boost.config(state="enabled")
            mode_buck.config(state="enabled")
            frec_slider.config(state="enabled")  # Reactivar frecuencia

        def ok_command():
            enable_controls()
            popup.destroy()

        def back_command():
            enable_controls()
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

        def on_popup_close():
            enable_controls()
            popup.destroy()

        popup.protocol("WM_DELETE_WINDOW", on_popup_close)
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
    def send2controller(rounded_value, frec_val):
        if serial_connection and serial_connection.is_open:
            try:
                # ### --- CAMBIO: Formateo de frecuencia como número ---
                # Ahora frec_val es un float (ej. 60.0), no string "60k"
                duty_standarized = str(int((rounded_value * 10)))
                frec_standarized = str(int(frec_val))  # Ej. "60"

                if len(duty_standarized) > 3:
                    duty_standarized = duty_standarized[:3]
                elif len(duty_standarized) < 3:
                    duty_standarized = duty_standarized.zfill(3)

                # Protocolo de 3 dígitos para frecuencia (ej. 060 para 60kHz)
                if len(frec_standarized) > 3:
                    frec_standarized = frec_standarized[:3]
                else:
                    frec_standarized = frec_standarized.zfill(3)

                command_string_duty = f"D{duty_standarized}\n"
                command_string_frec = f"F{frec_standarized}\n"

                serial_connection.write(command_string_duty.encode("utf-8"))
                serial_connection.write(command_string_frec.encode("utf-8"))

                # uncomment to debbug commands sent to the microcontroller
                # update_log(f"Sent: {command_string_duty.strip()}")
                # update_log(f"Sent: {command_string_frec.strip()}\n")

            except serial.SerialException as e:
                warning_log(f"No se pudieron mandar datos: {e}")
                disconnect()  # Auto-disconnect on write error
        else:
            if root.winfo_exists():  # Don't log on inith
                warning_log("No conectado. No es posible mandar Duty.")

    # // ---------------------------- Drawing Functions ----------------------------//
    # --- Voltge output draw ---

    def draw_output(
        target_canvas, duty_cycle_percent, mode_var, live_buck_var, live_boost_var, frec
    ):
        """
        Draws a line representing the smoothed DC output voltage (V_avg)
        with a small sinusoidal ripple based on the Buck/Boost mode.
        """
        RIPPLE_LOOKUP = {
            30000.0: 0.022,
            40000.0: 0.015,
            50000.0: 0.011,
            60000.0: 0.009,
            70000.0: 0.008,
            80000.0: 0.006,
            90000.0: 0.0056,
            100000.0: 0.0048,
        }
        target_canvas.delete("all")  # Use a tag to clear only the output line

        width = target_canvas.winfo_width()
        height = target_canvas.winfo_height()
        if width <= 1 or height <= 1:
            return

        grid_color = "#000000"

        for i in range(1, 10):
            x = width * (i / 10.0)
            target_canvas.create_line(x, 0, x, height, fill=grid_color, dash=(2, 4))

        y_center = height / 2
        target_canvas.create_line(
            0, y_center, width, y_center, fill=grid_color, dash=(2, 4)
        )

        amplitude = height * 0.3
        y_high = y_center - amplitude
        y_low = y_center + amplitude

        target_canvas.create_line(
            0, y_high, width, y_high, fill=grid_color, dash=(4, 4)
        )
        target_canvas.create_line(0, y_low, width, y_low, fill=grid_color, dash=(4, 4))

        duty_decimal = duty_cycle_percent / 100.0
        current_mode = mode_var

        # ### --- CAMBIO: Uso directo de valor numérico ---
        # f_value ahora es float directo (ej. 60.0), multiplicamos por 1000 para Hz
        f_value = float(frec) * 1000.0

        # Buscamos el valor más cercano o usamos default
        v_ripple = RIPPLE_LOOKUP.get(f_value, 0.01)  # Default 0.01 si no está exacto

        # ---  Calculate Average Output Voltage (V_avg) ---
        if current_mode == 1:  # BUCK
            # V_out ≈ D * V_in * 0.93 (using the same formula from draw_pwm_waveform)
            V_avg = live_buck_var.get()

            # Define max expected output voltage for scaling
            V_max_display = 30.0

        else:  # BOOST
            # Define max expected output voltage for scaling
            V_max_display = 100.0
            if duty_decimal >= 0.99:
                V_avg = (
                    0.0  # Treat as zero or undefined for visualization near 100% duty
                )
            else:
                # V_out ≈ V_in / (1 - D) * 0.87
                v_ripple *= 2
                V_avg = live_boost_var.get()

        # ---  Scale V_avg and Ripple to Pixel Coordinates ---

        y_center = height / 2
        amplitude = height * 0.3
        y_low = y_center + amplitude  # Represents 0V
        y_high = y_center - amplitude  # Represents the max voltage (e.g., 3.3V)

        #  y_low - 90% of height
        V_scale_height = height * 0.9

        # Clamp V_avg to V_max_display to prevent drawing off-screen
        V_clamped = min(V_avg, V_max_display)

        # Distance from the bottom (y_low) corresponding to V_avg
        y_offset_from_low = (V_clamped / V_max_display) * V_scale_height
        y_avg_px = y_low - y_offset_from_low

        # Scale the ripple to pixel amplitude
        ripple_amp_px = (v_ripple / 2) * (V_scale_height / V_max_display) * 100

        # ---  Generate Ripple Points ---
        points = []
        num_points = 200  # Number of line segments
        ripple_cycles = 6  # How many ripple oscillations to show across the screen

        for i in range(num_points):
            x = i * (width / num_points)

            # Calculate sinusoidal offset
            # math.sin(angle) * (amplitude)
            sin_offset = (
                math.sin(i * ripple_cycles * 2 * math.pi / num_points) * ripple_amp_px
            )

            y = y_avg_px + sin_offset

            points.append((x, y))

        # --- Draw the Ripple Line ---
        flattened_points = [coord for point in points for coord in point]

        target_canvas.create_line(
            flattened_points,
            width=2,
            fill="#344ceb",  # Success/Green color for output
            tag="output_ripple",
        )

        # --- Add V_avg label (Optional, if not already done by draw_pwm_waveform) ---
        target_canvas.create_text(
            width - 15,
            y_avg_px - 40,
            text=f"V_avg: {V_avg:.2f}V",
            anchor="ne",
            fill="#344ceb",
            tag="output_ripple",
        )

    # --- Frequency Draw ---
    def draw_frec(frec, duty_cycle_percent):
        frec_canvas.delete("all")

        frec_canvas.delete("all")
        width = frec_canvas.winfo_width()
        height = frec_canvas.winfo_height()
        if width <= 1 or height <= 1:
            return

        grid_color = "#000000"

        # ### --- CAMBIO: Uso directo de valor numérico ---
        # f_value ahora es float directo (ej. 60.0), multiplicamos por 1000 para Hz
        f_value = float(frec) * 1000.0

        period = 1.0 / f_value
        time_span = 32e-6

        total_cycles = time_span / period
        num_cycles = math.ceil(total_cycles)

        for i in range(1, 10):
            x = width * (i / 10.0)
            frec_canvas.create_line(x, 0, x, height, fill=grid_color, dash=(2, 4))

        y_center = height / 2
        frec_canvas.create_line(
            0, y_center, width, y_center, fill=grid_color, dash=(2, 4)
        )

        amplitude = height * 0.3
        y_high = y_center - amplitude
        y_low = y_center + amplitude

        frec_canvas.create_line(0, y_high, width, y_high, fill=grid_color, dash=(4, 4))
        frec_canvas.create_line(0, y_low, width, y_low, fill=grid_color, dash=(4, 4))

        # singal

        duty_decimal = duty_cycle_percent / 100.0
        padding = 10
        full_signal_width = max(0, width - padding * 2)
        cycles_width = full_signal_width / total_cycles

        on_width = cycles_width * duty_decimal
        off_width = cycles_width - on_width

        current_x = padding
        points = [(current_x, y_low)]

        for i in range(int(num_cycles)):
            # first point
            points.append((current_x, y_high))

            # end of on time
            current_x += on_width
            points.append((current_x, y_high))

            # first low point
            points.append((current_x, y_low))

            # off time
            current_x += off_width
            points.append((current_x, y_low))

            # stop if canvas lenght is exceeded
            if current_x > width - padding:
                break

        if points[-1][0] > width - padding:
            points[-1] = (width - padding, points[-1][1])

        # turns tupple into list
        flat_points = [coord for point in points for coord in point]
        frec_canvas.create_line(flat_points, width=3, fill="#4299e1")

        frec_canvas.create_text(
            width - 15,
            17,
            text=f"Frecuencia: {int(frec)}kHz",  # Mostrar como entero
            anchor="ne",
            fill="#000",
        )

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
            v_avg = live_buck_var.get()
            v_avg_text = f"Buck V_out: {v_avg:.2f}V"
        else:  # BOOST
            if duty_decimal >= 0.99:
                v_avg_text = "Boost V_out: ---"
            else:
                v_avg = live_boost_var.get()
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
            if rounded_value > 80:
                if warn_var.get() == 0:
                    warn_var.set(1)
                    warning_popup("ADVERTENCIA", "Sobre el punto de Operación sugerido")
                    if duty_var.get() != rounded_value:
                        return
            elif rounded_value == 72:
                update_log("Punto de operación sugerido 72 %")
            elif rounded_value < 70:
                warn_var.set(0)

            send2controller(rounded_value, frec_var.get())

        elif mode_var.get() == 0:  # BOOST
            if rounded_value > 80:
                if warn_var.get() == 0:
                    warn_var.set(1)
                    warning_popup("ADVERTENCIA", "Sobre el punto de operación sugerido")
                    if duty_var.get() != rounded_value:
                        return
            # --- FIX: Use 'and', not '&' ---
            elif rounded_value == 67 and mode_var.get() == 0:
                update_log("Punto de operación sugerido 67 %")
            elif rounded_value < 60:
                warn_var.set(0)

            # --- FIX: Send 100-D for BOOST ---
            send2controller(100.0 - rounded_value, frec_var.get())

        duty_value_label.config(text=f"Duty: {rounded_value:.1f} %")  # 1 decimal
        draw_pwm_waveform(rounded_value)
        # Pasamos el valor numérico directo de frecuencia
        draw_frec(frec_var.get(), duty_var.get())
        draw_output(
            output_canvas,
            duty_var.get(),
            mode_var.get(),
            live_buck_var,
            live_boost_var,
            frec_var.get(),
        )

    def set_operational_point():
        """sets operational point in smooth steps"""
        if mode_var.get() == 1:
            if duty_var.get() < 65:
                while duty_var.get() < 65:
                    duty_var.set(duty_var.get() + 0.2)
                    # to show the smooth transition
                    # print(duty_var.get())
            else:
                while duty_var.get() > 65:
                    duty_var.set(duty_var.get() - 0.2)
            duty_var.set(65)
            duty_change(str(65))
        elif mode_var.get() == 0:
            if duty_var.get() < 55:
                while duty_var.get() < 55:
                    duty_var.set(duty_var.get() + 0.2)
            else:
                while duty_var.get() > 55:
                    duty_var.set(duty_var.get() - 0.2)
            duty_var.set(55)
            duty_change(str(55))

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
        update_log("Modo Buck activado")

        # No need to send M:1

        duty_var.set(50.0)
        duty_change(str(duty_var.get()))  # Manually call to send duty

    def send_mode_boost():
        mode_boost.config(style="Primary.TButton")
        mode_buck.config(style="TButton")
        mode_var.set(0)
        update_log("Modo Boost activado")

        # No need to send M:0

        duty_var.set(40.0)
        duty_change(str(duty_var.get()))  # Manually call to send duty

    # --- Connection Functions ---
    def connect():
        """Establishes a serial connection to the selected port."""
        global serial_connection
        port_full_name = com_port_var.get()

        if "No ports found" in port_full_name:
            warning_log("Conexión fallida: No hay puertos seleccionados.")
            return

        port_name = port_full_name.split(" | ")[0]
        selected_baud = int(baud_rate_var.get())

        try:
            serial_connection = serial.Serial(port_name, selected_baud, timeout=1)
            update_log(f"Conectado a {port_name} a {selected_baud} baudios.")
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
            warning_log(f"Falló al conectar: {e}")
            serial_connection = None

    def disconnect():
        """Closes the active serial connection."""
        global serial_connection
        #  Send "safe" command first, only if connected
        if serial_connection and serial_connection.is_open:
            try:
                # Send a final "duty 0" command
                serial_connection.write(b"D:0.0\n")
                serial_connection.close()
                serial_connection = None
                update_log("Desconectado.")
            except serial.SerialException as e:
                warning_log(f"Error al desconectar: {e}")
                serial_connection = None  # Force-set to None

        #  Now that port is closed, update GUI
        mode_var.set(1)
        duty_var.set(0.0)
        duty_change(str(0.0))  # Update GUI visuals (won't send)

        #  Update buttons
        connect_button.config(state="normal")
        disconnect_button.config(state="disabled")
        refresh_button.config(state="normal")
        com_port_combo.config(state="normal")
        baud_frame.config(state="normal")

    def refresh_ports():
        new_ports = get_ports()
        update_log(f"{len(new_ports)} Puertos activos encontrados")
        com_port_combo["value"] = new_ports
        com_port_var.set(new_ports[0])

    # --- Bindings and Final Setup ---
    refresh_button.config(command=refresh_ports)
    connect_button.config(command=connect)
    disconnect_button.config(command=disconnect)

    mode_buck.config(command=send_mode_buck)
    mode_boost.config(command=send_mode_boost)
    duty_slider.config(command=duty_change)
    duty_set_button.config(command=set_operational_point)
    duty_button_up.config(command=up_duty)
    duty_button_down.config(command=down_duty)
    clear_log_button.config(command=clear_log)

    def on_resize(event):
        if event.widget == canvas:
            draw_pwm_waveform(duty_var.get())
        elif event.widget == frec_canvas:
            draw_frec(frec_var.get(), duty_var.get())
        elif event.widget == output_canvas:
            draw_output(
                output_canvas,
                duty_var.get(),
                mode_var.get(),
                live_buck_var,
                live_boost_var,
                frec_var.get(),
            )

    canvas.bind("<Configure>", on_resize)
    output_canvas.bind("<Configure>", on_resize)
    frec_canvas.bind("<Configure>", on_resize)

    def on_closing():
        disconnect()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    def initial_draw():
        draw_pwm_waveform(duty_var.get())
        draw_frec(frec_var.get(), duty_var.get())
        draw_output(
            output_canvas,
            duty_var.get(),
            mode_var.get(),
            live_buck_var,
            live_boost_var,
            frec_var.get(),
        )

    # --- UDP Listener Function ---
    def start_udp_listener():
        UDP_IP = "0.0.0.0"  # Listen to ALL incoming traffic
        UDP_PORT = 3333

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((UDP_IP, UDP_PORT))
        sock.settimeout(1.0)  # Don't block forever so we can close cleanly

        update_log(f"Escuchando UDP en puerto {UDP_PORT}...")

        def listen_loop():
            while not stop_udp_thread:
                try:
                    data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes
                    message = data.decode("utf-8")

                    # Parse the string: "Buck: 12.50 V, Boost: 24.00 V"
                    # We use Regex to find the numbers
                    match = re.search(
                        r"Buck:\s*([\d\.]+)\s*V,\s*Boost:\s*([\d\.]+)\s*V", message
                    )

                    if match:
                        v_buck_read = float(match.group(1))
                        v_boost_read = float(match.group(2))

                        # Update Tkinter variables safely
                        # (root.after ensures we don't crash the GUI thread)
                        root.after(0, lambda: live_buck_var.set(v_buck_read))
                        root.after(0, lambda: live_boost_var.set(v_boost_read))

                        def update_visuals():
                            # Update the data variables
                            live_buck_var.set(v_buck_read)
                            live_boost_var.set(v_boost_read)

                            # TRIGGER REDRAW
                            # This refreshes the text labels and the graph lines
                            draw_pwm_waveform(duty_var.get())
                            draw_output(
                                output_canvas,
                                duty_var.get(),
                                mode_var.get(),
                                live_buck_var,
                                live_boost_var,
                                frec_var.get(),
                            )

                        # Schedule the update on the Main Thread
                        root.after(0, update_visuals)

                except socket.timeout:
                    continue  # Loop back and check stop_flag
                except Exception as e:
                    print(f"UDP Error: {e}")
                    break

            sock.close()
            print("UDP Socket Closed")

        # Start the background thread
        t = threading.Thread(target=listen_loop, daemon=True)
        t.start()

    root.after(100, initial_draw)
    start_udp_listener()
    root.mainloop()


if __name__ == "__main__":
    main()
