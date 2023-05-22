# Changelog
All notable changes to this project will be documented in this file.

The format is inspired from [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and the versioning aim to respect [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

Here is a template for new release sections

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
