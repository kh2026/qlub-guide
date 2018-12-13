# -*- coding: utf-8 -*-
"""
Created on Thu Nov 15 21:15:06 2018

Gets the information for all of the clubs and then saves them to a csv file

"""

import urllib.request
import re
import csv

# get a string which includes all of the clubs 
clublist = ""
clubs = open('clubs.html', 'r')
for line in clubs:
    clublist += line

# from the webpage finds all of sections with clubs
q = re.compile("<li>([\s\S]*?)</li")
info_list = q.findall(clublist)
# remove uesless information
info_list = info_list[24:]

# get the names of all of the clubs from each section
q = re.compile(">(.*?)</a>")
club_names = []
for club in info_list:
    club_names.append(q.findall(club))


# get the webpage links of all of the clubs
q = re.compile("a href=\"(.*?)\">")
club_links = []
for club in info_list:
    club_links.append(q.findall(club))
    
# get the website/email information for all of the clubs by scraping the webpage links
club_emails = []
club_sites = []
club_descriptions = []
for club in club_links:
    link = "https://fas-mini-sites.fas.harvard.edu/osl/grouplist" + club[0]
    print(link)
    webpage = (urllib.request.urlopen(link)).read()
    webpage = str(webpage)
    club_emails.append(re.compile("a href=\"(.*?)\">").findall(webpage)[1])
    club_sites.append(re.compile("a href=\"(.*?)\">").findall(webpage)[2])
    club_descriptions.append(re.compile("<p>(.*?)</p>").findall(webpage)[0])

# change the lists for club names to lists of strings rather than lists of lists
for i in range(len(club_names)):
    club_names[i] = club_names[i][0]
    
# write the information to a csv file which may be imported to the database
information = list(zip(club_names, club_descriptions, club_emails, club_sites))
clubinfo = open('clubinfo.csv', 'w')
with clubinfo:
    writer = csv.writer(clubinfo)
    writer.writerows(information)
    



