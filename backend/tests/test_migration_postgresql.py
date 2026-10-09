import os
from datetime import datetime, timezone

import pytest
from flask_migrate import upgrade
from sqlalchemy import inspect, text

from app import create_app
from app.extensions import db


def test_fresh_postgresql_upgrade_preserves_mvp_expenses():
    database_url = os.getenv("V2_MIGRATION_TEST_DATABASE_URL")
    if not database_url:
        pytest.skip("Set V2_MIGRATION_TEST_DATABASE_URL to a fresh disposable PostgreSQL database.")

    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": database_url, "JWT_SECRET_KEY": "migration-test-secret-that-is-long-enough"})
    with app.app_context():
        existing_tables = set(inspect(db.engine).get_table_names())
        assert not existing_tables, "Migration test requires a fresh empty PostgreSQL database."

        migration_dir = os.path.join(os.path.dirname(__file__), "..", "migrations")
        upgrade(directory=migration_dir, revision="ad5a390c0763")
        db.session.execute(text("INSERT INTO users (id, email, password_hash, created_at) VALUES (1, 'migration@example.com', 'unused', '2025-01-01 00:00:00')"))
        db.session.execute(text("""
            INSERT INTO expenses (id, user_id, amount, title, expense_date, category, notes, created_at)
            VALUES
              (41, 1, 12.30, '  Lunch  ', '2025-02-03', CAST('Food' AS expense_category), NULL, '2025-02-03 10:11:12'),
              (42, 1, 8.40, '  Bus  ', '2025-02-04', CAST('Transport' AS expense_category), '  Airport  ', '2025-02-04 11:12:13')
        """))
        db.session.commit()

        upgrade(directory=migration_dir)
        rows = db.session.execute(text("""
            SELECT id, amount, transaction_date, notes, created_at, transaction_type, b_u_c, reflective_context
            FROM transactions ORDER BY id
        """)).all()
        assert [row.id for row in rows] == [41, 42]
        assert [row.notes for row in rows] == ["Lunch", "Bus\n\nAirport"]
        assert [str(row.amount) for row in rows] == ["12.30", "8.40"]
        assert [row.transaction_type for row in rows] == ["expense", "expense"]
        assert [(row.b_u_c, row.reflective_context) for row in rows] == [(None, None), (None, None)]
        assert [str(row.transaction_date) for row in rows] == ["2025-02-03", "2025-02-04"]
        assert rows[0].created_at.astimezone(timezone.utc) == datetime(2025, 2, 3, 10, 11, 12, tzinfo=timezone.utc)
        assert db.session.execute(text("SELECT c.key FROM transactions t JOIN categories c ON c.id = t.category_id ORDER BY t.id")).scalars().all() == [
            "expense_food", "expense_transport"
        ]
        assert db.session.execute(text("SELECT COUNT(*) FROM categories")).scalar_one() == 7
        assert "expenses" not in set(inspect(db.engine).get_table_names())
        assert "ai_request_attempts" in set(inspect(db.engine).get_table_names())
