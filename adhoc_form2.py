


import streamlit as st
import io
import datetime as dt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph
import os

############################################################################

## Pdf Formatting 

############################################################################


def create_pdf(form_data, grp_num, grp_nme, desc, comments):
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    styles = getSampleStyleSheet()

    # Header fill
    pdf.setStrokeColor(colors.blue)
    pdf.setFillColor(colors.blue)
    head_x, head_y, head_width, head_height = 10, 700, 592, 50
    pdf.rect(head_x, head_y, head_width, head_height, stroke=0, fill=1)

    # Header Text
    pdf.setFillColor(colors.white)
    pdf.setFont("Times-Bold", 24)
    text_x = head_x + 10
    text_y = head_y + head_height / 2 - 12

    text = "UW Reports Ad-Hoc Request Form"
    pdf.drawString(text_x, text_y, text)

    # Group header text - Grp Num
    pdf.setFillColor(colors.black)
    pdf.setFont("Times-Bold", 14)
    gr_num_x = text_x
    gr_num_y = text_y - 35

    gr_num = f"Group Number: {grp_num}"
    pdf.drawString(gr_num_x, gr_num_y, gr_num)

    # Group header text - Grp Name
    gr_nme_x = gr_num_x
    gr_nme_y = gr_num_y - 18

    gr_nme = f"Group Name: {grp_nme}"
    pdf.drawString(gr_nme_x, gr_nme_y, gr_nme)

    custom_style = ParagraphStyle(
        'CustomStyle',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        leading=15,
        spaceAfter=10,
        alignment=0
    )

    # Add a paragraph for description
    description = '''<font size="14"><b> Description:  </b></font>{}'''.format(desc)
    paragraph1 = Paragraph(description, custom_style)
    
    p_w, p_h = paragraph1.wrap(width-1*inch, height-2*inch)
    paragraph1.drawOn(pdf, gr_nme_x, gr_nme_y - 50)

    # Add a paragraph for comments
    if comments:
        cmnts = '''<b>Additional Comments:</b>{}'''.format(comments)
        paragraph2 = Paragraph(cmnts, custom_style)
        
        p_w, p_h = paragraph2.wrap(width-1*inch, height-1*inch)
        paragraph2.drawOn(pdf, gr_nme_x, 60)

    # Body Text Box
    content_x = 10
    content_y = 10
    content_width = 592
    content_height = 580
    pdf.rect(content_x, content_y, content_width, content_height, fill=0)

    # Body Content Formatting  
    text_object = pdf.beginText()  
    text_object.setTextOrigin(content_x + 5, content_y + content_height - 25)  
    
    # Below, there is a dictionary called form_data. It contains all of the info that will be placed into the pdf form # 

    bullet = chr(8226) 
    for k, v in form_data.items():  
        if v: 
            # Create bullet 
            text_object.textOut(bullet + " ")

            # Set font for the key  
            text_object.setFont("Helvetica-Bold", 12)  
            key_text = k + ":  "  
            text_object.textOut(key_text)  
    
            # Set font for the value  
            text_object.setFont("Times-Roman", 12)  
            value_text = v  
            text_object.textOut(value_text)  
    
            text_object.moveCursor(0,30)  
    
    pdf.drawText(text_object)  


    pdf.showPage()
    pdf.save()
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

############################################################################

## Ad-hoc Form Portion of the program

############################################################################

# Streamlit Interface
def main():

    st.title("UW Reports Ad-Hoc Request Form")
    st.divider()

    reviewed = False  # State variable for form review
    
    # Initialize a variable to check if all fields are filled
    all_fields_filled = True
    
    # Text dialog box for email and name with an option to add more

    names = st.text_input("**Requester Name:**")
    
    # Check if field is empty
    if not names:
        all_fields_filled = False
    
    # Text dialog box for number (up to 25 chars in case of multiple groups)
    grp_num = st.text_input("**Group Number**", max_chars=25)
    if not grp_num:
        all_fields_filled = False
    
    # Text box for large character field (up to 120 characters)
    grp_nme = st.text_area("**Group Name**", max_chars=50)
    if not grp_nme:
        all_fields_filled = False
    
    # Two dropdown menus with 3 options each
    recipient = st.selectbox("**Who will receive this report?**", options = ['','Broker', 'Group', 'New Carrier', 'Internal Only'] )

    if recipient == 'Broker':
        broker = ':blue[ISA is required if the report is Member identifier detail, Claim level detail and/or Case level detail]'
        st.caption(broker)
    elif recipient == 'Group':
        group = ''':blue[For Fully Insured Groups: If the report request includes Member identifier detail, 
                    Claim level detail and/or Case level detail, HIPAA Certification is required for reports going to group only.]'''
        st.caption(group)
    elif recipient == 'New Carrier':
        carrier = ''':blue[UW reports does not send reports externally. Requester is responsible for providing report to new carrier.]'''
        st.caption(carrier)

    financial = st.selectbox("**Financial Arrangement:**", options = ['', 'Self-funded', 'Fully Insured - HIPAA Certified', 'Fully Insured - Non-HIPAA Certified'])
    
    if financial == 'Fully Insured - HIPAA Certified':
        fi_hip = ''':blue[Claim level, PHI, and/or aggregate data - OK to send to group.]'''
        st.caption(fi_hip)

    elif financial == 'Fully Insured - Non-HIPAA Certified':
        fi_no_hip = ''':blue[No PHI or claim level detail can be sent to group - only aggregate and/or de-identified data.]'''
        st.caption(fi_no_hip)

    if any(not field for field in [recipient, financial]):
        all_fields_filled = False

   #  Description text box for a paragraph
    desc = st.text_area("**Report Description:**  ", max_chars=275)
    if not desc:
        all_fields_filled = False

    # desc = '''This is a long description. I want to see how it will do when it is placed in the pdf. 
    # Will it fit within the confines of the space or not? What do you think? Think it will fit? We'll see!'''
    
    st.divider()

    # Assigning none to all date variables to start
    inc_dt_strt, inc_dt_end, pd_dt_strt, pd_dt_end, strt_dt, end_dt, dt_as_of, curr_dt = '', '', '', '', '', '', '', ''

    # Dropdown with two options and a date range picker
    dt_choice = st.selectbox("**Dates:**", options = ['', 'Paid', 'Incurred', 'Paid and Incurred', 'Subscriber/Member Listing As Of..', 'Subscriber/Member Listing Current'])
    if dt_choice == 'Paid and Incurred':
        rng1, rng2 = st.columns(2)
        inc_dt_strt = rng1.date_input("Incurred Start Date:", value = dt.date(2023,1,1), format="MM-DD-YYYY")
        inc_dt_end = rng2.date_input("Incurred End Date:", format="MM-DD-YYYY")

        rng3, rng4 = st.columns(2)
        pd_dt_strt = rng1.date_input("Paid Start Date:",value = dt.date(2023,1,1), format="MM-DD-YYYY")
        pd_dt_end = rng2.date_input("Paid End Date:", format="MM-DD-YYYY")

        dates = f"""
        **Date Ranges:**
        * **Incurred Start:** {inc_dt_strt.strftime('%m-%d-%Y')}
        * **Incurred End:** {inc_dt_end.strftime('%m-%d-%Y')}
        * **Paid Start:** {pd_dt_strt.strftime('%m-%d-%Y')}
        * **Paid End:** {pd_dt_end.strftime('%m-%d-%Y')}
        """
        if not any([inc_dt_strt, pd_dt_strt]):
            all_fields_filled = False
    elif dt_choice == 'Paid':
        rng1, rng2 = st.columns(2)
        pd_dt_strt = rng1.date_input("Paid Start Date:",value = dt.date(2023,1,1), format="MM-DD-YYYY")
        pd_dt_end = rng2.date_input("Paid End Date:", format="MM-DD-YYYY")

        dates = f"""
        **Date Ranges:**
        * **Paid Start Date:** {pd_dt_strt.strftime('%m-%d-%Y')}
        * **Paid End Date:** {pd_dt_end.strftime('%m-%d-%Y')}
        """
    elif  dt_choice == 'Incurred':
        rng1, rng2 = st.columns(2)
        inc_dt_strt = rng1.date_input("Incurred Start Date:",value = dt.date(2023,1,1), format="MM-DD-YYYY")
        inc_dt_end = rng2.date_input("Incurred End Date:", format="MM-DD-YYYY")

        dates = f"""
        **Date Ranges:**
        * **Incurred Start Date:** {inc_dt_strt.strftime('%m-%d-%Y')}
        * **Incurred End Date:** {inc_dt_end.strftime('%m-%d-%Y')}
        """
    elif dt_choice == 'Subscriber/Member Listing As Of..':

        dt_as_of = st.date_input("Eligibility As Of:",value = dt.date(2024,1,1), format="MM-DD-YYYY")
        dates = f"""
        **Date Ranges:**
        * **Eligibility As Of:** {dt_as_of.strftime('%m-%d-%Y')}
        """
    elif dt_choice == 'Subscriber/Member Listing Current':
        curr_dt = dt.date.today().strftime('%m-%d-%Y')
        dates = f"""
            ***Current Date:*** {curr_dt}
            """
    else:
        dates = None

    if not dates:
        all_fields_filled = False
    st.divider()
    # Data Types
    st.write("**Choose at least one data type:**")

    # Check box with four options
    med = st.checkbox("Medical")
    rx = st.checkbox("Pharmacy")
    dental = st.checkbox("Dental")
    vision = st.checkbox("Vision")
    other = st.checkbox("Other")

    if dental:
        dental = 'Yes'
    if rx:
        rx = 'Yes'
        st.caption(':blue[Please send CPD approval with request, if needed.]')
    if med: 
        med = 'Yes'
    if vision:
        vision = 'Yes'
    if other:
        other = 'Yes'
    
    # Generate list for Review option later
    data_types = [dental, rx, med, vision, other]

    if not any(field for field in data_types):
        all_fields_filled = False

    # Three text boxes close to each other vertically that can take up to 120 characters each
    additional = {}
    add_require = st.selectbox("**Additional Requirements needed?** (e.g. subgroup, plan, department)", ("No", "Yes"))
    if add_require == "Yes":
        additional['Subgroup'] = st.text_input("Subgroup(s):", max_chars=75)
        additional['Plan_ID'] = st.text_input("Class Plan(s):", max_chars=75)
        additional['Department'] = st.text_input("Department(s):", max_chars=75)

    filled_sections = []
    for option, details in additional.items():
        if details:
            filled_section = f"* **{option}**: {details}"
            filled_sections.append(filled_section)
    
    comments = st.text_area("**Additional Comments** (*optional*):")
    
    st.divider()

    # Create state for review button
    if 'clicked' not in st.session_state:
        st.session_state.clicked = False

    def click_button():
        st.session_state.clicked = True

    form_data = {
                    "Name": names,
                    "Recipient": recipient,
                    "Financial Arrangement": financial,
                    "Incurred Date Start": str(inc_dt_strt),
                    "Incurred Date End": str(inc_dt_end),
                    "Paid Date Start": str(pd_dt_strt),
                    "Paid Date End": str(pd_dt_end),
                    "Eligibility As Of (for Member List)": str(dt_as_of),
                    "Current Date (for Member List)": str(curr_dt),
                    "Medical": med,
                    "Rx": rx,
                    "Dental": dental,
                    "Vision": vision,
                    "Other": other,
                    "Subgroup": additional.get('Subgroup', ''),
                    "Plan ID": additional.get('Plan_ID', ''),
                    "Department": additional.get('Department', '')
                }
    
    # Maybe remove this line??
    pdf = create_pdf(form_data, grp_num, grp_nme, desc, comments)

    st.caption("Please review your selections before downloading pdf")
    # Button to review the form
    if st.button("Review", on_click=click_button):
        st.subheader("Review your information")
        st.markdown('**Name:** {}'.format(names))
        st.markdown('**Group Number:** {}'.format(grp_num))
        st.markdown('**Group Name:** {}'.format(grp_nme))
        st.markdown('**Report Recipient:** {}'.format(recipient))
        st.markdown('**Financial Arrangement:** {}'.format(financial))
        st.markdown('**Report Description:** {}'.format(desc))
        st.markdown(dates)
        if med:
            st.markdown('**Medical:** Yes')
        if rx:
            st.markdown('**Rx:** Yes')
        if dental:
            st.markdown('**Dental:** Yes')
        if vision:
            st.markdown('**Vision:** Yes')
        if other:
            st.markdown('**Other:** Yes')
        if filled_sections:
            st.markdown("\n".join(filled_sections))
        else:
            st.markdown("No additional requirements needed")
        if comments:
            st.markdown(f" **Additional Comments:** {comments}") 

    if st.session_state.clicked:
        if all_fields_filled:
            st.download_button("Download pdf", pdf, f"Ad hoc request_{grp_num}.pdf", mime="application/pdf")
        else:
            st.warning("You must fill in all blank fields")

        


############################################################################

if __name__ == '__main__':
    main()

# streamlit run c:\Users\b17572f\Documents\Jupyter\adhoc_form2.py
