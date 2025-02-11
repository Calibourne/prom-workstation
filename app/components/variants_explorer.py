from app.utils import safe_exec
import streamlit as st
import pandas as pd
import pm4py as pm

@st.cache_data
def get_variants(filtered_log):
    return pm.statistics.variants.log.get.get_variants(filtered_log)


@safe_exec
def render_variants(filtered_log):
    """Displays the top process variants (execution paths)."""

    # Extract variants
    variants_dict = get_variants(filtered_log)
    st.write(f"Found {len(variants_dict)} unique variants.")
    if not variants_dict:
        st.warning("No variants found.")
        return
    
    variants_list = [(variant, len(cases)) for variant, cases in variants_dict.items()]
    variants_df = pd.DataFrame(variants_list, columns=["Variant", "Count"]).sort_values(by="Count", ascending=False)

    coverage = st.slider("Variant Coverage (%)", 1, 100, 10)
    top_n = int(len(variants_df) * coverage / 100)
    # st.bar_chart(variants_df.set_index("Variant").head(top_n))

    st.dataframe(variants_df.head(top_n).set_index("Variant")
                 , use_container_width=True)

def variants_explorer(filtered_log):
    st.subheader(" 🚀 Variants Explorer")
    render_variants(filtered_log)