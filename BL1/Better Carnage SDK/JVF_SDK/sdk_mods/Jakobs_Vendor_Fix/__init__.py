import unrealsdk
from unrealsdk.hooks import Type,add_hook, remove_hook
from unrealsdk.unreal import UObject, WrappedStruct, BoundFunction
from unrealsdk import logging
from mods_base import build_mod, hook, ENGINE, get_pc, SETTINGS_DIR 
from mods_base.options import BaseOption, BoolOption
from typing import Any

def obj(class_obj: UObject, obj_name: str) -> UObject:
    loaded_object = ENGINE.DynamicLoadObject(obj_name, class_obj, False)
    loaded_object.ObjectFlags |= 0x4000
    return loaded_object

def obj_temporary(class_name: str, obj_name: str) -> UObject:
    return ENGINE.DynamicLoadObject(obj_name, unrealsdk.find_class(class_name), False)

# one part to check if the mission is done or not
def get_mission_status(mission_name:str) -> int:
    player = get_pc()
    PlayThroughNumber = player.GetCurrentPlaythrough()
    in_mission = obj_temporary("MissionDefinition", mission_name)
    for mission in player.MissionPlaythroughData[PlayThroughNumber].MissionList:
        if mission.MissionDef == in_mission:
            return mission.Status
    return 0

@hook(hook_func="WillowGame.WillowGameInfo:PreCommitMapChange", hook_type=Type.PRE)
def FinalizedMapChange(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction):
    global PopulationOpportunity
    if args.NextMapName != "dlc1_island_p":
        return

    # Makes the jakobs claptrap more annoying by talking more often
    obj_temporary("SeqAct_Delay", "dlc1_island_p.TheWorld:PersistentLevel.Main_Sequence.Claptrap_Setup_Based_On_Missions.SeqAct_Delay_1").Duration = 40.0

    # Makes the ItemGrade into the custom ItemGrade, which gives the Jakobs-only pools
    PopulationOpportunity = obj_temporary("PopulationOpportunityPoint","dlc1_island_p.TheWorld:PersistentLevel.PopulationOpportunityPoint_5")
    PopulationOpportunity.PopulationDef = obj_temporary("PopulationDefinition","ugy_fjv_itemgrades.VendingMachine.dlc1_VendingMachine_Jakobs")

    # GameStageRegion changes for the Jakobs vendor to scale to your level just like the other vendors
    PopulationOpportunity.GameStageRegion = obj_temporary("WillowRegionDefinition","dlc1_PackageDefinition.DLC1.DLC1_Jakobs_Cove")

    # SeqAct_ApplyBehavior_1 = ReadyForFuse, SeqAct_ApplyBehavior_2 = NoFuse, SeqAct_ApplyBehavior_3 = On
    # The machine is actually being disabled AFTER loading via NoFuse Behavior always being applied
    # So instead of fighting it, just swap the behavior that it wants to apply
    status = get_mission_status("dlc1_missions.SideMissions.M_dlc1_FixJakobsVending")
    if status in (2,3,4):
        obj_temporary("SeqAct_ApplyBehavior", "dlc1_island_p.TheWorld:PersistentLevel.Main_Sequence.Missions.FixJakobsVending.SeqAct_ApplyBehavior_2").Behaviors[0].BehaviorSetName = "On"
        #obj_temporary("SeqAct_ApplyBehavior", "dlc1_island_p.TheWorld:PersistentLevel.Main_Sequence.Missions.FixJakobsVending.SeqAct_ApplyBehavior_1").Behaviors[0].BehaviorSetName = "On"
    return

build_mod(hooks=[FinalizedMapChange])
__version__: str
__version_info__: tuple[int, ...]
logging.info(f"Jakobs Vendors Fix Loaded: {__version__}, {__version_info__}")
