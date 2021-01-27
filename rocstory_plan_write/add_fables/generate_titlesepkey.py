input_sets = ["fairy_tale_title_key_story_test_10sents_fables.txt", "fairy_tale_title_key_story_dev_10sents_fables.txt", "fairy_tale_title_key_story_train_10sents_fables.txt"]
output_sets = ["fairy_tale_title_key_test_10sents_fables.txt", "fairy_tale_title_key_dev_10sents_fables.txt", "fairy_tale_title_key_train_10sents_fables.txt"]

for i in range(0, len(input_sets)):
    input_set = input_sets[i]
    output_set = output_sets[i]
    with open(input_set, 'r+') as f_in:
        with open(output_set, 'w') as f_out:
            num_of_blank = 0
            for line in f_in.readlines():
                line = line.split(" ")
                start_flg = True
                for word in line:
                    if '<EOL>' in word:
                        f_out.write(word + " ")
                        start_flg = False
                    if start_flg:
                        f_out.write(word + " ")
                f_out.write("\n")
            
            # f_out.write(line)
            # print(num_of_blank)
            # if num_of_blank >= 4:
            #     f_out.write("<|endoftext|>\n")
            #     num_of_blank = 0
                
            
f_in.close()
f_out.close()