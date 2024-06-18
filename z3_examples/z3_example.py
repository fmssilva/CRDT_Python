from z3 import *

# Create a solver
s = Solver()

RUN_EXAMPLE = 8

###############     EXAMPLES     ###############

if RUN_EXAMPLE == 8:
    x,y = Ints('x y')
    s.add( (x >= y) == (Or(x == y, Not(x < y))) )
    print(s.check())
    s.reset()
    s.add( (x >= y) == (Not(x < y))  ) 
    print(s.check())


if RUN_EXAMPLE == 0:
    # PROVE A CORRECT THEOREM: x+x is even
    x = Int('x')
    s.add(ForAll([x], (x + x) % 2 == 0))
    print("x+x is even ? ", s.check())

    # DISPROVE A WRONG THEOREM: x+x is odd
    s.reset()
    s.add(ForAll([x], (x + x) % 2 == 1))
    print("x+x is odd ? ", s.check())



if RUN_EXAMPLE == 1:
    ## ---> SOLVING SYSTEM OF EQUATIONS  
    # In each chech() the solver returns one answer if it exists 
    # to see all the answers we need to add the previous answer as a constraint so it won't be returned again

    # a + b + c = 500
    # a^2 + b^2 = c^2
    # a,b >= 0

    # Declare variables
    a, b, c = Ints('a b c')

    # Add constraints
    s.add(a + b + c == 500)
    s.add(a*a + b*b == c*c)
    s.add(a >= 0)
    s.add(b >= 0)

    # Solve
    print("\nSolving equation: a + b + c = 500  where a,b,c >= 0")
    while s.check() == sat:
        print(s.model())
        s.add(Or(a != s.model()[a], b != s.model()[b], c != s.model()[c]))


elif RUN_EXAMPLE == 2:
    ## ---> FINDING A COUNTER EXAMPLE FOR A THEOREM

    # Para provar que teorema é errado, basta correr solver e ver se check() == unsat
    # Para ver o contra-exemplo, negar o teorema, correr solver, e print s.model()

    # Teorema: 
    # For all integers x and y, if x + y = 0 then x = 0 or y = 0
    # The theorem is false because the counter example is x = 1 and y = -1
    
    # Declare variables
    x, y = Ints('x y')  

    # Add constraints
    s.add(ForAll([x, y], Implies(x + y == 0, Or(x == 0, y == 0))))

    # Solve
    print("\nSolving theorem: if x+y=0 -> x=0 V y=0")
    print (s.check())
    
    s.reset() # remover os constraints anteriores

    # Negar o teorema
    s.add(Exists([x, y], And(x + y == 0, Not(Or(x == 0, y == 0)))))
    print("\nSolving Negated theorem: if x+y=0 -> x=0 V y=0")
    print (s.check())
    print(s.model())
    m = s.model()
    print("x = ", m[x])
    print("y = ", m[y])



    


