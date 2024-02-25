import numpy as np


class Average:

    # The function sorts the array, smallest to largest, it then removes a set amount from each end (width).
    # The purpose of this is to eliminate any outliers and try to obtain a more accurate mean.
    def cut(self, array, width):
        array.sort()
        return array[width:-width]

# Testing
# av = Average()
# x = [2,5,7,3,7]
# print(av.mean(x, 1))


# x = [-9.768481943259605, -9.565736979742713, -9.09633883144042, -9.09633883144042, -8.452930181079317, -8.410506907807514, -8.410506907807514, -8.339345139344259, -8.339345139344259, -8.254006172179643, -8.097029300782804, -8.097029300782804]
#
# print(np.mean(x))
