""" This module holds the const class.
"""
#NOTE: CONST used in logger.py therefore; if we decide to log this class;
#           we will need to use the default Kivy logger.

#Comment disables the 'too-few-public-methods' warning in pylint
# pylint: disable=locally-disabled, too-few-public-methods
class CONST():
    """ This static CONST class holds the program's constant(s).
    """

    class ConstError(TypeError):
        """ This ConstError class is for raising an error of Type ConstError.
        """
        pass

    #NOTE: @classmethod is like @staticmethod but allows for inheriting.
    #      also: @staticmethod doesn't pass 'cls' as an arugment.
    @classmethod
    def __setattr__(cls, name, value):
        #cls is like 'self'
        if name in cls.__dict__:
            raise cls.ConstError('Can\'t rebind const({})'.format(name))
        cls.__dict__[name] = value
        return cls.__dict__[name]

    #NOTE: @classmethod is like @staticmethod but allows for inheriting.
    #      also: @Staticmethod doesn't pass 'cls' as an argument.
    @classmethod
    def __delattr__(cls, name):
        #cls is like 'self'
        if name in cls.__dict__:
            raise cls.ConstError('Can\'t unbind const({})'.format(name))
        raise NameError(name)
