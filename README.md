#Optimus CLI

### Requirements
* Computer running MacOS or Linux. Use WSL2 or Homestead on Windows.
* Python 3.6 or later, accessible in the system `PATH` as `python3`
* Yarn package manager, with the following packages installed:
    * `prettier`
    * `@prettier/plugin-php`
    * `eslint`
    
* Composer package manager, with the following packages installed
    * `php-cs-fixer`

### Installation

 * Create a virtual environment with `python3 -m venv .venv`
 
 * Activate the virtual environment with `source .venv/bin/activate`
 
 * Install the required dependencies with `pip3 install -r requirements.txt`

### Usage

Run the program using `python3 cli.py <command> <options>`. Note: all options must be supplied after the main command.

Available commands:

* `generate:module config.json` - generate a new backend module using the configuration in `config.json`.
* `generate:page config.json` - generate a new page template using the configuration in `config.json`.

Available options:

* `--overwrite` - allow existing project files do be overwritten during generation. 
* `--skip-cs-fix` - don't run cs fixers after generation is complete.
* `--skip-templates` - don't create new template files during generation.
* `--skip-updates` - don't update existing files during generation.
