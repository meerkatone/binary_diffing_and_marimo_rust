import marimo

__generated_with = "0.14.16"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    import plotly.express as px
    import polars as pl
    import quak
    import altair as alt
    import duckdb
    import pandas as pd
    import json
    from pathlib import Path
    import pyarrow as pa
    return Path, alt, duckdb, json, mo, pa, pd, quak


@app.cell
def _(mo):
    mo.md(r"""<h2>Setup Dataframe</h2>""")
    return


@app.cell
def _(Path, json, pd):
    def load_and_process_json(json_file_path, Path, json, pd):
        with open(json_file_path, 'r') as f:
            data = json.load(f)

        # Extract filenames from metadata
        binary_a = Path(data['metadata']['binary_a']).name
        binary_b = Path(data['metadata']['binary_b']).name

        # Create separate columns for each result
        processed_results = []
        for result in data['results']:
            processed_result = {
                'binary_a': binary_a,
                'binary_b': binary_b,
                'function_a_name': result['function_a']['name'],
                'function_a_address': f"0x{result['function_a']['address']:x}",
                'function_a_size': result['function_a']['size'],
                'function_b_name': result['function_b']['name'],
                'function_b_address': f"0x{result['function_b']['address']:x}",
                'function_b_size': result['function_b']['size'],
                'similarity': result['similarity'],
                'similarity_rounded': round(result['similarity'], 4),
                'confidence': result['confidence'],
                'match_type': result['match_type']
            }
            processed_results.append(processed_result)

        df = pd.DataFrame(processed_results)
        return df, binary_a, binary_b

    # Usage:
    json_file_path = "./nwifi/rust_nwifi1.json"
    df, binary1, binary2 = load_and_process_json(json_file_path, Path, json, pd)
    df
    return (df,)


@app.cell
def _(mo):
    mo.md(r"""<h2>Query Similarity < 0.99</h2>""")
    return


@app.cell
def _(duckdb, mo):
    query1 = """
    SELECT function_a_name, function_b_name, similarity
    FROM df
    WHERE similarity < 0.99
    ORDER BY similarity ASC
    LIMIT 30
    """

    sim = duckdb.query(query1).to_df()
    mo.ui.dataframe(sim)

    return (sim,)


@app.cell
def _(mo):
    mo.md(r"""<h2>Similarity Slider</h2>""")
    return


@app.cell
def _(mo):
    similarity_slider = mo.ui.slider(
        start=0.700,
        stop=1.000,
        step=0.010,
        value=0.990,
        label="Similarity Threshold")
    similarity_slider
    return (similarity_slider,)


@app.cell
def _(mo):
    mo.md(r"""<h2>Functions with Similarity Below Slider Threshold (Bar Chart)</h2>""")
    return


@app.cell
def _(alt, mo, sim, similarity_slider):
    df_filtered_slider = sim[sim["similarity"] < similarity_slider.value]

    # Build the chart
    chart_obj = alt.Chart(df_filtered_slider).mark_bar().encode(
        x=alt.X("function_a_name:N", title="Function Name").scale(zero=False),
        y=alt.Y("similarity:Q", title="Similarity").scale(zero=False),
        color=alt.Color('similarity:Q', scale=alt.Scale(scheme='viridis')),
        tooltip=["function_a_name", "function_b_name", "similarity"]
    ).properties(
        width=700,
        height=400,
        title="Functions with Similarity Below Slider Threshold"
        ).configure_axisX(
        labelAngle=45
    )

    # Display the chart
    mo.ui.altair_chart(chart_obj)

    return


@app.cell
def _(mo):
    mo.md(r"""<h2>Query Function Names Don't Match Similarity > 0.9</h2>""")
    return


@app.cell
def _(duckdb, mo):
    query4 = """
    SELECT binary_a, function_a_name, binary_b, function_b_name, similarity
    FROM df
    WHERE function_a_name != function_b_name
    AND similarity > 0.9
    ORDER BY similarity DESC
    LIMIT 20
    """

    cross_bin = duckdb.query(query4).to_df()
    mo.ui.dataframe(cross_bin)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""<h2>Read Dataframe and Register with DuckDB and Visualise with Marimo's UI and Quak</h2>""")
    return


@app.cell
def _(df, duckdb, mo, pa, quak):

    # Register the DataFrame with DuckDB
    duckdb.register("df", pa.Table.from_pandas(df))

    # Create and display the widget (using 'df' not 'df1')
    widget = mo.ui.anywidget(quak.Widget(df))
    widget
    return


@app.cell
def _(mo):
    mo.md(r"""<h2>Query Function Name Matches</h2>""")
    return


@app.cell
def _(duckdb, mo):
    query5 = """
    SELECT function_a_name, function_b_name, similarity
    FROM df
    WHERE function_a_name == function_b_name
    AND similarity < 0.99
    ORDER BY similarity DESC
    LIMIT 20

    """

    clashes = duckdb.query(query5).to_df()
    mo.ui.dataframe(clashes)

    return


@app.cell
def _(mo):
    mo.md(r"""<h2>Query Best Matches</h2>""")
    return


@app.cell
def _(duckdb, mo):
    query_best_matches = """
    WITH ranked_matches AS (
        SELECT *,
               ROW_NUMBER() OVER (PARTITION BY function_a_name ORDER BY similarity DESC) AS rank1,
               ROW_NUMBER() OVER (PARTITION BY function_b_name ORDER BY similarity DESC) AS rank2
        FROM df
        WHERE similarity <= 0.99
    )
    SELECT function_a_address, function_a_name, function_b_address, function_b_name, similarity
    FROM ranked_matches
    WHERE rank1 = 1 AND rank2 = 1
    ORDER BY similarity DESC
    """

    best_matches = duckdb.query(query_best_matches).to_df()
    mo.ui.dataframe(best_matches)

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    <h2>References</h2>
     - CVE-2024-38063: https://www.cve.org/CVERecord?id=CVE-2024-38063
     - Windows TCP/IP Remote Code Execution Vulnerability: https://msrc.microsoft.com/update-guide/vulnerability/CVE-2024-38063
     - tcpip.sys - Winbindex: https://winbindex.m417z.com/?file=tcpip.sys
     - Breaking down CVE-2024–38063: remote exploitation of the Windows kernel: https://bi-zone.medium.com/breaking-down-cve-2024-38063-remote-exploitation-of-the-windows-kernel-bdae36f5f61d
    """
    )
    return


if __name__ == "__main__":
    app.run()
