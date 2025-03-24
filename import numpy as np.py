import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.integrate import solve_ivp

# === UAV Parameters ===
mass = 27000  # kg
g = 9.81  # m/s^2
rho = 1.225  # kg/m^3 (air density at sea level)
S = 10  # Wing area (m^2)
S_tail = 5  # Tail wing area (m^2)
Cd = 0.03  # Drag coefficient (main wing)
Cl_alpha = 0.1  # Lift coefficient per angle of attack (approximation)
l_tail = 20  # Tail moment arm (m)
Iyy = 100.0  # Moment of inertia (kg.m^2)
Cd0 = 0.05  # Parasitic drag coefficient
c = 2  # Mean aerodynamic chord (m)

# === Initial Conditions ===
altitude = 10000  # meters
V0 = 200.0  # Initial velocity (m/s)
theta0 = -5 * np.pi / 180  # Initial pitch angle (rad)
q0 = 0.0  # Initial pitch rate (rad/s)

def lift(V, alpha, S):
    return 0.5 * rho * V**2 * S * (Cl_alpha * alpha)

def drag(V, alpha, S):
    return 0.5 * rho * V**2 * S * (Cd0 + Cd * alpha**2)

def moment_coefficient(alpha_wb, i_t):
    C_M_ac_wb = -0.02  # Wing-body moment coefficient at aerodynamic center
    a_wb = -0.05  # Wing-body moment slope
    C_M_CoG = C_M_ac_wb + a_wb * alpha_wb + 0.1 * i_t  # Including tail deflection effect
    return C_M_CoG

# === Equations of Motion ===
def uav_dynamics(t, state):
    x, z, V, theta, q = state  # Extract states
    
    alpha_wb = theta   
    i_t = (-2 * np.pi / 180 )
    
    L_wing = lift(V, alpha_wb, S)
    D_wing = drag(V, alpha_wb, S)
    L_tail = lift(V, alpha_wb + i_t, S_tail)  # Tail wing lift
    D_tail = drag(V, alpha_wb + i_t, S_tail)  # Tail wing drag
    
    C_M_CoG = moment_coefficient(alpha_wb, i_t)
    M = 0.5 * rho * V**2 * S * C_M_CoG * c + L_tail * l_tail  # Adding tail contribution

    # Ensure UAV keeps moving forward by preventing stagnation
    Vx_dot = (-D_wing - D_tail)/mass + (L_wing + L_tail) * np.sin(alpha_wb)/mass
    Vz_dot = (-L_wing - L_tail) * np.cos(alpha_wb)/mass + (D_wing + D_tail) * np.sin(alpha_wb)/mass + g

    # Rotational Equations
    q_dot = M / Iyy
    theta_dot = q  # Pitch angle rate

    return [V*np.cos(theta), V*np.sin(theta), Vx_dot, theta_dot, q_dot]

# === Simulation ===
t_span = (0, 300)  # Simulate for 300 seconds
state0 = [0, altitude, V0, theta0, q0]  # Initial state

sol = solve_ivp(uav_dynamics, t_span, state0, t_eval=np.linspace(0, 300, 1000), method='RK45')

# === Extract Results ===
x = sol.y[0]  # Horizontal Position
z = sol.y[1]  # Altitude
V = sol.y[2]  # Velocity
theta = sol.y[3]  # Pitch Angle

# === Animation ===
fig, ax = plt.subplots(figsize=(10, 5))
ax.set_xlim(0, np.max(x) + 1000)
ax.set_ylim(0, np.max(z) + 500)
ax.set_xlabel("Distance (m)")
ax.set_ylabel("Altitude (m)")
ax.set_title("Fixed-Wing UAV Glide Simulation")

wing_span = 50  # Arbitrary scaling for visualization
uav, = ax.plot([], [], 'bo-', markersize=8, label="UAV")
path, = ax.plot([], [], 'r-', linewidth=1, label="Path")

def init():
    uav.set_data([], [])
    path.set_data([], [])
    return uav, path

def update(frame):
    x_pos, z_pos = x[frame], z[frame]
    theta_angle = theta[frame]
    
    x_uav = [x_pos - wing_span*np.cos(theta_angle), x_pos, x_pos + wing_span*np.cos(theta_angle)]
    z_uav = [z_pos - wing_span*np.sin(theta_angle), z_pos, z_pos + wing_span*np.sin(theta_angle)]
    
    uav.set_data(x_uav, z_uav)  # Update UAV position
    path.set_data(x[:frame], z[:frame])  # Draw flight path
    return uav, path

ani = animation.FuncAnimation(fig, update, frames=len(x), init_func=init, blit=True, interval=20)

plt.legend()
plt.grid()
plt.show()
