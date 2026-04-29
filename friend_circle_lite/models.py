"""Domain models for Friend-Circle-Lite.

These models centralize the core concepts used across the crawler so that the
transport layer, parsing logic, cache logic, and output formatting can evolve
independently.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from zoneinfo import ZoneInfo


SHANGHAI_TZ = ZoneInfo("Asia/Shanghai")


@dataclass(slots=True)
class Website:
    """Represents a friend website entry from the upstream friend list."""

    name: str
    url: str
    avatar: str = ""

    @classmethod
    def from_friend_item(cls, raw_friend: list | tuple) -> "Website":
        """Create a website from the existing `[name, url, avatar]` structure."""
        name, url, avatar = raw_friend
        return cls(name=name, url=url, avatar=avatar or "")

    def to_error_payload(self) -> list[str]:
        """Return the legacy structure used by `errors.json`."""
        return [self.name, self.url, self.avatar]


@dataclass(slots=True)
class Article:
    """Represents one crawled article belonging to a website."""

    title: str
    author: str
    link: str
    published: str
    summary: str = ""
    content: str = ""
    avatar: str = ""

    def to_public_dict(self) -> dict[str, str]:
        """Return the legacy public article schema used by `all.json`."""
        return {
            "title": self.title,
            "created": self.published,
            "link": self.link,
            "author": self.author,
            "avatar": self.avatar,
        }

    def to_tracking_dict(self) -> dict[str, str]:
        """Return the article schema used by the latest article tracker."""
        return {
            "title": self.title,
            "author": self.author,
            "link": self.link,
            "published": self.published,
            "summary": self.summary,
            "content": self.content,
        }


@dataclass(slots=True)
class FeedEndpoint:
    """Represents a concrete feed endpoint and how it was found."""

    url: str
    feed_type: str
    source: str


@dataclass(slots=True)
class CacheRecord:
    """Represents one cached RSS endpoint mapping for a website."""

    name: str
    url: str
    source: str = "cache"

    def to_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "url": self.url,
        }


@dataclass(slots=True)
class CacheUpdate:
    """Describes how a crawl should update the persisted RSS cache."""

    action: str = "none"
    name: str | None = None
    url: str | None = None
    reason: str = ""

    def to_dict(self) -> dict[str, str | None]:
        return {
            "action": self.action,
            "name": self.name,
            "url": self.url,
            "reason": self.reason,
        }


@dataclass(slots=True)
class CrawlResult:
    """Represents the crawl result for a single website."""

    website: Website
    status: str
    articles: list[Article] = field(default_factory=list)
    feed_url: str | None = None
    feed_type: str = "none"
    source_used: str = "none"
    cache_update: CacheUpdate = field(default_factory=CacheUpdate)

    def to_legacy_dict(self) -> dict[str, object]:
        return {
            "name": self.website.name,
            "status": self.status,
            "articles": [article.to_public_dict() for article in self.articles],
            "feed_url": self.feed_url,
            "feed_type": self.feed_type,
            "cache_update": self.cache_update.to_dict(),
            "source_used": self.source_used,
        }


@dataclass(slots=True)
class CrawlStatistics:
    """Aggregated crawl statistics for the generated `all.json` output."""

    friends_num: int = 0
    active_num: int = 0
    error_num: int = 0
    article_num: int = 0
    last_updated_time: str = ""

    @classmethod
    def create(cls, friends_num: int, active_num: int, error_num: int, article_num: int) -> "CrawlStatistics":
        return cls(
            friends_num=friends_num,
            active_num=active_num,
            error_num=error_num,
            article_num=article_num,
            last_updated_time=datetime.now(SHANGHAI_TZ).strftime("%Y-%m-%d %H:%M:%S"),
        )

    def to_dict(self) -> dict[str, int | str]:
        return {
            "friends_num": self.friends_num,
            "active_num": self.active_num,
            "error_num": self.error_num,
            "article_num": self.article_num,
            "last_updated_time": self.last_updated_time,
        }
