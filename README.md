# list_sort_from_user_item_pair_votes

https://github.com/txemi/list_sort_from_user_item_pair_votes


## ABSTRACT

This project is a tool for helping in sorting lists of items (personal todo list, project backlog, list of movies, cooking recipes...) by some criteria (urgency, priority, affinity, rank of alignment to some concept...) taking care of mechanical part (algorithm and mechanics) and asking you throug UI for simple subjective questions (votes on pair of elements).

## MOTIVATION

Working with big lists (several tens)  for humans is hard and expensive. If you want to sort one you have two options:
* Directly reorder de list moving elements
* Assing numeric rank to each item in order to use it later for sorting

The first is hard and error prone, human will not be methodical, maintain attention, perhaps will evaluate locally parts of the big list losing top view...

The second suffers from same problems, your criteria can change as time pass and you will finish making judgements at the end in a different way you started.

This script convert this hard task for humans to a sequence of simple decisions as single votes among two elements that you can pause and resume as you wish.

## HOW IT WORKS

* You place the list in a csv in the same dir as development. You can replace the movie example file provided with code. You can also use other folder if you later exec script referencing its correct location and mantaining working directory where data files rest.
* Then you run main.py
* The script loads items
* It will start making simple questions to user: "which of this two elements do you rank more?"
* You answer 1, 2 or n depending if you assing higher rank to first, second or cannot decide.
* On each iteration script will build a bigger sorted list with new elements
* If you interrumpt the script and start again it will be able to recover as votes are stored in pickle and csv files on current folder (you could need to delete pickle file if you modify script code and something fails)
* As vote history is stored script will ask first about items with less uncertainty in order to reach bigger and more useful sorted list as soon as possible (with less votes asked to user)
* You will see a lot of logging on screen, but you can ignore and center on answering vote questions, as result is stored on your current directory on each iteration.

## TODO
* input CSV improvements: better autodetection of ID and item description, perhaps passing as argument

That's all!

Thanks