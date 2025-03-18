import unrealsdk

from pathlib import Path
from unrealsdk.hooks import Type
from unrealsdk.unreal import UObject, WrappedStruct, BoundFunction
from mods_base import hook, get_pc 
from mods_base.options import BaseOption, BoolOption
from mods_base import SETTINGS_DIR
from mods_base import build_mod
from unrealsdk import logging
import os

TEXT_MOD_FOLDER = "./Mods/BadTextModLoader/TextMods/"

setcommands = []
rsetcommands = []
bPatched = False
bPatched_volatile = False
Count = 0
current_obj = None

struct = unrealsdk.make_struct
wclass = unrealsdk.find_class

global EModifierType
EModifierType = unrealsdk.find_enum("EModifierType")

def obj(class_name: str, obj_name: str) -> UObject:
    obj = unrealsdk.find_object(class_name, obj_name)
    obj.ObjectFlags |= 0x4000
    return obj

# gd_weap_combat_shotgun.Barrel.Barrel_PartList

def patch():

        # Barrels as value thingies
    CarnageBarrel = obj("WeaponPartDefinition","gd_weap_combat_shotgun.Barrel.barrel3_Carnage")
    BoomStickBarrel = obj("WeaponPartDefinition","gd_weap_combat_shotgun.UniqueParts.BoomStick_barrel3_Carnage")
    JackalBarrel = obj("WeaponPartDefinition","dlc3_gd_weap_UniqueParts.CombatShotgun.barrel3_DahlJackal")

    # Stat Changes
        # Increase damage
    WeaponDamage = obj("AttributeDefinition","d_attributes.Weapon.WeaponDamage")
    CarnageBarrel.WeaponAttributeEffects[0].AttributeToModify = WeaponDamage
    CarnageBarrel.WeaponAttributeEffects[0].ModifierType = EModifierType.MT_Scale
    CarnageBarrel.WeaponAttributeEffects[0].BaseModifierValue.BaseValueConstant = 3.000000
        # BoomStick gets less because high fire rate
    BoomStickBarrel.WeaponAttributeEffects[3].AttributeToModify = WeaponDamage
    BoomStickBarrel.WeaponAttributeEffects[3].ModifierType = EModifierType.MT_Scale
    BoomStickBarrel.WeaponAttributeEffects[3].BaseModifierValue.BaseValueConstant = 2.750000
        # Jackal gets more because it's a pearl
    JackalBarrel.WeaponAttributeEffects[0].AttributeToModify = WeaponDamage
    JackalBarrel.WeaponAttributeEffects[0].ModifierType = EModifierType.MT_Scale
    JackalBarrel.WeaponAttributeEffects[0].BaseModifierValue.BaseValueConstant = 3.950000

    # Balancing
        # Increase spread (decrease accuracy) slightly to balance extra projectiles
    WeaponSpread = obj("AttributeDefinition","d_attributes.Weapon.WeaponSpread")
    CarnageBarrel.WeaponAttributeEffects[3].AttributeToModify = WeaponSpread
    CarnageBarrel.WeaponAttributeEffects[3].ModifierType = EModifierType.MT_Scale
    CarnageBarrel.WeaponAttributeEffects[3].BaseModifierValue.BaseValueConstant = -0.100000
        # Decrease BoomStick spread (increase accuracy) slightly
    BoomStickBarrel.WeaponAttributeEffects[6].AttributeToModify = WeaponSpread
    BoomStickBarrel.WeaponAttributeEffects[6].ModifierType = EModifierType.MT_Scale
    BoomStickBarrel.WeaponAttributeEffects[6].BaseModifierValue.BaseValueConstant = 0.500000
        # Jackal gets less nerfed accuracy since it's a pearl
    JackalBarrel.WeaponAttributeEffects[3].AttributeToModify = WeaponSpread
    JackalBarrel.WeaponAttributeEffects[3].ModifierType = EModifierType.MT_Scale
    JackalBarrel.WeaponAttributeEffects[3].BaseModifierValue.BaseValueConstant = -0.690000

        # Nerf BoomStick fire rate
    WeaponFireRate = obj("AttributeDefinition","d_attributes.Weapon.WeaponFireRate")
    BoomStickBarrel.WeaponAttributeEffects[1].AttributeToModify = WeaponFireRate
    BoomStickBarrel.WeaponAttributeEffects[1].ModifierType = EModifierType.MT_Scale
    BoomStickBarrel.WeaponAttributeEffects[1].BaseModifierValue.BaseValueConstant = -3.000000

    # Increase projectiles
        # x3 for Regular Carnage
    WeaponProjectiles = obj("AttributeDefinition","d_attributes.Weapon.WeaponProjectilesPerShot")
    CarnageBarrel.WeaponAttributeEffects[2].AttributeToModify = WeaponProjectiles
    CarnageBarrel.WeaponAttributeEffects[2].ModifierType = EModifierType.MT_PostAdd
    CarnageBarrel.WeaponAttributeEffects[2].BaseModifierValue.BaseValueConstant = 3.000000
        # x3 for BoomStick (Might change to x2?)
    BoomStickBarrel.WeaponAttributeEffects[5].AttributeToModify = WeaponProjectiles
    BoomStickBarrel.WeaponAttributeEffects[5].ModifierType = EModifierType.MT_PostAdd
    BoomStickBarrel.WeaponAttributeEffects[5].BaseModifierValue.BaseValueConstant = 3.000000
        # x3 for Jackal
    JackalBarrel.WeaponAttributeEffects[2].AttributeToModify = WeaponProjectiles
    JackalBarrel.WeaponAttributeEffects[2].ModifierType = EModifierType.MT_PostAdd
    JackalBarrel.WeaponAttributeEffects[2].BaseModifierValue.BaseValueConstant = 3.000000

    # Add acc4_Carnage to the shotgun accesory pool (broken)
    #obj("WeaponPartDefinition","gd_weap_combat_shotgun.Acc.Acc_PartList").ObjectFlags |= 0x4000
    #obj("WeaponPartListDefinition","gd_weap_combat_shotgun.Acc.Acc_PartList").WeightedParts.append(current_obj.WeightedParts[10])
    #obj("WeaponPartListDefinition","gd_weap_combat_shotgun.Acc.Acc_PartList").WeightedParts[-1].Part = #obj("WeaponPartDefinition","gd_weap_combat_shotgun.acc.acc4_Carnage")

    # Removes weird collision jank for the rockets
    obj("ProjectileDefinition","gd_weap_combat_shotgun.Rockets.rocket_mini").bUseAccurateCollision = False
    obj("ProjectileDefinition","dlc3_gd_weap_UniqueParts.CombatShotgun.projectile_JackalGrenade").bUseAccurateCollision = False
    # Makes the Carnage, BoomStick and Jackal bullets/projectiles faster
    obj("FiringModeDefinition","gd_weap_combat_shotgun.FiringModes.rocket_mini").Speed = 6000
    obj("FiringModeDefinition","gd_weap_combat_shotgun.FiringModes.FM_BoomStick_rocket").Speed = 6000
    obj("FiringModeDefinition","dlc3_gd_weap_UniqueParts.CombatShotgun.FM_grenade_mini").Speed = 7500
    obj("ProjectileDefinition","gd_weap_combat_shotgun.Rockets.rocket_mini").Speed = 6000
    obj("ProjectileDefinition","dlc3_gd_weap_UniqueParts.CombatShotgun.projectile_JackalGrenade").Speed = 7500


# Important loading stuff, activate when inventory is here
# If this does not work, save quitting and reloading once does work

@hook("Engine.WorldInfo:CommitMapChange")
def on_commit_map_change(_1, _2, _3, _4) -> None:
    patch()
    on_commit_map_change.disable()

def _on_enable() -> None:
  try:
    patch()
  except ValueError:
    pass


# Gets populated from `build_mod` below
__version__: str
__version_info__: tuple[int, ...]

build_mod(
    # These are defaulted
    # inject_version_from_pyproject=True, # This is True by default
    # version_info_parser=lambda v: tuple(int(x) for x in v.split(".")),
    # deregister_same_settings=True,      # This is True by default
    keybinds=[],
    hooks=[on_commit_map_change],
    commands=[],
    on_enable=_on_enable, # tell the mod factory to use my 'on_enable' function
    # Defaults to f"{SETTINGS_DIR}/dir_name.json" i.e., ./Settings/bl1_commander.json
    settings_file=Path(f"{SETTINGS_DIR}/BetterCarnageSDK.json"),
)

logging.info(f"Better Carnage SDK Loaded: {__version__}, {__version_info__}")
