import numpy as np

GRAVITY = 9.81  

class Stage:
    def __init__(self, name, dry_mass, prop_mass, Isp, delta_v):

        self.name      = name
        self.dry_mass  = dry_mass
        self.prop_mass = prop_mass
        self.Isp       = Isp
        self.delta_v   = delta_v
        stage_total_mass   = self.dry_mass + self.prop_mass
        self.struct_eff    = self.dry_mass / stage_total_mass if stage_total_mass > 0 else 0.0

stages = [
    Stage(name="Booster", dry_mass=45000, prop_mass=800000, Isp=327, delta_v=3000),
    Stage(name="Core",    dry_mass=31500, prop_mass=450000, Isp=338, delta_v=4000),
    Stage(name="Upper",   dry_mass=15100, prop_mass=60000, Isp=410, delta_v=2200)
]

payload_mass = 10000  

current_mass = payload_mass + sum(stg.dry_mass + stg.prop_mass for stg in stages)
print(f"Initial total mass at liftoff = {current_mass:.1f} kg")

for i, stage in enumerate(stages):
    print(f"\n--- Stage {i+1}: {stage.name} ---")

    print(f"Structural efficiency = {stage.struct_eff:.3f} "
          f"(dry={stage.dry_mass:.1f} / total={stage.dry_mass + stage.prop_mass:.1f})")
    
    m0 = current_mass

    ideal_mass_ratio = np.exp(stage.delta_v / (stage.Isp * GRAVITY))
    mf_ideal = m0 / ideal_mass_ratio


    if (m0 - mf_ideal) > stage.prop_mass:
        print("Warning: not enough propellant to provide the full delta_v!")

        mass_lost = stage.prop_mass
        mf_actual = m0 - mass_lost
        actual_dv = stage.Isp * GRAVITY * np.log(m0 / mf_actual)
        print(f"Stage can only deliver {actual_dv:.1f} m/s instead of {stage.delta_v} m/s.")
    else:
        mf_actual = mf_ideal
        mass_lost = m0 - mf_actual
    
    prop_burned = mass_lost

    print(f"Stage start mass (m0)  = {m0:.1f} kg")
    print(f"Propellant burned      = {prop_burned:.1f} kg (of {stage.prop_mass:.1f} available)")
    

    mass_after_drop = mf_actual - stage.dry_mass
    if mass_after_drop < 0:
        print("Error: negative rocket mass after dropping stage. Check your stage data!")
        mass_after_drop = 0
    
    current_mass = mass_after_drop
    print(f"Dropping stage dry mass => {stage.dry_mass:.1f} kg")
    print(f"Mass after dropping    = {current_mass:.1f} kg")

print(f"\nFinal rocket mass after all stages = {current_mass:.1f} kg")
print(f"Desired payload mass               = {payload_mass:.1f} kg")
