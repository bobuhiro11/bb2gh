#!/usr/bin/env python3

#
# Usage:
#   ./bb2gh.py <bibucket_user> <bibucket_pass> <github_user> <github_token>
#

import requests
import sys
import os
import time
import github
import random

bbuser = sys.argv[1]
bbpass = sys.argv[2]
ghuser = sys.argv[3]
ghtoken = sys.argv[4]

bbauth = requests.auth.HTTPBasicAuth(bbuser, bbpass)
g = github.Github(ghtoken)


def get_bb_repos():
    """
    get all bibucket repositories
    """
    bbrepos = {}
    url = 'https://api.bitbucket.org/2.0/repositories/' + bbuser
    while True:
        response = requests.get(url, auth=bbauth).json()
        for r in response["values"]:
            bbrepos[r["name"]] = r["links"]["clone"][1]["href"]
        time.sleep(1)

        # next page
        if "next" not in response:
            break
        else:
            url = response["next"]
    return bbrepos


def get_gh_repos():
    """
    get all github repositories
    """
    ghrepos = {}
    for r in g.get_user().get_repos():
        ghrepos[r.name] = r.ssh_url
    return ghrepos


def create_gh_repo(name):
    """
    create private github repository
    """
    return g.get_user().create_repo(
            name=name,
            private=True,
            )


def com_exec(command):
    print("command: " + command)
    rc = os.system(command)
    print("rc: " + str(rc))
    if rc != 0:
        sys.exit()


# main
print("--- bitbucket repositories ---")
bbrepos = get_bb_repos()
print(str(len(bbrepos)) + " repos found.")
for k, v in bbrepos.items():
    print(k + ": " + v)

print("--- github repositories ---")
ghrepos = get_gh_repos()
print(str(len(ghrepos)) + " repos found.")
for k, v in ghrepos.items():
    print(k + ": " + v)

print("--- repositories for migration ---")
mig_repo_names = bbrepos.keys() - ghrepos.keys()
# mig_repo_names = {"chatapp"}  # TEST repo
print(mig_repo_names)

print("--- start migration ---")
for name in mig_repo_names:
    bburl = bbrepos[name]
    ghurl = create_gh_repo(name).ssh_url
    time.sleep(random.randint(100, 200))
    com_exec("git clone --mirror " + bburl)
    com_exec("cd " + name.lower() + ".git;" +
             "git remote set-url --push origin " + ghurl)
    com_exec("cd " + name.lower() + ".git;" +
             "git push --mirror")
    com_exec("rm -rf " + name.lower() + ".git")
    time.sleep(random.randint(100, 200))
