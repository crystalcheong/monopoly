# Workflow

1. Import monthly statements into `./statements/uob`
2. Parse the specific statement
    ```
    /workspaces/monopoly/.venv/bin/monopoly statements/uob/2025-10-uob.pdf --ocr -o output
    ```
