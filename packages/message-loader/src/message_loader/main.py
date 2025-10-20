import json
from collections.abc import Sequence
from pathlib import Path

from jinja2 import Environment, StrictUndefined, Template, meta


class MessagesFileNotExistsError(Exception): ...


class MessagesFileExtensionError(Exception):
    def __str__(self):
        return "messages file extension is incorrect"


class MessageIdNotFoundError(Exception):
    def __init__(self, msg_id: str):
        super().__init__()
        self.msg_id: str = msg_id

    def __str__(self):
        return f"message id {self.msg_id} was not found in the messages file"


class MissingTemplateVariables(Exception):
    def __init__(self, vars: Sequence[str]):
        super().__init__()
        self.vars: Sequence[str] = vars

    def __str__(self):
        return (
            "message template is missing varibles: "
            f"{', '.join(f'`{var}`' for var in self.vars)}"
        )


class MessageLoader:
    def __init__(self, messages_file: str | Path):
        self._messages_file_path: Path = (
            messages_file if isinstance(messages_file, Path) else Path(messages_file)
        )
        if not self._messages_file_path.exists():
            raise MessagesFileNotExistsError
        if self._messages_file_path.suffix != ".json":
            raise MessagesFileExtensionError
        with self._messages_file_path.open(encoding="utf-8") as f:
            self._message_dict: dict[str, str] = json.loads(f.read())
        self._env = Environment()

    def render_msg(self, msg_id: str, **kwargs) -> str:
        if msg_id not in self._message_dict:
            raise MessageIdNotFoundError(msg_id)
        msg: str = self._message_dict[msg_id]
        vars = meta.find_undeclared_variables(self._env.parse(msg))
        missing_vars: set[str] = vars.difference(kwargs.keys())
        if len(missing_vars) > 0:
            raise MissingTemplateVariables(list(missing_vars))
        return Template(msg, undefined=StrictUndefined).render(kwargs)
