#This script runs a series of flask commands that fill the app with default data (creates users, groups, threads...)
import subprocess

Users = [
    #[name, password, profile_vis]
    ["admin", "admin", "0"],
    ["publicUser", "user", "0"],
    ["onlyRegisteredSeeMeUser", "user", "1"],
    ["privateUser", "user", "3"],
    ["ema", "user", "3"]
]

Groups = [
    #[name, visibility, isOpen, ownerName]
    ["PublicGroup", "0", "True", "admin"],
    ["OnlyRegisteredGroup", "1", "True", "admin"],
    ["PrivateGroup", "3", "False", "admin"],
    ["publicgroup2","0","True","publicUser"],
    ["onlyregisteregroup2","1","True","onlyRegisteredSeeMeUser"],
    ["privategroup2","3","False","privateUser"]
]

Threads = [
    #[subject, openerName, groupName]
    ["toniejejulia","privateUser","privategroup2"],
    ["somerandomthread","privateUser","PublicGroup"],
    ["otherranomthread","onlyRegisteredSeeMeUser","PublicGroup"],
    ["neadlismeITUcoteraz?","admin","OnlyRegisteredGroup"],
    ["aniterazneameITU","admin","OnlyRegisteredGroup"],
    ["Idemenapivo","onlyRegisteredSeeMeUser","publicgroup2"],
    ["......","publicUser","publicgroup2"]
]

Posts = [
    #[authorName, groupName, threadName, body]
    ["privateUser","publicgroup2","Idemenapivo","Ideme na pivo otvaraju krcmy"],
    ["publicUser","publicgroup2","Idemenapivo","okej kedy?"],
    ["privateUser","publicgroup2","Idemenapivo","15.1. kto chcete pridadjte sa"],
    ["publicUser","publicgroup2","Idemenapivo","to mam byt dodvtedy triezvy?"],
    ["privateUser","publicgroup2","Idemenapivo","...."],
    ["onlyRegisteredSeeMeUser","publicgroup2","Idemenapivo","...."],
    ["admin","OnlyRegisteredGroup", "neadlismeITUcoteraz?", "minuly rok sme neadli ITU preto nas projekt na iis vyzera neintuitivne, sorry"],
    ["admin","OnlyRegisteredGroup", "aniterazneameITU", "tento rok  snad dame ITU a ked nie tak budeme asi jediny co vypadnu s fitu vdaka ITU :D"],
    ["onlyRegisteredSeeMeUser","OnlyRegisteredGroup", "aniterazneameITU", "gl boyz"],
    ["admin","PublicGroup","somerandomthread","sdadsdaadsads" ],
    ["onlyRegisteredSeeMeUser","PublicGroup","somerandomthread","sdadsdaadsads" ],
    ["privateUser","PublicGroup","somerandomthread","sdadsdaadsads" ],
    ["publicUser","PublicGroup","somerandomthread","sdadsdaadsads" ],
    ["onlyRegisteredSeeMeUser","PublicGroup","somerandomthread","sdadsdaadsads" ],
    ["onlyRegisteredSeeMeUser","PublicGroup","otherranomthread","sdadsdaddadssdadddqwwdsadadasdsdadd" ],
    ["privateUser","PublicGroup","otherranomthread","sdadsdaddadssdadddqwwdsadadasdsdadd" ],
    ["publicUser","PublicGroup","otherranomthread","sdadsdaddadssdewqeaacsdvdadddqwwdsadadasdsdadd" ],
    ["admin","PublicGroup","otherranomthread","sdadsdaddadssdaweqeqwdddqwwdsadadasdsdadd" ],
    ["publicUser","PublicGroup","otherranomthread","sdadsdaddadssddsadddsdaddadddqwwdsadadasdsdadd" ],
    ["publicUser","PublicGroup","otherranomthread","sdadsdaddadssdadewqewqeqwddqwwdsadadasdsdadd" ],
]

TagsToUsers = [
    #[username, keyword]
]

TagsToGroups = [
    #[groupName, keyword]
    ["PublicGroup", "public"],
    ["PublicGroup", "ahoj"],
    ["PublicGroup", "serus"],
    ["PublicGroup", "ano"],
    ["OnlyRegisteredGroup","registered"],
    ["OnlyRegisteredGroup","ahoj"],
    ["PrivateGroup","private"],
    ["PrivateGroup","serus"],
    ["PrivateGroup","nie"],
    ["publicgroup2","public"],
    ["onlyregisteregroup2","nie"],
    ["onlyregisteregroup2","ano"],
    ["onlyregisteregroup2","ahoj"],
    ["privategroup2","mozno"],
    ["privategroup2","ano"]

]

addMembers = [
    #[group_name, username]
    ["PublicGroup","onlyRegisteredSeeMeUser"],
    ["PublicGroup","privateUser"],
    ["OnlyRegisteredGroup","ema"],
    ["PrivateGroup","ema"],
    ["PrivateGroup","onlyRegisteredSeeMeUser"],
    ["onlyregisteregroup2","onlyRegisteredSeeMeUser"],
    ["onlyregisteregroup2","admin"],
    ["privategroup2","admin"],
    ["privategroup2","ema"]
]

addModerators = [
    #[group_name, username]
    ["PublicGroup","onlyRegisteredSeeMeUser"],
    ["PrivateGroup","ema"],
    ["onlyregisteregroup2","admin"],
    ["privategroup2","admin"]
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

for tag in TagsToGroups:
    subprocess.run(["flask", "groups", "add-tag"] + tag)

for tag in TagsToUsers:
    subprocess.run(["flask", "users", "add-tag"] + tag)

for member in addMembers:
    subprocess.run(["flask", "groups", "add-member"] + member)

for moderator in addModerators:
    subprocess.run(["flask", "groups", "add-moderator"] + moderator)

