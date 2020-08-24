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

**ONLY IDEAS**
While doing literature review we noticed that few papers on online hate speech monitoring had both a sociology research approach and recent natural language processing tools. The literature seems to be divided mainly into methodological papers aiming to develop new machine learning tools to detect and characterise racism, and traditional (Emma's note: could that word be taken as a negative?) sociology research approaches, both qualitative and quantitative, that do not take full advantage of the available data and analysis methods.
We are aware that this is due in part to the difficulty of gathering interdisciplinary teams from very different fields, and in part to the rather young and precarious nature of automated hate speech detection. Our experiences during the hackathon lead us to believe that these issues could be somewhat bridged/alleviated by providing social sciences researchers with user-friendly tools leveraging the more robust of the current hate speech detection and analysis methods.

### CRANE Toolbox: The Python package for data analysis

CRANE Toolbox is designed to **support researchers and anti-racist organisations** in studying **how specific events impact online hate speech and racist narratives**. State-of-the-art text analysis algorithms evolve quickly and their spread is often limited to the dedicated field of computer science research. CRANE Toolbox wraps some of those methods, that fit typical social sciences questions, into **user-friendly tools that require no machine learning skills**.

:warning:In this first version, CRANE Toolbox will remain **specific to tweet analysis**.


CRANE Toolbox is a **Python package**. Once [installed](####Install-CRANE-Toolbox), users can [call its functions in their Python scripts](####Function-call-mode) or use the tools it provides [directly through their terminal](####Command-line-mode). Those tools are organised in several sub-packages called modules. Each module corresponds to a step in the general analysis pipeline.

 The first version of CRANE Toolbox provides tools and documentation for users to filter and format the data they have extracted from Twitter (*import* module), prepare it for analysis (*preprocessing* module), carry out the analysis(es) of their choice (*analysis module*), and get a basic graphic representation of the results (*visualisation* module).


:warning: As a Python package, CRANE Toolbox **does not provide the data to analyse**. It also does **not substitute for a research framework** in which its tools should be used.  The documentation contains advice on parameter choices and results interpretation, but they remain the responsibility of the user.


## Quick-start

:information_source: This section is for experienced programmers who want to dive head-first into the deep end. If you have no idea what we are talking about in there, please don't run away screaming! Though the length of the [Package Documentation section](##Package-documentation) might make it a bit daunting, we wrote it with non-specialists in mind, so you should find all the instructions and advice you need to use the CRANE Toolbox.

**TO BE FILLED WHEN THE PACKAGE DOCUMENTATION SECTION IS DONE**

## Package documentation

This section is divided into two parts: a first one describing how to install CRANE Toolbox and run its tools, either in command-line mode in a terminal or through function calls in Python scripts; and a second one giving details on each module, in particular data format and parameter choice.

Advanced users can find additional information on the content of each module in the [code documentation](link to Sphinx code doc).

### How to install and use CRANE Toolbox

#### Requirements

In order to successfully install CRANE Toolbox, you will need:
- A basic internet connection
- A terminal
- Python 3
- pip for Python 3

Some **basic knowledge in programming and command-lines is strongly recommanded**, but the brave and the studious may choose to proceed without.

If the above list is clear for you, skip to the [installation instructions](####Install-CRANE-Toolbox). Else, read the following paragraphs to get your environment ready.

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

We strongly recommand installing CRANE Toolbox using `pip`. Run `pip install cranetoolbox` in a terminal. The command might take some time because `pip` will also automatically install all the Python packages required for CRANE Toolbox to run. You can check the list of dependencies on the [PyPi page of CRANE Toolbox](link to Pypi page).

CRANE Toolbox can also be installed manually from the source code available in this repository.

#### Command-line mode

#### Function-call mode

### Modules

#### Import module

#### Preprocessing module

The preprocessing pipeline is accessible from the `crane-preprocess` command-line entry point.

The proposed preprocessing is adapted from [Effrosynidis et al. (2017)](https://github.com/Deffro/text-preprocessing-techniques#0-remove-unicode-strings-and-noise), using techniques 9, 0, 1, 3, 5 and 7, and 4.

The pipeline has two mandatory positional arguments and five optional arguments:
- Position 1: Path to the folder containing the dataset formatted with the *import* module, or a single dataset file.
- Position 2: Path to the folder to save the preprocessed dataset in. If it does not exist, the folder will be created.
- Optional, -url or --remove-url: Use this flag to remove URLs from the tweets instead of replacing them with 'url'.
- Optional, -mention or --remove-mentions: Use this flag to remove user mentions '@userHandle' from the tweets instead of replacing them with 'atUser'.
- Optional, -hashtag or --segment-hashtags: Use this flag to segment hashtags instead of simply removing the preceding '#' character. See documentation for details on the segmentation.
- Optional, -punct or --remove-punctuation: Use this flag to remove all punctuation expect hyphens, instead of replacing repeated symbols and newlines.
- Optional, -num or --remove-numbers: Use this flag to remove all numbers from the tweets instead of replacing them with their text version.

The dataset given as the first positional argument can be either a folder of CSV files or a single CSV file. Each CSV file should contain **3 columns** (ID of input, should be unique, int; Text of the tweet, string; timestamp: Timestamp string), **no headers**, comma separators, and optional double quotes for text.

In order and for a given string, it will:
- Transform uppercase characters to lowercase,
- Remove unicode strings (e.g. `\u002c`),
- Replace urls with "url", or remove them if `-url` is specified,
- Replace mentions (e.g. "@BobTheSurfer") with "atUser", or remove them if `-mention` is specified,
- Remove the hash symbol in front of hashtags (e.g. "#spreadTheLove", and segment the hashtags if `-hashtag` is specified,
- Replace contractions with their full spelling (e.g. "I'm" becomes "I am"),
- Replace repeated punctuation signs with a textual equivalent (e.g. "!!!" becomes "multiExclamation") and newlines with spaces, or remove all punctuation except underscore characters if `punct` is specified,
- Replace numbers with their text version, or remove them if `-num` is specified.

Hashtags are segmented, *i.e.* seperated into words, using the [wordsegment](`https://pypi.org/project/wordsegment/`) package. :warning::warning::warning::warning:Word segmentation runs in polynomial time and increase the preprocessing time by several orders of magnitude.

:warning: The algorithm to unpack contractions is currently rather basic. It will for example mistakenly interpret the possessive "'s" as a verb contraction.

:warning: Ordinal numbers are not yet supported.

A complete example for the command-line entry-point:

```bash
crane-preprocess mydataset/data mydataset/preprocessedData -punct
```

The processed dataset is saved in the folder given as the second positional argument. If it does not exist, the folder will be created. For each input file a processed file is generated. Files names are generated by appending "_preprocessed" to the name of the corresponding input file. Each CSV file contains **4 columns** (ID of input, should be unique, int; Original text of the tweet, string; **Preprocessed text of the tweet, string**; timestamp: Timestamp string), **no headers**, comma separators, and optional double quotes for text.

#### Analysis module
Currently the analysis module only offers some simple quantitative analysis pipeline to compute the daily frequency of given keywords.

##### Simple quantitative analysis

This analysis pipeline is accessible from the `crane-analysis-quanti` command-line entry point.

It computes the daily frequency of given keywords in a dataset. It allows for variants of keywords. For example, occurences of "boys" and "boyz" can be counted together.

The pipeline has three mandatory positional arguments and one optional argument:
- Position 1: Path to the folder containing the dataset preprocessed with the *preprocess* module, or a single dataset file.
- Position 2: Path to the JSON file containing the keywords and their variants. See below for the expected format.
- Position 3: Path for the result file.
- Optional, -d or --date-format: String defining the format of dates in the dataset. The default is %a %b %d %H:%M:%S %z %Y".

The dataset given as the first positional argument can be either a folder of CSV files or a single CSV file. Each CSV file should contain **4 columns** (ID of input, should be unique, int; Original text of the tweet, string; Preprocessed text of the tweet, string; timestamp: Timestamp string), **no headers**, comma separators, and optional double quotes for text. The preprocessed text is assumed to be lower-case.

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

A complete example for the command-line entry-point:

```bash
crane-analysis-quanti mydataset/preprocessedData keywords.json quanti_results.csv -d "%d %b %a %h:%M:%S %z %Y"
```

The output is a CSV file with a *day* date column (format "%Y-%m-%d"), a *total_count* column with the daily total number of tweets in the dataset, a *[keyword]_count* column for each keyword (its main variant is used to name the column) with the daily number of tweets containing at least one variant of the keyword and a *[keyword]_freq* column for each keyword (its main variant is used to name the column) with the daily frequency of tweets containing at least one variant of the keyword. For example, for the keywords set given above, the columns would be: day, total_count, color_count, chinese_count, color_freq, chinese_freq. Counts are given as integers and frequencies as floats.


#### Visualisation module

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
**TO BE DISCUSSED WITH SPARK!**
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
