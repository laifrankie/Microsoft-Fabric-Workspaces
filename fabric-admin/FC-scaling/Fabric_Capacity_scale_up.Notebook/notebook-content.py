# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# CELL ********************

import os 
import time 
import requests 
from azure.identity import ClientSecretCredential  # explicit, reliable 

API_VERSION = "2023-11-01" 
ARM_SCOPE = "https://management.azure.com/.default" 

os.environ["CLIENT_ID"] = "<your-client-id>"
os.environ["CLIENT_SECRET"] = "<your-client-secret>" 
os.environ["TENANT_ID"] = "<your-tenant-id>" 

SUB_ID = os.environ.get("AZ_SUBSCRIPTION_ID", "<your-Azuresubscription-id>") 
RG = os.environ.get("AZ_RESOURCE_GROUP", "<Resource-group>") 
CAPACITY = os.environ.get("FABRIC_CAPACITY_NAME", "<your-Fabriccapacity-name>") 
def require_env(name: str) -> str: 
    """Read an environment variable or raise a clear error.""" 
    val = os.getenv(name) 
    if not val: 
        raise RuntimeError(f"Missing required environment variable: {name}") 
    return val 
 
TENANT_ID  = require_env("TENANT_ID") 
CLIENT_ID     = require_env("CLIENT_ID") 
CLIENT_SECRET = require_env("CLIENT_SECRET") 
 
cred = ClientSecretCredential(tenant_id=TENANT_ID, client_id=CLIENT_ID, client_secret=CLIENT_SECRET) 
 
def bearer_token(): 
    tok = cred.get_token(ARM_SCOPE) 
    return tok.token 
 
def headers(): 
    return { 
        "Authorization": f"Bearer {bearer_token()}", 
        "Content-Type": "application/json" 
    } 
 
def get_current_capacity_sku(subscription_id, resource_group, 
capacity_name): 
    """Get the CURRENT SKU of a Fabric capacity.""" 
    url = ( 
        f"https://management.azure.com/subscriptions/{subscription_id}" 
        f"/resourceGroups/{resource_group}" 
        f"/providers/Microsoft.Fabric/capacities/{capacity_name}" 
        f"?api-version={API_VERSION}" 
    ) 
    r = requests.get(url, headers=headers()) 
    r.raise_for_status() 
    data = r.json() 
    return data.get("sku", {}).get("name") 
 
def get_next_fsku(current_sku: str) -> str: 
    """ 
    Given an F-SKU like 'F4', return the next SKU = F(value*2). 
    Print error if already at F2048. 
    """ 
 
    # Ensure format is F<number> 
    if not current_sku.startswith("F") or not current_sku[1:].isdigit(): 
        raise ValueError(f"Invalid SKU format: {current_sku}") 
 
    current_val = int(current_sku[1:])     # extract the number 
    max_val = 2048 
 
    if current_val >= max_val: 
        raise ValueError("Error: Already at maximum SKU F2048. Cannot scale higher.") 
 
    next_val = current_val * 2 
    next_sku = f"F{next_val}" 
 
    return next_sku 
 
def scale_capacity(subscription_id, resource_group, capacity_name, target_sku): 
    """Scale Fabric capacity to target_sku (e.g., 'F8', 'F64', 'F256').""" 
    url = (f"https://management.azure.com/subscriptions/{subscription_id}" 
           f"/resourceGroups/{resource_group}" 
           f"/providers/Microsoft.Fabric/capacities/{capacity_name}" 
           f"?api-version={API_VERSION}") 
 
    body = { 
        "sku": {"name": target_sku, "tier": "Fabric"} 
    } 
 
    resp = requests.patch(url, headers=headers(), json=body) 
 
    if resp.status_code in (200, 201): 
        return resp.json() 
 
    if resp.status_code == 202: 
        async_url = resp.headers.get("Azure-AsyncOperation") or resp.headers.get("Location") 
        if not async_url: 
            raise RuntimeError("202 Accepted but no AzureAsyncOperation/Location header to poll.") 
 
        # Poll until status indicates completion, then GET resource 
        for _ in range(120):  # ~10 minutes 
            time.sleep(5) 
            poll = requests.get(async_url, headers=headers()) 
            if poll.status_code == 200: 
                data = poll.json() 
                status = (data.get("status") or data.get("properties", {}).get("provisioningState")) 
                if status and status.lower() in ("succeeded", "updated", "preparing"): 
                    res = requests.get(url, headers=headers()) 
                    if res.status_code == 200: 
                        return res.json() 
                elif status and status.lower() in ("failed", "canceled"): 
                    raise RuntimeError(f"Scaling failed: {data}") 
            # transient errors while ARM propagates: continue 
        raise TimeoutError(f"Scaling did not finish. Poll: {async_url}") 
 
    raise RuntimeError(f"Unexpected response: {resp.status_code} {resp.text}") 
 
if __name__ == "__main__": 
    # Optional: see what SKUs you can move to 
    try: 
        skus = get_current_capacity_sku (SUB_ID, RG, CAPACITY) 
        print("Current SKUs:", skus) 
        target_sku = get_next_fsku(skus) 
        print(print(f"scale up {skus} → {target_sku}") ) 
    except Exception as e: 
        print("Could not list SKUs:", e)        
    try: 
        result = scale_capacity(SUB_ID, RG, CAPACITY, target_sku) 
        print("Final capacity state:", result) 
    except Exception as e: 
        print("Scale failed:", e)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
