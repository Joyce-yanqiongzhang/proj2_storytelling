input_sets = ["rocstory_plan_write/fairy_tale_title_key_story_test_5sents.txt", "rocstory_plan_write/fairy_tale_title_key_story_dev_5sents.txt", "rocstory_plan_write/fairy_tale_title_key_story_train_5sents.txt"]
output_sets = ["rocstory_plan_write/fairy_tale_key_story_test_5sents.txt", "rocstory_plan_write/fairy_tale_key_story_dev_5sents.txt", "rocstory_plan_write/fairy_tale_key_story_train_5sents.txt"]

for i in range(0, len(input_sets)):
    input_set = input_sets[i]
    output_set = output_sets[i]
    with open(input_set, 'r+') as f_in:
        with open(output_set, 'w') as f_out:
            num_of_blank = 0
            for line in f_in.readlines():
                line = line.split(" ")
                start_flg = False
                for word in line:
                    if word=='<EOT>':
                        start_flg = True
                        continue
                    if start_flg:
                        f_out.write(word + " ")
            
            # f_out.write(line)
            # print(num_of_blank)
            # if num_of_blank >= 4:
            #     f_out.write("<|endoftext|>\n")
            #     num_of_blank = 0
                
            
f_in.close()
f_out.close()