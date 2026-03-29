from fpdf import FPDF

pdf = FPDF(orientation='P', unit='mm', format='A4')
pdf.add_page()
pdf.set_font('Helvetica', 'B', 16)
pdf.cell(180, 10, 'TechCorp HR Policy Document', ln=True, align='C')
pdf.ln(10)

# Section 1
pdf.set_font('Helvetica', 'B', 14)
pdf.cell(180, 10, '1. Employee Handbook', ln=True)

pdf.set_font('Helvetica', 'B', 11)
pdf.cell(180, 8, 'Office Hours', ln=True)
pdf.set_font('Helvetica', '', 10)
pdf.cell(180, 6, 'Standard office hours are 9:00 AM to 6:00 PM, Monday through Friday.', ln=True)
pdf.cell(180, 6, 'Core hours are 10:00 AM to 4:00 PM. Remote work: 2 days per week.', ln=True)
pdf.ln(5)

pdf.set_font('Helvetica', 'B', 11)
pdf.cell(180, 8, 'Dress Code', ln=True)
pdf.set_font('Helvetica', '', 10)
pdf.cell(180, 6, 'Business Casual dress code. Jeans permitted on Fridays.', ln=True)
pdf.cell(180, 6, 'Client meetings require formal business attire.', ln=True)
pdf.ln(5)

pdf.set_font('Helvetica', 'B', 11)
pdf.cell(180, 8, 'Code of Conduct', ln=True)
pdf.set_font('Helvetica', '', 10)
pdf.cell(180, 6, 'Respectful workplace policies apply to all employees.', ln=True)
pdf.cell(180, 6, 'Zero tolerance for harassment or discrimination.', ln=True)
pdf.ln(10)

# Section 2
pdf.set_font('Helvetica', 'B', 14)
pdf.cell(180, 10, '2. Leave and Vacation Policy', ln=True)

pdf.set_font('Helvetica', 'B', 11)
pdf.cell(180, 8, 'Sick Leave', ln=True)
pdf.set_font('Helvetica', '', 10)
pdf.cell(180, 6, 'Employees are entitled to 12 days of paid sick leave per year.', ln=True)
pdf.cell(180, 6, 'Doctor note required for 3+ consecutive days absence.', ln=True)
pdf.ln(5)

pdf.set_font('Helvetica', 'B', 11)
pdf.cell(180, 8, 'Maternity and Paternity Leave', ln=True)
pdf.set_font('Helvetica', '', 10)
pdf.cell(180, 6, 'Maternity Leave: 26 weeks of paid leave for birth mothers.', ln=True)
pdf.cell(180, 6, 'Paternity Leave: 2 weeks of paid leave for fathers.', ln=True)
pdf.cell(180, 6, 'Adoption Leave: 16 weeks primary, 2 weeks secondary caregiver.', ln=True)
pdf.ln(5)

pdf.set_font('Helvetica', 'B', 11)
pdf.cell(180, 8, 'Leave Carry-Forward Rules', ln=True)
pdf.set_font('Helvetica', '', 10)
pdf.cell(180, 6, 'Up to 5 days of unused leave can be carried to next year.', ln=True)
pdf.cell(180, 6, 'Carried-forward leave must be used by March 31st.', ln=True)
pdf.ln(10)

# Section 3
pdf.add_page()
pdf.set_font('Helvetica', 'B', 14)
pdf.cell(180, 10, '3. Health Insurance FAQ', ln=True)
pdf.ln(5)

pdf.set_font('Helvetica', 'B', 10)
pdf.cell(180, 6, 'Q: Does the plan cover dental?', ln=True)
pdf.set_font('Helvetica', '', 10)
pdf.cell(180, 6, 'A: Yes, up to $500 per year for cleanings and basic procedures.', ln=True)
pdf.ln(4)

pdf.set_font('Helvetica', 'B', 10)
pdf.cell(180, 6, 'Q: Who is eligible for coverage?', ln=True)
pdf.set_font('Helvetica', '', 10)
pdf.cell(180, 6, 'A: Spouses and children under 25 are eligible.', ln=True)
pdf.ln(4)

pdf.set_font('Helvetica', 'B', 10)
pdf.cell(180, 6, 'Q: When does coverage begin?', ln=True)
pdf.set_font('Helvetica', '', 10)
pdf.cell(180, 6, 'A: First day of the month following your start date.', ln=True)
pdf.ln(4)

pdf.set_font('Helvetica', 'B', 10)
pdf.cell(180, 6, 'Q: Does the plan cover vision?', ln=True)
pdf.set_font('Helvetica', '', 10)
pdf.cell(180, 6, 'A: Yes, one eye exam per year and $200 for glasses.', ln=True)
pdf.ln(4)

pdf.set_font('Helvetica', 'B', 10)
pdf.cell(180, 6, 'Q: What is the annual deductible?', ln=True)
pdf.set_font('Helvetica', '', 10)
pdf.cell(180, 6, 'A: $500 for individuals, $1000 for families.', ln=True)
pdf.ln(4)

pdf.set_font('Helvetica', 'B', 10)
pdf.cell(180, 6, 'Q: Are mental health services covered?', ln=True)
pdf.set_font('Helvetica', '', 10)
pdf.cell(180, 6, 'A: Yes, up to 20 sessions per year with in-network providers.', ln=True)
pdf.ln(4)

pdf.set_font('Helvetica', 'B', 10)
pdf.cell(180, 6, 'Q: What prescription drugs are covered?', ln=True)
pdf.set_font('Helvetica', '', 10)
pdf.cell(180, 6, 'A: Generic $10 copay, brand-name $30, specialty $50.', ln=True)
pdf.ln(4)

pdf.set_font('Helvetica', 'B', 10)
pdf.cell(180, 6, 'Q: Is there an out-of-pocket maximum?', ln=True)
pdf.set_font('Helvetica', '', 10)
pdf.cell(180, 6, 'A: $3000 individual, $6000 family per year.', ln=True)

pdf.output("data/HR_Policy_Document.pdf")
print("PDF created successfully: data/HR_Policy_Document.pdf")
