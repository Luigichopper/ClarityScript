import re
from enum import Enum, auto
from typing import List, Tuple, Optional


class TokenType(Enum):
    ELEMENT = auto()
    ATTRIBUTE = auto()
    CONTENT = auto()
    VARIABLE_DECL = auto()
    VARIABLE_REF = auto()
    COLON = auto()
    STRING = auto()
    FOR_LOOP = auto()
    IF_STATEMENT = auto()
    ELSE_STATEMENT = auto()
    COMPONENT_DEF = auto()
    COMPONENT_USE = auto()
    COMMENT = auto()
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()
    EOF = auto()
    MULTILINE_STRING = auto()  # Added for triple-quoted strings


class Token:
    def __init__(self, token_type: TokenType, value: str, line: int, column: int):
        self.type = token_type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, '{self.value}', line={self.line}, col={self.column})"


class Lexer:
    def __init__(self, source_code: str):
        self.source = source_code
        self.tokens: List[Token] = []
        self.position = 0
        self.line = 1
        self.column = 1
        self.indent_stack = [0]  # Start with no indentation

    def tokenize(self) -> List[Token]:
        while self.position < len(self.source):
            # Skip whitespace at the beginning of lines
            if self.position == 0 or self.source[self.position - 1] == '\n':
                self._handle_indentation()

            # Process current character
            if self.position >= len(self.source):
                break

            char = self.source[self.position]

            # Check for triple quotes (multiline string)
            if self.position + 2 < len(self.source) and self.source[self.position:self.position + 3] == '"""':
                self._tokenize_multiline_string()
            elif char == '#':
                self._tokenize_comment()
            elif char == '"' or char == "'":
                self._tokenize_string()
            elif char == '$':
                if self._is_variable_declaration():
                    self._tokenize_variable_declaration()
                else:
                    self._tokenize_variable_reference()
            elif char == ':':
                self.tokens.append(Token(TokenType.COLON, ':', self.line, self.column))
                self._advance()
            elif char == '@':
                if self._is_component_definition():
                    self._tokenize_component_definition()
                else:
                    self._tokenize_component_use()
            elif char == '\n':
                self.tokens.append(Token(TokenType.NEWLINE, '\n', self.line, self.column))
                self._advance()
                self.line += 1
                self.column = 1
            elif self._is_for_loop():
                self._tokenize_for_loop()
            elif self._is_if_statement():
                self._tokenize_if_statement()
            elif self._is_else_statement():
                self._tokenize_else_statement()
            elif char.isalpha() or char == '_':
                self._tokenize_element_or_attribute()
            else:
                # Skip other characters
                self._advance()

        # Add any remaining DEDENT tokens
        while self.indent_stack[-1] > 0:
            self.indent_stack.pop()
            self.tokens.append(Token(TokenType.DEDENT, '', self.line, self.column))

        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, '', self.line, self.column))

        return self.tokens

    def _advance(self, count: int = 1) -> None:
        self.position += count
        self.column += count

    def _peek(self, offset: int = 0) -> Optional[str]:
        if self.position + offset >= len(self.source):
            return None
        return self.source[self.position + offset]

    def _handle_indentation(self) -> None:
        # Count spaces at the beginning of the line
        indent = 0
        start_pos = self.position

        while self.position < len(self.source) and self.source[self.position].isspace() and self.source[
            self.position] != '\n':
            indent += 1
            self._advance()

        # Skip empty lines or comment lines
        if self.position < len(self.source) and (
                self.source[self.position] == '\n' or self.source[self.position] == '#'):
            return

        # Compare with current indentation level
        current_indent = self.indent_stack[-1]

        if indent > current_indent:
            # Increased indentation
            self.indent_stack.append(indent)
            self.tokens.append(Token(TokenType.INDENT, ' ' * indent, self.line, start_pos + 1))
        elif indent < current_indent:
            # Decreased indentation
            while indent < self.indent_stack[-1]:
                self.indent_stack.pop()
                self.tokens.append(Token(TokenType.DEDENT, '', self.line, start_pos + 1))

            if indent != self.indent_stack[-1]:
                raise SyntaxError(f"Inconsistent indentation at line {self.line}")

    def _tokenize_comment(self) -> None:
        # Single line comment
        start_pos = self.position

        while self.position < len(self.source) and self.source[self.position] != '\n':
            self._advance()

        comment = self.source[start_pos:self.position]
        self.tokens.append(Token(TokenType.COMMENT, comment, self.line, start_pos + 1))

    def _tokenize_multiline_string(self) -> None:
        # Handle triple-quoted strings like """content"""
        start_pos = self.position
        start_line = self.line
        self._advance(3)  # Skip opening triple quotes

        # Find the closing triple quotes
        closing_found = False
        while self.position < len(self.source) - 2:
            if self.source[self.position:self.position + 3] == '"""':
                closing_found = True
                break

            if self.source[self.position] == '\n':
                self.line += 1
                self.column = 1

            self._advance()

        if not closing_found:
            raise SyntaxError(f"Unterminated multi-line string starting at line {start_line}")

        # Include the closing triple quotes
        string_value = self.source[start_pos:self.position + 3]
        self.tokens.append(Token(TokenType.MULTILINE_STRING, string_value, start_line, start_pos + 1))
        self._advance(3)  # Skip closing triple quotes

    def _tokenize_string(self) -> None:
        start_pos = self.position
        quote_char = self.source[self.position]
        self._advance()  # Skip opening quote

        # Find the closing quote
        closing_found = False
        while self.position < len(self.source):
            if self.source[self.position] == quote_char and (
                    self.position == 0 or self.source[self.position - 1] != '\\'):
                closing_found = True
                break

            if self.source[self.position] == '\n':
                self.line += 1
                self.column = 1

            self._advance()

        if not closing_found:
            raise SyntaxError(f"Unterminated string at line {self.line}")

        string_value = self.source[start_pos:self.position + 1]
        self.tokens.append(Token(TokenType.STRING, string_value, self.line, start_pos + 1))
        self._advance()  # Skip closing quote

    def _is_variable_declaration(self) -> bool:
        # Check if this is a variable declaration like $var = value
        i = self.position + 1
        while i < len(self.source) and (self.source[i].isalnum() or self.source[i] == '_'):
            i += 1

        while i < len(self.source) and self.source[i].isspace():
            i += 1

        return i < len(self.source) and self.source[i] == '='

    def _tokenize_variable_declaration(self) -> None:
        start_pos = self.position
        self._advance()  # Skip $

        # Get variable name
        while self.position < len(self.source) and (
                self.source[self.position].isalnum() or self.source[self.position] == '_'):
            self._advance()

        # Skip whitespace
        while self.position < len(self.source) and self.source[self.position].isspace():
            self._advance()

        # Skip =
        if self.position < len(self.source) and self.source[self.position] == '=':
            self._advance()
        else:
            raise SyntaxError(f"Expected = in variable declaration at line {self.line}")

        # Skip whitespace
        while self.position < len(self.source) and self.source[self.position].isspace():
            self._advance()

        # Get value until end of line or comment
        value_start = self.position
        while self.position < len(self.source) and self.source[self.position] != '\n' and self.source[
            self.position] != '#':
            self._advance()

        decl = self.source[start_pos:self.position].strip()
        self.tokens.append(Token(TokenType.VARIABLE_DECL, decl, self.line, start_pos + 1))

    def _tokenize_variable_reference(self) -> None:
        start_pos = self.position
        self._advance()  # Skip $

        # Get variable name
        while self.position < len(self.source) and (
                self.source[self.position].isalnum() or self.source[self.position] == '_'):
            self._advance()

        var_ref = self.source[start_pos:self.position]
        self.tokens.append(Token(TokenType.VARIABLE_REF, var_ref, self.line, start_pos + 1))

    def _is_for_loop(self) -> bool:
        if self.position + 3 < len(self.source):
            return self.source[self.position:self.position + 4] == 'for ' and self._check_keyword_boundary(4)
        return False

    def _tokenize_for_loop(self) -> None:
        start_pos = self.position

        # Find the end of the for loop statement
        while self.position < len(self.source) and self.source[self.position] != ':' and self.source[
            self.position] != '\n':
            self._advance()

        for_loop = self.source[start_pos:self.position].strip()
        self.tokens.append(Token(TokenType.FOR_LOOP, for_loop, self.line, start_pos + 1))

    def _is_if_statement(self) -> bool:
        if self.position + 2 < len(self.source):
            return self.source[self.position:self.position + 3] == 'if ' and self._check_keyword_boundary(2)
        return False

    def _tokenize_if_statement(self) -> None:
        start_pos = self.position

        # Find the end of the if statement
        while self.position < len(self.source) and self.source[self.position] != ':' and self.source[
            self.position] != '\n':
            self._advance()

        if_stmt = self.source[start_pos:self.position].strip()
        self.tokens.append(Token(TokenType.IF_STATEMENT, if_stmt, self.line, start_pos + 1))

    def _is_else_statement(self) -> bool:
        if self.position + 4 < len(self.source):
            return self.source[self.position:self.position + 5] == 'else:' or (
                    self.source[self.position:self.position + 4] == 'else' and
                    self.source[self.position + 4].isspace()
            )
        return False

    def _tokenize_else_statement(self) -> None:
        start_pos = self.position

        # Find the end of the else statement
        while self.position < len(self.source) and self.source[self.position] != ':' and self.source[
            self.position] != '\n':
            self._advance()

        if self.position < len(self.source) and self.source[self.position] == ':':
            self._advance()  # Include the colon

        else_stmt = self.source[start_pos:self.position].strip()
        self.tokens.append(Token(TokenType.ELSE_STATEMENT, else_stmt, self.line, start_pos + 1))

    def _is_component_definition(self) -> bool:
        # @component Name(params):
        if self.position + 9 < len(self.source):
            return self.source[self.position:self.position + 10] == '@component'
        return False

    def _tokenize_component_definition(self) -> None:
        start_pos = self.position

        # Find the end of the component definition
        while self.position < len(self.source) and self.source[self.position] != ':' and self.source[
            self.position] != '\n':
            self._advance()

        if self.position < len(self.source) and self.source[self.position] == ':':
            self._advance()  # Include the colon

        comp_def = self.source[start_pos:self.position].strip()
        self.tokens.append(Token(TokenType.COMPONENT_DEF, comp_def, self.line, start_pos + 1))

    def _is_component_use(self) -> bool:
        # @ComponentName(...):
        return self.position < len(self.source) and self.source[self.position] == '@' and self._peek(1) and self._peek(
            1).isalpha()

    def _tokenize_component_use(self) -> None:
        start_pos = self.position

        # Find the end of the component use
        while self.position < len(self.source) and self.source[self.position] != '\n':
            if self.source[self.position] == ':':
                self._advance()  # Include the colon
                break
            self._advance()

        comp_use = self.source[start_pos:self.position].strip()
        self.tokens.append(Token(TokenType.COMPONENT_USE, comp_use, self.line, start_pos + 1))

    def _tokenize_element_or_attribute(self) -> None:
        start_pos = self.position

        # Read element name or attribute
        while self.position < len(self.source) and (
                self.source[self.position].isalnum() or self.source[self.position] in '_-'):
            self._advance()

        # Check what follows
        next_non_space = None
        i = self.position
        while i < len(self.source) and self.source[i].isspace() and self.source[i] != '\n':
            i += 1

        if i < len(self.source):
            next_non_space = self.source[i]

        element_name = self.source[start_pos:self.position]

        # If followed by a colon or space, it's an element
        if next_non_space == ':' or (next_non_space and next_non_space != '\n' and next_non_space != '#'):
            self.tokens.append(Token(TokenType.ELEMENT, element_name, self.line, start_pos + 1))

            # Process attributes
            if next_non_space != ':':
                attr_start = self.position
                while self.position < len(self.source) and self.source[self.position] != ':' and self.source[
                    self.position] != '\n':
                    self._advance()

                attributes = self.source[attr_start:self.position].strip()
                if attributes:
                    self.tokens.append(Token(TokenType.ATTRIBUTE, attributes, self.line, attr_start + 1))
        else:
            # Otherwise, treat as content
            self.tokens.append(Token(TokenType.CONTENT, element_name, self.line, start_pos + 1))

    def _check_keyword_boundary(self, keyword_length: int) -> bool:
        """Check if the keyword is properly separated from other code."""
        after_pos = self.position + keyword_length
        if after_pos >= len(self.source):
            return True
        return not (self.source[after_pos].isalnum() or self.source[after_pos] == '_')