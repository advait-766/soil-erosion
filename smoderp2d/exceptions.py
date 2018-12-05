class SmoderpError(Exception):
    pass

class ProviderError(Exception):
    pass

class MaxIterationExceeded(SmoderpError):
    """Number of iteration exceed max iteration criterion.
    """
    def __init__(self, mi, t):
        self.msg = 'Maximum of iterations (max_iter = {}) was exceeded of at time [s]: {}'.format(
            mi, t
        )

    def __str__(self):
        return repr(self.msg)


class RainfallFileMissing(SmoderpError):

    """Exception raised if file with rainfall record is missing

    Attributes:
        name of file which is missing
    """

    def __init__(self, filen):
        self.msg = 'Missing file: ' + str(filen) + '.'

    def __str__(self):
        return repr(self.msg)
