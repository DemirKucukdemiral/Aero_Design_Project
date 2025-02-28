###===--------------------------------------------===###
# Script:        ADP_P1Q1.py
# Authors:       Demir Kucukdemiral 2883935K, Charikleia Nikou 2881802N, Cameron Norrington 2873038N, Adam Burns 2914690B, Ben Maconnachie 2911209M, Jeremi Rozanski 2881882R
# Created on:    2025-02-08
# Last Modified: 2025-02-08
# Description:   Analysis of the structural efficiency of a Ariane 5
# Version:       1.0
###===--------------------------------------------===###    

#QUESTION 1: 

import math

#Launch masses:
launch_mass_LEO =  184700 + (2*268000) + 19440 + 500 + 2000 +21000 
launch_mass_GTO =  184700 + (2*268000) + 19440 + 500 + 2000 + 10500 

launch_thrust = 960000 + (2*6470000) 

#Thrust to weight ratios
thrust_to_weight_LEO = ((launch_thrust)/((launch_mass_LEO)*9.81)) #Thrust to weight 
thrust_to_weight_GTO = ((launch_thrust)/((launch_mass_GTO)*9.81))

#Structural efficiencies:
sigma_core =14700/184700 
sigma_upper = 4540/19440 
sigma_srb = 30200 / 268000 

#Mass flow rates:
mass_flow_srb = (2*237800)/130
mass_flow_core = 170000 /540 

v_1 = (launch_thrust)/((mass_flow_core)+(mass_flow_srb)) #Exhuast gas vel for 1st stage
 
prop_1 = (mass_flow_core + mass_flow_srb)* 130 #Propellant used in 1st stage 
deltaV1_LEO = v_1 * math.log(launch_mass_LEO/(launch_mass_LEO - prop_1)) #Speed inc from LEO 1st stage:

v_2 = 432*9.81 #Exhaust gas vel for 2nd stage

mass_2_LEO = 184700 - (mass_flow_core*130) +19440+ 2000+ 500 + 21000 #Initial mass for LEO 2nd stage 
mass_2B_LEO = 14700 + 19440 + 2000 +500 +21000 #Mass at LEO 2nd stage burnout

deltaV2_LEO = v_2 * math.log(mass_2_LEO/mass_2B_LEO) #Speed inc from LEO 2nd stage
v_3 = 446*9.81 #Exhaust gas vel for 3rd stage

mass_3_LEO = 19440 + 500 + 21000 #Initial mass for LEO 3rd stage
mass_3B_LEO = 4540 +500 +21000 #Mass at LEO 3rd stage burnout

deltaV3_LEO = v_3 * math.log(mass_3_LEO/ mass_3B_LEO) #Speed inc from LEO 3rd stage 
total_deltaV_LEO = deltaV1_LEO + deltaV2_LEO + deltaV3_LEO #Total speed increase for LEO all stages

deltaV1_GTO = v_1 * math.log(launch_mass_GTO/(launch_mass_GTO - prop_1)) #Spped inc from GTO 1st stage
mass_2_GTO = 184700 - (mass_flow_core*130) +19440+ 2000+ 500 + 10500 #Initial mass for GTO 2nd stage

mass_2B_GTO = 14700 + 19440 + 2000 + 500 + 10500 #Mass at GTO 2nd stage burnout

deltaV2_GTO = v_2 * math.log(mass_2_GTO/mass_2B_GTO) #Speed inc from GTO 2nd stage

mass_3_GTO = 19440 + 500 + 10500 #Initial mass for GTO 3rd stage
mass_3B_GTO = 4540 + 500 + 10500 #Mass at GTO 3rd stage burnout

deltaV3_GTO = v_3 * math.log(mass_3_GTO/mass_3B_GTO) #Speed inc from GTO 3rd stage

total_deltaV_GTO = deltaV1_GTO + deltaV2_GTO + deltaV3_GTO #Total speed increase for GTO all stages


print ("Q1a.Thrust-weight ratio at lift-off for max LEO: ",thrust_to_weight_LEO)
print ("Q1b.Thrust-weight ratio at lift-off for max GTO: ",thrust_to_weight_GTO)

print ("Q1c.Structural efficiency of core stage: ",sigma_core)
print ("Q1d.Structural efficiency of upper stage: ", sigma_upper)
print ("Q1e.Structural efficiency of SRBs: ", sigma_srb)

print ("Q1f. speed inc for 1st stage LEO: ", deltaV1_LEO, "m/s")
print ("speed inc for 2nd stage LEO: ", deltaV2_LEO, "m/s")
print ("speed inc for 3rd stage LEO: ", deltaV3_LEO, "m/s")
print ("total speed inc LEO: ", total_deltaV_LEO, "m/s")

print ("Q1g. speed inc for 1st stage GTO: ", deltaV1_GTO, "m/s")
print ("speed inc for 2nd stage GTO: ", deltaV2_GTO, "m/s")
print ("speed inc for 3rd stage GTO: ", deltaV3_GTO, "m/s")
print ("total speed inc GTO: ", total_deltaV_GTO, "m/s")