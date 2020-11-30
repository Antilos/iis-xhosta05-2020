#This script runs a series of flask commands that fill the app with default data (creates users, groups, threads...)
import subprocess

Users = [
    #[name, password, profile_vis]
    ["admin", "admin", "0"],
    ["oliver", "test", "0"],
    ["eva", "test", "1"],
    ["liam", "test", "3"]
    ["ema", "test", "3"]
]

Groups = [
    #[name, visibility, isOpen, ownerName]
    ["PublicGroup", "0", "True", "admin"],
    ["OnlyRegisteredGroup", "1", "True", "admin"],
    ["PrivateGroup", "3", "False", "admin"],
]

Threads = [
    #[subject, openerName, groupName]
]

Posts = [
    #[authorName, threadName, body]
]

#empty database
subprocess.run(["flask", "users", "delete-all"])
subprocess.run(["flask", "groups", "delete-all"])
subprocess.run(["flask", "threads", "delete-all"])
subprocess.run(["flask", "posts", "delete-all"])

#fill database
for user in Users:
    subprocess.run(["flask", "users", "create"] + user)

subprocess.run(["flask", "users", "promote-to-admin", "admin"])

for group in Groups:
    subprocess.run(["flask", "groups", "create"] + group)

for thread in Threads:
    subprocess.run(["flask", "threads", "create"] + thread)

for post in Posts:
    subprocess.run(["flask", "posts", "create"] + post)
