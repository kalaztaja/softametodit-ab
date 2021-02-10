from pydriller import RepositoryMining
import csv
import shutil

filename = "commitData.csv"
csv_writer = csv.writer(open(filename, 'w'))
csv_writer.writerow(["projectID", "commitHash", "commitMessage", "author", "authorDate", "authorTimezone",
                     "committeer", "committeerDate", "committeerTimezone", "branches", "inMainBranch", "merge", "parents"])
for commit in RepositoryMining('../usr/src').traverse_commits():

    projectName = commit.project_name
    commitHash = commit.hash
    message = commit.msg

    author = commit.author.name
    date = commit.author_date
    timezone = commit.author_timezone

    committeer = commit.committer.name
    committeerDate = commit.committer_date
    committeerTimezone = commit.committer_timezone

    branches = commit.branches
    inMainBranch = commit.in_main_branch

    merge = commit.merge
    parents = commit.parents

    csv_writer.writerow([projectName, commitHash, message, author, date, timezone,
                         committeer, committeerDate, committeerTimezone, branches, inMainBranch, merge, branches])

shutil.move("commitData.csv", "usr/out/commitData.csv")
