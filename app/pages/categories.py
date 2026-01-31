"""
Admin: Category management page (categoriebeheer)
- List categories (hierarchical, visually indented)
- Create, edit, delete categories
- Only accessible to admins
- Uses streamlit-elements for UI
"""
import streamlit as st
from app import db, state
from sqlalchemy import select, insert, update, delete

def fetch_categories(conn):
    """Fetch all categories and build a parent_id -> children tree."""
    cats = conn.execute(select(db.categories)).mappings().all()
    tree = {}
    for cat in cats:
        tree.setdefault(cat["parent_id"], []).append(cat)
    return tree

def render_category_tree(tree, parent_id=None, level=0):
    """Recursively render the category tree with indentation and parent/child structure."""
    for cat in tree.get(parent_id, []):
        indent = "&nbsp;&nbsp;&nbsp;" * level
        bullet = "\u2022 " if level > 0 else ""
        st.markdown(f"{indent}{bullet}**{cat['label']}** <span style='color:gray'>({cat['key']})</span>", unsafe_allow_html=True)
        render_category_tree(tree, cat["id"], level + 1)

def show():
    """Main entry point for the category management admin page."""
    st.title("Categoriebeheer (Admin)")
    if not state.is_admin(st.session_state):
        st.error("Alleen admins mogen categorieën beheren.")
        return
    with db.get_engine().connect() as conn:
        tree = fetch_categories(conn)
        st.subheader("Categorieën (hiërarchisch)")
        render_category_tree(tree)
        st.divider()
        st.subheader("Categorie toevoegen")
        with st.form("add_cat_form", clear_on_submit=True):
            label = st.text_input("Label")
            parent = st.selectbox("Parent categorie", [None] + [c["label"] for c in conn.execute(select(db.categories)).mappings().all()])
            desc = st.text_area("Beschrijving")
            submit = st.form_submit_button("Toevoegen")
        if submit and label:
            gen_key = label.lower().replace(" ", "_")
            parent_id = None
            if parent:
                parent_id = next((c["id"] for c in conn.execute(select(db.categories)).mappings().all() if c["label"] == parent), None)
            conn.execute(insert(db.categories).values(label=label, key=gen_key, parent_id=parent_id, description=desc, is_active=True))
            conn.commit()
            st.success(f"Categorie '{label}' toegevoegd.")
            st.rerun()
        st.divider()
        st.subheader("Categorie bewerken/verwijderen")
        cats = conn.execute(select(db.categories)).mappings().all()
        all_labels = {c["id"]: c["label"] for c in cats}
        for cat in cats:
            with st.expander(f"{cat['label']} ({cat['key']})"):
                new_label = st.text_input("Label", value=cat["label"], key=f"edit_label_{cat['id']}")
                new_desc = st.text_area("Beschrijving", value=cat["description"] or "", key=f"edit_desc_{cat['id']}")
                new_active = st.checkbox("Actief", value=cat["is_active"], key=f"edit_active_{cat['id']}")
                parent_options = [None] + [lbl for cid, lbl in all_labels.items() if cid != cat["id"]]
                new_parent_label = st.selectbox("Parent categorie", parent_options, index=parent_options.index(all_labels.get(cat["parent_id"])) if cat["parent_id"] in all_labels else 0, key=f"edit_parent_{cat['id']}")
                edit = st.button("Opslaan", key=f"edit_btn_{cat['id']}")
                delete_btn = st.button("Verwijderen", key=f"del_btn_{cat['id']}")
                if edit:
                    new_parent_id = None
                    if new_parent_label:
                        new_parent_id = next((cid for cid, lbl in all_labels.items() if lbl == new_parent_label), None)
                    conn.execute(update(db.categories).where(db.categories.c.id == cat["id"]).values(label=new_label, description=new_desc, is_active=new_active, parent_id=new_parent_id))
                    conn.commit()
                    st.success("Categorie bijgewerkt.")
                    st.rerun()
                if delete_btn:
                    conn.execute(delete(db.categories).where(db.categories.c.id == cat["id"]))
                    conn.commit()
                    st.success("Categorie verwijderd.")
                    st.rerun()

# For router integration
page = {
    "route": "categories",
    "title": "Categoriebeheer",
    "auth": "admin"
}

def render():
    show()
