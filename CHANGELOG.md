# Change Log

## 0.1.6

### Changed

- Factory steps: only consider model's verbose name if the factory name matches
  (#111).

## 0.1.5

### Changed

- When unregistering a step, unregister all the sentences it is bound to
  (#107).

## 0.1.4

### Added

- Add an outline reference to the step (#106).

## 0.1.3

### Fixed

- Fix `run_feature_string` failing with non-ASCII characters (#105).

## 0.1.2

### Changed

- Update to work with Gherkin parser 4.0 (#104).

## 0.1.1

### Changed

- Follow symlinks when searching for feature directories (#102).

## 0.1.0

### Changed

- Make examples in scenario outlines independent test cases (#100).

## 0.0.45

### Fixed

- Require a proper version of `future` (#101).

## 0.0.44

### Added

- Better message when a step definition file failed to load (#91).

## 0.0.43

### Added

- Add a reference to the test instance to the step (#88).

## 0.0.42

### Fixed

- Fix line numbers reported for backgrounds (#83).

## 0.0.41

### Fixed

- Depend on the renamed `gherkin` package (#82).

## 0.0.40

### Changed

- Factory steps: prefer verbose name of the factory itself to the model name
  (#81).

## 0.0.39

### Changed

- Factory steps: try inferring verbose names for the created objects from the
  Meta classes (#80).

## 0.0.38

### Changed

- Colored output: remove colors incompatible with light backgrounds (#79).

### Added

- Colored output: Support for `CUCUMBER_COLORS` (#79).

## 0.0.37

### Changed

- Do not reload step modules during tests (#78).

## 0.0.36

### Fixed

- Do not crash when a feature directory contains files with non-ASCII
  characters (#77).

## 0.0.35

### Fixed

- Do not apply standard library patches from `future` (#76).

## 0.0.34

### Changed

- Factory steps: guess types of parameters passed in (#73).

## 0.0.33

### Added

- Report feature file name for syntax errors (#72).

## 0.0.32

### Fixed

- Fix `behave_as` when called from a scenario outline (#71).

## 0.0.31

- Fix `behave_as` when called from a background (#68).

## 0.0.30

### Changed

- Allow the features directory to be on the top level (#66).

## 0.0.29

### Fixed

- Fixes for new Gherkin package.

## 0.0.28

### Fixed

- Fix registering a new function for the same step definition (#64).
- Do not load feature files if they are not in a package (#61).

## 0.0.27

### Fixed

- Do not load feature files if they are found above a `features` directory
  (#57).
- Properly apply tags to scenario outlines (#59).

## 0.0.26

### Fixed

- Fix the exception when a step with non-ASCII characters in it is not defined
  on Python 2 (#51).

## 0.0.25

### Fixed

- Preserve the line number information in scenario outlines (#47).

### Added

- Support languages other than English for writing features (#46).

## 0.0.24

### Added

- Show tags when running with verbose output (#43).

## 0.0.23

### Fixed

- Fix verbose output on Python 2 (#39).

## 0.0.22

### Added

- Verbose output mode, like Cucumber (#33).
- Show feature file names in tracebacks as if they were modules (#38).

## Earlier releases

The release history below is not documented, please refer to the commit
history.
