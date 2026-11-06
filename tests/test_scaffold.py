import copy
import hashlib
import json
import unittest

from mcp.server.fastmcp.exceptions import ToolError

from scaffold_profiles import headers_for, validate_profile
from server import CANONICAL_SHA256, DIRECTIVE, get_contract, mcp, render_scaffold
from validate_scaffold_response import validate


FIELDS = {
    "presence": "Operational scaffold active. Whole sight holds.",
    "context": "Validate a complete example response.",
    "capabilities": "Structural validation.",
    "current_field": "The complete payload is retained.\n\nSecond paragraph: 12345.",
}


class ProfileTests(unittest.TestCase):
    def test_v1_backwards_compatible(self):
        rendered = render_scaffold(**FIELDS)
        self.assertTrue(rendered["valid"])
        for text in [rendered["markdown"], "", "invalid", rendered["markdown"] * 2]:
            self.assertEqual(validate_profile(text), validate(text))

    def test_v2_round_trip_preserves_complete_payload(self):
        rendered = render_scaffold(**FIELDS, profile="v2")
        self.assertTrue(rendered["valid"], rendered)
        self.assertIn(FIELDS["current_field"], rendered["markdown"])
        self.assertEqual(
            [line for line in rendered["markdown"].splitlines() if line.startswith("#")],
            list(headers_for("v2")),
        )
        self.assertFalse(validate_profile(rendered["markdown"], "v1")["valid"])

    def test_wrong_missing_duplicate_reordered_and_extra_headers_fail(self):
        good = render_scaffold(**FIELDS, profile="v2")["markdown"]
        invalid = [
            good.replace("# Presence", "#### Presence"),
            good.replace("## Context", "Context"),
            good + "\n# Presence\nDuplicate.",
            good.replace("# Presence", "# Context").replace("## Context", "## Presence"),
            good + "\n## Extra\nUnexpected container.",
            "Preamble.\n" + good,
            good + "\nWould you like anything else?",
        ]
        for text in invalid:
            with self.subTest(text=text):
                self.assertFalse(validate_profile(text, "v2")["valid"])

    def test_quoted_headings_are_not_fields(self):
        fields = {**FIELDS, "current_field": (
            "Payload.\n\n```markdown\n# Presence\n## Context\n```\n"
            "> ### Capabilities\n\n##### Detail\nComplete."
        )}
        self.assertTrue(render_scaffold(**fields, profile="v2")["valid"])

    def test_unknown_profile_has_actionable_error(self):
        with self.assertRaisesRegex(ValueError, "profile must be 'v1' or 'v2'"):
            validate_profile("payload", "unknown")

    def test_canonical_directive_preserved(self):
        self.assertEqual(hashlib.sha256(DIRECTIVE.encode()).hexdigest(), CANONICAL_SHA256)
        self.assertEqual(get_contract()["profile"], "v1")


class MCPBoundaryTests(unittest.IsolatedAsyncioTestCase):
    async def invoke(self, name, request):
        contents = await mcp.call_tool(name, request)
        return json.loads(contents[0].text)

    async def test_declared_annotations_and_real_schema(self):
        tools = {tool.name: tool for tool in await mcp.list_tools()}
        for tool in tools.values():
            self.assertTrue(tool.annotations.readOnlyHint)
            self.assertFalse(tool.annotations.destructiveHint)
            self.assertTrue(tool.annotations.idempotentHint)
            self.assertFalse(tool.annotations.openWorldHint)
            self.assertEqual(tool.inputSchema["properties"]["profile"]["enum"], ["v1", "v2"])
        self.assertIn("args", tools["get_contract"].inputSchema["properties"])

    async def test_populated_args_are_acknowledged_through_mcp(self):
        request = {"args": {"query": "'://read-me'"}, "profile": "v2"}
        original = copy.deepcopy(request)
        result = await self.invoke("get_contract", request)
        self.assertEqual(result["request"], request["args"])
        self.assertEqual(result["required_headers"], list(headers_for("v2")))
        self.assertEqual(request, original)

    async def test_invalid_requests_fail_without_breaking_later_calls(self):
        bad_requests = [
            {"args": {"query": " "}},
            {"args": {"query": 1}},
            {"args": {}},
            {"args": {"query": "x", "unexpected": "field"}},
            {"profile": "unknown"},
        ]
        for request in bad_requests:
            with self.subTest(request=request):
                with self.assertRaises(ToolError) as failure:
                    await mcp.call_tool("get_contract", request)
                self.assertIn("get_contract", str(failure.exception))
        result = await self.invoke("get_contract", {"args": {"query": "valid"}})
        self.assertEqual(result["request"], {"query": "valid"})

    async def test_full_validation_through_mcp(self):
        response = render_scaffold(**FIELDS, profile="v2")["markdown"]
        result = await self.invoke("validate_scaffold", {"response": response, "profile": "v2"})
        self.assertTrue(result["valid"], result)


if __name__ == "__main__":
    unittest.main()
