
class WrapperFunction:

    def __init__(self, wrapped_function):
        self.wrapped_function = wrapped_function

    def __call__(self, wrapper_function):
        def aggregate(*args, **kwargs):
            result = self.wrapped_function(*args, **kwargs)
            return wrapper_function(result, *args, **kwargs)
        return aggregate
