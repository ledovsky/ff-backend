from typing import Any
from datetime import datetime
from sqlalchemy import select, nulls_first, text
from sqlalchemy.dialects.postgresql import insert

from src.database import (
    language,
    meme,
    meme_source,
    meme_raw_telegram,
    execute, fetch_one, fetch_all,
)
from src.storage.parsers.schemas import TgChannelPostParsingResult
from src.storage.constants import (
    MEME_SOURCE_POST_UNIQUE_CONSTRAINT,
    MemeSourceType,
    MemeSourceStatus,
    MemeType,
    MemeStatus,
)


async def insert_parsed_posts_from_telegram(
    meme_source_id: int,
    telegram_posts: list[TgChannelPostParsingResult],
) -> None:
    posts = [
        post.model_dump(exclude_none=True) | {"meme_source_id": meme_source_id}
        for post in telegram_posts
    ]
    insert_statement = insert(meme_raw_telegram).values(posts)
    insert_posts_query = insert_statement.on_conflict_do_update(
        constraint=MEME_SOURCE_POST_UNIQUE_CONSTRAINT,
        set_={
            "media": insert_statement.excluded.media,
            "views": insert_statement.excluded.views,
            "updated_at": datetime.utcnow(),
        },
    )

    await execute(insert_posts_query)


async def get_telegram_sources_to_parse(limit=10) -> list[dict[str, Any]]:
    select_query = (
        select(meme_source)
        .where(meme_source.c.type == MemeSourceType.TELEGRAM)
        .where(meme_source.c.status == MemeSourceStatus.PARSING_ENABLED)
        .order_by(nulls_first(meme_source.c.parsed_at))
        .limit(limit)
    )
    return await fetch_all(select_query)


async def update_meme_source(meme_source_id: int, **kwargs) -> dict[str, Any] | None:
    update_query = (
        meme_source.update()
        .where(meme_source.c.id == meme_source_id)
        .values(**kwargs)
        .returning(meme_source)
    )
    return await fetch_one(update_query)


# TODO: separate file for ETL scripts?
async def etl_memes_from_raw_telegram_posts() -> None:
    insert_query = f"""
        INSERT INTO meme (meme_source_id, raw_meme_id, caption, status, type, language_code)
        SELECT 
            meme_source_id,
            post_id AS raw_meme_id, 
            content AS caption,
            '{MemeStatus.CREATED.value}' AS status,
            '{MemeType.IMAGE.value}' AS type,
            meme_source.language_code AS language_code
        FROM meme_raw_telegram
        LEFT JOIN meme_source
            ON meme_source.id = meme_raw_telegram.meme_source_id
        WHERE JSONB_ARRAY_LENGTH(media) = 1
        ON CONFLICT DO NOTHING
    """
    await execute(text(insert_query))


async def update_meme(meme_id: int, **kwargs) -> dict[str, Any] | None:
    update_query = (
        meme.update()
        .where(meme.c.id == meme_id)
        .values(**kwargs)
        .returning(meme)
    )
    return await fetch_one(update_query)


async def get_unloaded_tg_memes() -> list[dict[str, Any]]:
    "Returns only MemeType.IMAGE memes"
    select_query = f"""
        SELECT 
            meme.id,
            '{MemeType.IMAGE}' AS type,
            meme_raw_telegram.media->0->>'url' content_url
        FROM meme
        INNER JOIN meme_source 
            ON meme_source.id = meme.meme_source_id
            AND meme_source.type = '{MemeSourceType.TELEGRAM.value}'
        INNER JOIN meme_raw_telegram
            ON meme_raw_telegram.post_id = meme.raw_meme_id
            AND meme_raw_telegram.meme_source_id = meme.meme_source_id
        WHERE 1=1
            AND meme.telegram_file_id IS NULL;
    """
    return await fetch_all(text(select_query))