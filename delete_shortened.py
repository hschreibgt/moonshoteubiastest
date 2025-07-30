import os
import json
# Tu use, run python delete_shortened.py path/to/moonshot-data name-of-original-cookbook     
def delete_files_for_cookbook(base_dir, cookbook_name):
    # Delete the shortened cookbook file
    cookbooks_dir = os.path.join(base_dir, "cookbooks")
    for fname in os.listdir(cookbooks_dir):
        if fname.startswith(cookbook_name) and "shortened" in fname:
            path = os.path.join(cookbooks_dir, fname)
            os.remove(path)
            print(f"Deleted cookbook: {path}")
    # Find shortened recipes from the cookbook
    cookbook_path = os.path.join(cookbooks_dir, f"{cookbook_name}.json")
    shortened_recipe_names = []
    if os.path.exists(cookbook_path):
        with open(cookbook_path, "r", encoding="utf-8") as f:
            cookbook = json.load(f)
        for r in cookbook.get("recipes", []):
            shortened_recipe_names.append(r)
    # Delete shortened recipes
    recipes_dir = os.path.join(base_dir, "recipes")
    for fname in os.listdir(recipes_dir):
        for r in shortened_recipe_names:
            if fname.startswith(r) and "shortened" in fname:
                path = os.path.join(recipes_dir, fname)
                os.remove(path)
                print(f"Deleted recipe: {path}")
    # Delete shortened datasets
    datasets_dir = os.path.join(base_dir, "datasets")
    for fname in os.listdir(datasets_dir):
        if "shortened" in fname:
            path = os.path.join(datasets_dir, fname)
            os.remove(path)
            print(f"Deleted dataset: {path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python delete_shortened.py <base_dir> <cookbook_name>")
    else:
        delete_files_for_cookbook(sys.argv[1], sys.argv[2])
