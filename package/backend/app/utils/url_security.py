import ipaddress
import socket
from urllib.parse import urlparse


def _parse_ip_address(value: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address | None:
    try:
        return ipaddress.ip_address(value)
    except ValueError:
        return None


def _is_disallowed_address(address: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    return (
        not address.is_global
        or address.is_loopback
        or address.is_private
        or address.is_link_local
        or address.is_multicast
        or address.is_reserved
        or address.is_unspecified
        or str(address) == "169.254.169.254"
    )


def validate_external_https_url(value: str) -> str:
    """Validate a model provider Base URL before the server makes outbound requests."""
    normalized = (value or "").strip().rstrip("/")
    if not normalized:
        raise ValueError("Base URL 未配置")

    try:
        parsed = urlparse(normalized)
        port = parsed.port
    except ValueError as exc:
        raise ValueError("Base URL 格式不正确") from exc

    if parsed.scheme.lower() != "https":
        raise ValueError("Base URL 必须使用 https://")
    if not parsed.hostname:
        raise ValueError("Base URL 必须包含有效域名")
    if parsed.username or parsed.password:
        raise ValueError("Base URL 禁止包含用户名或密码")

    hostname = parsed.hostname.strip()
    hostname_for_check = hostname.rstrip(".").lower()
    if hostname_for_check in {"localhost"} or hostname_for_check.endswith(".localhost"):
        raise ValueError("Base URL 禁止指向 localhost")

    hostname_ip = _parse_ip_address(hostname_for_check)
    if hostname_ip is None and "." not in hostname_for_check:
        raise ValueError("Base URL 必须使用公网域名，不能使用单标签主机名")

    try:
        addrinfo = socket.getaddrinfo(hostname, port or 443, type=socket.SOCK_STREAM)
    except OSError as exc:
        raise ValueError("Base URL 域名解析失败") from exc

    resolved_addresses: set[ipaddress.IPv4Address | ipaddress.IPv6Address] = set()
    for item in addrinfo:
        sockaddr = item[4]
        if not sockaddr:
            continue
        resolved_ip = _parse_ip_address(sockaddr[0])
        if resolved_ip is not None:
            resolved_addresses.add(resolved_ip)

    if not resolved_addresses:
        raise ValueError("Base URL 域名没有解析到有效 IP")

    for address in resolved_addresses:
        if _is_disallowed_address(address):
            raise ValueError("Base URL 必须解析到公网 IP，不能指向内网、本机或云元数据地址")

    return normalized
