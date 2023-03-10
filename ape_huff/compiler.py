import contextlib
import subprocess
from collections import defaultdict
from functools import cached_property
from pathlib import Path

import huffc
from ape.api import CompilerAPI, PluginConfig
from ethpm_types import ContractType


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

    def compile(self, contract_filepaths, base_path=None):
        artifacts = {}
        for path in [file.relative_to(Path.cwd()) for file in contract_filepaths]:
            with contextlib.suppress(subprocess.CalledProcessError):
                artifacts.update(huffc.compile([path], version=self.version))

        def format(abi):
            result = []

            for typ in ("function", "event"):
                result.extend([{"type": typ, **val} for val in abi[f"{typ}s"].values()])

            if init := abi.get("constructor"):
                result.append({"type": "constructor", **init})

            return result

        for file, artifact in artifacts.items():
            artifact["contractName"] = Path(file).stem
            artifact["sourceId"] = Path.cwd().joinpath(file).relative_to(base_path).as_posix()
            artifact["deploymentBytecode"] = {"bytecode": artifact["bytecode"]}
            artifact["runtimeBytecode"] = {"bytecode": artifact["runtime"]}
            artifact["abi"] = format(artifact["abi"])

        return [ContractType.parse_obj(artifact) for artifact in artifacts.values()]

    def get_imports(self, contract_filepaths, base_path):
        artifacts = {}
        for path in [file.relative_to(Path.cwd()) for file in contract_filepaths]:
            with contextlib.suppress(subprocess.CalledProcessError):
                artifacts.update(huffc.compile([path], version=self.version))

        def collect(dependencies):
            result = []
            for dependency in dependencies:
                if dependency["dependencies"]:
                    result.extend(collect(dependency["dependencies"]))
                else:
                    result.append(
                        Path.cwd().joinpath(dependency["path"]).relative_to(base_path).as_posix()
                    )
            return result

        return {
            Path.cwd()
            .joinpath(file)
            .relative_to(base_path)
            .as_posix(): sorted(collect(artifact["file"]["dependencies"]))
            for file, artifact in artifacts.items()
        }
