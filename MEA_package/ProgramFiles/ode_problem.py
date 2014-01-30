
import sympy

class ODEProblem(object):
    """
    Stores the left and right hand side equations to be simulated
    """

    # These are private (as indicated by __, the code is a bit messier, but we can ensure immutability this way)
    __right_hand_side = None
    __left_hand_side = None
    __moment_dic = None
    __constants = None

    def __init__(self, left_hand_side, right_hand_side, constants, moments):
        """
        Creates a `ODEProblem` object that stores the problem to be simulated/used for inference
        :param left_hand_side: the left hand side of equations
        :param right_hand_side: the right hand side of equations
        :param constants: the constants of the model
        :param moments: the moments as a list of n-tuple, where n is the number of species
        """
        self.__left_hand_side = left_hand_side
        self.__right_hand_side = right_hand_side
        self.__constants = constants[:]
        self.__moment_dic = self.make_moment_dic(moments)

        self.validate()
#
    def make_moment_dic(self, moments):
        dic_out = dict()
        for i,m in enumerate(moments):
            dic_out[m] = i
        return dic_out


    def validate(self):
        """
        Validates whether the particular model is created properly
        """
        if self.left_hand_side.rows != self.right_hand_side.rows:
            raise ValueError("There is i% left hand side equations and %i right hand side ones. The same number is expected." % (self.left_hand_side.rows, self.right_hand_side.rows))

        if self.left_hand_side.rows != len(self.__moment_dic):
            raise ValueError("There is i% equations and %i hand side and %i moments. The same number is expected." % (self.left_hand_side.rows, len(self.__moment_dic)))

    # Expose public interface for the specified instance variables
    # Note that all properties here are "getters" only, thus assignment won't work
    @property
    def left_hand_side(self):
        return self.__left_hand_side

    @property
    def right_hand_side(self):
        return self.__right_hand_side

    @property
    def constants(self):
        return self.__constants

    @property
    def moment_dic(self):
        return self.__moment_dic



def parse_model(input_filename, from_string=False):
    """
    Parses model from the `input_filename` file and returns it
    :param input_filename:
    :param from_string: True if a string containing the file data is passed instead of a filename
    :return: Parsed `ODEProblem` object
    :rtype: ODEProblem
    """

    # Strings to identify appropriate fields of the file
    STRING_RIGHT_HAND = 'RHS of equations:'
    STRING_LEFT_HAND = 'LHS:'
    STRING_CONSTANT = 'Constants:'
    STRING_MOM = 'List of moments:'

    if not from_string:
        infile = open(input_filename)
        try:
            lines = infile.readlines()    #read input data
        finally:
            infile.close()
    else:
        lines = input_filename.split("\n")

    all_fields = dict()
    field = None
   # cut the file into chunks. The lines containing ":" are field headers
    for i, line in enumerate(lines):
        if ":" in line:
            field = line.rstrip()
            all_fields[field]=[]
        elif field:
            rsline = line.rstrip()
            if rsline:
                all_fields[field].append(rsline)

    # now we query all the fields we need

    try:
        right_hand_side = sympy.Matrix([sympy.simplify(l) for l in all_fields[STRING_RIGHT_HAND]])
    except KeyError:
        print 'The field "' + STRING_RIGHT_HAND + '" is not in the input file "' + input_filename +'"'
        raise
    try:
        left_hand_side = sympy.Matrix([l for l in all_fields[STRING_LEFT_HAND]])
    except KeyError:
        print 'The field "' + STRING_LEFT_HAND + '" is not in the input file "' + input_filename +'"'
        raise
    try:
        constants = sympy.Matrix([l for l in all_fields[STRING_CONSTANT]])
    except KeyError:
        print 'The field "' + STRING_CONSTANT + '" is not in the input file "' + input_filename +'"'
        raise
    try:
        moments = [tuple(eval(l)) for l in all_fields[STRING_MOM]]
    except KeyError:
        print 'The field "' + STRING_CONSTANT + '" is not in the input file "' + input_filename +'"'
        raise

    return ODEProblem(left_hand_side, right_hand_side,constants, moments)

