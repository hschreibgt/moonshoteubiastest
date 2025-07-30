import json
import os
import sys
# To run, use python cookbookstandardize.py /path/to/cookbook.json
def get_recipe_path(parent_dir, recipe_name):
    return os.path.join(parent_dir, "recipes", f"{recipe_name}.json")

def get_dataset_path(parent_dir, dataset_name):
    return os.path.join(parent_dir, "datasets", f"{dataset_name}.json")

def shorten_examples(examples, max_prompts):
    n = len(examples)
    if n > max_prompts:
        step = n / max_prompts
        selected_indices = [int(i * step) for i in range(max_prompts)]
        return [examples[i] for i in selected_indices]
    return examples

def process_recipe(parent_dir, recipe_name, max_prompts):
    recipe_path = get_recipe_path(parent_dir, recipe_name)
    if not os.path.exists(recipe_path):
        print(f"  Recipe {recipe_name}: File not found! ({recipe_path})")
        return None, None
    with open(recipe_path, 'r', encoding='utf-8') as f:
        recipe = json.load(f)
    datasets = recipe.get("datasets", [])
    total_prompts = 0
    dataset_examples = {}
    dataset_counts = {}
    for ds in datasets:
        ds_path = get_dataset_path(parent_dir, ds)
        if not os.path.exists(ds_path):
            print(f"    Dataset {ds}: File not found! ({ds_path})")
            continue
        with open(ds_path, 'r', encoding='utf-8') as f:
            ds_json = json.load(f)
        examples = ds_json.get("examples", [])
        dataset_examples[ds] = examples
        dataset_counts[ds] = len(examples)
        total_prompts += len(examples)
    if total_prompts <= max_prompts:
        print(f"    Recipe {recipe_name} has {total_prompts} prompts (<= {max_prompts}), not shortened.")
        return recipe, recipe_name
    # Proportional split
    shares = {}
    running_total = 0
    for i, ds in enumerate(datasets):
        if i == len(datasets) - 1:
            # Last dataset gets the remainder
            share = max_prompts - running_total
        else:
            share = round((dataset_counts[ds] / total_prompts) * max_prompts)
            running_total += share
        shares[ds] = min(share, dataset_counts[ds])
    shortened_dataset_names = []
    for ds in datasets:
        examples = dataset_examples[ds]
        num_to_keep = shares[ds]
        shortened = shorten_examples(examples, num_to_keep)
        ds_short_name = f"{ds}-shortened-{max_prompts}"
        ds_short_path = get_dataset_path(parent_dir, ds_short_name)
        ds_path = get_dataset_path(parent_dir, ds)
        with open(ds_path, 'r', encoding='utf-8') as f:
            ds_json = json.load(f)
        ds_json["examples"] = shortened
        ds_json["name"] = f"{ds_json.get('name', '')} Shortened {max_prompts}"
        ds_json["description"] = f"{ds_json.get('description', '')} Shortened {max_prompts}"
        with open(ds_short_path, 'w', encoding='utf-8') as f:
            json.dump(ds_json, f, indent=2)
        shortened_dataset_names.append(ds_short_name)
        print(f"    Shortened dataset saved: {ds_short_path} ({len(shortened)} examples)")
    # Create shortened recipe
    shortened_recipe = dict(recipe)
    shortened_recipe["name"] = f"{recipe.get('name', '')} Shortened {max_prompts}"
    shortened_recipe["description"] = f"{recipe.get('description', '')} Shortened {max_prompts}"
    shortened_recipe["datasets"] = shortened_dataset_names
    base_name = os.path.splitext(os.path.basename(recipe_path))[0]
    output_recipe_path = os.path.join(os.path.dirname(recipe_path), f"{base_name}-shortened-{max_prompts}.json")
    with open(output_recipe_path, 'w', encoding='utf-8') as f:
        json.dump(shortened_recipe, f, indent=2)
    print(f"  Shortened recipe saved: {output_recipe_path}")
    return shortened_recipe, f"{base_name}-shortened-{max_prompts}"

def main(cookbook_path):
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(cookbook_path)))
    with open(cookbook_path, 'r', encoding='utf-8') as f:
        cookbook = json.load(f)
    recipes = cookbook.get("recipes", [])
    print("Recipe list (with prompt counts):")
    for r in recipes:
        recipe_path = get_recipe_path(parent_dir, r)
        if not os.path.exists(recipe_path):
            print(f"  {r}: File not found! ({recipe_path})")
            continue
        with open(recipe_path, 'r', encoding='utf-8') as f:
            recipe = json.load(f)
        datasets = recipe.get("datasets", [])
        total_prompts = 0
        for ds in datasets:
            ds_path = get_dataset_path(parent_dir, ds)
            if not os.path.exists(ds_path):
                continue
            with open(ds_path, 'r', encoding='utf-8') as f:
                ds_json = json.load(f)
            examples = ds_json.get("examples", [])
            total_prompts += len(examples)
        print(f"  {r}: {total_prompts} prompts")
    try:
        max_prompts = int(input("Enter the max number of prompts per recipe: "))
        if max_prompts < 1:
            print("Max prompts must be >= 1.")
            return
    except ValueError:
        print("Invalid input. Please enter an integer.")
        return
    shortened_recipe_names = []
    for r in recipes:
        shortened_recipe, shortened_name = process_recipe(parent_dir, r, max_prompts)
        if shortened_name:
            shortened_recipe_names.append(shortened_name)
    # Create shortened cookbook
    shortened_cookbook = dict(cookbook)
    shortened_cookbook["name"] = f"{cookbook.get('name', '')} Shortened {max_prompts}"
    shortened_cookbook["description"] = f"{cookbook.get('description', '')} Shortened {max_prompts}"
    shortened_cookbook["recipes"] = shortened_recipe_names
    base_name = os.path.splitext(os.path.basename(cookbook_path))[0]
    output_cookbook_path = os.path.join(os.path.dirname(cookbook_path), f"{base_name}-shortened-{max_prompts}.json")
    with open(output_cookbook_path, 'w', encoding='utf-8') as f:
        json.dump(shortened_cookbook, f, indent=2)
    print(f"Shortened cookbook saved: {output_cookbook_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python cookbookstandardize.py <path_to_cookbook_json>")
    else:
        main(sys.argv[1])
