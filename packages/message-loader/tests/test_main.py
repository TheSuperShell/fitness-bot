from pathlib import Path

import pytest
from message_loader import (
    MessageIdNotFoundError,
    MessageLoader,
    MessagesFileExtensionError,
    MessagesFileNotExistsError,
    MissingTemplateVariables,
)


@pytest.fixture(scope="function")
def file_example(tmp_path) -> Path:
    file = tmp_path / "example.json"
    with file.open("a+") as f:
        f.write("""
        {
            "id_1": "Hello, {{user}}",
            "id_2": "Hello, {{another_user}}"
        }
        """)
    return file


def test_message_loader_missing_file():
    with pytest.raises(MessagesFileNotExistsError):
        MessageLoader(messages_file="random_file_123.json")


def test_message_loder_wrong_extension(tmp_path):
    random_file = tmp_path / "some_file.r"
    with random_file.open("a+") as f:
        f.write("{}")
    with pytest.raises(MessagesFileExtensionError):
        MessageLoader(messages_file=random_file)


def test_message_loader_no_id(file_example):
    message_loader = MessageLoader(file_example)
    with pytest.raises(MessageIdNotFoundError) as e:
        message_loader.render_msg("msg_3")
        assert str(e.value) == "message id msg_3 was not found in the messages file"


def test_message_missing_variable(file_example):
    message_loader = MessageLoader(file_example)
    with pytest.raises(MissingTemplateVariables) as e:
        message_loader.render_msg("id_2")
        assert str(e.value) == "message template is missing variables: `another_user`"


def test_message_loader(file_example):
    message_loader = MessageLoader(file_example)
    assert message_loader.render_msg("id_1", user="user") == "Hello, user"
