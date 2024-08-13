import io
import os
import re
import spacy
import pandas as pd
import docx
from spacy.matcher import Matcher
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from dateutil import parser
from datetime import *
from datetime import datetime
import time

df=pd.read_csv("/Users/pranavaggarwal/Documents/Personal Website/app/data.csv")

headings=["about","about me","education","experience","projects","volunteer","skills","Education","EDUCATION","Experience","EXPERIENCE"]
skills=df["skills"].tolist()
degree=["b.e.","be","b.tech","btech","bs","b.s.","b.sc","bsc"]
functions=["name","email","phoneno.","education","experience","skills","tags","projects","degree","total_work_experience"]
data={}
import spacy
roberta_nlp = spacy.load("en_core_web_trf")
nlp=roberta_nlp
nlp_sm=nlp

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as fh:
        for page in PDFPage.get_pages(fh, 
                                      caching=True,
                                      check_extractable=True):
            resource_manager = PDFResourceManager()
            fake_file_handle = io.StringIO()
            converter = TextConverter(resource_manager, fake_file_handle, codec='utf-8', laparams=LAParams())
            page_interpreter = PDFPageInterpreter(resource_manager, converter)
            page_interpreter.process_page(page)
 
            text = fake_file_handle.getvalue()
            yield text
 
            # close open handles
            converter.close()
            fake_file_handle.close()


def extract_text_from_word_doc(filename: str) -> str:
    # Open the Word document
    document = docx.Document(filename)

    # Initialize an empty string to store the text
    text = ""

    # Iterate through the paragraphs in the document
    for paragraph in document.paragraphs:
        # Get the text of the paragraph, including any formatting
        paragraph_text = paragraph.text

        # Add a newline character after each paragraph, to maintain the spacing
        text += paragraph_text + "\n"

    # Return the extracted text
    return text


def extract_text(file_path, extension):
    '''
    Wrapper function to detect the file extension and call text extraction function accordingly
    :param file_path: path of file of which text is to be extracted
    :param extension: extension of file `file_name`
    '''
    text = ''
    if extension == '.pdf':
        for page in extract_text_from_pdf(file_path):
            text += ' ' + page
    elif extension == '.docx' or extension == '.doc':
        text = extract_text_from_word_doc(file_path)
    return text

def extract_email(text):
  # Use a regular expression to search for email addresses
  email_regex = r'''(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b'''
  limst= re.findall(email_regex, text)
  for k in limst:
    return k

def extract_phone_number(text):
  # Use a regular expression to search for phone numbers
  phone_regex = r'\b(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})|(\+\d{1,2}[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4})\b'
  
  limst=re.findall(phone_regex, text)
  #flist=[]
  for i in limst:
    for k in i:
      if k != "":
        return k

def extract_website_links(text):
  # Use a regular expression to search for website links
  website_regex = r'https?://[^\s<>"]+|www\.[^\s<>"]+\.[^\s<>"]+|linkedin\.com/[^\s<>"]+'
  limst=re.findall(website_regex, text)
  for link in limst:
    if ')' in link:
      link=link[:-1]

  return limst


def text_cleaner(text):
    doc = roberta_nlp(text)
    # Extract all the noun chunks in the text
    noun_chunks = [chunk.text for chunk in doc.noun_chunks]
    # Extract all the entities in the text
    entities = [ent.text for ent in doc.ents]
    # Extract all the verbs in the text
    final_limst=noun_chunks+entities
    stri=""
    for i in final_limst:
      stri+=i+" "
    return stri




def extract_linkedin(links):
  for link in links:
    if "linkedin" and "www. "in link:
      return link
    elif "linkedin" in link:
      return "www."+link

def extract_skills(pipeline,text):
    nlp_text = pipeline(text)
    noun_chunks=nlp_text.noun_chunks
    tag=[]
    ignore=["DATE","CARDINAL"]
    # removing stop words and implementing word tokenization
    tokens = [token.text for token in nlp_text if not token.is_stop]
    
    global skills
    for token in nlp_text.ents:
      if token.label_ not in ignore:
        if token.text not in tag:
          tag.append(token.text)

    # extract values
    
    skillset = []
    
    # check for one-grams (example: python)
    for token in tokens:
        if token.lower() in skills:
            skillset.append(token)
    
    # check for bi-grams and tri-grams (example: machine learning)
    for token in noun_chunks:
        token = token.text.lower().strip()
        if token in skills:
            skillset.append(token)
    
    return tag, [i.capitalize() for i in set([i.lower() for i in skillset])]

def entities(pipeline, text):
    
    # Create a document 
    document = pipeline(text)
    # Entity text & label extraction
    return document.ents

from spacy.matcher import Matcher

nlp = roberta_nlp

# initialize matcher with a vocab
matcher = Matcher(nlp.vocab)

def extract_name(resume_text):
    nlp_text = nlp(resume_text)
    
    # First name and Last name are always Proper Nouns
    pattern = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]
    matcher.add('NAME',[pattern])
    
    matches = matcher(nlp_text)
    for match_id, start, end in matches:
        span = nlp_text[start:end]
        return span.text

#removiing all the basic data
def rem_basic(text):
  email_list= [extract_email(text)]
  phone_list=[extract_phone_number(text)]
  link_list=extract_website_links(text)
  name=[extract_name(text)]
  total_list=email_list+phone_list+link_list+name
  for i in total_list:
    text= text.replace(i,"")
  
  nt=text
  
  return nt

def f3(stri):
    prevnl = -1
    while True:
      nextnl = stri.find('\n', prevnl + 1)
      if nextnl < 0: break
      yield stri[prevnl + 1:nextnl]
      prevnl = nextnl

def education(text):
  education_flist=[]
  k=""
  deg=[]
  for i in f3(text):
    i=i.strip()
    k=k+"\n"+i
    if i.strip() == "":
      education_flist.append(k.strip())
      k=""
  education_flist.append(k.strip())
  for i in education_flist:
    if i =="":
      education_flist.remove(i)
  education_list=[]
  for i in education_flist:
    dictf={}
    entities_l=entities(roberta_nlp,i)
    condition=False
    for p in degree:
      if p in i.lower().strip() and p not in deg:
        deg.append(p)

    for k in entities_l:
      if k.label_=="ORG":
        dictf["name"]=k.text
        condition=True
      elif k.label_=="DATE" and condition:
        dictf["date"]=k.text
      elif k.label_=="GPE" and condition:
        dictf["place"]=k.text
      i=i.replace(k.text,"")
    if condition:
      dictf["details"]="".join(ch for ch in i if ch.isalnum())
      education_list.append(dictf)
  return education_list,deg

def experience(text):
  experience_flist=[]
  list_time=[]
  k=""
  for i in f3(text):
    i=i.strip()
    k=k+"\n"+i
    if i.strip() == "":
      experience_flist.append(k.strip())
      k=""
  experience_flist.append(k.strip())
  for i in experience_flist:
    if i =="":
      experience_flist.remove(i)
  experience_list=[]

  for i in experience_flist:
    dictf={}
    entities_l=entities(roberta_nlp,i)
    list_label=[]
    for p in entities_l:
      if p.label_ not in list_label:
        list_label.append(p.label_)
    if "ORG" in list_label:
      for k in entities_l:
        if k.label_=="ORG":
          dictf["name"]=k.text
        elif k.label_=="DATE":
          dictf["date"]=k.text
          dictf["time_in_months"]=calculate_total_experience([k.text])
          list_time.append(k.text)
        elif k.label_=="GPE":
          dictf["place"]=k.text
      dictf["details"]=i.replace(k.text,"")
      experience_list.append(dictf)
  return experience_list,list_time

def calculate_total_experience(experience_list):
  total_experience = 0
  current_date = parser.parse(datetime.now().strftime('%Y-%m-%d'))
  for experience in experience_list:
    # Check if the experience is already in a calculated form
    match = re.match(r'(\d+)\s+(\w+)', experience)
    if match:
      # Extract the duration and unit from the experience string
      duration, unit = match.groups()
      duration = int(duration)
      # Convert the duration to months
      if unit == 'months':
        total_experience += duration*30
      if unit == 'years':
        total_experience += duration * 12*30
    else:
      # Extract the start date from the experience string
      start_date = re.match(r'(\w+ \d{4}|\w+/\d{4})', experience)
      if start_date==None:
        continue
      start_date=start_date.group(1)
      # Parse the start date
      start_date = parser.parse(start_date)
      # Use the current date as the end date if no end date is provided
      end_date = current_date if '–' not in experience or "current" in experience.lower() else None
      if end_date is None:
        # Extract the end date from the experience string
        match = re.match(r'(\w+ \d{4}|\w+/\d{4}) [-] (\w+ \d{4}|\w+/\d{4})', experience)
        if match:
          end_date = match.group(1)
          # Parse the end date
          end_date = parser.parse(end_date)
        else:
          end_date=current_date
      # Calculate the duration between the start and end dates
      duration = end_date - start_date
      total_experience += duration.days
      #print(start_date,"----",end_date)
  # Convert the total duration to months
  return total_experience // 30

def project(text):
  project_flist=[]
  k=""
  for i in f3(text):
    i=i.strip()
    k=k+"\n"+i
    if i.strip() == "":
      project_flist.append(k.strip())
      k=""
  project_flist.append(k.strip())
  for i in project_flist:
    if i =="":
      project_flist.remove(i)
  project_list=[]
  for i in project_flist:
    dictf={}
    entities_l=entities(roberta_nlp,i)
    for k in entities_l:
      if k.label_=="PRODUCT" or k.label_=="PERSON":
        dictf["name"]=k.text
      i=i.replace(k.text,"")
    dictf["details"]=text_cleaner(i)
    project_list.append(dictf)
  return project_list

def master(text):
  start_time = time.perf_counter()
  resume={}
  resume["name"]=extract_name(text)
  resume["email"]=extract_email(text)
  resume["phone number"]=extract_phone_number(text)
  resume["links"]=extract_website_links(text)
  resume["linkedin"]=extract_linkedin(resume["links"])
  head="about"
  data[head]=" "

  for i in f3(text):
    if i.strip().lower() in headings:
      head=i.lower().strip()
      data[head]=" "
      
    else:
      data[head]= data[head]+ "\n"+ i
  if "education" in data.keys():
    ed_list,deg=education(data["education"])
    resume["education"]=ed_list
    resume["degrees"]=deg
  if "experience" in data.keys():
    exp_list,list_time=experience(data["experience"])
    resume["experience"]=exp_list
    resume["total_experience_in_months"]=calculate_total_experience(list_time)
  resume["tags"],resume["skills"]=extract_skills(roberta_nlp,text)
  resume["about"]=text_cleaner(data["about"])
  if "projects" in data.keys():
    resume["projects"]=project(data["projects"])
  end_time = time.perf_counter()
  elapsed_time = end_time - start_time
  return resume,elapsed_time

def determine_file_type(file_name):
  # Get the file extension
  _, file_extension = os.path.splitext(file_name)
  file_extension = file_extension.lower()
  return file_extension if file_extension in [".pdf",".docx",".doc"] else None


def generate_html(resume_data,elapsed_time):
  html = '''
  <html>
    <head>
      <title>Resume</title>
      <style>
      body {
      font-family: Arial, sans-serif;
      margin: 0;
      padding: 0;
      border: 8px solid #333;
      }

.header {
  background-color: #333;
  color: white;
  padding: 15px;
  text-align: center;
}

.header-time {
  font-size: 12px;
  float: right;
}


h1 {
  font-size: 36px;
  margin: 10px 0;
}

h2 {
  font-size: 24px;
  color: #333;
  text-transform: uppercase;
  letter-spacing: 2px;
}

p {
  margin: 0;
  padding: 0;
  font-size: 16px;
}

b {
  font-weight: bold;
}

a {
  text-decoration: none;
  color: #006699;
}

a:hover {
  text-decoration: underline;
}

.tag-list {
  margin: 10px 0;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
}

.tag {
  display: inline-block;
  margin: 0 10px 10px 0;
  padding: 5px 10px;
  background-color: #333;
  color: black;
  border-radius: 5px;
  font-size: 14px;
  border: 1px solid #333;
  text-align: center;
  transition: transform 0.2s, background-color 0.2s, border-color 0.2s, box-shadow 0.2s;
}

.tag:hover {
  transform: scale(1.1);
  background-color: #444;
  border-color: #444;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  cursor: pointer;
}

.skill-tag {
  display: inline-block;
  margin: 0 10px 10px 0;
  padding: 5px 10px;
  background-color: #333;
  color: white;
  border-radius: 5px;
  font-size: 14px;
  border: 1px solid #333;
  text-align: center;
  transition: transform 0.2s, background-color 0.2s, border-color 0.2s, box-shadow 0.2s;
}

.skill-tag:hover {
  transform: scale(1.1);
  background-color: #444;
  border-color: #444;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  cursor: pointer;
}
  


ul {
  list-style: none;
  margin: 0;
  padding: 0;
}

li {
  margin: 10px 0;
  font-size: 16px;
}

.resume {
  max-width: 800px;
  margin: auto;
  padding: 20px;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.resume h1,
.resume h2,
.resume h3,
.resume h4,
.resume h5,
.resume h6 {
  margin-top: 0;
}

.resume h2 {
  font-size: 22px;
  margin-bottom: 10px;
}

.resume p,
.resume li {
  font-size: 16px;
  line-height: 1.5;
}

.resume .section {
  margin-bottom: 20px;
}

.resume .section-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 10px;
}

.resume .section-subtitle {
  font-size: 16px;
  font-style: italic;
  margin-bottom: 10px;
}
</style>
'''
  html+="""
  <script>
  function clearVariables(){
    address = "";
    results = "";
    html = "";
  }
  </script>
  """
  html+=f"""

    </head>
    <body>
      <div class="header">
      <a href="/" onClick='clearVariables()'>Restart</a>
        <span class="header-time">{resume_data["name"]}'s resume processed in {elapsed_time:.2f}s without multiprocessing</span>
      </div>
      <h1>Resume</h1>
      <h2>Contact Information</h2>
      <p><b>Name:</b> {resume_data["name"]}</p>
      <p><b>Email:</b> {resume_data["email"]}</p>
      <p><b>Phone:</b> {resume_data["phone number"]}</p>
      <p><b>LinkedIn:</b> <a href='{resume_data["linkedin"]}' class='skill-tag'>{resume_data["linkedin"]}</a></p>
      <h2>Links</h2>
      <div class="tag-list">
  """
  for link in resume_data['links']:
    html += f"<a href='{link}' class='skill-tag'>{link}</a>"

  if "education" in resume_data.keys():
    html += """
      </div>
      <h2>Education</h2>
      <ul>
  """
    for school in resume_data['education']:
      for i in school.keys():
        if school[i]!= None:
          html += f"<p><b>{i.capitalize()}:</b> {school[i]}</p>"
      html +="<li>\n</li>"
  html += """
      </ul>
      <h2>Degrees</h2>
      <ul>
  """
  colors = ["#0000ff","#ff00ff","#ff0000", "#ffff00", "#00ffff",  "#00ff00"]
  color_index = 0
  html+= '''   
        <div class="tag-list">
        '''
  for degree in resume_data['degrees']:
    html += f"<span class='tag tag' style='background-color: {colors[color_index]}'>{degree.upper()}</span>"
    color_index = (color_index + 1) % len(colors)
  html +="<li>\n</li>"
  html += """
      </div>
      </ul>
      <h2>Work Experience</h2>
      <ul>
  """
  html +="<li>\n</li>"
  if "experience" in resume_data.keys():
    for job in resume_data['experience']:
      html += f"<p><b>{job['name']}:</b> {job['details']}</p>"
      if 'place' in job:
        html += f"<p><b>Location: </b>{job['place']}</p>"
      if 'date' in job:
        html += f"<p><b>Date:</b> {job['date']}</p>"
      html+="<p>\n</p>"
    html += f"""
        </ul>
        <p><b>Total Experience:</b> {resume_data["total_experience_in_months"]} months</p>
    """
  else:
    html+=f"<li>No Job Experience</li>"
  html +="<li>\n</li>"
  html+='''
  <h2>Skills</h2>
  '''
  colors = ["#ff0000", "#00ff00", "#0000ff", "#ffff00", "#00ffff", "#ff00ff"]
  color_index = 0
  html+= '''   
        <div class="tag-list">
        '''
  for skill in resume_data['skills']:
    html += f"<span class='tag tag' style='background-color: {colors[color_index]}'>{skill}</span>"
    color_index = (color_index + 1) % len(colors)
  html += f"""
      </div>
      <h2>About</h2>
      <p>{resume_data["about"]}</p>
      """

  if "projects" in resume_data.keys():
    html+="""
      <h2>Projects</h2>
      <ul>
  """
    i=0
    for project in resume_data['projects']:
      i=i+1
      if "name" in project.keys():
        html += f"<li><b>{project['name']}:</b> {project['details']}</li>"
      else:
        if project['details']!="":
          html += f"<li><b>Project{i}: </b>{project['details']}</li>"
        else:
          i=i-1
  html += """
        </ul>
        <h2>Tags</h2>
        <div class="tag-list">
    """
  color_index1 = 0
  for tag in resume_data['tags']:
    html += f"<span class='tag tag' style='background-color: {colors[color_index1]}'>{tag}</span>"
    color_index1 = (color_index1 + 1) % len(colors)
  html += """
      </div>
    </body>
  </html>
  """
  return html
