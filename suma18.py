def func(*args, **kwargs):
  for a in args:
    print(a)
  for k,v in kwargs.items():
    print(k, ':', v)

func(100,200,300, animal='perro', fruta='manzana', pais='Japón')
