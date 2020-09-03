# Crisis Racism and Narrative Evaluation

Project **CRANE** (Crisis Racism and Narrative Evaluation) aims to **support researchers and anti-racist organisations** that wish to use **state-of-the-art text analysis algorithms** to study how specific **events impact online hate speech and racist narratives**. CRANE Toolbox is a **Python package**: once installed, the tools in CRANE are available as functions that users can use in their Python programs or directly through their terminal. CRANE targets users with basic programming but **no machine learning skills**.

[Skip to Quick-start](###Quick-start)

![CRANE thumbnail](https://github.com/CRANE-toolbox/analysis-pipelines/blob/master/thumbnail.jpg?raw=true)

## Table of Contents

<!-- TOC depthFrom:2 depthTo:4 withLinks:1 updateOnSave:1 orderedList:0 -->

- [Table of Contents](#table-of-contents)
- [Introduction](#introduction)
	- [Genesis](#genesis)
	- [Project motivation](#project-motivation)
	- [CRANE Toolbox: The Python package for data analysis](#crane-toolbox-the-python-package-for-data-analysis)
- [Quick-start](#quick-start)
- [Package documentation](#package-documentation)
	- [How to install and use CRANE Toolbox](#how-to-install-and-use-crane-toolbox)
		- [Requirements](#requirements)
		- [Install CRANE Toolbox](#install-crane-toolbox)
		- [Command-line mode](#command-line-mode)
		- [Function-call mode](#function-call-mode)
	- [Modules](#modules)
		- [Import module](#import-module)
		- [Preprocessing module](#preprocessing-module)
		- [Analysis module](#analysis-module)
		- [Visualisation module](#visualisation-module)
- [Contributing](#contributing)
	- [Join the team](#join-the-team)
- [Frequently asked questions](#frequently-asked-questions)
	- [On the CRANE project](#on-the-crane-project)
	- [On using CRANE Toolbox](#on-using-crane-toolbox)

<!-- /TOC -->

## Introduction

### Genesis

**Crisis Racism and Narrative Evaluation**, or **CRANE** for short, was born during the [Resiliency Challenge](https://theresiliencychallenge.devpost.com/?ref_content=default&ref_feature=challenge&ref_medium=discover), a COVID19-driven hackathon. During nine weeks, an interdisciplinary team composed of students and professional designers, programmers and computer science researchers developed a [prototype website](https://crane-toolbox.github.io/#/) for **real-time monitoring of racist rhetoric linked to the Covid19 pandemic**. The project was proposed by Gianluca Stringhini, Boston University, following his [work on early emergence of online sinophobic behaviour during the Covid19 (SARS-Cov-2) pandemic](https://arxiv.org/pdf/2004.04046.pdf). Readers may find more details on the approach taken for the Resiliency Challenge on the [corresponding Devpost page](https://devpost.com/software/crane-dvkeuf) and the [resiliency-challenge-legacy branch](https://github.com/CRANE-toolbox/analysis-pipelines/tree/resiliency_challenge-legacy) of this repository.

### Project motivation

While doing literature review we noticed that few papers on online hate speech monitoring had both a sociology research approach and recent natural language processing tools. The literature seems to be divided mainly into methodological papers aiming to develop new machine learning tools to detect and characterise racism, and traditional sociology research approaches, both qualitative and quantitative, that do not take full advantage of the available data and analysis methods.

We are aware that this is due in part to the difficulty of gathering interdisciplinary teams from very different fields, and in part to the rather young and precarious nature of automated hate speech detection.

Our experiences during the hackathon lead us to believe that these issues could be somewhat alleviated by providing social sciences researchers with user-friendly tools leveraging the more robust of the current hate speech detection and analysis methods.

### CRANE Toolbox: The Python package for data analysis

CRANE Toolbox is designed to **support researchers and anti-racist organisations** in studying **how specific events impact online hate speech and racist narratives**. State-of-the-art text analysis algorithms evolve quickly and their spread is often limited to the dedicated field of computer science research. CRANE Toolbox wraps some of those methods, that fit typical social sciences questions, into **user-friendly tools that require no machine learning skills**.

:warning:In this first version, CRANE Toolbox will remain **specific to tweet analysis**.


CRANE Toolbox is a **Python package**. Once [installed](#install-crane-toolbox), users can [call its functions in their Python scripts](#function-call-mode) or use the tools it provides [directly through their terminal](#command-line-mode). Those tools are organised in several sub-packages called modules. Each module corresponds to a step in the general analysis pipeline.

 The first version of CRANE Toolbox provides tools and documentation for users to filter and format the data they have extracted from Twitter (*import* module), prepare it for analysis (*preprocessing* module), carry out the analysis(es) of their choice (*analysis module*), and get a basic graphic representation of the results (*visualisation* module).


:warning: As a Python package, CRANE Toolbox **does not provide the data to analyse**. It also does **not substitute for a research framework** in which its tools should be used.  The documentation contains advice on parameter choices and results interpretation, but they remain the responsibility of the user.


## Quick-start

:information_source: This section is for experienced programmers who want to dive head-first into the deep end. If you have no idea what we are talking about in there, please don't run away screaming!
Though the length of the [Package Documentation section](##Package-documentation) might make it a bit daunting, we wrote it with non-specialists in mind, so you should find all the instructions and advice you need to use the CRANE Toolbox.

### Install

```bash
pip install cranetoolbox
```

### Transform Data
The first step is to transform your data into our common data exchange format, a three column CSV file.
We use the `crane-import` module to perform this step. It takes source files that contain a single JSON tweet object per line and transforms them into a lightweight CSV file. The available parameters are detailed in the [Import Module](#import-module) section.

```bash
crane-import --source-folder ./my_source --output-folder ./my_output
```

### Preprocess Data
It is important to clean-up text data before data analysis. We provide a CLI tool to perform this step, with several preprocessing options. The available parameters are detailed in the [Preprocessing Module](#preprocessing-module) section.

```bash
crane-preprocess ./my_output ./my_preproc_output
```

### Run analysis

We currently provide a single statistical analysis tool that performs basic frequency analysis on the data set using a provided set of keywords. The required input formats and available parameters are detailed in the [Analysis Module](#analysis-module) section.

```bash
crane-analysis-quanti ./my_preproc_output keywords.json quanti_results.csv
```


## Package documentation

This section is divided into two parts: a first one describing how to install CRANE Toolbox and run its tools, either in command-line mode in a terminal or through function calls in Python scripts; and a second one giving details on each module, in particular data format and parameter choice.

Advanced users can find additional information on the content of each module in the [code documentation](https://crane-toolbox.github.io/analysis-pipelines/).

### How to install and use CRANE Toolbox

#### Requirements

In order to successfully install CRANE Toolbox, you will need:
- A basic internet connection
- A terminal
- Python 3
- pip for Python 3

Some **basic knowledge in programming and command-lines is strongly recommanded**, but the brave and the studious may choose to proceed without.

If the above list is clear for you, skip to the [installation instructions](#install-crane-toolbox). Else, read the following paragraphs to get your environment ready.

:warning:If you choose not to follow the recommanded installation process, you will probably need to install additional packages or software.

##### What is a terminal and where do I find one?

The terminal is an interface in which you can type and execute text based commands. You may find a more detailed explanation [here](https://www.quora.com/In-coding-terms-what-is-a-terminal-and-what-is-it-used-for) and pictures of what a terminal looks like [here](https://vgkits.org/blog/what-is-a-terminal/).

A terminal is already installed on your computer. If you are using a Unix-based operating system (either **MacOSX or a Linux distribution**), it is aptly named **Terminal** and lives with your other applications. If you are using a Windows operating system, it is named **Command Prompt** and can be found in your Start Menu. For Windows 8 and 10, it is located in the *Windows System* folder.

To run a command in the terminal, simply type it in and press Enter.

:warning: Copy-pasting shortcuts (Ctrl^C and Ctrl^V) are disabled by default in terminals, because Ctrl^C is used to abort programs instead. Use right-click to copy and paste.

##### How do I install Python 3?

**Python 3** is a programming language. :warning: It is very similar to Python 2 but the two are not interchangeable.

The installation process depends on your operating system. Basic instructions can be found on [the official Python website](https://wiki.python.org/moin/BeginnersGuide/Download), but you will easily find more detailed guides on the internet.

##### How do I install pip for Python 3?

**pip** is a package manager: it helps you download Python packages and update them when necessary.

Basic instructions for its installation can be found on [its official website](https://pip.pypa.io/en/stable/installing/). It is widely used so step-by-step guides and other resources are easily found on the internet.

:warning: Because of the co-existence of Python 2.7 and Python 3, pip might be installed for both languages on your computer. In that case, use the `pip3` command instead. You can check which version of `pip` is used by running `pip --version` in your terminal (`python -m pip --version` for Windows users).

#### Install CRANE Toolbox

We strongly recommend installing CRANE Toolbox using `pip`. Run `pip install cranetoolbox` in a terminal.
The command might take some time because `pip` will also automatically install all the
 Python packages required for CRANE Toolbox to run.
 You can check the list of dependencies on the [PyPi page of CRANE Toolbox](link to Pypi page).

CRANE Toolbox can also be installed manually from the source code available in this repository.

#### Command-line mode

The command line mode is the easiest method of using this package, it enables the user to quickly run all parts of the package and produce usable statistics in a very short period of time.

There are three different CLI commands available in the toolbox, they are `crane-import`, `crane-preprocess` and `crane-analysis-quanti`. In order, they handle importing/transforming raw data into a standard CSV format, preprocessing that data into a usable format and finally computing the daily frequencies of given keywords.

For specifics on the parameters provided under each CLI tool please check the detailed documentation below.

#### Function-call mode

This package has been written with reuse in mind. While the CLI tools are easier to use as standalone tools, CRANE Toolbox can be imported and used within another python project. All functions are available to the user through standard Python package usage. In addition, a single high level function corresponds to each CLI tool so users can easily call their desired pipeline directly from Python.

### Modules

#### Import module

The import module is accessible from the `crane-import` command-line entry point.

The goal of this module is to **transform raw twitter JSON data into something more manageable and lightweight** for use by the rest of the pipeline.
**This is not a required step** and could be performed manually by the user or have already been done via some other tool since data is passed between modules as files.

This module can **process a large number of large (multiple gigabyte) files** without relying heavily on swap or memory usage. This is accomplished by reading files by chunks (the user can specify the number of lines in the options) as well as writing in chunks.
This ensures that only a certain amount of data is held in memory at any given moment.

In addition, it removes extra tweet data that is not required for the analysis pipeline, reducing file size and increasing the performance of later steps in this package.

#### Expected input format
The module will attempt to read any file in the specified folder, regardless of extension, name, etc. It supports any text-based file format (.json, .csv, .txt). In addition, it can handle compressed `tar` archives and treat multiple files or folders in a given tar archive. :warning: Currently, it only supports singly compressed tar archives -- thus no `tar.gz` or similar formats are supported.

Regardless of the exact file type, data **should always be stored with one [JSON object tweet](https://developer.twitter.com/en/docs/twitter-api/v1/data-dictionary/overview/intro-to-tweet-json) per line**, using `\n` as the end-of-line character.

#### Output Format

The module will concatenate all files into a single CSV file with the following columns:

| id                 | text            | created_at         |
|--------------------|-----------------|--------------------|
| unique id of tweet | full text tweet | timestamp of tweet |

The CSV file has **no headers**, comma separators, and optional double quotes for text.

The text column is dynamically selected depending on if the tweet is over 140 characters or not, for more information about extended tweets see the [official documentation on extended tweets](https://developer.twitter.com/en/docs/twitter-api/v1/data-dictionary/overview/intro-to-tweet-json#extendedtweet)

If the output file already exists, it will append to the existing file. In the case that it does not exist it will create a new one, using the default path ("./filtered_data.csv") if none is specified.

#### CLI Commands

The import package can be used as a command-line tool and supports a several different options.

- (Required) `--source-folder` The source folder or file to scan for files/archives to process.
- (Optional) `--output-folder` The folder to save the output. The specified folder must exists. Defaults to `./`.
- (Optional) `--output-name` The name, including extension, of the output file. Defaults to `output.csv`.
- (Optional) `--tweet-language` The language of tweets saved to the file. Based on the language field in the
JSON object. Defaults to `en`.
- (Optional) `--max-lines-in-memory` The maximum number of lines that will be held in memory. This can be adjusted to
to optimize for performance or on machines that have limited memory. Defaults to `50000`.
- (Optional) `--retweets` Use this flag to _include_ retweets in the output set. Defaults to `false`

A complete example for the command-line entry-point:

```bash
crane-import --source-folder tweets/november --output-folder mydataset/data --max-lines-in-memory 2000 --output-name dataset.csv
```

#### Preprocessing module

The preprocessing pipeline is accessible from the `crane-preprocess` command-line entry point.

The proposed preprocessing is adapted from [Effrosynidis et al. (2017)](https://github.com/Deffro/text-preprocessing-techniques#0-remove-unicode-strings-and-noise), using techniques 9, 0, 1, 3, 5 and 7, and 4.

#### Expected input format

The dataset given as the first positional argument can be either a folder of CSV files or a single CSV file. Each CSV file should contain **3 columns** (ID of input, should be unique, int; Text of the tweet, string; timestamp: Timestamp string), **no headers**, comma separators, and optional double quotes for text.

| id                 | text            | created_at         |
|--------------------|-----------------|--------------------|
| unique id of tweet | full text tweet | timestamp of tweet |

#### Preprocessing steps

In order and for a given string, it will:
- Transform uppercase characters to lowercase,
- Remove unicode strings (e.g. `\u002c`),
- Replace urls with "url", or remove them if `-url` is specified,
- Replace mentions (e.g. "@BobTheSurfer") with "atUser", or remove them if `-mention` is specified,
- Remove the hash symbol in front of hashtags (e.g. "#spreadTheLove", and segment the hashtags if `-hashtag` is specified,
- Replace contractions with their full spelling (e.g. "I'm" becomes "I am"),
- Replace repeated punctuation signs with a textual equivalent (e.g. "!!!" becomes "multiExclamation") and newlines with spaces, or remove all punctuation except underscore characters if `punct` is specified,
- Replace numbers with their English text version, or remove them if `-num` is specified.

Hashtags are segmented, *i.e.* seperated into words, using the [wordsegment](`https://pypi.org/project/wordsegment/`) package. :warning: Only supported for English language. :warning::warning::warning::warning:Word segmentation runs in polynomial time and increase the preprocessing time by several orders of magnitude.

:warning: The algorithm to unpack contractions is currently rather basic. It will for example mistakenly interpret the possessive "'s" as a verb contraction.

:warning: Ordinal numbers are not yet supported.

#### Output Format

The processed dataset is saved in the folder given as the second positional argument. If it does not exist, the folder will be created. For each input file a processed file is generated. Files names are generated by appending "_preprocessed" to the name of the corresponding input file. Each CSV file contains **4 columns** (ID of input, should be unique, int; Original text of the tweet, string; **Preprocessed text of the tweet, string**; timestamp: Timestamp string), **no headers**, comma separators, and optional double quotes for text.

| id                 | original_text   | clean_text                 | created_at         |
|--------------------|-----------------|----------------------------|--------------------|
| unique id of tweet | full text tweet | preprocessed text of tweet | timestamp of tweet |

#### CLI Commands

The pipeline has two mandatory positional arguments and five optional arguments:
- (Required) Position 1. Path to the folder containing the dataset formatted with the *import* module, or a single dataset file.
- (Required) Position 2. Path to the folder to save the preprocessed dataset in. If it does not exist, the folder will be created.
- (Optional) `-url` or `--remove-url` Use this flag to remove URLs from the tweets instead of replacing them with 'url'.
- (Optional) `-mention` or `--remove-mentions` Use this flag to remove user mentions '@userHandle' from the tweets instead of replacing them with 'atUser'.
- (Optional) `-hashtag` or `--segment-hashtags` Use this flag to segment hashtags instead of simply removing the preceding '#' character.
- (Optional) `-punct` or `--remove-punctuation` Use this flag to remove all punctuation expect hyphens, instead of replacing repeated symbols and newlines.
- (Optional) `-num` or `--remove-numbers` Use this flag to remove all numbers from the tweets instead of replacing them with their text version.

A complete example for the command-line entry-point:

```bash
crane-preprocess mydataset/data mydataset/preprocessedData -punct
```

#### Analysis module
Currently the analysis module only offers some simple quantitative analysis pipeline to compute the daily frequency of given keywords.

##### Simple quantitative analysis

This analysis pipeline is accessible from the `crane-analysis-quanti` command-line entry point.

It computes the daily frequency of given keywords in a dataset. It allows for variants of keywords. For example, occurences of "boys" and "boyz" can be counted together.

#### Expected input format

The dataset given as the first positional argument can be either a folder of CSV files or a single CSV file. Each CSV file should contain **4 columns** (ID of input, should be unique, int; Original text of the tweet, string; Preprocessed text of the tweet, string; timestamp: Timestamp string), **no headers**, comma separators, and optional double quotes for text. The preprocessed text is assumed to be lower-case.

| id                 | original_text   | clean_text                 | created_at         |
|--------------------|-----------------|----------------------------|--------------------|
| unique id of tweet | full text tweet | preprocessed text of tweet | timestamp of tweet |


The keywords are defined in a JSON dictionary where the keys are the main variant for each keyword and the values are lists of variants. All keywords should be lower-case strings. For example:
```JSON
{
	"color" : [
		"colour",
		"color"
	],
	"chinese" : [
		"chinese",
		"chineze",
		"chines"
	]
}
```

#### Output format

The output is a CSV file with a *day* date column (format "%Y-%m-%d"), a *total_count* column with the daily total number of tweets in the dataset, a *[keyword]_count* column for each keyword (its main variant is used to name the column) with the daily number of tweets containing at least one variant of the keyword and a *[keyword]_freq* column for each keyword (its main variant is used to name the column) with the daily frequency of tweets containing at least one variant of the keyword.

For example, for the keywords set given above:

| day  | total_count            | color_count                                      | chinese_count | color_freq | chinese_freq |
|------|------------------------|--------------------------------------------------|---------------|------------|--------------|
| date | daily number of tweets | daily number of tweets with "color" or a variant | daily number of tweets with "chinese" or a variant | daily frequency of tweets with "color" or a variant | daily frequency of tweets with "chinese" or a variant |


#### CLI Commands

The pipeline has three mandatory positional arguments and one optional argument:
- (Required) Position 1. Path to the folder containing the dataset preprocessed with the *preprocess* module, or a single dataset file.
- (Required) Position 2. Path to the JSON file containing the keywords and their variants. See below for the expected format.
- (Required) Position 3. Path for the result file.
- (Optional) `-d` or `--date-format` String defining the format of dates in the dataset. The default is %a %b %d %H:%M:%S %z %Y".

A complete example for the command-line entry-point:

```bash
crane-analysis-quanti mydataset/preprocessedData keywords.json quanti_results.csv -d "%d %b %a %h:%M:%S %z %Y"
```

#### Visualisation module

**Not implemented yet**

## Contributing

We welcome all contributions! If you have questions, a feature request or some feedback, please use the **issues** feature of GitHub.

The [Issues page](https://github.com/CRANE-toolbox/analysis-pipelines/issues) works rather like your good old forum page, with many additional features specific to programming and git versioning. GitHub provides a [detailed guide](https://guides.github.com/features/issues/) to them, but here are the basics:
1. **Search the existing issues** for similar questions/feature requests/feedback
2. If you find an issue similar enough, you can add to its discussion with your own details
3. If you don't find an issue similar enough, create a new one
4. **Give as much relevant information as possible**. For example, if you want to report a bug or get help with an error, provide both your code/command-line and the error message. If possible, link to the data.
5. Always keep in mind that this is a volunteer project, and contributors do their best to help. **Be nice and patient**.

### Join the team

You are welcome to submit Pull Requests for open issues. In that case, please comment on the issue to notify everyone of your intention to do so to make sure no one else is working on the same problem.

If you wish to join the team, please email **ADD EMAIL** to get onboarded. We welcome developers, of course, but also designers, researchers from all academic fields, technical writers...

We have chosen to onboard people privately instead of sharing all our resources in the repo for two reasons. First, we wanted to make it easier for users not used to open source projects to find what they need. Second, some of our resources contain private information from user research.

## Frequently asked questions

### On the CRANE project

###### What is this website linked to the repo?
https://crane-toolbox.github.io/#/ is a prototype website build during the Resiliency Challenge hackathon, in an attempt to quantify and characterise the impact of the COVID19 pandemic on online sinophobic hate speech. We left it online as a very basic example of the type of data analysis that could be carried out with CRANE Toolbox.

###### Are you going to continue working on real-time analysis of COVID19-related online hate speech?
We do not plan to at the moment. Due to the composition of the team, we have decided to focus our efforts on CRANE Toolbox, where we believe we can make a difference.

###### Who is doing this?
Currently, the team is composed of two Computer Science students, two designers and a research engineer (Emma Barme, [Rachael Dier](http://rachaeldier.com/), Kelly Ly, [Svetlana Moldavskaya](https://www.behance.net/svetlanacheban), and Ian Saucy), supported by Boston University Spark! organisation and Assistant Professor Gianluca Stringhini.

The list of hackathon contributors for the first phase of the project can be found on [CRANE Devpost page](https://devpost.com/software/crane-dvkeuf).

###### Can I help?

Yes! Check out the [Contributing](##Contributing) section.

### On using CRANE Toolbox

###### What is Python? What is a Python package? What is a Python module?
Python is a very common programming language for data analysis tasks. Packages are installable add-ons to the basic Python language. Roughly speaking, a module is a file with Python code.

That said, if you are entirely unfamiliar with Python, you might want to experiment with it some before using CRANE Toolbox.

###### I have a question/a feature request/some feedback, how do I contact you?
Please use the [**Issues** page](https://github.com/CRANE-toolbox/analysis-pipelines/issues) of this repo. Check out the [Contributing](##Contributing) section for more details.

###### Can I copy your code for my project?
CRANE Toolbox is distributed under [GNU Affero General Public License v3.0](https://github.com/CRANE-toolbox/analysis-pipelines/blob/master/LICENSE).

You can use it however you want provided you respect the license requirements: include a license and copyright notice, state the changes you made, disclose your source (this repo), and distribute your code under the same license. Please note that we are not liable for whatever use you make of this code, and we provide no warranty.

###### How do I cite CRANE Toolbox in my paper?
Please link to this repo.

###### Where can I find Twitter data?
Sharing of tweets datasets is restricted by [Twitter Developer Terms](https://developer.twitter.com/en/developer-terms/policy). You will not be able to find publicly available datasets with tweets content, but rather datasets of tweet ids. Those can by *hydrated*, using for example [Hydrator](https://github.com/DocNow/hydrator).

From there it really depends on your research topic and questions.
Some are very time-sensitive, some are less. If yours are not very time-sensitive, try your luck with a regular search engine.
Some require a *naive* dataset, representative of the full information flow of Twitter. In this case, your best bet is to collaborate with a research team doing frequent analyses on Twitter content. They probably keep a stream running to collect 1% of the daily Twitter data.
Others require a dataset that has already been filtered for specific keywords or users. If that's your case, try your luck with a regular search engine.
If you don't need historical data, you could also start your own Twitter stream to collect exactly the data you desire.

###### My data is not in your specific input format, what do I do?
We are working to include several standard input format to our *import* module. If your data format is not supported, please [get in touch](##Contributing) and we will do our best to either include support for it in CRANE Toolbox or guide you to transform it into one of our supported format.

###### Method X is very useful and should be included, why is it not there?
Maybe we don't know about it, maybe we didn't have time to implement it yet, maybe we choose not to include it for a given reason. Please [get in touch](##Contributing) to tell us about it. (Unless it's a proprietary method with a use fee.)
