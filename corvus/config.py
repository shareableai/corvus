from __future__ import annotations

__all__ = ["CorvusConfig", "CorvusConfigBuilder", "OutputFormat"]

import dataclasses
import enum
import os
import pathlib
from dataclasses import dataclass
from typing import Optional, Any

import tomli
import tomli_w


def remove_nones(d: Any) -> Any:
    if isinstance(d, dict):
        return {k: remove_nones(v) for k, v in d.items() if v is not None}
    return d


class OutputFormat(enum.Enum):
    Table = enum.auto()
    JSON = enum.auto()

    @staticmethod
    def from_str(x: Optional[str]) -> Optional[OutputFormat]:
        return OutputFormat.__members__.get(x, None)

    def as_str(self) -> str:
        if self is OutputFormat.Table:
            return "Table"
        elif self is OutputFormat.JSON:
            return "JSON"
        else:
            raise RuntimeError("Unreachable")


@dataclass
class CorvusConfig:
    api_key: Optional[str]
    output_format: OutputFormat

    @staticmethod
    def config_location() -> pathlib.Path:
        location = pathlib.Path(
            os.environ.get(
                "CORVUS_CONFIG_FILE",
                pathlib.Path.home() / ".shareableai" / "corvus.config.toml",
            )
        )
        location.parent.mkdir(parents=True, exist_ok=True)
        return location

    def set_api_key(self, api_key: str) -> CorvusConfig:
        self.api_key = api_key
        return self

    def set_format(self, format: OutputFormat) -> CorvusConfig:
        self.output_format = format
        return self

    def write(self) -> None:
        with open(CorvusConfig.config_location(), "wb") as f:
            tomli_w.dump(
                remove_nones(
                    {
                        "api_key": self.api_key,
                        "output_format": self.output_format.as_str(),
                    }
                ),
                f,
            )


@dataclass
class CorvusConfigBuilder:
    api_key: Optional[str]
    output_format: Optional[OutputFormat]

    @staticmethod
    def _from_env() -> CorvusConfigBuilder:
        api_key = os.environ.get("CORVUS_API_KEY", None)
        output_format = OutputFormat.from_str(
            os.environ.get("CORVUS_OUPUT_FORMAT", None)
        )
        if api_key is not None:
            return CorvusConfigBuilder(api_key, output_format)

    @staticmethod
    def _from_file() -> Optional[CorvusConfigBuilder]:
        if not CorvusConfig.config_location().exists():
            return None
        with open(CorvusConfig.config_location(), "rb") as f:
            config_dict = tomli.load(f)
            return CorvusConfigBuilder(
                config_dict.get("api_key", None),
                OutputFormat.from_str(config_dict.get("output_format", None)),
            )

    @staticmethod
    def defaults() -> CorvusConfigBuilder:
        return CorvusConfigBuilder(api_key=None, output_format=OutputFormat.Table)

    def _combine(self, other: Optional[CorvusConfigBuilder]) -> CorvusConfigBuilder:
        if other is None:
            return self
        return CorvusConfigBuilder(
            **(dataclasses.asdict(self) | remove_nones(dataclasses.asdict(other)))
        )

    def build(self) -> CorvusConfig:
        if self.output_format is None:
            raise ValueError("OutputFormat was not provided for Corvus Config")
        return CorvusConfig(self.api_key, self.output_format)

    @staticmethod
    def load() -> CorvusConfig:
        return (
            CorvusConfigBuilder.defaults()
            ._combine(CorvusConfigBuilder._from_file())
            ._combine(CorvusConfigBuilder._from_env())
        ).build()
