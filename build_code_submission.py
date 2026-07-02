import os

files_to_bundle = [
    ('server.py', 'python'),
    ('public/js/app.js', 'javascript'),
    ('public/css/style.css', 'css'),
    ('public/index.html', 'html'),
    ('public/comparison.html', 'html'),
    ('public/calculator.html', 'html'),
    ('public/assessment.html', 'html'),
    ('public/roadmap.html', 'html'),
    ('public/case-studies.html', 'html'),
    ('public/literature.html', 'html'),
]

output_filename = 'SOURCE_CODE_SUBMISSION.md'

print(f"Bundling {len(files_to_bundle)} source code files into {output_filename}...")

with open(output_filename, 'w', encoding='utf-8') as outfile:
    outfile.write("# Project Source Code Submission\n")
    outfile.write("### Project: Enhancing Small Business Efficiency through Cloud-Based IT Solutions\n\n")
    outfile.write("This document aggregates all the backend and frontend source files developed for the project.\n\n")
    outfile.write("---\n\n")

    for filepath, lang in files_to_bundle:
        if os.path.exists(filepath):
            outfile.write(f"## File: `{filepath}`\n\n")
            outfile.write(f"```{lang}\n")
            with open(filepath, 'r', encoding='utf-8') as infile:
                outfile.write(infile.read())
            outfile.write("\n```\n\n")
            outfile.write("---\n\n")
            print(f"Added {filepath}")
        else:
            print(f"File not found: {filepath}")

print(f"\nSuccessfully generated {output_filename}!")
print("You can open this markdown file in VS Code, a browser, or a markdown viewer and print it directly to PDF.")
