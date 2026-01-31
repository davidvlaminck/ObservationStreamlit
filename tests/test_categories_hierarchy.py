import importlib

def reload_db_with_tmp(tmp_path):
    db_file = tmp_path / "cat.db"
    db_url = f"sqlite:///{db_file}"
    import app.db as db
    importlib.reload(db)
    return db

def test_category_hierarchy(tmp_path):
    db = reload_db_with_tmp(tmp_path)
    db.init_db()
    eng = db.get_engine()
    with eng.connect() as conn:
        # Add root category
        res = conn.execute(db.categories.insert().values(label="Root", key="root", parent_id=None, description="", is_active=True))
        root_id = res.inserted_primary_key[0]
        # Add child
        res = conn.execute(db.categories.insert().values(label="Child", key="child", parent_id=root_id, description="", is_active=True))
        child_id = res.inserted_primary_key[0]
        # Add grandchild
        res = conn.execute(db.categories.insert().values(label="Grandchild", key="grandchild", parent_id=child_id, description="", is_active=True))
        grandchild_id = res.inserted_primary_key[0]
        # Fetch all
        cats = conn.execute(db.categories.select()).mappings().all()
        assert any(c["id"] == root_id and c["parent_id"] is None for c in cats)
        assert any(c["id"] == child_id and c["parent_id"] == root_id for c in cats)
        assert any(c["id"] == grandchild_id and c["parent_id"] == child_id for c in cats)
