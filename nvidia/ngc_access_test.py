import requests
import json
import sys
import base64

# --- CONFIGURATION ---
# Endpoint for testing text generation (validates key works for AI models)
NIM_API_URL = "https://integrate.api.nvidia.com/v1"
# Endpoint for testing container downloads
REGISTRY_URL = "https://nvcr.io/v2"

def get_key():
    print("\n--- ENTER CREDENTIALS ---")
    print("Please paste your NVIDIA API Key (starts with nvapi-...)")
    key = input("API Key > ").strip()
    return key

def parse_image_uri(uri):
    """
    Parses 'nvcr.io/nvidia/tensorrt:24.03-py3' into repo and tag.
    """
    # Remove protocol if present
    if uri.startswith("https://"): uri = uri[8:]
    if uri.startswith("http://"): uri = uri[7:]
    
    # Remove registry prefix 'nvcr.io/' if present
    if uri.startswith("nvcr.io/"):
        uri = uri[len("nvcr.io/"):]
        
    # Split repo and tag
    parts = uri.split(":")
    if len(parts) == 2:
        return parts[0], parts[1]
    else:
        return uri, "latest"

# --- OPTION 1: VALIDATE KEY (Inference Test) ---
def test_inference_access():
    """
    Tests if the key is valid for generating AI responses (NIM).
    """
    api_key = get_key()
    if not api_key: return

    print("\n--- 🔒 TESTING API KEY (Inference) ---")
    print("Attempting to generate text with 'meta/llama-3.1-8b-instruct'...")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "meta/llama-3.1-8b-instruct",
        "messages": [{"role": "user", "content": "Ping"}],
        "max_tokens": 1
    }

    try:
        response = requests.post(f"{NIM_API_URL}/chat/completions", headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            print("\n✅ SUCCESS: API Key is active and valid for Inference.")
        elif response.status_code == 401:
            print("\n❌ FAILED: 401 Unauthorized.")
            print("   The key is invalid or expired.")
        else:
            print(f"\n⚠️ FAILED: Status {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"\n❌ CONNECTION ERROR: {e}")

# --- OPTION 2: TEST CONTAINER ACCESS (Registry Test) ---
def test_container_access():
    """
    Tests if the key can access/pull a specific container from nvcr.io
    """
    api_key = get_key()
    if not api_key: return

    print("\n--- 🐳 TESTING CONTAINER ACCESS ---")
    print("Enter the full container URI you want to test.")
    print("Example: nvcr.io/nvidia/tensorrt:24.03-py3")
    
    container_uri = input("Container > ").strip()
    if not container_uri:
        print("Error: No container name provided.")
        return

    repo, tag = parse_image_uri(container_uri)
    
    print(f"\nChecking permissions for:")
    print(f"   Repo: {repo}")
    print(f"   Tag:  {tag}")

    try:
        # Step 1: Get Authentication Token from NVIDIA NGC
        # We use the standard Docker Registry Auth flow
        print("\n1. Authenticating with NGC Registry...")
        
        auth_url = f"https://nvcr.io/proxy_auth?scope=repository:{repo}:pull&service=nvcr.io"
        
        # NGC uses username='$oauthtoken' and password=API_KEY
        auth_response = requests.get(auth_url, auth=('$oauthtoken', api_key), timeout=10)

        if auth_response.status_code == 200:
            token = auth_response.json().get('token')
            print("✅ AUTH SUCCESS: Your key is valid for NGC.")
        elif auth_response.status_code == 401:
            print("❌ AUTH FAILED: 401 Unauthorized.")
            print("   Your API key cannot access NVIDIA NGC.")
            return
        else:
            print(f"⚠️ AUTH ERROR: {auth_response.status_code}")
            return

        # Step 2: Check if the Image actually exists (Manifest Check)
        print(f"2. Verifying if image '{tag}' exists...")
        
        manifest_url = f"{REGISTRY_URL}/{repo}/manifests/{tag}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.docker.distribution.manifest.v2+json"
        }
        
        resp = requests.get(manifest_url, headers=headers, timeout=10)
        
        if resp.status_code == 200:
            print(f"\n✅ IMAGE FOUND: Success!")
            print(f"   You have permission to pull '{repo}:{tag}'.")
        elif resp.status_code == 404:
            print(f"\n❌ NOT FOUND (404):")
            print(f"   Authentication passed, but the version/tag '{tag}' does not exist.")
            print("   Please check the version number.")
        elif resp.status_code == 403:
            print(f"\n❌ FORBIDDEN (403):")
            print("   You do not have permission to view this specific container.")
        else:
            print(f"\n⚠️ ERROR: Status {resp.status_code}")

    except Exception as e:
        print(f"\n❌ CONNECTION ERROR: {e}")

def main():
    while True:
        print("\n===============================")
        print("   NVIDIA NIM & REGISTRY TOOL")
        print("===============================")
        print("1. Validate API Key (Inference)")
        print("2. Test Container Access (Docker/NGC)")
        print("q. Quit")
        
        choice = input("\nSelect > ").lower()
        
        if choice == '1':
            test_inference_access()
        elif choice == '2':
            test_container_access()
        elif choice == 'q':
            break

if __name__ == "__main__":
    main()
