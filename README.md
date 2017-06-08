# ![HiveMinder](hiveminder/static/img/hiveminder.png)

Bee logistics game for the [Man AHL Coder Prize.](http://www.ahl.com/coderprize)

You can [play the demo online.](http://hiveminder.pythonanywhere.com/)

Rules are available via the 'i' pop-up in the top right corner of the game.

This repo contains an implementation of the game that was used in the Man AHL Coder Prize 2017 competition. It allows
you to write algo players in python and play against them or have them play against each other.

This repo contains everything you need to run the game including all the 3rd party libraries it depends on.

Once you have cloned the repo run ```python game.py``` to launch the game in your browser. The only requirements on
your system are python* and a relatively up-to-date web browser. 

The challenge in the original competition was to write an algo player for the game and two example algo players were
provided in the algos package to help entrants get started. You can measure the relative performance of all your algos
by running ```python simulate.py```.
