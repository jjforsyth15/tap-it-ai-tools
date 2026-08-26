import asyncio
from tapit_ai.testing.models import TestResult, TestStatus
from tapit_ai.testing.scenarios import SCENARIOS


STATUS_ICONS = {
    TestStatus.PASSED: "PASS",
    TestStatus.WARNING: "WARN",
    TestStatus.FAILED: "FAIL",
}


async def run_app_tests() -> list[TestResult]:
    print("Running TapIt user journey tests...\n")

    results = []

    for scenario in SCENARIOS:
        try:
            result = await scenario()
        except Exception as e:
            result = TestResult(
                scenario=getattr(scenario, "__name__", "unknown scenario"),
                status=TestStatus.FAILED,
                summary="Scenario raised an unhandled exception.",
                details=[str(e)],
            )

        results.append(result)

        status_icon = STATUS_ICONS.get(result.status, "FAIL")

        print(f"{status_icon} {result.scenario}")
        print(f"{result.summary}")

        for detail in result.details:
            print(f"  - {detail}")

        print()

    return results


def run() -> list[TestResult]:
    return asyncio.run(run_app_tests())
