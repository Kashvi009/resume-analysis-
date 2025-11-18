import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
from io import BytesIO
import streamlit as st

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'AI-Fit Score Report', 0, 0, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def create_radar_chart(data: pd.DataFrame) -> BytesIO | None:
    """
    Creates a visually enhanced radar chart from a DataFrame of skills and ratings.
    """
    if data.empty or 'Competency Rating (1-10)' not in data.columns:
        return None

    labels = data['Skill/Keyword'].values
    stats = data['Competency Rating (1-10)'].astype(float).values

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    stats = np.concatenate((stats, [stats[0]]))
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor('#f0f2f6') # Match Streamlit's background
    ax.set_facecolor('#ffffff')

    # Plotting
    ax.fill(angles, stats, color='#007bff', alpha=0.25)
    ax.plot(angles, stats, color='#007bff', linewidth=2, marker='o')

    # Customizing ticks and labels
    ax.set_yticks(np.arange(2, 11, 2))
    ax.set_yticklabels(np.arange(2, 11, 2), color="grey", size=9)
    ax.set_rlabel_position(30)
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, size=11)
    ax.set_title('Competency Radar', size=16, color='black', y=1.1)

    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', pad_inches=0.5)
    plt.close(fig)
    return buffer

def create_pdf_report(analysis_text: str, competency_df: pd.DataFrame, radar_chart: BytesIO) -> bytes:
    """
    Generates a professional PDF report from the analysis text, competency table, and radar chart.
    """
    pdf = PDF()
    pdf.add_page()

    # Add Radar Chart if available
    if radar_chart:
        pdf.image(radar_chart, x=pdf.w / 4, y=None, w=pdf.w / 2)
        pdf.ln(15)

    # Add Competency Matrix Table
    if not competency_df.empty:
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Competency Matrix", ln=True, align='L')
        pdf.set_font("Arial", size=10)
        
        # Table Header
        pdf.set_fill_color(230, 230, 230)
        col_widths = [60, 30, 35, 60]
        headers = ['Skill/Keyword', 'In Resume?', 'Rating (1-10)', 'Suggestion']
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 10, header, 1, 0, 'C', 1)
        pdf.ln()

        # Table Rows
        for _, row in competency_df.iterrows():
            pdf.cell(col_widths[0], 10, str(row.iloc[0]), 1)
            pdf.cell(col_widths[1], 10, str(row.iloc[1]), 1, align='C')
            pdf.cell(col_widths[2], 10, str(row.iloc[2]), 1, align='C')
            pdf.multi_cell(col_widths[3], 10, str(row.iloc[3]), 1) # Multi-cell for suggestions
        pdf.ln(10)

    # Add Analysis Text
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Analysis & Review", ln=True, align='L')
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 8, analysis_text)

    return pdf.output(dest='S').encode('latin-1')