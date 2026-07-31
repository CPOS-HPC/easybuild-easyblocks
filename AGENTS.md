# Repository guide for EasyBuild easyblocks

## Scope

This repository contains EasyBuild easyblocks: Python classes that implement
software-specific build and installation logic. Easyconfigs belong in the
separate `easybuild-easyconfigs` repository.

Before changing an easyblock, inspect:

- the closest software-specific easyblock;
- the generic easyblock it inherits from;
- the corresponding easyconfig, when available;
- `test/easyblocks/` and `.github/workflows/` for validation conventions.

Preserve unrelated work in the checkout and keep each change narrowly scoped.

## Creating an easyblock

1. Put the module in `easybuild/easyblocks/<first-letter>/`. The module and
   class must agree with the software name used by the easyconfig. Use
   `easybuild.tools.filetools.encode_class_name` and
   `easybuild.framework.easyconfig.easyconfig.get_module_path` when a name
   contains punctuation or mixed case instead of guessing the encoding. For
   example, `code-server` uses `code_server.py` and
   `EB_code_minus_server`.
2. Select the narrowest generic base class that already models the package:
   `ConfigureMake`, `CMakeMake`, `PythonPackage`, `Binary`, `PackedBinary`,
   `Tarball`, and similar classes live under
   `easybuild/easyblocks/generic/`. Read the selected base completely before
   overriding it.
3. Override only the lifecycle steps that differ from the base:
   `extract_step`, `configure_step`, `build_step`, `install_step`,
   `post_processing_step`, `sanity_check_step`, and `make_module_extra`.
   Delegate to `super()` where the parent still owns part of the operation.
4. Define software-specific easyconfig parameters with `extra_options`.
   Extend the parent's options and use `CUSTOM` or `MANDATORY` as appropriate.
5. Use EasyBuild helpers instead of ad-hoc operations where possible:
   `easybuild.tools.filetools` for files, `run_shell_cmd` for commands,
   `get_software_root` for dependencies, and
   `self.module_load_environment` or `self.module_generator` for module
   environment changes.
6. Keep initialization compatible with `--module-only`. Do not require source
   files, build artifacts, network access, or runnable dependencies in
   `__init__`.

For prebuilt archives, inspect the archive layout rather than assuming a
top-level directory. `Tarball` is suitable when extracted content should be
copied as a tree. `PackedBinary` is useful for packed executable
distributions, but archives with multiple root entries may need a custom
install step.

## Sanity checks

Every software-specific easyblock should provide checks that demonstrate a
usable installation:

- list stable, essential files and directories relative to `installdir`;
- run a lightweight command such as `tool --version` or `tool --help` when the
  installed product provides one;
- avoid checks tied to incidental or hash-named build artifacts;
- call the parent `sanity_check_step` with `custom_paths` and, when useful,
  `custom_commands`.

Static web applications generally have no executable command. Check their
entry point, release metadata, and stable asset directories. Do not add a
development web server to the installation unless upstream distributes it as
part of the product.

## Style and validation

- Retain the GPLv2 project header and current copyright year.
- Follow the existing import ordering and 120-character line limit in
  `setup.cfg`.
- Use modern `super()` calls and `run_shell_cmd`; deprecated `run_cmd` APIs and
  logging calls such as `log.error` are rejected by the tests.
- Prefer `%` formatting in logging calls to avoid eagerly formatting messages.
- Run `flake8` when available.
- Exercise a real easyconfig with `eb --extended-dry-run` and
  `eb --module-only --force` before attempting a full installation.
- Run `python -O -m test.easyblocks.suite` in an environment with the matching
  EasyBuild framework and a supported modules tool.
- At minimum, compile changed Python modules and run
  `git diff --check` when the full EasyBuild test environment is unavailable.
