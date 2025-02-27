# Example Clarity file (index.clar)
$page_title = "Clarity Demo"
$items = ["Home", "Products", "About", "Contact"]
$is_logged_in = True
$username = "DemoUser"

document:
    head:
        title: $page_title
        meta charset="utf-8"
        meta name="viewport" content="width=device-width, initial-scale=1.0"
        link rel="stylesheet" href="styles.css"
        
        style:
            """
            body {
                font-family: 'Arial', sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                color: #333;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 0 15px;
            }
            .nav-menu {
                display: flex;
                list-style: none;
                padding: 0;
            }
            .nav-menu li {
                margin-right: 15px;
            }
            .card {
                border: 1px solid #ddd;
                border-radius: 4px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
            .card-header {
                background-color: #f5f5f5;
                padding: 10px 15px;
                border-bottom: 1px solid #ddd;
            }
            .card-header h3 {
                margin: 0;
                color: #333;
            }
            .card-body {
                padding: 15px;
            }
            .feature-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }
            .form-group {
                margin-bottom: 15px;
            }
            .form-group label {
                display: block;
                margin-bottom: 5px;
            }
            .form-group input,
            .form-group textarea {
                width: 100%;
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            .btn {
                display: inline-block;
                padding: 8px 16px;
                background-color: #0066cc;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }
            .btn:hover {
                background-color: #0052a3;
            }
            .site-header {
                background-color: #f8f9fa;
                padding: 20px 0;
                margin-bottom: 30px;
            }
            footer {
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #eee;
                text-align: center;
            }
            """

    body:
        header class="site-header":
            div class="container":
                h1: $page_title
                nav:
                    ul class="nav-menu":
                        for item in $items:
                            li: a href="/": item

        main class="container":
            section id="welcome":
                if $is_logged_in:
                    h2: "Welcome back, DemoUser!"
                    p: "We're glad you're here."
                else:
                    h2: "Welcome to Clarity!"
                    p: "Please log in to continue."

            # Features showcase
            section id="features":
                h2: "Features"
                div class="feature-grid":
                    @Card("Readable Syntax", "Clarity makes HTML as readable as Python.")
                    @Card("Easy Components", "Create reusable components with ease.")
                    @Card("Powerful Logic", "Use conditionals and loops directly in your markup.")

            # Contact form
            section id="contact":
                h2: "Contact Us"
                form action="/submit" method="post":
                    div class="form-group":
                        label for="name": "Name:"
                        input type="text" id="name" name="name" required:

                    div class="form-group":
                        label for="email": "Email:"
                        input type="email" id="email" name="email" required:

                    div class="form-group":
                        label for="message": "Message:"
                        textarea id="message" name="message" rows=5:

                    button type="submit" class="btn btn-primary": "Send Message"

        footer:
            div class="container":
                p: "© 2025 Clarity Language"
                p: "Created with simplicity in mind."

        script:
            """
            document.addEventListener('DOMContentLoaded', function() {
                console.log('Clarity page loaded!');

                // Simple form validation
                const form = document.querySelector('form');
                if (form) {
                    form.addEventListener('submit', function(event) {
                        event.preventDefault();
                        alert('Form submitted successfully!');
                    });
                }
            });
            """

# Component definition
@component Card(title, content):
    div class="card":
        div class="card-header":
            h3: title
        div class="card-body":
            p: content