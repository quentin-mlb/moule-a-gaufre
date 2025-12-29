# to do:
# homogeneize the libraries API

from md_recipe_parser import markdown_recipe_to_json
from generate_html import generate_html
from generate_pdf import generate_pdf
import os
import shutil

working_dir = './tmp/'
input_dir = './examples/'

templates_dir = "./src/templates/fiche/"
template_name = "index.html.jinja"

# ensure working_dir exists and is empty
if os.path.exists(working_dir):
    shutil.rmtree(working_dir)
os.makedirs(working_dir, exist_ok=True)

md_file = "Cake au citron.md"
file_name = md_file.split('.')[0]

 
markdown_recipe_to_json(input_dir+md_file,working_dir+file_name+'.json')
html = generate_html(templates_dir + template_name, working_dir + file_name + '.json')
output_path = os.path.join(working_dir, f"{file_name}.html")
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html)
generate_pdf(working_dir+file_name+".html", css=templates_dir+"classicA5.css", out=working_dir+file_name+'.pdf')