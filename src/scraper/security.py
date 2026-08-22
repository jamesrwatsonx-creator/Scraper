from __future__ import annotations

import ipaddress
import socket
from dataclasses import dataclass
from urllib.parse import urlparse


class SecurityError(ValueError):
    pass


@dataclass(frozen=True)
class UrlPolicy:
    allow_private_networks: bool = False
    allowed_schemes: tuple[str, ...] = ("http", "https")

    def validate(self, url: str) -> str:
        parsed = urlparse(url)
        if parsed.scheme not in self.allowed_schemes:
            raise SecurityError(f"unsupported URL scheme: {parsed.scheme!r}")
        if not parsed.hostname:
            raise SecurityError("URL must include a hostname")

        hostname = parsed.hostname.lower()
        if hostname in {"localhost", "localhost.localdomain"}:
            raise SecurityError("localhost targets are blocked")

        if not self.allow_private_networks:
            for address in self._resolve(hostname):
                if self._is_non_public(address):
                    raise SecurityError(f"non-public network target blocked: {address}")

        return url

    @staticmethod
    def _resolve(hostname: str) -> set[ipaddress.IPv4Address | ipaddress.IPv6Address]:
        try:
            infos = socket.getaddrinfo(hostname, None, proto=socket.IPPROTO_TCP)
        except socket.gaierror as exc:
            raise SecurityError(f"could not resolve hostname: {hostname}") from exc
        addresses = set()
        for info in infos:
            addresses.add(ipaddress.ip_address(info[4][0]))
        return addresses

    @staticmethod
    def _is_non_public(address: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
        return any(
            (
                address.is_private,
                address.is_loopback,
                address.is_link_local,
                address.is_multicast,
                address.is_reserved,
                address.is_unspecified,
            )
        )


ALLOWED_BROWSER_STEPS = {
    "navigate",
    "click",
    "fill",
    "wait_for",
    "extract_text",
    "extract_attr",
    "assert_text",
    "assert_url",
}


def validate_step_type(step_type: str) -> None:
    if step_type not in ALLOWED_BROWSER_STEPS:
        raise SecurityError(f"browser step is not allow-listed: {step_type}")
