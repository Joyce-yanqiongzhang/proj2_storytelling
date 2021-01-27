from generate_fairytale import generate_story_from_characters
from utils import print_story_storyline
import sys
import numpy, math
import torch
import torch.nn as nn
from numbers import Number
from utils import batchify, get_batch, repackage_hidden
from ir_baseline import IRetriver
import random
#from . 
import data as da
from queue import Queue

STORYPATH = '/home/serena/Desktop/proj2_storytelling/story/'
TEXTPATH = '/home/serena/Desktop/proj2_storytelling/story/storytelling/statics/text/'
# vocabtk = STORYPATH+'models/tidied/vocab_tk.pkl'
# vocabks = STORYPATH+'models/tidied/vocab_ks.pkl'
# checkpointtk = STORYPATH+'models/tidied/tk_500epoch_bptt100.pkl'
# checkpointks = STORYPATH+'models/tidied/ks_300epoch_bptt2000.pkl'
vocabtk = STORYPATH+'models/tidied/vocab_tk_addshort.pkl'
vocabks = STORYPATH+'models/tidied/vocab_ks_addshort.pkl'
checkpointtk = STORYPATH+'models/tidied/tk_addshort_500epoch_bptt100.pkl'
checkpointks = STORYPATH+'models/tidied/ks_addshort_300epoch_bptt2000.pkl'
args_sents = 40
args_words = 2000
args_seed = 1111
args_cuda = True
temperaturetk = 0.5
temperatureks = 0.8

def generate_story_from_characters(character_set):
    # Set the random seed manually for reproducibility.
    if torch.cuda.is_available():
        if not args_cuda:
            print("WARNING: You have a CUDA device, so you should probably run with --cuda")
        else:
            torch.cuda.manual_seed(args_seed)

    if temperaturetk < 1e-3 or temperatureks < 1e-3:
        print("--temperature has to be greater or equal 1e-3")

    # with open(checkpointtk, 'rb') as f:
    #     #model = torch.load(f, map_location=lambda storage, loc: storage)
    #     modeltk, criteriontk, optimizertk = torch.load(f, map_location=lambda storage, loc: storage)
    # with open(checkpointks, 'rb') as f:
    #     #model = torch.load(f, map_location=lambda storage, loc: storage)
    #     modelks, criterionks, optimizerks = torch.load(f, map_location=lambda storage, loc: storage)
    modeltk, criteriontk, optimizertk = torch.load(checkpointtk, map_location=lambda storage, loc: storage)
    modelks, criteriontk, optimizertk = torch.load(checkpointks, map_location=lambda storage, loc: storage)

    if args_cuda:
        modeltk.cuda()
        modelks.cuda()
    else:
        modeltk.cpu()
        modelks.cpu()


    corpustk = da.Corpus(applyDict=True, dict_path=vocabtk)
    corpusks = da.Corpus(applyDict=True, dict_path=vocabks)

    ntokenstk = len(corpustk.dictionary)
    ntokensks = len(corpusks.dictionary)

    criteriontk = nn.CrossEntropyLoss()  #NLLLoss()
    criterionks = nn.CrossEntropyLoss()  #NLLLoss()

    hiddentk = modeltk.init_hidden(1)
    hiddenks = modelks.init_hidden(1)

    inputtk = torch.rand(1, 1).mul(ntokenstk).long()  #, volatile=True)
    inputks = torch.rand(1, 1).mul(ntokensks).long()  #, volatile=True)

    # For HappyEnding and SadEnding Generation
    # ending_dict = {0:'*HappyEnding', 1:'*SadEnding', 2:'*OtherEnding'}
    #start_word = ending_dict[numpy.random.randint(0,3)]
    #input.data.fill_(corpus.dictionary.word2idx[start_word])
    print('ntokenstk', ntokenstk, file=sys.stderr)
    print('ntokensks', ntokensks, file=sys.stderr)
    #print('input:', input)
    if args_cuda:
        inputtk.data = inputtk.data.cuda()
        inputks.data = inputks.data.cuda()

    ######### GLOBALS #########
    eos_idtk = corpustk.dictionary.word2idx['<eos>']
    eos_idks = corpusks.dictionary.word2idx['<eos>']

    delimiter = '#'  # this delimits multi-word phrases. Only used to prevent the delimiter from being deduped in cond_generate when flag present
    delimiter_idxtk = corpustk.dictionary.word2idx[delimiter]
    delimiter_idxks = corpusks.dictionary.word2idx[delimiter]

    print('eos id tk:', eos_idtk, file=sys.stderr)
    print('eos id ks:', eos_idks, file=sys.stderr)
    #data = corpus.test.tolist() #test.tolist()
    #punc_idxs = set([corpus.dictionary.word2idx[p] for p in '.?!'])
    test_batch_size = 1

    # environment_set = ['castle', 'forest', 'mountain']
    # selected_env = random.choice(environment_set)
    # print('selected env:', selected_env)
    # print('characters:', character_set)

    #create the buffer title txt
    with open(TEXTPATH+'buffer_title.txt', 'w') as f:
        for cha in character_set:
            f.write(cha + ' <EOT> \n')
        f.close()

    # generate storyline from title
    with torch.no_grad(): 
        with open(TEXTPATH+'buffer_storyline.txt', 'w') as outf: #, open('gold_4sent.txt', 'w') as gf:      
                data = corpustk.tokenize(TEXTPATH+'buffer_title.txt', applyDict=True).tolist()  # this is a list of ids corresponding to words from the word2idx dict
                nsent = 0
                while nsent < args_sents:
                    try:
                        idx = data.index(eos_idtk)  # the only thing that breaks the while loop is if there are no more eos_ids
                    except:
                        break
                    # this sets the conditional length to be before the first encountered EOS symbol, which is added in preprocessing
                    cond_length = idx #min(idx, 3) #ent_idxes[-3] #0] #-2]
                    #print('cond. length:', idx)
                    exist_word = set()
                    for i in range(args_words):
                        if i < cond_length:
                            word_idx = data[i]
                        else:
                            output = modeltk.decoder(output)
                            word_weights = output.squeeze().data.div(temperaturetk).exp().cpu()
                            samples = torch.multinomial(word_weights, 5)
                            # apply dedup to storyline generation
                            for word_idx in samples:
                                word_idx = word_idx.item()
                                if word_idx not in exist_word or word_idx == delimiter_idxtk:
                                    break
                            #print('dedup!!!', exist_word, samples, word_idx)
                            exist_word.add(word_idx)
                        inputtk.data.fill_(word_idx)
                        output, hiddentk = modeltk(inputtk, hiddentk)
                        if word_idx == eos_idtk :
                            outf.write('\n')
                            break
                        word = corpustk.dictionary.idx2word[word_idx]
                         # prints the prompt that is conditioned on only when flag is present
                            # not print the conditional data
                            # outf.write(word + ' ')
                        if i >= cond_length:
                            outf.write(word + ' ')
                        #if i == cond_length-1:
                        #    outf.write('\t >>\t')
                    data = data[idx+1:]  # start after the previous idx id
                    print('| Generated {} sentences'.format(nsent+1), file=sys.stderr)
                    nsent += 1
                #gf.flush()
                outf.flush()

    # # add character_set into buffer_storyline
    # with open(TEXTPATH+'buffer_added_storyline.txt', 'w') as fout, open(TEXTPATH+'buffer_storyline.txt', 'r+') as fread:
    #     for i, line in enumerate(fread.readlines()):
    #         fout.write(character_set[i] + ' # ' + line)
    # fout.close()
    # fread.close()

    # generate the complete storyline file
    with open(TEXTPATH+'buffer_storyline.txt', 'r+') as fin, open(TEXTPATH+'buffer_added_storyline.txt', 'w+') as fout:
        character_set_co = character_set.copy()
        key_sets = []
        complete_storyline = ''
        for line in fin.readlines():
            line = line.replace('\n', '')
            line = line.replace('<EOL>', '')
            line = line.strip().replace('\t', '').split('#')
            key_queue = Queue()
            for item in line:
                if not item=='':
                    key_queue.put(item)
            key_sets.append(key_queue)
        while not len(key_sets)==0:
            selected_idx = random.randint(0, len(character_set_co)-1)
            if not key_sets[selected_idx].empty():
                fout.write(character_set_co[selected_idx] + '\t#\t' + key_sets[selected_idx].get() + '\t#\t')
                if not key_sets[selected_idx].empty():
                    fout.write(key_sets[selected_idx].get() + '\t#\t')
            else:
                character_set_co.remove(character_set_co[selected_idx])
                key_sets.remove(key_sets[selected_idx])
        fout.write(' <EOL>\n')
        


    # generate story
    with torch.no_grad(): 
        with open(TEXTPATH+'buffer_story.txt', 'w') as outf: #, open('gold_4sent.txt', 'w') as gf:      
                data = corpusks.tokenize(TEXTPATH+'buffer_added_storyline.txt', applyDict=True).tolist()  # this is a list of ids corresponding to words from the word2idx dict
                nsent = 0
                while nsent < args_sents:
                    try:
                        idx = data.index(eos_idks)  # the only thing that breaks the while loop is if there are no more eos_ids
                    except:
                        break
                    # this sets the conditional length to be before the first encountered EOS symbol, which is added in preprocessing
                    cond_length = idx #min(idx, 3) #ent_idxes[-3] #0] #-2]
                    #print('cond. length:', idx)
                    exist_word = set()
                    for i in range(args_words):
                        if i < cond_length:
                            word_idx = data[i]
                        else:
                            output = modelks.decoder(output)
                            word_weights = output.squeeze().data.div(temperatureks).exp().cpu()
                            samples = torch.multinomial(word_weights, 5)
                            # not apply dedup
                            word_idx = samples[0]
                        inputks.data.fill_(word_idx)
                        output, hiddenks = modelks(inputks, hiddenks)
                        if word_idx == eos_idks :
                            outf.write('\n')
                            break
                        word = corpusks.dictionary.idx2word[word_idx]
                        if i < cond_length: # prints the prompt that is conditioned on only when flag is present
                            # print conditional data
                            outf.write(word + ' ')
                        else:
                            outf.write(word + ' ')
                        #if i == cond_length-1:
                        #    outf.write('\t >>\t')
                    data = data[idx+1:]  # start after the previous idx id
                    print('| Generated {} sentences'.format(nsent+1), file=sys.stderr)
                    nsent += 1
                #gf.flush()
                outf.flush()

# characters = ['prince', 'king', 'princess', 'rabbit']
# generate_story_from_characters(characters)


cha = ['bird', 'frog', 'pig', 'squirrel']
generate_story_from_characters(cha)
buffer_story_path = '/home/serena/Desktop/proj2_storytelling/story/storytelling/statics/text/buffer_story.txt'
print_story_storyline(buffer_story_path)
