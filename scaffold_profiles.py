"""Explicit v2 compatibility without editing the canonical v1 validator."""
from __future__ import annotations

import re
from typing import Literal

from validate_scaffold_response import REQUIRED_HEADERS, mask_noncontent, validate

Profile = Literal["v1", "v2"]
PROFILES = {
    "v1": tuple(f"#### {name}" for name in REQUIRED_HEADERS),
    "v2": tuple(f"{'#' * level} {name}" for level, name in enumerate(REQUIRED_HEADERS, 1)),
}
HEADING = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*$")


def headers_for(profile: Profile) -> tuple[str, ...]:
    try:
        return PROFILES[profile]
    except (KeyError, TypeError):
        raise ValueError("profile must be 'v1' or 'v2'") from None


def validate_profile(response: str, profile: Profile = "v1") -> dict:
    """Validate the selected hierarchy; never infer or switch profiles."""
    headers = headers_for(profile)
    if profile == "v1":
        return validate(response)

    raw = response.replace("\r\n", "\n")
    lines = raw.split("\n")
    expected = dict(zip(REQUIRED_HEADERS, headers))
    profile_errors = []
    # Normalize only a temporary validation copy. The caller's payload is intact.
    for index, line in enumerate(mask_noncontent(raw).split("\n")):
        match = HEADING.fullmatch(line)
        if not match:
            continue
        marks, name = match.groups()
        if name in expected:
            actual = f"{marks} {name}"
            if actual != expected[name]:
                profile_errors.append(
                    f"wrong heading for v2: expected {expected[name]}, found {actual}"
                )
            lines[index] = f"#### {name}"
        elif len(marks) <= 4:
            profile_errors.append(f"extra response heading: {marks} {name}")

    result = validate("\n".join(lines))
    errors = list(result["errors"])
    for index, error in enumerate(errors):
        for name, header in expected.items():
            error = error.replace(f"#### {name}", header)
        errors[index] = error
    result["errors"] = list(dict.fromkeys(errors + profile_errors))
    result["valid"] = not result["errors"]
    return result
