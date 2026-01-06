import streamlit as st
from streamlit.components.v1 import html

st.title("Material Design in Streamlit")

st.subheader("1) Material Components Web (via injected HTML)")

html(
    """
<link rel="stylesheet"
      href="https://fonts.googleapis.com/icon?family=Material+Icons">
<link rel="stylesheet"
      href="https://cdn.jsdelivr.net/npm/material-components-web@latest/dist/material-components-web.min.css">
<script src="https://cdn.jsdelivr.net/npm/material-components-web@latest/dist/material-components-web.min.js"></script>

<div class="mdc-card" style="padding: 16px; margin: 20px; border-radius: 12px;">
  <h2 class="mdc-typography--headline6">Material Design Card</h2>
  <p class="mdc-typography--body2">
    This is what a Material Design component looks like inside Streamlit.
  </p>
  <button class="mdc-button mdc-button--raised">
    <span class="mdc-button__label">Material Button</span>
  </button>
</div>

<script>
  mdc.ripple.MDCRipple.attachTo(document.querySelector('.mdc-button'));
</script>
""",
    height=300,
)

st.subheader("2) streamlit-elements (Material UI components)")
st.caption("Install with: pip install streamlit-elements")

try:
    from streamlit_elements import elements, mui, html as elements_html

    with elements("elements_demo"):
        mui.Card(
            mui.CardContent(
                mui.Typography("This card is rendered via streamlit-elements (MUI).", variant="h6"),
                mui.Typography(
                    "Unlike injected HTML, elements can interact with Python state more cleanly.",
                    variant="body2",
                    sx={"mt": 1},
                ),
                mui.Button(
                    "Click me",
                    variant="contained",
                    onClick=elements_html.js_callback("alert('Hello from streamlit-elements!')"),
                    sx={"mt": 2},
                ),
            ),
            sx={"maxWidth": 520, "m": 2, "borderRadius": 3},
        )

except ModuleNotFoundError:
    st.info(
        "streamlit-elements isn't installed in this environment. "
        "Run `pip install streamlit-elements` to see the example.",
        icon="ℹ️",
    )
