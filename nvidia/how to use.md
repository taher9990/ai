# NVIDIA NIM & NGC Access Tester

A lightweight Python script to validate your NVIDIA API Key and test connectivity to both NVIDIA NIM (Inference Microservices) and the NGC Container Registry.

## Features
* **Validate API Key:** Performs a strict authentication check against the NVIDIA Inference API to ensure your key is active.
* **Test Container Access:** Verifies if your key has permission to pull specific Docker images (e.g., `tensorrt`, `pytorch`) from `nvcr.io`.

## Prerequisites
* Python 3.x
* `requests` library

## Setup & Installation

1.  **Clone the repository** (or download the script):
    ```bash
    git clone [https://github.com/YOUR_USERNAME/YOUR_REPO.git](https://github.com/YOUR_USERNAME/YOUR_REPO.git)
    cd YOUR_REPO
    ```

2.  **Install dependencies:**
    ```bash
    pip install requests
    ```
    *(On Linux/Mac, you might need `pip3 install requests`)*

## Usage

Run the script using Python:

```bash
python nvidia_final.py
