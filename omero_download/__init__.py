import argparse
import logging
import os

from omero.cli import cli_login
from omero.gateway import BlitzGateway
from omero.plugins.download import DownloadControl

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s][%(levelname)s] %(message)s"
)

__version__ = "0.1.0"


def download_images(conn, images, output_dir, ignore_hierarchy=False):
    dc = DownloadControl()
    filesets = set()
    for idx, image in enumerate(images):
        # check if image has files accesible
        fileset = image.getFileset()
        logging.info(f"[{idx+1}/{len(images)}] Image:{image.id} {image.getName()}")
        if fileset is None:
            logging.error(f"Image:{image.id} doesn't have files")
            continue
        if fileset.id in filesets:
            logging.info(
                f"Skip Image:{image.id} - Fileset:{fileset.id} already downloaded."
            )
            continue

        # build output path
        target_dir = output_dir
        if not ignore_hierarchy:
            hierarchy1 = image.getDetails().getGroup().getName()  # group
            hierarchy2 = image.getParent().getParent().getName()  # project
            hierarchy3 = image.getParent().getName()  # dataset
            target_dir = os.path.join(output_dir, hierarchy1, hierarchy2, hierarchy3)
            os.makedirs(target_dir, exist_ok=True)

        filesets.add(fileset.id)
        dc.download_fileset(conn, fileset, target_dir)


def collect_project_images(conn, projects_ids):
    logging.info(f"Collecting projects {projects_ids}")
    images = []
    for project_id in projects_ids:
        project = conn.getObject("Project", project_id)
        if project is None:
            logging.warning(f"Project:{project_id} not found")
            continue
        for dataset in project.listChildren():
            for image in dataset.listChildren():
                images.append(image)
    return images


def collect_dataset_images(conn, dataset_ids):
    logging.info(f"Collecting datasets {dataset_ids}")
    images = []
    for dataset_id in dataset_ids:
        dataset = conn.getObject("Dataset", dataset_id)
        if dataset is None:
            logging.warning(f"Dataset:{dataset_id} not found")
            continue
        for image in dataset.listChildren():
            images.append(image)
    return images


def collect_images(conn, image_ids):
    logging.info(f"Collecting images {image_ids}")
    images = []
    for image_id in image_ids:
        image = conn.getObject("Image", image_id)
        if image is None:
            logging.warning(f"Image:{image_id} not found")
            continue
        images.append(image)
    return images


def main(cli, args):
    output_dir = os.path.realpath(args.output_dir)
    logging.info(f"Output directory: '{output_dir}'")
    conn = BlitzGateway(client_obj=cli._client)
    conn.SERVICE_OPTS.setOmeroGroup(-1)

    images = []
    # if user specified projects
    images.extend(collect_project_images(conn, args.projects))
    # if user specified datasets
    images.extend(collect_dataset_images(conn, args.datasets))
    # if user specified images
    images.extend(collect_images(conn, args.images))

    logging.info(f"{len(images)} total images found")
    logging.info(f"Downloading images...")
    download_images(conn, images, output_dir, args.ignore_hierarchy)


def command_line_entrypoint():
    parser = argparse.ArgumentParser(prog="OMERO image downloader")
    parser.add_argument(
        "--projects",
        help="List of space-separated Project IDs. Default=[].",
        nargs="+",
        default=[],
    )
    parser.add_argument(
        "--datasets",
        help="List of space-separated Dataset IDs. Default=[].",
        nargs="+",
        default=[],
    )
    parser.add_argument(
        "--images",
        help="List of space-separated Image IDs. Default=[]",
        nargs="+",
        default=[],
    )
    parser.add_argument(
        "--output_dir",
        help=f"Directory to download data. Defaults to current directory.",
        default=".",
    )
    parser.add_argument(
        "--ignore_hierarchy",
        help="Don't create Group/Project/Dataset folders for downloaded images.",
        action="store_true",
        default=False,
    )

    try:
        args = parser.parse_args()
    except:
        parser.print_help()
        exit(1)

    if not any([args.projects, args.datasets, args.images]):
        parser.print_help()
        logging.error(
            "Must provide at least one of: --projects, --datasets or --images"
        )
        exit(1)

    logging.info("Fetching OMERO server details...")
    import json
    import urllib.request

    with urllib.request.urlopen(
        "https://omeroplus.sanger.ac.uk/api/v0/servers/"
    ) as url:
        server_data = json.load(url)
        server_data = server_data["data"][0]
    logging.info(f"Using {server_data['host']}")

    with cli_login("-s", server_data["host"], "-p", str(server_data["port"])) as cli:
        main(cli, args)
