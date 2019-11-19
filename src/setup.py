import os
import json
from FileManager import parent_folder, write_dataset, DATASET

if __name__ == "__main__":
    # Initialice the dataset with all the files
    dataset = {}
    for root, dirs, files in os.walk(os.path.join(parent_folder, "dataset", "savings")):
        for f in files:
            if ".png" in f:
                if str(f[0:-15]) not in dataset:
                    dataset[str(f[0:-15])] = {"label": None}
                root = root.replace(str(parent_folder), "")

                if "depth" in root:
                    dataset[str(f[0:-15])]["path_depth"] = str(os.path.join(root, f))
                    dataset[str(f[0:-15])]["path_color"] = str(os.path.join(root, f)).replace("depth", "color")

    # Save the indexation of the dataset in a configuration file
    print(json.dumps(dataset, sort_keys=True, indent=4))
    write_dataset(DATASET.ORIGINAL, dataset)
    write_dataset(DATASET.WORKING, dataset)
    write_dataset(DATASET.LABELED, {})
    write_dataset(DATASET.USERS, {})
