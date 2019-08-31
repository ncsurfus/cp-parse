"""
Provides methods for reading tokens from the Check Point configuration format.
"""

from .token import TokenType, read_token, read_token_name, read_token_var, read_token_quoted_var, read_tokens