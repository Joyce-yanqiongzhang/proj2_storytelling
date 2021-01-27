import argparse
import math
import random

parser = argparse.ArgumentParser()
parser.add_argument('--duptime', type = int, default = 1, 
                        help='the number of times we copy fables data')
args = parser.parse_args()

# clear buffer 
with open('buffer.txt', 'r+') as f:
    f.truncate()
f.close()
# process title to key, use 10 sents data
# combine fairy tale tk train, dev, test and add fables
datasets = ['train', 'dev', 'test']
total_lines = 0
for d in datasets:
    readpath_fairy = '../fairy_tale_title_key_' + d + '_10sents.txt'
    readpath_fables = 'fairy_tale_title_key_' + d + '_10sents_fables.txt'
    # outpath = 'fairy_fables_title_key_' + d + '_10sents.txt'   
    with open('buffer.txt', 'a') as fwrite, open(readpath_fairy, 'r') as f_fairy, open(readpath_fables, 'r') as f_fables:
        for line in f_fairy.readlines():
            fwrite.write(line)
            total_lines += 1
        for t in range(args.duptime):
            for line in f_fables.readlines():
                fwrite.write(line)
                total_lines += 1
        
    fwrite.close()
    f_fairy.close()
    f_fables.close()

num_dev_test = total_lines // 5
dev_train_idx = set()
while len(dev_train_idx)<num_dev_test:
    dev_train_idx.add(random.randint(0,total_lines))
cur_dev_test = 0
[train_path, dev_path, test_path] = ['fairy_fables_title_key_' + d + '_10sents_dup' + str(args.duptime) + '.txt' for d in datasets]
with open(train_path, 'w') as f_train, open(dev_path, 'w') as f_dev, open(test_path, 'w') as f_test, open('buffer.txt', 'r') as f:
    for i, line in enumerate(f.readlines()):
        if i in dev_train_idx:
            if cur_dev_test < num_dev_test//2:
                f_dev.write(line)
                cur_dev_test += 1
            elif cur_dev_test < num_dev_test:
                f_test.write(line)
                cur_dev_test += 1
        else:
            f_train.write(line)
f_train.close()
f_dev.close()
f_test.close()
f.close()

# clear buffer 
with open('buffer.txt', 'r+') as f:
    f.truncate()
f.close()


# process key to story data, use 5 sents data
total_lines = 0
for d in datasets:
    readpath_fairy = '../fairy_tale_key_story_' + d + '_5sents.txt'
    readpath_fables = 'fairy_tale_key_story_' + d + '_5sents_fables.txt'
    # outpath = 'fairy_fables_title_key_' + d + '_10sents.txt'   
    with open('buffer.txt', 'a') as fwrite, open(readpath_fairy, 'r') as f_fairy, open(readpath_fables, 'r') as f_fables:
        for line in f_fairy.readlines():
            fwrite.write(line)
            total_lines += 1
        for t in range(args.duptime):
            for line in f_fables.readlines():
                fwrite.write(line)
                total_lines += 1
        
    fwrite.close()
    f_fairy.close()
    f_fables.close()

num_dev_test = math.floor(total_lines * 0.2)
dev_train_idx = set()
while len(dev_train_idx)<num_dev_test:
    dev_train_idx.add(random.randint(0,total_lines))
cur_dev_test = 0
[train_path, dev_path, test_path] = ['fairy_fables_key_story_' + d + '_5sents_dup' + str(args.duptime) + '.txt' for d in datasets]
with open(train_path, 'w') as f_train, open(dev_path, 'w') as f_dev, open(test_path, 'w') as f_test, open('buffer.txt', 'r') as f:
    for i, line in enumerate(f.readlines()):
        if i in dev_train_idx:
            if cur_dev_test < num_dev_test//2:
                f_dev.write(line)
                cur_dev_test += 1
            elif cur_dev_test < num_dev_test:
                f_test.write(line)
                cur_dev_test += 1
        else:
            f_train.write(line)

f_train.close()
f_dev.close()
f_test.close()
f.close()

# clear buffer 
with open('buffer.txt', 'r+') as f:
    f.truncate()
f.close()
        
