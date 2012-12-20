class GiottoControl(object):
    pass


class Redirection(GiottoControl):
    def __init__(self, path, persist={}):
        self.path = path
        self.persist = persist










class OldRedirection(GiottoControl):
    """
    Represents the result of one invocation as the result of another.
    """
    rendered_invocation = ()

    def __init__(self, invocation, args=[], kwargs={}):
        self.invocation = invocation
        self.args = args
        self.kwargs = kwargs

    def render_args_kwargs(self, model):
        """
        Now that we have the model data, render the actual url we want to
        redirect to.
        """
        new_args = []
        for arg in self.args:
            if type(arg) == _M:
                new_args.append(arg.get_value(model))
        
        new_kwargs = {}
        for k, v in self.kwargs.iteritems():
            if type(v) == _M:
                new_kwargs[k] = v.get_value(model)

        self.rendered_invocation = (self.invocation, new_args, new_kwargs)

    def render(self, result, mimetype, errors):
        self.render_args_kwargs(result)
        return self

class _M(object):
    """
    Represents the getting of a value on an abstract model retun value.
    For internal use only.
    """
    def __init__(self, attribute=None, brackets=None):
        self.attribute = attribute
        self.brackets = brackets

    def get_value(self, model):
        if self.brackets:
            return model[self.brackets]

        if self.attribute:
            return getattr(model, self.attribute)

class MClass(object):
    """
    Symbolic representation the return value of the model
    """
    def __getattr__(self, item):
        return _M(attribute=item)

    def __getitem__(self, item):
        return _M(brackets=item)

M = MClass()