"""Provides methods for reading tokens from the Check Point configuration format."""

import collections
import enum

Token = collections.namedtuple("Token", ["value", "type", "offset"])


class TokenType(enum.Enum):
    """Represents the type of token."""
    OBJECT_NAME = 1
    OBJECT_OPEN = 2
    OBJECT_CLOSE = 3
    WHITESPACE = 4
    NEED_MORE_DATA = 5

def read_tokens(data):
    """Returns tokens until more data is needed."""
    while True:
        token = read_token(data)
        data = data[token.offset:]
        yield token

        if token.type == TokenType.NEED_MORE_DATA:
            break

def read_token(data):
    """Returns the first Token found in data.

    If no end of the token was found, the Token type will be NEED_MORE_DATA.
    If only whitespace was found, the Token type will be WHITESPACE.
    If any unexpected data is found, an exception will be thrown.
    """

    # Escape early if there isn't enough data
    if len(data) == 0:
        return Token(value="", type=TokenType.NEED_MORE_DATA, offset=0)

    # Default to whitespace
    value = ""
    type = TokenType.WHITESPACE
    offset = 1

    # Find Token
    # There are a couple different types of tokens
    # WHITESPACE: spaces, \n, \r, \t can all be skipped
    # OBJECT_CLOSE: )
    # OBJECT_OPEN: (value or ("value
    # OBJECT_NAME: :value 
    for i, b in enumerate(data):
        if b == ' ' or b == '\n' or b == '\r' or b == '\t':
            continue
        elif b == ")":
            value, type, offset = ("", TokenType.OBJECT_CLOSE, 1)
        elif i + 2 == len(data):
            value, type, offset = ("", TokenType.NEED_MORE_DATA, 0)
        elif data[i:i + 2] == '("':
            i = i + 2
            value, type, offset = read_token_quoted_var(data[i:])
        elif b == "(":
            i = i + 1
            value, type, offset = read_token_var(data[i:])
        elif b == ":":
            i = i + 1
            value, type, offset = read_token_name(data[i:])
        else:
            raise Exception(f"Invalid File:{data}")
        break
    return Token(value=value, type=type, offset=offset + i)


def read_token_name(data):
    """Reads to the end of an OBJECT_NAME and returns a Token.

    If no end of the token was found, the Token type will be NEED_MORE_DATA.
    """
    for i, b in enumerate(data):
        if b == ' ':
            return Token(value=data[:i], type=TokenType.OBJECT_NAME, offset=i + 1)
    return Token(value="", type=TokenType.NEED_MORE_DATA, offset=0)


def read_token_var(data):
    """Reads to the end of an OBJECT_OPEN and returns a Token.

    If no end of the token was found, the Token type will be NEED_MORE_DATA.
    """
    for i, b in enumerate(data):
        if b == ')' or b == '\n' or b == '\r' or b == '\t':
            return Token(value=data[:i], type=TokenType.OBJECT_OPEN, offset=i)
    return Token(value="", type=TokenType.NEED_MORE_DATA, offset=0)


def read_token_quoted_var(data):
    """Reads to the end of a quoted OBJECT_OPEN and returns a Token.

    If no end of the token was found, the Token type will be NEED_MORE_DATA.
    """
    for i, b in enumerate(data):
        if b == '"':
            return Token(value=data[:i], type=TokenType.OBJECT_OPEN, offset=i + 1)
    return Token(value="", type=TokenType.NEED_MORE_DATA, offset=0)
