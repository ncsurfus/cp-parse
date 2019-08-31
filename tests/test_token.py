import unittest
import cp_parse


class TestToken(unittest.TestCase):

    def test_read_token(self):
        test_cases = [
            ("\t:test_data (remainder)", "test_data", "(remainder)"),
            ("\t(test_data) remainder", "test_data", ") remainder"),
            ('\t("test_data") remainder', "test_data", ") remainder"),
            ("\t) remainder", "", " remainder"),
            ("\t \n \t ", "", "")
        ]
        for test in test_cases:
            with self.subTest(test=test):
                data = test[0]
                expect_value = test[1]
                expect_remainder = test[2]
                token = cp_parse.read_token(data)
                self.assertEqual(token.value, expect_value)
                self.assertEqual(data[token.offset:], expect_remainder)

    def test_read_token_name(self):
        data = "test_name (test_data)"
        token = cp_parse.read_token_name(data)
        self.assertEqual(token.type, cp_parse.TokenType.OBJECT_NAME)
        self.assertEqual(token.value, "test_name")
        self.assertEqual(data[token.offset:], "(test_data)")

    def test_read_token_var(self):
        for delimiter in [")", "\r", "\n", "\t"]:
            with self.subTest(delimiter=delimiter):
                data = f"test_data{delimiter} :test"
                token = cp_parse.read_token_var(data)
                self.assertEqual(token.type, cp_parse.TokenType.OBJECT_OPEN)
                self.assertEqual(token.value, "test_data")
                self.assertEqual(data[token.offset:], f"{delimiter} :test")

    def test_read_token_quoted_var(self):
        data = 'test_data" :test'
        token = cp_parse.read_token_quoted_var(data)
        self.assertEqual(token.type, cp_parse.TokenType.OBJECT_OPEN)
        self.assertEqual(token.value, "test_data")
        self.assertEqual(data[token.offset:], ' :test')

    def test_read_tokens(self):
        data = """
        (MyConfigFile
            :Networks (
                : (
                    :Network ("127.0.0.1")
                    :Address ("255.255.255.255")
                )
                :Network (
                    :Network (127.0.0.2)
                    :Address (255.255.255.0)
                )
            )
        )
        """
        expectedTokens = [
            (cp_parse.TokenType.OBJECT_OPEN, "MyConfigFile"),
            (cp_parse.TokenType.OBJECT_NAME, "Networks"),
            (cp_parse.TokenType.OBJECT_OPEN, ""),
            (cp_parse.TokenType.OBJECT_NAME, ""),
            (cp_parse.TokenType.OBJECT_OPEN, ""),
            (cp_parse.TokenType.OBJECT_NAME, "Network"),
            (cp_parse.TokenType.OBJECT_OPEN, "127.0.0.1"),
            (cp_parse.TokenType.OBJECT_CLOSE, ""),
            (cp_parse.TokenType.OBJECT_NAME, "Address"),
            (cp_parse.TokenType.OBJECT_OPEN, "255.255.255.255"),
            (cp_parse.TokenType.OBJECT_CLOSE, ""),
            (cp_parse.TokenType.OBJECT_CLOSE, ""),
            (cp_parse.TokenType.OBJECT_NAME, "Network"),
            (cp_parse.TokenType.OBJECT_OPEN, ""),
            (cp_parse.TokenType.OBJECT_NAME, "Network"),
            (cp_parse.TokenType.OBJECT_OPEN, "127.0.0.2"),
            (cp_parse.TokenType.OBJECT_CLOSE, ""),
            (cp_parse.TokenType.OBJECT_NAME, "Address"),
            (cp_parse.TokenType.OBJECT_OPEN, "255.255.255.0"),
            (cp_parse.TokenType.OBJECT_CLOSE, ""),
            (cp_parse.TokenType.OBJECT_CLOSE, ""),
            (cp_parse.TokenType.OBJECT_CLOSE, ""),
            (cp_parse.TokenType.OBJECT_CLOSE, ""),
            (cp_parse.TokenType.WHITESPACE, ""),
            (cp_parse.TokenType.NEED_MORE_DATA, "")
        ]
        tokens = []
        for token in cp_parse.read_tokens(data):
            tokens.append((token.type, token.value))

        self.assertSequenceEqual(expectedTokens, tokens)
