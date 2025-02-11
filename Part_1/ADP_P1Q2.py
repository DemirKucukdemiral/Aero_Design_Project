#QUESTION 2: Analysis of the Peagasus XL Launch System

import math

###Structural Efficiencies:

sigma1 = (1369+1000) / (16383+1000) #Stage 1 
print ("Structural Efficiency of Stage 1:" , round (sigma1, 4))

sigma2 = (391/4306) #Stage 2 
print ("Structural Efficiency of Stage 2:" , round (sigma2, 4))

sigma3 = (102.1/872.3) #Stage 3 
print ("Structural Efficiency of Stage 2:" , round (sigma3, 4))

###Payload Fractions:

L1 = (443+872.3+4306) / (16383+1000) #Stage 1 
print ("Payload Fraction of Stage 1:" , round (L1, 4))

L2 = (443+872.3) / 4306 #Stage 2
print ("Payload Fraction of Stage 2:" , round (L2, 4))

L3 = 443/872.3 #Stage 3
print ("Payload Fraction of Stage 3:" , round (L3, 4))

###Average propellent mass-flow rates:

massflow1 = 15014/68.6 #Stage 1 
print ("Average propellant mass-flow rate for Stage 1:" , round (massflow1, 4), "kg/s")

massflow2 = 3915/71 #Stage 2
print ("Average propellant mass-flow rate for Stage 2:" , round (massflow2, 4) ,"kg/s")

massflow3 = 770.6/67 #Stage 3
print ("Average propellant mass-flow rate for Stage 3:" , round (massflow3, 4) ,"kg/s")

###Estimation of the exhaust gas velocities:

Ve1 = 726000/massflow1 #Stage 1
print ("Estimation of stage 1 exhaust gas velocity:" , round (Ve1, 4) ,"m/s")

Ve2 = 158000/massflow2 #Stage 2
print ("Estimation of stage 2 exhaust gas velocity:" , round (Ve2, 4) ,"m/s")

Ve3 = 32700/massflow3 #Stage 3
print ("Estimation of stage 3 exhaust gas velocity:" , round (Ve3, 4) ,"m/s")

#Horizontal vaccum conditions are assumed
#The effect of jettisoning has been ignored

launch_mass_total= 16383+1000+4306+872.3+443

deltaV1 = (295*9.81)*math.log(launch_mass_total/(launch_mass_total-15014)) #Stage 1 speed increase 
print ("Stage 1 speed increase :" , round (deltaV1, 4) ,"m/s")

launch_mass_2 = 4306+872.3+443

deltaV2 = (289*9.81)*math.log(launch_mass_2/(launch_mass_2-3915)) #Stage 2 speed increase
print ("Stage 2 speed increase :" , round (deltaV2, 4) ,"m/s")

launch_mass_3 = 872.3+443

deltaV3 = (287*9.81)*math.log(launch_mass_3 /(launch_mass_3-770.2)) #Stage 3 speed increase 
print ("Stage 3 speed increase :" , round (deltaV3, 4) ,"m/s")

deltaV_total = deltaV1 + deltaV2 + deltaV3 #Speed increase from all stages:
print ("Total ΔV:" , round (deltaV_total, 4) ,"m/s")