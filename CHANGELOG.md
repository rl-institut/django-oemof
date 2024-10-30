# Changelog
All notable changes to this project will be documented in this file.

The format is inspired from [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and the versioning aim to respect [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

Here is a template for new release sections

## [0.18.2] - 2024-10-30
### Fixed
- add dependencies for pandas, numpy and psycopg2

## [0.18.1] - 2024-05-22
### Fixed
- error responses for invalid simulation runs

## [0.18.0] - 2024-04-30
### Added
- check for stored simulation to prevent doubling simulation results

### Changed
- removed `oemof.tabular` from dependencies (BREAKING) 

## [0.17.0] - 2024-02-27
### Added
- config option DJANGO_OEMOF_IGNORE_SIMULATION_PARAMETERS to ignore parameters when running simulation

## [0.16.0] - 2023-11-09
### Changed
- Updated oemof.tabular version to v0.0.4

## [0.15.1] - 2023-10-09
### Fixed
- simulation unpack of mapped results

## [0.15.0] - 2023-10-05
### Added
- error exception if oemof simulation is infeasible

### Fixed
- oemof.tabular version

## [0.14.0] - 2023-08-24
### Changed
- update solph version to 0.0.5

## [0.13.1] - 2023-07-14
### Fixed
- series results with different column name than "values"

## [0.13.0] - 2023-07-13
### Fixed
- float64 and int64 conversion error in restore results function

## [0.12.0] - 2023-07-12
### Added
- manual adaption of flow attributes

### Fixed
- automatic energysystem adaption of flow attributes

## [0.11.0] - 2023-07-07
### Added
- automatic energysystem adaption of flow attributes

## [0.10.1] - 2023-07-04
### Added
- option to store LP file in simulation run

## [0.10.0] - 2023-06-16
### Added
- calculations in `get_results` function can be named in order to get more readable results

## [0.9.0] - 2023-06-16
### Changed
- result model name length to text field (no char limit)

### Fixed
- too short names for results with many parameters

## [0.8.0] - 2023-06-08
### Added
- warning if component cannot be found during ES adaption
- warning if attribute of component cannot be found during ES adaption

### Fixed
- skip component if component can not be found during ES adaption

## [0.7.1] - 2023-06-07
### Added
- logging info when hook is applied

## [0.7.0] - 2023-05-24
### Changed
- integrated celery for running simulations (instead of multiprocessing)

## [0.6.0] - 2023-05-22
### Changed
- switched to oemof.tabular (instead of using postprocessing from oemoflex)

## [0.5.0] - 2023-05-02
### Added
- oemof results can be gathered using calculation class instead of name

## [0.4.0] - 2023-04-14
### Added
- simulation ID is returned in simulation view  after successful simulation run

## Changed
- simulation ID is used to look up results and calculations

## [0.3.0] - 2023-03-30
### Added
- setup hook which differentiates parameter setup from bild parameters
- namespace for django-oemof app

## [0.2.0] - 2023-02-22
### Added
- hooks for parameters, energysystem and model

## [0.1.0] - 2023-01-01
### Added
- oemof ES can be built using datapackages
- energysystem build can be adapted using user parameters
- energysystem can be simulated within multiprocess
- results from simulation are stored in database
- simulation is not re-run in case of already existing results in DB
- calculations from (oemoflex, in future oemof.tabular) can be made
- calculations are stored in database and can be restored
