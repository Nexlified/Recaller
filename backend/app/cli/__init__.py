"""Main CLI entry point for Recaller backend commands."""

import click
from app.cli.config import config


@click.group()
def cli():
    """Recaller Backend CLI"""
    pass


# Register command groups
cli.add_command(config)


if __name__ == '__main__':
    cli()