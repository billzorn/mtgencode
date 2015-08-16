Dependencies
======

## mtgjson

First, you'll need the json corpus of Magic the Gathering cards, which can be found at:

http://mtgjson.com/

You probably want the file AllSets.json, which you should also be able to download here:

http://mtgjson.com/json/AllSets.json

## Python packages

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

## word2vec

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

## Rebuilding the data files

The standard procedure to produce the derived data files from AllSets.json is the following:

```
./encode.py -v data/AllSets.json data/output.txt
./encode.py -v data/output.txt data/cbow.txt -s -e vec
cd data
./cbow.sh
```

This of course assumes that you have AllSets.json in data/, and that you start from the root of the repo, in the same directory as encode.py.

## Magic Set Editor 2

MSE2 is a tool for creating and viewing custom magic cards:

http://magicseteditor.sourceforge.net/

Set files, with the extension .mse-set, can be produced by decode.py using the -mse option and then viewed in MSE2.

Unfortunately, getting MSE2 to run on Linux can be tricky. Both Wine 1.6 and 1.7 have been reported to work on Ubuntu; instructions for 1.7 can be found here:

https://www.winehq.org/download/ubuntu

To install MSE with Wine, download the standard Windows installer and open it with Wine. Everything should just work. You will need some additional card styles:

http://sourceforge.net/projects/msetemps/files/Magic%20-%20Recently%20Printed%20Styles.mse-installer/download

And possibly this:

http://sourceforge.net/projects/msetemps/files/Magic%20-%20M15%20Extra.mse-installer/download

Once MSE2 is installed with Wine, you should be able to just click on the template installers and MSE2 will know what to do with them.

Some additional system fonts are required, specifically Beleren Bold, Beleren Small Caps Bold, and Relay Medium. Those can be found here:

http://www.slightlymagic.net/forum/viewtopic.php?f=15&t=14730

http://www.azfonts.net/download/relay-medium/ttf.html

Open them in Font Viewer and click install; you might then have to clear the caches so MSE2 can see them:

```
sudo fc-cache -fv
```

If you're running a Linux distro other than Ubuntu, then a similar procedure will probably work. If you're on Windows, then it should work fine as is without messing around with Wine. You'll still need the additional styles.

I tried to build MSE2 from source on 64-bit Ubuntu. After hacking up some of the files, I did get a working binary, but I was unable to set up the data files it needs in such a way that I could actually open a set. If you manage to get this to work, please explain how, and I will be very grateful.
