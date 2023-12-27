# paper.py
An arXiv.org article batch downloader.

## Setup
1. [Install Python3](https://www.python.org/downloads/) (tested using `v3.11.2`).
2. Clone this repository.
3. Copy the file `paper.py` to some directory that is in the `PATH` environment variable
   of your Operating system.
4. Optional: add the following convenience functions and aliases to the configuration of your POSIX-shell-compatible OS shell:
   ```sh
   arxivh()
   {
       cat <<EOF
   arxivall <query> [option...]
   arxivtitle <query> [option...]
   arxivauthor <query> [option...]
   arxivabstract <query> [option...]
   arxivcomment <query> [option...]
   arxivjournalreference <query> [option...]
   arxivsubjectcategory <query> [option...]
   arxivreportnumber <query> [option...]
   arxivid <query> [option...]
   
   For arxivXYZ, the <query> parameter specifies a query of type XYZ.
   
   [option...] is a list of options to be passed to paper.py.
   
   The query for arxivauthor should be an author name in the following form:
   <lowercase-last-name>_<first-name-initial>_<optional-middle-name-initial>
   The query for author "Art I. Ficial" should be "ficial_a_i".
   
   If the last name comprises of multiple words, then they must be separated by underscores.
   For example, the query for "Fictional Del Maestro" should be "del_maestro_f".
   EOF
   }
   _arxiv_parent()
   {
       ARXIV_QUERY_TYPE="$1"
       ARXIV_QUERY="$2"
       shift 2
   
       paper.py "$@" "${ARXIV_QUERY_TYPE}:${ARXIV_QUERY}"
   }
   alias arxivall='_arxiv_parent all'
   alias arxivtitle='_arxiv_parent ti'
   alias arxivauthor='_arxiv_parent au'
   alias arxivabstract='_arxiv_parent abs'
   alias arxivcomment='_arxiv_parent co'
   alias arxivjournalreference='_arxiv_parent jr'
   alias arxivsubjectcategory='_arxiv_parent cat'
   alias arxivreportnumber='_arxiv_parent rn'
   # alias arxivid='_arxiv_parent id'
   arxivid()
   {
       paper.py --id-list "$@"
   }
   ```

## Help
Run `paper.py -h` to get a list of fine-tuning options, usage examples, and relevant sources for arXiv.org search query construction.

## Basic usage examples
Search for articles by author `Art I. Ficial`:
```sh
$ paper.py "au:ficial_a_i"
```

The list looks good? Download the articles (pdf):
```sh
$ paper.py -d "au:ficial_a_i"
```

Look up articles by their arXiv ids...
```sh
$ paper.py -i 2309.06314,1811.02452
```

... and download them:
```sh
$ paper.py -d -i 2309.06314,1811.02452
```

Search for articles by title:
```sh
$ paper.py "ti:quantum"
```

Combine them:
```sh
$ paper.py "au:ficial_a_i AND ti:quantum"
$ paper.py "au:ficial_a_i AND (ti:quantum OR ti:subconvexity)"
$ paper.py "au:ficial_a_i ANDNOT (ti:quantum OR ti:subconvexity)"
$ paper.py -i 2309.06314,1811.02452 'au:ficial_a_i AND ti:"quantum unique ergodicity"'
```

## Acknowledgment
Inspired by GNU Emacs-based ideas of [@ultronozm](https://github.com/ultronozm).
