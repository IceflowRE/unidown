class TqdmOption:
    """
    Wrapper for options about the tqdm progress bar.

    :param desc: description
    :type desc: str
    :param unit: unit
    :type unit: str

    :ivar desc: description
    :vartype _desc: str
    :ivar unit: unit
    :vartype unit: str
    """

    def __init__(self, desc: str, unit: str):
        self.desc = desc
        self.unit = unit
