def read_list_args(*args):
    for count, arg in enumerate(args):
        print( '%d - %s' % (count, arg))
read_list_args('Ricardo', 'jarroba.com')
read_list_args('Ricardo', 23, 'Ramon', [1, 2, 3], 'jarroba.com')
read_list_args(10,"juan",5.5,(5,2,0), 'cetpropuno.edu.pe',0)
