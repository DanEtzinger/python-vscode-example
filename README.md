# python-vscode-example extension

## Building and signing

* `dt-sdk build .`

## Running

* `dt-sdk run`

## Developing

1. Clone this repository
2. Install dependencies with `pip install .`
3. Increase the version under `extension/extension.yaml` after modifications
4. Run `dt-sdk build`

## Structure

### python_vscode_example folder

Contains the python code for the extension

### extension folder

Contains the yaml and activation definitions for the framework v2 extension

### setup.py

Contains dependency and other python metadata

### activation.json

Used during simulation only, contains the activation definition for the extension

## Acknowledgements
This extension uses the sqlite implementation of the popular Northwind sample database, to create sample data for the extension. This is sourced from the https://github.com/jpwhite3/northwind-SQLite3 repoistory which uses the MIT license.
