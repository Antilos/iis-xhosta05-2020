#This script runs a series of flask commands that fill the app with default data (creates users, groups, threads...)
import subprocess

Users = [
    #[name, password, profile_vis]
    ["admin", "admin", "0"],
    ["oliver", "test", "0"],
    ["julia", "test", "1"],
    ["liam", "test", "3"]
    ["ema", "test", "3"]
]

Groups = [
    #[name, visibility, isOpen, ownerName]
    ["PublicGroup", "0", "True", "admin"],
    ["OnlyRegisteredGroup", "1", "True", "admin"],
    ["PrivateGroup", "3", "False", "admin"],
    ["publicgroup2","0","True","oliver"],
    ["onlyregisteregroup2","1","True","julia"],
    ["privategroup2","3","False","ema"]
]

Threads = [
    #[subject, openerName, groupName]
    ["toniejejulia","ema","privategroup2"],
    ["somerandomthread","ema","PublicGroup"],
    ["otherranomthread","julia","PublicGroup"],
    ["neadlismeITUcoteraz?","admin","OnlyRegisteredGroup"],
    ["aniterazneameITU","admin","OnlyRegisteredGroup"],
    ["Idemenapivo","julia","publicgroup2"],
    ["......","oliver","publicgroup2"]
]

Posts = [
    #[authorName, groupName, threadName, body]
    ["ema","publicgroup2","Idemenapivo","Ideme na pivo otvaraju krcmy"],
    ["oliver","publicgroup2","Idemenapivo","okej kedy?"],
    ["ema","publicgroup2","Idemenapivo","15.1. kto chcete pridadjte sa"],
    ["oliver","publicgroup2","Idemenapivo","to mam byt dodvtedy triezvy?"],
    ["ema","publicgroup2","Idemenapivo","...."],
    ["julia","publicgroup2","Idemenapivo","...."],
    ["admin","OnlyRegisteredGroup", "neadlismeITUcoteraz?", "minuly rok sme neadli ITU preto nas projekt na iis vyzera neintuitivne, sorry"],
    ["admin","OnlyRegisteredGroup", "aniterazneameITU", "tento rok  snad dame ITU a ked nie tak budeme asi jediny co vypadnu s fitu vdaka ITU :D"],
    ["julia","OnlyRegisteredGroup", "aniterazneameITU", "gl boyz"],
    ["admin","PublicGroup","somerandomthread","sdadsdaadsads" ],
    ["julia","PublicGroup","somerandomthread","sdadsdaadsads" ],
    ["ema","PublicGroup","somerandomthread","sdadsdaadsads" ],
    ["oliver","PublicGroup","somerandomthread","sdadsdaadsads" ],
    ["julia","PublicGroup","somerandomthread","sdadsdaadsads" ],
    ["julia","PublicGroup","otherranomthread","sdadsdaddadssdadddqwwdsadadasdsdadd" ],
    ["ema","PublicGroup","otherranomthread","sdadsdaddadssdadddqwwdsadadasdsdadd" ],
    ["oliver","PublicGroup","otherranomthread","sdadsdaddadssdewqeaacsdvdadddqwwdsadadasdsdadd" ],
    ["admin","PublicGroup","otherranomthread","sdadsdaddadssdaweqeqwdddqwwdsadadasdsdadd" ],
    ["oliver","PublicGroup","otherranomthread","sdadsdaddadssddsadddsdaddadddqwwdsadadasdsdadd" ],
    ["oliver","PublicGroup","otherranomthread","sdadsdaddadssdadewqewqeqwddqwwdsadadasdsdadd" ],
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
