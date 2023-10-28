"""
We're working with manhattan distances.  Seems like I'll need to identify where the beacon CANNOT be, per-row.

Each sensor identifies the precise location of the one closest beacon to it, as determined by manhattan distance.

Instead of enumerating all integer coordinates within the exclusion-range for each sensor, I should instead
    just do per-row `range`s for each sensor.  Then, if I need to query a specific row,
    I can enumerate and find the union of the `range`s to answer the question.

Each sensor can first calculate the manhattan distance to the closest beacon.
    Then, it can calculate the "perimiter" of exclusion: picture a cross / dimond shape.
    The straight lines are like the axes - we know that at the tips, there is just one point 
    and that in the middle the entire row-portion is filled. (minimal example below)

         #
        ###
         #

I also want to generate an image with all of the exclusion zones - maybe they make a cool shape!
Give them different / random colors and each with some opacity!
"""