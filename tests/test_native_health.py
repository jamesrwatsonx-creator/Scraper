from __future__ import annotations

from scraper.capabilities import CapabilityCompiler, CapabilityRegistry
from scraper.health import ScraperDoctor
from scraper.models import CapabilityStatus, PageSnapshot
from scraper.native_tools import discover_native_tools


def test_discovers_declarative_and_imperative_webmcp():
    html = """
    <html>
      <body>
        <form
          id="flight-search"
          toolname="search-flights"
          tooldescription="Search available flights"
          toolautosubmit
        >
          <input
            name="origin"
            required
            toolparamdescription="Departure airport"
          >
          <input
            name="passengers"
            type="number"
            min="1"
            max="9"
            required
          >
          <select name="cabin">
            <option value="economy">Economy</option>
            <option value="business">Business</option>
          </select>
        </form>
        <script>
          document.modelContext.registerTool({name: "show-map"});
        </script>
      </body>
    </html>
    """
    snapshot = PageSnapshot(
        url="https://travel.example.com/search",
        title="Travel",
        text="Search available flights",
        html=html,
    )

    discovery = discover_native_tools(snapshot)

    assert discovery.imperative_api_detected is True
    assert discovery.has_native_tools is True
    assert len(discovery.declarative_tools) == 1
    tool = discovery.declarative_tools[0]
    assert tool.name == "search-flights"
    assert tool.autosubmit is True
    assert tool.form_selector == "form#flight-search"
    assert tool.input_schema["required"] == ["origin", "passengers"]
    assert tool.input_schema["properties"]["passengers"]["type"] == "number"
    assert tool.input_schema["properties"]["cabin"]["enum"] == [
        "economy",
        "business",
    ]


def test_doctor_reports_degraded_domain(tmp_path):
    registry = CapabilityRegistry(tmp_path)
    compiler = CapabilityCompiler()

    trusted = compiler.compile(
        capability_id="example.search",
        domain="example.com",
        name="Search",
        description="Search example.com",
        goal="search",
        steps=[{"type": "navigate", "value": "https://example.com"}],
    )
    trusted.status = CapabilityStatus.TRUSTED
    registry.save(trusted)

    degraded = compiler.compile(
        capability_id="example.details",
        domain="example.com",
        name="Details",
        description="Read details",
        goal="details",
        steps=[{"type": "navigate", "value": "https://example.com/details"}],
    )
    degraded.status = CapabilityStatus.DEGRADED
    registry.save(degraded)

    report = ScraperDoctor(registry).inspect("example.com")

    assert report.status == "needs_attention"
    assert report.capability_count == 2
    assert report.domains[0].trusted == 1
    assert report.domains[0].degraded == 1
    assert report.domains[0].status == "needs_attention"


def test_doctor_reports_empty_scope(tmp_path):
    report = ScraperDoctor(CapabilityRegistry(tmp_path)).inspect("missing.example")

    assert report.status == "empty"
    assert report.capability_count == 0
    assert report.issues
