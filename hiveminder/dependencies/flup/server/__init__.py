def get_errno(err):
    """
    Returns errno for select.error, handles differences between Py2 and Py3
    :param err: instance of select.error or OSError
    :return: Errno number
    """
    if isinstance(err, OSError):
        return err.errno
    else:
        # on older versions of python select.error is a tuple like object
        # with errno in first position
        return err[0]