from dataclasses import dataclass
from typing import List

@dataclass
class Stage:
    name: str
    launch_mass: float      
    Isp: float              
    thrust_vac: float      
    thrust_sl: float        
    burn_time: float
    number: int

class Launcher_Data:
    def __init__(self):   
        self.gravity = 9.81
        self.mass_payload_1 = 1000
        self.mass_payload_2 = 1000
        self.mass_fairing = 1000
        self.mass_adapter = 1000
        self.total_mass = self.mass_payload_1 + self.mass_payload_2 + self.mass_fairing + self.mass_adapter 
        + self.core_stage.launch_mass + (self.lpb.launch_mass * self.lpb.number)

        self.core_stage = Stage(
            name="Core Stage",
            launch_mass=100000,  
            Isp=432,          
            thrust_vac=1_390_000,     
            thrust_sl=960_000,        
            burn_time=540,
            number=1
        )

        self.srb = Stage(
            name="Liquid Proppelent Booster",
            launch_mass=268000,
            Isp=274.5,
            thrust_vac=6_470_000, 
            thrust_sl=6_470_000,    
            burn_time=130,
            number=4
        )


        self.phases = [
            {
                "name": "lpb",
                "active_stages": ["srb", "core", "upper"],  # total mass at start
                "drop_stages":   ["srb"],                   # mass dropped at end
                "jettison_fairing": False,
                "Isp_stage": "srb",     
                "active_engine": ["srb"]
            },
            {
                "name": "core",
                "active_stages": ["core", "upper"],         # total mass at start
                "drop_stages":   ["core"],                  # mass dropped at end
                "jettison_fairing": True,                   # fairing jettison
                "Isp_stage": "core",
                "active_engine": ["core"]
            }
   
        ]
