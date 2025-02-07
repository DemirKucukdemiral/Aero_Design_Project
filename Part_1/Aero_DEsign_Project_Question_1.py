"""
Data for Ariane 5 Core (Main) Stage : launch mass = 184,700 kg, structural mass = 14,700 kg, propellant mass = 170,000 kg. Isp = 432s (in vacuum), thrust T = 1,390 kN (vacuum) or 960 kN at Sea Level. Burn time = 540s

Data for Ariane 5 Solid Rocket Booster (data for 1 of 2): launch mass = 268,000 kg, structural mass = 30,200 kg, propellant mass = 237,800 kg. Isp = 274.5s, thrust T = 6,470 kN (Sea Level). Burn time = 130s

Data for Ariane 5 Upper Stage (Cryogenic) : launch mass = 19,440 kg, structural mass = 4,540 kg, propellant mass = 14,900. Isp = 446s, thrust T = 62.7 kN. Burn time = 945s

"""
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
    

rocket = Ariane()

rocket.structural_eff("srb")

    


