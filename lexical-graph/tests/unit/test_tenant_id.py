"""Tests for TenantId validation, formatting, and the to_tenant_id factory."""

import pytest
from graphrag_toolkit.lexical_graph.tenant_id import TenantId, to_tenant_id


# --- __init__ validation ---


@pytest.mark.parametrize("value", ["acme", "tenant1", "a.b.c", "x"])
def test_tenant_id_valid(value):
    """Lowercase alphanumeric values (with internal periods) are accepted."""
    t = TenantId(value)
    assert t.value == value


@pytest.mark.parametrize("value", ["UPPER", "a" * 26, ".start", "end.", "has space", "special!"])
def test_tenant_id_invalid_raises(value):
    """Uppercase, too-long, leading/trailing period, spaces, and special chars are rejected."""
    with pytest.raises(ValueError, match="Invalid TenantId"):
        TenantId(value)


def test_tenant_id_default_none():
    """No argument produces the default tenant (value=None)."""
    assert TenantId().value is None


def test_tenant_id_default_string_normalized():
    """The literal 'default_' is normalized to the default tenant."""
    assert TenantId("default_").value is None


# --- is_default_tenant ---


def test_is_default_tenant_true(default_tenant):
    assert default_tenant.is_default_tenant() is True


def test_is_default_tenant_false(custom_tenant):
    assert custom_tenant.is_default_tenant() is False


# --- format_label: default wraps in backticks, custom appends tenant + '__' ---


def test_format_label_default(default_tenant):
    assert default_tenant.format_label("Topic") == "`Topic`"


def test_format_label_custom(custom_tenant):
    assert custom_tenant.format_label("Topic") == "`Topicacme__`"


# --- format_index_name: default unchanged, custom appends _<tenant> ---


def test_format_index_name_default(default_tenant):
    assert default_tenant.format_index_name("my_index") == "my_index"


def test_format_index_name_custom(custom_tenant):
    assert custom_tenant.format_index_name("my_index") == "my_index_acme"


# --- format_hashable: default unchanged, custom prepends <tenant>:: ---


def test_format_hashable_default(default_tenant):
    assert default_tenant.format_hashable("topic::foo") == "topic::foo"


def test_format_hashable_custom(custom_tenant):
    assert custom_tenant.format_hashable("topic::foo") == "acme::topic::foo"


# --- format_id: default uses ::, custom inserts tenant with single colons ---


def test_format_id_default(default_tenant):
    assert default_tenant.format_id("aws", "abc123") == "aws::abc123"


def test_format_id_custom(custom_tenant):
    assert custom_tenant.format_id("aws", "abc123") == "aws:acme:abc123"


# --- rewrite_id: default unchanged, custom inserts tenant after prefix ---


def test_rewrite_id_default(default_tenant):
    assert default_tenant.rewrite_id("aws::abc:def") == "aws::abc:def"


def test_rewrite_id_custom(custom_tenant):
    assert custom_tenant.rewrite_id("aws::abc:def") == "aws:acme:abc:def"


# --- to_tenant_id factory ---


def test_to_tenant_id_none():
    """None returns the global default tenant."""
    result = to_tenant_id(None)
    assert result.is_default_tenant()


def test_to_tenant_id_passthrough():
    """An existing TenantId instance is returned as-is."""
    t = TenantId("acme")
    assert to_tenant_id(t) is t


def test_to_tenant_id_from_string():
    """A string is converted into a TenantId."""
    result = to_tenant_id("acme")
    assert isinstance(result, TenantId)
    assert result.value == "acme"
