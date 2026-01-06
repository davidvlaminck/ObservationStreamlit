# ObservationStreamlit

Streamlit app developed in phases (see `spec/phases.md`).

## Phase 0 (current)
- App skeleton + configuration helpers
- Simple navigation (Home/Login/Protected)
- Protected area gated by session state (stub auth)
- UI direction: Streamlit + **streamlit-elements** (Material UI components)

> Phase 0 **does not implement real authentication** or a database yet.

---

## Setup (using uv)
You said you normally do:

```bash
pip install uv
uv pip install ...
```

That works fine here.

### 1) Create/activate a local venv
If you already use `.venv/`, keep using it:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies with uv

```bash
pip install uv
uv pip install -r requirements.txt
```

---

## Run the app

```bash
streamlit run main.py
```

Then open the URL Streamlit prints (usually `http://localhost:8501`).

---

## Notes
- If `streamlit-elements` is installed, some UI will render using Material UI widgets.
- If it is not installed, the app falls back to standard Streamlit widgets.

---

## Specs
- `spec/spec.md`  overall requirements
- `spec/phases.md`  development roadmap
- `spec/data_model.md`  schema draft (fill this in before Phase 2/3)

