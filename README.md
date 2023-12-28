# paper.py
A command-line-based [arXiv.org](https://arxiv.org/) article browser and batch downloader.
```sh
$ paper.py --publish-years 2015-2019 'ti:"attention is all you need"' | fold -w 80
1
-
ID: 1706.03762v7
Authors: ['Ashish Vaswani', 'Noam Shazeer', 'Niki Parmar', 'Jakob Uszkoreit', 'L
lion Jones', 'Aidan N. Gomez', 'Lukasz Kaiser', 'Illia Polosukhin']
Title: Attention Is All You Need
Published: Mon Jun 12 2017 05:57:34PM UTC
Updated: Wed Aug 02 2023 12:41:18AM UTC
Output file name: 2017-Ashish_Vaswani-Noam_Shazeer-Niki_Parmar-Jakob_Uszkoreit-L
lion_Jones-Aidan_N_Gomez-Lukasz_Kaiser-Illia_Polosukhin-Attention_Is_All_You_Nee
d-1706.03762v7.pdf
PDF links:
['http://arxiv.org/pdf/1706.03762v7']
Other links:
['http://arxiv.org/abs/1706.03762v7']

2
-
ID: 1910.14537v3
Authors: ['Sufeng Duan', 'Hai Zhao']
Title: Attention Is All You Need for Chinese Word Segmentation
Published: Thu Oct 31 2019 03:32:19PM UTC
Updated: Tue Oct 06 2020 06:38:42AM UTC
Output file name: 2019-Sufeng_Duan-Hai_Zhao-Attention_Is_All_You_Need_for_Chines
e_Word_Segmentation-1910.14537v3.pdf
PDF links:
['http://arxiv.org/pdf/1910.14537v3']
Other links:
['http://arxiv.org/abs/1910.14537v3']

3
-
ID: 1906.02792v1
Authors: ['Manjot Bilkhu', 'Siyang Wang', 'Tushar Dobhal']
Title: Attention is all you need for Videos: Self-attention based Video
  Summarization using Universal Transformers
Published: Thu Jun 06 2019 07:59:56PM UTC
Updated: Thu Jun 06 2019 07:59:56PM UTC
Output file name: 2019-Manjot_Bilkhu-Siyang_Wang-Tushar_Dobhal-Attention_is_all_
you_need_for_Videos_Self_attention_based_Video_Summarization_using_Universal_Tra
nsformers-1906.02792v1.pdf
PDF links:
['http://arxiv.org/pdf/1906.02792v1']
Other links:
['http://arxiv.org/abs/1906.02792v1']

$ paper.py --download --download-selection 1 \
> --publish-years 2015-2019 'ti:"attention is all you need"' >/dev/null
$ ls | fold -w 80
2017-Ashish_Vaswani-Noam_Shazeer-Niki_Parmar-Jakob_Uszkoreit-Llion_Jones-Aidan_N
_Gomez-Lukasz_Kaiser-Illia_Polosukhin-Attention_Is_All_You_Need-1706.03762v7.pdf
```

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
Run `paper.py -h` to get a list of fine-tuning options, usage examples, and relevant sources for [arXiv.org](https://arxiv.org/) search query construction.

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
