# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.1] - 2023-04-03
<!-- markdown-link-check-disable-next-line -->
This version is only compatible with [STEMMUS_SCOPE 1.2.0](https://github.com/EcoExtreML/STEMMUS_SCOPE/releases/tag/1.2.0).

### Added:
- LAI data can now be read by the global data routines ([#69](https://github.com/EcoExtreML/STEMMUS_SCOPE_Processing/pull/69)).
- Data validation checks (file existance, spatial & temporal bounds, ...) to global data read routines ([#71](https://github.com/EcoExtreML/STEMMUS_SCOPE_Processing/pull/71)).

### Changed:
- The project has been moved to a `pyproject.toml` + `hatch` setup, with ruff as the linter and mypy as type checker ([#68](https://github.com/EcoExtreML/STEMMUS_SCOPE_Processing/pull/68)).

### Fixed:
- The output netcdf file is again compatible to the model evaluation website ([#76](https://github.com/EcoExtreML/STEMMUS_SCOPE_Processing/pull/76)).

## [0.2.0] - 2023-02-21
<!-- markdown-link-check-disable-next-line -->
This version is only compatible with [STEMMUS_SCOPE 1.2.0](https://github.com/EcoExtreML/STEMMUS_SCOPE/releases/tag/1.2.0).

### Added:
 - A time range can now be specified for which the model should be run.
 - The model can now be run on any site globally, by providing a latitude and longitude, assuming that the required data is available for those sites.
     - Note: land cover and LAI are not dynamically retrieved yet, but use a dummy value.

### Changed:
 - Documentation now uses mkdocs instead of sphinx.

## [0.1.1] - 2022-11-24
### Changed:
- Supported Python versions are now 3.8, 3.9 and 3.10.

## [0.1.0] - 2022-11-24
The first release of PyStemmusScope. Compatible with STEMMUS_SCOPE 1.1.11.

### Added

### Removed

### Changed

<!-- [Unreleased]: https://github.com/EcoExtreML/STEMMUS_SCOPE_Processing/compare/v1.0.0...HEAD
[0.0.1]: https://github.com/EcoExtreML/STEMMUS_SCOPE_Processing/releases/tag/v0.0.1 -->
