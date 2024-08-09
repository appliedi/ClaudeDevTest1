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

def calculate_totals(host_clubs, international_clubs, other_donors, endowed_gift):
    """
    Calculate the total contributions and funding for a Rotary Global Grant project.
    
    The funding structure is as follows:
    - DDF (District Designated Fund): Allocated by Rotary districts, not actual cash.
    - Cash Direct to Project: Actual money contributed directly to the project.
    - Cash through TRF: Cash contributed through The Rotary Foundation, subject to a 5% fee.
    - World Fund Match: 80% of total DDF contributions, up to a maximum of $400,000.
    - Other Donors: Additional contributions from other sources.
    - Endowed/Directed Gift: Treated as project cash, not subject to the 5% fee.
    """
    total_host_ddf = sum(club['ddf'] for club in host_clubs)
    total_host_cash_direct = sum(club['cash_direct'] for club in host_clubs)
    total_host_cash_trf = sum(club['cash_trf'] for club in host_clubs)
    total_international_ddf = sum(club['ddf'] for club in international_clubs)
    total_international_cash_direct = sum(club['cash_direct'] for club in international_clubs)
    total_international_cash_trf = sum(club['cash_trf'] for club in international_clubs)
    
    total_ddf = total_host_ddf + total_international_ddf
    total_cash_direct = total_host_cash_direct + total_international_cash_direct
    total_cash_trf = total_host_cash_trf + total_international_cash_trf
    
    # Cash through TRF is subject to a 5% fee
    fee = total_cash_trf * 0.05
    project_cash_trf = total_cash_trf
    
    # World Fund match is 80% of DDF, max $400,000
    world_fund_match = min(total_ddf * 0.8, 400000)
    
    total_other_donors_direct = sum(donor['amount_direct'] for donor in other_donors)
    total_other_donors_trf = sum(donor['amount_trf'] for donor in other_donors)
    
    # Total funding includes all contributions
    total_funding = (total_ddf + total_cash_direct + project_cash_trf + world_fund_match + 
                     total_other_donors_direct + total_other_donors_trf + endowed_gift)
    
    total_contributions = total_ddf + total_cash_direct + total_cash_trf
    international_contribution_percentage = ((total_international_ddf + total_international_cash_direct + total_international_cash_trf) / 
                                             total_contributions if total_contributions > 0 else 0)
    
    return {
        'total_host_ddf': total_host_ddf,
        'total_host_cash_direct': total_host_cash_direct,
        'total_host_cash_trf': total_host_cash_trf,
        'total_international_ddf': total_international_ddf,
        'total_international_cash_direct': total_international_cash_direct,
        'total_international_cash_trf': total_international_cash_trf,
        'total_ddf': total_ddf,
        'total_cash_direct': total_cash_direct,
        'total_cash_trf': total_cash_trf,
        'project_cash_trf': project_cash_trf,
        'fee': fee,
        'world_fund_match': world_fund_match,
        'total_other_donors_direct': total_other_donors_direct,
        'total_other_donors_trf': total_other_donors_trf,
        'endowed_gift': endowed_gift,
        'total_funding': total_funding,
        'international_contribution_percentage': international_contribution_percentage,
        'total_contributions': total_contributions
    }

def validate_funding(results):
    """
    Validate the funding structure based on Rotary International rules.
    """
    warnings = []
    if results['international_contribution_percentage'] < 0.15:
        warnings.append("International partner contributions must be at least 15% of the total.")
    if results['total_funding'] < 30000:
        warnings.append("Total funding must be at least $30,000.")
    return warnings

def validate_other_donors(other_donors):
    """
    Validate other donors to ensure they comply with Rotary International rules.
    """
    warnings = []
    for donor in other_donors:
        if "foundation" in donor['name'].lower() or "corporation" in donor['name'].lower():
            warnings.append(f"Non-Rotarian contribution from {donor['name']} may not be eligible. Please ensure it's not from a cooperating organization or a beneficiary of the project.")
    return warnings

def generate_pie_chart(data):
    """
    Generate a pie chart showing the funding breakdown.
    """
    labels = ['Host Contributions', 'International Contributions', 'World Fund Match', 'Other Donors', 'Endowed/Directed Gift']
    sizes = [
        data['total_host_ddf'] + data['total_host_cash_direct'] + data['total_host_cash_trf'],
        data['total_international_ddf'] + data['total_international_cash_direct'] + data['total_international_cash_trf'],
        data['world_fund_match'],
        data['total_other_donors_direct'] + data['total_other_donors_trf'],
        data['endowed_gift']
    ]
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff99cc']
    
    plt.figure(figsize=(8, 6))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    plt.axis('equal')
    plt.title('Funding Breakdown')
    
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    return img_buffer

def generate_pdf(data, project_details):
    """
    Generate a PDF report with detailed information about the Global Grant project.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    elements = []
    
    styles = getSampleStyleSheet()
    elements.append(Paragraph("Global Grant Financing Planner", styles['Title']))
    elements.append(Paragraph(f"Application #: {project_details['application_number']} | Project Country: {project_details['project_country']}", styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Create tables for each section
    host_data = [['Host Rotary Clubs/Districts', 'DDF (USD)', 'Cash Direct to Project', 'Cash through TRF', 'Project Cash', '5% Fee', 'Total to TRF']]
    for club in data['host_clubs']:
        fee = club['cash_trf'] * 0.05
        total_to_trf = club['cash_trf'] + fee
        host_data.append([club['name'], club['ddf'], club['cash_direct'], club['cash_trf'], club['cash_trf'], fee, total_to_trf])
    host_data.append(['Total Host Contributions', data['total_host_ddf'], data['total_host_cash_direct'], 
                      data['total_host_cash_trf'], data['total_host_cash_trf'], data['total_host_cash_trf'] * 0.05, 
                      data['total_host_cash_trf'] * 1.05])
    
    international_data = [['International Rotary Clubs/Districts', 'DDF (USD)', 'Cash Direct to Project', 'Cash through TRF', 'Project Cash', '5% Fee', 'Total to TRF']]
    for club in data['international_clubs']:
        fee = club['cash_trf'] * 0.05
        total_to_trf = club['cash_trf'] + fee
        international_data.append([club['name'], club['ddf'], club['cash_direct'], club['cash_trf'], club['cash_trf'], fee, total_to_trf])
    international_data.append(['Total International Contributions', data['total_international_ddf'], data['total_international_cash_direct'], 
                               data['total_international_cash_trf'], data['total_international_cash_trf'], data['total_international_cash_trf'] * 0.05, 
                               data['total_international_cash_trf'] * 1.05])
    
    other_donors_data = [['Other donors', 'Cash Direct to Project', 'Cash through TRF', 'Project Cash', '5% Fee', 'Total to TRF']]
    for donor in data['other_donors']:
        fee = donor['amount_trf'] * 0.05
        total_to_trf = donor['amount_trf'] + fee
        other_donors_data.append([donor['name'], donor['amount_direct'], donor['amount_trf'], donor['amount_trf'], fee, total_to_trf])
    
    endowed_gift_data = [['Endowed/Directed Gift', 'GIFT Number', 'Amount']]
    endowed_gift_data.append([data['endowed_gift_name'], data['endowed_gift_number'], data['endowed_gift']])
    
    summary_data = [
        ['Total Rotarian Contributions', data['total_ddf'] + data['total_cash_direct'] + data['total_cash_trf']],
        ['TRF World Fund match (80% of DDF)', data['world_fund_match']],
        ['Total Other Donors', data['total_other_donors_direct'] + data['total_other_donors_trf']],
        ['Endowed/Directed Gift', data['endowed_gift']],
        ['Total Project Funding', data['total_funding']]
    ]
    
    for table_data in [host_data, international_data, other_donors_data, endowed_gift_data, summary_data]:
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
    
    # Add warnings to PDF
    if data['warnings']:
        elements.append(Paragraph("Warnings:", styles['Heading2']))
        for warning in data['warnings']:
            elements.append(Paragraph(f"• {warning}", styles['Normal']))
        elements.append(Spacer(1, 12))
    
    # Add funding breakdown
    elements.append(Paragraph("Funding Breakdown:", styles['Heading2']))
    funding_breakdown = [
        ['Category', 'Amount', 'Percentage'],
        ['Host Contributions', f"${data['total_host_ddf'] + data['total_host_cash_direct'] + data['total_host_cash_trf']:,.2f}", 
         f"{(data['total_host_ddf'] + data['total_host_cash_direct'] + data['total_host_cash_trf']) / data['total_funding'] * 100:.1f}%"],
        ['International Contributions', f"${data['total_international_ddf'] + data['total_international_cash_direct'] + data['total_international_cash_trf']:,.2f}", 
         f"{data['international_contribution_percentage'] * 100:.1f}%"],
        ['World Fund Match', f"${data['world_fund_match']:,.2f}", f"{data['world_fund_match'] / data['total_funding'] * 100:.1f}%"],
        ['Other Donors', f"${data['total_other_donors_direct'] + data['total_other_donors_trf']:,.2f}", 
         f"{(data['total_other_donors_direct'] + data['total_other_donors_trf']) / data['total_funding'] * 100:.1f}%"],
        ['Endowed/Directed Gift', f"${data['endowed_gift']:,.2f}", f"{data['endowed_gift'] / data['total_funding'] * 100:.1f}%"],
        ['Total', f"${data['total_funding']:,.2f}", "100.0%"]
    ]
    t = Table(funding_breakdown)
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
    """
    Save project data to a JSON file.
    """
    with open(filename, 'w') as f:
        json.dump(data, f)

def load_project_data(filename):
    """
    Load project data from a JSON file.
    """
    with open(filename, 'r') as f:
        return json.load(f)

def main():
    st.set_page_config(page_title="Rotary International Grant Calculator", layout="wide")
    st.title("Rotary International Grant Calculator")

    # Initialize session state for dynamic rows
    if 'host_club_count' not in st.session_state:
        st.session_state.host_club_count = 1
    if 'international_club_count' not in st.session_state:
        st.session_state.international_club_count = 1
    if 'other_donor_count' not in st.session_state:
        st.session_state.other_donor_count = 1

    st.header("Project Details")
    col1, col2 = st.columns(2)
    with col1:
        application_number = st.text_input("Application #", key="application_number")
    with col2:
        project_country = st.text_input("Project Country", key="project_country")

    st.header("Host Rotary Clubs/Districts")
    host_clubs = []
    for i in range(st.session_state.host_club_count):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            name = st.text_input(f"Host Club/District Name #{i+1}", key=f"host_name_{i}")
        with col2:
            ddf = st.number_input(f"DDF Amount (USD) #{i+1}", min_value=0.0, format="%.2f", key=f"host_ddf_{i}")
        with col3:
            cash_direct = st.number_input(f"Cash Direct to Project (USD) #{i+1}", min_value=0.0, format="%.2f", key=f"host_cash_direct_{i}")
        with col4:
            cash_trf = st.number_input(f"Cash through TRF (USD) #{i+1}", min_value=0.0, format="%.2f", key=f"host_cash_trf_{i}")
        if name and (ddf > 0 or cash_direct > 0 or cash_trf > 0):
            host_clubs.append({"name": name, "ddf": ddf, "cash_direct": cash_direct, "cash_trf": cash_trf})

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Add Host Club"):
            st.session_state.host_club_count += 1
            st.rerun()
    with col2:
        if st.button("Remove Host Club") and st.session_state.host_club_count > 1:
            st.session_state.host_club_count -= 1
            st.rerun()

    st.header("International Rotary Clubs/Districts")
    international_clubs = []
    for i in range(st.session_state.international_club_count):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            name = st.text_input(f"International Club/District Name #{i+1}", key=f"int_name_{i}")
        with col2:
            ddf = st.number_input(f"DDF Amount (USD) #{i+1}", min_value=0.0, format="%.2f", key=f"int_ddf_{i}")
        with col3:
            cash_direct = st.number_input(f"Cash Direct to Project (USD) #{i+1}", min_value=0.0, format="%.2f", key=f"int_cash_direct_{i}")
        with col4:
            cash_trf = st.number_input(f"Cash through TRF (USD) #{i+1}", min_value=0.0, format="%.2f", key=f"int_cash_trf_{i}")
        if name and (ddf > 0 or cash_direct > 0 or cash_trf > 0):
            international_clubs.append({"name": name, "ddf": ddf, "cash_direct": cash_direct, "cash_trf": cash_trf})

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Add International Club"):
            st.session_state.international_club_count += 1
            st.rerun()
    with col2:
        if st.button("Remove International Club") and st.session_state.international_club_count > 1:
            st.session_state.international_club_count -= 1
            st.rerun()

    st.header("Other Donors")
    other_donors = []
    for i in range(st.session_state.other_donor_count):
        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input(f"Other Donor Name #{i+1}", key=f"other_name_{i}")
        with col2:
            amount_direct = st.number_input(f"Cash Direct to Project (USD) #{i+1}", min_value=0.0, format="%.2f", key=f"other_amount_direct_{i}")
        with col3:
            amount_trf = st.number_input(f"Cash through TRF (USD) #{i+1}", min_value=0.0, format="%.2f", key=f"other_amount_trf_{i}")
        if name and (amount_direct > 0 or amount_trf > 0):
            other_donors.append({"name": name, "amount_direct": amount_direct, "amount_trf": amount_trf})

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Add Other Donor"):
            st.session_state.other_donor_count += 1
            st.rerun()
    with col2:
        if st.button("Remove Other Donor") and st.session_state.other_donor_count > 1:
            st.session_state.other_donor_count -= 1
            st.rerun()

    st.header("Endowed/Directed Gift")
    col1, col2, col3 = st.columns(3)
    with col1:
        endowed_gift_name = st.text_input("Endowed/Directed Gift Name")
    with col2:
        gift_number = st.text_input("GIFT Number")
    with col3:
        endowed_gift_amount = st.number_input("Amount (USD)", min_value=0.0, format="%.2f")

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
                    "other_donors": other_donors,
                    "endowed_gift_name": endowed_gift_name,
                    "endowed_gift_number": gift_number,
                    "endowed_gift_amount": endowed_gift_amount
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
            st.session_state.host_club_count = len(project_data["host_clubs"])
            st.session_state.international_club_count = len(project_data["international_clubs"])
            st.session_state.other_donor_count = len(project_data["other_donors"])
            st.rerun()

    if st.button("Calculate and Generate PDF"):
        if not application_number or not project_country:
            st.error("Please enter both Application # and Project Country.")
        elif not host_clubs and not international_clubs:
            st.error("Please enter at least one Host or International Rotary Club/District.")
        else:
            results = calculate_totals(host_clubs, international_clubs, other_donors, endowed_gift_amount)
            
            funding_warnings = validate_funding(results)
            donor_warnings = validate_other_donors(other_donors)
            
            for warning in funding_warnings + donor_warnings:
                st.warning(warning)
            
            project_details = {
                "application_number": application_number,
                "project_country": project_country
            }
            
            pdf_data = {
                "host_clubs": host_clubs,
                "international_clubs": international_clubs,
                "other_donors": other_donors,
                "endowed_gift_name": endowed_gift_name,
                "endowed_gift_number": gift_number,
                "warnings": funding_warnings + donor_warnings,
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
                ["Total Host Contributions", f"${results['total_host_ddf'] + results['total_host_cash_direct'] + results['total_host_cash_trf']:,.2f}"],
                ["Total International Contributions", f"${results['total_international_ddf'] + results['total_international_cash_direct'] + results['total_international_cash_trf']:,.2f}"],
                ["Total Rotarian Contributions", f"${results['total_ddf'] + results['total_cash_direct'] + results['total_cash_trf']:,.2f}"],
                ["TRF World Fund match (80% of DDF)", f"${results['world_fund_match']:,.2f}"],
                ["Total Other Donors", f"${results['total_other_donors_direct'] + results['total_other_donors_trf']:,.2f}"],
                ["Endowed/Directed Gift", f"${results['endowed_gift']:,.2f}"],
                ["Total Project Funding", f"${results['total_funding']:,.2f}"]
            ]
            
            df = pd.DataFrame(summary_data, columns=["Item", "Amount"])
            st.table(df)
            
            # Display pie chart in Streamlit
            st.header("Funding Breakdown")
            fig, ax = plt.subplots(figsize=(10, 6))
            labels = ['Host Contributions', 'International Contributions', 'World Fund Match', 'Other Donors', 'Endowed/Directed Gift']
            sizes = [
                results['total_host_ddf'] + results['total_host_cash_direct'] + results['total_host_cash_trf'],
                results['total_international_ddf'] + results['total_international_cash_direct'] + results['total_international_cash_trf'],
                results['world_fund_match'],
                results['total_other_donors_direct'] + results['total_other_donors_trf'],
                results['endowed_gift']
            ]
            colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff99cc']
            ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            st.pyplot(fig)

    # Add explanatory text about the funding structure
    st.header("How Rotary Global Grant Funding Works")
    st.markdown("""
    1. **DDF (District Designated Fund)**: This is money allocated by Rotary districts from their District Designated Fund. It's not cash, but rather funds available for the district to use on Rotary Foundation programs.
    
    2. **Cash Contributions**:
       - **Cash Direct to Project**: This is actual money contributed directly to the project, bypassing The Rotary Foundation (TRF).
       - **Cash through TRF**: This is cash contributed to the project through The Rotary Foundation. It's subject to a 5% fee.
    
    3. **TRF World Fund Match**: The Rotary Foundation matches 80% of the total DDF contributions, up to a maximum of $400,000.
    
    4. **Other Donors**: Additional contributions from other sources can be included in the project funding. They can contribute either directly to the project or through TRF.
    
    5. **Endowed/Directed Gift**: This is a special type of contribution that is treated as project cash and is not subject to the 5% fee.
    
    6. **Total Project Funding**: This includes all DDF, cash contributions (both direct and through TRF), the World Fund match, other donor contributions, and the Endowed/Directed Gift.
    
    **Key Points**:
    - International partner contributions must be at least 15% of the total.
    - There's no minimum World Fund match, but there's a maximum of $400,000.
    - The total funding must be at least $30,000.
    - Non-Rotarian contributions can't come from a cooperating organization or a beneficiary of the project.
    - Individual Rotarian contributions should be entered under their club's name.
    - Cash contributions through TRF are subject to a 5% fee, which is added to the total amount sent to TRF.
    - Endowed/Directed Gifts are not subject to the 5% fee and are treated as project cash.
    
    This calculator helps you plan and visualize your Global Grant funding structure, ensuring it meets Rotary International's requirements.
    """)

if __name__ == "__main__":
    main()