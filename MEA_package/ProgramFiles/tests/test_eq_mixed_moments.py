import unittest
import sympy
from TaylorExpansion import taylor_expansion
from eq_mixedmoments import eq_mixedmoments
from eq_mixedmoments import make_f_of_x
from eq_mixedmoments import make_f_expectation
from eq_mixedmoments import make_k_chose_e
from eq_mixedmoments import make_s_pow_e
from test_ode_problem import Moment


class TestEqMixedMoments(unittest.TestCase):
    def test_for_p53(self):

        stoichio = sympy.Matrix([
            [1, -1, -1, 0,  0,  0],
            [0,  0,  0, 1, -1,  0],
            [0,  0,  0, 0,  1, -1]
        ])

        propensities = sympy.Matrix([
            ["                    c_0"],
            ["                c_1*y_0"],
            ["c_2*y_0*y_2/(c_6 + y_0)"],
            ["                c_3*y_0"],
            ["                c_4*y_1"],
            ["                c_5*y_2"]])

        counter = [
        Moment([0, 0, 0], 1),
        Moment([0, 0, 2], sympy.Symbol("yx1")),
        Moment([0, 1, 1], sympy.Symbol("yx2")),
        Moment([0, 2, 0], sympy.Symbol("yx3")),
        Moment([1, 0, 1], sympy.Symbol("yx4")),
        Moment([1, 1, 0], sympy.Symbol("yx5")),
        Moment([2, 0, 0], sympy.Symbol("yx6"))
        ]

        species = sympy.Matrix(["y_0", "y_1", "y_2"])
        k_vec = [1, 0, 0]
        ek_counter = [Moment([1, 0, 0], sympy.Symbol("y_0"))]
        answer = eq_mixedmoments(propensities,counter,stoichio,species,k_vec,ek_counter).T
        result = sympy.Matrix(["c_0 - c_1*y_0 - c_2*y_0*y_2/(c_6 + y_0)"," 0"," 0"," 0"," c_2*y_0/(c_6 + y_0)**2 - c_2/(c_6 + y_0)"," 0"," -c_2*y_0*y_2/(c_6 + y_0)**3 + c_2*y_2/(c_6 + y_0)**2"])
        self.assertEqual(answer, result)

