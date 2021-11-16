# cnosolar
 
## Instalación

Se recomienda instalar [Anaconda](https://www.anaconda.com/products/individual) o [Miniconda](https://docs.conda.io/en/latest/miniconda.html) e instalar las librerías necesarias dentro de un ambiente específico para este software. Anaconda es una distribución de Python con muchas librearías necesarias para computación científica o ciencia de datos. Miniconda es una distribución básica y más recomendada en sistemas con limitación de recursos.

Luego de descargar e instalar la distribución de su elección, inicie el terminal. Si la instalación se realizó de manera correcta, debe estar en el ambiente `(base)`. Ahora se puede crear un ambiente específico para PvLib y los demás requerimientos de este sofware:

```
conda create --name pvllib
```

Por ejemplo, si queremos que el ambiente se llame pvlib. Ahora se activa dicho ambiente:

```
conda activate pvlib
```

Después del comando anterior se debe estar en el ambiente correspondiente, en este caso denotado por `(pvlib)`. Ahora se pueden instalar las librearías requeridas para correr los cuadernos así:

```
conda install 
```

Para clonar el repositorio se recomiendo usar el software [GitHub Desktop](https://desktop.github.com/). La url del repositorio es: [andresgm/cno_solar](https://github.com/andresgm/cno_solar).

