import os

def is_tainted(method_signature):
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    f = open(os.path.join(project_dir, "src" ,"files", "java_sql_xss_sources.txt"), "r")
    for line in f:
        if line.strip() == method_signature:
            f.close()
            return True
    f.close()
    return False
