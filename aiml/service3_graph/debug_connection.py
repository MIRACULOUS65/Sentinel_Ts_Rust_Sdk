import httpx
import asyncio
import os

SERVICE1_URL = "https://sentinel-653o.onrender.com"

async def test_fetch():
    print(f"Attempting to fetch from: {SERVICE1_URL}/explorer/transactions/recent?limit=10")
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(f"{SERVICE1_URL}/explorer/transactions/recent?limit=10")
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Success! Received {len(data.get('transactions', []))} transactions.")
                print("Sample Data:", str(data)[:200])
            else:
                print("Failed with status:", response.status_code)
                print("Response:", response.text)
    except Exception as e:
        print(f"Exception occurred: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(test_fetch())
