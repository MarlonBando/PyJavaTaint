from tainted_var import Tainted_var

new_var: Tainted_var = Tainted_var(4, tainted=False)
print(new_var)