# OMERO download

Download images from OMERO server. Can download individual images (`--images`) or full dataset (`--datasets`) or project (`--projects`) folders.

# Install

```shell
pip install git+https://github.com/cellgeni/omero-download.git
```


# Usage
Basic use:
```shell
omero-download --images 123 456 789 --output_dir /path/to/download
```

If you don't want the Group-Project-Dataset structure to be created as folders you can use the `--ignore_hierarchy` flag to flatten all the paths.

Downloading dataset  or project folders:
```shell
omero-download --projects 6969 --output_dir /path/to/download
omero-download --datasets 7337 8008 --output_dir /path/to/download
```