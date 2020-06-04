# tracking-racist-covid19-rhetoric

## Introduction
This repository is the work of the [CRANE team](https://devpost.com/software/crane-dvkeuf) for the [Resiliency Challenge](https://theresiliencychallenge.devpost.com/?ref_content=default&ref_feature=challenge&ref_medium=discover), on **real-time monitoring of racist rhetoric linked to the Covid19 pandemic**.

The project was proposed by Gianluca Stringhini, Boston University, following his [work on early emergence of online sinophobic behaviour during the Covid19 (SARS-Cov-2) pandemic](https://arxiv.org/pdf/2004.04046.pdf).

Using live Twitter data and historical Twitter data, filtered for sinophobic hate speech, we are looking for quantitative and qualitative trends in the vocabulary or stereotypes contained in sinophobic hate speech tweets.

We do not claim to conduct a full research project, but we aim to provide preliminary analyses that could be reused in research projects, and present our findings on a website to raise awareness. Our results could be useful both short-term, for anti-racist associations trying to debunk new stereotypes, and long-term, to expand on thesauruses used by hate speech detection algorithms.

:information_source: Information framed by :information_source: are specific to our CRANE setup for the Resiliency Challenge and are not relevant to other people that might want to use our project. :information_source:

## Architecture
Architecture of the current branch:
* **hatebaseAccess** Scripts and hard-coded datasets to compile a list of racist slurs from papers, hatebase.org and Wikipedia
* **src** :information_source: Main directory for the preprocessing and analysis :information_source:
  * **results** :information_source: Main directory for the results of analysis scripts :information_source:
    * **classification** :information_source: Results of the classification pipeline :information_source:
    * **slurFreq** :information_source: Results of the pipeline to compute the frequency of known slurs :information_source:
    * **topicModelling** :information_source: Results of the LDA topic modelling pipeline :information_source:
    * **wordEmbedding** :information_source: Results of the word2vec pipeline :information_source:
* **word2vec** [Submodule](https://github.com/tmikolov/word2vec)
**.envTemplate** Template for `.env`, see Setup->Environment
**Pipfile** `pipenv` environment description
**README.md** The current file, presentation and usage of the repository

All scripts are documented following the [reStructuredText syntax](https://docutils.sourceforge.io/rst.html).

## Setup
### Clone
Clone the repository on your system:
- Using HTTPS ` git clone https://github.com/IanSaucy/CoBRa.git`
- Using SSH (recommended) `git clone git@github.com:IanSaucy/CoBRa.git`
- Using a desktop client like [Github Desktop](https://desktop.github.com)

If you are unfamiliar with git version-controlling, many [resources](https://try.github.io) are available to learn basic commands. Desktop clients let you perform most frequent actions using a visual interface but it is safer to understand the main underlying principles before contributing to a repository.

This repo includes a submodule: the word2vec repository. It needs to be initialised by running `git submodule init` followed by `git submodule update` from the root of the CoBRa folder. If word2vec is updated (unlikely considering how long it has been since the last commit), you will need to [update the submodule](https://chrisjean.com/git-submodules-adding-using-removing-and-updating/).

### Environment
The project uses a [pipenv environment](https://realpython.com/pipenv-guide/) for dependency management and requires Python 3.6+.

If you don't have `pipenv`, install it using `pip install pipenv` (or `pip3 install pipenv` depending on your system). You might need to [install pip](https://packaging.python.org) if you've never used it before.

In the repo root directory:
- Before anything else, run `pipenv install --dev` to download all dependencies requires for development work. You should only need to do this once.
- If you ever add a package to **Pipfile**, run `pipenv update`
- Before running any python script, run `pipenv shell` to enter the virtual shell. In this shell, you can use python as you normally would -- except in this case it's a virtual environment. Check out [this link](https://realpython.com/pipenv-guide/) for an intro on how to use `pipenv`.

#### .env and environment variables
`pipenv` provides a file to store environment variables: `.env`. This file is not included in the repository because it contains private information such as API keys. **Never share your API keys in a public space.**

Create a `.env` by running `cp .envTemplate .env` in the repo root directory. It will be automatically ignored by git.

Fill in the values of the variables in .env using your preferred text editor. *Note: As their name begins with a dot, the .env and .envTemplate files are hidden by default.*

Currently, `.env` holds the following variables:
- HATEBASE_KEY= *Your API key for hatebase.org. Can be left blank if you do not wish to update the slurs list.*
- PERSPECTIVE_KEY= *Your API key for Google Perspective API. Can be left blank if you do not wish to run the classification pipeline. See [Perspective support](https://support.perspectiveapi.com/s/article/Generating-an-API-key) for instruction to create your API key.*
- PERSPECTIVE_QPS= *Your Query-Per-Second limit for Perspective. Unless you send a request for more, this should be 1*
- SLURS_LIST_PATH= *Path to the JSON-encoded file holding the slurs for the classification pipeline.*
- DATASET_PATH= *Path to the folder containing the raw dataset. For information on the expected format of this dataset, see the Data section below*
- INTERMEDIATE_PATH= *Path to the folder containing the prepared dataset.*
- RESULTS_PATH= *Path to the folder containing the result folders for the various analysis pipelines.*
**Path variables should use the repo root directory as their root. The paths can point to folders outside the repo.**

Let us say it again: **Never share your API keys in a public space.**

### A note on tmux
Depending on the size of the dataset, many scripts in this repo take several hours, even several days, to run. As such, we recommend the use of `tmux` because it lets you *detach* from a terminal session.
Let's imagine you are running a script on a server you are connected to via `ssh` and your internet connection dies. With a naive setup, your script will fail and might become a zombie. With tmux you will be able to disconnect safely and come back to your running script later.
And it's [not even that difficult to learn](https://www.hamvocke.com/blog/a-quick-and-easy-guide-to-tmux/), promise!

## Data
All the analysis scripts take files with one-JSON encoded tweet per line. They iterate over all files in the INTERMEDIATE_PATH folder.
The following fields must be present in the description of each tweet: `created_at`, `id`, `text`.

`src/prepareDataset.py` can populate INTERMEDIATE_PATH from a raw dataset.
The raw dataset needs to be in the following format: a `tar.gz` archive in DATASET_PATH, with files containing one JSON-encoded tweet per line. Others files can be present in the archive, but the data files to read must be identified by a common string in their name, passed to `src/prepareDataset.py`.
The following fields must be present in the description of each tweet: `created_at`, `id`, `text`.
`src/prepareDataset.py` filters the dataset to select only English original tweets (removing retweets and tweets beginning by “RT”) and drop all unused fields from the tweet description.

If you have several `tar.gz` archives to prepare, it can be a good idea to use a [Bash loop](https://www.cyberciti.biz/faq/bash-loop-over-file/).

:information_source:
For the Resiliency Challenge, we are working on streaming data collected by Gianluca Stringhini. The marker for the data files in the archives is "Spritzer". The data in INTERMEDIATE_PATH contains only English original tweets.
:information_source:

### I don't have my own dataset, where can I find one?
Sharing of tweets datasets is restricted by [Twitter Developer Terms](https://developer.twitter.com/en/developer-terms/policy). You will not be able to find publicly available datasets with tweets content, but rather datasets of tweet ids. Those can by *hydrated*, using for example [Hydrator](https://github.com/DocNow/hydrator).

From there it really depends on your research topic and questions.
Some are very time-sensitive, some are less. If yours are not very time-sensitive, try your luck with a regular search engine.
Some require a *naive* dataset, representative of the full information flow of Twitter. In this case, your best bet is to collaborate with a research team doing frequent analyses on Twitter content. They probably keep a stream running to collect 1% of the daily Twitter data.
Others require a dataset that has already been filtered for specific keywords or users. If that's your case, try your luck with a regular search engine.
If you don't need historical data, you could also start your own Twitter stream to collect exactly the data you desire.

## Preprocessing
The preprocessing function is located in `src/preprocessingTools.py`. It is called directly by the analysis pipelines with the most suitable arguments.

Our preprocessing was adapted from [Effrosynidis et al. (2017)](https://github.com/Deffro/text-preprocessing-techniques#0-remove-unicode-strings-and-noise).
It deals with unicode, URLs, mentions, hashtags, punctuation, contractions, numbers and newlines. We have added variants as options for URLs, mentions, hashtags, punctuation and numbers. In particular, the preprocessing function can segment hashtags and replace numbers by their text version.

## Analysis

*A note on the selection of slurs: The "Frequency of known slurs" and the "Classification of anti-black and anti-asian hate speech" pipelines require list of slurs. The selection of those slurs is not trivial. For example, when including slurs that have been reclaimed by their original targets, like the "n-word", one should be aware that they might introduce a [racist bias in their analysis](https://arxiv.org/abs/1905.12516).*

### Frequency of known slurs
This pipeline performs a simple quantitative analysis over the dataset. Given a list of slurs (with variants), it computes the daily and weekly frequency of these slurs in the dataset.

It iterates over the files in INTERMEDIATE_PATH and saves its results to `RESULTS_PATH/slurFreq` in two different formats: an ubiquitous CSV file and the JSON-encoded file formatted for the [nivo](https://nivo.rocks/line/) library.

### Classification of anti-black and anti-asian hate speech
This pipeline performs a [classification](https://en.wikipedia.org/wiki/Statistical_classification) task to detect anti-asian hate speech tweets (`src/classifier.py`), then computes the daily frequency of the thus classified tweets in the dataset (`src/statsForClassifier.py`).

:warning: :warning: :warning: **The accuracy of this classifier has not been tested yet, we are working on obtaining a test set.**

It iterates over the files in INTERMEDIATE_PATH and saves its results to `RESULTS_PATH/classification` in two different formats: an ubiquitous CSV file and the JSON-encoded file formatted for the [nivo](https://nivo.rocks/line/) library.
Intermediates CSV files with the results of the classifier are always saved to `RESULTS_PATH/classification`.

The classifier (`src/classifier.py`) relies on a two-steps approach: it flags tweets containing slurs against different ethnicities then evaluate the toxicity of those tweets using [Google Perspective API](https://support.perspectiveapi.com)

The list of slurs to detect was compiled from a survey of hate-speech detection papers, hatebase.org and Wikipedia slurs list (:information_source: see Trello for details :information_source:). For each ethnicity, the first detected slur is saved. Tweets with a detected slur for at least one ethnicity are flagged and passed to the scoring step, as well as saved to a CSV file.
**For now only anti-black and anti-asian slurs are saved and flagged for the scoring step.**

The text of the flagged tweets is sent to [Google Perspective API](https://support.perspectiveapi.com) for scoring. Default score type is SEVERE_TOXICITY, but it can be replaced by TOXICITY. By default, tweets scoring at or higher than 0.6 will be classified as hate speech. This threshold can be replaced if a visual inspection of the results show it to be necessary.
:warning:*Known performance issue: to go over 10 QPS a multithread implementation would be required.*

Daily frequencies of hate-speech tweets are then computed (`src/statsForClassifier.py`) and saved to `RESULTS_PATH/classification` in two different formats: an ubiquitous CSV file and the JSON-encoded file formatted for the [nivo](https://nivo.rocks/line/) library.
:warning:*Known performance issue: to compute frequencies the script has to compute the daily counts of the entire dataset. This needs to be moved to the dataset preparation step.*

:information_source: Not used for the website :information_source:

### Word embeddings
The word embedding analysis pipeline is based on [Gianluca Stringhini’s paper](https://arxiv.org/pdf/2004.04046.pdf), it makes use of the [word2vec package](https://github.com/tmikolov/word2vec) which is a submodule of our repo.

An additional preprocessing step is required to transform the content of INTERMEDIATE_PATH into something that `word2vec` can process.
prepareForWord2Vec.py iterates over the files in INTERMEDIATE_PATH, preprocesses the text and split it according to its date. Two period modes are available: periods defined by their length (in days) and the beginning date of the first period; or periods defined by calendar month+year.

The main script, to train the model, is `word2vec`. Don’t forget to run `make` in the `word2vec` directory to be able to run the executable the first time. The hyperparameters were chosen with the advice in the (very short) package doc.
Run from the repo root directory: `word2vec/word2vec -train <inputFile> -output <outputFile> -window 10 -hs 1 -cbow 0 -min-count 20 -threads 6 -binary 1`
This gives a binary-encoded file where each line is a word followed by the distance value to each other word (= a matrix).

This result can then be interpreted by running `word2vec/distance <file>`. The terminal will prompt you to enter a word and output the 40 words closest to the given word as well as the cosine distance. The bigger the cosine value, the more similar the words are. It works on a loop that allows you to input words until you enter the `EXIT` keyword.
To save the results from the `distance` script into a file for easier post-analysis, run instead `word2vec/distance <inputFile> >> <outputFile>`. **In this case, the prompt will not appear so you will have to enter the words, one per line, without being asked to, finishing by the `EXIT` keyword.**

:information_source: Our current keyword list is: [virus, corona, coronavirus, covid, kungflu, kung, wuflu, infection, infecting, disease, bat, bats, pangolin, pangolins, quarantine, china, chinese, asian, asia, chingchong, wuhan, chink, chinaman, jap, slant, immigration, immigrant, immigrants, country, disgusting, alien] :information_source:

Depending on your research question, these results can be used and interpreted in different ways, for example [detecting new words](https://arxiv.org/pdf/2004.04046.pdf) or [tracking trends in topics](https://docs.google.com/spreadsheets/d/1O0N9Yho32oa_P1cCEj89LR0dU2EBi6I39Y9MzPzGcVc/edit?usp=sharing).

### Topic modelling with LDA
This pipeline performs a rather standard [Latent Dirichlet Allocation](https://en.wikipedia.org/wiki/Latent_Dirichlet_allocation) analysis for [topic modelling](https://en.wikipedia.org/wiki/Topic_model), using [gensim's implementation](https://radimrehurek.com/gensim/auto_examples/tutorials/run_lda.html).

To allow for multithreading, it is used as a module: e.g. `python -m genericDatasetAnalysis.topicModelling 1 empty output.txt`.

For now this pipeline remains highly specific to our Resiliency Challenge use-case: it is able to run either on the results of the classifier pipeline or on the full dataset filtered for Covid19-related tweets.

The dataset is split into two periods around 1st Feb 2020 (*this will soon become an argument*) and the corpora are prepared by preprocessing the text (using hashtag segmentation), [tokenising](https://en.wikipedia.org/wiki/Lexical_analysis#Tokenization), removing tokens of less than 3 characters, [lemmatising](https://en.wikipedia.org/wiki/Lemmatisation) with a [POS-tag](https://en.wikipedia.org/wiki/Part-of-speech_tagging) filter (keeping only nouns or nouns and adjectives), removing [stop words](https://en.wikipedia.org/wiki/Stop_words), adding bigrams and trigrams, and turning the tokens into a [bag-of-words](https://en.wikipedia.org/wiki/Bag-of-words_model).

A specificity of unsupervised topic modelling is that the number of topics to be generated by the model needs to be provided by the user. Here, we try to detect 3, 6 and 9 topics (*this will soon become an argument*). The multiple models are trained in parallel.

:warning:It appears that standard LDA under-performs on short texts like tweets, as evidenced by the omnipresence of `beer` in our results for Covid19-related tweets. This pipeline will be reworked with known adaptations of LDA for Twitter analysis.

:information_source: Not used for the website :information_source:
