# Clarity Language Guide

## Introduction

Clarity is a HTML templating language with Python-like syntax. It combines the functionality of HTML with the readability and elegance of Python's indentation-based structure.

## Installation

1. Download the Clarity compiler files:
   - `clarity.py` - Main entry point
   - `clarity_lexer.py` - Tokenizer
   - `clarity_parser.py` - Parser
   - `clarity_ast.py` - Abstract Syntax Tree nodes
   - `clarity_compiler.py` - HTML generator

2. Make sure you have Python 3.6+ installed

3. Run the compiler:
   ```bash
   python clarity.py input.clar output.html
   ```

## Basic Syntax

### Document Structure

Every Clarity file starts with a `document` element, similar to HTML:

```clarity
document:
    head:
        title: "My Page Title"
    body:
        h1: "Hello, World!"
```

### Elements and Attributes

Elements are defined with a name followed by a colon. Attributes are specified after the element name and before the colon:

```clarity
div class="container" id="main":
    p style="color: blue;": "This is a paragraph"
```

### Content

You can add content to elements in three ways:

1. **Inline content** (after the colon):
   ```clarity
   p: "This is inline content"
   ```

2. **Block content** (indented):
   ```clarity
   div:
       p: "This is a paragraph inside a div"
       span: "And a span"
   ```

3. **Multi-line content** (triple quotes):
   ```clarity
   script:
       """
       function sayHello() {
           alert('Hello!');
       }
       """
   ```

### Variables

Variables are prefixed with `$` and can be used for content or attributes:

```clarity
$title = "My Page"
$color = "blue"

h1: $title
p style=f"color: {$color};": "Colored text"
```

### Loops

You can use `for` loops to iterate over collections:

```clarity
$items = ["Home", "Products", "About"]

ul:
    for item in $items:
        li: item
```

### Conditionals

Use `if` and `else` statements for conditional content:

```clarity
$is_logged_in = True

div:
    if $is_logged_in:
        p: "Welcome back!"
    else:
        a href="/login": "Log in"
```

### Components

Define reusable components with the `@component` directive:

```clarity
@component Button(text, type="primary"):
    button class=f"btn btn-{type}": text

# Usage
@Button("Click Me")
@Button("Submit", type="success")
```

## Advanced Features

### Style Blocks

Style blocks are supported with indentation:

```clarity
style:
    """
    body {
        font-family: sans-serif;
    }
    .container {
        max-width: 1200px;
    }
    """
```

### Script Blocks

JavaScript is supported with triple quotes:

```clarity
script:
    """
    document.addEventListener('DOMContentLoaded', function() {
        console.log('Page loaded');
    });
    """
```

### Comments

Use `#` for single-line comments:

```clarity
# This is a comment
div:  # This is an inline comment
    p: "Content"
```

## Best Practices

1. Use consistent indentation (spaces preferred)
2. Name variables with descriptive names
3. Break complex components into smaller, reusable parts
4. Add comments to clarify intent
5. Keep components small and focused

## Limitations

This initial version of Clarity has some limitations:

1. Limited error handling and reporting
2. No support for complex expressions in conditionals
3. Limited variable interpolation
4. No import/include system for files
5. Basic component system without inheritance

Future versions will address these limitations.
