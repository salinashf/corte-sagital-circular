# Definir variables
$diametro_base = 87
$diametro_injerto = 52
$grosor_injerto = 1
$angulo_inclinacion = 90
$numero_divisiones = 120
$ancho_linea = 1


write-host "Diametro base " $diametro_base 
write-host "Diametro injerto " $diametro_injerto 
write-host "Grosor injerto:" $grosor_injerto
write-host "Angulo de inclinacion:" $angulo_inclinacion 
write-host "Numero de divisiones " $numero_divisiones 
write-host "Ancho linea en el dibujo " $ancho_linea 


# Ejecutar scripts Python con variables
python generar_plantilla_arg.py --diametro_base $diametro_base --diametro_injerto $diametro_injerto --grosor_injerto $grosor_injerto --angulo_inclinacion $angulo_inclinacion --numero_divisiones $numero_divisiones --ancho_linea $ancho_linea

python 3d_graph_template.py --diametro_injerto $diametro_injerto