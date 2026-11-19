"""Snowflake connection helper.

Credentials are NEVER hard-coded. Everything comes from environment variables:

    SNOWFLAKE_ACCOUNT               e.g. "myorg-myaccount"      (required)
    SNOWFLAKE_USER                                                (required)
    SNOWFLAKE_PASSWORD              prompted if missing (and no private key is set)
    SNOWFLAKE_MFA_PASSCODE          6-digit TOTP code; prompted if missing
    SNOWFLAKE_PRIVATE_KEY_PATH      key-pair auth (no password / MFA needed)
    SNOWFLAKE_PRIVATE_KEY_PASSPHRASE  only if the private key is encrypted
    SNOWFLAKE_ROLE                  optional, defaults to the user's default role
    SNOWFLAKE_WAREHOUSE             default LAB_WH
    SNOWFLAKE_DATABASE              default INSTACART_LAB
    SNOWFLAKE_SCHEMA                default RAW

Interactive runs (password + TOTP) are fine for manual practice. Automated runs
(dbt, Airflow, schedules) should use key-pair authentication.
"""
from __future__ import annotations

import getpass
import os
from pathlib import Path

import snowflake.connector


def _require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _load_private_key_der(path: str, passphrase: str | None) -> bytes:
    """Read a PEM private key and return it as unencrypted PKCS#8 DER bytes."""
    from cryptography.hazmat.primitives import serialization

    key = serialization.load_pem_private_key(
        Path(path).read_bytes(),
        password=passphrase.encode() if passphrase else None,
    )
    return key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )


def get_connection() -> snowflake.connector.SnowflakeConnection:
    params: dict = {
        "account": _require("SNOWFLAKE_ACCOUNT"),
        "user": _require("SNOWFLAKE_USER"),
        "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE", "LAB_WH"),
        "database": os.getenv("SNOWFLAKE_DATABASE", "INSTACART_LAB"),
        "schema": os.getenv("SNOWFLAKE_SCHEMA", "RAW"),
    }
    if os.getenv("SNOWFLAKE_ROLE"):
        params["role"] = os.environ["SNOWFLAKE_ROLE"]

    key_path = os.getenv("SNOWFLAKE_PRIVATE_KEY_PATH")
    if key_path:
        params["private_key"] = _load_private_key_der(
            key_path, os.getenv("SNOWFLAKE_PRIVATE_KEY_PASSPHRASE")
        )
    else:
        params["password"] = os.getenv("SNOWFLAKE_PASSWORD") or getpass.getpass(
            "Snowflake password: "
        )
        passcode = os.getenv("SNOWFLAKE_MFA_PASSCODE") or getpass.getpass(
            "MFA / TOTP passcode (leave empty to skip): "
        )
        if passcode:
            params["passcode"] = passcode

    return snowflake.connector.connect(**params)
