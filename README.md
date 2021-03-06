# ytviewcount

## What it does

Counts views of videos on YouTube.
It reads a list of YouTube URLs from a file, logs the title and views for each video in a CSV file, and adds a total of all views.

**Note:** Running this script does *not* increase the view count of the videos.

## Why?

I use this to keep track of the views of the videos from our TEDxStuttgart events. Hence the `--tedx` and `--tedxstuttgart` options explained below.

This started its life as a Bash script. As YouTube kept changing the page format, it became increasingly harder to parse it with \*nix command line tools, so I eventually rewrote it in Python. These days, a YouTube page is mostly JavaScript, and what you see in your browser has been generated on the fly.


## Requirements

- Python 3

You don't need a YouTube account or own the videos that you're monitoring.


## Usage

### Basic usage

You can simply run the script like so:

`python3 ytviewcount.py`

It will attempt to read URLs from a file called `videos.txt` (one URL per line) and write the result to a file called `viewcount.csv`.

Change the name of the input file with the `-i` option and that of the output file with the `-o` option:

`python3 ytviewcount.py -i myvideos.txt -o analysis.csv`

### Options

`--skipTotals` will not write the number of total views into the CSV file. May be useful if you want to do some automated processing of the CSV files.

`--printTotals` prints (displays) the total view count when running the script.

`--useCommas` will make the script use commas instead of semicolons as the field separators for the CSV file. I found that semicolons work better for software like Microsoft Excel or Apple's Numbers, but other software may prefer commas.

`--addUrl` will also write the video URL to the CSV file.

`--tedx` activates a TEDx mode where it assumes that the title of the video contains the name of the speaker and the name of the talk. The CSV file will then list them in separate columns.

`--tedxstuttgart` activates some special formatting for older videos from our TEDxStuttgart events. You won't need this option.


## Caveats and Side Effects

- Haven't tested this on Windows.
- This script relies on specific information embedded in the YouTube pages in specific ways. Once YouTube changes that format (again - it has happened before), this script will break.
- Use at your own risk and always make backups first.


## Who wrote this?

My name is Dirk Haun. I used to be a software engineer but have been doing other things for the past 5+ years. I also haven't written any Python in as many years, so please bear with me.


## Which license is this under?

MIT License, for now. I may change my mind at a later point, but for now there isn't a lot here that's worth protecting anyway. It'll always be open source under an OSI-approved license, promised!
