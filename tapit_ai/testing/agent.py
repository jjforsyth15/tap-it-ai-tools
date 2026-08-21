import asyncio
from tapit_ai.testing.scenarios import test_login

async def run_app_tests():
    print("Running TapIt user journey tests...\n")
    result = await test_login()
    
    status_icon = "✅" if result.status == "passed" else "❌"
    
    print(f"{status_icon} {result.scenario}")
    print(f"{result.summary}")
    
    for detail in result.details:
        print(f"  - {detail}")
        
    return result


def run():
    return asyncio.run(run_app_tests())