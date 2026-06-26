from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

USERNAME_RE = re.compile(r"^[a-zA-Z0-9_.-]{3,32}$")
CODE_RE = re.compile(r"^[A-Z0-9_-]{2,32}$")
BARCODE_RE = re.compile(r"^[0-9]{6,32}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def clean_text(value: str | None) -> str:
    return (value or "").strip()


def normalize_code(value: str | None) -> str:
    return clean_text(value).upper().replace(" ", "-")


def require_text(value: str | None, field_name: str, *, max_length: int = 255) -> str:
    text = clean_text(value)
    if not text:
        raise ValueError(f"{field_name} không được để trống")
    if len(text) > max_length:
        raise ValueError(f"{field_name} tối đa {max_length} ký tự")
    return text


def optional_text(value: str | None, *, max_length: int = 255) -> str | None:
    text = clean_text(value)
    if not text:
        return None
    if len(text) > max_length:
        raise ValueError(f"Giá trị tối đa {max_length} ký tự")
    return text


def validate_username(value: str | None) -> str:
    username = require_text(value, "Tên đăng nhập", max_length=32).lower()
    if not USERNAME_RE.match(username):
        raise ValueError("Tên đăng nhập chỉ gồm chữ, số, dấu gạch dưới, gạch ngang hoặc dấu chấm")
    return username


def validate_code(value: str | None, field_name: str = "Mã") -> str:
    code = normalize_code(require_text(value, field_name, max_length=32))
    if not CODE_RE.match(code):
        raise ValueError(f"{field_name} chỉ gồm chữ in hoa, số, gạch ngang hoặc gạch dưới")
    return code


def validate_email(value: str | None) -> str | None:
    email = optional_text(value, max_length=255)
    if email and not EMAIL_RE.match(email):
        raise ValueError("Email không đúng định dạng")
    return email


def validate_barcode(value: str | None) -> str | None:
    barcode = optional_text(value, max_length=32)
    if barcode and not BARCODE_RE.match(barcode):
        raise ValueError("Mã vạch chỉ gồm số và dài từ 6 đến 32 ký tự")
    return barcode


def validate_money(value: str | int | float | Decimal, field_name: str) -> float:
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f"{field_name} phải là số hợp lệ") from None
    if amount < 0:
        raise ValueError(f"{field_name} không được âm")
    return float(amount)


def validate_non_negative_int(value: str | int, field_name: str) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} phải là số nguyên") from None
    if number < 0:
        raise ValueError(f"{field_name} không được âm")
    return number

