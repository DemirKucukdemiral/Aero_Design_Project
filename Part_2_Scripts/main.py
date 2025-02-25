import numpy as np
from dataclasses import dataclass

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

class Launcher_Data:
    def __init__(self):
        self.gravity = 9.81
        
        # Example masses in kg
        self.mass_payload_1 = 21100  # might be the main payload
        self.mass_payload_2 = 10010  # maybe a secondary payload
        self.mass_fairing = 1000
        self.mass_adapter = 1000

        # --- Define Stages ---
        # Stage 1: Booster (LPB)
        self.lpb = Stage(
            name="Liquid Propellant Booster",
            launch_mass=200000 * 4,   # e.g. 5 segments combined
            Isp=282,                  # s
            thrust_vac=900000 * 4,    # total thrust in vacuum
            thrust_sl=900000 * 4,     # sea-level thrust
            burn_time=130,
            delta_v=3000,            # e.g. 3 km/s for the booster
            number=1
        )

        # Stage 2: Core
        self.core_stage = Stage(
            name="Core Stage",
            launch_mass=200000,   
            Isp=300,            
            thrust_vac=900000, 
            thrust_sl=900000,  
            burn_time=540,       
            delta_v=4000,       # e.g. 4 km/s to reach LEO
            number=1
        )

        # Stage 3: Upper
        self.upper_stage = Stage(
            name="Upper Stage",
            launch_mass=30000,    # total mass for the upper stage
            Isp=320,              # better vacuum performance
            thrust_vac=200000,    # smaller engine, purely vacuum
            thrust_sl=0,          # not used at sea level
            burn_time=500,        
            delta_v=4000,         # e.g. 4 km/s from LEO to GTO
            number=1
        )

        # Bundle them in a dictionary for lookups
        self.stages = {
            "lpb":   self.lpb,
            "core":  self.core_stage,
            "upper": self.upper_stage
        }

        # --- Compute total_mass ---
        self.total_mass = (
            self.mass_payload_1
            + self.mass_payload_2
            + self.lpb.launch_mass * self.lpb.number
            + self.core_stage.launch_mass * self.core_stage.number
            + self.upper_stage.launch_mass * self.upper_stage.number
        )

        # --- Define phases (3-stage flight) ---
        self.phases = [
            {
                "name": "lpb",
                "active_stages": ["lpb", "core", "upper"],
                "drop_stages":   ["lpb"],
                "jettison_fairing": False,
                "active_engine": ["lpb"]  # only boosters fire here
            },
            {
                "name": "core",
                "active_stages": ["core", "upper"],
                "drop_stages":   ["core"],
                "jettison_fairing": True, 
                "active_engine": ["core"]  # only core fires
            },
            {
                "name": "upper",
                "active_stages": ["upper"],
                "drop_stages":   ["upper"],
                "jettison_fairing": False,
                "active_engine": ["upper"]  # final stage to GTO
            }
        ]
class Launcher:

    def __init__(self):
        self.data = Launcher_Data()
        
        self.time = 0
        self.total_mass = self.data.total_mass
        
        # A default structural efficiency, e.g. 7% 
        self.structural_efficiency = 0.07
        
        # For 2-stage rocket
        self.number_of_stages = 3
        
        # Effective exhaust velocity for the rocket equation 
        self.Ve = self.data.lpb.Isp*9.81 # (m/s), example figure

        # For convenience, store references
        self.phases = self.data.phases      # from the data container
        self.stages = self.data.stages      # dictionary of Stage objects

    def Thrust_to_weight(self, phase: str) -> float:
        """
        Computes the thrust-to-weight ratio at sea level for a given phase name.
        """
        phase_info = None
        for p in self.phases:
            if p["name"] == phase:
                phase_info = p
                break
        if phase_info is None:
            raise ValueError(f"Invalid phase '{phase}' in Thrust_to_weight().")

        # Sum thrust_sl from all active engines
        total_thrust_sl = 0.0
        for engine_name in phase_info["active_engine"]:
            stage_obj = self.stages[engine_name]
            total_thrust_sl += stage_obj.thrust_sl * stage_obj.number

        # Weight = total mass * g
        tw_ratio = total_thrust_sl / (self.total_mass * self.data.gravity)
        return tw_ratio
    
    def final_payload_mass(self, structural_efficiency, Ve, verbose=True):
        alpha = structural_efficiency / (1 - structural_efficiency)
        current_m0 = self.total_mass  # total rocket mass at liftoff

        for stage_key in ["lpb", "core", "upper"]:
            stg = self.stages[stage_key]

            # 1. Rocket eq: M0/Mf = exp(DeltaV / Ve)
            K = np.exp(stg.delta_v / Ve)
            m_after_burn = current_m0 / K
            m_propellant = current_m0 - m_after_burn
            m_structure = alpha * m_propellant

            if verbose:
                print(f"Stage {stage_key} => dv={stg.delta_v:.1f} m/s | "
                    f"m_prop={m_propellant:.1f} kg | m_struct={m_structure:.1f} kg")

            # 2. Remove the structure for this stage
            current_m0 = m_after_burn - m_structure

            if stage_key == "core":
                current_m0 -= self.data.mass_payload_1
                
            if current_m0 <= 0:
                return 0.0

        return current_m0
    
    def optimal_efficiency(self, target_payload: float):

        current_eff = self.structural_efficiency
        
        while current_eff > 0:
            payload = self.final_payload_mass(Ve=self.Ve, structural_efficiency=current_eff, verbose=False)
            if payload >= target_payload:
                print(f"Found structural efficiency ~ {current_eff:.2f} => payload ~ {payload:.1f} kg")
                return
            current_eff -= 0.001
        
        print("Could not achieve the desired payload with the given model.")
            

if __name__ == "__main__":
    # Example usage
    launcher = Launcher()
    
    # 1) Thrust-to-weight in first (lpb) phase
    tw_lpb = launcher.Thrust_to_weight("lpb")
    print(f"T/W ratio during LPB phase: {tw_lpb:.3f}")

    # 2) Thrust-to-weight in second (core) phase
    tw_core = launcher.Thrust_to_weight("core")
    print(f"T/W ratio during Core phase: {tw_core:.3f}")
    
    # 3) Print out final payload mass with the default structural efficiency
    leftover = launcher.final_payload_mass(launcher.structural_efficiency, launcher.Ve, verbose=True)
    print(f"Final payload mass (default efficiency={launcher.structural_efficiency:.2f}) ~ {leftover:.1f} kg")

    # 4) Attempt to find a structural efficiency that yields 1000 kg leftover
    print("\nSearching for an optimal structural efficiency to get 1000 kg payload...")
    launcher.optimal_efficiency(10500)