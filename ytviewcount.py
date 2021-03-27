# ytviewcount - Counts views of videos on YouTube
#
# written 2021 by Dirk Haun <dirk AT haun-online DOT de>
# licensed under the MIT license
#
import argparse
import json
import os
import urllib.request

### ###########################################################################

def format_tedxtitle(fulltitle):
    """ For TEDx talks, split the video title into speaker + talk title """

    global args

    # newer titles are formatted "<title> | <speaker> | TEDxEvent"
    parts = fulltitle.split('|')
    if len(parts) < 3:
        # old-style titles are formatted "<title>: <speaker> at TEDxEvent"

        # exception: Ross Fisher's talk has a colon in the title,
        # and the title ends in a question mark
        p = fulltitle.find('?')
        if p > 0:
            # include question mark
            title = fulltitle[0:p+1]
        else:
            # find last(!) colon, for titles with a colon in them
            p = fulltitle.rfind(':')
            title = fulltitle[0:p]
        if p > 0:
            at = fulltitle.find(" at ")
            if at > 0:
                speaker = fulltitle[p+2:at]

                title = title.strip()
                speaker = speaker.strip()
            else:
                print("not found - old-style speaker name")
        else:
            print("not found - old-style title")
    else:
        title = parts[0].strip()
        speaker = parts[1].strip()

    if args.tedxstuttgart:
        # At TEDxStuttgart, we strip speakers of their titles.
        # Some early videos have it, though.
        speaker = speaker.replace('Dr.', '')
        speaker = speaker.replace('Prof.', '')

        title = title.replace('--', '-')

    title = title.strip()
    speaker = speaker.strip()

    return speaker, title


def start_csvfile():

    global args

    with open(args.output, 'w') as fs:
        if args.tedx:
            fs.write('"Speaker";"Title";"Views"' + os.linesep)
        else:
            fs.write('"Title";"Views"' + os.linesep)


def write_csvline(title, views, speaker = ''):

    global args

    # need to escape quotes for CSV
    title = title.replace('"', '""')

    if args.tedx:
        line = '"' + speaker + '";"' + title + '";"' + views + '"'
    else:
        line = '"' + title + '";"' + views + '"'

    with open(args.output, 'a', encoding = 'utf-8') as fs:
        fs.write(line + os.linesep)


def finish_csvfile(totalviews):

    global args

    with open(args.output, 'a') as fs:
        if args.tedx:
            fs.write('"";"Total Views:";"' + str(totalviews) + '"' + os.linesep)
        else:
            fs.write('"Total Views:";"' + str(totalviews) + '"' + os.linesep)



def parse_page(code):

    global args

    views = 0

    # We assume there's a piece of JSON between "videoDetails" & "annotations".
    # Should YouTube change this, this piece of code will break.
    # (tbd: instead, search for a pair of matching { + } after videoDetails)

    pos1 = code.find('"videoDetails":')
    pos2 = code.find('"annotations":')

    if pos1 > 0 and pos2 > 0 and pos2 > pos1:

        videoDetails = code[pos1 + 15:pos2 - 1]

        # videoDetails should now hold a valid JSON string
        if videoDetails[0] == '{' and videoDetails[-1] == '}':
            details = json.loads(videoDetails)
            fulltitle = details['title']
            views = details['viewCount']

            if args.tedx:
                # do some special formatting for TEDx talks
                speaker, title = format_tedxtitle(fulltitle)
            else:
                title = fulltitle

            if args.tedx:
                write_csvline(title, views, speaker)
            else:
                write_csvline(title, views)

        else:
            print("not found - matching brackets for videoDetails")
    else:
        print("not found - videoDetails")

    return int(views)

### ###########################################################################

parser = argparse.ArgumentParser(description = 'Counts views of videos on YouTube')
parser.add_argument('-o', '--output', metavar = 'csvfile', default = 'viewcount.csv', help = 'Name of CSV output file')
parser.add_argument('-i', '--input', metavar = 'videofile', default = 'videos.txt', help = 'Name of a file with a list of URLs')
parser.add_argument('--tedx', action = 'store_true', default = False, help = 'Videos are from a TEDx event (split title into speaker + talk title')
parser.add_argument('--tedxstuttgart', action = 'store_true', default = False, help = 'Videos are from a TEDxStuttgart event (activates some custom formatting)')
args = parser.parse_args()

if args.tedxstuttgart:
    args.tedx = True

with open(args.input, 'r') as fs:
    videos = fs.readlines()

start_csvfile()

totalviews = 0
for line in videos:
    url = line.strip()
    if len(url) > 0 and url[0] != '#':

        with urllib.request.urlopen(url) as f:
            content = f.read().decode('utf-8')

        views = parse_page(content)
        totalviews = totalviews + views

finish_csvfile(totalviews)

