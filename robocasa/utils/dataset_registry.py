import os
from collections import OrderedDict
from copy import deepcopy
from pathlib import Path

import robocasa
import robocasa.macros as macros

SINGLE_STAGE_TASK_DATASETS = OrderedDict(
    AdjustToasterOvenTemperature=dict(
        horizon=600,
        human_path="v0.5/train/atomic/AdjustToasterOvenTemperature/20250714",
        mg_path="v0.5/train/atomic/AdjustToasterOvenTemperature/mg/demo/2025-07-16-18-16-56",
    ),
    AdjustWaterTemperature=dict(
        horizon=600,
        human_path="v0.5/train/atomic/AdjustWaterTemperature/20250718",
    ),
    CloseCabinet=dict(
        horizon=1000,
        human_path="v0.5/train/atomic/CloseCabinet/20250711",
        mg_path="v0.5/train/atomic/CloseCabinet/mg/demo/2025-07-18-18-52-41",
    ),
    CloseDishwasher=dict(
        horizon=800,
        human_path="v0.5/train/atomic/CloseDishwasher/20250711",
        mg_path="v0.5/train/atomic/CloseDishwasher/mg/demo/2025-07-14-21-13-52",
    ),
    CloseDrawer=dict(
        horizon=600,
        human_path="v0.5/train/atomic/CloseDrawer/20250714",
        mg_path="v0.5/train/atomic/CloseDrawer/mg/demo/2025-07-15-23-08-21",
    ),
    CloseElectricKettleLid=dict(
        horizon=200,
        human_path="v0.5/train/atomic/CloseElectricKettleLid/20250712",
        mg_path="v0.5/train/atomic/CloseElectricKettleLid/mg/demo/2025-07-17-00-58-24",
    ),
    CloseFridge=dict(
        horizon=1400,
        human_path="v0.5/train/atomic/CloseFridge/20250711",
    ),
    CloseMicrowave=dict(
        horizon=700,
        human_path="v0.5/train/atomic/CloseMicrowave/20250712",
        mg_path="v0.5/train/atomic/CloseMicrowave/mg/demo/2025-07-15-14-37-52",
    ),
    CloseOven=dict(
        horizon=500,
        human_path="v0.5/train/atomic/CloseOven/20250711",
        mg_path="v0.5/train/atomic/CloseOven/mg/demo/2025-07-16-01-04-44",
    ),
    CloseStandMixerHead=dict(
        horizon=500,
        human_path="v0.5/train/atomic/CloseStandMixerHead/20250711",
        mg_path="v0.5/train/atomic/CloseStandMixerHead/mg/demo/2025-07-12-14-59-28",
    ),
    CloseToasterOvenDoor=dict(
        horizon=400,
        human_path="v0.5/train/atomic/CloseToasterOvenDoor/20250714",
    ),
    CoffeeServeMug=dict(
        horizon=900,
        human_path="v0.5/train/atomic/CoffeeServeMug/20250711",
        mg_path="v0.5/train/atomic/CoffeeServeMug/mg/demo/2025-07-17-01-00-52",
    ),
    CoffeeSetupMug=dict(
        horizon=900,
        human_path="v0.5/train/atomic/CoffeeSetupMug/20250711",
        mg_path="v0.5/train/atomic/CoffeeSetupMug/mg/demo/2025-07-15-19-25-48",
    ),
    OpenCabinet=dict(
        horizon=1400,
        human_path="v0.5/train/atomic/OpenCabinet/20250711",
        mg_path="v0.5/train/atomic/OpenCabinet/mg/demo/2025-07-19-18-32-04",
    ),
    OpenDishwasher=dict(
        horizon=800,
        human_path="v0.5/train/atomic/OpenDishwasher/20250711",
        mg_path="v0.5/train/atomic/OpenDishwasher/mg/demo/2025-07-12-15-00-12",
    ),
    OpenDrawer=dict(
        horizon=700,
        human_path="v0.5/train/atomic/OpenDrawer/20250714",
        mg_path="v0.5/train/atomic/OpenDrawer/mg/demo/2025-07-16-09-53-11",
    ),
    OpenElectricKettleLid=dict(
        horizon=300,
        human_path="v0.5/train/atomic/OpenElectricKettleLid/20250712",
        mg_path="v0.5/train/atomic/OpenElectricKettleLid/mg/demo/2025-07-16-17-57-23",
    ),
    OpenFridge=dict(
        horizon=1400,
        human_path="v0.5/train/atomic/OpenFridge/20250711",
    ),
    OpenMicrowave=dict(
        horizon=800,
        human_path="v0.5/train/atomic/OpenMicrowave/20250711",
        mg_path="v0.5/train/atomic/OpenMicrowave/mg/demo/2025-07-15-12-07-46",
    ),
    OpenOven=dict(
        horizon=400,
        human_path="v0.5/train/atomic/OpenOven/20250711",
        mg_path="v0.5/train/atomic/OpenOven/mg/demo/2025-07-13-19-13-07",
    ),
    OpenStandMixerHead=dict(
        horizon=700,
        human_path="v0.5/train/atomic/OpenStandMixerHead/20250711",
        mg_path="v0.5/train/atomic/OpenStandMixerHead/mg/demo/2025-07-14-21-14-03",
    ),
    OpenToasterOvenDoor=dict(
        horizon=400,
        human_path="v0.5/train/atomic/OpenToasterOvenDoor/20250714",
        mg_path="v0.5/train/atomic/OpenToasterOvenDoor/mg/demo/2025-07-16-06-43-12",
    ),
    PnPCabinetToCounter=dict(
        horizon=800,
        human_path="v0.5/train/atomic/PnPCabinetToCounter/20250711",
        mg_path="v0.5/train/atomic/PnPCabinetToCounter/mg/demo/2025-07-16-10-47-20",
    ),
    PnPCounterToCabinet=dict(
        horizon=800,
        human_path="v0.5/train/atomic/PnPCounterToCabinet/20250712",
        mg_path="v0.5/train/atomic/PnPCounterToCabinet/mg/demo/2025-07-15-19-24-59",
    ),
    PnPCounterToMicrowave=dict(
        horizon=1500,
        human_path="v0.5/train/atomic/PnPCounterToMicrowave/20250712",
        mg_path="v0.5/train/atomic/PnPCounterToMicrowave/mg/demo/2025-07-15-19-14-49",
    ),
    PnPCounterToOven=dict(
        horizon=1000,
        human_path="v0.5/train/atomic/PnPCounterToOven/20250714",
        mg_path="v0.5/train/atomic/PnPCounterToOven/mg/demo/2025-07-16-10-40-51",
    ),
    PnPCounterToSink=dict(
        horizon=900,
        human_path="v0.5/train/atomic/PnPCounterToSink/20250711",
        mg_path="v0.5/train/atomic/PnPCounterToSink/mg/demo/2025-07-12-15-02-36",
    ),
    PnPCounterToStandMixer=dict(
        horizon=1100,
        human_path="v0.5/train/atomic/PnPCounterToStandMixer/20250711",
        mg_path="v0.5/train/atomic/PnPCounterToStandMixer/mg/demo/2025-07-13-19-10-48",
    ),
    PnPCounterToStove=dict(
        horizon=900,
        human_path="v0.5/train/atomic/PnPCounterToStove/20250711",
        mg_path="v0.5/train/atomic/PnPCounterToStove/mg/demo/2025-07-13-19-12-04",
    ),
    PnPCounterToToasterOven=dict(
        horizon=900,
        human_path="v0.5/train/atomic/PnPCounterToToasterOven/20250714",
        mg_path="v0.5/train/atomic/PnPCounterToToasterOven/mg/demo/2025-07-16-10-01-13",
    ),
    PnPMicrowaveToCounter=dict(
        horizon=1500,
        human_path="v0.5/train/atomic/PnPMicrowaveToCounter/20250711",
        mg_path="v0.5/train/atomic/PnPMicrowaveToCounter/mg/demo/2025-07-16-23-41-43",
    ),
    PnPSinkToCounter=dict(
        horizon=1000,
        human_path="v0.5/train/atomic/PnPSinkToCounter/20250711",
        mg_path="v0.5/train/atomic/PnPSinkToCounter/mg/demo/2025-07-17-16-13-25",
    ),
    PnPStoveToCounter=dict(
        horizon=1100,
        human_path="v0.5/train/atomic/PnPStoveToCounter/20250711",
        mg_path="v0.5/train/atomic/PnPStoveToCounter/mg/demo/2025-07-15-12-20-34",
    ),
    PnPToasterOvenToCounter=dict(
        horizon=600,
        human_path="v0.5/train/atomic/PnPToasterOvenToCounter/20250714",
        mg_path="v0.5/train/atomic/PnPToasterOvenToCounter/mg/demo/2025-07-17-01-00-50",
    ),
    PnPToasterToCounter=dict(
        horizon=1000,
        human_path="v0.5/train/atomic/PnPToasterToCounter/20250714",
        mg_path="v0.5/train/atomic/PnPToasterToCounter/mg/demo/2025-07-25-01-29-30",
    ),
    StartCoffeeMachine=dict(
        horizon=300,
        human_path="v0.5/train/atomic/StartCoffeeMachine/20250711",
        mg_path="v0.5/train/atomic/StartCoffeeMachine/mg/demo/2025-07-11-18-31-31",
    ),
    TurnOffMicrowave=dict(
        horizon=800,
        human_path="v0.5/train/atomic/TurnOffMicrowave/20250711",
        mg_path="v0.5/train/atomic/TurnOffMicrowave/mg/demo/2025-07-16-01-02-52",
    ),
    TurnOffSinkFaucet=dict(
        horizon=800,
        human_path="v0.5/train/atomic/TurnOffSinkFaucet/20250711",
        mg_path="v0.5/train/atomic/TurnOffSinkFaucet/mg/demo/2025-07-14-16-38-56",
    ),
    TurnOffStove=dict(
        horizon=700,
        human_path="v0.5/train/atomic/TurnOffStove/20250711",
        mg_path="v0.5/train/atomic/TurnOffStove/mg/demo/2025-07-11-18-29-00",
    ),
    TurnOnElectricKettle=dict(
        horizon=400,
        human_path="v0.5/train/atomic/TurnOnElectricKettle/20250712",
        mg_path="v0.5/train/atomic/TurnOnElectricKettle/mg/demo/2025-07-16-18-16-21",
    ),
    TurnOnMicrowave=dict(
        horizon=700,
        human_path="v0.5/train/atomic/TurnOnMicrowave/20250711",
        mg_path="v0.5/train/atomic/TurnOnMicrowave/mg/demo/2025-07-14-14-45-53",
    ),
    TurnOnSinkFaucet=dict(
        horizon=1100,
        human_path="v0.5/train/atomic/TurnOnSinkFaucet/20250711",
        mg_path="v0.5/train/atomic/TurnOnSinkFaucet/mg/demo/2025-07-14-15-30-37",
    ),
    TurnOnStove=dict(
        horizon=600,
        human_path="v0.5/train/atomic/TurnOnStove/20250712",
        mg_path="v0.5/train/atomic/TurnOnStove/mg/demo/2025-07-17-10-34-55",
    ),
    TurnOnToaster=dict(
        horizon=200,
        human_path="v0.5/train/atomic/TurnOnToaster/20250714",
        mg_path="v0.5/train/atomic/TurnOnToaster/mg/demo/2025-07-24-23-09-11",
    ),
    TurnOnToasterOven=dict(
        horizon=700,
        human_path="v0.5/train/atomic/TurnOnToasterOven/20250714",
        mg_path="v0.5/train/atomic/TurnOnToasterOven/mg/demo/2025-07-17-00-47-20",
    ),
    TurnSinkSpout=dict(
        horizon=300,
        human_path="v0.5/train/atomic/TurnSinkSpout/20250711",
        mg_path="v0.5/train/atomic/TurnSinkSpout/mg/demo/2025-07-14-16-38-26",
    ),
)


MULTI_STAGE_TASK_DATASETS = OrderedDict(
    AirDryFruit=dict(
        horizon=1900,
        human_path="v0.5/train/composite/AirDryFruit/20250718",
    ),
    ArrangeBreadBasket=dict(
        horizon=2900,
        human_path="v0.5/train/composite/ArrangeBreadBasket/20250716",
    ),
    ArrangeTea=dict(
        horizon=3200,
        human_path="v0.5/train/composite/ArrangeTea/20250714",
    ),
    ArrangeVegetables=dict(
        horizon=1100,
        human_path="v0.5/train/composite/ArrangeVegetables/20250714",
    ),
    BeverageSorting=dict(
        horizon=3500,
        human_path="v0.5/train/composite/BeverageSorting/20250718",
    ),
    BowlAndCup=dict(
        horizon=1600,
        human_path="v0.5/train/composite/BowlAndCup/20250715",
    ),
    BreadSetupSlicing=dict(
        horizon=800,
        human_path="v0.5/train/composite/BreadSetupSlicing/20250719",
    ),
    CheesyBread=dict(
        horizon=500,
        human_path="v0.5/train/composite/CheesyBread/20250714",
    ),
    ChooseMeasuringCup=dict(
        horizon=1200,
        human_path="v0.5/train/composite/ChooseMeasuringCup/20250718",
    ),
    ClearCuttingBoard=dict(
        horizon=1200,
        human_path="v0.5/train/composite/ClearCuttingBoard/20250719",
    ),
    ClearSink=dict(
        horizon=3300,
        human_path="v0.5/train/composite/ClearSink/20250717",
    ),
    ClearSinkSpace=dict(
        horizon=1200,
        human_path="v0.5/train/composite/ClearSinkSpace/20250718",
    ),
    CollectWashingSupplies=dict(
        horizon=1800,
        human_path="v0.5/train/composite/CollectWashingSupplies/20250717",
    ),
    ColorfulSalsa=dict(
        horizon=1600,
        human_path="v0.5/train/composite/ColorfulSalsa/20250719",
    ),
    CondimentCollection=dict(
        horizon=1400,
        human_path="v0.5/train/composite/CondimentCollection/20250721",
    ),
    CupcakeCleanup=dict(
        horizon=700,
        human_path="v0.5/train/composite/CupcakeCleanup/20250716",
    ),
    DefrostByCategory=dict(
        horizon=2200,
        human_path="v0.5/train/composite/DefrostByCategory/20250716",
    ),
    DessertAssembly=dict(
        horizon=900,
        human_path="v0.5/train/composite/DessertAssembly/20250719",
    ),
    DivideBasins=dict(
        horizon=1400,
        human_path="v0.5/train/composite/DivideBasins/20250718",
    ),
    DryDishes=dict(
        horizon=1100,
        human_path="v0.5/train/composite/DryDishes/20250714",
    ),
    DryDrinkware=dict(
        horizon=900,
        human_path="v0.5/train/composite/DryDrinkware/20250714",
    ),
    FoodCleanup=dict(
        horizon=2200,
        human_path="v0.5/train/composite/FoodCleanup/20250715",
    ),
    FryingPanAdjustment=dict(
        horizon=800,
        human_path="v0.5/train/composite/FryingPanAdjustment/20250714",
    ),
    HeatMultipleWater=dict(
        horizon=2800,
        human_path="v0.5/train/composite/HeatMultipleWater/20250714",
    ),
    LoadDishwasher=dict(
        horizon=1200,
        human_path="v0.5/train/composite/LoadDishwasher/20250717",
    ),
    MealPrepStaging=dict(
        horizon=2000,
        human_path="v0.5/train/composite/MealPrepStaging/20250718",
    ),
    MicrowaveThawing=dict(
        horizon=3100,
        human_path="v0.5/train/composite/MicrowaveThawing/20250715",
    ),
    OrganizeMugsByHandle=dict(
        horizon=900,
        human_path="v0.5/train/composite/OrganizeMugsByHandle/20250718",
    ),
    OrganizeVegetables=dict(
        horizon=600,
        human_path="v0.5/train/composite/OrganizeVegetables/20250719",
    ),
    PanTransfer=dict(
        horizon=1200,
        human_path="v0.5/train/composite/PanTransfer/20250714",
    ),
    PlaceDishesBySink=dict(
        horizon=1600,
        human_path="v0.5/train/composite/PlaceDishesBySink/20250717",
    ),
    PreRinseStation=dict(
        horizon=1500,
        human_path="v0.5/train/composite/PreRinseStation/20250717",
    ),
    PreSoakPan=dict(
        horizon=1600,
        human_path="v0.5/train/composite/PreSoakPan/20250715",
    ),
    PrepForSanitizing=dict(
        horizon=2500,
        human_path="v0.5/train/composite/PrepForSanitizing/20250715",
    ),
    PrepMarinatingMeat=dict(
        horizon=1900,
        human_path="v0.5/train/composite/PrepMarinatingMeat/20250714",
    ),
    PrepareCoffee=dict(
        horizon=1200,
        human_path="v0.5/train/composite/PrepareCoffee/20250716",
    ),
    PrepareDishwasher=dict(
        horizon=900,
        human_path="v0.5/train/composite/PrepareDishwasher/20250717",
    ),
    PrepareToast=dict(
        horizon=2500,
        human_path="v0.5/train/composite/PrepareToast/20250714",
    ),
    PressChicken=dict(
        horizon=1000,
        human_path="v0.5/train/composite/PressChicken/20250717",
    ),
    PrewashFoodAssembly=dict(
        horizon=1100,
        human_path="v0.5/train/composite/PrewashFoodAssembly/20250714",
    ),
    PrewashFoodSorting=dict(
        horizon=2400,
        human_path="v0.5/train/composite/PrewashFoodSorting/20250718",
    ),
    RecycleBottlesBySize=dict(
        horizon=2500,
        human_path="v0.5/train/composite/RecycleBottlesBySize/20250717",
    ),
    RecycleBottlesByType=dict(
        horizon=1900,
        human_path="v0.5/train/composite/RecycleBottlesByType/20250717",
    ),
    RecycleSodaCans=dict(
        horizon=4500,
        human_path="v0.5/train/composite/RecycleSodaCans/20250719",
    ),
    RecycleStackedYogurt=dict(
        horizon=1400,
        human_path="v0.5/train/composite/RecycleStackedYogurt/20250717",
    ),
    RestockPantry=dict(
        horizon=1700,
        human_path="v0.5/train/composite/RestockPantry/20250714",
    ),
    RinseBowls=dict(
        horizon=1900,
        human_path="v0.5/train/composite/RinseBowls/20250718",
    ),
    RotatePan=dict(
        horizon=400,
        human_path="v0.5/train/composite/RotatePan/20250717",
    ),
    ScrubBowl=dict(
        horizon=900,
        human_path="v0.5/train/composite/ScrubBowl/20250717",
    ),
    SearingMeat=dict(
        horizon=2900,
        human_path="v0.5/train/composite/SearingMeat/20250716",
    ),
    ServeSteak=dict(
        horizon=1400,
        human_path="v0.5/train/composite/ServeSteak/20250718",
    ),
    SetBowlsForSoup=dict(
        horizon=3600,
        human_path="v0.5/train/composite/SetBowlsForSoup/20250716",
    ),
    SimmeringSauce=dict(
        horizon=2300,
        human_path="v0.5/train/composite/SimmeringSauce/20250715",
    ),
    SizeSorting=dict(
        horizon=1000,
        human_path="v0.5/train/composite/SizeSorting/20250714",
    ),
    SnackSorting=dict(
        horizon=1300,
        human_path="v0.5/train/composite/SnackSorting/20250718",
    ),
    SoakSponge=dict(
        horizon=1700,
        human_path="v0.5/train/composite/SoakSponge/20250718",
    ),
    StackBowlsCabinet=dict(
        horizon=1400,
        human_path="v0.5/train/composite/StackBowlsCabinet/20250717",
    ),
    StackBowlsInSink=dict(
        horizon=900,
        human_path="v0.5/train/composite/StackBowlsInSink/20250714",
    ),
    StartElectricKettle=dict(
        horizon=700,
        human_path="v0.5/train/composite/StartElectricKettle/20250717",
    ),
    SteamInMicrowave=dict(
        horizon=1200,
        human_path="v0.5/train/composite/SteamInMicrowave/20250714",
    ),
    StockingBreakfastFoods=dict(
        horizon=1600,
        human_path="v0.5/train/composite/StockingBreakfastFoods/20250715",
    ),
    ThawInSink=dict(
        horizon=1000,
        human_path="v0.5/train/composite/ThawInSink/20250721",
    ),
    TransportCookware=dict(
        horizon=1900,
        human_path="v0.5/train/composite/TransportCookware/20250717",
    ),
    VeggieDipPrep=dict(
        horizon=2100,
        human_path="v0.5/train/composite/VeggieDipPrep/20250718",
    ),
    WaffleReheat=dict(
        horizon=2700,
        human_path="v0.5/train/composite/WaffleReheat/20250715",
    ),
    WashFruitColander=dict(
        horizon=2100,
        human_path="v0.5/train/composite/WashFruitColander/20250717",
    ),
    WeighIngredients=dict(
        horizon=2000,
        human_path="v0.5/train/composite/WeighIngredients/20250718",
    ),
)


def get_ds_path(task, ds_type, return_info=False):
    if task in SINGLE_STAGE_TASK_DATASETS:
        ds_config = SINGLE_STAGE_TASK_DATASETS[task]
    elif task in MULTI_STAGE_TASK_DATASETS:
        ds_config = MULTI_STAGE_TASK_DATASETS[task]
    else:
        raise ValueError

    if ds_type == "human_raw":
        folder = ds_config["human_path"]
        fname = "demo.hdf5"
    elif ds_type == "human_im":
        folder = ds_config["human_path"]
        if task in SINGLE_STAGE_TASK_DATASETS:
            fname = "demo_im128.hdf5"
        elif task in MULTI_STAGE_TASK_DATASETS:
            fname = "demo_im128.hdf5"
    elif ds_type == "mg_im":
        # mg dataset is not available for all tasks
        folder = ds_config.get("mg_path", None)
        fname = "demo_im128.hdf5"
    else:
        raise ValueError

    # if dataset type is not registered, return None
    if folder is None:
        ret = (None, None) if return_info is True else None
        return ret

    if macros.DATASET_BASE_PATH is None:
        ds_base_path = os.path.join(
            Path(robocasa.__path__[0]).parent.absolute(), "datasets"
        )
    else:
        ds_base_path = macros.DATASET_BASE_PATH
    ds_path = os.path.join(ds_base_path, folder, fname)

    if return_info is False:
        return ds_path

    ds_info = {}
    if "download_links" in ds_config:
        ds_info["url"] = ds_config["download_links"][ds_type]
    ds_info["horizon"] = ds_config["horizon"]
    return ds_path, ds_info
