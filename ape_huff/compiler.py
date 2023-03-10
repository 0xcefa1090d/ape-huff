from collections import defaultdict
from functools import cached_property

import huffc
from ape.api import CompilerAPI, PluginConfig


class HuffConfig(PluginConfig):
    version: str | None = None


class HuffCompiler(CompilerAPI):
    @property
    def name(self):
        return "huff"

    @property
    def config(self):
        return self.config_manager.get_config(self.name)

    @cached_property
    def version(self):
        with huffc.VersionManager() as hvm:
            version = self.config.version or max(hvm.fetch_remote_versions())

            if hvm.get_executable(version) is None:
                hvm.install(self.version)

    def get_versions(self, all_paths):
        with huffc.VersionManager() as hvm:
            return hvm.fetch_remote_versions()

    def get_compiler_settings(self, contract_filepaths, base_path=None):
        return defaultdict(dict)

    def get_version_map(self, contract_filepaths, base_path=None):
        return {self.version: set(contract_filepaths)}
