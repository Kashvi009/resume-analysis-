import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
from io import BytesIO

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'AI-Fit Score & Competency Report', 0, 0, 'C')
        self.ln(15)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def create_radar_chart(data: pd.DataFrame) -> BytesIO | None:
    """Creates a visually enhanced radar chart."""
    if data.empty or 'Competency Rating (1-10)' not in data.columns: return None
    labels = data['Skill/Keyword'].values
    stats = data['Competency Rating (1-10)'].astype(float).values
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    stats = np.concatenate((stats, [stats[0]]))
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    ax.fill(angles, stats, color='#007bff', alpha=0.25)
    ax.plot(angles, stats, color='#007bff', linewidth=2)
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, size=11)
    ax.set_title('Competency Radar', size=16, y=1.1)
    
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    return buf

def create_bar_chart(data: pd.DataFrame) -> BytesIO | None:
    """Creates a horizontal bar chart of competency ratings."""
    if data.empty or 'Competency Rating (1-10)' not in data.columns: return None
    
    data = data.sort_values('Competency Rating (1-10)', ascending=True)
    labels = data['Skill/Keyword'].values
    stats = data['Competency Rating (1-10)'].astype(float).values
    
    fig, ax = plt.subplots(figsize=(10, len(labels) * 0.5))
    ax.barh(labels, stats, color='#007bff')
    ax.set_xlabel('Rating (out of 10)')
    ax.set_title('Competency Ratings')
    ax.set_xlim(0, 10)
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    return buf

def create_pdf_report(analysis_text: str, competency_df: pd.DataFrame, radar_chart: BytesIO, bar_chart: BytesIO) -> bytes:
    """Generates a professional PDF report with multiple visualizations."""
    pdf = PDF()
    pdf.add_page()

    # Add Analysis Text First
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Analysis & Review", ln=True)
    pdf.set_font("Arial", size=11)
    # Encode with error handling to prevent crashes on unsupported characters
    safe_analysis_text = analysis_text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 8, safe_analysis_text)
    pdf.ln(10)

    # Add Competency Matrix Table
    if not competency_df.empty:
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Competency Matrix", ln=True)
        pdf.set_font("Arial", 'B', 10)
        
        col_widths = [60, 30, 35, 60]
        headers = ['Skill/Keyword', 'In Resume?', 'Rating', 'Suggestion']
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 10, header, 1, 0, 'C', 1)
        pdf.ln()

        pdf.set_font("Arial", size=9)
        for _, row in competency_df.iterrows():
            pdf.cell(col_widths[0], 10, str(row.iloc[0]), 1)
            pdf.cell(col_widths[1], 10, str(row.iloc[1]), 1, align='C')
            pdf.cell(col_widths[2], 10, str(row.iloc[2]), 1, align='C')
            pdf.multi_cell(col_widths[3], 10, str(row.iloc[3]), 1)
        pdf.ln(10)

    # Add Visualizations on a new page if they exist
    if radar_chart or bar_chart:
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Visualizations", ln=True)
        if radar_chart:
            pdf.image(radar_chart, x=10, y=pdf.get_y(), w=pdf.w / 2 - 15)
        if bar_chart:
            pdf.image(bar_chart, x=pdf.w / 2 + 5, y=pdf.get_y(), w=pdf.w / 2 - 15)

    return bytes(pdf.output(dest='S'))