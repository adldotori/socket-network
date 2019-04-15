import module

a = module.client()
if a.login():
    a.execute()

