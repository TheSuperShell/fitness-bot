from pathlib import Path
from typing import Annotated

import jinja2
import rich
import typer
from jinja2 import meta
from message_loader import (
    MessageLoader,
    MessagesFileExtensionError,
    MessagesFileNotExistsError,
)

app = typer.Typer(
    name="Message Loader tools", help="Dev tools for the message-loader package"
)


@app.command()
def get_vars(
    messages_path: Annotated[Path, typer.Argument()],
    msg_id: Annotated[str, typer.Argument()],
) -> typer.Exit:
    try:
        message_loader = MessageLoader(messages_path)
    except MessagesFileNotExistsError:
        rich.print(f"[red]ERROR[/red]: file {messages_path} does not exist")
        return typer.Exit()
    except MessagesFileExtensionError:
        rich.print("[red]ERROR[/red]: file extension should be json")
        return typer.Exit()

    messages: dict[str, str] = message_loader._message_dict
    if msg_id not in messages:
        rich.print(f"[red]ERROR[/red]: there is no message with id {msg_id}")
        return typer.Exit()

    env = jinja2.Environment()
    variables = meta.find_undeclared_variables(env.parse(messages[msg_id]))
    rich.print("Variables:")
    for var in variables:
        rich.print(f"- [blue bold]{var}[/blue bold]")
    return typer.Exit()
