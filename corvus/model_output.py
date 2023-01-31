import datetime
import json
from typing import Iterable

from artefact_link import PyModelSearchResult
from rich import print_json
from rich.console import Console
from rich.table import Table

from corvus.utils import sizeof_fmt


def models_to_json(models: Iterable[PyModelSearchResult]) -> None:
    model_dicts = []
    for model in models:
        if model.vcs_info.remote_repository is None:
            owner, repository = None, None
        else:
            owner = model.vcs_info.remote_repository.owner
            repository = model.vcs_info.remote_repository.repository
        model_dicts.append({
            "model_name": model.model_id.name,
            "short_model_id": str(model.model_id.short_schema_id),
            "repository": f"{owner}\\{repository}" if owner is not None else "No Remote VCS Configured",
            "branch": model.vcs_info.branch,
            "git_sha": model.vcs_info.sha[0:7],
            "size": sizeof_fmt(model.model_id.model_size),
            "creation_time": datetime.datetime.fromtimestamp(
                model.creation_time
            ).strftime("%d/%m/%Y %H:%M:%S "),
        })
    print_json(json.dumps(model_dicts))


def models_to_table(models: Iterable[PyModelSearchResult]) -> None:
    console = Console()
    console.print()
    table = Table(show_header=True, header_style="cyan")
    table.add_column("Model Name")
    table.add_column("Short Model ID", overflow="ignore")
    table.add_column("Repository")
    table.add_column("Branch")
    table.add_column("Git SHA")
    table.add_column("Size", justify="right")
    table.add_column("Creation Time")
    for model in models:
        if model.vcs_info.remote_repository is None:
            owner, repository = None, None
        else:
            owner = model.vcs_info.remote_repository.owner
            repository = model.vcs_info.remote_repository.repository

        table.add_row(
            model.model_id.name,
            str(model.model_id.short_schema_id),
            f"{owner}\\{repository}" if owner is not None else "No Remote VCS Configured",
            model.vcs_info.branch,
            model.vcs_info.sha[0:7],
            sizeof_fmt(model.model_id.model_size),
            datetime.datetime.fromtimestamp(model.creation_time).strftime(
                "%d/%m/%Y %H:%M:%S"
            ),
        )
    console.print(table)
