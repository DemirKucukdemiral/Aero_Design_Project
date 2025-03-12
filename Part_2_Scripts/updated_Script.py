
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
        Initi function to declare or parameters, phases and stage informations
        also declares all engine informations.
        """
        self.gravity = 9.81
        
        self.mass_payload_1 = 21100  
        self.mass_payload_2 = 10010 

        self.lpb = Stage(
            name="Liquid Propellant Booster",
            launch_mass=100000 * 4,   
            Isp=363,                  
            thrust_vac=2279000 * 4,   
            thrust_sl=2279000 * 4,    
            burn_time=130,
            delta_v=2700,
            number=1
        )

        self.core_stage = Stage(
            name="Core Stage",
            launch_mass=300000,   
            Isp=300,            
            thrust_vac=900000, 
            thrust_sl=900000,  
            burn_time=540,       
            delta_v=5000,       
            number=1
        )

        self.upper_stage = Stage(
            name="Upper Stage",
            launch_mass=10000,    
            Isp=410,              
            thrust_vac=66700,    
            thrust_sl=0,          
            burn_time=500,        
            delta_v= 2700,         
            number=1,
            structural_efficiency = 0.15
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
        
        self.structural_efficiency = 0.06
        
        self.number_of_stages = 3

        self.phases = self.data.phases      
        self.stages = self.data.stages      

    def Thrust_to_weight(self, phase: str) -> float: 
        #thrust to weight calculation (of the booster phase) using given paramaters
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
    
    #Final mass calculation using the given structural efficiency
    def final_payload_mass(self, structural_efficiency, verbose=True):
        """
        Calculates final remaining rocket mass after all stage burns,
        ensuring each stage's "launch_mass" is fully subtracted (propellant + structure).

        Manual override for upper stage efficiency is retained.
        """

        current_m0 = self.total_mass  # Start with full rocket mass

        for stage_key in ["lpb", "core", "upper"]:
            stg = self.stages[stage_key]
            g = self.data.gravity
            Ve = stg.Isp * g

            # Apply manual override for upper stage efficiency
            if stage_key == "upper":
                stage_efficiency = 0.15
            else:
                stage_efficiency = structural_efficiency  # Use default efficiency for other stages

            # Compute α based on structural efficiency
            alpha = stage_efficiency / (1 - stage_efficiency)

            # Compute propellant and structural mass
            m_stage_propellant = stg.launch_mass / (1.0 + alpha)
            m_stage_structure = stg.launch_mass - m_stage_propellant  # Ensures sum = launch_mass

            # Check if this stage can provide the needed Δv
            if (current_m0 - stg.launch_mass) <= 0:
                return 0.0  # If we don't have enough mass, mission fails

            dv_available = Ve * np.log(current_m0 / (current_m0 - stg.launch_mass))

            if dv_available < stg.delta_v:
                print(f"Stage {stage_key} cannot provide required Δv of {stg.delta_v} m/s "
                    f"(only {dv_available:.1f} m/s). Mission fail.")
                return 0.0  # If the stage does not provide enough Δv, we fail

            # Print stage details
            if verbose:
                print(f"Stage {stage_key} => dv_required={stg.delta_v:.1f} m/s | "
                    f"dv_avail={dv_available:.1f} m/s | "
                    f"m_prop={m_stage_propellant:.1f} kg | m_struct={m_stage_structure:.1f} kg")

            # Subtract stage's total mass (propellant + structure) from the total stack
            current_m0 -= stg.launch_mass  

            # Remove mass_payload_1 after the core stage
            if stage_key == "core":
                current_m0 -= self.data.mass_payload_1
                if current_m0 <= 0:
                    return 0.0

        # Remaining mass after all stages
        return current_m0
    
    def optimal_efficiency(self, target_payload: float): 
        #searching for the optimal structural efficiency until desired final mass is reached
        current_eff =  0.15
        
        while current_eff > 0:
            payload = self.final_payload_mass(structural_efficiency=current_eff, verbose=False)
            if payload >= target_payload:
                print(f"Found structural efficiency ~ {current_eff:.2f} => payload ~ {payload:.1f} kg")
                return
            current_eff -= 0.001
        
        print("Could not achieve the desired payload with the given model.")
            

if __name__ == "__main__":
    launcher = Launcher()
    
    tw_lpb = launcher.Thrust_to_weight("lpb")
    print(f"T/W ratio during LPB phase: {tw_lpb:.3f}")
    
    leftover = launcher.final_payload_mass(launcher.structural_efficiency, verbose=True)
    print(f"Final payload mass (default efficiency={launcher.structural_efficiency:.2f}) ~ {leftover:.1f} kg")

    print("\nSearching for an optimal structural efficiency to get desired payload...")
    launcher.optimal_efficiency(10000)
