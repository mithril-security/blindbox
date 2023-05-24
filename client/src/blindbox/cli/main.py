import inquirer
import os
import typer
from typing import Annotated, Optional

from .logging import log
from .context import Context

app = typer.Typer(rich_markup_mode="rich")

@app.command()
def init(
    platform: Annotated[Optional[str], typer.Option()] = None,
    dir: Annotated[str, typer.Option()] = os.getcwd(),
    interactive: Annotated[bool, typer.Option()] = True,
    auto_approve: Annotated[bool, typer.Option()] = False,
):
    if platform is None:
        if not interactive:
            log.error("Please supply a --platform to init the project.")
            exit(1)
        else:
            answers = inquirer.prompt(
                [
                    inquirer.List(
                        "platform",
                        "Select the platform to use",
                        choices=[
                            "azure-amd-sev - AMD-SEV SNP on Azure Cloud via ACI containers",
                            "aws-nitro - Nitro containers on Amazon Web Services",
                        ],
                    )
                ]
            )
            if not answers:  # CTRL+C
                exit(1)
    
        platform = answers["platform"].split(" ")[0]

    ctx = Context.from_platform(platform, interactive, auto_approve)
    ctx.init_cmd(dir)

@app.command()
def apply(
    dir: Annotated[str, typer.Option()] = os.getcwd(),
    interactive: Annotated[bool, typer.Option()] = True,
    auto_approve: Annotated[bool, typer.Option()] = False,
):
    ctx = Context.from_cfg_file(dir, interactive, auto_approve)
    ctx.apply_cmd(dir)

@app.command()
def destroy(
    dir: Annotated[str, typer.Option()] = os.getcwd(),
    interactive: Annotated[bool, typer.Option()] = True,
    auto_approve: Annotated[bool, typer.Option()] = False,
):
    ctx = Context.from_cfg_file(dir, interactive, auto_approve)
    ctx.destroy_cmd(dir)
