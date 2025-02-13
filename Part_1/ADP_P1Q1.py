###===--------------------------------------------===###
# Script:        ADP_P1Q1.py
# Authors:       [Your Team]
# Created on:    2025-02-08
# Last Modified: 2025-02-08
# Description:   Demonstration of multi-stage rocket equation
# Version:       1.0
###===--------------------------------------------===###    

from dataclasses import dataclass
import math

@dataclass
class Stage:
    name: str
    launch_mass: float      # (wet mass) stage structural + propellant
    structural_mass: float  
    propellant_mass: float  
    Isp: float              
    thrust_vac: float      
    thrust_sl: float        
    burn_time: float
    number: int       
    
class Ariane:
    def __init__(self):
        self.std_g = 9.81
        self.mass_fairing = 2000
        self.mass_adapter = 500

        self.fairing_jettisoned = False

        # Define each stage data
        self.core_stage = Stage(
            name="Core Stage",
            launch_mass=184700,  
            structural_mass=14700,
            propellant_mass=170000,
            Isp=432,          
            thrust_vac=1_390_000,     
            thrust_sl=960_000,        
            burn_time=540,
            number=1        
        )

        self.srb = Stage(
            name="Solid Rocket Booster",
            launch_mass=268000,
            structural_mass=30200,
            propellant_mass=237800,
            Isp=274.5,
            thrust_vac=6_470_000, 
            thrust_sl=6_470_000,    
            burn_time=130,
            number=2
        )

        self.upper_stage = Stage(
            name="Upper Stage",
            launch_mass=19_440,
            structural_mass=4_540,
            propellant_mass=14_900,
            Isp=446,
            thrust_vac=62_700,
            thrust_sl=0,
            burn_time=945,
            number=1
        )

        self.stages = {
            "core":  self.core_stage,
            "srb":   self.srb,
            "upper": self.upper_stage
        }

        # Define the launch phases (assuming simple serial drop logic)
        self.phases = [
            {
                "name": "srb",
                "active_stages": ["srb", "core", "upper"],  # total mass at start
                "drop_stages":   ["srb"],                   # mass dropped at end
                "jettison_fairing": False,
                "Isp_stage": "srb",     
                "active_engine": ["srb", "core"]
            },
            {
                "name": "core",
                "active_stages": ["core", "upper"],         # total mass at start
                "drop_stages":   ["core"],                  # mass dropped at end
                "jettison_fairing": True,                   # fairing jettison
                "Isp_stage": "core",
                "active_engine": ["core"]
            },
            {
                "name": "upper",
                "active_stages": ["upper"],
                "drop_stages":   [],
                "jettison_fairing": False,
                "Isp_stage": "upper",
                "active_engine": ["upper"]
            }
        ]

        self.totalMass = self.__total_mass()

    def __total_mass(self):
        """
        Total rocket mass on the pad (all stages + fairing + adapter).
        """
        total = sum(stage.launch_mass * stage.number for stage in self.stages.values())
        total += self.mass_fairing + self.mass_adapter
        return total
    
    def Thrust_to_weight(self, mass_payload, phase: str):
        """
        T/W ratio at sea level for the given phase, summing the SL thrust
        of each engine active in that phase.
        """
        phase = phase.lower()
        # Find the relevant phase dictionary
        for p in self.phases:
            if p["name"] == phase:
                phase_info = p
                break

        # Sum the sea-level thrust of all active engines in that phase
        total_thrust_sl = 0
        for engine_name in phase_info["active_engine"]:
            stg = self.stages[engine_name]
            total_thrust_sl += stg.thrust_sl * stg.number

        # Weight = (rocket mass + payload) * g
        # We'll assume rocket mass = self.totalMass for T/W at liftoff,
        # or if you want a more exact approach, re-compute only the "active" mass. 
        # For demonstration, we use totalMass + payload:
        weight = (self.totalMass + mass_payload) * self.std_g
        ttw = total_thrust_sl / weight
        
        print(f"[{phase.upper()}] Thrust-to-weight ratio: {ttw:.3f}")
        return ttw

    def structural_eff(self, name: str):
        """
        Simple ratio: structural_mass / launch_mass (wet mass).
        """
        stage = self.stages[name]
        sigma = stage.structural_mass / stage.launch_mass
        print(f"The structural efficiency of {name} = {sigma:.4f}")
        return sigma

    def velocity_increase_phase(self, phase: str, mass_payload: float):
        """
        Computes delta-V for the given phase using:
          Δv = Isp * g * ln(M0 / Mf)
        Where:
          - M0 = sum of all active stages + payload + adapter + (fairing if not yet dropped)
          - Mf = M0 minus (drop_stages + fairing if jettisoned in this phase)
        """
        phase = phase.lower()
        if phase not in ["srb", "core", "upper"]:
            raise ValueError("Invalid phase name.")

        # Find phase info
        for p in self.phases:
            if p["name"] == phase:
                phase_info = p
                break

        # 1) Compute M0
        M0 = 0.0
        for stg_name in phase_info["active_stages"]:
            stg = self.stages[stg_name]
            M0 += stg.launch_mass * stg.number

        # Add payload + adapter
        M0 += mass_payload + self.mass_adapter

        # If we have NOT jettisoned fairing yet, include it in M0
        if not self.fairing_jettisoned:
            M0 += self.mass_fairing

        # 2) Compute Mf by removing the mass of dropped stages
        Mf = M0
        for dropped_stg_name in phase_info["drop_stages"]:
            dropped_stg = self.stages[dropped_stg_name]
            drop_mass = dropped_stg.launch_mass * dropped_stg.number
            Mf -= drop_mass

        # Also jettison fairing if indicated (and if not yet jettisoned)
        if phase_info["jettison_fairing"] and not self.fairing_jettisoned:
            Mf -= self.mass_fairing
            self.fairing_jettisoned = True

        # 3) Isp for this phase
        Isp = self.stages[phase_info["Isp_stage"]].Isp

        # 4) Rocket Equation

        if phase == "upper":
            Mf -= self.stages["upper"].propellant_mass

        dv = Isp * self.std_g * math.log(M0 / Mf)

        print(f"[{phase.upper()}] delta-v = {dv:,.1f} m/s   (M0={M0:,.1f} kg, Mf={Mf:,.1f} kg)")
        return dv


if __name__ == "__main__":
    LEO_payload = 21000
    GTO_payload = 10500

    rocket = Ariane()

    # Question 1, a) T/W with LEO payload, phase SRB
    rocket.Thrust_to_weight(LEO_payload, "srb")

    # Question 1, b) T/W with GTO payload, phase SRB
    rocket.Thrust_to_weight(GTO_payload, "srb")

    # Question 1, c) Structural efficiency of core
    rocket.structural_eff("core")

    # Question 1, d) Structural efficiency of upper
    rocket.structural_eff("upper")

    # Question 1, e) Structural efficiency of srb
    rocket.structural_eff("srb")

    # Question 1, f) Delta-v for each phase to LEO
    rocket.velocity_increase_phase("srb", LEO_payload)
    rocket.velocity_increase_phase("core", LEO_payload)
    rocket.velocity_increase_phase("upper", LEO_payload)

    # Question 1, g) Delta-v for each phase to GTO
    rocket.velocity_increase_phase("srb", GTO_payload)
    rocket.velocity_increase_phase("core", GTO_payload)
    rocket.velocity_increase_phase("upper", GTO_payload)