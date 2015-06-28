mtgencode
======

Python scripts for encoding MTG cards in a way that is hopefully nice for neural networks.

I apologize in advance for the quality of this code. Once I figure out the best way to do things, I might try to clean it up. Until then it's going to be a mess.

To use the script, you'll need to get the json corpus of magic cards from mtgjson.com. I usually encode from AllSets.json, but if you want to extend the code you can change it to use the other fields from AllSets-x.json.

Once you have the json corpus:
```
python encode.py AllSets.json output.txt
```
will read the corpus from AllSets.json and put the new encoding in output.txt.

Apparently I'm running Python 2.7.6.
