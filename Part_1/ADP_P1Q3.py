###===--------------------------------------------===###
# Script:       ADP_P1Q3.py
# Authors:      Demir Kucukdemiral 2883935K, Charikleia Nikou 2881802N, Cameron Norrington 2873038N, Adam Burns 2914690B, Ben Maconnachie 2911209M, Jeremi Rozanski 2881882R
# Created on:   2025-02-24
# Last Modified: 2025-02-24
# Description:  This script calculates the mass breakdown for a multi-stage rocket and finds the required Ve and structural efficiency to achieve a target payload mass.
# Version:      1.0
###===--------------------------------------------===###    

import numpy as np


class Launcher:
    def __init__(self, structural_efficiency=0.07, number_of_stages=2):

        self.Ve = 3400          # m/s
        self.total_mass = 200000  # kg 
        self.delta_v = 10000      # m/s 
        self.structural_efficiency = structural_efficiency
        self.number_of_stages = number_of_stages

        self.delta_v_per_stage = self.delta_v / self.number_of_stages
    
    def final_payload_mass(self, Ve=3400, structural_efficiency=0.07, verbose=True):  
        alpha = structural_efficiency / (1 - structural_efficiency)
        
        K = np.exp(self.delta_v_per_stage / Ve)
        current_m0 = self.total_mass
        
        for i in range(self.number_of_stages):
            m_after_burn = current_m0 / K
            m_propellant = current_m0 - m_after_burn
            m_structure = alpha * m_propellant
            
            if verbose:
                print(f"Stage {i+1} | m_prop = {m_propellant:.1f} kg, "
                      f"m_struct = {m_structure:.1f} kg")
            
            current_m0 = m_after_burn - m_structure
            if current_m0 <= 0:
                return 0.0

        return current_m0
    
    def optimal_Ve(self, target_payload):

        current_Ve = self.Ve
 
        payload = self.final_payload_mass(Ve=current_Ve, verbose=False)
        
        # Use a tiny tolerance to avoid infinite loop
        while abs(payload - target_payload) > 1e-3:
            payload = self.final_payload_mass(Ve=current_Ve, verbose=False)
            if payload >= target_payload:
                break

            current_Ve += 1

        print(f"Optimal Ve (approx) = {current_Ve} m/s (payload ~ {payload:.1f} kg)")

    def optimal_efficiency(self, target_payload):

        current_structure_efficiency = self.structural_efficiency
        current_Ve = self.Ve
        

        payload = self.final_payload_mass(Ve=current_Ve, structural_efficiency=current_structure_efficiency, verbose=False)
        
        while abs(payload - target_payload) > 1e-3:
            payload = self.final_payload_mass(Ve=current_Ve, structural_efficiency=current_structure_efficiency, verbose=False)
            if payload >= target_payload:
                break
            current_structure_efficiency -= 0.01

        print(f"Optimal structural efficiency (approx) = {current_structure_efficiency:.2f}"
              f" (payload ~ {payload:.1f} kg)")


if __name__ == "__main__":
    print('---------------------- efficiency = 0.07 ----- 2 stage--------------------')
    launcher = Launcher(structural_efficiency=0.07, number_of_stages=2)
    payload_2stage = launcher.final_payload_mass()
    print(f"\nFinal payload mass (2-stage, e=0.07, Ve=3400): {payload_2stage:.1f} kg")

    print()

    print('----------------------  Optimal Value Finder --------------------------------')
    launcher.optimal_Ve(6500)
    launcher.optimal_efficiency(6500)

    print()

    print('---------------------- efficiency = 0.07 ----- 3 stage--------------------')
    launcher = Launcher(structural_efficiency=0.07, number_of_stages=3)
    payload_2stage = launcher.final_payload_mass()
    print(f"\nFinal payload mass (3-stage, e=0.07, Ve=3400): {payload_2stage:.1f} kg")

    print()

    print('---------------------- efficiency = 0.08 ----- 3 stage--------------------')
    launcher = Launcher(structural_efficiency=0.08, number_of_stages=3)
    payload_2stage = launcher.final_payload_mass()
    print(f"\nFinal payload mass (3-stage, e=0.08, Ve=3400): {payload_2stage:.1f} kg")


