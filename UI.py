import streamlit as st
import pandas as pd
import plotly.express as px

# Load the dataset (replace with actual file path)
df = pd.read_csv('Report-happiness.csv')

# Preprocess data
df['Year'] = df['Year'].astype(int)
df['Happiness Rank'] = pd.to_numeric(df['Happiness Rank'], errors='coerce')
df['Happiness Score'] = pd.to_numeric(df['Happiness Score'], errors='coerce')

# Streamlit app
st.title('Happiness Score Dashboard')

# Set dark mode theme for the dashboard
st.markdown(
    """
    <style>
    .main {background-color: #111111;}
    .sidebar .sidebar-content {background-color: #111111; color: #ffffff;}
    .stMetric, .stText, .stMarkdown {color: #ffffff;}
    </style>
    """, unsafe_allow_html=True
)

# Sidebar for selecting year and color theme
selected_year = st.sidebar.selectbox('Select Year', df['Year'].unique())
color_theme = st.sidebar.selectbox(
    'Select Color Theme', 
    ['Viridis', 'Cividis', 'Inferno', 'Magma', 'Plasma', 'Turbo']
)

# Filter data for the selected year
df_year = df[df['Year'] == selected_year]

# Top Section: List of countries and metric cards
st.header("Top Section")
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"Top Countries by Happiness Rank in {selected_year}")
    top_countries = df_year[['Country', 'Happiness Rank']].sort_values(by='Happiness Rank').head(10)
    st.write(top_countries)

with col2:
    st.subheader(f"Top and Bad Happiness Scores in {selected_year}")
    top_score = df_year.loc[df_year['Happiness Score'].idxmax()]
    bad_score = df_year.loc[df_year['Happiness Score'].idxmin()]

    st.metric(label="Top Happiness Score", value=top_score['Happiness Score'], delta=top_score['Country'])
    st.metric(label="Bad Happiness Score", value=bad_score['Happiness Score'], delta=bad_score['Country'])

# Middle Section: Map and Density Plot (stacked vertically)
st.header("Middle Section")
st.subheader(f"Map of Happiness Scores by Country in {selected_year}")
map_fig = px.choropleth(
    df_year, 
    locations='Country', 
    color='Happiness Score', 
    locationmode="country names",
    color_continuous_scale=color_theme,
    range_color=(0, max(df_year['Happiness Score'])),
    labels={'Happiness Score': 'Happiness Score'}
)
map_fig.update_layout(
    template='plotly_dark',
    plot_bgcolor='rgba(0, 0, 0, 0)',
    paper_bgcolor='rgba(0, 0, 0, 0)',
    margin=dict(l=0, r=0, t=0, b=0),
    height=500
)
st.plotly_chart(map_fig)

st.subheader("Density Plot: Economy (GDP per Capita) for Happy and Unhappy Countries")
happiness_threshold = 6
happy_countries = df_year[df_year['Happiness Score'] > happiness_threshold]
unhappy_countries = df_year[df_year['Happiness Score'] <= happiness_threshold]

density_fig = px.density_contour(
    pd.concat([
        happy_countries.assign(Category='Happy'),
        unhappy_countries.assign(Category='Unhappy')
    ]),
    x="Economy (GDP per Capita)",
    y="Happiness Score",
    color="Category",
    color_discrete_map={"Happy": "green", "Unhappy": "red"},
    labels={
        "Economy (GDP per Capita)": "Economy (GDP per Capita)",
        "Happiness Score": "Happiness Score"
    },
    title="Density Plot: Economy vs Happiness for Happy vs Unhappy Countries",
    template="plotly_dark"
)

threshold_density = df_year[df_year['Happiness Score'] > happiness_threshold]['Economy (GDP per Capita)'].min()
density_fig.add_vline(
    x=threshold_density,
    line_dash="dash",
    line_color="red",
    annotation_text=f"Suggested Threshold: {threshold_density:.2f}",
    annotation_position="top right"
)
st.plotly_chart(density_fig)

# Bottom Section: Bar Charts (Two by Two)
st.header("Bottom Section")
characteristics = [
    'Economy (GDP per Capita)', 
    'Family', 
    'Health (Life Expectancy)', 
    'Freedom', 
    'Trust (Government Corruption)', 
    'Generosity'
]

for i in range(0, len(characteristics), 2):
    col1, col2 = st.columns(2)

    for j, char in enumerate(characteristics[i:i+2]):
        col = col1 if j == 0 else col2
        with col:
            top_10 = df_year.nsmallest(10, 'Happiness Rank')
            bottom_10 = df_year.nlargest(10, 'Happiness Rank')
            top_mean = top_10[char].mean()
            bottom_mean = bottom_10[char].mean()

            bar_fig = px.bar(
                x=['Top 10 Happy', 'Bottom 10 Happy'], 
                y=[top_mean, bottom_mean],
                labels={'x': 'Group', 'y': f'Mean {char}'},
                title=f'Mean {char}: Top 10 vs Bottom 10',
                color=['Top 10 Happy', 'Bottom 10 Happy'],
                color_discrete_map={'Top 10 Happy': 'green', 'Bottom 10 Happy': 'red'}
            )
            st.plotly_chart(bar_fig)
