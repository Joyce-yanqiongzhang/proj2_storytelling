#import argparse
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


# parser = argparse.ArgumentParser(description='PyTorch Language Model')

# # Model parameters.
# #parser.add_argument('--train-data', type=str, default='data/penn/train.txt',
# #                    help='location of the training data corpus. Used for the rescore_story function')
# parser.add_argument('--vocabtk', type=str, default='../models/fairytale_vocab_tk.pickle',
#                     help='path to a pickle of the vocab used in training the tk model')
# parser.add_argument('--vocabks', type=str, default='../models/fairytale_vocab_ks.pickle',
#                     help='path to a pickle of the vocab used in training the ks model')
# parser.add_argument('--conditional-data', type=str, default='',
#                     help='location of the file that contains the content that the generation conditions on')
# parser.add_argument('--checkpointtk', type=str, default='../models/title_to_key_cleaned3.0_fairytale_50epoch_10sents_bptt40.pkl',
#                     help='model checkpoint to use for tk model')
# parser.add_argument('--checkpointks', type=str, default='../models/key_to_story_cleaned3.0_fairytale_10epoch_bptt300.pkl',
#                     help='model checkpoint to use for ks model')
# parser.add_argument('--sents', type=int, default='40',
#                     help='number of sentences to generate')
# parser.add_argument('--words', type=int, default='1000',
#                     help='number of words to generate')
# parser.add_argument('--seed', type=int, default=1111,
#                     help='random seed')
# parser.add_argument('--cuda', action='store_true', default=True,
#                     help='use CUDA')
# parser.add_argument('--temperaturetk', type=float, default=0.5,
#                     help='temperature tk - higher will increase diversity')
# parser.add_argument('--temperatureks', type=float, default=0.8,
#                     help='temperature ks - higher will increase diversity')
# args = parser.parse_args()

STORYPATH = '/home/serena/Desktop/proj2_storytelling/story/'
TEXTPATH = '/home/serena/Desktop/proj2_storytelling/story/storytelling/statics/text/'
vocabtk = STORYPATH+'models/fairytale_vocab_tk.pkl'
vocabks = STORYPATH+'models/fairytale_vocab_ks.pkl'
checkpointtk = STORYPATH+'models/title_to_key_cleaned3.0_fairytale_50epoch_10sents_bptt40.pkl'
checkpointks = STORYPATH+'models/key_to_story_cleaned3.0_fairytale_100epoch_bptt300.pkl'
args_sents = 40
args_words = 1000
args_seed = 1111
args_cuda = True
temperaturetk = 0.5
temperatureks = 0.8




# def evaluate(data, hidden, args):
#     bdata = batchify(torch.LongTensor(data), test_batch_size, args)
#     #print ('current sentence: %d, ending: %d, and hidden: %s' %(j, i, str(lhidden)))
#     source, targets = get_batch(bdata, 0, args, evaluation=True)
#     loutput, lhidden = model(source, hidden)
#     output_flat = loutput.view(-1, ntokens)
#     #print ('output_flat:', output_flat.size())
#     total_loss = criterion(output_flat, targets).data
#     #print ('total_loss:', total_loss.size(), total_loss)
#     return total_loss[0], lhidden

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

    environment_set = ['castle', 'forest', 'mountain']
    selected_env = random.choice(environment_set)
    print('selected env:', selected_env)
    print('characters:', character_set)

    #create the buffer title txt
    with open(TEXTPATH+'buffer_title.txt', 'w') as f:
        #add the blank headers
        character_set = ['first']+character_set
        for cha in character_set:
            f.write(cha + ' in ' + selected_env + ' <EOT> \n')
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

    # add character_set into buffer_storyline
    with open(TEXTPATH+'buffer_added_storyline.txt', 'w') as fout, open(TEXTPATH+'buffer_storyline.txt', 'r+') as fread:
        for i, line in enumerate(fread.readlines()):
            fout.write(character_set[i] + ' # ' + line)
    fout.close()
    fread.close()
        


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

if __name__=='__main__':
    test_set = ['prince', 'princess', 'rabbit']
    generate_story_from_characters(test_set)