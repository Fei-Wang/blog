import argparse
from pathlib import Path

import yaml
from bs4 import BeautifulSoup


def process_front_matter(front_matter_path, html_dir):
    with front_matter_path.open("r", encoding="utf-8") as file:
        yaml_content = yaml.safe_load(file)

        title = yaml_content["title"]
        date = yaml_content["date"]

        date_part = date.split(" ")[0]
        title_slug = title.lower().replace(" ", "-")

        file_name = f"{date_part}-{title_slug}.html"

        yaml_content["media_subpath"] = str(html_dir)  # media_subpath

        yaml_content = yaml.dump(yaml_content, allow_unicode=True)
        return file_name, yaml_content


def move_id_to_header(soup):
    for section in soup.find_all("section", id=True):
        section_id = section["id"]
        section["id"] = None

        header = section.find(["h2", "h3", "h4"])
        if header:
            header["id"] = section_id


def del_header(soup):
    for h1 in soup.find_all("h1"):
        h1.decompose()


def save_html(output_path, front_matter, body_content):
    with output_path.open("w", encoding="utf-8") as file:
        out = "---\n" + front_matter + "---\n\n" + body_content
        file.write(out)


def process_html(args):
    sub_dir, latex_dir, html_dir = Path(args.dir), Path(args.latex_dir), Path(args.html_dir)
    html_dir = html_dir / sub_dir
    latex_dir = latex_dir / sub_dir
    html_path = html_dir / "main.html"
    front_matter_path = latex_dir / "front_matter.yml"

    html_name, front_matter = process_front_matter(front_matter_path, html_dir)
    output_path = html_dir / html_name

    with html_path.open("r", encoding="utf-8") as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, "html.parser")
    move_id_to_header(soup)  # section id -> header id
    del_header(soup)  # delete h1
    body_content = soup.body.prettify(formatter="html5")  # type: ignore

    save_html(output_path, front_matter, body_content)


def main():
    parser = argparse.ArgumentParser(description="Process HTML file and modify img sources.")
    parser.add_argument("dir", type=str, help="changed dir.")
    parser.add_argument("-i", "--latex-dir", type=str, default="posts/latex", help="latex dir.")
    parser.add_argument("-o", "--html-dir", type=str, default="_posts", help="html dir.")
    args = parser.parse_args()
    process_html(args)


if __name__ == "__main__":
    main()
