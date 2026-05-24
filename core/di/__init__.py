"""
Dependency Injection module
"""
from .container import container, DIContainer
from .providers import ServiceProvider

__all__ = ['container', 'DIContainer', 'ServiceProvider']