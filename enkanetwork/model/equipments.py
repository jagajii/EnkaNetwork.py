from pydantic import BaseModel, Field
from typing import Any, List

from ..enum import EquipmentsType, DigitType, EquipType
from ..json import Config
from ..utils import create_ui_path

class EquipmentsStats(BaseModel):
    prop_id: str = ""
    type: DigitType = DigitType.NUMBER
    name: str = ""
    value: int = 0

    def __init__(__pydantic_self__, **data: Any) -> None:
        super().__init__(**data)

        if "mainPropId" in data:
            __pydantic_self__.prop_id = str(data["mainPropId"])
            fight_prop = Config.HASH_MAP["fight_props"].get(str(data["mainPropId"]))
        else:
            __pydantic_self__.prop_id = str(data["appendPropId"])
            fight_prop = Config.HASH_MAP["fight_props"].get(str(data["appendPropId"]))

        if fight_prop:
            __pydantic_self__.name = fight_prop[Config.LANGS]

        if isinstance(data["statValue"], float):
            __pydantic_self__.type = DigitType.PERCENT

        __pydantic_self__.value = data["statValue"]


class EquipmentsDetail(BaseModel):
    """
        API Response
    """
    nameTextMapHash: str = ""
    setNameTextMapHash: str = ""

    """
        Custom data
    """
    name: str = "" # Get from name hash map
    artifactType: EquipType = EquipType.UNKNOWN # Type of artifact
    icon: str = "" 
    rarity: int = Field(0, alias="rankLevel")
    mainstats: EquipmentsStats = Field(None, alias="reliquaryMainstat")
    substats: List[EquipmentsStats] = []

    def __init__(__pydantic_self__, **data: Any) -> None:
        super().__init__(**data)

        if data["itemType"] == "ITEM_RELIQUARY": # AKA. Artifact 
            __pydantic_self__.name = Config.HASH_MAP["artifacts"].get(str(data["nameTextMapHash"]))[Config.LANGS]
            __pydantic_self__.artifactType = EquipType[data["equipType"]]
            for stats in data["reliquarySubstats"]:
                __pydantic_self__.substats.append(EquipmentsStats.parse_obj(stats))

        if data["itemType"] == "ITEM_WEAPON": # AKA. Weapon
            __pydantic_self__.name = Config.HASH_MAP["weapons"].get(str(data["nameTextMapHash"]))[Config.LANGS]
            __pydantic_self__.mainstats = EquipmentsStats.parse_obj(data["weaponStats"][0])
            for stats in data["weaponStats"][1:]:
                __pydantic_self__.substats.append(EquipmentsStats.parse_obj(stats))
        
        __pydantic_self__.icon = create_ui_path(data["icon"])

    class Config:
        use_enum_values = True

class Equipments(BaseModel):
    """
        API Response data
    """
    id: int = Field(0, alias="itemId")
    detail: EquipmentsDetail = Field({}, alias="flat")

    """
        Custom data
    """
    level: int = 0 # Get form key "reliquary" and "weapon"
    type: EquipmentsType = EquipmentsType.UNKNOWN # Type of equipments (Ex. Artifact, Weapon)

    class Config:
        use_enum_values = True

    def __init__(__pydantic_self__, **data: Any) -> None:
        super().__init__(**data)

        if data["flat"]["itemType"] == "ITEM_RELIQUARY": # AKA. Artifact
            __pydantic_self__.type = EquipmentsType.ARTIFACT
            __pydantic_self__.level = data["reliquary"]["level"] - 1
        
        if data["flat"]["itemType"] == "ITEM_WEAPON": # AKA. Weapon
            __pydantic_self__.type = EquipmentsType.WEAPON
            __pydantic_self__.level = data["weapon"]["level"] - 1