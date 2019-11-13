import os
import json
parent_folder = os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

__dataset_conf_file__ = os.path.join(parent_folder, "dataset", "dataset.json")
__users_data__ = os.path.join(parent_folder, "dataset", "datausers.json")

if __name__ == "__main__":
    # Initialice the dataset with all the files
    dataset = {}
    for root, dirs, files in os.walk(os.path.join(parent_folder, "dataset", "savings")):
        for f in files:
            if ".png" in f:
                if str(f[0:-15]) not in dataset:
                    dataset[str(f[0:-15])] = {"label": None}
                root = root.replace(str(parent_folder), "")
                if "color" in root:
                    dataset[str(f[0:-15])
                            ]["path_color"] = str(os.path.join(root, f))
                elif "depth" in root:
                    dataset[str(f[0:-15])
                            ]["path_depth"] = str(os.path.join(root, f))

    # Save the indexation of the dataset in a configuration file
    print(json.dumps(dataset, sort_keys=True, indent=4))
    with open(__dataset_conf_file__, "w") as f:
        f.write(json.dumps(dataset, sort_keys=True, indent=4))
        # json.dump(dataset, f)
    #Initialice the users_data file
    with open(__users_data__, "w") as f:
        json.dump({}, f)
