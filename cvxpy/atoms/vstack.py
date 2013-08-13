from atom import Atom
import cvxpy.expressions.types as types
from cvxpy.expressions.variable import Variable
from cvxpy.constraints.affine import AffEqConstraint, AffLeqConstraint
import cvxpy.utilities as u
import cvxpy.interface.matrix_utilities as intf

class vstack(Atom):
    """ Vertical concatenation """
    # The shape is the common width and the sum of the heights.
    def set_shape(self):
        self.validate_arguments()
        cols = self.args[0].size[1]
        rows = sum(arg.size[0] for arg in self.args)
        self._shape = u.Shape(rows, cols)

    @property
    def sign(self):
        return u.Sign.UNKNOWN

    # Default curvature.
    def base_curvature(self):
        return u.Curvature.AFFINE

    def monotonicity(self): # TODO what would make sense?
        return len(self.args)*[u.Monotonicity.INCREASING]

    # Any argument size is valid.
    def validate_arguments(self):
        arg_cols = [arg.size[1] for arg in self.args]
        if max(arg_cols) != min(arg_cols):
            raise TypeError( ("All arguments to vstack must have "
                              "the same number of columns.") )

    def graph_implementation(self, var_args):
        t = Variable(*self.size)
        constraints = []
        offset = 0
        for arg in var_args:
            rows,cols = arg.size
            for i in range(rows):
                for j in range(cols):
                    constraints.append( AffEqConstraint(t[i+offset,j], arg[i,j]) )
            offset += rows

        return (t, constraints)

    # Return the absolute value of the argument at the given index.
    def index_object(self, key):
        index = 0
        offset = 0
        while offset + self.args[index].size[0] <= key[0]:
            offset += self.args[index].size[0]
            index += 1
        return self.args[index][key[0] - offset, key[1]]