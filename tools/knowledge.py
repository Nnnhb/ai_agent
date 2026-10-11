from agents import function_tool

from knowledge.database import (
    save_knowledge,
    search_knowledge,
    get_knowledge,
    delete_knowledge,
)


@function_tool
def remember_knowledge(
    category: str,
    key: str,
    value: str,
    source: str = "UIE",
) -> str:
    return save_knowledge(
        category=category,
        key=key,
        value=value,
        source=source,
    )


@function_tool
def recall_knowledge(
    query: str,
    limit: int = 10,
) -> str:
    results = search_knowledge(
        query=query,
        limit=limit,
    )

    if not results:
        return "No matching knowledge was found."

    output = [
        "UIE Memory Results",
        "==================",
    ]

    for item in results:
        output.append(
            f"Category: {item['category']}\n"
            f"Key: {item['key']}\n"
            f"Value: {item['value']}\n"
            f"Source: {item['source']}\n"
            f"Updated: {item['updated_at']}"
        )

    return "\n\n".join(output)


@function_tool
def recall_exact_knowledge(
    category: str,
    key: str,
) -> str:
    result = get_knowledge(
        category=category,
        key=key,
    )

    if result is None:
        return (
            f"No memory found for "
            f"category='{category}' "
            f"and key='{key}'."
        )

    return (
        "UIE Memory\n"
        "==========\n"
        f"Category: {result['category']}\n"
        f"Key: {result['key']}\n"
        f"Value: {result['value']}\n"
        f"Source: {result['source']}\n"
        f"Created: {result['created_at']}\n"
        f"Updated: {result['updated_at']}"
    )


@function_tool
def forget_knowledge(
    category: str,
    key: str,
) -> str:
    deleted = delete_knowledge(
        category=category,
        key=key,
    )

    if deleted:
        return (
            f"Memory deleted successfully: "
            f"{category}/{key}"
        )

    return (
        f"No matching memory was found: "
        f"{category}/{key}"
    )
