# Magneto

This repo is for our MAGNETO project on automated test oracles for mobile apps.

## Behavioral Oracle Taxonomy
This repo contains the datasets collected for the ![behavioral oracle taxonomy](https://github.com/SageSELab/Magneto/blob/main/images/taxonomy.pdf). Resources for ![taxonomy norming](https://docs.google.com/spreadsheets/d/15dbbp-zaFA_6UBr0IVcsuBHmfVG0gCDYwTP-SBpybzo/edit?usp=sharing), ![axial coding](https://docs.google.com/spreadsheets/d/1iddjAeBIdNvxcRswPsc1MG6jVpQXWIMrHJmr5aRgsyE/edit?usp=sharing), and ![taxonomy analysis](https://docs.google.com/spreadsheets/d/13setORacGxlAF8OOBpnzCIEt3vusN8ZPQPXQT9jDt_c/edit?usp=sharing) are also available.

## Automated Oracles

MAGNETO automatically analyzes if an app contains failure of specific type. This repo also contains the source code to the automated part, example resources to try MAGNETO.

## Dependencies
MAGNETO supports building the project via [poetry](https://python-poetry.org/).
All required dependencies are listed in <code>pyproject.toml</code> under _tool.poetry.dependencies_.
If using poetry, simply run <code> poetry install </code> to install dependencies.
If poetry is not used, you can also install the dependency individually via <code>pip install</code>.

## MAGNETO Approach Overview:

![MAGNETO Approach Overview](https://github.com/SageSELab/Magneto/blob/main/images/MAGNETO-overview.png)

## App Execution
* All the Android applications we used in this MAGNETO evaluation are in `apks` folder.
* The result from *App Execution* for the different apps are in `oracleResourcesAll` folder.
* `oracleResourcesAll` folder contains screen metadata in `uis` and screenshots in `screens` for all the buggy version and fixed version of the apps.

## Oracle Trigger Detection and Oracle Execution
* The five automated oracle implementations are in `oracleFromBehavior` folder.

| folder | Oracle |
|---|---|
|![backButton](https://github.com/SageSELab/Magneto/tree/main/oracleFromBehavior/backButton) | Pressing back should lead to the previous screen |
|![languageDetection](https://github.com/SageSELab/Magneto/tree/main/oracleFromBehavior/languageDetection) | The language change should be reflected on all screens |
|![orientationChange](https://github.com/SageSELab/Magneto/tree/main/oracleFromBehavior/orientationChange) | The screen content should not change on rotation |
|![themeChange](https://github.com/SageSELab/Magneto/tree/main/oracleFromBehavior/themeChange) | Theme change should be reflected on all screens |
|![userEnteredData](https://github.com/SageSELab/Magneto/tree/main/oracleFromBehavior/userEnteredData) | User-entered data should display correctly |

* Each oracle folder has resources used for development, and evaluation along with the python scripts for trigger detection and oracle execution.
* The oracles can be called from command line as:

`python <oracleScript.py> -a <appName> -b <bugId>`
* Command line examples for each oracle type is in `AllTestScripts.txt`
