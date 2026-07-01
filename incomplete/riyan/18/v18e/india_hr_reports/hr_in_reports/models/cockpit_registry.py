# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

"""Registry for HR cockpit metric providers (registered by companion modules)."""

_COCKPIT_PROVIDERS = {}


def register_cockpit_provider(key, provider_cls):
    """Register a provider class with staticmethod collect(env, filters) -> dict segment."""
    if not key or not isinstance(key, str):
        raise ValueError("cockpit provider key must be a non-empty string")
    _COCKPIT_PROVIDERS[key] = provider_cls


def iter_cockpit_providers():
    return list(_COCKPIT_PROVIDERS.items())


def clear_cockpit_providers_for_tests():
    """Test hook only."""
    _COCKPIT_PROVIDERS.clear()
