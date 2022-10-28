"""Module containing the circular list class"""
import numpy as np
import collections


class CircularList:
    """FIFO style buffer class
    List of fixed size where appended data overwrites the oldest entries
    Args:
        size (int, optional): Length of the array to reserve. Defaults
            to 0.
    """
    def __init__(self, size: int = 0) -> None:
        self._index = 0
        self._size = size
        self._data = np.array([])
        self.reset(self._size)

    def __getitem__(self, index: int) -> float:
        return self._data[(self._index+index) % self._size]

    def __len__(self):
        return self._size

    def __array__(self):
        return np.append(self._data[self._index:], self._data[:self._index])

    def append(self, data: list) -> None:
        """Replace the oldest entries in the buffer by those in data
        Args:
            data (list): New data of variable length
        """
        try:
            self._data[self._index:self._index+len(data)] = data
        except ValueError:
            self._data[self._index:] = data[:self._size-self._index]
            self._data[:(self._index+len(data)) % self._size] = \
                data[self._size-self._index:]
        finally:
            self._index = (self._index+len(data)) % self._size

    def reset(self, size: int = None) -> None:
        """Reset the buffer
        Resizes the buffer to the specified size if not None, fills
        the array with np.nan and resets the index back to 0.
        Args:
            size (int, optional): Length of the array to reserve.
                Defaults to None.
        """
        self._index = 0
        if size is not None:
            self._size = size
            self._data = np.zeros(self._size)
        self._data.fill(np.nan)


class RingBuffer:
    """ class that implements a not-yet-full buffer """
    def __init__(self, size_max):
        self.max = size_max
        self.data = []

    def __call__(self):
        return self.data

    class __Full:
        """ class that implements a full buffer """
        def append(self, x):
            """ Append an element overwriting the oldest one. """
            self.data[self.cur] = x
            self.cur = (self.cur+1) % self.max

        def get(self):
            """ return list of elements in correct order """
            return self.data[self.cur:]+self.data[:self.cur]

        def __call__(self):
            return self.data

    def append(self, x):
        """append an element at the end of the buffer"""
        self.data.append(x)
        if len(self.data) == self.max:
            self.cur = 0
            # Permanently change self's class from non-full to full
            self.__class__ = self.__Full

    def get(self):
        """ Return a list of elements from the oldest to the newest. """
        return self.data


class Buffer:

    def __init__(self, length):
        self._data = collections.deque(maxlen=length)

    def __call__(self):
        return self._data

    def __len__(self):
        return len(self._data)

    def __getitem__(self, key):
        if isinstance(key, slice):
            return [self._data[i] for i in range(*key.indices(len(self)))]
        elif isinstance(key, int):
            return self._data[key]

    def __setitem__(self, key, item):
        if isinstance(key, slice):
            if len(item) == len(range(*key.indices(len(self)))):
                for i, e in enumerate(range(key.start, key.stop)):
                    self._data[e] = item[i]
            else:
                raise IndexError

        elif isinstance(key, int):
            self._data[key] = item

    def __contains__(self, item):
        return item in self._data

    def __iter__(self):
        self.n = 0
        self.dataSub = self._data
        return iter(self.dataSub)

    def __next__(self):
        if self.n <= len(self._data):
            result = self._data[self.n]
            self.n += 1
            return result
        else:
            raise IndexError

    def __repr__(self):
        return str(list(self._data))

    def append(self, x):
        self._data.append(x)

    def get(self):
        return self._data
