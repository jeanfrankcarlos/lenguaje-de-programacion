def read_dict_args(**kwargs):
  for key, value in kwargs.items():
    print('%s - %s' % (key, value))

print('1')
read_dict_args(ciudad='Lima', pais='Perú', continente='América')
print('2')
read_dict_args(marca='Toyota', modelo='Corolla', año=2022, color='Rojo')
print('3')
read_dict_args(pelicula='Inception', director='Christopher Nolan', año=2010, género='Ciencia ficción')
print('4')
read_dict_args(nombre='Sofía', apellido='García', ocupacion='Médica', ciudad='Madrid')
