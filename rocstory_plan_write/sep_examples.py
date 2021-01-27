import random
n_total = 935
n_test = 90
n_dev = 90
# n_total = 2629
# n_test = 200
# n_dev = 200
test_dev_set = set()
while len(test_dev_set) < n_test+n_dev:
    test_dev_set.add(random.randint(0, n_total))
i_test = 0
i_dev = 0
with open('tidied/ks_dataset_addshort.txt', 'r') as f, open('tidied/ks_train_addshort.txt', 'w') as f_train, open('tidied/ks_dev_addshort.txt', 'w') as f_dev, open('tidied/ks_test_addshort.txt', 'w') as f_test:
    for i, line in enumerate(f.readlines()):
        if i in test_dev_set:
            if i_dev < n_dev:
                f_dev.write(line)
                i_dev += 1
            elif i_test < n_test:
                f_test.write(line)
                i_test += 1
        else:
            f_train.write(line)
f.close()
f_train.close()
f_dev.close()
f_test.close()

# i_test = 0
# i_dev = 0
# with open('title_key_story_5sents.txt', 'r') as f, open('fairy_tale_title_key_story_train_5sents.txt', 'w') as f_train, open('fairy_tale_title_key_story_dev_5sents.txt', 'w') as f_dev, open('fairy_tale_title_key_story_test_5sents.txt', 'w') as f_test:
#     for i, line in enumerate(f.readlines()):
#         if i in test_dev_set:
#             if i_dev < n_dev:
#                 f_dev.write(line)
#                 i_dev += 1
#             elif i_test < n_test:
#                 f_test.write(line)
#                 i_test += 1
#         else:
#             f_train.write(line)
# f.close()
# f_train.close()
# f_dev.close()
# f_test.close()


