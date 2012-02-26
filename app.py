def build_application(project, interface):
    Handler = __import__(interface, globals(), locals(), -1).Handler
    handler = Handler(project)
    return handler
    

