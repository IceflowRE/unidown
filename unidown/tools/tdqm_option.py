class TdqmOption:
    """
    Wrapper for options about the tqdm progress bar.
    """

    def __init__(self, desc: str, unit: str):
        """
        Constructor.

        :param desc: description
        :param unit: download unit
        """
        self._desc = desc
        self._unit = unit

    @property
    def desc(self):
        return self._desc

    @property
    def unit(self):
        return self._unit
