import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

# --- Crear la figura y el eje ---
fig, ax = plt.subplots(figsize=(7, 5))

# Imagen de fondo inicial
fondo = mpimg.imread("assets/montana.png")
ax.imshow(fondo, extent=[-50, 120, -10, 40], aspect="auto")

# Sprite del esquiador
sprite = mpimg.imread("assets/sky.png")

# Variables globales
linea_trayectoria, = ax.plot([], [], "b", linewidth=2, label="Trayectoria")
esquiador = None
ani = None


def simular_salto():
    global ani, esquiador, linea_trayectoria

    btn_simular.config(state=tk.DISABLED)

    try:
        v0 = float(entry_velocidad.get())
        angulo = float(entry_angulo.get())
        m = -float(entry_pendiente.get())
        h = float(entry_altura.get())
    except ValueError:
        label_resultado.config(text="❌ Ingresa valores numéricos")
        btn_simular.config(state=tk.NORMAL)
        return

    g = 9.81
    theta = np.radians(angulo)

    # Posición inicial
    x0, y0 = 0, h

    # Componentes de la velocidad
    v0x = v0 * np.cos(theta)
    v0y = v0 * np.sin(theta)

    # Tiempo de aterrizaje
    t_aterrizaje = 2 * (v0y - m * v0x) / g
    if t_aterrizaje <= 0:
        label_resultado.config(text="⚠️ No hay intersección con la pista")
        btn_simular.config(state=tk.NORMAL)
        return

    # Trayectoria
    t = np.linspace(0, t_aterrizaje, num=300)
    x = x0 + v0x * t
    y = y0 + v0y * t - 0.5 * g * t**2

    # Punto de aterrizaje
    x_land = x[-1]
    y_land = y[-1]

    # --- Calcular mejor ángulo ---
    mejor_dist = 0
    mejor_ang = 0
    for ang_test in np.linspace(1, 80, 200):
        th = np.radians(ang_test)
        vx = v0 * np.cos(th)
        vy = v0 * np.sin(th)
        t_at = 2 * (vy - m * vx) / g
        if t_at > 0:
            x_test = x0 + vx * t_at
            if x_test > mejor_dist:
                mejor_dist = x_test
                mejor_ang = ang_test

    # --- Límites dinámicos ---
    xmax = mejor_dist + 20
    ymin = min(np.min(y), y_land) - 20
    ymax = max(h + 10, np.max(y) + 10)

    # Reset gráfico (sin fondo de imagen)
    ax.clear()
    ax.set_facecolor("skyblue")
    ax.set_xlim(0, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_title("Salto de esquí animado")
    ax.set_xlabel("Distancia (m)")
    ax.set_ylabel("Altura (m)")
    ax.grid(True, linestyle=":")

    # Dibujar pista
    xpista = np.linspace(x0, xmax, 400)
    ypista = y0 + m * (xpista - x0)
    ax.fill_between(xpista, ypista, ymin, color="saddlebrown")
    ax.plot(xpista, ypista, "k--", linewidth=2, label="Pista")

    # Elementos animados
    linea_trayectoria, = ax.plot([], [], "b", linewidth=2)
    imagebox = OffsetImage(sprite, zoom=0.1)
    esquiador = AnnotationBbox(imagebox, (x[0], y[0]), frameon=False)
    ax.add_artist(esquiador)
    ax.plot(x_land, y_land, "ro", label="Aterrizaje")

    # Animación
    def actualizar(frame):
        linea_trayectoria.set_data(x[:frame], y[:frame])
        esquiador.xy = (x[frame], y[frame])
        return linea_trayectoria, esquiador

    def on_animation_end():
        btn_simular.config(state=tk.NORMAL)

    ani = FuncAnimation(fig, actualizar, frames=len(t), interval=0.5, blit=True, repeat=False)
    ventana.after(len(t) * 10, on_animation_end)

    canvas.draw()

    distancia = x_land - x0
    label_resultado.config(
        text=f"⛷️ Distancia: {distancia:.2f} m\n🏆 Mejor ángulo: {mejor_ang:.2f}° (alcanzaría {mejor_dist:.2f} m)"
    )


# --- Ventana principal ---
ventana = tk.Tk()
ventana.title("Simulador de Salto de Esquí Animado")

# frame de controles
frame = ttk.Frame(ventana, padding=10)
frame.pack(side=tk.LEFT, fill=tk.Y)

ttk.Label(frame, text="Velocidad inicial (m/s):").grid(column=0, row=0, sticky="w")
entry_velocidad = ttk.Entry(frame)
entry_velocidad.grid(column=1, row=0)
entry_velocidad.insert(0, "25")

ttk.Label(frame, text="Ángulo (grados):").grid(column=0, row=1, sticky="w")
entry_angulo = ttk.Entry(frame)
entry_angulo.grid(column=1, row=1)
entry_angulo.insert(0, "22.8")

ttk.Label(frame, text="Pendiente (m, negativa):").grid(column=0, row=2, sticky="w")
entry_pendiente = ttk.Entry(frame)
entry_pendiente.grid(column=1, row=2)
entry_pendiente.insert(0, "1")

ttk.Label(frame, text="Altura (m):").grid(column=0, row=3, sticky="w")
entry_altura = ttk.Entry(frame)
entry_altura.grid(column=1, row=3)
entry_altura.insert(0, "20")

btn_simular = ttk.Button(frame, text="Saltar", command=simular_salto)
btn_simular.grid(column=0, row=4, columnspan=2, pady=10)

label_resultado = ttk.Label(frame, text="")
label_resultado.grid(column=0, row=5, columnspan=2)

# frame para la gráfica
frame_grafica = ttk.Frame(ventana)
frame_grafica.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# incrustar la figura en Tkinter
canvas = FigureCanvasTkAgg(fig, master=frame_grafica)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

ventana.mainloop()
