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

======

So, what exactly does it do? Here's an excerpt from the output file. Hopefully it's even up to date.

```
|assault||sorcery||||{RR}|@ deals &^^ damage to target creature or player.|
|battery||sorcery||||{^^^GG}|put a &^^^/&^^^ green elephant creature token onto the battlefield.|

|moat||enchantment||||{^^WWWW}|creatures without flying can't attack.|

|nether spirit||creature||spirit|&^^/&^^|{^BBBB}|at the beginning of your upkeep, if @ is the only creature card in your graveyard, you may return @ to the battlefield.|

|cryptic command||instant||||{^UUUUUU}|choose two ~\= counter target spell.\= return target permanent to its owner's hand.\= tap all creatures your opponents control.\= draw a card.|

|darksteel reactor||artifact||||{^^^^}|countertype # charge\indestructible \at the beginning of your upkeep, you may put a # counter on @.\when @ has twenty or more # counters on it, you win the game.|

|jace, memory adept||planeswalker|&^^^^|jace||{^^^UUUU}|+&^: draw a card. target player puts the top card of his or her library into his or her graveyard.\&: target player puts the top ten cards of his or her library into his or her graveyard.\-&^^^^^^^: any number of target players each draw twenty cards.|
```

The format is:
```
|cardname|supertypes|types|planeswalker loyalty|subtypes|power and toughness|mana cost|text|
```

Cards are separated by two newlines. Multifaced cards (split, flip, etc.) are encoded together, with the castable one first if applicable, and separated by only one newline.

All decimal numbers are in represented in unary, with numbers over 30 special-cased into english. Fun fact: the only numbers over 30 on cards are 40, 50, 100, and 200. The unary represenation uses one character to mark the start of the number, and another to count. So 0 is &, 1 is &^, 2 is &^, 11 is &^^^^^^^^^^^, and so on.

Mana costs are specially encoded between braces {}. I use unary counter to encode the colorless part, and then special two-character symbols for everything else. So, {3}{W}{W} becomes {^^^WWWW}, {U/B}{U/B} becomes {UBUB}, and {X}{X}{X} becomes {XXXXXX}. Read encode.py if you want more details, there's a nice table.

The name of the card becomes @ in the text. I try to handle all the stupid special cases correctly. For example, Crovax the Cursed is referred to in his text box as simple 'Crovax.' Yuch.

The names of counters are similarly replaced with #, and then a speial line of text is added to tell what kind of counter # refers to. Fun fact: there's more than a hundred different kinds.

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

* Change the names of all counters to # and add a line to identify what kind of counter # refers to

* Move the equip cost of equipment to the beginning of the text so that it's closer to the type

* Replace acutal newline characters with \ so that we can use those to separate cards

* clean all the unicode junk like accents and unicode minus signs out of the text so there are fewer characters