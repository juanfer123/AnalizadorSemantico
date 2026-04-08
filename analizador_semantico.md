Asignación: Analizador semántico de B-Minor en Python
Curso
Compiladores
Tema
Construcción del analizador semántico para el lenguaje B-Minor
Modalidad
Individual o en parejas, según indique el profesor.

________________________________________
1. Contexto
En esta asignación se continuará el desarrollo del compilador de B-Minor construido en Python. En esta fase ya se asume que existe, al menos en una versión funcional básica, el análisis léxico, el análisis sintáctico y una representación del programa mediante un AST (Abstract Syntax Tree).

El objetivo principal de esta práctica es implementar el análisis semántico, siguiendo un estilo de trabajo semejante al de las asignaciones clásicas de compiladores: especificación clara, entregables precisos, verificación incremental y pruebas automáticas sobre archivos fuente.

B-Minor es un lenguaje fuertemente tipado, por lo tanto el analizador semántico debe verificar la coherencia de tipos, el uso correcto de identificadores y la validez contextual de las construcciones del lenguaje.

________________________________________
2. Objetivos de aprendizaje
Al finalizar esta asignación, el estudiante deberá ser capaz de:

1.	Construir y administrar una tabla de símbolos con alcance léxico.
2.	Implementar el patrón Visitor sobre el AST usando la librería multimethod.
3.	Realizar chequeo de tipos en un lenguaje fuertemente tipado.
4.	Detectar y reportar errores semánticos con mensajes útiles.
5.	Verificar reglas semánticas relacionadas con declaraciones, expresiones, sentencias, funciones y bloques.
6.	Validar el compilador usando un conjunto de archivos de prueba.

________________________________________
3. Restricciones y requisitos técnicos
El trabajo debe cumplir obligatoriamente con las siguientes condiciones:

-	El analizador semántico debe implementarse en Python.
-	El recorrido del AST debe hacerse mediante el patrón Visitor.
-	El patrón Visitor debe implementarse usando la librería multimethod.
-	La tabla de símbolos podrá construirse de una de estas dos maneras:
-	usando el archivo adjunto symtab.py, o
-	usando directamente la estructura ChainMap de Python.
-	El sistema debe estar preparado para ejecutarse sobre un conjunto de archivos de prueba suministrados para evaluar el progreso.

________________________________________
4. Archivos base esperados
Se espera que el proyecto tenga una estructura semejante a la siguiente:

bminor/
├── lexer.py
├── parser.py
├── model.py
├── symtab.py
├── checker.py
├── tests/
│   ├── good/
│   └── bad/
└── main.py
Archivo principal de esta práctica
El núcleo de la solución debe estar en un archivo llamado, por ejemplo:

-	checker.py
-	o semantic.py

En este archivo deberá implementarse la lógica del análisis semántico.

________________________________________
5. Alcance de la asignación
El analizador semántico debe recorrer el AST y verificar, como mínimo, los siguientes aspectos.
5.1. Declaraciones
Debe verificarse que:

-	todo identificador sea declarado antes de usarse;
-	no existan redefiniciones inválidas en un mismo alcance;
-	el sombreado de variables en alcances internos se maneje correctamente, según el diseño de su tabla de símbolos;
-	cada declaración quede registrada con su información semántica relevante.
5.2. Alcances léxicos
Deben existir nuevos alcances para construcciones como:

-	bloques { ... };
-	funciones;
-	parámetros formales;
-	estructuras adicionales del lenguaje, si su versión de B-Minor las tiene.

El analizador debe poder entrar y salir de alcances correctamente.
5.3. Tipos
El lenguaje debe tratarse como fuertemente tipado. Esto significa que el analizador debe comprobar compatibilidad de tipos en:

-	asignaciones;
-	operadores aritméticos;
-	operadores relacionales;
-	operadores lógicos;
-	condiciones de if, for y while;
-	expresiones unarias;
-	llamadas a funciones;
-	sentencias return;
-	acceso a arreglos, si están soportados.
5.4. Funciones
Debe verificarse que:

-	una función no se redefina incorrectamente;
-	los parámetros formales se registren en el alcance adecuado;
-	la cantidad de argumentos en una llamada coincida con la cantidad de parámetros;
-	los tipos de los argumentos coincidan con los tipos esperados;
-	el tipo del valor retornado coincida con el tipo declarado de la función;
-	una función que debe retornar un valor lo haga correctamente.
5.5. Expresiones
Toda expresión debe quedar anotada con su tipo resultante. Por ejemplo, podría añadirse un atributo como:

node.type

Esta información será usada por nodos superiores durante el chequeo semántico.

________________________________________
6. Reglas mínimas de chequeo semántico
A continuación se presenta un conjunto mínimo de reglas que su implementación debe soportar. El profesor podrá ampliar esta lista según la versión concreta de B-Minor usada en clase.
6.1. Variables
-	Una variable debe estar declarada antes de utilizarse.
-	No se puede redeclarar una variable en el mismo alcance si la política del compilador no lo permite.
-	Una asignación solo es válida si el tipo del lado izquierdo es compatible con el del lado derecho.

Ejemplo:

x: integer = 10;
x = 20;        // válido
x = true;      // error semántico
6.2. Operadores aritméticos
Los operadores aritméticos solo deben aceptar operandos de tipos apropiados.

Por ejemplo:

-	+, -, *, /, % requieren operandos numéricos enteros, salvo que su diseño incluya float.
-	% normalmente solo aplica a enteros.

Ejemplo:

x: integer = 3 + 4;     // válido
b: boolean = true;
y: integer = x + b;     // error semántico
6.3. Operadores relacionales
Los operandos comparados deben ser compatibles.

Ejemplo:

x: integer = 5;
b: boolean = x < 10;    // válido
c: boolean = x < true;  // error
6.4. Operadores lógicos
Los operadores lógicos deben trabajar con valores booleanos.

Ejemplo:

b: boolean = true && false;   // válido
x: integer = 3;
c: boolean = x && true;       // error
6.5. Condiciones
Las condiciones de estructuras de control deben ser booleanas.

if (true) { print 1; }        // válido
if (5) { print 1; }           // error semántico
6.6. Funciones y retorno
f: function integer (x: integer) = {
    return x + 1;
}

es válido, mientras que:

f: function integer (x: integer) = {
    return true;
}

es un error semántico.
6.7. Arreglos (si aplica)
Si su versión de B-Minor soporta arreglos, deben verificarse al menos estas reglas:

-	el índice debe ser entero;
-	el acceso debe hacerse sobre una variable de tipo arreglo;
-	el valor asignado a una posición del arreglo debe coincidir con el tipo base del arreglo.

________________________________________
7. Diagrama sugerido del proceso semántico
El siguiente diagrama resume el flujo esperado:

Código fuente
     │
     ▼
 Analizador léxico
     │
     ▼
 Analizador sintáctico
     │
     ▼
        AST
     │
     ▼
 Analizador semántico (Visitor)
     │
     ├── Tabla de símbolos
     ├── Reglas de alcance
     ├── Chequeo de tipos
     └── Anotación de nodos con type
     │
     ▼
 AST validado o lista de errores semánticos

________________________________________
8. Diagrama sugerido de tipos
Se recomienda documentar su sistema de tipos con un diagrama como el siguiente:

                 ┌─────────┐
                 │  Type   │
                 └────┬────┘
                      │
      ┌───────────────┼───────────────┐
      │               │               │
      ▼               ▼               ▼
 ┌─────────┐     ┌─────────┐     ┌─────────┐
 │integer  │     │boolean  │     │ string  │
 └─────────┘     └─────────┘     └─────────┘
      │
      ▼
 ┌────────────┐
 │ array[T]   │
 └────────────┘

También puede complementarse con una tabla de compatibilidad de operadores como esta:

Operador	Tipos permitidos	Tipo resultado
+	integer, integer	integer
-	integer, integer	integer
*	integer, integer	integer
/	integer, integer	integer
%	integer, integer	integer
<, <=, >, >=	integer, integer	boolean
==, !=	tipos compatibles	boolean
`&&,		`
!	boolean	boolean

Si su implementación incluye otros tipos como char o float, la tabla debe ampliarse.

________________________________________
9. Requerimiento de implementación con Visitor
El análisis semántico debe implementarse usando el patrón Visitor. La idea general esperada es similar a la siguiente:

from multimethod import multimeta

class Visitor(metaclass=multimeta):
    pass

class Checker(Visitor):
    def __init__(self):
        self.errors = []
        self.symtab = None

    def visit(self, node):
        raise NotImplementedError(type(node).__name__)

Cada nodo del AST debe delegar en el visitor correspondiente. Por ejemplo:

class Node:
    def accept(self, v):
        return v.visit(self)

La solución debe estar organizada, ser extensible y separar claramente:

-	la definición del AST,
-	la tabla de símbolos,
-	y el chequeo semántico.

________________________________________
10. Tabla de símbolos
La tabla de símbolos puede implementarse usando el archivo adjunto symtab.py o una versión propia basada en ChainMap.

Como mínimo, la tabla debe permitir:

-	crear un alcance nuevo con referencia al padre;
-	insertar símbolos en el alcance actual;
-	buscar símbolos respetando alcance léxico;
-	detectar redeclaraciones inválidas;
-	facilitar la depuración o visualización del contenido de los alcances.
Información mínima sugerida por símbolo
Cada entrada de la tabla podría contener información como:

-	nombre;
-	clase del símbolo (variable, function, parameter, etc.);
-	tipo;
-	mutabilidad, si aplica;
-	nodo asociado del AST;
-	alcance de declaración.

Ejemplo conceptual:

x -> Symbol(name='x', kind='variable', type='integer')
f -> Symbol(name='f', kind='function', type='function(integer)->integer')

________________________________________
11. Manejo de errores
El analizador semántico no debe abortar en el primer error, salvo que el profesor indique otra política. Se recomienda acumular errores y reportarlos al final.

Cada error debe incluir, cuando sea posible:

-	tipo de error;
-	identificador o construcción involucrada;
-	número de línea;
-	mensaje claro.

Ejemplos de mensajes esperados:

error: símbolo 'x' no definido en la línea 12
error: no se puede asignar un valor de tipo boolean a una variable de tipo integer en la línea 18
error: la función 'sum' espera 2 argumentos pero recibió 3 en la línea 27
error: la condición del if debe ser boolean y se recibió integer en la línea 34

________________________________________
12. Archivos de prueba
Se entregará un conjunto de archivos de prueba para validar el progreso del proyecto. Estos archivos estarán separados, idealmente, en dos grupos:

-	tests/good/: programas semánticamente correctos;
-	tests/bad/: programas con errores semánticos.
Requisitos mínimos de pruebas
El estudiante debe demostrar que su analizador detecta correctamente casos como:

1.	uso de variable no declarada;
2.	redeclaración de variable;
3.	asignación incompatible;
4.	operador aplicado a tipos inválidos;
5.	condición no booleana;
6.	retorno con tipo incorrecto;
7.	llamada a función con número incorrecto de argumentos;
8.	llamada a función con tipos de argumentos incorrectos;
9.	acceso inválido a arreglos, si aplica.

________________________________________
13. Entregables
Cada grupo o estudiante debe entregar:
13.1. Código fuente
El código completo de la solución en Python.
13.2. Documento breve
Un archivo README.md que explique:

-	cómo ejecutar el analizador semántico;
-	cómo está implementada la tabla de símbolos;
-	cómo está implementado el Visitor con multimethod;
-	qué tipos soporta el sistema;
-	qué chequeos semánticos fueron implementados;
-	qué aspectos quedaron pendientes, si los hay.
13.3. Evidencia de pruebas
Salida de ejecución sobre varios archivos de prueba, mostrando:

-	ejemplos válidos aceptados;
-	ejemplos inválidos rechazados con mensajes claros.

________________________________________
14. Sugerencia de interfaz de ejecución
La herramienta podría ejecutarse así:

python3 main.py checker tests/good/test01.bminor
python3 main.py checker tests/bad/test07.bminor

Salida esperada en un caso correcto:

semantic check: success

Salida esperada en un caso con errores:

error: símbolo 'x' no definido en la línea 8
error: la condición del while debe ser boolean en la línea 13
semantic check: failed

________________________________________
15. Rúbrica sugerida
Criterio	Porcentaje
Implementación correcta de tabla de símbolos y alcances	20%
Uso adecuado del patrón Visitor con multimethod	15%
Chequeo de tipos en expresiones y asignaciones	20%
Verificación semántica de funciones y retornos	15%
Calidad del reporte de errores	10%
Cobertura de archivos de prueba	10%
Organización, limpieza y documentación del código	10%

________________________________________
16. Recomendaciones de diseño
1.	No mezcle lógica sintáctica con lógica semántica.
2.	Anote los tipos directamente en los nodos del AST cuando sea pertinente.
3.	Defina una representación clara para los tipos del lenguaje.
4.	Centralice las reglas de compatibilidad en tablas o funciones auxiliares.
5.	Construya primero una versión mínima funcional y luego amplíe los chequeos.
6.	Pruebe continuamente con archivos pequeños.

________________________________________
17. Extensiones opcionales
Para estudiantes que quieran ir más allá, se sugieren las siguientes extensiones:

-	verificación de que toda ruta de ejecución de una función no void retorne valor;
-	chequeo semántico de arreglos multidimensionales;
-	conversión del sistema de tipos a una jerarquía de clases;
-	impresión gráfica del árbol de alcances;
-	reporte de errores con formato enriquecido usando rich.

________________________________________
18. Criterio de aceptación
Una solución se considerará satisfactoria si:

-	recorre correctamente el AST;
-	maneja alcances léxicos;
-	detecta errores semánticos fundamentales;
-	realiza chequeo de tipos coherente con un lenguaje fuertemente tipado;
-	utiliza multimethod en la implementación del Visitor;
-	pasa satisfactoriamente los archivos de prueba básicos.

________________________________________
19. Observación final
Esta práctica constituye la base para fases posteriores del compilador, tales como:

-	interpretación del programa,
-	generación de código intermedio,
-	optimización,
-	o generación de código objeto.

Por esa razón, el analizador semántico debe diseñarse con cuidado, claridad y posibilidad de extensión.

________________________________________
20. Anexo: guía de progreso sugerida
Fase 1
-	implementar tabla de símbolos;
-	registrar declaraciones globales;
-	detectar uso de identificadores no definidos.
Fase 2
-	manejar bloques y alcances anidados;
-	registrar parámetros de funciones;
-	verificar redeclaraciones.
Fase 3
-	anotar tipos de expresiones;
-	validar operadores unarios y binarios;
-	validar asignaciones.
Fase 4
-	validar llamadas a funciones;
-	validar retornos;
-	ejecutar batería completa de pruebas.

________________________________________
21. Formato de entrega
Entregue un archivo comprimido con:

-	código fuente;
-	archivos de prueba;
-	README.md;
-	cualquier script auxiliar necesario para ejecutar la solución.

Nombre sugerido del archivo:

apellido1_apellido2_bminor_semantic.zip

________________________________________

Fin de la asignación

