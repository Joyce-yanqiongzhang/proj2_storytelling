import torch
import _pickle as pickle



def repackage_hidden(h):
    """Wraps hidden states in new Tensors,
    to detach them from their history."""
    if isinstance(h, torch.Tensor):
        return h.detach()
    else:
        return tuple(repackage_hidden(v) for v in h)


def batchify(data, bsz, args):
    # Work out how cleanly we can divide the dataset into bsz parts.
    nbatch = data.size(0) // bsz
    # Trim off any extra elements that wouldn't cleanly fit (remainders).
    data = data.narrow(0, 0, nbatch * bsz)
    # Evenly divide the data across the bsz batches.
    data = data.view(bsz, -1).t().contiguous()
    if args.cuda:
        data = data.cuda()
    return data


def get_batch(source, i, args, seq_len=None, evaluation=False):
    seq_len = min(seq_len if seq_len else args.bptt, len(source) - 1 - i)
    data = source[i:i+seq_len]
    target = source[i+1:i+1+seq_len].view(-1)
    return data, target


def load_pickle(path):
    with open(path, 'rb') as fin:
        obj = pickle.load(fin)
    return obj


def make_vocab(corpus_dictionary, vocab_path):
    """take data, create pickle of vocabulary"""
    with open(vocab_path, 'wb') as fout:
        pickle.dump(corpus_dictionary, fout)
    print('Saved dictionary to', vocab_path)

def print_story(filepath):
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

def print_story_storyline(filepath):
    story = ''
    print('')
    with open(filepath, 'r') as f:
        for i, line in enumerate(f.readlines()):
            if True:
                line = line.split(" ")
                start_story = False
                if "<EOL>" in line:
                    num_of_seg = 0
                    for word in line:
                        if word=="<EOL>":
                            start_story = True
                            continue
                        if not start_story:
                            print(word, end=' ')
                        else:
                            if not word=="</s>":
                                story = story + word + ' '
                            else:
                                num_of_seg += 1
                                if num_of_seg%8==0:
                                    story += '\n'
                else:
                    for word in line:   
                        if not word == "</s>":
                            story = story + word + ' '
                print('')
                #story = story + "***** end of the part *****\n"
                #print("***** end of the story *****")
        story = story + '***** end of the story *****\n'
        print('')
        print(story)


    f.close()