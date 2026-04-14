import unrealsdk

from pathlib import Path
from unrealsdk.hooks import Type
from unrealsdk.unreal import UObject, WrappedStruct, BoundFunction
from mods_base import build_mod, hook, get_pc, SETTINGS_DIR
from mods_base.options import BaseOption, BoolOption
from typing import Any
from unrealsdk import logging
import os

# To anyone reading this: I know my code sucks. I'm a newbie at this stuff :) -ugyuu
    # FYI: Carnage rockets and the Jackal deal Grenade Damage.
    # The Bad Ass & Warmonger class mods (Brick), the Sharpshooter class mod (Mordecai), Grenadier skill (Roland) all boost Grenade Damage.

global EModifierType
EModifierType = unrealsdk.find_enum("EModifierType")

bPatched = False
bPatched_unstable = False
Count = 0

def obj(class_obj: UObject, obj_name: str) -> UObject:
    current_obj = ENGINE.DynamicLoadObject(obj_name, class_obj, False)
    current_obj.ObjectFlags |= 0x4000
    return current_obj

def patch():

    # Barrels as value thingies
    CarnageBarrel = obj("WeaponPartDefinition","gd_weap_combat_shotgun.Barrel.barrel3_Carnage")
    JackalBarrel = obj("WeaponPartDefinition","dlc3_gd_weap_UniqueParts.CombatShotgun.barrel3_DahlJackal")

    # Stat Changes
        # Increase damage
    WeaponDamage = obj("AttributeDefinition","d_attributes.Weapon.WeaponDamage")
    CarnageBarrel.WeaponAttributeEffects[0].AttributeToModify = WeaponDamage
    CarnageBarrel.WeaponAttributeEffects[0].ModifierType = EModifierType.MT_Scale
    CarnageBarrel.WeaponAttributeEffects[0].BaseModifierValue.BaseValueConstant = 3.0
        # Jackal gets more damage because it's a pearl
    JackalBarrel.WeaponAttributeEffects[0].AttributeToModify = WeaponDamage
    JackalBarrel.WeaponAttributeEffects[0].ModifierType = EModifierType.MT_Scale
    JackalBarrel.WeaponAttributeEffects[0].BaseModifierValue.BaseValueConstant = 3.9
        # Nerf the Jackal's fire rate since it's too fast otherwise
    JackalBarrel.WeaponAttributeEffects.emplace_struct(AttributeToModify = WeaponFireRate,ModifierType = EModifierType.MT_Scale,)
    JackalBarrel.WeaponAttributeEffects[-1].BaseModifierValue.BaseValueConstanct = 0.4
    JackalBarrel.WeaponAttributeEffects[-1].BaseModifierValue.BaseValueScaleConstant = 1
    # or
    #(bvc := JackalBarrel.WeaponAttributeEffects[-1].BaseModifierValue).BaseValueConstanct = 0.4
    #bvc.BaseValueScaleConstant = 1

    # Balancing
        # Increase spread (decrease accuracy) to balance extra projectiles
    WeaponSpread = obj("AttributeDefinition","d_attributes.Weapon.WeaponSpread")
    CarnageBarrel.WeaponAttributeEffects[3].AttributeToModify = WeaponSpread
    CarnageBarrel.WeaponAttributeEffects[3].ModifierType = EModifierType.MT_Scale
    CarnageBarrel.WeaponAttributeEffects[3].BaseModifierValue.BaseValueConstant = 0.3
        # Jackal gets less nerfed accuracy, since it's a pearl
    JackalBarrel.WeaponAttributeEffects[3].AttributeToModify = WeaponSpread
    JackalBarrel.WeaponAttributeEffects[3].ModifierType = EModifierType.MT_Scale
    JackalBarrel.WeaponAttributeEffects[3].BaseModifierValue.BaseValueConstant = -0.3

    # Increase projectiles
        # x3 for Regular Carnage
    WeaponProjectiles = obj("AttributeDefinition","d_attributes.Weapon.WeaponProjectilesPerShot")
    CarnageBarrel.WeaponAttributeEffects[2].AttributeToModify = WeaponProjectiles
    CarnageBarrel.WeaponAttributeEffects[2].ModifierType = EModifierType.MT_PostAdd
    CarnageBarrel.WeaponAttributeEffects[2].BaseModifierValue.BaseValueConstant = 3.0
        # x3 for Jackal
    JackalBarrel.WeaponAttributeEffects[2].AttributeToModify = WeaponProjectiles
    JackalBarrel.WeaponAttributeEffects[2].ModifierType = EModifierType.MT_PostAdd
    JackalBarrel.WeaponAttributeEffects[2].BaseModifierValue.BaseValueConstant = 3.0
    # FiringMode / Projectile changes
        # Removes collision jank for the rockets (not sure if it works)
    obj("ProjectileDefinition","gd_weap_combat_shotgun.Rockets.rocket_mini").bUseAccurateCollision = False
    obj("ProjectileDefinition","dlc3_gd_weap_UniqueParts.CombatShotgun.projectile_JackalGrenade").bUseAccurateCollision = False
        # Makes the Carnage and Jackal bullets/projectiles faster
    obj("FiringModeDefinition","gd_weap_combat_shotgun.FiringModes.rocket_mini").Speed = 6400
    obj("ProjectileDefinition","gd_weap_combat_shotgun.Rockets.rocket_mini").Speed = 6400
    obj("FiringModeDefinition","dlc3_gd_weap_UniqueParts.CombatShotgun.FM_grenade_mini").Speed = 7500
    ##TEST BOUNCES -- obviously this didn't work
    #obj("FiringModeDefinition","dlc3_gd_weap_UniqueParts.CombatShotgun.FM_grenade_mini").NumRicochets = 4
    #obj("ProjectileDefinition","dlc3_gd_weap_UniqueParts.CombatShotgun.projectile_JackalGrenade").Speed = 7500

    # Boomstick changes (executing these last in case it is not loaded by the game. Early experiments with hooks were buggy on BoomStick changes specifically)
    BoomStickBarrel = obj("WeaponPartDefinition","gd_weap_combat_shotgun.UniqueParts.BoomStick_barrel3_Carnage")
        # x3 projectiles (Maybe make the others x4 as this is still the best Carnage in most cases)
    BoomStickBarrel.WeaponAttributeEffects[5].AttributeToModify = WeaponProjectiles
    BoomStickBarrel.WeaponAttributeEffects[5].ModifierType = EModifierType.MT_PostAdd
    BoomStickBarrel.WeaponAttributeEffects[5].BaseModifierValue.BaseValueConstant = 3.0
        # Small damage buff
    BoomStickBarrel.WeaponAttributeEffects[3].AttributeToModify = WeaponDamage
    BoomStickBarrel.WeaponAttributeEffects[3].ModifierType = EModifierType.MT_Scale
    BoomStickBarrel.WeaponAttributeEffects[3].BaseModifierValue.BaseValueConstant = 2.0
        # Nerf BoomStick fire rate by a lot (but it's still very fast)
    WeaponFireRate = obj("AttributeDefinition","d_attributes.Weapon.WeaponFireRate")
    BoomStickBarrel.WeaponAttributeEffects[1].AttributeToModify = WeaponFireRate
    BoomStickBarrel.WeaponAttributeEffects[1].ModifierType = EModifierType.MT_Scale
    BoomStickBarrel.WeaponAttributeEffects[1].BaseModifierValue.BaseValueConstant = -1.5
        # Faster Boomstick projectile
    obj("FiringModeDefinition","gd_weap_combat_shotgun.FiringModes.FM_BoomStick_rocket").Speed = 6000


@hook("Engine.WorldInfo:IsMenuLevel", Type.PRE)
def OnGameStarted(obj:UObject, args:WrappedStruct, ret:Any, func:BoundFunction) -> None:
    global bPatched
    if bPatched is False:
        bPatched = True

@hook("Engine.WorldInfo:CommitMapChange", Type.POST)
def OnMapChanged(obj:UObject, args:WrappedStruct, ret:Any, func:BoundFunction) -> None:
    bPatched_unstable = False

# IDK what the purpose of adding 'bPatched_unstable' is here, but these 3 hooks seem to do what I want to do (apply changes right before loading into a map or save). Can't only have a def anyway, so it's there for some reason regardless

@hook("Engine.WorldInfo:PostBeginPlay", Type.POST)
def OnLevelLoaded(obj:UObject, args:WrappedStruct, ret:Any, func:BoundFunction) -> None:
    global bPatched_unstable
    global Count
    if Count >= 2:
        Count = 0
        if bPatched_unstable != True:
            bPatched_unstable = True

    else:
        Count = Count + 1

build_mod(hooks=[OnGameStarted, OnMapChanged, OnLevelLoaded])

