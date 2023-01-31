from typing import Optional

import click
from jackdaw_ml.artefact_endpoint import ArtefactEndpoint
from jackdaw_ml.search import Searcher

from corvus.config import CorvusConfigBuilder, OutputFormat
from corvus.model_output import models_to_json, models_to_table


@click.group()
@click.version_option(package_name="corvus")
def cli():
    """Corvus - Search & Explore ShareableAI Models"""
    pass


@cli.group("set")
def set():
    """Configure Corvus settings"""
    pass


@set.command("format")
@click.argument("output_format", type=click.Choice(["Table", "JSON"]), required=True)
def set_format(output_format: str) -> None:
    """Set output format for displaying models"""
    CorvusConfigBuilder.load().set_format(OutputFormat.from_str(output_format)).write()


@set.command("api_key")
@click.password_option("--api_key", confirmation_prompt=False)
def endpoint(api_key: str) -> None:
    """Set API Key for ShareableAI Cloud"""
    CorvusConfigBuilder.load().set_api_key(api_key).write()
    if len(api_key) > 2:
        click.echo(f"API Key ({api_key[0:3]}...) saved in config")


@cli.command("list")
@click.option("--local/--remote", default=True)  # Default of Local
@click.option("--all", default=False, is_flag=True, )
@click.option("--repo", type=str, required=False)
@click.option("--branch", type=str, required=False)
def list(local: bool, all: bool, repo: Optional[str], branch: Optional[str]):
    """
    list

    List models from locally defined storage or ShareableAI Cloud. This CLI function is effectively a wrapper around
    the Searcher functionality in Jackdaw, and it is recommended that Jackdaw is used directly for any programmatic
    use case such as CI/CD.

    Output format can be set via `corvus set format` to either JSON or Tabular.

    [OPTIONS]

    --local

        Fetch models from Local storage - typically in ~/.artefact_registry.sqlite

    --remote

        Fetch all remote models that the user has permission to view, either by user, group, or organisation.

    --repo

        Filter models to those attached to a named repository, i.e. 'jackdaw'

    --branch

        Filter models to those attached to a given branch name, i.e. 'main'

    """
    corvus_config = CorvusConfigBuilder.load()
    if local:
        artefact_endpoint = ArtefactEndpoint.default()
    else:
        if corvus_config.api_key is None:
            click.echo("API Key has not been set - please set via `corvus set api_key {API_KEY}`", err=True)
            return None
        artefact_endpoint = ArtefactEndpoint.remote(corvus_config.api_key)
    searcher = Searcher(artefact_endpoint)
    if repo is not None or branch is not None:
        if repo is None:
            repo = '%'
        searcher = searcher.with_repository(repo, branch)
    if all:
        searcher = searcher.with_children()
    if corvus_config.output_format == OutputFormat.Table:
        models_to_table(searcher.models())
    elif corvus_config.output_format is OutputFormat.JSON:
        models_to_json(searcher.models())
