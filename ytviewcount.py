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

    # most titles are formatted "<title> | <speaker> | TEDxEvent"
    parts = fulltitle.split(' | ')
    if len(parts) == 3:
        # most titles use this format
        title = parts[0]
        speaker = parts[1]

    # there's a lot of variation in the early days, though ...

    elif len(parts) == 2:
        # Possibly old style w/o title; there are two variants:
        # "<speaker> | TEDxEvent" and "TEDxEvent | <speaker>"
        if parts[0].find('TEDx') >= 0:
            title = parts[0]  # no title given, so use TEDx event name
            speaker = parts[1]
        elif parts[1].find('TEDx') >= 0:
            speaker = parts[0]
            title = parts[1]  # no title given, so use TEDx event name
        else:
            # just use both parts, whatever they are
            speaker = parts[0]
            title = parts[1]
            print("WARNING: format not recognized for", fulltitle)

        if title == 'TEDx':
            # special handling for https://www.youtube.com/watch?v=zf2F0c9R4Mc
            title = speaker
            speaker = 'TEDx'

    elif fulltitle[:4] == 'TEDx':
        # another popular old format: "TEDxEvent - <speaker> - <date>"
        # but also sometimes:         "TEDxEvent - <speaker> - <title>"
        parts = fulltitle.split(' - ')
        if len(parts) < 3:
            # typos (missing blank) happen ...
            p2 = fulltitle.split(' -')
            if len(p2) == 3:
                parts = p2
            else:
                p2 = fulltitle.split('- ')
                if len(p2) == 3:
                    parts = p2

        if len(parts) == 3:
            # double-check the last part - does it have numbers?
            p3 = parts[2].strip()
            if p3[:1].isdigit() and p3[-1].isdigit():
                title = parts[0]  # no title given, so use TEDx event name
                speaker = parts[1]
            else:
                title = parts[2]  # assume the last part is the title
                speaker = parts[1]
        else:
            # just use what we have, whatever it may be
            if len(parts) == 2:
                speaker = part[0]
                title = part[1]
            else:
                speaker = ''
                title = fulltitle
            print("WARNING: format not recognized for", fulltitle)

    elif ' at TEDx' in fulltitle:
        # yet another popular variation: "<something> at TEDxEvent"
        # where <something> may or may not include the title

        at = fulltitle.find(' at TEDx')
        something = fulltitle[:at].strip()

        c = something.find(':')
        if c < 0:
            # no colon? probably just "<speaker> at TEDxEvent"
            speaker = something
            title = fulltitle[at + 4:]  # use the TEDx event name

        else:
            # assume it's "<title>: <speaker> at TEDxEvent"
            # but there's a twist when the title ends with a punctuation mark
            p = something.rfind(':')  # find last(!) colon

            # check for title ending in '!' or '?'
            p2 = something.rfind('! ')
            if p2 < 0:
                p2 = something.rfind('? ')

            if p2 > 0 and p2 > p:
                # title ends in an exclamation mark
                title = something[:p2 + 1]  # including the punctuation mark
                speaker = something[p2 + 2:]
            else:
                # no extra punctuation mark, so assume title ends at ':'
                title = something[:p]
                speaker = something[p + 2:]

    else:
        # give up
        speaker = ''
        title = fulltitle
        print("WARNING: format not recognized for", fulltitle)

    if args.tedxstuttgart:
        # At TEDxStuttgart, we strip speakers of their titles.
        # Some early videos have it, though.
        speaker = speaker.replace('Dr.', '')
        speaker = speaker.replace('Prof.', '')
        # fix an embarrassing little typo in a speaker name
        if speaker == 'Dong Seon-Chang':
            speaker = 'Dong-Seon Chang'

        title = title.replace('--', '-')

    title = title.strip()
    speaker = speaker.strip()

    return speaker, title


def start_csvfile():
    global args, fieldsep

    headline = '"Title"' + fieldsep + '"Views"'
    if args.tedx:
        headline = '"Speaker"' + fieldsep + headline
    if args.addUrl:
        headline = headline + fieldsep + '"URL"'
    if args.withDate:
        headline = headline + fieldsep + '"PublicationDate"'

    with open(args.output, 'w', encoding='utf-8') as fs:
        fs.write(headline + os.linesep)


def write_csvline(title, views, url, speaker='', date=''):
    global args, fieldsep

    # need to escape quotes for CSV
    title = title.replace('"', '""')

    line = '"' + title + '"' + fieldsep + str(views)
    if args.tedx:
        line = '"' + speaker + '"' + fieldsep + line
    if args.addUrl:
        line = line + fieldsep + '"' + url + '"'
    if args.withDate:
        line = line + fieldsep + '"' + str(date) + '"'

    with open(args.output, 'a', encoding='utf-8') as fs:
        fs.write(line + os.linesep)


def finish_csvfile(totalviews):
    global args, fieldsep

    totals_text = 'Total Views:'

    if not args.skipTotals:
        totals = '"' + totals_text + '"' + fieldsep + str(totalviews)
        if args.tedx:
            totals = '""' + fieldsep + totals

        with open(args.output, 'a') as fs:
            fs.write(totals + os.linesep)

    if args.printTotals:
        print(totals_text, totalviews)


# Code originally by Christian Hill, taken from
# https://scipython.com/blog/parenthesis-matching-in-python/ & adapted
def find_parentheses(s):
    """ Find and return the location of the matching parentheses pairs in s.

    Given a string, s, return a dictionary of start: end pairs giving the
    indexes of the matching parentheses in s. Suitable exceptions are
    raised if s contains unbalanced parentheses.

    """

    # The indexes of the open parentheses are stored in a stack, implemented
    # as a list

    stack = []
    parentheses_locs = {}
    for i, c in enumerate(s):
        if c == '{':
            stack.append(i)
        elif c == '}':
            try:
                parentheses_locs[stack.pop()] = i
            except IndexError:
                # we don't care since we're parsing something incomplete
                break

    if stack:
        raise IndexError('No matching close parenthesis to open parenthesis '
                         'at index {}'.format(stack.pop()))

    # actually, we only care about the first, ie. outermost pair
    p = sorted([(k, v) for k, v in parentheses_locs.items()])

    return p[0][0], p[0][1]


def parse_page_video_details(code, url: str):
    global args

    views = 0
    result = {}

    pos1 = code.find('"videoDetails":')
    if pos1 > 0:
        pos = find_parentheses(code[pos1:])
        found_json = code[pos1 + pos[0]: pos1 + pos[1] + 1]

        # videoDetails should now hold a valid JSON string
        if found_json[0] == '{' and found_json[-1] == '}':
            details = json.loads(found_json)
            full_title = details['title']
            result['views'] = int(details['viewCount'])
            result['url'] = url

            if args.tedx:
                # do some special formatting for TEDx talks
                speaker, title = format_tedxtitle(full_title)
                result['speaker'] = speaker
                result['title'] = title
                # write_csvline(title, views, url, speaker)
            else:
                result['title'] = full_title

        else:
            print("not found - matching brackets for videoDetails")
    else:
        print("not found - videoDetails")

    return result


def parse_page_player_microformat_renderer(code, url: str):
    global args

    pos1 = code.find('"playerMicroformatRenderer":')
    if pos1 > 0:
        pos = find_parentheses(code[pos1:])
        found_json = code[pos1 + pos[0]: pos1 + pos[1] + 1]

        # videoDetails should now hold a valid JSON string
        if found_json[0] == '{' and found_json[-1] == '}':
            details = json.loads(found_json)
            if details['publishDate']:
                return details['publishDate']
            else:
                print("no publication date found")

        else:
            print("not found - matching brackets for playerMicroformatRenderer")
    else:
        print("not found - playerMicroformatRenderer")


### ###########################################################################


parser = argparse.ArgumentParser(description='Counts views of videos on YouTube')
parser.add_argument('-o', '--output', metavar='csvfile', default='viewcount.csv', help='Name of CSV output file')
parser.add_argument('-i', '--input', metavar='videofile', default='videos.txt',
                    help='Name of a file with a list of URLs')
parser.add_argument('--skipTotals', action='store_true', default=False,
                    help='Do not add total views entry to the CSV file.')
parser.add_argument('--printTotals', action='store_true', default=False, help='Print/display total views count.')
parser.add_argument('--useCommas', action='store_true', default=False,
                    help='Use commas as field separators in the CSV file.')
parser.add_argument('--addUrl', action='store_true', default=False, help='Add video URL to the CSV file.')
parser.add_argument('--tedx', action='store_true', default=False,
                    help='Videos are from a TEDx event (split title into speaker + talk title')
parser.add_argument('--tedxstuttgart', action='store_true', default=False,
                    help='Videos are from a TEDxStuttgart event (activates some custom formatting)')
parser.add_argument('--withDate', action='store_true', default=False,
                    help='Extract date of the publication of the video')
args = parser.parse_args()

if args.tedxstuttgart:
    args.tedx = True

fieldsep = ';'
if args.useCommas:
    fieldsep = ','

with open(args.input, 'r') as fs:
    videos = fs.readlines()

start_csvfile()

total_views = 0
for line in videos:
    url = line.strip()
    if len(url) > 0 and url[0] != '#' and url[:4] == 'http':

        with urllib.request.urlopen(url) as fs:
            content = fs.read().decode('utf-8')

        page_info = parse_page_video_details(content, url)

        if args.withDate:
            publication_date = parse_page_player_microformat_renderer(content, url)

        # We're in TEDx mode if speaker is set
        if args.tedx and page_info['speaker']:
            if args.withDate and publication_date:
                write_csvline(page_info['title'], page_info['views'], page_info['url'], page_info['speaker'],
                              publication_date)
            else:
                write_csvline(page_info['title'], page_info['views'], page_info['url'], page_info['speaker'])
        else:
            if args.withDate and publication_date:
                write_csvline(page_info['title'], page_info['views'], page_info['url'], publication_date)
            else:
                write_csvline(page_info['title'], page_info['views'], page_info['url'])

        total_views = total_views + page_info['views']

finish_csvfile(total_views)
