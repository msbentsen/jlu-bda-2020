import subprocess


def pull_data(source_path, dest_path, csv_path, *args):
    # install tools needed for processing
    rc = subprocess.call("./scripts/tools.sh")
    if rc != 0:
        print("error installing tools")
    # Download data
    rc = subprocess.call("./scripts/download.r")
    if rc != 0:
        print("error")
    # validate and convert files as needed
    rc = subprocess.call("./scripts/convert.sh")
    if rc != 0:
        print("error converting files")
    # Sort files into folderstructure
    rc = subprocess.call(
        ["./scripts/sort.sh", source_path, dest_path, csv_path])
    if rc != 0:
