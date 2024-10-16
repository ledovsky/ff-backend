from typing import Any

import pytest

from src.recommendations.candidates import CandidatesRetriever
from src.recommendations.meme_queue import generate_with_blender


@pytest.mark.asyncio
async def test_generate_with_blender_below_30():
    async def get_fast_dopamine(
        self,
        user_id: int,
        limit: int = 10,
        exclude_meme_ids: list[int] = [],
    ) -> list[dict[str, Any]]:
        return [
            {"id": 1},
            {"id": 2},
        ]

    async def get_fast_dopamine_empty(
        self,
        user_id: int,
        limit: int = 10,
        exclude_meme_ids: list[int] = [],
    ) -> list[dict[str, Any]]:
        return []

    async def get_best_memes_from_each_source(
        self,
        user_id: int,
        limit: int = 10,
        exclude_meme_ids: list[int] = [],
    ) -> list[dict[str, Any]]:
        return [
            {"id": 3},
            {"id": 4},
        ]

    class TestRetriever(CandidatesRetriever):
        engine_map = {
            "fast_dopamine": get_fast_dopamine,
            "best_meme_from_each_source": get_best_memes_from_each_source,
        }

    candidates = await generate_with_blender(1, 10, 10, TestRetriever())
    assert len(candidates) == 2
    assert candidates[0]["id"] == 1
    assert candidates[1]["id"] == 2

    class TestRetriever(CandidatesRetriever):
        engine_map = {
            "fast_dopamine": get_fast_dopamine_empty,
            "best_memes_from_each_source": get_best_memes_from_each_source,
        }

    candidates = await generate_with_blender(1, 10, 10, TestRetriever())
    assert len(candidates) == 2
    assert candidates[0]["id"] == 3
    assert candidates[1]["id"] == 4


@pytest.mark.asyncio
async def test_generate_with_blender_below_100():
    async def uploaded_memes(
        self,
        user_id: int,
        limit: int = 10,
        exclude_meme_ids: list[int] = [],
    ) -> list[dict[str, Any]]:
        return [
            {"id": 1},
            {"id": 2},
        ]

    async def get_fast_dopamine(
        self,
        user_id: int,
        limit: int = 10,
        exclude_meme_ids: list[int] = [],
    ) -> list[dict[str, Any]]:
        return [
            {"id": 3},
            {"id": 4},
        ]

    async def get_best_memes_from_each_source(
        self,
        user_id: int,
        limit: int = 10,
        exclude_meme_ids: list[int] = [],
    ) -> list[dict[str, Any]]:
        return [
            {"id": 5},
            {"id": 6},
        ]

    async def get_lr_smoothed(
        self,
        user_id: int,
        limit: int = 10,
        exclude_meme_ids: list[int] = [],
    ) -> list[dict[str, Any]]:
        return [
            {"id": 7},
            {"id": 8},
            {"id": 9},
            {"id": 10},
        ]

    class TestRetriever(CandidatesRetriever):
        engine_map = {
            "uploaded_memes": uploaded_memes,
            "fast_dopamine": get_fast_dopamine,
            "best_memes_from_each_source": get_best_memes_from_each_source,
            "lr_smoothed": get_lr_smoothed,
        }

    candidates = await generate_with_blender(1, 10, 40, TestRetriever())
    assert len(candidates) == 10
    # hardcoded values
    assert candidates[0]["id"] == 7
    assert candidates[1]["id"] == 8
    assert candidates[2]["id"] == 9
    assert candidates[3]["id"] == 1
    assert candidates[4]["id"] == 3
    assert candidates[5]["id"] == 4


@pytest.mark.asyncio
async def test_generate_with_blender_above_100():
    async def uploaded_memes(
        self,
        user_id: int,
        limit: int = 10,
        exclude_meme_ids: list[int] = [],
    ) -> list[dict[str, Any]]:
        return [
            {"id": 1},
            {"id": 2},
            {"id": 3},
        ]

    async def like_spread_and_recent_memes(
        self,
        user_id: int,
        limit: int = 10,
        exclude_meme_ids: list[int] = [],
    ) -> list[dict[str, Any]]:
        return [
            {"id": 4},
            {"id": 5},
            {"id": 6},
        ]

    async def get_lr_smoothed(
        self,
        user_id: int,
        limit: int = 10,
        exclude_meme_ids: list[int] = [],
    ) -> list[dict[str, Any]]:
        return [
            {"id": 7},
            {"id": 8},
            {"id": 9},
            {"id": 10},
        ]

    class TestRetriever(CandidatesRetriever):
        engine_map = {
            "uploaded_memes": uploaded_memes,
            "like_spread_and_recent_memes": like_spread_and_recent_memes,
            "lr_smoothed": get_lr_smoothed,
        }

    candidates = await generate_with_blender(
        1, 10, 200, TestRetriever(), random_seed=102
    )
    assert len(candidates) == 10
    # hardcoded values
    assert candidates[0]["id"] == 7
    assert candidates[1]["id"] == 8
    assert candidates[2]["id"] == 1
    assert candidates[3]["id"] == 9
    assert candidates[4]["id"] == 2
    assert candidates[5]["id"] == 10


@pytest.mark.asyncio
async def test_generate_with_blender_empty_above_100():
    async def uploaded_memes(
        self,
        user_id: int,
        limit: int = 10,
        exclude_meme_ids: list[int] = [],
    ) -> list[dict[str, Any]]:
        return []

    async def like_spread_and_recent_memes(
        self,
        user_id: int,
        limit: int = 10,
        exclude_meme_ids: list[int] = [],
    ) -> list[dict[str, Any]]:
        return []

    async def get_lr_smoothed(
        self,
        user_id: int,
        limit: int = 10,
        exclude_meme_ids: list[int] = [],
    ) -> list[dict[str, Any]]:
        return []

    async def top_memes_from_less_seen_sources(
        self,
        user_id: int,
        limit: int = 10,
        exclude_meme_ids: list[int] = [],
    ) -> list[dict[str, Any]]:
        return [
            {"id": 1},
            {"id": 2},
        ]

    async def get_best_memes_from_each_source(
        self,
        user_id: int,
        limit: int = 10,
        exclude_meme_ids: list[int] = [],
    ) -> list[dict[str, Any]]:
        return [
            {"id": 3},
            {"id": 4},
        ]

    class TestRetriever(CandidatesRetriever):
        engine_map = {
            "uploaded_memes": uploaded_memes,
            "like_spread_and_recent_memes": like_spread_and_recent_memes,
            "lr_smoothed": get_lr_smoothed,
            "less_seen_meme_and_source": top_memes_from_less_seen_sources,
            "best_memes_from_each_source": get_best_memes_from_each_source,
        }

    candidates = await generate_with_blender(1, 10, 200, TestRetriever())
    assert len(candidates) == 2
    assert candidates[0]["id"] == 3

    candidates = await generate_with_blender(1, 10, 1200, TestRetriever())
    assert len(candidates) == 2
    assert candidates[0]["id"] == 1
