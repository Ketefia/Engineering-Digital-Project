#!/usr/bin/env python3
"""
GRP Structural Design Assistant — backend regression checks.

This script does not modify application files or engineering calculations.
Run the application first, then execute:

    python verify_calculator.py

Optional server URL:

    python verify_calculator.py http://localhost:8000

Material properties and engineering outputs are only checked where the
API exposes enough information to do so reliably.
"""

from __future__ import annotations

import json
import math
import sys
import urllib.error
import urllib.request
from typing import Any


BASE_URL = (
    sys.argv[1].rstrip("/")
    if len(sys.argv) > 1
    else "http://localhost:8000"
)

passed = 0
failed = 0
skipped = 0


def request(
    path: str,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
) -> tuple[int, Any]:
    """Make an HTTP request and return status plus decoded response."""

    url = BASE_URL + path
    data = None

    headers = {
        "Accept": "application/json",
    }

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(
        url,
        data=data,
        headers=headers,
        method=method,
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            body = response.read().decode("utf-8")
            try:
                return response.status, json.loads(body)
            except json.JSONDecodeError:
                return response.status, body

    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            decoded = json.loads(body)
        except json.JSONDecodeError:
            decoded = body
        return exc.code, decoded

    except Exception as exc:
        raise RuntimeError(
            f"Could not reach {url}: {exc}"
        ) from exc


def check(
    name: str,
    condition: bool,
    detail: str = "",
) -> bool:
    global passed, failed

    if condition:
        passed += 1
        print(f"[PASS] {name}")
        return True

    failed += 1
    print(f"[FAIL] {name}")
    if detail:
        print(f"       {detail}")
    return False


def skip(name: str, reason: str) -> None:
    global skipped
    skipped += 1
    print(f"[SKIP] {name}")
    print(f"       {reason}")


def as_mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def first_key(mapping: dict[str, Any]) -> str | None:
    return next(iter(mapping), None)


def find_numeric(
    obj: Any,
    candidate_keys: tuple[str, ...],
    depth: int = 0,
) -> float | None:
    """Find the first finite numeric value matching a known field name."""

    if depth > 8:
        return None

    if isinstance(obj, dict):
        for key in candidate_keys:
            value = obj.get(key)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                if math.isfinite(float(value)):
                    return float(value)

        for value in obj.values():
            found = find_numeric(
                value,
                candidate_keys,
                depth + 1,
            )
            if found is not None:
                return found

    elif isinstance(obj, list):
        for value in obj:
            found = find_numeric(
                value,
                candidate_keys,
                depth + 1,
            )
            if found is not None:
                return found

    return None


def unwrap_calculation(response: Any) -> dict[str, Any]:
    root = as_mapping(response)
    return as_mapping(root.get("calculation", root))


def main() -> int:
    global passed, failed, skipped

    print("GRP Structural Design Assistant — regression checks")
    print(f"Server: {BASE_URL}")
    print("-" * 64)

    # 1. Backend health
    try:
        status, health = request("/health")
    except RuntimeError as exc:
        print(f"[STOP] {exc}")
        print("Start the backend and run this script again.")
        return 2

    health_data = as_mapping(health)

    check(
        "1. Backend health endpoint",
        status == 200
        and health_data.get("status") == "ok",
        f"HTTP {status}; response={health!r}",
    )

    # 2. Material endpoint
    status, materials_response = request("/materials")
    materials_root = as_mapping(materials_response)
    materials = as_mapping(materials_root.get("materials"))

    materials_ok = status == 200 and bool(materials)

    check(
        "2. Material endpoint returns material records",
        materials_ok,
        f"HTTP {status}; material count={len(materials)}",
    )

    # 3. Profile endpoint
    status, profiles_response = request("/profiles")
    profiles_root = as_mapping(profiles_response)
    profiles = as_mapping(profiles_root.get("profiles"))

    profiles_ok = status == 200 and bool(profiles)

    check(
        "3. Profile endpoint returns profile records",
        profiles_ok,
        f"HTTP {status}; profile count={len(profiles)}",
    )

    if not materials_ok or not profiles_ok:
        print("\nCannot run calculation checks until the catalogue endpoints work.")
        print_summary()
        return 1

    # 4. Confirm rectangular profile factory is available
    rectangular_key = (
        "Rectangular panel strip"
        if "Rectangular panel strip" in profiles
        else None
    )

    check(
        "4. Rectangular panel strip is available",
        rectangular_key is not None,
        f"Available profile keys: {list(profiles.keys())}",
    )

    material_key = first_key(materials)

    if material_key is None:
        print("\nNo material was returned; stopping.")
        print_summary()
        return 1

    # 5. Send a minimal, valid calculation request.
    #
    # These values are API test inputs, not recommended design values.
    # Dimensions are in metres for the rectangular profile factory.
    base_payload: dict[str, Any] = {
        "span": 2.0,
        "tributary_width": 1.0,
        "permanent_load": 0.0,
        "imposed_load": 1000.0,
        "gamma_G": 1.35,
        "gamma_Q": 1.5,
        "support_condition": "simply_supported",
        "material": material_key,
        "profile": rectangular_key or first_key(profiles),
        "allowable_stress": 100000000.0,
        "allowable_deflection": 0.01,
    }

    if rectangular_key:
        base_payload["profile"] = rectangular_key
        base_payload["width"] = 1.0
        base_payload["thickness"] = 0.05

    status, base_response = request(
        "/calculation",
        method="POST",
        payload=base_payload,
    )

    root = as_mapping(base_response)
    base_result = unwrap_calculation(base_response)

    calculation_ok = (
        status == 200
        and root.get("success") is True
        and bool(base_result)
    )

    check(
        "5. Valid calculation request succeeds",
        calculation_ok,
        f"HTTP {status}; response={base_response!r}"
        if not calculation_ok
        else "",
    )

    if not calculation_ok:
        print("\nThe API rejected the test calculation. Check the returned error.")
        print_summary()
        return 1

    # 6. Confirm the response contains structured calculation output.
    check(
        "6. Calculation response is structured JSON",
        isinstance(base_result, dict)
        and len(base_result) > 0,
        f"Returned type: {type(base_result).__name__}",
    )

    # 7. Check that a missing required input is rejected.
    invalid_payload = dict(base_payload)
    invalid_payload.pop("span", None)

    invalid_status, invalid_response = request(
        "/calculation",
        method="POST",
        payload=invalid_payload,
    )

    check(
        "7. Missing required input is rejected",
        invalid_status == 400
        and isinstance(invalid_response, dict)
        and "error" in invalid_response,
        f"HTTP {invalid_status}; response={invalid_response!r}",
    )

    # 8. Increase imposed load and compare a reported moment if available.
    higher_payload = dict(base_payload)
    higher_payload["imposed_load"] = 2000.0

    higher_status, higher_response = request(
        "/calculation",
        method="POST",
        payload=higher_payload,
    )

    higher_root = as_mapping(higher_response)
    higher_result = unwrap_calculation(higher_response)

    check(
        "8. Higher-load calculation request succeeds",
        higher_status == 200
        and higher_root.get("success") is True
        and bool(higher_result),
        f"HTTP {higher_status}; response={higher_response!r}"
        if higher_status != 200
        else "",
    )

    # Use explicit common result names only. If the API schema uses different
    # names, do not guess; inspect the JSON response and map it deliberately.
    moment_keys = (
        "maximum_moment",
        "max_moment",
        "max_bending_moment",
        "maximum_bending_moment",
    )

    base_moment = find_numeric(base_result, moment_keys)
    higher_moment = find_numeric(higher_result, moment_keys)

    if base_moment is not None and higher_moment is not None:
        check(
            "8a. Reported bending moment rises with imposed load",
            higher_moment > base_moment,
            f"Base={base_moment}; higher load={higher_moment}",
        )
    else:
        skip(
            "8a. Bending moment trend",
            "The API output does not expose a recognised scalar moment key. "
            "Inspect its JSON schema before adding a precise assertion.",
        )

    # 9. Inspect the result for non-finite values.
    def contains_nonfinite(value: Any) -> bool:
        if isinstance(value, float):
            return not math.isfinite(value)
        if isinstance(value, dict):
            return any(contains_nonfinite(v) for v in value.values())
        if isinstance(value, list):
            return any(contains_nonfinite(v) for v in value)
        return False

    check(
        "9. Calculation output contains no non-finite numbers",
        not contains_nonfinite(base_response),
        "Found NaN or infinity in the response.",
    )

    # 10. Report whether core engineering checks are actually exposed.
    stress_keys = (
        "maximum_stress",
        "max_stress",
        "bending_stress",
        "stress",
    )
    deflection_keys = (
        "maximum_deflection",
        "max_deflection",
        "maximum_deflection_m",
        "max_deflection_m",
    )
    utilisation_keys = (
        "utilisation",
        "utilization",
        "utilisation_ratio",
        "utilization_ratio",
    )

    stress = find_numeric(base_result, stress_keys)
    deflection = find_numeric(base_result, deflection_keys)
    utilisation = find_numeric(base_result, utilisation_keys)

    exposed = {
        "stress": stress,
        "deflection": deflection,
        "utilisation": utilisation,
    }

    check(
        "10. Engineering result fields are inspectable",
        any(value is not None for value in exposed.values()),
        f"Recognised result fields found: {exposed}",
    )

    print("\nSelected material:", material_key)
    print("Selected profile:", base_payload["profile"])
    print("Returned result keys:", list(base_result.keys()))
    print("Recognised engineering values:", exposed)

    print_summary()

    print(
        "\nImportant: these are API smoke/regression checks, not "
        "independent verification of the structural calculation."
    )
    return 1 if failed else 0


def print_summary() -> None:
    print("-" * 64)
    print(f"Passed: {passed} | Failed: {failed} | Skipped: {skipped}")


if __name__ == "__main__":
    raise SystemExit(main())