# Siyuan Zhou
# coding=UTF-8
import urllib.request
from collections import deque
import csv
from tkinter import *


# if "HTTPError 403", open url with this method
def SetHeaderOpenURL(url):
    u = urllib.request.URLopener()
    u.addheaders = []
    u.addheader('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36')
    u.addheader('Accept-Language', 'de-DE,de;q=0.9,en;q=0.8')
    u.addheader('Accept', '*/*')
    try:
        page = u.open(url)
        pagetext = page.read().decode("utf-8")
        page.close()
    except Exception:
        return ""
    return pagetext


# if "HTTP Error 302", open url with this method
def RequestOpenURL(url):
    request = urllib.request.Request(url)
    opener = urllib.request.build_opener()
    try:
        page = opener.open(request, timeout=5)
        pagetext = page.read().decode("utf-8")
        page.close()
    except Exception:
        return ""
    return pagetext


def ParseURL(url):
    try:
        page = urllib.request.urlopen(url, timeout=3)
        pagetext = page.read().decode("utf-8")
        page.close()
        return pagetext
    except urllib.request.HTTPError as err:
        if err.code == 403:     # forbidden
            return SetHeaderOpenURL(url)
        elif err.code == 302:   # redirect temporary url
            return RequestOpenURL(url)
        else:
            return ""
    except Exception:
        return ""


def BreadthFirstOrderHref(url, serialnum):
    hrefdeque = deque()     # in order to breadth first order, store links
    hrefvisited = []        # store visited links
    link_childs = {}        # a dictionary of link:links which link includes
    linktext = []           # the name of all links

    hrefstr = '<a href ?= ?\"(https?://.+?)\".*?>([^</>]+?)</a>'  # regualr expression
    hrefre = re.compile(hrefstr, re.I)  # get matches

    hrefdeque.append(url)
    hrefvisited.append(url)
    hrefcount = 1           # the count of links of appending hrefdeque
    index = 0
    while hrefdeque:        # hrefdeque is not empty
        while hrefdeque:
            hreftemp = hrefdeque.popleft()  # dequeue
            link_childs[hreftemp] = []
            print("\t" + str(index) + " " + hreftemp + " is being parsed...")   # print prompt message --> parsing url
            index += 1
            pagetext = ParseURL(hreftemp)    # get the decode of the "hreftemp" link
            if len(pagetext) > 0:               # ParseURL is successed
                break
        href_textlist = hrefre.findall(pagetext)    # return a list of tuple(link, text)
        for href_text in href_textlist:
            link_childs[hreftemp].append(href_text[0])
            if href_text[0] not in hrefvisited:     # is not repeated link
                if hrefcount <= 100:        # not greater than 100 links
                    hrefcount += 1
                    hrefdeque.append(href_text[0])
                hrefvisited.append(href_text[0])
                linktext.append(href_text[1])

    # Generate a csv file
    resultfilename = str(serialnum) + ".csv"
    with open(resultfilename, 'w') as fresult:
        spamwriter = csv.writer(fresult, dialect='excel')
        l = len(link_childs.keys())
        if l > 101:
            l = 101
        for index in range(1, l):
            href = hrefvisited[index]
            if len(link_childs[href]) == 0:
                spamwriter.writerow(list((href, "")))
                continue
            childstr = link_childs[href][0]
            for i in range(1, len(link_childs[href])):
                childstr += (", " + link_childs[href][i])
            spamwriter.writerow(list((href, childstr)))
    return linktext


def GeneratorWordCloud(names):
    word_nums = {}

    # calculate the number of words
    for name in names:
        name = name.split()
        for i in range(len(name)):
            if name[i] in word_nums.keys():
                word_nums[name[i]] += 1
            else:
                word_nums[name[i]] = 1

    # sorted by number and show the 15 most popular words
    wordnumlist = sorted(word_nums.items(), key=lambda value: value[1], reverse=True)
    length = len(wordnumlist)
    if length == 0:
        return []
    if length > 15:
        length = 15

    printcon = "{" + wordnumlist[0][0] + ":" + str(wordnumlist[0][1])
    for i in range(1, length):
        printcon += (", " + wordnumlist[i][0] + ":" + str(wordnumlist[i][1]))
    printcon += "}"
    print(printcon)
    return wordnumlist[0:length]


def DrawWordCloud(wordnumlist, title):
    root = Tk()
    rel = [(0.75, 0.3), (0.4, 0.65), (0.25, 0.46), (0.3, 0.1), (0.25, 0.28), (0.81, 0.7), (0.25, 0.8), (0.85, 0.1),\
         (0.5, 45.6), (0.25, 0.55), (0.78, 0.45), (0.48, 0.18), (0.58, 0.8), (0.4, 0.35), (0.5, 0.5)]
    fonts = []
    for i in range(38, 8, -2):
        fonts.append(("Arial", i))
    root.title(title)
    root.geometry('600x380')
    for i in range(len(wordnumlist)):
        l = Label(root, text=wordnumlist[i][0], font=fonts[i])
        l.place(relx=rel[i][0], rely=rel[i][1], anchor=CENTER)
    root.mainloop()


if __name__ == "__main__":
    furl = open("urls.txt")
    urls = furl.readlines()
    furl.close()
    for i in range(len(urls)):
        url = urls[i].strip()
        print(url)          # output prompt message --> which url
        textname = BreadthFirstOrderHref(url, i+1)
        wordnumlist = GeneratorWordCloud(textname)
        DrawWordCloud(wordnumlist, url)
