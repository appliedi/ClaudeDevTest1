import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from io import BytesIO
import numpy as np
import json

def calculate_totals(host_clubs, international_clubs, ddf, other_donors):
    total_host_ddf = sum(club['ddf'] for club in host_clubs)
    total_host_cash = sum(club['cash'] for club in host_clubs)
    total_international_ddf = sum(club['ddf'] for club in international_clubs)
    total_international_cash = sum(club['cash'] for club in international_clubs)
    
    total_ddf = total_host_ddf + total_international_ddf + ddf
    total_cash = total_host_cash + total_international_cash
    
    cash_through_trf = total_cash * 0.95  # 5% fee
    fee = total_cash * 0.05
    
    world_fund_match = min(total_ddf * 0.8, 400000)  # 80% of DDF, max $400,000
    
    total_other_donors = sum(donor['amount'] for donor in other_donors)
    
    total_funding = total_ddf + cash_through_trf + world_fund_match + total_other_donors
    
    return {
        'total_host_ddf': total_host_ddf,
        'total_host_cash': total_host_cash,
        'total_international_ddf': total_international_ddf,
        'total_international_cash': total_international_cash,
        'total_ddf': total_ddf,
        'total_cash': total_cash,
        'cash_through_trf': cash_through_trf,
        'fee': fee,
        'world_fund_match': world_fund_match,
        'total_other_donors': total_other_donors,
        'total_funding': total_funding
    }

def generate_pie_chart(data):
    labels = ['Host Contributions', 'International Contributions', 'World Fund Match', 'Other Donors']
    sizes = [
        data['total_host_ddf'] + data['total_host_cash'],
        data['total_international_ddf'] + data['total_international_cash'],
        data['world_fund_match'],
        data['total_other_donors']
    ]
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
    
    plt.figure(figsize=(8, 6))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    plt.axis('equal')
    plt.title('Funding Breakdown')
    
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    return img_buffer

def generate_pdf(data, project_details):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    elements = []
    
    styles = getSampleStyleSheet()
    elements.append(Paragraph("Global Grant Financing Planner", styles['Title']))
    elements.append(Paragraph(f"Application #: {project_details['application_number']} | Project Country: {project_details['project_country']}", styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Create tables for each section
    host_data = [['Host Rotary Clubs/Districts', 'DDF (USD)', 'Cash Direct to Project', 'Cash through TRF (Equiv USD)', '5% Fee', 'Total to TRF']]
    for club in data['host_clubs']:
        cash_through_trf = club['cash'] * 0.95
        fee = club['cash'] * 0.05
        total_to_trf = cash_through_trf + fee
        host_data.append([club['name'], club['ddf'], club['cash'], cash_through_trf, fee, total_to_trf])
    host_data.append(['Total Host Contributions', data['total_host_ddf'], data['total_host_cash'], 
                      data['total_host_cash'] * 0.95, data['total_host_cash'] * 0.05, 
                      data['total_host_cash'] * 0.95 + data['total_host_cash'] * 0.05])
    
    international_data = [['International Rotary Clubs/Districts', 'DDF (USD)', 'Cash Direct to Project', 'Cash through TRF (Equiv USD)', '5% Fee', 'Total to TRF']]
    for club in data['international_clubs']:
        cash_through_trf = club['cash'] * 0.95
        fee = club['cash'] * 0.05
        total_to_trf = cash_through_trf + fee
        international_data.append([club['name'], club['ddf'], club['cash'], cash_through_trf, fee, total_to_trf])
    international_data.append(['Total International Contributions', data['total_international_ddf'], data['total_international_cash'], 
                               data['total_international_cash'] * 0.95, data['total_international_cash'] * 0.05, 
                               data['total_international_cash'] * 0.95 + data['total_international_cash'] * 0.05])
    
    other_donors_data = [['Other donors', 'Cash Direct to Project', 'Cash through TRF (Equiv USD)', '5% Fee', 'Total to TRF']]
    for donor in data['other_donors']:
        cash_through_trf = donor['amount'] * 0.95
        fee = donor['amount'] * 0.05
        total_to_trf = cash_through_trf + fee
        other_donors_data.append([donor['name'], donor['amount'], cash_through_trf, fee, total_to_trf])
    
    summary_data = [
        ['Total Rotarian Contributions', data['total_ddf'] + data['total_cash']],
        ['TRF World Fund match (80% of DDF)', data['world_fund_match']],
        ['Total Other Donors', data['total_other_donors']],
        ['Total Project Funding', data['total_funding']]
    ]
    
    for table_data in [host_data, international_data, other_donors_data, summary_data]:
        t = Table(table_data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(t)
        elements.append(Spacer(1, 12))
    
    # Add pie chart to PDF
    pie_chart = generate_pie_chart(data)
    img = Image(pie_chart, width=400, height=300)
    elements.append(img)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

def save_project_data(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)

def load_project_data(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def main():
    st.set_page_config(page_title="Rotary International Grant Calculator", layout="wide")
    st.title("Rotary International Grant Calculator")

    st.header("Project Details")
    col1, col2 = st.columns(2)
    with col1:
        application_number = st.text_input("Application #", key="application_number")
    with col2:
        project_country = st.text_input("Project Country", key="project_country")

    st.header("Host Rotary Clubs/Districts")
    host_clubs = []
    for i in range(5):  # Allow up to 5 host clubs
        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input(f"Host Club/District Name #{i+1}", key=f"host_name_{i}")
        with col2:
            ddf = st.number_input(f"DDF Amount (USD) #{i+1}", min_value=0.0, format="%.2f", key=f"host_ddf_{i}")
        with col3:
            cash = st.number_input(f"Cash Amount (USD) #{i+1}", min_value=0.0, format="%.2f", key=f"host_cash_{i}")
        if name and (ddf > 0 or cash > 0):
            host_clubs.append({"name": name, "ddf": ddf, "cash": cash})

    st.header("International Rotary Clubs/Districts")
    international_clubs = []
    for i in range(5):  # Allow up to 5 international clubs
        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input(f"International Club/District Name #{i+1}", key=f"int_name_{i}")
        with col2:
            ddf = st.number_input(f"DDF Amount (USD) #{i+1}", min_value=0.0, format="%.2f", key=f"int_ddf_{i}")
        with col3:
            cash = st.number_input(f"Cash Amount (USD) #{i+1}", min_value=0.0, format="%.2f", key=f"int_cash_{i}")
        if name and (ddf > 0 or cash > 0):
            international_clubs.append({"name": name, "ddf": ddf, "cash": cash})

    st.header("TRF World Fund Match")
    ddf = st.number_input("Additional DDF Amount (USD)", min_value=0.0, format="%.2f")

    st.header("Other Donors")
    other_donors = []
    for i in range(3):  # Allow up to 3 other donors
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input(f"Other Donor Name #{i+1}", key=f"other_name_{i}")
        with col2:
            amount = st.number_input(f"Amount (USD) #{i+1}", min_value=0.0, format="%.2f", key=f"other_amount_{i}")
        if name and amount > 0:
            other_donors.append({"name": name, "amount": amount})

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save Project Data"):
            if not application_number:
                st.error("Please enter an Application # before saving.")
            else:
                project_data = {
                    "application_number": application_number,
                    "project_country": project_country,
                    "host_clubs": host_clubs,
                    "international_clubs": international_clubs,
                    "ddf": ddf,
                    "other_donors": other_donors
                }
                save_project_data(project_data, f"{application_number}.json")
                st.success(f"Project data saved as {application_number}.json")

    with col2:
        uploaded_file = st.file_uploader("Load Project Data", type="json")
        if uploaded_file is not None:
            project_data = json.load(uploaded_file)
            st.success("Project data loaded successfully")
            # Update form fields with loaded data
            st.session_state.application_number = project_data["application_number"]
            st.session_state.project_country = project_data["project_country"]
            # Update other fields similarly
            st.experimental_rerun()

    if st.button("Calculate and Generate PDF"):
        if not application_number or not project_country:
            st.error("Please enter both Application # and Project Country.")
        elif not host_clubs and not international_clubs:
            st.error("Please enter at least one Host or International Rotary Club/District.")
        else:
            results = calculate_totals(host_clubs, international_clubs, ddf, other_donors)
            
            project_details = {
                "application_number": application_number,
                "project_country": project_country
            }
            
            pdf_data = {
                "host_clubs": host_clubs,
                "international_clubs": international_clubs,
                "other_donors": other_donors,
                **results
            }
            
            pdf = generate_pdf(pdf_data, project_details)
            
            st.download_button(
                label="Download PDF Report",
                data=pdf,
                file_name=f"rotary_grant_report_{application_number}.pdf",
                mime="application/pdf"
            )
            
            st.success("Calculations complete. You can now download the PDF report.")
            
            # Display summary in Streamlit
            st.header("Summary")
            summary_data = [
                ["Total Host Contributions", f"${results['total_host_ddf'] + results['total_host_cash']:,.2f}"],
                ["Total International Contributions", f"${results['total_international_ddf'] + results['total_international_cash']:,.2f}"],
                ["Total Rotarian Contributions", f"${results['total_ddf'] + results['total_cash']:,.2f}"],
                ["TRF World Fund match (80% of DDF)", f"${results['world_fund_match']:,.2f}"],
                ["Total Other Donors", f"${results['total_other_donors']:,.2f}"],
                ["Total Project Funding", f"${results['total_funding']:,.2f}"]
            ]
            
            df = pd.DataFrame(summary_data, columns=["Item", "Amount"])
            st.table(df)
            
            # Display pie chart in Streamlit
            st.header("Funding Breakdown")
            fig, ax = plt.subplots(figsize=(10, 6))
            labels = ['Host Contributions', 'International Contributions', 'World Fund Match', 'Other Donors']
            sizes = [
                results['total_host_ddf'] + results['total_host_cash'],
                results['total_international_ddf'] + results['total_international_cash'],
                results['world_fund_match'],
                results['total_other_donors']
            ]
            colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
            ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            st.pyplot(fig)

if __name__ == "__main__":
    main()