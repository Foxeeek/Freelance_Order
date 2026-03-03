from __future__ import annotations

from freelance_ai.app.config import get_settings
from freelance_ai.platforms.base import BasePlatform
from freelance_ai.platforms.freelancehunt import FreelancehuntPlatform


def build_platform_registry() -> dict[str, BasePlatform]:
    all_platforms: dict[str, BasePlatform] = {
        FreelancehuntPlatform.platform_name: FreelancehuntPlatform(),
    }
    settings = get_settings()
    return {name: platform for name, platform in all_platforms.items() if name in settings.ENABLED_PLATFORMS}
