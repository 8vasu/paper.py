#!/usr/bin/python3

# paper.py - A command-line-based arXiv.org article browser and batch downloader.
# Copyright (C) 2023 Soumendra Ganguly

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys
import argparse
import urllib.request
from urllib.parse import quote as urlquote
import xml.etree.ElementTree as ET
import re
import traceback
from os import remove
from datetime import datetime

USAGE_EXAMPLES = f"""
Reference on the arXiv API query interface:
https://info.arxiv.org/help/api/user-manual.html#31-calling-the-api

Reference on constructing search queries:
https://info.arxiv.org/help/api/user-manual.html#51-details-of-query-construction

All of the information in the above two links apply except that spaces,
parentheses, and double quotes do not need to be quoted/escaped; the
program will do that for you.

Usage examples with a focus on the "search_query" parameter:
------------------------------------------------------------
Search for articles by author "Art I. Ficial":
{sys.argv[0]} "au:ficial_a_i"

The list looks good? Download the articles (pdf):
{sys.argv[0]} -d "au:ficial_a_i"

Look up articles by their arXiv ids...
{sys.argv[0]} -i 2309.06314,1811.02452

... and download them:
{sys.argv[0]} -d -i 2309.06314,1811.02452

Search for articles by title:
{sys.argv[0]} "ti:quantum"

Combine them:
{sys.argv[0]} "au:ficial_a_i AND ti:quantum"
{sys.argv[0]} "au:ficial_a_i AND (ti:quantum OR ti:subconvexity)"
{sys.argv[0]} "au:ficial_a_i ANDNOT (ti:quantum OR ti:subconvexity)"
{sys.argv[0]} -i 2309.06314,1811.02452 'au:ficial_a_i AND ti:"quantum unique ergodicity"'
"""

URL_PREFIX = "http://export.arxiv.org/api/query?"

DOWNLOAD_FAIL_MESSAGE = """
failed to download file; it is possible that the article was withdrawn
"""

YES = ["", "y", "yes"]
NO = ["n", "no"]

NONPDF = "downloaded file {0} is not a pdf; remove file? (y/n): "

def nonnegative_int(val):
    """Only nonnegative integers are valid."""
    try:
        val = int(val)
    except ValueError:
        raise argparse.ArgumentTypeError(f'"{val}" is not an integer')

    if val < 0:
        raise argparse.ArgumentTypeError(f'"{val}" is not >= 0')

    return val

def in_range(num, range_str):
    """Check if num is in range_str, which is a string
    of comma (,) separated terms of the form "k" or of
    the form "n-m", where k,n,m are positive integers
    with n < m."""
    range_list = range_str.split(",")
    for r in range_list:
        if "-" in r:
            start, end = r.split("-")
            if num >= int(start) and num <= int(end):
                return True
        elif num == int(r):
            return True
    return False

def slugify(s):
    """Convert string to a slug."""
    return re.sub("[^0-9a-zA-Z_]+", "_", s)

def validate_pdf(file_path, keep_non_pdf, remove_non_pdf):
    """Check if downloaded file is actually a pdf and act."""
    if keep_non_pdf:
        return

    # check if downloaded file is actually pdf
    with open(file_path, "rb") as dl_file:
        # is a pdf
        if dl_file.read(4) == b"%PDF":
            return

    # automatically remove
    if remove_non_pdf:
        remove(file_path)
        return

    # prompt user
    ok = False
    while not ok:
        prompt = NONPDF.format(file_path)
        choice = input(prompt).lower()

        if choice in YES:
            remove(file_path)
            ok = True
        elif choice in NO:
            ok = True
        else:
            print("valid choices are 'y' and 'n'",
                  file=sys.stderr)

        print("")

class CombinedFormatter(argparse.ArgumentDefaultsHelpFormatter,
                        argparse.RawDescriptionHelpFormatter):
    pass

parser = argparse.ArgumentParser(epilog=USAGE_EXAMPLES,
                                 formatter_class=CombinedFormatter)
parser.add_argument("-i", "--id-list",
                    help="""this is the value of the "id_list"
parameter of the "query" method of the arXiv API query interface""",
                    default="")
parser.add_argument("-S", "--start",
                    help="""this is the value of the "start"
parameter of the "query" method of the arXiv API query interface""",
                    type=nonnegative_int, default=0)
parser.add_argument("-m", "--max-results",
                    help="""this is the value of the "max_results"
parameter of the "query" method of the arXiv API query interface""",
                    type=nonnegative_int, default=50)
parser.add_argument("-b", "--sort-by",
                    help="""this is the value of the "sortBy"
parameter of the "query" method of the arXiv API query interface""",
                    choices=["relevance",
                             "lastUpdatedDate",
                             "submittedDate"],
                    default="lastUpdatedDate")
parser.add_argument("-O", "--sort-order",
                    help="""this is the value of the "sortOrder"
parameter of the "query" method of the arXiv API query interface""",
                    choices=["ascending", "descending"],
                    default="descending")
parser.add_argument("-y", "--publish-years",
                    help="""a string of comma (,) separated terms of the form
"k" or of the form "n-m", where k,n,m are positive
integers with n < m; these terms specify the
acceptable ranges of article publish years; in absence
of this option, all years qualify
""",
                    default=None)
parser.add_argument("-Y", "--update-years",
                    help="""a string of comma (,) separated terms of the form
"k" or of the form "n-m", where k,n,m are positive
integers with n < m; these terms specify the
acceptable ranges of article update years; in absence
of this option, all years qualify
""",
                    default=None)
parser.add_argument("-d", "--download",
                    help="download the pdf files",
                    const=True, default=False,
                    action="store_const")
parser.add_argument("-o", "--output-filename-template",
                    help="""template string to be used for naming downloaded
pdf files: optionally containing {id}, {auth},
{title}, {pub}, {updt} as placeholders for
arXiv ID, author names, title, publish year,
and update year respectively""",
                    type=str, default="{pub}-{auth}-{title}-{id}")
parser.add_argument("-D", "--output-dir",
                    help="""download the files to this directory""",
                    type=str, default=".")
parser.add_argument("-s", "--download-selection",
                    help="""a string of comma (,) separated terms of the form
"k" or of the form "n-m", where k,n,m are positive
integers with n < m; the article entries in the output
of this program are indexed (numbered) and these terms
specify the ranges of indices to be downloaded; all
entries are considered for download if this option is
not specified
""",
                    default=None)
group = parser.add_mutually_exclusive_group()
# --remove-non-pdf and --keep-non-pdf are mutually exclusive
group.add_argument("-r", "--remove-non-pdf",
                    help="""if a downloaded file is not a pdf (for example if
the article was withdrawn and a placeholder html
message mentioning the absence of the pdf is
retrieved in place of the pdf), then automatically
remove that file; the --keep-non-pdf switch does the
opposite of this; default behavior (absence of both
--remove-non-pdf and --keep-non-pdf) is to prompt the
user for deletion of each non-pdf file downloaded""",
                    const=True, default=False,
                    action="store_const")
group.add_argument("-k", "--keep-non-pdf",
                    help="""opposite of --remove-non-pdf;
keep all non-pdf files downloaded and do not prompt the
user for deletion of such files""",
                    const=True, default=False,
                    action="store_const")
parser.add_argument("search_query",
                    help="""this is the value of the "search_query"
parameter of the "query" method of the arXiv API query interface""",
                    nargs="?", default="")
args = parser.parse_args()

quoted_query = urlquote(args.search_query)
url = (f"{URL_PREFIX}search_query={quoted_query}"
       f"&id_list={args.id_list}"
       f"&start={args.start}"
       f"&max_results={args.max_results}"
       f"&sortBy={args.sort_by}"
       f"&sortOrder={args.sort_order}")

with urllib.request.urlopen(url) as u:
    r = u.read()

root = ET.fromstring(r.decode("utf-8"))
entry_list = []
for child in root:
    if "entry" in child.tag:
        entry_list.append(child)

entry_index = 0
in_format = "%Y-%m-%dT%H:%M:%S%z"
out_format = "%a %b %d %Y %I:%M:%S%p %Z"
for entry in entry_list:
    link_elements = []
    authors = []
    for child in entry:
        if "id" in child.tag:
            id_ = child.text.split("/")[-1]
        elif "title" in child.tag:
            title = child.text
        elif "link" in child.tag:
            link_elements.append(child)
        elif "author" in child.tag:
            for gchild in child:
                if "name" in gchild.tag:
                    authors.append(gchild.text)
        elif "published" in child.tag:
            publish_time = datetime.strptime(child.text,
                                             in_format).strftime(out_format)
            publish_year = datetime.strptime(child.text,
                                             in_format).strftime("%Y")
        elif "updated" in child.tag:
            update_time = datetime.strptime(child.text,
                                            in_format).strftime(out_format)
            update_year = datetime.strptime(child.text,
                                            in_format).strftime("%Y")

    if (args.publish_years and
        not in_range(int(publish_year), args.publish_years)):
        continue
    if (args.update_years and
        not in_range(int(update_year), args.update_years)):
        continue

    entry_index += 1
    numbering = str(entry_index)
    print(numbering)
    print("-"*len(numbering))

    slugified_title = slugify(title)
    slugified_authors = "-".join([slugify(name) for name in authors])
    slug = args.output_filename_template.format(id=id_,
                                                auth=slugified_authors,
                                                title=slugified_title,
                                                pub=publish_year,
                                                updt=update_year)

    print(f"""ID: {id_}
Authors: {authors}
Title: {title}
Published: {publish_time}
Updated: {update_time}
Output file name: {slug}.pdf""")

    pdf_links = []
    other_links = []
    for link_elt in link_elements:
        if link_elt.get("href"):
            if link_elt.get("title") == "pdf" or \
               link_elt.get("type") == "application/pdf":
                pdf_links.append(link_elt.get("href"))
            else:
                other_links.append(link_elt.get("href"))

    # print all links, not just pdfs
    print(f"""PDF links:
{pdf_links}
Other links:
{other_links}
""")

    if (args.download and
        (not args.download_selection or
         in_range(entry_index, args.download_selection))):

        # add numerical suffix to filename if there are multiple pdfs
        # associated with the same entry
        excess_index = 1

        for link in pdf_links:
            try:
                if excess_index > 1:
                    local_file_path = (f"{args.output_dir}/"
                                       f"{slug}--{excess_index}.pdf")
                else:
                    local_file_path = f"{args.output_dir}/{slug}.pdf"
                urllib.request.urlretrieve(link, local_file_path)
            except urllib.error.HTTPError:
                traceback.print_exc(file=sys.stderr)
                print(DOWNLOAD_FAIL_MESSAGE, file=sys.stderr)
            else:
                validate_pdf(local_file_path,
                             args.keep_non_pdf,
                             args.remove_non_pdf)

            excess_index += 1
