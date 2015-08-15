Dependencies
======

# mtgjson

First, you'll need the json corpus of Magic the Gathering cards, which can be found at:

http://mtgjson.com/

You probably want the file AllSets.json, which you should also be able to download here:

http://mtgjson.com/json/AllSets.json

# Python packages

mtgencode uses a few additional Python packages which you should be able to install with Pip, Python's package manager. They aren'y mission critical, but they provide better capitalization of names and text in human-readable output formats. If they aren't installed, mtgencode will silently fall back to less effective workarounds.

On Ubuntu, you should be able to install the necessary packages with:

```
sudo apt-get install python-pip
sudo pip install titlecase
sudo pip install nltk
```

nltk requires some additional data files to work, so you'll also have to do:

```
mkdir ~/nltk_data
cd ~/nltk_data
python -c "import nltk; nltk.download('punkt')"
cd -
```

You don't have to put the files in ~/nltk_data, that's just one of the places it will look automatically. If you try to run decode.py with nltk but without the additional files, the error message is pretty helpful.

mtgencode can also use numpy to speed up some of the long calculations required to generate the creativity statistics comparing similarity of generated and existing cards. You can install numpy with:

```
sudo apt-get install python-dev python-pip
sudo pip install numpy
```

This will launch an absolutely massive compilation process for all of the numpy C sources. Go get a cup of coffee, and if it fails consult google. You'll probably need to at least have GCC installed, I'm not sure what else.

Some additional packages will be needed for multithreading, but that doesn't work yet, so no worries.

# word2vec

The creativity analysis is done using vector models produced by this tool:

https://code.google.com/p/word2vec/

You can install it pretty easily with subversion:

``` 
sudo apt-get install subversion
mkdir ~/word2vec
cd ~/word2vec
svn checkout http://word2vec.googlecode.com/svn/trunk/
cd trunk
make
```

That should create some files, among them a binary called word2vec. Add this to your path somehow, and you'll be able to invoke cbow.sh from within the data/ subdirectory to recompile the vector model (cbow.bin) from whatever text representation was last produced (cbow.txt).

# Rebuilding the data files

The standard procedure to produce the derived data files from AllSets.json is the following:

```
./encode.py -v data/AllSets.json data/output.txt
./encode.py -v data/output.txt data/cbow.txt -s -e vec
cd data
./cbow.sh
```

This of course assumes that you have AllSets.json in data/, and that you start from the root of the repo, in the same directory as encode.py.

# Generating cards with neural nets

This repo is just a bunch of formatting and analysis support code; to do anything interesting you're going to need to train a neural net.

All this work is based on the implementation provided here:

https://github.com/karpathy/char-rnn

A customized version is also available here, with modifications specifically to support this format:

https://github.com/billzorn/mtg-rnn

Consult the documentation of those projects about how to install and use them. Generally, output files produced by encode.py are intended for use as training input; for example, the file called data/output.py here is also included in mtg-rnn as data/mtgencode-std/input.txt.
