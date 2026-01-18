from sqlalchemy import func, text
from src.models.user import db
from src.models.material import Material


def update_search_vector(material):
    if db.engine.dialect.name == 'postgresql':
        db.session.execute(
            text("""
                UPDATE materials
                SET search_vector = to_tsvector('english',
                    coalesce(name, '') || ' ' ||
                    coalesce(description, '') || ' ' ||
                    coalesce(category, '') || ' ' ||
                    coalesce(subcategory, '')
                )
                WHERE id = :material_id
            """),
            {'material_id': material.id}
        )


def search_materials_fulltext(query, limit=20):
    if db.engine.dialect.name != 'postgresql':
        return Material.query.filter(
            Material.name.ilike(f'%{query}%') |
            Material.description.ilike(f'%{query}%')
        ).limit(limit).all()

    results = db.session.execute(
        text("""
            SELECT m.*, ts_rank(search_vector, plainto_tsquery('english', :query)) as rank
            FROM materials m
            WHERE search_vector @@ plainto_tsquery('english', :query)
            ORDER BY rank DESC
            LIMIT :limit
        """),
        {'query': query, 'limit': limit}
    ).fetchall()

    material_ids = [row.id for row in results]
    if not material_ids:
        return []

    return Material.query.filter(Material.id.in_(material_ids)).all()


def rebuild_all_search_vectors():
    if db.engine.dialect.name != 'postgresql':
        return

    db.session.execute(
        text("""
            UPDATE materials
            SET search_vector = to_tsvector('english',
                coalesce(name, '') || ' ' ||
                coalesce(description, '') || ' ' ||
                coalesce(category, '') || ' ' ||
                coalesce(subcategory, '')
            )
        """)
    )
    db.session.commit()
