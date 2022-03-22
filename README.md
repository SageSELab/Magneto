# Magneto

This repo is for our Magneto project on automated test oracles.
![MAGNETO Approach Overview](https://github.com/SageSELab/Magneto/blob/main/MAGNETO-overview.png)

## App Execution
* All the Android applications we used in this MAGNETO evaluation are in `apks` folder.
* The result from *App Execution* for the different apps are in `oracle_resources_all` folder.
* `oracle_resources_all` folder contains screen metadata in `uis` and screenshots in `screens` for all the buggy version and fixed version of the apps.

## Oracle Trigger Detection and Oracle Execution
* The python scripts for trigger detection and oracle execution are in `oracleFromBehavior` folder.
* This folder contains five automated oracle implementations:

| folder | Oracle |
|---|---|
|![backButton](https://github.com/SageSELab/Magneto/tree/main/oracleFromBehavior/backButton) | Pressing back should lead to the previous screen |
| `languageDetection` | The language change should be reflected on all screens |
| `orientationChange` | The screen content should not change on rotation |
| `themeChange` | Theme change should be reflected on all screens |
| `userEnteredData` | User-entered data should display correctly |
