def func(*args, **kwargs):
    for a in args:
        print(a)
    for k,v in kwargs.items():
        print(k, ':', v)
func(1,2,6,3, uno='one', dos='two', tres='three')
