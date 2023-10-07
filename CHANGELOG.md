## [1.1.0] - 2023-10-08

### New features

- Added Changelog
- Added script definition for direct execution
- Version now extracted from pyproject.toml

### Bugfixes

- Upgraded urllib3 to >=2.0.6 because CVE-2023-43804
- Disabled HTTP redirects using redirects=False because CVE-2023-43804
- Increased about screen width

## [1.0.0] - 2023-09-27
- Initial MVP release