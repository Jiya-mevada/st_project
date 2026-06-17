import cv2
import streamlit as st
import numpy as np
import pytesseract
import re

st.set_page_config(layout="wide")

col1, col2, col3, col4 = st.columns([1, 1, 2, 1])
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

with col1:
    aadhar_upload=st.file_uploader("Upload aadhar card (front)",type=['jpg','jpeg','png'])
    voter_upload=st.file_uploader("Upload Voter id (front)",type=['jpg','jpeg','png'])
    passport_upload=st.file_uploader("Upload Passport (front)",type=['jpg','jpeg','png'])
    pancard_upload=st.file_uploader("Upload Pancard (front)",type=['jpg','jpeg','png'])

    verify = st.button("Verify Documents")

with col2:
    aadhar_upload2=st.file_uploader("Upload aadhar card (back)",type=['jpg','jpeg','png'])
    voter_upload2=st.file_uploader("Upload voter id(back)",type=['jpg','jpeg','png'])


with col3:
    if verify:

        if aadhar_upload and passport_upload and pancard_upload and voter_upload and aadhar_upload2 and voter_upload2:

            docs = [
                ("AADHAAR", [aadhar_upload,aadhar_upload2]),
                ("PAN", [pancard_upload]),
                ("PASSPORT",[passport_upload]),
                ("VOTER ID", [voter_upload,voter_upload2])
            ]

            from collections import defaultdict
            names = {}

            for doc_type, uploaded_files in docs:
                text = ""
                for uploaded_file in uploaded_files:
                    file_bytes = np.asarray(bytearray(uploaded_file.read()),dtype=np.uint8)
                    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                    
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    text += pytesseract.image_to_string(gray)
                    

                    if doc_type == "PASSPORT":
                        cropped_bday=img[426:472, 1134:1373]
                        cropped_bday_gray=cv2.cvtColor(cropped_bday,cv2.COLOR_BGR2GRAY)
                        crop_bday = pytesseract.image_to_string(cropped_bday_gray)

                        cropped_expiry = img[687:766, 1011:1339]
                        cropped_expiry_gray = cv2.cvtColor(cropped_expiry,cv2.COLOR_BGR2GRAY)
                        crop_expiry = pytesseract.image_to_string(cropped_expiry_gray)


                text = text.upper()

                document_number = ""
                document_name = ""
                document_surname = ""
                document_dob = ""
                document_issue = ""
                document_expiry = ""
                father_name=""
                document_address=""
                husband_name=""


                if doc_type == "PASSPORT":

                    passport_match = re.search(r'\b[A-Z][0-9]{7}\b',text)
                    if passport_match:
                        document_number = passport_match.group()

                    dob_match = re.search(r'\b\d{2}[/-]\d{2}[/-]\d{4}\b',crop_bday)
                    if dob_match:
                        document_dob = dob_match.group()

                    name_match= re.search(r"Given Name.*?\n([A-Z ]+)",text,re.IGNORECASE)
                    if name_match:
                        document_name = name_match.group(1)
                    names["PASSPORT"] = f"{document_name} {document_surname}".strip()

                    surname_match= re.search(r"Surname.*?\n([A-Z ]+)",text,re.IGNORECASE)
                    if surname_match:
                        document_surname=surname_match.group(1)

                    expiry_date=re.search(r'\b\d{2}[/-]\d{2}[/-]\d{4}\b',crop_expiry)
                    if expiry_date:
                        document_expiry=expiry_date.group()

                    st.subheader(doc_type)
                    # st.write(text)
                    st.write("Name :", document_name,"  ",document_surname)
                    st.write("DOB :", document_dob)
                    st.write("Document Number :", document_number)
                    st.write("Date of Expiry : ",document_expiry)
                    st.divider()


                elif doc_type == "AADHAAR":

                    aadhaar_match = re.search(r'\b\d{4}\s?\d{4}\s?\d{4}\b',text)
                    if aadhaar_match:
                        document_number = aadhaar_match.group()

                    dob_match=re.search(r'(?:DOB|DATE\s*OF\s*BIRTH)\s*:?\s*(\d{2}[/-]\d{2}[/-]\d{4})',text,re.IGNORECASE)
                    if dob_match:
                        document_dob=dob_match.group(1)

#                   name_match=re.search(r'GOVERNMENT\s+OF\s+INDIA\s+([A-Z\s]+?)\s+(?:DOB|DATE\s*OF\s*BIRTH|YEAR OF BIRTH|YOB)',text,re.IGNORECASE | re.DOTALL)
#                   if name_match:
#                        document_name = name_match.group(1).strip()

                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    for i, line in enumerate(lines):
                        if "DOB" in line.upper():
                            candidate = lines[i-1]
                            if len(candidate.split()) >= 2 and not any(x in candidate.upper() for x in ["INDIA", "GOVERNMENT", "AADHAAR"]):
                                document_name = candidate
                            break
                    names["AADHAAR"] = document_name
                    

                    address_match = re.search(r'(?:D\/O|S\/O|W\/O)\s*[^,]+,\s*(.*?)(?=\b\d{6}\b)',text,re.IGNORECASE | re.DOTALL)
                    if address_match:
                        document_address = address_match.group(1).strip()
                    document_address = re.sub(r'\s+', ' ', document_address)
                    
                    st.subheader(doc_type)
                    # st.write(text)
                    st.write("Name :", document_name)
                    st.write("DOB :", document_dob)
                    st.write("Document Number :", document_number)
                    st.write("Address : ",document_address)
                    st.divider()
        


                elif doc_type == "PAN":

                    pan_match = re.search(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b',text)
                    if pan_match:
                        document_number = pan_match.group()

                    dob_match=re.search(r'\b\d{2}[/-]\d{2}[/-]\d{4}\b', text)
                    if dob_match:
                        document_dob=dob_match.group()

                    name_match = re.search(r'NAME.*?\n([A-Z ]+)',text,re.IGNORECASE)
                    if name_match:
                        document_name = name_match.group(1).strip()
                    names["PAN"] = document_name

                    father_match = re.search(r"FATHER'?S\s+NAME\s*\n([A-Z ]+)",text,re.IGNORECASE)
                    if father_match:
                        father_name = father_match.group(1).strip()

                    st.subheader(doc_type)
                    # st.write(text)
                    st.write("Name :", document_name)
                    st.write("DOB :", document_dob)
                    st.write("Document Number :", document_number)
                    st.write("Father Name : ",father_name)
                    st.divider()

                    
                

                elif doc_type == "VOTER ID":

                    voter_match = re.search(r'\b[A-Z]{3}[0-9]{7}\b',text)
                    if voter_match:
                        document_number = voter_match.group()

                    dob_match=dob_match = re.search(r'(?:DOB|DATE\s*OF\s*BIRTH)(?:\s*/\s*AGE)?\s*:?\s*(\d{2}[/-]\d{2}[/-]\d{4})',text,re.IGNORECASE)
                    if dob_match:
                        document_dob = dob_match.group(1)

                    husband_match = re.search(r"HUSBAND'?S\s*NAME\s*:\s*([A-Z ]+)",text,re.IGNORECASE)
                    if husband_match:
                        husband_name = husband_match.group(1).strip()

                    text = text.replace("É", "E").replace("È", "E").replace("Ë", "E")
                    name_match = re.search(r'(?:ELECTORS\s*NAME|NAME)\s*[:\-]?\s*([A-Z ]+)',text,re.IGNORECASE)
                    if name_match:
                        document_name = name_match.group(1).strip()
                    names["VOTER ID"] = f"{document_name} {husband_name}".strip()

                    address_match = re.search(r'ADDRESS\s*[:\-]?\s*(.*?\b\d{6}\b)',text,re.IGNORECASE | re.DOTALL)
                    if address_match:
                        document_address=address_match.group(1).strip()

                    st.subheader(doc_type)
    
                    st.write("Name :", document_name," ",husband_name)
                    st.write("DOB :", document_dob)
                    st.write("Document Number :", document_number)
                    st.write("Document Address : ",document_address)

    else:
        st.write("Please upload all documents.")

with col4:
    st.subheader("Verification Result")
    groups = defaultdict(list)
            
    for doc, name in names.items():
        if not name:
            continue
        clean_name = name.upper().strip()
        groups[clean_name].append(doc)

    different_docs = []

    for name, docs in groups.items():
        if len(docs) > 1:
            st.write(f"Matching Documents: {', '.join(docs)}")
        else:
            different_docs.extend(docs)

    st.write(f"Different Document: {different_docs}")