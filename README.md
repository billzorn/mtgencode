# mtgencode

Utilities to assist in the process of generating Magic the Gathering cards with neural nets. Inspired by this thread on the mtgsalvation forums:

http://www.mtgsalvation.com/forums/creativity/custom-card-creation/612057-generating-magic-cards-using-deep-recurrent-neural

The purpose of this code is mostly to wrangle text between various human and machine readable formats. The original input comes from [mtgjson](http://mtgjson.com); this is filtered and reduced to one of several input formats intended for neural network training, such as the standard encoded format used in [data/output.txt](https://github.com/billzorn/mtgencode/blob/master/data/output.txt). Any json or encoded data, including output from appropriately trained neural nets, can then be interpreted as cards and decoded to a human readable format, such as a text spoiler, [Magic Set Editor 2](http://magicseteditor.sourceforge.net) set file, or a pretty, portable html file that can be viewed in any browser.

## Requirements

I'm running this code on Ubuntu 14.04 with Python 2.7. Unfortunately it does not work with Python 3, though apparently it isn't too hard to use 2to3 to automatically convert it.

For the most part it should work out of the box, though there are a few optional bonus features that will make it much better. See [DEPENDENCIES.md](https://github.com/billzorn/mtgencode/blob/master/DEPENDENCIES.md#dependencies).

This code does not have anything to do with neural nets; if you want to generate cards with them, see the [tutorial](https://github.com/billzorn/mtgencode#tutorial).

## Usage

Functionality is provided by two main driver scripts: encode.py and decode.py. Logically, encode.py handles encoding to formats intended to feed into a neural network, while decode.py handles decoding to formats intended to be read by a human.

### encode.py

```
usage: encode.py [-h] [-e {std,named,noname,rfields,old,norarity,vec,custom}]
                 [-r] [--nolinetrans] [--nolabel] [-s] [-v]
                 infile [outfile]

positional arguments:
  infile                encoded card file or json corpus to encode
  outfile               output file, defaults to stdout

optional arguments:
  -h, --help            show this help message and exit
  -e {std,named,noname,rfields,old,norarity,vec,custom}, --encoding {std,named,noname,rfields,old,norarity,vec,custom}
                        encoding format to use
  -r, --randomize       randomize the order of symbols in mana costs
  --nolinetrans         don't reorder lines of card text
  --nolabel             don't label fields
  -s, --stable          don't randomize the order of the cards
  -v, --verbose         verbose output
```

The supported encodings are:

Argument   | Description
-----------|------------
std        | Standard format: `|type|supertype|subtype|loyalty|pt|text|cost|rarity|name|`.
named      | Name first: `|name|type|supertype|subtype|loyalty|pt|text|cost|rarity|`.
noname     | No name field at all: `|type|supertype|subtype|loyalty|pt|text|cost|rarity|`.
rfields    | Randomize the order of the fields, using only the label to distinguish which field is which.
old        | Legacy format: `|name|supertype|type|loyalty|subtype|rarity|pt|cost|text|`. No field labels.
norarity   | Older legacy format: `|name|supertype|type|loyalty|subtype|rarity|pt|cost|text|`. No field labels.
vec        | Produce a content vector for each card; used with [word2vec](https://code.google.com/p/word2vec/).
custom     | Blank format slot, inteded to help users add their own formats to the python source.

### decode.py

```
usage: decode.py [-h] [-e {std,named,noname,rfields,old,norarity,vec,custom}]
                 [-g] [-f] [-c] [-d] [-v] [-mse] [-html]
                 infile [outfile]

positional arguments:
  infile                encoded card file or json corpus to encode
  outfile               output file, defaults to stdout

optional arguments:
  -h, --help            show this help message and exit
  -e {std,named,noname,rfields,old,norarity,vec,custom}, --encoding {std,named,noname,rfields,old,norarity,vec,custom}
                        encoding format to use
  -g, --gatherer        emulate Gatherer visual spoiler
  -f, --forum           use pretty mana encoding for mtgsalvation forum
  -c, --creativity      use CBOW fuzzy matching to check creativity of cards
  -d, --dump            dump out lots of information about invalid cards
  -v, --verbose         verbose output
  -mse, --mse           use Magic Set Editor 2 encoding; will output as .mse-
                        set file
  -html, --html         create a .html file with pretty forum formatting
```

The default output is a text spoiler which modifies the output of the neural net as little as possible while making it human readable. Specifying the -g option will produce a prettier, Gatherer-inspired text spoiler with heavier-weight transformations applied to the text, such as capitalization. The -f option encodes mana symbols in the format used by the mtgsalvation forum; this is useful if you want to cut and paste your spoiler into a post to share it.

Passing the -mse option will cause decode.py to produce both the hilarious internal MSE text format as well as an actual mse set file, which is really just a renamed zip archive. The -f and -g flags will be respected in the text that is dumped to each card's notes field.

Finally, the -c and -d options will print out additional data about the quality of the cards. Running with -c is extremely slow due to the massive amount of computation involved, though at least we can do it in parallel over all of your processor cores; -d is probably a good idea to use in general unless you're trying to produce pretty output to show off. Using html mode is especially useful with -c as we can link to visual spoilers from magiccards.info.

### Examples

To generate the standard encoding in data/output.txt, I run:

```
./encode.py -v data/AllSets.json data/output.txt
```

Of course, this requires that you've downloaded the mtgjson corpus to data/AllSets.json, and are running from the root of the repo.

If I wanted to convert that standard output to a Magic Set Editor 2 set, I'd run:

```
./decode.py -v data/output.txt data/allcards -f -g -d
```

This will produce a useless text file called data/allcards, and a set file called data/allcards.mse-set that you can open with MSE2. The -f and -g options will cause the text spoiler included in the notes field of each card in the set to be a pretty Gatherer-inspired affair that you could cut and paste onto the mtgsalvation forum. The -d option will dump additional information if any of the cards are invalidly formatted, which probably won't do anything because all existing magic cards are encoded correctly. Specifying the -c option here would be a bad idea; it would probably take several days to run.

### Scripts

A bunch of additional data processing functionality is provided by the files in scripts/. Right now there isn't a whole lot, but more tools might be added in the future, to do things such as convert card dumps into .arff files that could be analyzed in [Weka](http://www.cs.waikato.ac.nz/ml/weka/).

Currently, scripts/summarize.py will build a bunch of big data mining indices and use them to print out interesting statistics about a dump of cards. If you want to use mtgencode to do your own data analysis, taking a look at it would be a good place to start.



## Tutorial

This tutorial will cover how to generate cards from scratch using neural nets.

### Set up a Linux environment

If you're already running on Linux, hooray! If not, you have a few options. The easiest is probably to use a virtual machine; the disadvantage of this approach is that it will prevent you from using a graphics card to train the neural net, which speeds things up immensely. For reference, my GTX Titan is about 10x faster than my overclocked 8-core i7-5960X.

The other option is to dual boot your machine (which is what I do) or otherwise acquire a machine that you can run Linux on natively. How exactly you do this is beyond the scope of this tutorial.

If you do decide to go the virtual machine route:

1. Download some sort of virtual machine software. I recommend [VirtualBox](https://help.ubuntu.com/community/VirtualBox).
2. Download a Linux operating system. I recommend [Ubuntu](http://www.ubuntu.com/download/desktop).
3. [Create a virtual machine, and install the operating system on it](https://help.ubuntu.com/community/VirtualBox/FirstVM).

IMPORTANT NOTE: Training neural nets is extremely CPU intensive, and rather memory intensive as well. If you don't want training to take multiple weeks, it's a very good idea to give your virtual machine as many processor cores and as much memory as you can spare, and to monitor system performance with the 'top' command to make sure you aren't [swapping](https://help.ubuntu.com/community/SwapFaq), as that will degrade performance immensely.

You should be able to boot up the virtual machine and use whatever operating system you installed. If you're new to Linux, you might want to familiarize yourself with it a little. For my own sanity, I'm going to assume at least basic familiarity. Most of what we'll be doing will be in terminals; if the instructions say to do something and then provide some code in a block quote, it probably means to type that into a terminal, on line at a time.

### Set up the neural net code

We're ultimately going to use the code from the [mtg-rnn repo](https://github.com/billzorn/mtg-rnn); if anything is unclear you can refer to the documentation there as well.

First, we need to install some dependencies. The primary one is Torch, the scientific computing framework the neural net code is written. Directions are [here](http://torch.ch/docs/getting-started.html).

Next, open a terminal and install some additional lua packages:

```
luarocks install nngraph
luarocks install optim
```

Now we'll clone the git repo with the neural net code. You'll need git installed, if it isn't:

```
sudo apt-get install git
```

Then go to your home directory (or wherever you want to put the repo, it can be anywhere really) and clone it:

```
cd ~
git clone https://github.com/billzorn/mtg-rnn.git
```

This should create the folder mtg-rnn, with a bunch of files in it. To check if it works, try:

```
cd ~/mtg-rnn
th train.lua --help
```

A large usage message should be printed. If you get an error, then check to make sure Torch is working. As always, Google is your best friend when anything goes wrong.

### Set up mtgencode

Go back to your home directory (or wherever) and clone mtgencode as well:

```
cd ~
git clone https://github.com/billzorn/mtgencode.git
```

This should create the folder mtgencode, also with a bunch of files in it.

You'll need Python to run it; to get full functionality, consult [DEPENDENCIES.md](https://github.com/billzorn/mtgencode/blob/master/DEPENDENCIES.md#dependencies). But, it should work with just Python. To install Python:

```
sudo apt-get install python
```

To check if it works:

```
cd ~/mtgencode
./encode.py --help
```

Again, you should see a usage message; if you don't, make sure Python is working. mtgencode uses Python 2.7, so if you think your default python is Python 3, you can try:

```
python2 encode.py --help
```

instead of running the script directly.

### Generating an encoded corpus for training

If you just want to train with the default corpus, you can skip this step, as it already exists in mtg-rnn. Just replace all instances of 'custom_encoding' with 'mtgencode-std'.

To generate an encoded corpus, you'll first need to download AllSets.json from [mtgjson.com](http://mtgjson.com/) to data/AllSets.json. Then to encode it:

```
./encode.py -v data/AllSets.json data/custom_encoding.txt
```

This will create a the file data/custom_encoding.txt with your encoding in it. You can add some options to create a different encoding; consult the usage of [encode.py](https://github.com/billzorn/mtgencode#encodepy).

Now copy this encoded corpus over to mtg-rnn:

```
cd ~/mtg-rnn
mkdir data/custom_encoding
cp ~/mtgencode/data/custom_encoding.txt data/custom_encoding/input.txt
```

The input file does have to be named input.txt, though you can name the folder that holds it, under mtg-rnn/data/, whatever you want.

### Training a neural net

There are lots of parameters to control training. With a good GPU, I can train a 3-layer, size 512 network in a few hours; on a CPU this will probably take at least a day. 

Most networks we use are about that size. I'd recommend avoiding anything much larger, as they don't seem to produce appreciably better results and take longer to train. The only other parameter you really have to change from the defaults is seq_length, which we usually set somewhere from 120-200. If this causes memory issues you can reduce batch_size slightly to compensate.

A sample training command might like this:

```
th train.lua -gpuid -1 -rnn_size 256 -num_layers 3 -seq_length 200 -data_dir data/custom_encoding -checkpoint_dir cv/custom_format-256/ -eval_val_every 1000 -seed 7767
```

This tells the neural network to train using the corpus in data/custom_encoding/, and to output periodic checkpoints to the directory cv/custom_format-256/. The option "-gpuid -1" means to use the CPU, not a GPU (which won't be possible in VirtualBox anyway). The final options, -eval_val_every and -seed, aren't necessary, but I like to specify them. The seed will be set to a fixed 123 if you don't specify one yourself. If you're generating too many checkpoints and filling up your disk, you can increase the number of iterations between saving them by increasing the argument to -eval_val_every.

If all goes well, you should see the neural net code do some stuff and then start training, reporting training loss and batch times as it goes:

```
1/112100 (epoch 0.000), train_loss = 4.21492900, grad/param norm = 3.1264e+00, time/batch = 4.73s
2/112100 (epoch 0.001), train_loss = 4.29372822, grad/param norm = 8.6741e+00, time/batch = 3.62s
3/112100 (epoch 0.001), train_loss = 4.02817964, grad/param norm = 8.0445e+00, time/batch = 3.57s
...
```

This process can take a while, so go to sleep or something and come back in the morning. The train_loss should eventually start to decrease and settle around 0.5 or so; if it doesn't, then something is wrong and the neural net will probably produce gibberish.

Every N iterations, where N is the argument to -eval_val_every, the neural net will generate a checkpoint in cv/custom_format-256/. They look like this:

```
lm_lstm_epoch2.23_0.5367.t7
```

The numbers are important; the first is the epoch, which tells you how many passes the neural network had made over the training data when it saved the checkpoint, and the second is the validation loss of the checkpoint. Validation loss is effectively a measurement of how accurate the checkpoint is at producing text that resembles the encoded format, the lower the better. The two numbers are separated by an underscore, so for the example above, the checkpoint is from epoch 2.23, and it had a validation loss of 0.5367, which isn't great but probably isn't gibberish either.

### Sampling checkpoints to generate cards

Once you're done training, or you've got enough checkpoints and you're just impatient, you can sample to generate actual cards. If the network is still training, you'll probably want to pause it by typing Control-Z in the terminal; you can resume it later with the command 'fg'. Training will use all available CPU resources all by itself, so trying to sample at the same time is a recipe for slow.

Once you're ready, go the the mtg-rnn repo. A typical sampling command might look like this:

```
th sample.lua cv/custom_format-256/lm_lstm_epochXX.XX_X.XXXX.t7 -gpuid -1 -temperature 0.9 -length 2000 | tee cards.txt
```

Replace the Xs in the checkpoint name with the numbers in the name of an actual checkpoint; tab completion is your friend. This command will sample 2000 characters, which is probably something like 20 cards, and both print them to the terminal and write them to a file called cards.txt. The interesting options here are the temperature and the length. Temperature controls how cautious the network is; lower values produce more probable output, while higher values make it wilder and more creative. Somewhere in the range of 0.7-1.0 usually works best. Length is just how many characters to generate. You can also specify a seed with -seed, exactly as for training, which is a particularly good idea if you just generated a few million characters and would like to see something new. The default seed is fixed at 123, again exactly as for training.

You can read the output yourself, but it might be painful, especially if you're using randomly ordered fields.

### Postprocessing neural net output with mtgencode

Once you've generated some cards, you can turn them into pretty text spoilers or a set file for MSE2.

Go back to mtgencode, and run something like:

```
./decode.py -v ~/mtg-rnn/cards.txt cards.pretty.txt -d
```

This should create a file called cards.pretty.txt with a text spoiler in it that's actually designed for human consumption. Open it in your favorite text editor and enjoy!

The -d option ensures you'll still be able to see anything that went wrong with the cards. You can change the formatting with -f and -g, and produce a set file for MSE2 with -mse. The -c option produces some intersting comparisons to existing cards, but it's slow, so be prepared to wait a long time if you use it on a large dump.

## Gory details of the format

Individual cards are separated by two newlines. Multifaced cards (split, flip, etc.) are encoded together, with the castable one first if applicable, and separated by only one newline.

All decimal numbers are in represented in unary, with numbers over 20 special-cased into english. Fun fact: the only numbers over 20 on cards are 25, 30, 40, 50, 100, and 200. The unary represenation uses one character to mark the start of the number, and another to count. So 0 is &, 1 is &^, 2 is &^^, 11 is &^^^^^^^^^^^, and so on.

Mana costs are specially encoded between braces {}. I use the unary counter to encode the colorless part, and then special two-character symbols for everything else. So, {3}{W}{W} becomes {^^^WWWW}, {U/B}{U/B} becomes {UBUB}, and {X}{X}{X} becomes {XXXXXX}. The details are controlled in lib/utils.py, and handled with the Manacost and Manatext objects in lib/manalib.py.

The name of the card becomes @ in the text. I try to handle all the stupid special cases correctly. For example, Crovax the Cursed is referred to in his text box as simply 'Crovax'. Yuch.

The names of counters are similarly replaced with %, and then a speial line of text is added to tell what kind of counter % refers to. Fun fact: there's more than a hundred different kinds used in real cards.

Several ambiguous words are resolved. Most directly, the word 'counter' as in 'counter target spell' is replaced with 'uncast'. This should prevent confusion with +&^/+&^ counters and % counters.

I also reformat cards that choose between multiple things by removing the choice clause itself and instead having a delimited list of options prefixed by a number. If you could choose different numbers of things (one or both, one or more - turns out the latter is valid in all existing cases) then the number is 0, otherwise it's however many things you'd get to choose. So, 'choose one -\= effect x\= effect y' (the \ is a newline) becomes [&^ = effect x = effect y].

Finally, some postprocessing is done to put the lines of a card's ability text into a standardized, canonical form. Lines with multiple keywords are split, and then we put all of the simple keywords first, followed by things like static or activated abilities. A few things always go first (such as equip and enchant) and a few other things always go last (such as kicker and countertype). There are various reasons for doing this transformation, and some proper science could probably come up with a better specific procedure. One of the primary motivations for putting abilities onto individual lines is that it should simplify the process of adding back in reminder text. It should be noted somewhere that the definition of a simple keyword ability vs. some other line of text is that a simple keyword won't contain a period, and we can split a line with multiple of them by looking for commas and semicolons.

======

Here's an attempt at a list of all the things I do:

* Aggregate split / flip / rotating / etc. cards by their card number (22a with 22b) and put them together

* Make all text lowercase, so the symbols for mana and X are distinct

* Remove all reminder text

* Put @ in for the name of the card

* Encode the mana costs, and the tap and untap symbols

* Convert decimal numbers to unary

* Simplify the syntax of dashes, so that - is only used as a minus sign, and ~ is used elsewhere

* Make sure that where X is the variable X, it's uppercase

* Change the names of all counters to % and add a line to identify what kind of counter % refers to

* Move the equip cost of equipment to the beginning of the text so that it's closer to the type

* Rename 'counter' in the context of 'counter target spell' to 'uncast'

* Put choices into [&^ = effect x = effect y] format

* Replace acutal newline characters with \ so that we can use those to separate cards

* Clean all the unicode junk like accents and unicode minus signs out of the text so there are fewer characters

* Split composite text lines (i.e. "flying, first strike" -> "flying\first strike") and put the lines into canonical order
