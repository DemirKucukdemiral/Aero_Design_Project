import numpy as np

from Data import Launcher_Data

class Launcher:
    def __init__(self):
        self.data = Launcher_Data()
        self.time = 0
        self.total_mass = self.data.total_mass

    def Thrust_to_weight(self, phase: str):
        for p in self.data.phases:
            if p["name"] == phase:
                phase_info = p
                break

        total_thrust_sl = 0
        for engine_name in phase_info["active_engine"]:
            stg = self.data.stages[engine_name]
            total_thrust_sl += stg.thrust_sl * stg.number

        thrust_to_weight = total_thrust_sl / (self.total_mass * self.data.gravity)
        return thrust_to_weight
    
    def Mass_flow_rate(self, phase: str):
        for p in self.data.phases:
            if p["name"] == phase:
                phase_info = p
                break

        total_mass_flow_rate = 0
        for engine_name in phase_info["active_engine"]:
            stg = self.data.stages[engine_name]
            total_mass_flow_rate += stg.thrust_sl / (stg.Isp * self.data.gravity) * stg.number

        return total_mass_flow_rate

