
###===--------------------------------------------===###
# Script:       main.py
# Authors:      Demir Kucukdemiral 2883935K, Charikleia Nikou 2881802N, 
#               Cameron Norrington 2873038N, Adam Burns 2914690B, 
#               Ben Maconnachie 2911209M, Jeremi Rozanski 2881882R
# Created on:   2025-02-28
# Last Modified: 2025-02-28
# Description:  optimal structural efficiency solver for a concpet launcher
# Version:      1.0
###===--------------------------------------------===###    


import numpy as np
from dataclasses import dataclass

"""
This script uses a dataclass to store the information about the stages 
of a launcher. The Launcher class uses this data to calculate the 
thrust-to-weight ratio and the final payload mass given some initial 
totoal mass, engine data, phase information and required final velocity.
"""

@dataclass
class Stage:
    name: str
    launch_mass: float
    Isp: float
    thrust_vac: float
    thrust_sl: float
    burn_time: float
    delta_v: float
    number: int
    structural_efficiency: float = 0.0

class Launcher_Data:
    def __init__(self):
        """
        Init function to declare or parameters, phases and stage informations
        also declares all engine informations.
        """
        self.gravity = 9.81

        self.mass_payload_1 = 21100  
        self.mass_payload_2 = 10010 

        self.lpb = Stage(
            name="Liquid Propellant Booster",
            launch_mass=513044.4 + 40257.5,   # was 110000 * 4
            Isp=363,                  
            thrust_vac=2279000 * 4,   
            thrust_sl=2279000 * 4,    
            burn_time=130,
            delta_v=3000,
            number=1
        )

        self.core_stage = Stage(
            name="Core Stage",
            launch_mass=265468.9 + 21705.0,   # was 300000
            Isp=283,            
            thrust_vac=3.6e6, 
            thrust_sl=3.6e6,  
            burn_time=540,       
            delta_v=4000,       
            number=1
        )

        self.upper_stage = Stage(
            name="Upper Stage",
            launch_mass=30000,    
            Isp=410,              
            thrust_vac=66700,    
            thrust_sl=0,          
            burn_time=500,        
            delta_v=4000,         
            number=1
        )


        self.stages = {
            "lpb":   self.lpb,
            "core":  self.core_stage,
            "upper": self.upper_stage
        }

       
        self.total_mass = (
            self.mass_payload_1
            + self.mass_payload_2
            + self.lpb.launch_mass * self.lpb.number
            + self.core_stage.launch_mass * self.core_stage.number
            + self.upper_stage.launch_mass * self.upper_stage.number
        )

        
        self.phases = [
            {
                "name": "lpb",
                "active_stages": ["lpb", "core", "upper"],
                "drop_stages":   ["lpb"],
                "jettison_fairing": False,
                "active_engine": ["lpb"]  
            },
            {
                "name": "core",
                "active_stages": ["core", "upper"],
                "drop_stages":   ["core"],
                "jettison_fairing": True, 
                "active_engine": ["core"]  
            },
            {
                "name": "upper",
                "active_stages": ["upper"],
                "drop_stages":   ["upper"],
                "jettison_fairing": False,
                "active_engine": ["upper"]  
            }
        ]

class Launcher:

    def __init__(self):
        self.data = Launcher_Data()
        
        self.time = 0
        self.total_mass = self.data.total_mass
        
        self.structural_efficiency = 0.07
        
        self.number_of_stages = 3

        self.phases = self.data.phases      
        self.stages = self.data.stages      

    def Thrust_to_weight(self, phase: str) -> float: 
        phase_info = None
        for p in self.phases:
            if p["name"] == phase:
                phase_info = p
                break
        if phase_info is None:
            raise ValueError(f"Invalid phase '{phase}' in Thrust_to_weight().")

        total_thrust_sl = 0.0
        for engine_name in phase_info["active_engine"]:
            stage_obj = self.stages[engine_name]
            total_thrust_sl += stage_obj.thrust_sl * stage_obj.number

        tw_ratio = total_thrust_sl / (self.total_mass * self.data.gravity)
        return tw_ratio
    

    def final_payload_mass(self, str_eff, verbose=True):
        current_m0 = self.total_mass  
        upper_stage_eff = 0.15  

        for phase in self.phases:
            active_stages = phase["active_stages"]
            
  
            stage_key = phase["drop_stages"][0]  
            stg = self.stages[stage_key]

       
            total_active_mass = sum(self.stages[s].launch_mass for s in active_stages)
            weighted_efficiency = sum(
                (self.stages[s].launch_mass / total_active_mass) * 
                (upper_stage_eff if s == "upper" else str_eff)
                for s in active_stages
            )

            alpha = weighted_efficiency / (1 - weighted_efficiency)
            
            Ve = stg.Isp * self.data.gravity
            K = np.exp(stg.delta_v / Ve)
            m_after_burn = current_m0 / K
            m_structure = alpha * (current_m0 - m_after_burn)

            if m_after_burn <= 0:
                return 0.0

            if verbose:
                print(f"Stage {stage_key} => Δv={stg.delta_v:.1f} m/s | "
                    f"m_propellant={current_m0 - m_after_burn:.1f} kg | "
                    f"m_structure={m_structure:.1f} kg")

            
            current_m0 = m_after_burn - m_structure

   
            if stage_key == "core":
                current_m0 -= self.data.mass_payload_1

            if current_m0 <= 0:
                return 0.0

        return current_m0  
    
    def optimal_efficiency(self, target_payload: float):
         
        current_eff =  0.99
        
        while current_eff > 0:
            payload = self.final_payload_mass(str_eff=current_eff, verbose=False)
            if payload >= target_payload:
                print(f"Found structural efficiency ~ {current_eff:.2f} => payload ~ {payload:.1f} kg")
                return
            current_eff -= 0.01
        
        print("Could not achieve the desired payload with the given model.")
            

if __name__ == "__main__":
    launcher = Launcher()
    
    tw_lpb = launcher.Thrust_to_weight("lpb")
    print(f"T/W ratio during LPB phase: {tw_lpb:.3f}")
    
    leftover = launcher.final_payload_mass(launcher.structural_efficiency, verbose=True)
    print(f"Final payload mass (default efficiency={launcher.structural_efficiency:.2f}) ~ {leftover:.1f} kg")

    print("\nSearching for an optimal structural efficiency to get desired payload...")
    launcher.optimal_efficiency(10000)


