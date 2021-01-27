import argparse

#get filepath from the input
parser = argparse.ArgumentParser()
parser.add_argument('--printfile', type=str, default = "")
args = parser.parse_args()
filepath = args.printfile

with open(filepath, 'r') as f:
    for line in f.readlines():
        line = line.split(" ")
        start_story = False
        if "<EOL>" in line:
            for word in line:
                if word=="<EOL>":
                    start_story = True
                    continue
                if start_story:
                    if not word == "</s>":
                        print(word, end=' ')
        else:
            for word in line:   
                if not word == "</s>":
                    print(word, end=' ')
        print("***** end of the story *****")


f.close()