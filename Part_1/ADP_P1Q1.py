
###===--------------------------------------------===###
# Script:       ADP_P1Q1.py
# Authors:       Demir Kucukdemiral 2883935K, Charikleia Nikou 2881802N, Cameron Norrington 2873038N, Ben Maconnachie 2911209M, Jeremi Rozanski 2881882R
# Created on:   2025-02-08
# Last Modified: 2025-02-08
# Description:  [Short description of the script]
# Version:      1.0
###===--------------------------------------------===###    


from dataclasses import dataclass
import numpy as np
import math

@dataclass
class Stage:
    name: str
    launch_mass: float      
    structural_mass: float  
    propellant_mass: float  
    Isp: float              
    thrust_vac: float      
    thrust_sl: float        
    burn_time: float       

class Ariane:
    def __init__(self):
        self.std_g = 9.81
        
        self.core_stage = Stage(
            name="Core Stage",
            launch_mass=184700,  
            structural_mass=14700,
            propellant_mass=170000,
            Isp=432,          
            thrust_vac=1390,     
            thrust_sl=960,        
            burn_time=540        
        )

        self.srb = Stage(
            name="Solid Rocket Booster",
            launch_mass=268000,
            structural_mass=30200,
            propellant_mass=237800,
            Isp=274.5,
            thrust_vac=6470, 
            thrust_sl=6470,    
            burn_time=130
        )

        self.upper_stage = Stage(
            name="Upper Stage",
            launch_mass=19440,
            structural_mass=4540,
            propellant_mass=14900,
            Isp=446,
            thrust_vac=62.7,
            thrust_sl=0,   
            burn_time=945
        )

        self.stages = {
            "core": self.core_stage,
            "srb": self.srb,
            "upper": self.upper_stage
        }

    def Thrust_to_weight(self, mass_payload):
        self.mass_payload = mass_payload
        TtoW = (self.srb.thrust_sl*2+self.core_stage.thrust_sl)/((self.upper_stage.launch_mass+self.core_stage.launch_mass+self.srb.launch_mass + self.mass_payload)*self.std_g)
        if TtoW <= 1:
            print("Insufficient thrust")
            
        print("Thrust to weight ratio is,", TtoW)

        return TtoW 
    
    def structural_eff(self, name : str):

        stage = self.stages[name]

        sigma = stage.structural_mass/(stage.launch_mass)

        print(f"The structural efficiency of {name} =", sigma)
        return sigma
    
    def mass_ratio(self, name:str, mass_payload):
        stage = self.stages[name]

        mass_ratio = (stage.launch_mass+mass_payload)/(stage.structural_mass+mass_payload)
        return mass_ratio
    
    def velocity_increase(self, name:str, mass_payload):
        stage = self.stages[name]

        mass_ratio = self.mass_ration(name, mass_payload)

        velocity = stage.Isp*self.std_g*math.log(mass_ratio)

        return velocity
    


if __name__ == "__main__":
    LEO_payload = 21000
    GTO_payload = 10500

    rocket = Ariane()
    rocket.Thrust_to_weight(LEO_payload)
    rocket.structural_eff("srb")

    


