"""
UIE Knowledge Database

Persistent structured memory for UIE.

This module provides a SQLite-based knowledge store.

Current memory structure:

- category: type of memory
- key: identifier for the memory
- value: stored information
- source: where the information came from
- created_at: when the memory was first stored
- updated_at: when the memory was last updated

The database is intentionally simple for now.

Semantic/vector memory can be added later without changing
the basic memory tool interface.
"""

import sqlite3
from pathlib import Path
from typing import Optional


# ============================================================
# DATABASE LOCATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_PATH = (
    PROJECT_ROOT
    / "data"
    / "memory"
    / "uie_knowledge.db"
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection() -> sqlite3.Connection:
    """
    Create a connection to the UIE knowledge database.

    The database directory is created automatically.
    """

    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            key TEXT NOT NULL,
            value TEXT NOT NULL,
            source TEXT,
            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    connection.commit()

    return connection


# ============================================================
# VALIDATION
# ============================================================

def _validate_text(
    value: str,
    field_name: str,
) -> str:
    """
    Validate and normalize a text value.
    """

    if not isinstance(value, str):
        raise ValueError(
            f"{field_name} must be a string."
        )

    value = value.strip()

    if not value:
        raise ValueError(
            f"{field_name} cannot be empty."
        )

    return value


# ============================================================
# SAVE KNOWLEDGE
# ============================================================

def save_knowledge(
    category: str,
    key: str,
    value: str,
    source: str = "UIE",
) -> str:
    """
    Save or update a knowledge item.

    The combination of category + key identifies a memory.

    If that memory already exists, it is updated.

    This implementation intentionally does not depend on a
    UNIQUE database constraint, so it remains compatible
    with older UIE knowledge databases.
    """

    try:

        category = _validate_text(
            category,
            "category",
        )

        key = _validate_text(
            key,
            "key",
        )

        value = _validate_text(
            value,
            "value",
        )

        source = _validate_text(
            source,
            "source",
        )

        with get_connection() as connection:

            # ------------------------------------------------
            # Try to update an existing memory first.
            # ------------------------------------------------

            cursor = connection.execute(
                """
                UPDATE knowledge

                SET
                    value = ?,
                    source = ?,
                    updated_at = CURRENT_TIMESTAMP

                WHERE category = ?
                  AND key = ?
                """,
                (
                    value,
                    source,
                    category,
                    key,
                ),
            )

            # ------------------------------------------------
            # If nothing was updated, create a new memory.
            # ------------------------------------------------

            if cursor.rowcount == 0:

                connection.execute(
                    """
                    INSERT INTO knowledge
                    (
                        category,
                        key,
                        value,
                        source
                    )

                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        category,
                        key,
                        value,
                        source,
                    ),
                )

        return "Knowledge saved successfully."

    except ValueError as error:

        return (
            f"Knowledge validation error: "
            f"{error}"
        )

    except Exception as error:

        return (
            f"Could not save knowledge: "
            f"{error}"
        )


# ============================================================
# SEARCH KNOWLEDGE
# ============================================================

def search_knowledge(
    query: str,
    limit: int = 10,
) -> list[dict]:
    """
    Search stored knowledge using simple text matching.

    Searches:

    - category
    - key
    - value

    Results are ordered by most recently updated memory.
    """

    try:

        query = _validate_text(
            query,
            "query",
        )

        if not isinstance(limit, int):
            raise ValueError(
                "limit must be an integer."
            )

        if limit < 1:
            raise ValueError(
                "limit must be greater than zero."
            )

        if limit > 100:
            limit = 100

        search_pattern = f"%{query}%"

        with get_connection() as connection:

            cursor = connection.execute(
                """
                SELECT
                    id,
                    category,
                    key,
                    value,
                    source,
                    created_at,
                    updated_at

                FROM knowledge

                WHERE category LIKE ?
                   OR key LIKE ?
                   OR value LIKE ?

                ORDER BY updated_at DESC

                LIMIT ?
                """,
                (
                    search_pattern,
                    search_pattern,
                    search_pattern,
                    limit,
                ),
            )

            rows = cursor.fetchall()

        return [
            {
                "id": row["id"],
                "category": row["category"],
                "key": row["key"],
                "value": row["value"],
                "source": row["source"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
            }
            for row in rows
        ]

    except ValueError:
        return []

    except Exception:
        return []


# ============================================================
# GET EXACT KNOWLEDGE
# ============================================================

def get_knowledge(
    category: str,
    key: str,
) -> Optional[dict]:
    """
    Retrieve one exact knowledge item.

    Returns None when the item does not exist.
    """

    try:

        category = _validate_text(
            category,
            "category",
        )

        key = _validate_text(
            key,
            "key",
        )

        with get_connection() as connection:

            cursor = connection.execute(
                """
                SELECT
                    id,
                    category,
                    key,
                    value,
                    source,
                    created_at,
                    updated_at

                FROM knowledge

                WHERE category = ?
                  AND key = ?

                ORDER BY updated_at DESC

                LIMIT 1
                """,
                (
                    category,
                    key,
                ),
            )

            row = cursor.fetchone()

        if row is None:
            return None

        return {
            "id": row["id"],
            "category": row["category"],
            "key": row["key"],
            "value": row["value"],
            "source": row["source"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    except Exception:
        return None


# ============================================================
# DELETE KNOWLEDGE
# ============================================================

def delete_knowledge(
    category: str,
    key: str,
) -> bool:
    """
    Delete a specific knowledge item.

    Returns True if at least one matching memory was deleted.
    """

    try:

        category = _validate_text(
            category,
            "category",
        )

        key = _validate_text(
            key,
            "key",
        )

        with get_connection() as connection:

            cursor = connection.execute(
                """
                DELETE FROM knowledge

                WHERE category = ?
                  AND key = ?
                """,
                (
                    category,
                    key,
                ),
            )

            return cursor.rowcount > 0

    except Exception:
        return False
