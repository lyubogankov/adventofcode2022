1. Amending git commiter: useful bash script for performing this.
    https://stackoverflow.com/questions/3042437/how-to-change-the-commit-author-for-a-single-commit

    I checked before/after by putting "git log" into a file:
        `git log > log.txt`

2. Experimenting with `gif` -> `mp4` conversion
    
    - https://deaddabe.fr/blog/2022/04/27/exporting-mov-and-mp4-animations-from-gimp/
    I found a blog post that worked!  I needed to "unoptimize" the gif I made using GIMP, otherwise the mp4 does not work.

    However, in order to run this, I needed to increase the amount of system resources allocated to imagemagick (specifically, the amount of disk space): https://stackoverflow.com/a/53699200
    
    Further however -- I couldn't get the mp4 to embed in the README.

3. `gif` creation with ImageMagick

    Since `mp4` didn't work, I wanted to try making a gif out of pngs with IM.

    However, I found that their `-delay` flag takes an [integer in centiseconds](https://imagemagick.org/script/command-line-options.php#delay), aka 1/100s.  This is too slow for me... I was hoping for 200-250FPS.

    Also, I noticed that the output size was rather large - can "mogrify" to shrink? (https://stackoverflow.com/a/47343340)

    Based on [this SO thread](https://superuser.com/questions/569924/why-is-the-gif-i-created-so-slow), I also tried increasing the minimum delay to 2x100, and 5x100 but the result appeared the same?

    **Update**: I tried making GIFs with delay = [1, 25] to see the difference.
        In FireFox/Chrome, delay=2 is the fastest value allowed;  1 is rendered way slower.

    I will try regenerating my gifs with delay=2!


4. I want to try out `asciinema`:

    - https://github.com/asciinema/asciinema

    - https://github.com/marionebl/svg-term-cli (asciinema -> svg, embeddable in README!!)

    - I should probably combine this with `curses` for more efficient updating... instead of the print-then-clear-screen thing I'm currently doing.

        https://docs.python.org/3/howto/curses.html