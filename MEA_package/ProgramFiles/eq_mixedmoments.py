#####################################################################
# Called by centralmoments.py
# Provides the terms needed for equation 11 in Angelique's paper
# This gives the expressions for dB/dt in equation 9, these are the 
# time dependencies of the mixed moments
####################################################################


import sympy as sp
from TaylorExpansion import derive_expr_from_counter_entry
from TaylorExpansion import get_factorial_term
import itertools
import operator


def make_f_of_x(variables, k_vec, e_vec, reaction):


    # all values of {x ^ (k - e)} for all combination of e and k
    all_xs = [var ** (k_vec[i] - e_vec[i]) for i,var in enumerate(variables)]

    # The product of all values
    product = reduce(operator.mul, all_xs)

    # multiply the product by the propensity {a(x)}
    return product * reaction

def make_f_expectation(variables, expr, counter):

    """
    Creates <F> in eq. 12 (see Ale et al. 2013) to calculate <F> for EACH VARIABLE combination.

    :param variables: the name of the variables (typically {y_0, y_1, ..., y_n})
    :param expr: an expression
    :param counter: a list of all possible combination of order of derivation
    :return: a column vector (as a sympy matrix). Each row correspond to an element of counter
    """

    # compute derivatives for  EACH ENTRY in COUNTER
    derives = [derive_expr_from_counter_entry(expr, variables, c) for c in counter]

    # Computes the factorial terms for EACH entry in COUNTER
    factorial_terms = [get_factorial_term(c) for (c) in counter]

    # Element wise product of the two vectors
    te_matrix = sp.Matrix(len(counter), 1, [d*f for (d, f) in zip(derives, factorial_terms)])

    return te_matrix
    # return [d*f for (d, f) in zip(derives, factorial_terms)]

def make_k_chose_e(e_vec, k_vec):

    factorials = [sp.factorial(k) / (sp.factorial(e) * sp.factorial(k - e)) for e,k in zip(e_vec, k_vec)]
    product = reduce(operator.mul, factorials)
    return product

def make_s_pow_e(S, reac_idx, e_vec):
    vec = [S[i, reac_idx] ** e for i,e in enumerate(e_vec)]
    product = reduce(operator.mul, vec)
    return product


def eq_mixedmoments(amat, counter, S, ymat , kvec, ekcounter):

    # f o
    f_of_x_vec = [make_f_of_x(ymat, kvec, c, reac) for (reac, c) in itertools.product(amat, ekcounter)]

    f_expectation_vec = [make_f_expectation(ymat, f, counter) for f in f_of_x_vec]

    s_pow_e_vec = [make_s_pow_e(S, reac_idx, c) for (reac_idx, c) in itertools.product(range(len(amat)), ekcounter)]

    k_choose_e_vec = [make_k_chose_e(e, kvec) for e in ekcounter] * len(amat)

    product = [ f * s * ke for (f, s, ke) in zip(f_expectation_vec, s_pow_e_vec, k_choose_e_vec)]

    to_sum = sp.Matrix(product).reshape(len(product),len(product[0]))

    summed = [reduce(operator.add, to_sum[: ,i ]) for i in range(to_sum.cols)]

    mixed_moments = sp.Matrix(1, len(summed), summed)


    return mixed_moments

#
#
# def eq_mixedmoments2(nreactions, nvariables, nMoments, amat, counter, S, ymat, nDerivatives, kvec, ekcounter, dAdt):
#
#     """
#     Function called by centralmoments.py
#
#     This implements equation 11 in the paper:
#     ::math::`\frac{d \beta}{dt} = \sum_{e_1}^{k_1} ... \sum_{e_d}^{k_d} \mathbf{s^e} \mathbf{{k \choose e}} \langle \mathbf{x^{(k-e)}} \alpha(x) \rangle`.
#
#     It also computes the required terms provided by equation 12
#
#     :param nreactions: number of reactions
#     :param nvariables: number of variables
#     :param nMoments: maximal degree of moments
#     :param amat: column vector of all propensities
#     :param counter: all possible combinations of moments
#     :param S: stoichiometry matrix
#     :param ymat: vector of terms for all species
#     :param nDerivatives: the maximum order of moments
#     :param kvec: vector of ks (upper limit for the sums).
#     :param ekcounter: all possible ::math::`[e_1, ..., e_d]` vectors that are needed for the sums (precomputed in advance)
#     :param dAdt: the result of equation 10 in the paper, ::math::`\frac{d\alpha}{dt}` term. A column vector with columns representing different counter values.
#     :return: A vector of mixed moments, where each column is for each combination k1, ..., kd in equation 9 (i.e. `ekcounter` values)
#     """
#
#     print "______________________"
#     print ekcounter
#     print dAdt
#
#
#     mixedmomentst = Matrix(len(ekcounter), dAdt.cols, lambda i, j: 0)
#     for reaction in range(0, nreactions):
#
#         mixedmoments = Matrix(len(ekcounter), dAdt.cols, lambda i, j: 0)
#
#         # for evec in ekcounter:
#         for ekloop in range(0, len(ekcounter)):
#             evec = ekcounter[ekloop]
#
#             Enumber = sum(evec)    # order of the evec moment, used only to check whether it is zero below
#
#             # Replace with
#             # if Enumber <= 0:
#             #     continue
#             if Enumber > 0:
#                 # s^e term in eq. 11 calculated for the particular reaction only
#                 # calculated as ::math::`\mathbf{s_l^e} = s_{l,1}^{e_1} ... s_{l,d}^{e_d}` for some reaction l
#                 f_1 = 1
#                 for fi in range(0, len(evec)):
#                     f_1 = f_1 * S[fi, reaction] ** evec[fi]
#
#                 # (k e) binomial terms in eq 11, (symbolic) scalar, not dependent on a reaction
#                 f_2 = 1
#                 for fi in range(0, len(evec)):
#                     f_2 = f_2 * factorial(kvec[fi]) / (factorial(evec[fi]) * factorial(kvec[fi] - evec[fi]))
#
#                 # x^(k-e) terms in eq 11
#                 yterms = (ymat[0]) ** (kvec[0] - evec[0])
#                 for nv in range(1, nvariables):
#                     yterms = yterms * (ymat[nv]) ** (kvec[nv] - evec[nv])
#
#                 # Expectation value term, amat[reaction] is the propensity of the reaction
#                 E = yterms * amat[reaction]
#
#                 ########################################
#                 # Derivatives of dF/dt in equation 12 in
#                 # Angelique's paper
#                 #######################################
#
#                 # TODO: This code block computes something similar as damat computations somewhere
#                 dEmat = Matrix(nDerivatives, 1, lambda i, j: 0)
#                 for D in range(0, nDerivatives):
#                     if D == 0:
#                         row = []
#                         for nv in range(0, nvariables):
#                             deriv = diff(E, ymat[nv])
#                             row.append(deriv)
#                         dEmat[D, 0] = row
#                     else:
#                         prev = Matrix(dEmat[D - 1, 0])
#                         row = []
#                         y = len(prev)
#                         for eq in range(0, y):
#                             for nv in range(0, nvariables):
#                                 deriv = diff(prev[eq], ymat[nv])
#                                 row.append(deriv)
#                         dEmat[D, 0] = row
#
#
#                 #########################################
#                 # Loops over necessary combinations of
#                 # moments to calculate terms for equation
#                 # 12 in paper
#                 #########################################
#
#                 TE = Matrix(len(counter), 1, lambda i, j: 0)
#                 for Te in range(0, len(counter)):
#
#                     nvec = counter[Te]
#                     Dnumber = sum(nvec)
#
#                     if Dnumber == 0:
#                         # This is essentially the case where n1=n2=...=nd=0, where Taylor expansion term is just F(X)
#                         # .. or E as they use it (therefore no factorials and stuff)
#                         TE[Te] = E
#                     # (else) if 1 < Dnumber < (nMoments + 1)
#                     if Dnumber > 1 and Dnumber < (nMoments + 1):
#
#                         # Compute the ::math::`\mathbf{n!} = n_1! ... n_d!` term in the taylor expansion
#                         # (it is actually 1/n!, but it's divided from one a bit later on).
#                         r_1 = 1
#                         for j in nvec:
#                             r_1 = r_1 * factorial(j)
#
#                         # Yeah, we shortened "n_vector" to nvec, but going further, as typing "nvec" was just too long
#                         n = nvec
#
#                         nzidx = []
#                         for i in range(0, len(n)):
#                             if n[i] != 0:
#                                 nzidx.append(i)
#
#                         # nzidx - all i's such that n_i are not zero
#
#                         nnew = []
#                         for i in range(0, len(nzidx)):
#                             idx = nzidx[i]
#                             for j in range(0, n[idx]):
#                                 nnew.append(idx)
#
#                         # nnew - nzidx values repeated as many times as the corresponding n_i values
#
#                         # Okay, this is just using the nnew above to calculate where the appropriate derivative is,
#                         # easy.
#                         Didx = 0
#                         for nzs in range(0, len(nnew)):
#                             Didx = Didx + ((nvariables) ** (Dnumber - nzs - 1)) * (nnew[nzs])
#
#                         # Compile the final taylor expansion term for given counter value
#                         # The correct derivative is computed in the end, whereas factorial is computed in r_1
#                         TE[Te] = F(1) / r_1 * dEmat[Dnumber - 1][Didx]
#
#                     # The final taylor exp term is the
#                     # s^e term * binomial term * TE vector
#                     # This should be outside of the loop
#                     Taylorexp = f_1 * f_2 * TE
#
#                 for i in range(0, mixedmoments.cols):
#                     mixedmoments[ekloop, i] = Taylorexp[i]
#
#
#         # The rows correspond to k1, ..., kd and the columns to species
#         # This matrix is summed iteratively for all reactions to generate the `mixedmomentst` matrix.
#         # `mixedmomentst` is a matrix with a row for each e1,..,ed combination in eq.11.
#         # Columns (species) are summed over to give mixed moments (for all species at once, not individually)
#         # which gives dB/dt terms for use in eq. 9.
#         mixedmomentst = mixedmomentst + mixedmoments
#
#     # `Mixedmoments` is a vector with an entry for each k1,...,kd combination in equation 9
#     mixedmoments = Matrix(1, mixedmomentst.cols, lambda i, j: sum(mixedmomentst[:, j]))
#
#     return mixedmoments
