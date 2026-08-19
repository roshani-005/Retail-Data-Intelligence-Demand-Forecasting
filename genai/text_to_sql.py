"""Basic Generative-AI text-to-SQL concept.

This module demonstrates the safety boundary around an LLM-generated SQL
statement. It does not call an external model or require an API key. In a
production version, `generate_sql()` would be replaced by an LLM call using
the database schema as context, followed by the same validation step.
"""
import re

READ_ONLY = re.compile(r"^\s*(SELECT|WITH)\b", re.IGNORECASE)
BLOCKED = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|CREATE|GRANT|REVOKE|EXEC|CALL)\b",
    re.IGNORECASE,
)

EXAMPLES = {
    "total sales by region": """
        SELECT l.region, SUM(f.sales) AS total_sales
        FROM retail.fact_sales f
        JOIN retail.dim_location l ON l.location_key = f.location_key
        GROUP BY l.region
        ORDER BY total_sales DESC;
    """,
    "top products by sales": """
        SELECT p.product_name, SUM(f.sales) AS total_sales
        FROM retail.fact_sales f
        JOIN retail.dim_product p ON p.product_key = f.product_key
        GROUP BY p.product_name
        ORDER BY total_sales DESC
        LIMIT 10;
    """,
}


def validate_sql(sql: str) -> str:
    """Allow only read-only SELECT/CTE queries for the assistant."""
    if not READ_ONLY.match(sql) or BLOCKED.search(sql):
        raise ValueError("Only read-only SELECT/CTE SQL is allowed.")
    if ";" in sql.rstrip(";"):
        raise ValueError("Multiple SQL statements are not allowed.")
    return sql.strip()


def generate_sql(question: str) -> str:
    """Demo generator; replace with an LLM call in a production system."""
    normalized = " ".join(question.lower().split())
    for phrase, sql in EXAMPLES.items():
        if phrase in normalized:
            return validate_sql(sql)
    raise ValueError(
        "No demo template matches this question. A production LLM would generate SQL from the schema."
    )


if __name__ == "__main__":
    question = input("Ask a retail data question: ")
    print(generate_sql(question))
