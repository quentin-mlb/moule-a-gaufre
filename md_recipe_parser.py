import json
import re

def markdown_recipe_to_json(markdown_file_path, json_file_path):
    """
    Convertit un fichier Markdown contenant une recette en un fichier JSON respectant le schéma Recipe de schema.org.

    Args:
        markdown_file_path (str): Chemin vers le fichier Markdown contenant la recette.
        json_file_path (str): Chemin vers le fichier JSON de sortie.
    """
    with open(markdown_file_path, 'r', encoding='utf-8') as file:
        markdown_content = file.read()

    # Initialiser le dictionnaire pour stocker les informations de la recette
    recipe_info = {
        "@context": "https://schema.org/",
        "@type": "Recipe",
        "name": "",
        "author": {
            "@type": "Person",
            "name": ""
        },
        "recipeCategory": [],
        "recipeCuisine": "",
        "recipeYield": "",
        "prepTime": "",
        "cookTime": "",
        "totalTime": "",
        "recipeIngredient": [],
        "recipeInstructions": [],
        "suitableForDiet": [],
        "recipeNote": []
    }

    # Extraire les métadonnées du début du fichier
    metadata_section = re.search(r'---(.*?)---', markdown_content, re.DOTALL)
    if metadata_section:
        metadata = metadata_section.group(1)
        tags_match = re.search(r'tags:\s*(.*?)(?:temps de préparation|$)', metadata, re.DOTALL)
        if tags_match:
            tags = tags_match.group(1).strip().split('\n')
            for tag in tags:
                if tag.strip().startswith('- '):
                    recipe_info["suitableForDiet"].append(tag.strip())

        prep_time_match = re.search(r'temps de préparation:\s*(\d+)', metadata)
        if prep_time_match:
            prep_time = prep_time_match.group(1)
            recipe_info["prepTime"] = f"PT{prep_time}M"

        cook_time_match = re.search(r'temps de cuisson:\s*(\d+)', metadata)
        if cook_time_match:
            cook_time = cook_time_match.group(1)
            recipe_info["cookTime"] = f"PT{cook_time}M"
            recipe_info["totalTime"] = f"PT{int(prep_time) + int(cook_time)}M"

        source_match = re.search(r'source:\s*(.+)', metadata)
        if source_match:
            recipe_info["author"]["name"] = source_match.group(1).strip()

        quantity_match = re.search(r'quantité:\s*(.+)', metadata)
        if quantity_match:
            recipe_info["recipeYield"] = quantity_match.group(1).strip()

    # Extraire le nom de la recette
    name_match = re.search(r'#\s*(.+)', markdown_content)
    if name_match:
        recipe_info["name"] = name_match.group(1).strip()

    # Extraire les ingrédients
    ingredients_section = re.search(r'## Ingrédients(.*?)(?:##|$)', markdown_content, re.DOTALL)
    if ingredients_section:
        ingredients = ingredients_section.group(1).strip().split('\n')
        for ingredient in ingredients:
            if ingredient.strip().startswith('- '):
                recipe_info["recipeIngredient"].append(re.sub(r'^-\s+', '', ingredient.strip()))

    # Extraire les instructions par sections (niveau 3) ou en une seule section si pas de niveau 3
    instructions_sections = re.findall(r'### (.*?)\n(.*?)(?=###|##|$)', markdown_content, re.DOTALL)
    if instructions_sections:
        for section_title, section_content in instructions_sections:
            section = {
                "@type": "HowToSection",
                "name": section_title.strip(),
                "itemListElement": []
            }
            steps = section_content.strip().split('\n')
            for step in steps:
                if step.strip() and step.strip()[0].isdigit():
                    step_text = step.strip()
                    section["itemListElement"].append({
                        "@type": "HowToStep",
                        "name": step_text,
                        "text": step_text
                    })
            recipe_info["recipeInstructions"].append(section)
    else:
        # Cas où il n'y a pas de sections de niveau 3
        instructions_section = re.search(r'## Préparation(.*?)(?:##|$)', markdown_content, re.DOTALL)
        if instructions_section:
            section = {
                "@type": "HowToSection",
                "name": "Préparation",
                "itemListElement": []
            }
            steps = instructions_section.group(1).strip().split('\n')
            for step in steps:
                if step.strip() and step.strip()[0].isdigit():
                    #step_text = step.strip()
                    step_text = re.sub(r'^\d\.\s+', '', step.strip())
                    section["itemListElement"].append({
                        "@type": "HowToStep",
                        "name": step_text,
                        "text": step_text
                    })
            recipe_info["recipeInstructions"].append(section)

    # Extraire les notes
    notes_section = re.search(r'## Notes(.*?)$', markdown_content, re.DOTALL)
    if notes_section:
        notes = notes_section.group(1).strip().split('\n')
        for note in notes:
            if note.strip().startswith('- '):
                recipe_info["recipeNote"].append(note.strip())

    # Sauvegarder les informations dans un fichier JSON
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(recipe_info, json_file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    markdown_recipe_to_json('./examples/Cake au citron.md', './examples/Cake au citron.json')

