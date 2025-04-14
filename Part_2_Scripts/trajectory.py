import numpy as np
import matplotlib.pyplot as plt

# Time step (seconds) and number of steps
dt = 0.1
n_vertical = 900
n_gravity  = 10000
n_steps    = n_vertical + n_gravity

# ----- STAGE 1 PARAMETERS ------
Tphase1_stage1 = 9.116e6*4  # Thrust, N
M0_1_stage1    = 1.4016e6    # Initial total mass, kg
mdot1_stage1   = 10150       # Mass flow rate, kg/s

# Earth radius (for flight-path angle update)
Rearth = 6.371e6  # meters

# Arrays to store data
time  = np.zeros(n_steps)
vel   = np.zeros(n_steps)
velx  = np.zeros(n_steps)
velz  = np.zeros(n_steps)
xpos  = np.zeros(n_steps)
zpos  = np.zeros(n_steps)
gamma = np.zeros(n_steps)
acc   = np.zeros(n_steps)

# --------------------------
# INITIAL CONDITIONS
# --------------------------
# Start with rocket pointed vertically:
gamma[0] = np.deg2rad(90.0)

# Initial net acceleration:
#   a = T/m - g
acc[0] = Tphase1_stage1 / (M0_1_stage1 - mdot1_stage1 * time[0]) - 9.81

# --------------------------
#  1) STAGE 1: VERTICAL FLIGHT
# --------------------------
for k in range(1, n_vertical):
    time[k] = time[k-1] + dt
    # Update velocity in vertical direction
    velz[k] = velz[k-1] + acc[k-1]*dt
    # Horizontal velocity remains zero
    velx[k] = 0.0
    # Overall velocity magnitude
    vel[k]  = np.sqrt(velx[k]**2 + velz[k]**2)
    
    # Current mass of stage 1
    cur_mass = M0_1_stage1 - mdot1_stage1 * time[k]
    if cur_mass < 1e-6:
        # If we somehow run out of mass, clamp it and set thrust to 0
        cur_mass = 1e-6
        Tphase1_stage1 = 0.0
    
    # Net acceleration ignoring gravity: T/m
    acc[k] = (Tphase1_stage1 / cur_mass) - 9.81
    
    # Update positions
    xpos[k] = 0.0
    zpos[k] = zpos[k-1] + velz[k-1]*dt + 0.5 * acc[k-1] * (dt**2)
    # Flight-path angle remains 90 deg in vertical phase
    gamma[k] = gamma[k-1]

# Force a slight tilt before second stage:
gamma[n_vertical - 1] = np.deg2rad(75.0)

# Record the time at staging
t_staging = time[n_vertical - 1]


M0_2      = cur_mass   # mass at start of stage 2 (including propellant)
mdot2     = 8218   # new mass flow rate, kg/s
Tphase2   = 9.116e6*4      # new thrust, N
m_dry_2   = 0.0 

        
for k in range(n_vertical, n_steps):
    
    if k == n_vertical + 200:
        M0_2      = 450e3     # mass at start of stage 2 (including propellant)
        mdot2     = 2379     # new mass flow rate, kg/s
        Tphase2   = 7.887e6     # new thrust, N
        m_dry_2   = 100.3e3       # example: a "dry mass" for stage 2, to avoid negative mass
        
    time[k] = time[k-1] + dt
    
    # Time since stage 2 ignition
    dt_stage2 = time[k] - t_staging
    
    # Current mass in stage 2
    cur_mass_2 = M0_2 - mdot2 * dt_stage2
    
    # If stage 2 is burnt out, clamp mass to dry mass and set thrust = 0
    if cur_mass_2 <= m_dry_2:
        cur_mass_2 = m_dry_2
        Tphase2 = 0.0
        # Optionally break out if you want to end the simulation
        # break
    
    # Thrust-based acceleration ignoring gravity
    thrust_acc_2 = Tphase2 / cur_mass_2
    
    # 1) Update total velocity with net forward accel minus gravity vertical
    vel[k] = (
        vel[k-1]
        + dt * (thrust_acc_2 - 9.81 * np.sin(gamma[k-1]))
    )
    
    # 2) Decompose into x and z
    velx[k] = vel[k] * np.cos(gamma[k-1])
    velz[k] = vel[k] * np.sin(gamma[k-1])
    
    # 3) Update positions
    xpos[k] = (
        xpos[k-1]
        + velx[k-1]*dt
        + 0.5 * thrust_acc_2 * np.cos(gamma[k-1]) * (dt**2)
    )
    zpos[k] = (
        zpos[k-1]
        + velz[k-1]*dt
        + 0.5 * (thrust_acc_2*np.sin(gamma[k-1]) - 9.81) * (dt**2)
    )
    
    # 4) Update gamma using standard gravity-turn logic (if v>0)
    if vel[k-1] > 1e-6:
        gamma[k] = (
            gamma[k-1]
            + vel[k]*np.cos(gamma[k-1]) * dt / (Rearth + zpos[k-1])
            - 9.81*np.cos(gamma[k-1]) * dt / vel[k-1]
        )
    else:
        gamma[k] = gamma[k-1]
    
    # Store the net thrust-based acceleration
    acc[k] = thrust_acc_2

# --------------------------
#  PLOTTING
# --------------------------
fig, ax1 = plt.subplots()

color1 = "tab:blue"
ax1.set_xlabel("Time (s)")
ax1.set_ylabel("Altitude (m)", color=color1)
line1 = ax1.plot(time, zpos, color=color1, label="Altitude")
ax1.tick_params(axis='y', labelcolor=color1)

ax2 = ax1.twinx()
color2 = "tab:red"
ax2.set_ylabel("Velocity (m/s)", color=color2)
line2 = ax2.plot(time, vel, color=color2, label="Velocity")
ax2.tick_params(axis='y', labelcolor=color2)

ax3 = ax1.twinx()
color3 = "tab:green"
ax3.spines["right"].set_position(("axes", 1.2))
ax3.set_ylabel("Flight-path angle (deg)", color=color3)
line3 = ax3.plot(time, np.rad2deg(gamma), color=color3, label="Gamma (deg)")
ax3.tick_params(axis='y', labelcolor=color3)

# Combine legend entries
lines = line1 + line2 + line3
labels = [l.get_label() for l in lines]
ax1.legend(lines, labels, loc="upper left")

plt.title("Altitude, Velocity, Flight-Path Angle")
plt.show()

plt.figure()
plt.plot(xpos, zpos)
plt.title("Trajectory")
plt.xlabel("X Position (m)")
plt.ylabel("Z Position (m)")
plt.grid()  
plt.show()