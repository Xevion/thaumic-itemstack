# thaumic-itemstack
*A parser script for the Thaumic JEI itemstack NBT file with sorting functions.*

The purpose of this parser script was completely personal; I have problems with Thaumcraft's aspect system if you ask me: I could never find the item best suited for burning to get aspects I needed. So, while looking into how I could get through this, I discovered Thaumic JEI had a full file with ALL of the items and their respective aspects.

So, I got to work on creating a function for parsing the NBT file (I only realized it was NBT after I had got to work parsing it, I'm still not sure whether or not there was a Python module built for parsing something like that).

I created a couple functions for sorting the file, and I only now realize the mistake I had made in making this as it's completely unnessecary. My sorting functions were intended to sort by multiple different values, for example, the ratio of the selected aspect(s) to total aspect(s), and then by the total aspects in the item.

This was essentially required as the file had thousands of items and proper advanced sorting was required if you didn't want to be scrolling up and down for the best item for the aspect you wanted, as the better one could be hid behind something else.

Anyways, the reason I regret this is the whole set of sorting functions could have been solved with tuple key sorting. The python `.sort` function allows you to input a function that gives off some kind of sortable key, for example in this example below:

```python
>>> x.sort(key=lambda item : (item * -1) if item % 2 != 0 else item)
>>> x
[9, 7, 5, 3, 1, 2, 4, 6, 8, 10]
```

The sorting function essentially did what the `map()` function does, and then sorts based on this. It applies the function supplied by the `key` argument to every item, and then applies the sorting algorithm.

This particular example essentially made the list look like so:

```python
[-1, 2, -3, 4, -5, 6, -7, 8, -9, 10]
```

Now, I used this function quite often in my thaumic script, but there was a caveat to my style of applying multi-layer sorting: I applied it in a way more complicated way than I ever could have needed to.

The `key` argument can be supplied with a `tuple`, of which the items of the tuple correspond to the key each part of the multi-sort you want go.

I'm bad with words, so here's an example if that didn't make sense at all:

```python
    >>> import random
    >>> x = [''.join(random.choices(list('aeiou'), k=random.randint(3, 10))) for _ in range(15)
    >>> x
['aioueeeuei', 'iouo', 'auau', 'aiu', 'aee', 'oueaiao', 'ueuuo', 'auea', 'iieo', 'oiueuoaoi', 'ioeoaii', 'eiee', 'eeiaoua', 'uoa', 'uiee']
    >>> multisort = lambda item : (item[0], len(item))
```

So, I first created a list of random strings using a character set of `aeiou` (this is my personal favorite way of doing it, using `random.choices`, I substitute that with `string.ascii_letters` otherwise).

Then I created a multisort function that will act as our key, and passed it to the `sorted` function. The multisort function returns the first character of the string, and then the length of the string.

Can you guess what the array will be sorted by?

`Alphabetically` (a-z), and then by `Length` (shortest first), of course!

```python
>>> print(sorted(x, key=multisort))
['aiu',
 'aee',
 'auau',
 'auea',
 'aioueeeuei',
 'eiee',
 'eeiaoua',
 'iouo',
 'iieo',
 'ioeoaii',
 'oueaiao',
 'oiueuoaoi',
 'uoa',
 'uiee',
 'ueuuo']
 ```

 I really wish I had known this had worked, and am surprised I didn't find out about it sooner. Well, luckily I know about it now, and I still have the chance to write the GUI part of this thing next.

 If you wish to work on it and refactor my awful code (sorry, I tried my best to make it understandable), feel free to make a pull request.