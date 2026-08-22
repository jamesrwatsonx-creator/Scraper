from __future__ import annotations

from contextlib import suppress
from typing import Any

from bs4 import BeautifulSoup, Tag
from pydantic import BaseModel, Field, HttpUrl

from .models import PageSnapshot


class NativeTool(BaseModel):
    name: str
    description: str | None = None
    source: str = "webmcp_declarative"
    form_selector: str
    autosubmit: bool = False
    input_schema: dict[str, Any] = Field(default_factory=dict)


class NativeToolDiscovery(BaseModel):
    url: HttpUrl
    imperative_api_detected: bool = False
    declarative_tools: list[NativeTool] = Field(default_factory=list)

    @property
    def has_native_tools(self) -> bool:
        return self.imperative_api_detected or bool(self.declarative_tools)


def _control_schema(control: Tag) -> dict[str, Any] | None:
    name = control.get("name")
    if not name:
        return None

    tag_name = control.name.lower()
    input_type = str(control.get("type", "text")).lower()
    if tag_name == "input" and input_type in {"hidden", "submit", "button", "reset", "image"}:
        return None

    schema: dict[str, Any] = {}
    if tag_name == "select":
        schema["type"] = "string"
        options = [
            str(option.get("value", option.get_text(strip=True)))
            for option in control.find_all("option")
            if not option.has_attr("disabled")
        ]
        if options:
            schema["enum"] = options
    elif tag_name == "input" and input_type in {"number", "range"}:
        schema["type"] = "number"
    elif tag_name == "input" and input_type == "checkbox":
        schema["type"] = "boolean"
    else:
        schema["type"] = "string"

    description = (
        control.get("toolparamdescription")
        or control.get("aria-label")
        or control.get("title")
    )
    if description:
        schema["description"] = str(description)

    value = control.get("value")
    if value and input_type not in {"checkbox", "radio"}:
        schema["default"] = str(value)

    if control.get("min") is not None and schema["type"] == "number":
        with suppress(ValueError):
            schema["minimum"] = float(str(control.get("min")))
    if control.get("max") is not None and schema["type"] == "number":
        with suppress(ValueError):
            schema["maximum"] = float(str(control.get("max")))

    return schema


def _form_selector(form: Tag, index: int) -> str:
    form_id = form.get("id")
    if form_id:
        return f"form#{form_id}"
    tool_name = form.get("toolname")
    if tool_name:
        escaped = str(tool_name).replace('"', '\\"')
        return f'form[toolname="{escaped}"]'
    return f"form:nth-of-type({index + 1})"


def discover_native_tools(snapshot: PageSnapshot) -> NativeToolDiscovery:
    html = snapshot.html or ""
    soup = BeautifulSoup(html, "html.parser")
    imperative_detected = "document.modelContext.registerTool" in html
    tools: list[NativeTool] = []

    for index, form in enumerate(soup.find_all("form")):
        if not isinstance(form, Tag) or not form.has_attr("toolname"):
            continue

        properties: dict[str, Any] = {}
        required: list[str] = []
        for control in form.find_all(["input", "select", "textarea"]):
            if not isinstance(control, Tag):
                continue
            name = control.get("name")
            schema = _control_schema(control)
            if not name or schema is None:
                continue
            field_name = str(name)
            properties[field_name] = schema
            if control.has_attr("required"):
                required.append(field_name)

        input_schema: dict[str, Any] = {
            "type": "object",
            "properties": properties,
        }
        if required:
            input_schema["required"] = required

        tools.append(
            NativeTool(
                name=str(form.get("toolname")),
                description=(
                    str(form.get("tooldescription"))
                    if form.get("tooldescription") is not None
                    else None
                ),
                form_selector=_form_selector(form, index),
                autosubmit=form.has_attr("toolautosubmit"),
                input_schema=input_schema,
            )
        )

    return NativeToolDiscovery(
        url=snapshot.url,
        imperative_api_detected=imperative_detected,
        declarative_tools=tools,
    )
