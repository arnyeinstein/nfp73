import pandas as pd
import gams
import numpy as np
import collections


def add_set(values, name, gdx, text="", append=False, overwrite=False):
    """Adds sets to gdx database. If an existing symbol is passed, the symbol can be extended (append=True) or created new
    :param values: <list> of values
    :param gdx: <gams.GamsDatabase> in which values are inserted ()
    :param symbol: <gams.GamsSet> of existing gams set
    :param text: <string> explanatory string
    :param append: <boolean> if true values are append to symbol else existing records are cleared
    :param overwrite: <boolean> if true existing symbol is overwritten or appended, else error is thrown if symbol alread exists
    :return: <gams.GamsSet>
    """
    try:
        symbol = gdx.get_symbol(name)
        if not overwrite:
            raise ValueError("Symbol already exists. Set override=True to re-create of append values")
    except gams.GamsException:
        # get dimension
        dim = 1
        if isinstance(values[0], collections.Iterable) and (not isinstance(values[0], basestring)):
            dim = len(values[0])
        # create symbol
        symbol = gdx.add_set(name, dim, text)

    # add records
    if append == False:
        symbol.clear()
    for v in values:
        if symbol.dimension == 1:
            symbol.merge_record(str(v))
        else:
            symbol.merge_record(list(map(str,v)))


def add_parameter(values, name, gdx, text="", append=False, overwrite=False):
    """Adds sets to gdx database. If an existing symbol is passed, the symbol can be extended (append=True) or created new
    :param values: <dict set: value> parameter added
                   <numeric> scalar is added
    :param gdx: <gams.GamsDatabase> in which values are inserted ()
    :param symbol: <gams.GamsSet> of existing gams set
    :param text: <string> explanatory string
    :param append: <boolean> if true values are append to symbol else existing records are cleared
    :param overwrite: <boolean> if true existing symbol is overwritten or appended, else error is thrown if symbol alread exists
    :return: <gams.GamsSet>
    """
    try:
        symbol = gdx.get_symbol(name)
        if not overwrite:
            raise ValueError("Symbol already exists. Set override=True to re-create of append values")
    except gams.GamsException:
        # get dimension
        dim = 1
        basestring = str
        keys = list(values.keys())
        # check for scalar case
        if isinstance(values, (float, int, np.int, np.float)):
            dim=0
        # more dimensional case
        elif isinstance(keys[0], collections.Iterable) and (not isinstance(keys[0], basestring)):
            dim = len(keys[0])
        # create symbol
        symbol = gdx.add_parameter(name, dim, text)

    # add records
    if append == False:
        symbol.clear()
    # scalar case
    if symbol.dimension == 0:
        symbol.add_record().value = values
    # parameter case
    else:
        for k, v in values.items():
            # one dimensional
            if symbol.dimension == 1:
                symbol.merge_record(str(k)).value = v
            # multi dimensional
            else:
                ret = symbol.merge_record(list(map(str,k))).value = v

def get_symbol_values(db, name, col_names=None, kind="value"):
    """Wrapper around to gams.GamsDatabase.get_symbol method that returns a pandas series.
    :param db: <gams.GamsDatabase> data origin
    :param name: <string> name of the symbol
    :param col_names: [<string>] Column names for dimensions
    :param kind: <string> kind of value to return ("value", "level", "marginal",
                                                    "lower", "upper", "scale" only for equations)
    :return: (x) IF SET: <list>
                 ELSE:  <float> for scalar values; <pd.Series> for remaining with values as entries
                                and dimensions as index """
    sym = db.get_symbol(name)
    n_dim = sym.dimension
    text = sym.text

    # prepare column names
    if col_names is None:
        col_names = ["dim%d" % (i+1)  for i in range(n_dim)]

    # VARIABLES
    if isinstance(sym, gams.database.GamsVariable) or isinstance(sym, gams.database.GamsEquation):
        if kind == "value":
            kind = "level"
        # in case of scalar return single value
        if n_dim == 0:
            return getattr(sym.find_record(),kind)
        else: # return a dataframe
            vals = [i.keys + [getattr(i,kind)] for i in sym]
            col_names += ["Value"]

    # PARAMETERS
    elif isinstance(sym, gams.database.GamsParameter):
        if n_dim == 0:
            return sym.find_record().get_value()
        else:
            vals = [i.keys + [getattr(i,kind)] for i in sym]
            col_names += ["Value"]

    # SETS
    elif isinstance(sym, gams.database.GamsSet):
        if n_dim == 1:
            return [i.keys[0]  for i in sym]
        else:
            return [tuple(i.keys)  for i in sym]

    # create and return dataframe
    df = pd.DataFrame(vals, columns=col_names).set_index(col_names[:n_dim])
    return df["Value"]

def copy_symbol(name, source, target):
    """Copys symbols from source to target database
    Note: currently only works for parameters
    param name: <string> name of symbol to copy
    param source: <gams.GamsDatabase> with source data
    param target: <gams.GamsDatabase> target gdx database"""
    s_sym = source.get_symbol(name)
    
    # create a blank symbol in the target data base and copy values
    try:
        t_sym = target.add_parameter(name, s_sym.get_dimension(), s_sym.get_text())
    except gams.GamsException:
        # symbol already exists 
        t_sym = target.get_symbol(name)
        pass
                
    if not s_sym.copy_symbol(t_sym):
        raise ValueError("Could not copy GAMS Symbol")

## Function to get parameter from gdx file (slightly adjusted version of Jan's)
def  get_parameter(database, name, column_names=None):
    """Wrapper around to gams.database.get_symbol method that returns a pandas data frame
    :param database: <gams.database> data origin
    :param name: <string> name of the symbol
    :param column_names: <string> Column names for dimensions
    :return: (x) DataFrame"""
    sym = database.get_symbol(name)
    n_dim = sym.dimension + 1

    # prepare column names
    if column_names is None:
        column_names = ["dim%d" % (i + 1) for i in range(n_dim)]
    if isinstance(sym, gams.database.GamsParameter):
        x = dict((tuple(rec.keys), rec.value) for rec in sym)
    if isinstance(sym, gams.database.GamsVariable):
        x = dict((tuple(rec.keys), rec.level) for rec in sym)
    x = pd.DataFrame.from_dict(x, orient='index', columns=['Value']).reset_index()
    xi = pd.DataFrame(x['index'].tolist())
    x = pd.concat([xi, x['Value'].reindex(xi.index)], axis=1)
    x.columns = column_names
    return x