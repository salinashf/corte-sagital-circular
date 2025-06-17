# Plantilla para corte boca de pez

![image](screenshot/aplicando_plantilla.gif)

Este script permite generar una plantilla para hacer corte boca de pez, el script genera

- Plantilla PDF
- Archivo DXF
- Archivo SVG
- Archivo PNG `imagen previa`

##### FORMULAS APLICADAS

Las fórmulas aplicadas son las siguientes  
`Para Angulo 90 Grados perpendicular 
`

$$
\begin{equation}
\text{calculoDirectriz} = \text{radioBase} - \sqrt{\text{radioBase}^2 - (\sin(\text{anguloDirectriz}) \times \text{radioInjerto})^2}
\end{equation}
$$

`Para Angulo entre 0-89 Grados  
`

$$
\begin{equation}
\text{calculoDirectriz} = \left( \text{radioInjerto} + \cos(\text{anguloDirectriz}) \times \text{radioInjerto} \right) \times \tan(\text{anguloInclinacion}) + \frac{\text{radioBase} - \sqrt{\text{radioBase}^2 - (\sin(\text{anguloDirectriz}) \times \text{radioInjerto})^2}}{\cos(\text{anguloInclinacion})}
\end{equation}
$$

##### FORMULAS APLICADAS EN CODIGO

Las funciones donde describe las fórmulas están en

- Función para 90 grados
  > `calcular_directrices_90`
- Función para entre 0 y 89 grados
  > `calcular_directrices_45`

##### VISOR DE ARCHIVOS DXF

Existe dos versiones del visor de archivos DXF, no están terminado como quisiera, pero funcionan de forma básica, cuando tenga tiempo lo termino.

- visor_dxf_v0.py
- visor_dxf_v1.py

##### INSTALAR LIBRERIAS

Para poder instalar la dependencia de Python está el archivo `requirements.txt` , espero no me falto ninguna

- `pip install -r requirements.txt`
