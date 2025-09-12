def read_dict_args(**kwargs):
    for key, value in kwargs.items():
        print('%s  %s' % (key, value))
print('Primero')
read_dict_args(name1='Ricardo', name2='Ramon', web='jarroba.com')
print('Segundo')
read_dict_args(Team='FC Barcelona', player='Iniesta', demarcation='Righr winger', number=8)
print('Tercero')
read_dict_args(Uno=1, Dos=2, Tres=3,Cuatro=4)
print('Cuarto')
read_dict_args(nambre='Ricardo',apellido='Ramos', edad=30,dni="45682510",correo="ricardorr@gmail.com")
