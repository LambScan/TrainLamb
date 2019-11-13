import os
import json

__dataset_conf_file__ = "dataset/dataset.json"
__users_data__ = "dataset/datausers.json"

if __name__ == "__main__":
    # Initialice the dataset with all the files
    dataset = {}
    for root, dirs, files in os.walk(os.getcwd()):
        for f in files:
            if ".png" in f:
                if str(f[0:-15]) not in dataset:
                    dataset[str(f[0:-15])] = {"label": None}
                root = root.replace(str(os.getcwd()), "")
                if "color" in root:
                    dataset[str(f[0:-15])
                            ]["path_color"] = str(os.path.join(root, f))
                elif "depth" in root:
                    dataset[str(f[0:-15])
                            ]["path_depth"] = str(os.path.join(root, f))

    # Save the indexation of the dataset in a configuration file
    print(json.dumps(dataset, sort_keys=True, indent=4))
    with open(__dataset_conf_file__, "w") as f:
        json.dump(dataset, f)
    #Initialice the users_data file
    with open(__users_data__, "w") as f:
        json.dump({}, f)
