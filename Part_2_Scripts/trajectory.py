###===--------------------------------------------===###
# Script:        trajectory.py
# Authors:       Demir Kucukdemiral 2883935K, Charikleia Nikou 2881802N, Cameron Norrington 2873038N, Adam Burns 2914690B, Ben Maconnachie 2911209M, Jeremi Rozanski 2881882R
# Created on:    2025-04
# Last Modified: 2025-04
# Description:   Trajectory simulation of a rocket launch
# Version:       1.0
###===--------------------------------------------===###  

import numpy as np
import matplotlib.pyplot as plt


dt = 0.1
n_vertical = 900
n_gravity  = 10000
n_steps    = n_vertical + n_gravity


Tphase1_stage1 = 9.116e6*4  
M0_1_stage1    = 1.4016e6  
mdot1_stage1   = 10150      


Rearth = 6.371e6  


time  = np.zeros(n_steps)
vel   = np.zeros(n_steps)
velx  = np.zeros(n_steps)
velz  = np.zeros(n_steps)
xpos  = np.zeros(n_steps)
zpos  = np.zeros(n_steps)
gamma = np.zeros(n_steps)
acc   = np.zeros(n_steps)

gamma[0] = np.deg2rad(90.0)

acc[0] = Tphase1_stage1 / (M0_1_stage1 - mdot1_stage1 * time[0]) - 9.81


for k in range(1, n_vertical):
    time[k] = time[k-1] + dt

    velz[k] = velz[k-1] + acc[k-1]*dt
   
    velx[k] = 0.0
    
    vel[k]  = np.sqrt(velx[k]**2 + velz[k]**2)
    
    cur_mass = M0_1_stage1 - mdot1_stage1 * time[k]
    if cur_mass < 1e-6:

        cur_mass = 1e-6
        Tphase1_stage1 = 0.0
    
    acc[k] = (Tphase1_stage1 / cur_mass) - 9.81
    
    xpos[k] = 0.0
    zpos[k] = zpos[k-1] + velz[k-1]*dt + 0.5 * acc[k-1] * (dt**2)
   
    gamma[k] = gamma[k-1]

gamma[n_vertical - 1] = np.deg2rad(75.0)

t_staging = time[n_vertical - 1]

M0_2      = cur_mass 
mdot2     = 8218  
Tphase2   = 9.116e6*4    
m_dry_2   = 0.0 

        
for k in range(n_vertical, n_steps):
    
    if k == n_vertical + 200:
        M0_2      = 450e3     
        mdot2     = 2379     
        Tphase2   = 7.887e6    
        m_dry_2   = 100.3e3       
        
    time[k] = time[k-1] + dt
    
    dt_stage2 = time[k] - t_staging

    cur_mass_2 = M0_2 - mdot2 * dt_stage2
    
    if cur_mass_2 <= m_dry_2:
        cur_mass_2 = m_dry_2
        Tphase2 = 0.0

    thrust_acc_2 = Tphase2 / cur_mass_2
    
    vel[k] = (
        vel[k-1]
        + dt * (thrust_acc_2 - 9.81 * np.sin(gamma[k-1]))
    )
    
    velx[k] = vel[k] * np.cos(gamma[k-1])
    velz[k] = vel[k] * np.sin(gamma[k-1])
    
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
    
    if vel[k-1] > 1e-6:
        gamma[k] = (
            gamma[k-1]
            + vel[k]*np.cos(gamma[k-1]) * dt / (Rearth + zpos[k-1])
            - 9.81*np.cos(gamma[k-1]) * dt / vel[k-1]
        )
    else:
        gamma[k] = gamma[k-1]
    
    acc[k] = thrust_acc_2

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