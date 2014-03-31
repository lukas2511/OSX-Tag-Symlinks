#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from xattr import xattr
sys.path.append("bplist-python/")
from bplist import BPlistReader
from glob import glob

TARGET = "/Users/lukas2511/Projects"

def touch(fname, times=None):
    with file(fname, 'a'):
        os.utime(fname, times)

def set_icon(tagname):
    iconpath = "%s/All/.icons/%s.png" % (TARGET, tagname)
    rsrcpath = "%s/All/.icons/%s.rsrc" % (TARGET, tagname)
    tagpath = "%s/%s" % (TARGET, tagname)
    iconfilepath = "%s/%s/Icon\r" % (TARGET, tagname) 
    if os.path.exists(iconpath):
        if not os.path.exists(iconfilepath) or os.path.getmtime(iconpath) > os.path.getmtime(iconfilepath):
            print("New Icon for %s" % tagname)
            os.system("sips -i %s > /dev/null" % iconpath)
            os.system("DeRez -only icns %s > %s" % (iconpath, rsrcpath))
            os.system("Rez -append %s -o %s/$'Icon\\r'" % (rsrcpath, tagpath))
            os.system("SetFile -a C %s" % tagpath)
            os.system("SetFile -a V %s/$'Icon\\r'" % tagpath)
    elif os.path.exists(iconfilepath):
        os.unlink(iconfilepath)

def get_tags(path):
    try:
        attrs = xattr(path)
        kMDItemUserTags = attrs['com.apple.metadata:_kMDItemUserTags']
        tmptags = BPlistReader(kMDItemUserTags).parse()
    except:
        tmptags = []
    rettags = []
    for tag in tmptags:
        rettags.append(tag.split("\n")[0])
    return rettags

def tag_exists(tagname):
    return os.path.exists("%s/%s" % (TARGET, tagname))

def create_tag(tagname):
    print("Creating new tag '%s'" % tagname)
    os.mkdir("%s/%s" % (TARGET, tagname))
    touch("%s/%s/.istag" % (TARGET, tagname))

def get_existing_tags():
    existing_folders = glob("%s/*/.istag" % TARGET)
    oldtags = []
    for existing_folder in existing_folders:
        oldtag = os.path.basename(os.path.dirname(existing_folder))
        oldtags.append(oldtag)
    return oldtags

def get_projects(tagname):
    existing_links = glob("%s/%s/*" % (TARGET, tagname))
    projects = []
    for existing_link in existing_links:
        project = os.path.basename(existing_link)
        if not project == "Icon\r":
            projects.append(project)
    return projects

def tag_empty(tagname):
    return get_projects(tagname) == []

def remove_empty_tag(tagname):
    print("Tag '%s' is empty, removing from directory structure" % tagname)
    os.unlink("%s/%s/.istag" % (TARGET, tagname))
    stupid_apple_files = ['.DS_Store',"Icon\r"]
    for stupid_apple_file in stupid_apple_files:
        if os.path.exists("%s/%s/%s" % (TARGET, tagname, stupid_apple_file)):
            os.unlink("%s/%s/%s" % (TARGET, tagname, stupid_apple_file))
    os.rmdir("%s/%s" % (TARGET, tagname))

def remove_project_from_tag(project, tagname):
    print("Removing '%s' from '%s'" % (os.path.basename(project), tagname))
    os.unlink("%s/%s/%s" % (TARGET, tagname, project))

def add_project_to_tag(project, tagname):
    print("Adding '%s' to '%s'" % (os.path.basename(project), tagname))
    os.symlink("%s/All/%s" % (TARGET, project), "%s/%s/%s" % (TARGET, tagname, project))

tags = {}

for project_path in glob("%s/All/*" % TARGET):
    tmptags = get_tags(project_path)
    project = os.path.basename(project_path)
    for tag in tmptags:
        if not tag in tags:
            tags[tag] = []
        tags[tag].append(project)

for tagname in get_existing_tags():
    oldprojects = get_projects(tagname)
    if not tagname in tags:
        for project in oldprojects:
            remove_project_from_tag(project, tagname)
        if tag_empty(tagname):
            remove_empty_tag(tagname)
    else:
        for project in oldprojects:
            if not project in tags[tagname]:
                remove_project_from_tag(project, tagname)
        for project in tags[tagname]:
            if not project in oldprojects:
                add_project_to_tag(project, tagname)

for tagname, projects in tags.iteritems():
    set_icon(tagname)
    if not tag_exists(tagname):
        create_tag(tagname)
        for project in projects:
            add_project_to_tag(project, tagname)
