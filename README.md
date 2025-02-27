# ClarityScript Programming Language

## Overview

Clarity is a programming language that combines the functionality of HTML with the readability of Python. It provides a more intuitive, indentation-based approach to creating web content that eliminates the verbosity of HTML while preserving its power.

## Features

- **Python-like Syntax**: Use indentation for nesting instead of closing tags
- **Variables**: Easily define and reuse content with variables
- **Control Flow**: Include conditionals and loops directly in your markup
- **Components**: Create reusable components with parameters
- **CSS and JavaScript Integration**: Seamlessly include styles and scripts

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/Luigichopper/ClarityScript
   cd clarity-language
   ```

2. Make sure you have Python 3.6+ installed

3. Run the compiler:
   ```bash
   python clarity.py input.clar output.html
   ```

## Example

Here's a simple example of Clarity code:

```python
$title = "Hello, Clarity!"

document:
    head:
        title: $title
        meta charset="utf-8"
        style:
            """
            body {
                font-family: sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            """
    body:
        h1: $title
        p: "Welcome to Clarity, where HTML meets Python!"
        
        # A simple component example
        @Button("Click Me", "primary")
        
        # Looping through items
        ul:
            for item in ["Simple", "Readable", "Powerful"]:
                li: item

# Component definition
@component Button(text, type="default"):
    button class=f"btn btn-{type}": text
```

## Clarity Syntax Guide

### Basic Elements and Attributes

```python
element_name attribute1="value1" attribute2="value2":
    nested_element: "Content"
```

### Variables

```python
$variable_name = "Variable value"
element: $variable_name
```

### Conditionals

```python
if $is_logged_in:
    p: "Welcome back!"
else:
    a href="/login": "Log in"
```

### Loops

```python
ul:
    for item in $items:
        li: item
```

### Components

```python
# Define a component
@component Card(title, body, footer=None):
    div class="card":
        div class="card-header": title
        div class="card-body": body
        if footer:
            div class="card-footer": footer

# Use a component
@Card("My Title", "Card content")
@Card("With Footer", "More content", footer="Footer text")
```

### Special Blocks (CSS and JavaScript)

```python
style:
    """
    .container {
        max-width: 1200px;
        margin: 0 auto;
    }
    """

script:
    """
    document.addEventListener('DOMContentLoaded', function() {
        console.log('Page loaded!');
    });
    """
```

## File Structure

- **clarity.py** - Main entry point
- **clarity_lexer.py** - Tokenizes Clarity code
- **clarity_parser.py** - Parses tokens into AST
- **clarity_ast.py** - AST node definitions
- **clarity_compiler.py** - Generates HTML from AST

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Inspired by the readability of Python and the functionality of HTML
- Created for developers who prefer clean, minimal syntax
