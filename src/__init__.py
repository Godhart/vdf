if False:
    """VDF Magic"""
    __version__ = '0.0.1'

    # as per
    # https://ipython.readthedocs.io/en/stable/config/custommagics.html#complete-example

    from .jovyan.vdf_magic import VdfMagic

    _CONTEXT = {}

    def load_ipython_extension(ipython):
        magics = VdfMagic(ipython, _CONTEXT)
        ipython.register_magics(magics)
