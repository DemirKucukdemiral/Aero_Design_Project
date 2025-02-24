
###===--------------------------------------------===###
# Script:       ADP_P1Q3.py
# Authors:       Demir Kucukdemiral 2883935K, Charikleia Nikou 2881802N, Cameron Norrington 2873038N, Adam Burns 2914690B, Ben Maconnachie 2911209M, Jeremi Rozanski 2881882R
# Created on:   2025-02-24
# Last Modified: 2025-02-24
# Description:  This script calculates the mass breakdown for a multi-stage rocket and finds the required Ve and structural efficiency to achieve a target payload mass.
# Version:      1.0
###===--------------------------------------------===###    


import numpy as np
import scipy.optimize as opt

def rocket_equation(m0, mf, ve):
    return ve * np.log(m0 / mf)

def stage_mass_distribution(total_mass, delta_v, ve, structural_efficiency, num_stages=2):
    """
    Calculates the mass breakdown for a multi-stage rocket.
    """
    delta_v_stage = delta_v / num_stages  # Equal delta-V split between stages
    
    def compute_stage_masses(m_upper, delta_v_stage):
        mass_ratio = np.exp(delta_v_stage / ve)
        m0 = m_upper * mass_ratio
        mp = (m0 - m_upper) * (1 - structural_efficiency)
        ms = (m0 - m_upper) * structural_efficiency
        return m0, mp, ms
    
    def objective(payload_mass):
        if payload_mass <= 0 or payload_mass >= total_mass:
            return float('inf')  # Invalid payload mass
        
        try:
            masses = [payload_mass]
            for _ in range(num_stages):
                m0, _, _ = compute_stage_masses(masses[-1], delta_v_stage)
                masses.append(m0)
            
            if masses[-1] > total_mass:
                return float('inf')  # Stage mass exceeds total allowed mass
            
            return -payload_mass  # Maximize payload mass
        except:
            return float('inf')  # Invalid case
    
    result = opt.minimize_scalar(objective, bounds=(1, total_mass / 10), method='bounded')
    max_payload = result.x
    
    # Compute final stage mass breakdowns
    masses = [max_payload]
    stage_breakdown = []
    for _ in range(num_stages):
        m0, mp, ms = compute_stage_masses(masses[-1], delta_v_stage)
        masses.append(m0)
        stage_breakdown.append((m0, mp, ms))
    
    return max_payload, stage_breakdown

def find_required_ve(target_payload, total_mass, delta_v, structural_efficiency, num_stages=2):
    """
    Finds the required Ve to achieve a target payload mass.
    """
    def objective(ve):
        max_payload, _ = stage_mass_distribution(total_mass, delta_v, ve, structural_efficiency, num_stages)
        return abs(max_payload - target_payload)  # Minimize difference from target payload
    
    result = opt.minimize_scalar(objective, bounds=(3000, 6000), method='bounded')
    return result.x

def find_required_structural_efficiency(target_payload, total_mass, delta_v, ve, num_stages=2):
    """
    Finds the required structural efficiency to achieve a target payload mass.
    """
    def objective(structural_efficiency):
        max_payload, _ = stage_mass_distribution(total_mass, delta_v, ve, structural_efficiency, num_stages)
        return abs(max_payload - target_payload)  # Minimize difference from target payload
    
    result = opt.minimize_scalar(objective, bounds=(0.01, 0.2), method='bounded')
    return result.x

# Given parameters
total_mass = 200000  # kg
delta_v = 10000  # m/s
ve = 3400  # m/s
structural_efficiency = 0.07  # 7% structural mass
target_payload = 6500  # kg

# Part A: Two-stage rocket mass breakdown
max_payload, stage_breakdown = stage_mass_distribution(total_mass, delta_v, ve, structural_efficiency, num_stages=2)
print("Part A: Two-Stage Rocket")
print(f"Maximum Payload Mass: {max_payload:.2f} kg")
for i, (m0, mp, ms) in enumerate(stage_breakdown, 1):
    print(f"Stage {i} Mass: {m0:.2f} kg (Propellant: {mp:.2f} kg, Structure: {ms:.2f} kg)")

# Part B: Required Ve for target payload
required_ve = find_required_ve(target_payload, total_mass, delta_v, structural_efficiency, num_stages=2)
print(f"\nPart B: Required Ve to achieve {target_payload} kg payload: {required_ve:.2f} m/s")

# Part C: Required structural efficiency for target payload
required_structural_efficiency = find_required_structural_efficiency(target_payload, total_mass, delta_v, ve, num_stages=2)
print(f"\nPart C: Required Structural Efficiency to achieve {target_payload} kg payload: {required_structural_efficiency:.4f}")

# Part D: Three-stage rocket mass breakdown
max_payload, stage_breakdown = stage_mass_distribution(total_mass, delta_v, ve, structural_efficiency, num_stages=3)
print("\nPart D: Three-Stage Rocket")
print(f"Maximum Payload Mass: {max_payload:.2f} kg")
for i, (m0, mp, ms) in enumerate(stage_breakdown, 1):
    print(f"Stage {i} Mass: {m0:.2f} kg (Propellant: {mp:.2f} kg, Structure: {ms:.2f} kg)")

# Part E: Three-stage rocket with 8% structural efficiency
structural_efficiency = 0.08
max_payload, stage_breakdown = stage_mass_distribution(total_mass, delta_v, ve, structural_efficiency, num_stages=3)
print("\nPart E: Three-Stage Rocket with 8% Structural Efficiency")
print(f"Maximum Payload Mass: {max_payload:.2f} kg")
for i, (m0, mp, ms) in enumerate(stage_breakdown, 1):
    print(f"Stage {i} Mass: {m0:.2f} kg (Propellant: {mp:.2f} kg, Structure: {ms:.2f} kg)")